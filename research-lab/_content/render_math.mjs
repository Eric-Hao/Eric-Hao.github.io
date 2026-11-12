import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import katex from 'katex';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const decode = s => s.replace(/&quot;/g, '"').replace(/&#x27;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
let count = 0;
for (const dir of fs.readdirSync(path.join(root, 'articles'))) {
  const filename = path.join(root, 'articles', dir, 'index.html');
  let html = fs.readFileSync(filename, 'utf8');
  let pageCount = 0;
  html = html.replace(/<(span|div) class="(math-inline|equation)" data-math="([^"]*)"( data-display="true")?><\/\1>/g, (_, tag, cls, tex, display) => {
    count++; pageCount++;
    return `<${tag} class="${cls}">${katex.renderToString(decode(tex), {displayMode: !!display, throwOnError: true, trust: false, strict: 'error', output: 'htmlAndMathml'})}</${tag}>`;
  });
  if (pageCount) html = html.replace('</head>', '<link rel="stylesheet" href="../../fonts/katex/katex.min.css"></head>');
  fs.writeFileSync(filename, html);
}
console.log(`Rendered ${count} math expressions with KaTeX.`);
