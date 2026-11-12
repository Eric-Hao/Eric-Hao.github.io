"""Build Research Lab from independent, English source-based editorial records.

No previous article text, translation, or report renderer is imported. Run from any cwd.
"""
from pathlib import Path
from html import escape
from urllib.parse import urlparse
import hashlib, json, re, subprocess
from datetime import date

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
<meta name="theme-color" content="#ffffff"><link rel="stylesheet" href="{prefix}fonts/openai/openai-fonts.css"><link rel="stylesheet" href="{prefix}site.css?v={version('site.css')}"><script src="{prefix}app.js?v={version('app.js')}" defer></script></head>
<body class="{'article-page' if canonical else 'index-page'}"><a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><a class="home-link" href="{prefix}../" aria-label="Home"><svg class="nav-wordmark" width="56" height="28" viewBox="0 0 56 28" aria-hidden="true"><text x="0" y="21">Home</text></svg></a><a class="blog-link" href="{prefix or './'}" aria-label="Blog"><svg class="nav-wordmark" width="44" height="28" viewBox="0 0 44 28" aria-hidden="true"><text x="0" y="21">Blog</text></svg></a></header>'''


def footer(prefix=''):
 return ''


def venue_label(paper):
 if paper.get('date'):
  stamp = date.fromisoformat(paper['date'])
  label = {'release': 'Released', 'report': 'Report', 'repository': 'Repository'}[paper['date_kind']]
  return f"{label} {stamp.strftime('%b')} {stamp.day}, {stamp.year}"
 venue = paper['venue']
 year = str(paper.get('year') or '')
 return venue + (' ' + year if year and year not in venue else '')


def meta(paper):
 return f'<span>{e(venue_label(paper))}</span><span aria-hidden="true">·</span><span>{e(CATEGORY[paper["cats"][0]][0])}</span>'


def publication_type(paper):
 if paper.get('content_type') == 'models': return ('Models', 'models')
 venue = paper['venue'].lower()
 if 'model release' in venue: return ('Model release', 'release')
 if 'arxiv' in venue or 'technical report' in venue: return ('Preprint & report', 'report')
 return ('Publication', 'publication')


def card_label(paper):
 return 'Models' if publication_type(paper)[1] == 'models' else CATEGORY[paper['cats'][0]][0]


def chronological_value(paper):
 # A year-only record keeps its known precision; no month/day is invented.
 return int(paper['date'].replace('-', '')) if paper.get('date') else (paper.get('year') or 0) * 10000


def featured_order(paper):
 return (paper.get('featured_rank', 999), -chronological_value(paper), CATALOG.index(paper))


def icon(name):
 paths = {
  'home': '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/>',
  'filter': '<path d="M4 6h10m4 0h2M4 17h2m4 0h10"/><circle cx="16" cy="6" r="2"/><circle cx="8" cy="17" r="2"/>',
  'chevron': '<path d="m6 9 6 6 6-6"/>',
  'grid': '<rect x="4" y="4" width="6" height="6" rx=".5"/><rect x="14" y="4" width="6" height="6" rx=".5"/><rect x="4" y="14" width="6" height="6" rx=".5"/><rect x="14" y="14" width="6" height="6" rx=".5"/>',
  'list': '<path d="M9 5h11M9 12h11M9 19h11M4 5h.01M4 12h.01M4 19h.01"/>',
  'search': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
 }
 return f'<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">{paths[name]}</svg>'


def card(paper, record, cover):
 key = paper['image']; category = CATEGORY[paper['cats'][0]][1]
 search = ' '.join([paper['title'], record['title'], record['standfirst'], paper['authors'], paper['venue'], paper['cats'][0]])
 kind, kind_key = publication_type(paper)
 attrs = f'data-category="{category}" data-search="{e(search.lower())}" data-year="{paper.get("year") or "unknown"}" data-type="{kind_key}" data-title="{e(record["title"])}" data-order="{CATALOG.index(paper)}" data-date="{chronological_value(paper)}" data-featured="{paper.get("featured_rank", 999)}"'
 image = f'<div class="cover"><img src="{e(cover["thumbnail"])}" width="{cover["width"]}" height="{cover["height"]}" alt="" loading="lazy" decoding="async"></div>' if cover else ''
 return f'''<article class="research-card" {attrs}><a href="{e(paper['article'])}" class="card-link">{image}<div class="card-meta"><span class="card-category">{e(card_label(paper))}</span><span class="card-venue">{e(venue_label(paper))}</span></div><div class="card-copy"><h2>{e(record['title'])}</h2><p>{e(record['standfirst'])}</p></div></a></article>'''


def build_index(records):
 parts = [head('Research', 'Research on language models, generative vision, and fluid dynamics. Methods, results, and limitations from the original sources.')]
 parts.append('''<main id="main" class="index-main"><header class="index-intro"><h1>Research</h1></header>
<section class="research-browser" aria-label="Browse research"><div class="browse-bar"><div class="filters" role="group" aria-label="Filter by topic"><button type="button" class="filter is-active" data-filter="all" aria-pressed="true">All</button>''')
 for label, key in CATEGORY.values(): parts.append(f'<button type="button" class="filter" data-filter="{key}" aria-pressed="false">{e(label)}</button>')
 parts.append(f'''</div><div class="browse-tools"><button class="tool-button" id="filter-toggle" type="button" aria-controls="filter-panel" aria-expanded="false" data-popover="filter-panel">Filter <span class="filter-count" hidden></span>{icon('filter')}</button><button class="tool-button" type="button" aria-controls="sort-panel" aria-expanded="false" data-popover="sort-panel">Sort {icon('chevron')}</button><div class="view-switch" role="group" aria-label="Research view"><button type="button" class="view-button is-active" data-view="grid" aria-label="Panel view, show images" aria-pressed="true" title="Panel view">{icon('grid')}</button><button type="button" class="view-button" data-view="list" aria-label="List view, hide images" aria-pressed="false" title="List view">{icon('list')}</button></div></div></div>
<input type="hidden" id="research-search" value="">
<div class="filter-panel popover" id="filter-panel" hidden><div class="filter-columns"><fieldset><legend>Year</legend>''')
 for year in sorted({p['year'] for p in CATALOG if p.get('year')}, reverse=True):
  parts.append(f'<label><input type="checkbox" name="year" value="{year}"><span>{year}</span></label>')
 parts.append('</fieldset><fieldset><legend>Type</legend>')
 for label, key in [('Publication', 'publication'), ('Preprint & report', 'report'), ('Models', 'models')]:
  parts.append(f'<label><input type="checkbox" name="type" value="{key}"><span>{e(label)}</span></label>')
 parts.append('</fieldset></div><div class="filter-panel-footer"><button type="button" id="clear-refinements">Clear filters</button><button type="button" data-close-popover>Cancel</button></div></div><div class="sort-panel popover" id="sort-panel" hidden><fieldset><legend class="sr-only">Sort research</legend>')
 for label, key in [('Featured', 'featured'), ('Newest first', 'newest'), ('Oldest first', 'oldest'), ('Title: A–Z', 'title'), ('Title: Z–A', 'title-desc')]:
  parts.append(f'<label><input type="radio" name="sort" value="{key}"{" checked" if key == "featured" else ""}><span>{label}</span></label>')
 parts.append('</fieldset></div><div class="results-bar sr-only"><p class="results-count" aria-live="polite" aria-atomic="true">22 entries</p><button type="button" id="clear-all" hidden>Clear all filters</button></div><div class="research-results" data-layout="grid">')
 for paper in sorted(CATALOG, key=featured_order):
  parts.append(card(paper, records[paper['image']], COVERS.get(paper['image'])))
 parts.append('</div><div class="empty-state" hidden><h2>No matching research</h2><p>Try another title, author, or topic.</p><button type="button" id="reset-search">Clear filters</button></div><noscript><p class="no-script">All research is shown below. Enable JavaScript to filter, sort, or switch views.</p></noscript></section></main>')
 parts.append(footer()); parts.append('</body></html>')
 (ROOT / 'index.html').write_text('\n'.join(parts))


def render_figure(figure):
 return f'''<figure class="paper-figure"><button class="figure-open" data-image="../../{e(figure['src'])}" data-caption="{e(figure['caption'])}" type="button" aria-label="Enlarge figure: {e(figure['alt'])}"><img src="../../{e(figure['src'])}" alt="{e(figure['alt'])}" loading="lazy"></button><figcaption>{rich(figure['caption'])}<span class="figure-source">Source: <a href="{safe_url(figure['sourceUrl'])}" target="_blank" rel="noopener noreferrer">{e(figure['sourceLabel'])} <span class="arrow-icon" aria-hidden="true"></span></a></span></figcaption></figure>'''


def build_article(paper, record, records):
 prefix = '../../'; key = paper['image']
 parts = [head(record['title'], record['standfirst'], prefix, paper['article'])]
 cover = COVERS.get(key)
 is_model = publication_type(paper)[1] == 'models'
 background = '#fff' if is_model else (cover.get('background', '#f1f1ed') if cover else '#f1f1ed')
 parts.append(f'''<main id="main" class="article-main"><section class="article-hero{' model-hero' if is_model else ''}" style="--hero-bg:{e(background)}">''')
 if cover:
  parts.append(f'<div class="article-banner" aria-hidden="true"><img src="../../{e(cover.get("full", cover["thumbnail"]))}" width="{cover.get("fullWidth", cover["width"])}" height="{cover.get("fullHeight", cover["height"])}" alt="" fetchpriority="high"></div>')
 parts.append(f'<header class="article-header"><p class="eyebrow"><span>{e(venue_label(paper))}</span><span>{e(card_label(paper))}</span></p><h1>{e(record["title"])}</h1><p class="standfirst">{rich(record["standfirst"])}</p></header></section>')
 parts.append('<div class="article-layout"><aside class="article-aside"><nav class="desktop-contents" aria-label="In this article">')
 for section in record['sections']:
  if not section.get('intro'): parts.append(f'<a href="#{e(section["id"])}">{e(section["title"])}</a>')
 parts.append('</nav><details class="mobile-contents"><summary>In this article</summary><nav aria-label="Article sections">')
 for section in record['sections']:
  if not section.get('intro'): parts.append(f'<a href="#{e(section["id"])}">{e(section["title"])}</a>')
 parts.append('</nav></details></aside><article class="article-body">')
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
 if record.get('publicationNote'): parts.append(f'<p>{e(record["publicationNote"])}</p>')
 parts.append('<div class="article-actions">')
 if paper.get('url'): parts.append(f'<a href="{safe_url(paper["url"])}" target="_blank" rel="noopener noreferrer">Read the original paper <span class="arrow-icon" aria-hidden="true"></span></a>')
 for link in paper.get('links', []): parts.append(f'<a href="{safe_url(link["url"])}" target="_blank" rel="noopener noreferrer">{e(link["label"])} <span class="arrow-icon" aria-hidden="true"></span></a>')
 parts.append('</div>')
 bib_path = ROOT / 'citations' / f'{key}.bib'
 if bib_path.exists() and record['status'] == 'complete':
  parts.append(f'<details class="citation"><summary>BibTeX citation</summary><button type="button" class="copy-citation">Copy citation</button><pre>{e(bib_path.read_text())}</pre><span class="copy-status" role="status"></span></details>')
 if paper.get('date_source'):
  parts.append(f'<p class="date-provenance">{e(venue_label(paper))} · <a href="{safe_url(paper["date_source"])}" target="_blank" rel="noopener noreferrer">Date source</a></p>')
 parts.append('<h3>Sources & reading</h3><ol class="references">')
 for reference in record.get('references', []): parts.append(f'<li><a href="{safe_url(reference["url"])}" target="_blank" rel="noopener noreferrer">{e(reference["label"])} <span class="arrow-icon" aria-hidden="true"></span></a></li>')
 parts.append('</ol><p class="editorial-note">Results are quoted from the cited sources and have not been independently reproduced for this note.</p></section></article></div>')
 related = [p for p in CATALOG if p['image'] != key and p['cats'][0] == paper['cats'][0]][:3]
 if related:
  parts.append('<section class="related"><div class="collection-heading"><h2>Continue reading</h2><a href="../../">All research <span class="arrow-icon" aria-hidden="true"></span></a></div><div class="related-grid">')
  for p in related:
   related_cover = COVERS.get(p['image'])
   cover_markup = f'<div class="related-cover"><img src="../../{e(related_cover["thumbnail"])}" width="{related_cover["width"]}" height="{related_cover["height"]}" alt="" loading="lazy" decoding="async"></div>' if related_cover else ''
   parts.append(f'<a href="../../{e(p["article"])}">{cover_markup}<h3>{e(records[p["image"]]["title"])}</h3><span class="card-meta">{e(venue_label(p))}</span></a>')
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
