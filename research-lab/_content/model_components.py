"""Accessible release cards and source-attributed benchmark matrices."""
from html import escape as e

def release_card(key, model, article):
 return f'''<article class="model-release"><h3><a href="{e(article)}">{e(model['name'])}</a></h3><p class="release-summary">{e(model['summary'])}<span class="zh" lang="zh-CN">{e(model['summaryZh'])}</span></p><dl><div><dt>Release</dt><dd>{e(model['date'])}</dd></div><div><dt>Type</dt><dd>{e(model['kind'])}</dd></div><div><dt>Focus</dt><dd>{e(model['focus'])}</dd></div></dl><a class="release-button" href="{e(article)}">Explore model <span aria-hidden="true">→</span></a></article>'''

def benchmark_tables(model):
 out=['<section class="model-evaluations" id="evaluations"><h2>Model evaluations<span class="zh" lang="zh-CN">模型评测</span></h2><p class="evaluation-intro">Published results, with the evaluation setting kept alongside each comparison. Scores are percentages; higher is better. Bold marks the highest reported value in each row, including ties.<span class="zh" lang="zh-CN">保留原始评测条件；分数单位为百分比，越高越好。粗体表示每行已报告数值中的最高值（含并列）。</span></p>']
 for i,t in enumerate(model['tables']):
  label=f"benchmark-caption-{i}";note=f"benchmark-note-{i}"
  out.append(f'<div class="benchmark-scroll" role="region" aria-labelledby="{label}" tabindex="0"><table class="model-benchmark" aria-describedby="{note}"><caption id="{label}">{e(t["title"])}</caption><thead><tr><th scope="col">Benchmark</th>')
  out.extend(f'<th scope="col" class="{"kat-column" if j==0 else ""}">{e(m)}</th>' for j,m in enumerate(t['models']))
  out.append('</tr></thead><tbody>')
  for row in t['rows']:
   best=max(x for x in row['values'] if x is not None)
   out.append(f'<tr><th scope="row">{e(row["benchmark"])}<span>{e(row["detail"])}</span></th>')
   for j,v in enumerate(row['values']):
    value='—' if v is None else f'{v:g}%'
    value+=e(row.get('markers',{}).get(str(j),''))
    if v==best:value=f'<strong>{value}</strong>'
    if 'subvalues' in row:value+=f'<small>{e(row["subvalues"][j])}</small>'
    out.append(f'<td class="{"kat-column" if j==0 else ""}">{value}</td>')
   out.append('</tr>')
  out.append(f'</tbody></table></div><p class="benchmark-note" id="{note}">{e(t["note"])} <a href="{e(t["source"])}">Source data</a></p>')
 out.append('</section>')
 return ''.join(out)
