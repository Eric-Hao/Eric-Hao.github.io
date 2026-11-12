"""Build Research Lab from independent, English source-based editorial records.

No previous article text, translation, or report renderer is imported. Run from any cwd.
"""
from pathlib import Path
from html import escape
from urllib.parse import urlparse
import hashlib, json, re, subprocess

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / '_content' / 'editorial'
CATALOG = json.loads((CONTENT / 'catalog.json').read_text())
COVERS = json.loads((ROOT / '_content' / 'covers.json').read_text())
CATEGORY = {
 'Large Language Models': ('Language & agents', 'language'),
 'Generative AI': ('Generative models', 'generative'),
 'Restoration & Super-Resolution': ('Vision & restoration', 'vision'),
 'Physics & Fluid Dynamics': ('Physics & fluids', 'physics'),
}
SITE = 'https://eric-hao.github.io/research-lab/'
e = lambda x: escape(str(x), quote=True)


def version(path):
 return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:12]


def safe_url(url):
 if not url: return ''
 if urlparse(url).scheme not in ('https', 'http'): raise ValueError(f'Unsafe URL: {url}')
 return e(url)


def validate(record):
 key = record['key']
 for field in ('title', 'standfirst', 'thesis', 'sections', 'source', 'status'):
  if field not in record: raise ValueError(f'{key}: missing {field}')
 if record['status'] not in ('complete', 'source-unavailable'): raise ValueError(key)
 ids = set()
 for section in record['sections']:
  if not re.fullmatch(r'[a-z0-9-]+', section['id']) or section['id'] in ids: raise ValueError(f'{key}: section id')
  ids.add(section['id'])
  if not section.get('paragraphs'): raise ValueError(f'{key}: empty section')
  if fig := section.get('figure'):
   if not fig['src'].startswith('images/') or '..' in fig['src'] or not (ROOT / fig['src']).is_file(): raise ValueError(f'{key}: missing figure {fig["src"]}')
   if not all(fig.get(x) for x in ('alt', 'caption', 'sourceLabel', 'sourceUrl')): raise ValueError(f'{key}: incomplete figure provenance')
   safe_url(fig['sourceUrl'])
  if section.get('figure_after') is not None and (not section.get('figure') or not 1 <= section['figure_after'] <= len(section['paragraphs'])): raise ValueError(f'{key}: invalid figure placement')
  if table := section.get('table'):
   if not all(len(row) == len(table['headers']) for row in table['rows']): raise ValueError(f'{key}: malformed table')
 if re.search('[\u4e00-\u9fff]', json.dumps(record, ensure_ascii=False)): raise ValueError(f'{key}: non-English copy')
 if record['status'] == 'complete' and not record.get('evidence'): raise ValueError(f'{key}: evidence required')
 return record


def rich(text):
 text = str(text)
 # Only small, controlled inline formatting. Raw HTML remains text.
 pieces = re.split(r'(\$[^$\n]+\$)', text)
 for i, piece in enumerate(pieces):
  if piece.startswith('$') and piece.endswith('$'):
   pieces[i] = f'<span class="math-inline" data-math="{e(piece[1:-1])}"></span>'
  else:
   pieces[i] = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', e(piece))
 return ''.join(pieces)


def head(title, description, prefix='', canonical=''):
 return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · Research Lab</title><meta name="description" content="{e(description)}">
<link rel="canonical" href="{SITE}{e(canonical)}"><meta property="og:type" content="{'article' if canonical else 'website'}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{SITE}{e(canonical)}">
<meta name="theme-color" content="#f9f8f4"><link rel="stylesheet" href="{prefix}site.css?v={version('site.css')}"><script src="{prefix}app.js?v={version('app.js')}" defer></script></head>
<body><a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><a class="wordmark" href="{prefix or './'}" aria-label="Research Lab home"><span class="brand-mark" aria-hidden="true"></span>Research Lab<span class="wordmark-by">by Jinhua Hao</span></a><nav aria-label="Main navigation"><a href="{prefix or './'}">Research</a><a href="{prefix}../">About the author <span aria-hidden="true"><span class="arrow-icon" aria-hidden="true"></span></span></a></nav></header>'''


def footer(prefix=''):
 return f'''<footer class="site-footer"><a class="footer-brand" href="{prefix or './'}">Research Lab</a><p>Research explained through its methods, results, and open questions.</p><a href="{prefix}../">Jinhua Hao <span aria-hidden="true"><span class="arrow-icon" aria-hidden="true"></span></span></a></footer>'''


def venue_label(paper):
 if paper['image'] == 'vortex-bursting': return 'Source unavailable'
 venue = paper['venue']
 year = str(paper.get('year') or '')
 return venue + (' ' + year if year and year not in venue else '')


def meta(paper):
 return f'<span>{e(venue_label(paper))}</span><span aria-hidden="true">·</span><span>{e(CATEGORY[paper["cats"][0]][0])}</span>'


def card(paper, record, cover):
 key = paper['image']; category = CATEGORY[paper['cats'][0]][1]
 search = ' '.join([paper['title'], record['title'], paper['authors'], paper['venue'], paper['cats'][0]])
 attrs = f'data-category="{category}" data-search="{e(search.lower())}"'
 if cover:
  return f'''<article class="paper-card" {attrs}><a href="{e(paper['article'])}" class="card-link"><div class="cover"><img src="{e(cover['thumbnail'])}" width="{cover['width']}" height="{cover['height']}" alt="" loading="lazy"><span class="cover-label">Research note <span aria-hidden="true"><span class="arrow-icon" aria-hidden="true"></span></span></span></div><div class="card-meta">{meta(paper)}</div><h3>{e(record['title'])}</h3></a></article>'''
 return f'''<article class="text-card" {attrs}><a class="text-card-link" href="{e(paper['article'])}"><div><div class="card-meta">{meta(paper)}</div><h3>{e(record['title'])}</h3><p>{e(record['standfirst'])}</p>{'<span class="source-tag">Manuscript unavailable</span>' if record['status'] != 'complete' else ''}</div><span class="card-arrow" aria-hidden="true"><span class="arrow-icon" aria-hidden="true"></span></span></a></article>'''


def build_index(records):
 parts = [head('Research', 'Original research on language models, generative vision, and fluid dynamics. Clear explanations, primary sources, and the limits of the evidence.')]
 parts.append('''<main id="main" class="index-main"><section class="index-intro"><div><p class="eyebrow">Research notes & technical reports</p><h1>Research</h1></div><p class="index-description">Language models, generative vision, and fluid dynamics.<br>Methods, results, and limitations from the original research.</p></section>
<section class="research-browser" aria-label="Browse research"><div class="browse-bar"><div class="filters" role="group" aria-label="Filter by topic"><button type="button" class="filter is-active" data-filter="all" aria-pressed="true">All research</button>''')
 for label, key in CATEGORY.values(): parts.append(f'<button type="button" class="filter" data-filter="{key}" aria-pressed="false">{e(label)}</button>')
 parts.append('''</div><label class="search"><span class="sr-only">Search research</span><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><input type="search" placeholder="Search papers" autocomplete="off" id="research-search"></label></div><p class="results-count" aria-live="polite" aria-atomic="true">22 entries</p>''')
 with_covers = [p for p in CATALOG if p['image'] in COVERS and records[p['image']]['status'] == 'complete']
 without_covers = [p for p in CATALOG if p not in with_covers]
 for heading, cls, papers in [('Research articles', 'paper-grid', with_covers), ('Reports & papers', 'text-grid', without_covers)]:
  parts.append(f'<section class="collection"><div class="collection-heading"><h2>{heading}</h2><span>{"Illustrated research notes" if cls == "paper-grid" else "Methods & evaluations"}</span></div><div class="{cls}">')
  for paper in papers: parts.append(card(paper, records[paper['image']], COVERS.get(paper['image']) if cls == 'paper-grid' else None))
  parts.append('</div></section>')
 parts.append('<div class="empty-state" hidden><h2>No matching papers</h2><p>Try another title, author, or topic.</p><button type="button" id="reset-search">Clear filters</button></div></section></main>')
 parts.append(footer()); parts.append('</body></html>')
 (ROOT / 'index.html').write_text('\n'.join(parts))


def render_figure(figure):
 return f'''<figure class="paper-figure"><button class="figure-open" data-image="../../{e(figure['src'])}" data-caption="{e(figure['caption'])}" type="button" aria-label="Enlarge figure: {e(figure['alt'])}"><img src="../../{e(figure['src'])}" alt="{e(figure['alt'])}" loading="lazy"><span class="figure-zoom" aria-hidden="true">View larger <span class="arrow-icon" aria-hidden="true"></span></span></button><figcaption>{rich(figure['caption'])}<span class="figure-source">Source: <a href="{safe_url(figure['sourceUrl'])}" target="_blank" rel="noopener noreferrer">{e(figure['sourceLabel'])} <span class="arrow-icon" aria-hidden="true"></span></a></span></figcaption></figure>'''


def build_article(paper, record, records):
 prefix = '../../'; key = paper['image']
 parts = [head(record['title'], record['standfirst'], prefix, paper['article'])]
 words = len(' '.join(p for s in record['sections'] for p in s['paragraphs']).split())
 reading = max(2, round(words / 220))
 parts.append(f'''<main id="main" class="article-main"><div class="article-breadcrumb"><a href="../../">All research</a><span aria-hidden="true">/</span><span>{e(CATEGORY[paper['cats'][0]][0])}</span></div><header class="article-header"><p class="eyebrow">{e(venue_label(paper))} <span aria-hidden="true">/</span> {reading} min read</p><h1>{e(record['title'])}</h1><p class="standfirst">{rich(record['standfirst'])}</p><div class="article-actions">''')
 if paper.get('url'): parts.append(f'<a class="source-button" href="{safe_url(paper["url"])}" target="_blank" rel="noopener noreferrer">Read the original <span aria-hidden="true"><span class="arrow-icon" aria-hidden="true"></span></span></a>')
 for link in paper.get('links', []): parts.append(f'<a href="{safe_url(link["url"])}" target="_blank" rel="noopener noreferrer">{e(link["label"])} <span aria-hidden="true"><span class="arrow-icon" aria-hidden="true"></span></span></a>')
 parts.append('<a href="#citation">Cite this paper</a></div>')
 authors = paper['authors'].split(', ')
 short_authors = ', '.join(authors[:3]) + ', et al.' if len(authors) > 6 else paper['authors']
 parts.append(f'<div class="publication-line"><p class="publication-title">{e(paper["title"])}</p><p class="publication-authors">{e(short_authors)} <a href="#citation">Publication details</a></p></div></header>')
 parts.append('<div class="article-layout"><aside class="article-aside"><nav class="desktop-contents" aria-label="In this article"><p class="eyebrow">In this article</p>')
 for section in record['sections']:
  if not section.get('intro'): parts.append(f'<a href="#{e(section["id"])}">{e(section["title"])}</a>')
 parts.append('</nav><details class="mobile-contents"><summary>In this article</summary><nav aria-label="Article sections">')
 for section in record['sections']:
  if not section.get('intro'): parts.append(f'<a href="#{e(section["id"])}">{e(section["title"])}</a>')
 parts.append('</nav></details><div class="aside-source"><span class="eyebrow">Source</span><p>')
 if record['source'].get('url'): parts.append(f'<a href="{safe_url(record["source"]["url"])}">{e(record["source"]["label"])} <span class="arrow-icon" aria-hidden="true"></span></a>')
 else: parts.append(e(record['source']['label']))
 parts.append('</p></div></aside><article class="article-body">')
 if record['status'] != 'complete': parts.append('<div class="source-notice" role="note"><strong>Source unavailable</strong><p>The original manuscript is needed before a research explanation can be published. No conclusions have been reconstructed from the previous article.</p></div>')

 for section in record['sections']:
  parts.append(f'<section id="{e(section["id"])}" class="essay-section{ " essay-intro" if section.get("intro") else "" }">')
  if not section.get('intro'): parts.append(f'<h2>{e(section["title"])}</h2>')
  for i, paragraph in enumerate(section['paragraphs'], 1):
   parts.append(f'<p>{rich(paragraph)}</p>')
   if section.get('figure') and section.get('figure_after') == i: parts.append(render_figure(section['figure']))
  if equation := section.get('equation'): parts.append(f'<div class="equation" data-math="{e(equation)}" data-display="true"></div>')
  if section.get('figure') and not section.get('figure_after'): parts.append(render_figure(section['figure']))
  if table := section.get('table'):
   parts.append(f'<div class="results-table" tabindex="0" role="region" aria-label="{e(table["caption"])}"><table><caption>{e(table["caption"])}</caption><thead><tr>')
   for header in table['headers']: parts.append(f'<th scope="col">{e(header)}</th>')
   parts.append('</tr></thead><tbody>')
   for row in table['rows']:
    parts.append('<tr>')
    for i, cell in enumerate(row):
     tag = 'th' if i == 0 else 'td'
     attr = ' scope="row"' if i == 0 else ''
     parts.append(f'<{tag}{attr}>{e(cell)}</{tag}>')
    parts.append('</tr>')
   parts.append('</tbody></table></div>')
   if table.get('note'): parts.append(f'<p class="table-note">{rich(table["note"])}</p>')
  parts.append('</section>')
 parts.append(f'<section class="paper-details" id="citation"><p class="eyebrow">{'Original publication' if record['status'] == 'complete' else 'Unverified catalog entry'}</p><h2>{e(paper["title"])}</h2><p class="paper-authors">{e(paper["authors"])}</p><p>{e(paper["venue"])}</p>')
 bib_path = ROOT / 'citations' / f'{key}.bib'
 if bib_path.exists() and record['status'] == 'complete':
  parts.append(f'<details class="citation"><summary>BibTeX citation</summary><button type="button" class="copy-citation">Copy citation</button><pre>{e(bib_path.read_text())}</pre><span class="copy-status" role="status"></span></details>')
 parts.append('<h3>Sources & reading</h3><ol class="references">')
 for reference in record.get('references', []): parts.append(f'<li><a href="{safe_url(reference["url"])}" target="_blank" rel="noopener noreferrer">{e(reference["label"])} <span class="arrow-icon" aria-hidden="true"></span></a></li>')
 parts.append('</ol><p class="editorial-note">Results are quoted from the cited sources and have not been independently reproduced for this note.</p></section></article></div>')
 related = [p for p in CATALOG if p['image'] != key and p['cats'][0] == paper['cats'][0]][:3]
 if related:
  parts.append('<section class="related"><div class="collection-heading"><h2>Continue reading</h2><a href="../../">All research <span class="arrow-icon" aria-hidden="true"></span></a></div><div class="related-grid">')
  for p in related:
   parts.append(f'<a href="../../{e(p["article"])}"><span class="card-meta">{e(p["venue"])}</span><h3>{e(records[p["image"]]["title"])}</h3><span aria-hidden="true"><span class="arrow-icon" aria-hidden="true"></span></span></a>')
  parts.append('</div></section>')
 parts.append('</main>'); parts.append(footer(prefix))
 parts.append('''<dialog class="image-viewer" aria-label="Research figure viewer"><button type="button" class="viewer-close" aria-label="Close figure">Close ×</button><div class="viewer-content"><img alt=""><p></p></div></dialog></body></html>''')
 (ROOT / paper['article'] / 'index.html').write_text('\n'.join(parts))


def main():
 records = {p['image']: validate(json.loads((CONTENT / f'{p["image"]}.json').read_text())) for p in CATALOG}
 if set(records) != {p['image'] for p in CATALOG}: raise ValueError('Catalog mismatch')
 (ROOT / 'site.css').write_text((ROOT / '_content' / 'styles' / 'research.css').read_text())
 build_index(records)
 for paper in CATALOG: build_article(paper, records[paper['image']], records)
 (ROOT / 'data.js').write_text('const papers = ' + json.dumps([{**paper, 'headline': records[paper['image']]['title']} for paper in CATALOG], ensure_ascii=False, indent=2) + ';\n')
 # Small, independently implemented KaTeX build step; no previous reader code.
 subprocess.run(['node', str(ROOT / '_content' / 'render_math.mjs')], check=True)
 print(f'Built index and {len(records)} English editorial routes.')

if __name__ == '__main__': main()
