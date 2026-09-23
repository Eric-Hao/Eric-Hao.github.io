from pathlib import Path
import json,html
r=Path(__file__).resolve().parents[1];e=html.escape
papers=json.loads((r/'data.js').read_text().removeprefix('const papers = ').rstrip(';\n'))
briefs=json.loads((r/'_content/research-briefs.json').read_text())
content=json.loads((r/'_content/articles.json').read_text());translations=json.loads((r/'_content/zh.json').read_text());figures=json.loads((r/'_content/figures.json').read_text());benchmarks={d['id']:d for d in json.loads((r/'_content/kat-benchmarks.json').read_text())}
author_roles=json.loads((r/'_content/author-roles.json').read_text())['roles']
def zh(t):return '<span class="zh" lang="zh-CN">'+e(t)+'</span>'
category_zh={'Large Language Models':'大语言模型','Generative AI':'生成式人工智能','Super-Resolution & Restoration':'超分辨率与复原','Physics & Fluid Dynamics':'物理与流体动力学'}
resource_zh={'Code':'代码','Post':'相关文章','Project':'项目主页','PKU News':'北大新闻'}
for p in papers:
 key=p['image'];c=content[key];z=translations[key];f=figures[key];folder=r/p['article'];folder.mkdir(parents=True,exist_ok=True)
 native=json.loads((r/'_content/source-figures.json').read_text()).get(key,[])
 author_html=e(p['authors']).replace('Jinhua Hao','<strong>Jinhua Hao</strong>')
 roles=author_roles.get(key,[])
 role_html=('<p class="author-role">Jinhua Hao · '+e(' · '.join(roles))+'</p>') if roles else ''
 brief=briefs[key]
 cover_html=f'''<section class="research-brief brief-{e(brief['theme'])}" aria-label="Research at a glance">
 <div class="brief-scene" style="background-image:url('../../images/brief-backgrounds/{e(brief['theme'])}.webp')">
 <div class="brief-sheet"><p class="brief-kicker">THE CHALLENGE</p><h2>{e(brief['challenge'])}<span lang="zh-CN">{e(brief['challengeZh'])}</span></h2></div></div>
 <div class="brief-question"><p class="brief-kicker">THE IDEA</p><p class="brief-prompt">{e(brief['title'])}<span lang="zh-CN">{e(brief['titleZh'])}</span></p><p class="brief-answer">{e(brief['solution'])}<span lang="zh-CN">{e(brief['solutionZh'])}</span></p><div class="brief-bottom"><span>{e(p['venue'])}</span><a href="#section-0">Explore the approach <span aria-hidden="true">↑</span></a></div></div></section>'''
 def render_figure(fig):
  original=fig.get('original',fig['full'])
  return f'<figure class="article-figure"><a href="../../{e(fig["full"])}" data-original="../../{e(original)}" data-zoom data-caption="{e(fig["label"])}"><img src="../../{e(fig["thumbnail"])}" alt="{e(fig["label"])}" width="{fig["width"]}" height="{fig["height"]}" loading="lazy"></a><figcaption>{e(fig["label"])} · <a href="../../{e(original)}" target="_blank" rel="noopener">Original figure</a> · <a href="{e(fig["source"])}">Paper source</a></figcaption></figure>'
 sections=''
 for i,(h,t) in enumerate(c['sections']):
  english=t.split('\n\n');chinese=z['sections'][i][1].split('\n\n')
  paragraphs=''.join('<p>'+e(en)+'</p>'+('<p class="zh" lang="zh-CN">'+e(chinese[j])+'</p>' if j<len(chinese) else '') for j,en in enumerate(english))
  heading='' if i==0 else f'<h2>{e(h)}{zh(z["sections"][i][0])}</h2>'
  sections+=f'<section id="section-{i}" class="{"article-opening" if i==0 else "article-chapter"}">{heading}{paragraphs}</section>'
  if i==1:sections+=render_figure(native[0] if native else f)
  if i==3 and len(native)>1:sections+=render_figure(native[1])
 resources=''.join(f'<a href="{e(l["url"])}">{e(l["label"])}</a>' for l in p['links'])
 related=[x for x in papers if x!=p and any(cat in x['cats'] for cat in p['cats'])][:2]
 related_html=''.join(f'<a href="../../{e(x["article"])}"><span>{e(x["venue"])}</span><h3>{e(x["headline"])}{zh(x["headlineZh"])}</h3><span aria-hidden="true">↗</span></a>' for x in related)
 bib=(r/'citations'/f'{key}.bib').read_text();page_note=f' · PDF page {f["page"]}' if 'page' in f else ''
 caption=f'{f["label"]}{page_note}.'
 if key=='magknot':caption+=' Original homepage image (800 px).'
 chart_note=''
 if key in benchmarks:
  b=benchmarks[key];headers=['Scaffold','KAT V2','Opus 4.6'] if key=='kat-v2' else ['Model','Score']
  table='<table><caption>'+e(b['title'])+' (%)</caption><thead><tr>'+''.join('<th scope="col">'+e(h)+'</th>' for h in headers)+'</tr></thead><tbody>'
  for row in b['rows']:table+='<tr><th scope="row">'+e(row[0])+'</th>'+''.join('<td>'+str(v)+('*' if key=='kat-v2' and row[0]=='Claude Code' and j==1 else '')+'</td>' for j,v in enumerate(row[1:]))+'</tr>'
  chart_note='<details class="benchmark-data"><summary>Data &amp; evaluation setup / 数据与评测条件</summary>'+table+'</tbody></table><p>'+e(b['note'])+zh(b['noteZh'])+'</p><a href="'+e(b['source'])+'">'+e(b['sourceLabel'])+' ↗</a></details>'
 (folder/'index.html').write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{e(c['dek'])}"><title>{e(c['headline'])} — Jinhua Hao</title><link rel="icon" href="../../../images/favicon.ico"><link rel="stylesheet" href="../../style.css"><link rel="stylesheet" href="../../article.css"><link rel="stylesheet" href="../../bilingual.css"><script src="../../reader.js" defer></script><script src="../../brief-layout.js" defer></script><script src="../../physics-particles.js" defer></script></head>
<body class="article-page"><a class="skip" href="#article">Skip to article</a><header><a class="wordmark" href="../../">Jinhua Hao</a><nav aria-label="Main navigation"><a href="../../#directions">Explore topics</a><a href="https://eric-hao.github.io/">Academic homepage ↗</a></nav></header>
<main id="article"><div class="article-heading"><a class="back-link" href="../../#directions">← Explore topics</a><p class="article-meta">{e(p['venue'])} · {e(p['cats'][0])}</p><h1>{e(c['headline'])}</h1><p class="article-title-zh" lang="zh-CN">{e(z['headline'])}</p><p class="article-dek">{e(c['dek'])}{zh(z['dek'])}</p><div class="article-actions"><a class="primary-link" href="{e(p['url'])}">{'Model card' if key=='kat-v25-dev' else 'Read the paper'}</a>{resources}</div></div>
{cover_html}<div class="article-layout"><article class="prose">{sections}{chart_note}<section class="paper-details" id="paper-details"><h2>Paper &amp; authors{zh('论文与作者')}</h2><p class="original-title"><a href="{e(p['url'])}">{e(p['title'])} ↗</a></p><p class="article-authors">{author_html}</p>{role_html}</section><section id="cite" class="citation"><h2>Cite this work</h2><div class="citation-actions"><button type="button" data-copy-bib aria-controls="bibtex">Copy BibTeX </button></div><pre><code id="bibtex">{e(bib)}</code></pre><p class="copy-status" role="status" aria-live="polite"></p></section></article></div>
<section class="related"><h2>Continue reading</h2><div>{related_html}</div></section></main></body></html>''')
print('Built',len(papers),'bilingual blogs with high-resolution figures and BibTeX.')
