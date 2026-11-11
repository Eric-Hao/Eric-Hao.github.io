import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateMarkdown } from '../vendor/paper-deep-reader/render_report.mjs';
const content = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('bilingual math compiles to accessible KaTeX', async () => {
  const r = await validateMarkdown('The loss is $x^2$.\n\n损失为 $x^2$。\n\n$$\nx^2 + y^2 = 1\n$$', {reportPath:path.join(content,'report.md')});
  assert.equal(r.ok,true); assert.equal(r.counts.inlineMath,2); assert.equal(r.counts.displayMath,1);
  assert.match(r.html,/katex-mathml/); assert.match(r.html,/损失为/);
});
test('malformed math is rejected rather than silently displayed', async () => {
  const r = await validateMarkdown('$$\n\\badmacro{a}\n$$');
  assert.equal(r.ok,false); assert.ok(r.errors.length);
});
test('raw executable HTML is rejected', async () => {
  const r = await validateMarkdown('<script>alert(1)</script>'); assert.equal(r.ok,false);
});
test('table mismatch is rejected and correct table has a scroll wrapper', async () => {
  assert.equal((await validateMarkdown('|A|B|\n|-|-|\n|1|2|3|')).ok,false);
  const r=await validateMarkdown('|A|B|\n|-|-|\n|1|2|'); assert.equal(r.ok,true); assert.match(r.html,/report-table-scroll/);
});
test('remote unverified images are rejected', async () => {
  const r=await validateMarkdown('![Unverified](https://example.com/image.png)'); assert.equal(r.ok,false);
});
test('verified local image is embedded and has an original-size control', async () => {
  const r=await validateMarkdown('![Figure 3 / 图3](assets/crops/figure-3-p004-verified.png)',{reportPath:path.join(content,'deep-read/cpga/report.md')});
  assert.equal(r.ok,true); assert.equal(r.counts.images,1); assert.match(r.html,/data:image\/png;base64/); assert.match(r.html,/<details>/);
});

const { assertMarkdownInputs } = await import('../deep_read_security.mjs');
test('integration rejects executable links, including references and entities', async () => {
  for (const md of ['[x](javascript:alert%281%29)', '[x](data:text/html;base64,PHNjcmlwdD4=)', '[x][a]\n\n[a]: javascript:alert%281%29', '[x](javascript&#58;alert%281%29)']) {
    await assert.rejects(assertMarkdownInputs(md,content),/Unsafe link scheme/);
  }
});
test('integration allows ordinary source links, citations and mail addresses', async () => {
  await assertMarkdownInputs('[Paper](https://arxiv.org/abs/2603.27703v1) [Figure](#figure-1) [Mail](mailto:example@example.org)',content);
});
test('integration disallows inline and reference images outside the report root', async () => {
  const reportDir=path.join(content,'deep-read/cpga');
  await assert.rejects(assertMarkdownInputs('![x](../../package.json)',reportDir),/escapes/);
  await assert.rejects(assertMarkdownInputs('![x][a]\n\n[a]: ../../package.json',reportDir),/escapes/);
});
