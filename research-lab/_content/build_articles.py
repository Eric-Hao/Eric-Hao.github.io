from pathlib import Path
from asset_versions import write_page
from build_styles import build_styles
build_styles()
import json,html
from model_components import benchmark_tables
r=Path(__file__).resolve().parents[1];e=html.escape
papers=json.loads((r/'data.js').read_text().removeprefix('const papers = ').rstrip(';\n'))
briefs=json.loads((r/'_content/research-briefs.json').read_text())
content=json.loads((r/'_content/articles.json').read_text());translations=json.loads((r/'_content/zh.json').read_text());figures=json.loads((r/'_content/figures.json').read_text());benchmarks={d['id']:d for d in json.loads((r/'_content/kat-benchmarks.json').read_text())}
models=json.loads((r/'_content/kat-models.json').read_text())
author_roles=json.loads((r/'_content/author-roles.json').read_text())['roles']
def zh(t):return '<span class="zh" lang="zh-CN">'+e(t)+'</span>'
category_zh={'Large Language Models':'大语言模型','Generative AI':'生成式人工智能','Restoration & Super-Resolution':'复原与超分辨率','Physics & Fluid Dynamics':'物理与流体动力学'}
resource_zh={'Code':'代码','Post':'相关文章','Project':'项目主页','PKU News':'北大新闻'}
# Follow the homepage category order; wrap into the next topic at each boundary.
category_order=list(category_zh)
priority={'kat-v25-dev':-4,'kat-v25':-3,'kat-v2':-2,'lpm':-1}
reading_order=sorted(papers,key=lambda p:(category_order.index(p['cats'][0]),priority.get(p['image'],0)))
for p in papers:
 key=p['image'];c=content[key];z=translations[key];f=figures[key];folder=r/p['article'];folder.mkdir(parents=True,exist_ok=True)
 native=json.loads((r/'_content/source-figures.json').read_text()).get(key,[])
 roles=author_roles.get(key,[])
 role_symbols={'Corresponding author':'*','Project leader':'†'}
 markers=''.join(f'<sup class="author-marker" tabindex="0" title="{e(role)}" aria-label="{e(role)}">{role_symbols[role]}</sup>' for role in roles)
 author_html=e(p['authors']).replace('Jinhua Hao','<strong>Jinhua Hao</strong>'+markers)
 venue_html=f'<p class="publication-venue">{e(p["venue"])}</p>'
 brief=briefs[key]
 cover_html=f'''<section class="research-brief brief-{e(brief['theme'])}" aria-label="Research at a glance">
 <div class="brief-scene" style="background-image:url('../../images/brief-backgrounds/{e(brief['theme'])}.webp')">
 <div class="brief-sheet"><h2>{e(brief['challenge'])}<span lang="zh-CN">{e(brief['challengeZh'])}</span></h2></div></div>
 <div class="brief-question"><p class="brief-prompt">{e(brief['title'])}<span lang="zh-CN">{e(brief['titleZh'])}</span></p><p class="brief-answer">{e(brief['solution'])}<span lang="zh-CN">{e(brief['solutionZh'])}</span></p></div></section>'''
 def render_figure(fig):
  original=fig.get('original',fig['full'])
  return f'<figure class="article-figure"><a href="../../{e(fig["full"])}" data-original="../../{e(original)}" data-zoom data-caption="{e(fig["label"])}"><img src="../../{e(fig["thumbnail"])}" alt="{e(fig["label"])}" width="{fig["width"]}" height="{fig["height"]}" loading="lazy"></a><figcaption>{e(fig["label"])}</figcaption></figure>'
 sections=''
 for i,(h,t) in enumerate(c['sections']):
  english=t.split('\n\n');chinese=z['sections'][i][1].split('\n\n')
  paragraphs=''.join('<p>'+e(en)+'</p>'+('<p class="zh" lang="zh-CN">'+e(chinese[j])+'</p>' if j<len(chinese) else '') for j,en in enumerate(english))
  heading='' if i==0 else f'<h2>{e(h)}{zh(z["sections"][i][0])}</h2>'
  sections+=f'<section id="section-{i}" class="{"article-opening" if i==0 else "article-chapter"}">{heading}{paragraphs}</section>'
  if i==1:sections+=render_figure(native[0] if native else f)
  if i==3 and len(native)>1:sections+=render_figure(native[1])
  if i==2 and key in models:sections+=benchmark_tables(models[key])
  if i==4 and len(native)>2:sections+=''.join(render_figure(fig) for fig in native[2:])
 paper_label='Model card' if key=='kat-v25-dev' else 'Read the paper'
 paper_action=(f'<a class="primary-link" href="{e(p["url"])}">{paper_label}</a>' if p.get('url') else f'<span class="primary-link" aria-disabled="true">{paper_label}</span>')
 paper_title=(f'<a href="{e(p["url"])}">{e(p["title"])}</a>' if p.get('url') else e(p['title']))
 resources=''.join(f'<a href="{e(l["url"])}">{e(l["label"])}</a>' for l in p['links'])
 position=reading_order.index(p)
 related=[reading_order[(position+offset)%len(reading_order)] for offset in (1,2)]
 next_paper=related[0]
 related_html=''.join(f'<a href="../../{e(x["article"])}"><span>{e(x["venue"])}</span><h3>{e(x["headline"])}{zh(x["headlineZh"])}</h3></a>' for x in related)
 bib=(r/'citations'/f'{key}.bib').read_text();page_note=f' · PDF page {f["page"]}' if 'page' in f else ''
 caption=f'{f["label"]}{page_note}.'
 chart_note=''
 write_page(folder/'index.html', f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{e(c['dek'])}"><title>{e(c['headline'])} — Jinhua Hao</title><link rel="icon" href="../../../images/favicon.ico"><link rel="stylesheet" href="../../site.css"><script src="../../reader.js" defer></script><script src="../../brief-layout.js" defer></script><script src="../../physics-particles.js" defer></script></head>
<body class="article-page{' model-article' if key in models else ''}"><a class="skip" href="#article">Skip to article</a><header><nav class="article-navigation" aria-label="Article navigation">
<a class="icon-button" href="../../" aria-label="Research home / 研究主页" title="Research home / 研究主页"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m3 10 9-7 9 7M5 9v12h5v-7h4v7h5V9"/></svg></a>
<a class="icon-button" href="../../" data-history-back aria-label="Go back / 返回" title="Go back / 返回"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 5-7 7 7 7M5 12h14"/></svg></a>
<a class="icon-button" href="../../{e(next_paper['article'])}" data-next-article aria-label="Next article / 下一篇" title="Next: {e(next_paper['headline'])}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 5 7 7-7 7M5 12h14"/></svg></a>
</nav></header>
<main id="article"><div class="article-heading"><h1>{e(c['headline'])}</h1><p class="article-title-zh" lang="zh-CN">{e(z['headline'])}</p><p class="article-dek">{e(c['dek'])}{zh(z['dek'])}</p><div class="article-actions">{paper_action}{resources}</div></div>
{cover_html}<div class="article-layout"><article class="prose">{sections}{chart_note}<section class="paper-details" id="paper-details"><h2>Paper &amp; authors</h2><p class="original-title">{paper_title}</p><p class="article-authors">{author_html}</p>{venue_html}</section><section id="cite" class="citation"><h2>Cite this work</h2><div class="citation-box"><button class="icon-button citation-copy" type="button" data-copy-bib aria-controls="bibtex" aria-label="Copy BibTeX / 复制引用" title="Copy BibTeX / 复制引用"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/></svg></button><pre><code id="bibtex">{e(bib)}</code></pre></div><p class="copy-status" role="status" aria-live="polite"></p></section></article></div>
<section class="related"><h2>Continue reading</h2><div>{related_html}</div></section></main></body></html>''')
print('Built',len(papers),'bilingual blogs with high-resolution figures and BibTeX.')
