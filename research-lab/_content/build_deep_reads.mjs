/** Render paired Markdown with the pinned paper-deep-reader rendering engine. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { validateMarkdown } from './vendor/paper-deep-reader/render_report.mjs';
import { assertMarkdownInputs } from './deep_read_security.mjs';

const content = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(content);
const reports = path.join(content, 'deep-read');
const escape = text => text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const headings = [
  ['Elevator pitch', '核心思想一句话总结'],
  ['Background & motivation', '论文背景与动机'],
  ['The core method', '核心方法 / 模型详解'],
  ['Experiments & results', '实验与结果分析'],
  ['Contribution & impact', '论文的贡献与影响'],
  ['Conclusion', '结论'],
];

async function blockHtml(markdown, directory, key, assets) {
  await assertMarkdownInputs(markdown, directory);
  const result = await validateMarkdown(markdown, { reportPath: path.join(directory, 'report.md') });
  if (!result.ok) throw new Error(`${key}: ${JSON.stringify(result.errors)}`);
  let html = result.html;
  for (const match of html.matchAll(/src="(data:image\/([^;]+);base64,([^"]+))"/g)) {
    const bytes = Buffer.from(match[3], 'base64');
    const extension = ({ 'svg+xml': 'svg', 'jpeg': 'jpg' })[match[2]] || match[2];
    const digest = crypto.createHash('sha256').update(bytes).digest('hex').slice(0, 20);
    const name = `${digest}.${extension}`;
    const output = path.join(root, 'images', 'deep-read', key, name);
    await fs.mkdir(path.dirname(output), { recursive: true });
    await fs.writeFile(output, bytes);
    const url = `../../images/deep-read/${key}/${name}`;
    assets.add(url);
    html = html.replaceAll(match[1], url);
  }
  return html.replaceAll('<img ', '<img loading="lazy" decoding="async" ');
}

await fs.mkdir(path.join(root, 'fonts', 'katex'), { recursive: true });
const katexDir = path.join(content, 'node_modules', 'katex', 'dist');
await fs.cp(path.join(katexDir, 'fonts'), path.join(root, 'fonts', 'katex', 'fonts'), { recursive: true });
await fs.copyFile(path.join(katexDir, 'katex.min.css'), path.join(root, 'fonts', 'katex', 'katex.min.css'));
await fs.copyFile(path.join(content, 'node_modules', 'katex', 'LICENSE'), path.join(root, 'fonts', 'katex', 'LICENSE'));
const selected = process.argv.slice(2);
const directories = selected.length ? selected : (await fs.readdir(reports, { withFileTypes: true })).filter(x => x.isDirectory()).map(x => x.name).sort();
const rendered = {};
for (const key of directories) {
  if (!/^[a-z0-9_-]+$/.test(key)) throw new Error(`Invalid report key: ${key}`);
  const directory = path.join(reports, key);
  let data;
  try { data = JSON.parse(await fs.readFile(path.join(directory, 'report.json'), 'utf8')); }
  catch (error) { if (error.code === 'ENOENT') continue; throw error; }
  if (data.status !== 'complete') continue; // Unverified reports never replace the existing note.
  const assets = new Set();
  const sections = [];
  for (const [i, section] of data.sections.entries()) {
    const parts = [`<section id="section-${i}" class="article-chapter deep-read-section"><h2><span>${i + 1}. ${headings[i][0]}</span><span class="zh" lang="zh-CN">${headings[i][1]}</span></h2>`];
    for (const [j, block] of section.blocks.entries()) {
      if (block.shared) parts.push(`<div class="shared-block">${await blockHtml(block.shared, directory, key, assets)}</div>`);
      else {
        parts.push(`<div class="bilingual-block" data-pair="${i + 1}-${j + 1}">`);
        for (const language of ['en', 'zh']) {
          parts.push(`<div class="lang-${language}" lang="${language === 'zh' ? 'zh-CN' : 'en'}">${await blockHtml(block[language], directory, key, assets)}</div>`);
        }
        parts.push('</div>');
      }
    }
    parts.push('</section>');
    sections.push(parts.join('\n'));
  }
  const toc = '<nav class="article-toc" aria-label="Contents / 目录"><ol>' + headings.map(([en, zh], i) => `<li><a href="#section-${i}">${escape(en)}<span lang="zh-CN">${escape(zh)}</span></a></li>`).join('') + '</ol></nav>';
  const sourceNote = `<aside class="source-note" aria-label="Source and verification / 来源与核验"><div lang="en">${await blockHtml(data.source_note.en, directory, key, assets)}</div><div class="lang-zh" lang="zh-CN">${await blockHtml(data.source_note.zh, directory, key, assets)}</div></aside>`;
  const sourceMap = JSON.parse(await fs.readFile(path.join(directory, 'source_map.json'), 'utf8'));
  const firstSource = sourceMap.paper.sources[0];
  const sourceUrl = typeof firstSource === 'string' ? firstSource : firstSource.location || firstSource.url;
  if (!/^https:\/\//.test(sourceUrl || '')) throw new Error(`${key}: a verified HTTPS primary source is required`);
  const reviewedSource = `<p class="reviewed-source"><a href="${escape(sourceUrl)}">Reviewed source / 本次核验版本</a></p>`;
  rendered[key] = { title: data.title, dek: data.dek, source_url: sourceUrl, html: sourceNote + reviewedSource + toc + sections.join('\n'), assets: [...assets], blocks: data.sections.reduce((n, s) => n + s.blocks.length, 0) };
  console.log(`Rendered ${key}: ${rendered[key].blocks} blocks, ${assets.size} assets`);
}
await fs.writeFile(path.join(content, 'deep-read-rendered.json'), JSON.stringify(rendered));
