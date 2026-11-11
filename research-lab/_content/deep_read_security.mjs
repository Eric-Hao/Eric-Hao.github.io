/** Site policy around the unchanged, pinned report renderer. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { unified } from 'unified';
import remarkParse from 'remark-parse';

export async function assertMarkdownInputs(markdown, directory) {
  const tree = unified().use(remarkParse).parse(markdown);
  const nodes = [];
  const visit = node => { nodes.push(node); for (const child of node.children || []) visit(child); };
  visit(tree);
  const definitions = new Map(nodes.filter(x => x.type === 'definition').map(x => [x.identifier, x.url]));
  for (const node of nodes.filter(x => x.type === 'link' || x.type === 'linkReference')) {
    const url = node.url || definitions.get(node.identifier);
    if (!url) throw new Error('Unresolved link reference');
    // Browsers discard ASCII controls while interpreting schemes. Reject schemes
    // after the same normalization, including entity-decoded Markdown URLs.
    const normalized = url.replace(/[\u0000-\u0020\u007f]/g, '');
    const scheme = normalized.match(/^([a-z][a-z\d+.-]*):/i)?.[1].toLowerCase();
    if (scheme && !['https', 'http', 'mailto'].includes(scheme)) throw new Error(`Unsafe link scheme: ${scheme}`);
  }
  const root = await fs.realpath(directory);
  for (const node of nodes.filter(x => x.type === 'image' || x.type === 'imageReference')) {
    const url = node.url || definitions.get(node.identifier);
    if (!url) throw new Error('Unresolved image reference');
    if (/^[a-z][a-z\d+.-]*:/i.test(url) || url.startsWith('//')) throw new Error('Images must be local verified assets');
    const target = await fs.realpath(path.resolve(directory, decodeURIComponent(url)));
    if (!target.startsWith(root + path.sep)) throw new Error('Image escapes its report directory');
  }
}
