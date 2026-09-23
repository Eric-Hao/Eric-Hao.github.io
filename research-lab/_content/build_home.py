from pathlib import Path
import json,html
r=Path(__file__).resolve().parents[1];e=html.escape
papers=json.loads((r/'data.js').read_text().removeprefix('const papers = ').rstrip(';\n'))
figures=json.loads((r/'_content/covers.json').read_text())
originals=json.loads((r/'_content/figures.json').read_text())
categories=[('Large Language Models','大语言模型','models'),('Generative AI','生成式人工智能','generative-models'),('Super-Resolution & Restoration','超分辨率与复原','super-resolution'),('Physics & Fluid Dynamics','物理与流体动力学','physics')]
for p in papers:p['homeCategory']=p['cats'][0]
prefix=(r/'_content/home-prefix.html').read_text().replace('</head>','<script src="reader.js" defer></script><script src="physics-particles.js" defer></script></head>')
parts=[prefix,'<nav id="directions" class="topic-nav" aria-label="Research topics / 研究方向">']
for en,cn,slug in categories:parts.append(f'<a href="#{slug}">{en}<span class="zh" lang="zh-CN">{cn}</span></a>')
parts.append('</nav>')
priority={'kat-v25-dev':-4,'kat-v25':-3,'kat-v2':-2,'lpm':-1}
for en,cn,slug in categories:
 layout="research-list" if slug=="super-resolution" else "research-grid"
 parts.append(f'<section id="{slug}" class="topic-section" aria-labelledby="heading-{slug}"><div class="section-heading"><h2 id="heading-{slug}">{en}<span class="zh" lang="zh-CN">{cn}</span></h2></div><div class="{layout}">')
 for p in sorted(papers,key=lambda p:priority.get(p['image'],0)):
  if p['homeCategory']!=en:continue
  if layout=='research-list':
   parts.append(f'<article class="research-row"><p class="paper-meta">{e(p["venue"])}</p><h3><a href="{e(p["article"])}">{e(p["title"])}<span class="zh" lang="zh-CN">{e(p["headlineZh"])}</span></a></h3></article>')
   continue
  f=figures[p['image']];is_chart=False
  key=p['image'];physics=key in ('magvortex','magknot','vortex')
  target=originals[key]['full'] if physics else f['full']
  attrs=(f'data-physics="{key}" data-paper-original="{e(target)}" data-particle-large="images/physics-large/{key}.png"') if physics else ''
  parts.append(f'''<article class="research-card"><a class="research-cover{' chart-cover' if is_chart else ''}" href="{e(target)}" {attrs} data-zoom data-caption="{e(p['headline'])} — {e(f['label'])}" aria-label="Enlarge figure: {e(p['headline'])}"><img src="{e(f['thumbnail'])}" alt="{e(f['label'])}: {e(p['title'])}" loading="lazy" width="{f['width']}" height="{f['height']}"></a><div class="card-copy"><p class="paper-meta">{e(p['venue'])}</p><h3><a href="{e(p['article'])}"><span class="card-title-en">{e(p['headline'])}</span><span class="zh" lang="zh-CN">{e(p['headlineZh'])}</span></a></h3></div></article>''')
 parts.append('</div></section>')
parts.append('</main></body></html>')
(r/'index.html').write_text(''.join(parts))
print('Built',len(papers),'research entries across four topics (2024 restoration uses lists).')
