#!/usr/bin/env node
/** Validate the final Markdown AST and compile every formula, without changing source. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

let enginePromise;
async function engine() {
  enginePromise ??= Promise.all([
    import('unified'), import('remark-parse'), import('remark-gfm'),
    import('remark-math'), import('remark-rehype'), import('rehype-stringify'),
    import('katex'), import('hast-util-from-html'), import('katex/contrib/mhchem'),
  ]).then(([u, p, g, m, r, s, k, h]) => ({
    unified: u.unified, parse: p.default, gfm: g.default, math: m.default,
    rehype: r.default, stringify: s.default, katex: k.default, fromHtml: h.fromHtml,
  }));
  return enginePromise;
}

function escaped(source, i) {
  let n = 0;
  while (i > 0 && source[--i] === '\\') n++;
  return n % 2 === 1;
}

function walk(node, fn, parent = null) {
  fn(node, parent);
  for (const child of node.children ?? []) walk(child, fn, node);
}

// Build bounded reading surfaces once, without measuring a viewport or changing
// the Markdown/TeX. Keep table semantics and a single embedded copy of each image.
function readingLayout(tree) {
  const element = (tagName, properties, children) => ({ type: 'element', tagName, properties, children });
  function visit(parent) {
    parent.children = parent.children?.map(node => {
      if (node.type !== 'element') return node;
      const classes = node.properties?.className ?? [];
      if (classes.includes('report-inline-math') || classes.includes('report-display-math')) {
        Object.assign(node.properties, { tabIndex: 0, ariaLabel: '数学公式，可横向滚动 / Scrollable math' });
        return node; // Preserve KaTeX's HTML and accessible MathML verbatim.
      }
      const content = node.children?.filter(n => n.type !== 'text' || n.value.trim()) ?? [];
      if (node.tagName === 'p' && content.length === 1 && content[0].tagName === 'img') {
        return element('figure', { className: ['report-figure'] }, [
          element('details', {}, [element('summary', {}, [
            element('span', { className: ['report-image-hint'] }, [
              { type: 'text', value: '图片：点按切换适宽 / 原尺寸 · Toggle fit / original size' },
            ]),
            element('span', { className: ['report-image-viewport'], tabIndex: 0,
              role: 'region', ariaLabel: '原图查看区域 / Image viewport' }, content),
          ])]),
        ]);
      }
      visit(node);
      if (node.tagName === 'th' || node.tagName === 'td') {
        node.children = [element('div', { className: ['report-table-cell'] }, node.children)];
      }
      if (node.tagName === 'table') {
        return element('div', { className: ['report-table-scroll'], tabIndex: 0,
          role: 'region', ariaLabel: '表格，可横向滚动 / Scrollable table' }, [node]);
      }
      if (node.tagName === 'pre') {
        Object.assign(node.properties ??= {}, { tabIndex: 0, ariaLabel: '代码，可横向滚动 / Scrollable code' });
      }
      return node;
    });
  }
  visit(tree);
  return tree;
}

// GFM splits even pipes inside code/math, unless the pipe itself is escaped.
function tableCells(row) {
  const parts = [];
  let start = 0;
  for (let i = 0; i < row.length; i++) {
    if (row[i] === '|' && !escaped(row, i)) {
      parts.push(row.slice(start, i));
      start = i + 1;
    }
  }
  parts.push(row.slice(start));
  if (!parts[0].trim()) parts.shift();
  if (parts.length && !parts.at(-1).trim()) parts.pop();
  return parts.length;
}

export async function validateMarkdown(source, { reportPath = 'report.md' } = {}) {
  const e = await engine();
  const parser = e.unified().use(e.parse).use(e.gfm).use(e.math, { singleDollarTextMath: true });
  const tree = parser.parse(source);
  const errors = [];
  const counts = { inlineMath: 0, displayMath: 0, strong: 0, tables: 0, images: 0 };
  const images = [];
  const starts = [0];
  for (let i = 0; i < source.length; i++) if (source[i] === '\n') starts.push(i + 1);
  function issue(code, message, offset = 0) {
    let low = 0, high = starts.length;
    while (low + 1 < high) {
      const middle = (low + high) >> 1;
      if (starts[middle] <= offset) low = middle;
      else high = middle;
    }
    errors.push({ code, line: low + 1, column: offset - starts[low] + 1, message });
  }
  const definitions = new Map();
  walk(tree, n => { if (n.type === 'definition') definitions.set(n.identifier, n); });
  walk(tree, (node, parent) => {
    const start = node.position?.start.offset ?? 0;
    const raw = source.slice(start, node.position?.end.offset ?? start);
    if (node.type === 'strong') counts.strong++;
    if (node.type === 'image' || node.type === 'imageReference') {
      counts.images++;
      const url = node.url ?? definitions.get(node.identifier)?.url;
      if (url) images.push({ node, url, start });
      else issue('image-reference', 'Image reference has no definition.', start);
    }
    if (node.type === 'math' || node.type === 'inlineMath') {
      const display = node.type === 'math';
      counts[display ? 'displayMath' : 'inlineMath']++;
      if (display) {
        const lines = raw.split(/\r?\n/);
        if (lines[0].trim() !== '$$' || lines.length < 3 ||
            !/^\s*(?:>\s*)*\$\$\s*$/.test(lines.at(-1))) {
          issue('math-fence', 'Use a complete $$ block, with each $$ on its own line and no metadata.', start);
        }
      } else if (!/^\$[^$\s](?:[^\n]*[^$\s])?\$$/.test(raw)) {
        issue('inline-math-delimiter', 'Use $formula$ on one line without padding; move long formulas to a $$ block.', start);
      }
      if (!node.value.trim()) issue('empty-math', 'Formula is empty.', start);
      // A frequent accidental pair is "$5 and $10": do not silently render currency as math.
      if (!display && /^\d/.test(node.value) && /^\d/.test(source.slice(node.position.end.offset))) {
        issue('currency-ambiguity', 'Possible currency parsed as math. Escape literal dollar signs as \\$.', start);
      }
      try {
        const html = e.katex.renderToString(node.value, {
          displayMode: display, throwOnError: true, strict: 'error',
          trust: false, maxExpand: 1000, maxSize: 20, output: 'htmlAndMathml',
        });
        node.data = {
          hName: display ? 'div' : 'span',
          hProperties: { className: [display ? 'report-display-math' : 'report-inline-math'], 'data-source-line': node.position.start.line },
          hChildren: e.fromHtml(html, { fragment: true }).children,
        };
      } catch (error) {
        issue('katex', String(error.message ?? error), start);
      }
    }
    if (node.type === 'text') {
      // Link destinations, fenced/inline code, math and image alt text are not prose nodes.
      // Also exclude literal autolinks, whose visible text is the URL itself.
      if (parent?.type === 'link' && (parent.url === node.value || parent.url === `mailto:${node.value}`)) return;
      for (let i = 0; i < raw.length; i++) {
        if (escaped(raw, i)) continue;
        if (raw[i] === '\\' && /[()[\]]/.test(raw[i + 1] ?? '')) {
          issue('legacy-math-delimiter', 'Backslash math delimiters are plain Markdown escapes here. Use $...$ or a $$ block; put literal examples in code.', start + i);
          i++;
        } else if (raw[i] === '$') {
          issue('unparsed-dollar', 'Dollar sign did not become math. Close the formula correctly or escape a literal dollar as \\$.', start + i);
        } else if (raw.slice(i, i + 2) === '**') {
          issue('unparsed-strong', 'Literal ** did not become bold. Check delimiter balance and CJK punctuation; add outside spaces or move punctuation outside bold.', start + i);
          i++;
        } else if (raw[i] === '`') {
          issue('unparsed-code', 'Backtick did not become inline code. Match delimiter lengths or escape a literal backtick.', start + i);
        }
      }
    }
    if (node.type === 'code') {
      const lines = raw.split(/\r?\n/);
      const open = lines[0].match(/^(`{3,}|~{3,})/);
      if (open) {
        const close = lines.at(-1).replace(/^\s*(?:>\s*)*/, '').trim();
        if (lines.length < 2 || !new RegExp(`^${open[1][0]}{${open[1].length},}$`).test(close)) {
          issue('code-fence', 'Fenced code is not closed; it may swallow the rest of the report.', start);
        }
      }
    }
    if (node.type === 'table') {
      counts.tables++;
      for (const row of node.children) {
        const rowRaw = source.slice(row.position.start.offset, row.position.end.offset);
        const actual = tableCells(rowRaw);
        if (actual !== node.align.length) {
          issue('table-columns', `Table expects ${node.align.length} cells, found ${actual}. For math use \\lvert/\\rvert instead of bare |; escape literal pipes as \\|.`, row.position.start.offset);
        }
      }
    }
    if (node.type === 'html' && !/^<!--[\s\S]*-->$/.test(raw.trim())) {
      issue('raw-html', 'Raw HTML is outside this report profile. Use Markdown/math or a code block so content is not silently dropped.', start);
    }
  });
  for (const { node, url, start } of images) {
    try {
      if (/^data:image\/(?:png|jpeg|gif|webp);base64,/.test(url)) continue;
      if (/^[a-z][a-z\d+.-]*:/i.test(url) || url.startsWith('//')) {
        issue('image-local', 'Use a verified local image for the offline report preview.', start);
        continue;
      }
      const imagePath = path.resolve(path.dirname(reportPath), decodeURIComponent(url));
      const mime = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml' }[path.extname(imagePath).toLowerCase()];
      if (!mime) throw new Error('Unsupported image type; use PNG, JPEG, GIF, WebP or SVG.');
      const bytes = await fs.readFile(imagePath);
      // Reference images need their own resolved URL; do not mutate a shared link definition.
      node.type = 'image';
      node.url = `data:${mime};base64,${bytes.toString('base64')}`;
    } catch (error) {
      issue('image-file', `Cannot load image ${url}: ${error.message}`, start);
    }
  }
  let html = null;
  if (!errors.length) {
    const compiler = e.unified().use(e.rehype).use(e.stringify);
    html = compiler.stringify(readingLayout(await compiler.run(tree)));
  }
  return { ok: errors.length === 0, profile: 'commonmark-gfm-dollar-math-katex', counts, errors, html };
}

export async function previewDocument(body, title = 'Paper reading report') {
  const cssPath = fileURLToPath(import.meta.resolve('katex/dist/katex.min.css'));
  let css = await fs.readFile(cssPath, 'utf8');
  const urls = [...new Set([...css.matchAll(/url\(([^)]+)\)/g)].map(m => m[1]))];
  for (const url of urls) {
    const font = url.replace(/^['"]|['"]$/g, '');
    const bytes = await fs.readFile(path.resolve(path.dirname(cssPath), font));
    const ext = path.extname(font).slice(1);
    css = css.split(`url(${url})`).join(`url(data:font/${ext};base64,${bytes.toString('base64')})`);
  }
  const escapedTitle = title.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; font-src data:; style-src 'unsafe-inline'; base-uri 'none'">
<title>${escapedTitle}</title><style>${css}
*{box-sizing:border-box}html{color-scheme:light}body{margin:0;background:#fff;color:#20252b;font:17px/1.85 system-ui,-apple-system,sans-serif}
main{width:100%;max-width:960px;min-width:0;margin:auto;padding:clamp(16px,4vw,36px) clamp(16px,3vw,28px);overflow-wrap:anywhere}
main :where(p,li,blockquote,figure,details,summary,div){min-width:0}h1,h2,h3{line-height:1.4;margin:1.5em 0 .65em}h1{font-size:clamp(1.6em,5vw,2em)}h2{border-bottom:1px solid #dce2e8;padding-bottom:.3em}
a{color:#1756a9}img{display:block;max-width:100%;height:auto;margin:20px auto}blockquote{border-left:4px solid #adc5db;margin:1em 0;padding-left:clamp(12px,3vw,18px);color:#465261}ul,ol{padding-inline-start:clamp(18px,4vw,28px)}
pre{max-width:100%;padding:16px;background:#f4f6f8;overflow:auto;line-height:1.5;white-space:pre;overflow-wrap:normal}code{font-size:.9em}p code,li>code{white-space:break-spaces;overflow-wrap:anywhere}
.report-table-scroll{max-width:100%;overflow:auto;margin:1.2em 0}table{width:100%;border-collapse:collapse;font-size:.9em}th,td{padding:8px 12px;border:1px solid #dce2e8;vertical-align:top}th{background:#f4f6f8}.report-table-cell{min-width:8ch;max-width:36ch;overflow-wrap:anywhere}
.report-display-math{max-width:100%;overflow:auto;padding:.35em .15em;overflow-wrap:normal}.katex-display{margin:.6em 0}.katex-display>.katex{white-space:nowrap;text-align:left}
.report-inline-math{display:inline-block;max-width:100%;overflow:auto;padding:.25em .1em;vertical-align:middle;line-height:normal;white-space:nowrap;overflow-wrap:normal}
.report-figure{max-width:100%;margin:1.4em 0}.report-figure summary{cursor:zoom-in;list-style:none}.report-figure summary::-webkit-details-marker{display:none}.report-image-hint{display:block;color:#526273;font-size:.8em}
.report-image-viewport{display:block;max-width:100%;overflow:auto}.report-image-viewport img{margin:0 auto}.report-figure details[open] summary{cursor:zoom-out}.report-figure details[open] .report-image-viewport{max-height:80vh}.report-figure details[open] img{max-width:none;margin:0}
:where([tabindex],summary,a):focus-visible{outline:2px solid #1756a9;outline-offset:2px}
@media print{main{max-width:none;padding:0}.report-image-hint{display:none}.report-figure details[open] img{max-width:100%}.report-figure details[open] .report-image-viewport{max-height:none}}
</style></head><body><main>${body}</main></body></html>`;
}

async function main() {
  const args = process.argv.slice(2);
  const report = args.shift();
  let htmlPath;
  if (args[0] === '--html' && args[1]) { args.shift(); htmlPath = path.resolve(args.shift()); }
  if (!report || args.length) throw new Error('Usage: node scripts/render_report.mjs REPORT.md [--html PREVIEW.html]');
  const reportPath = path.resolve(report);
  if (htmlPath === reportPath || (htmlPath && path.extname(htmlPath).toLowerCase() !== '.html')) {
    throw new Error('Preview must be a separate .html file; refusing to overwrite report source.');
  }
  const source = await fs.readFile(reportPath, 'utf8');
  const result = await validateMarkdown(source, { reportPath });
  if (htmlPath && result.ok) {
    await fs.mkdir(path.dirname(htmlPath), { recursive: true });
    await fs.writeFile(htmlPath, await previewDocument(result.html, path.basename(reportPath)));
  }
  // An unsuccessful check never generates a new preview. Consumers must check ok/exit code,
  // rather than trusting an older file that may still exist at the requested destination.
  const { html, ...summary } = result;
  console.log(JSON.stringify({ ...summary, preview: result.ok ? htmlPath ?? null : null }, null, 2));
  process.exitCode = result.ok ? 0 : 1;
}

if (process.argv[1] && pathToFileURL(await fs.realpath(process.argv[1])).href === import.meta.url) {
  main().catch(error => {
    console.log(JSON.stringify({ ok: false, errors: [{ code: 'render-runtime', message: `${error.message}. If dependencies are missing, run npm ci --ignore-scripts in the skill directory.` }] }, null, 2));
    process.exitCode = 2;
  });
}
