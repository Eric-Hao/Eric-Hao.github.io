"""Build responsive, accessible SVG benchmark artwork from cited numeric data."""
from pathlib import Path
import json,html,re
r=Path(__file__).resolve().parents[1]
e=html.escape
data=json.loads((r/'_content/kat-benchmarks.json').read_text())
features=json.loads((r/'_content/home-features.json').read_text())
for d in data:
 grouped=len(d['rows'][0])==3
 parts=['<svg xmlns="http://www.w3.org/2000/svg" width="440" height="440" viewBox="0 0 440 440" role="img" aria-labelledby="title desc">',f'<title id="title">{e(d["title"])}</title>',f'<desc id="desc">{e(d["note"])} '+e('; '.join(str(x) for x in d['rows']))+'</desc>', '<rect width="440" height="440" fill="#f0eee6"/>','<g font-family="Arial, Helvetica, sans-serif" fill="#26251f">',f'<text x="26" y="40" font-size="24">{e(d["title"])}</text>',f'<text x="26" y="66" font-size="15" fill="#65645c">{e(d["subtitle"])}</text>']
 if grouped:
  parts.extend(['<rect x="26" y="89" width="11" height="11" fill="#b65c3e"/><text x="44" y="100" font-size="14">KAT-Coder V2</text>','<rect x="204" y="89" width="11" height="11" fill="#999c92"/><text x="222" y="100" font-size="14">Opus 4.6</text>'])
 for i,row in enumerate(d['rows']):
  y=(136+i*79) if grouped else (108+i*(68 if len(d['rows'])==4 else 55))
  parts.append(f'<text x="26" y="{y}" font-size="18">{e(row[0])}</text>')
  for j,value in enumerate(row[1:]):
   by=y+10+j*23
   color='#b65c3e' if (grouped and j==0) or (not grouped and row[0].startswith('KAT')) else '#999c92'
   parts.append(f'<rect x="26" y="{by}" width="340" height="16" fill="#e3e1d7"/><rect x="26" y="{by}" width="{value*3.4:.2f}" height="16" fill="{color}"/>')
   label=f'{value:.1f}'+('*' if grouped and i==0 and j==1 else '')
   parts.append(f'<text x="{26+value*3.4+7:.2f}" y="{by+13}" font-size="16" fill="#26251f">{label}</text>')
 parts.extend(['<path d="M26 383H366" stroke="#bab8ae"/>','<text x="26" y="405" font-size="14" fill="#65645c">0</text>','<text x="366" y="405" text-anchor="end" font-size="14" fill="#65645c">100%</text>','<text x="414" y="427" text-anchor="end" font-size="13" fill="#65645c">Higher is better</text>','</g></svg>'])
 (r/f'images/{d["id"]}-benchmark.svg').write_text(''.join(parts))
 alt=d['title']+'. '+('; '.join(row[0]+': '+', '.join(f'{n:.1f}' for n in row[1:]) for row in d['rows']))
 table='<table><caption>'+e(d['title'])+' (%)</caption><thead><tr><th scope="col">'+('Scaffold' if grouped else 'Model')+'</th><th scope="col">'+('KAT V2' if grouped else 'Score')+'</th>'+('<th scope="col">Opus 4.6</th>' if grouped else '')+'</tr></thead><tbody>'
 for row in d['rows']:
  table+='<tr><th scope="row">'+e(row[0])+'</th>'+''.join(f'<td>{v:.1f}'+('*' if grouped and row[0]=='Claude Code' and j==1 else '')+'</td>' for j,v in enumerate(row[1:]))+'</tr>'
 table+='</tbody></table>'
 block=f'<figure class="benchmark"><a href="images/{d["id"]}-benchmark.svg" target="_blank" rel="noopener" aria-label="Enlarge {e(d["id"])} benchmark chart"><img class="kat-cover" src="images/{d["id"]}-benchmark.svg" alt="{e(alt,quote=True)}" width="440" height="440" loading="lazy"></a><figcaption><details><summary>Data &amp; source <span lang="zh-CN">数据与来源</span></summary>{table}<p>{e(d["note"])}<span class="zh" lang="zh-CN">{e(d["noteZh"])}</span></p><a href="{e(d["source"])}">{e(d["sourceLabel"])} ↗</a></details></figcaption></figure>'
 pattern=r'<figure class="benchmark">.*?</figure>|<img class="kat-cover"[^>]*>'
 # Match only this card, so rebuilding is idempotent.
 cards=features['kat'].split('<article class="kat-item">')
 for i,card in enumerate(cards):
  if f'images/{d["id"]}.png' in card or f'images/{d["id"]}-benchmark.svg' in card:
   cards[i]=re.sub(pattern,lambda _:block,card,count=1,flags=re.S)
 features['kat']='<article class="kat-item">'.join(cards)
(r/'_content/home-features.json').write_text(json.dumps(features,ensure_ascii=False,indent=2)+'\n')
print('Built three cited benchmark charts.')
