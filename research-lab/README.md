# Research Notes

An independent English-language research journal at `/research-lab/`.
The 22 established article URLs are preserved.

## Measured layout references

- Index: https://openai.com/zh-Hans-CN/research/index/
- Panel view: https://openai.com/zh-Hans-CN/research/index/?display=grid
- Selected article template: https://openai.com/zh-Hans-CN/index/measuring-how-ai-agents-handle-wet-lab-science/

This implementation follows the selected template rather than combining different
OpenAI article templates. The page has an illustrated full-bleed hero, lower-left
headline, and centered reading column. Other OpenAI articles can use different
hero layouts.

Measured features include responsive type sizes and leading, 32px desktop / 24px
mobile gutters, list metadata columns, 32px list row padding, square panel images,
24px horizontal / 80px vertical grid gaps, and the article reading column. The
panel layout uses four columns at 1200px and above, three at 768–1199px, two at 360–767px, and one below 360px. Default is panel; explicit list-view URLs and in-page switching remain available.
Mobile panels use 16px gaps, 16px untruncated titles, wrapping 12px metadata, and whole-card links.
The compact header contains Home and Blog text links, with no footer.

Topic, year/type filtering, five sorting orders, and list/panel controls remain.
State is reflected in the URL and survives reload and history navigation. Search
UI, visible result count, article breadcrumb, reading-time/author strip, separate
banner caption, and contents heading were removed. Accessible live count and
legacy `q` URL handling remain without visible controls. Article source figures,
provenance, citations, and related research are retained.

The independent Research Notes identity, topic names, article text, and illustrations are
not replaced with OpenAI branding or content. Consequently, differences in text
length and illustration composition produce different line wraps and hero
heights even where the layout measurements are equal. This is not a claim of
whole-page screenshot identity or an OpenAI affiliation.

## Fonts and artwork

Typography uses OpenAI Sans and OpenAI Sans SC. Font files, original notices,
source/version information, and checksums are retained in `fonts/openai/`.
This project does not grant permission to reuse these fonts elsewhere.
The font-enabled rendering was checked for both English and Chinese. System
Latin/CJK fallbacks remain available if a font request fails.

All 22 conceptual covers were generated for this project. Their media vary by
subject: ink illustration, paper collage, engraving, photographic concepts, and
scientific field-line imagery. Full 1254px-square WebP images and 640px thumbnails live in `images/covers-index-2026/`; `_content/covers.json` and
`_content/cover-prompts-2026.json` document the assets. These are conceptual art,
not experimental figures, real photographs, or model evaluation outputs. Original paper figures remain separately attributed.

## Editorial content

All 22 entries now have complete English explanations with source evidence.
`vortex-bursting` was integrated from the supplied manuscript and reviewed source
record. Its DOI, 10.1017/jfm.2026.12259, is transcribed from the supplied PDF; the
DOI and final publication metadata have not been independently verified. No final
volume or article number has been invented. That qualification appears in the
article, bibliography, and source reference.

The existing 21 other article records and scientific claims are unchanged.
Publication years, not invented day-level dates, drive chronological sorting.
Within a year the original catalog order is preserved.

## Source of truth

- `_content/editorial/catalog.json`: bibliography and established routes.
- `_content/editorial/<key>.json`: article prose and evidence pointers.
- `_content/build_editorial.py`: page builder; compatibility entry points call it.
- `_content/styles/research.css`: CSS source; `site.css` is generated.
- `_content/covers.json`: illustration paths and provenance.
- `app.js`: browsing controls, history state, figure viewer, citation copying.
- `_content/render_math.mjs`: KaTeX build step with trust disabled.
- `citations/`: BibTeX records.

Prose is escaped. Only controlled inline emphasis and mathematics are supported;
links are limited to HTTP(S) and image paths stay local.

## Build and verify

From the repository root, with Python 3.12+ and Node 20+:

```sh
npm ci --ignore-scripts --prefix research-lab/_content
python3 research-lab/_content/build_editorial.py
npm test --prefix research-lab/_content
node --check research-lab/app.js
JEKYLL_ENV=production bundle _2.2.19_ exec jekyll build --safe
```

The current build passes 37 unit tests and 1,684 static checks across all 23
pages. Tests cover route preservation, figures, references, browsing controls,
duplicate IDs, escaping, mathematical rendering, and editorial records.
Browser review covers desktop, tablet-width, and narrow responsive viewports.
These are desktop-browser responsive checks, not real-device tests.

The supplied private manuscript PDF is not a publishing asset. Only its
authorized figure excerpts and the source-based explanation are included.

## Model introductions and ordering

KAT-Coder-V2.5, KAT-Coder-V2.5-Dev, KAT-Coder-V2, and LPM are classified as Models and lead the default Featured ordering, in that order. The three KAT introductions appear together before LPM. Newest and Oldest use date values only, without featured pinning. Records with only a year retain year-level precision rather than invented month/day values. Model metadata stores date, date_kind, and date_source: release dates for V2 and V2.5, report-first-publication for LPM, and repository-history date for Dev. These are historical introductions, not statements of current service availability. The four model pages use centered headings on white and a separate banner; other articles retain their layouts.

Within the same year, records without month/day precision keep catalog order; exact-day records sort by their documented dates. No January 1 date is displayed or claimed for year-only entries.

## Reproduce model-cover typography

Install Python dependencies `Pillow`, `fontTools`, and `Brotli` in your build environment. The four background-only WebP assets live in `images/covers-index-2026/backgrounds/`; the renderer loads `fonts/openai/OpenAISans-Bold.woff2` directly, decodes it through fontTools, and uses that font in Pillow. There is no system-font or bitmap-font fallback: a missing font or dependency fails the render.

From the repository root:

```sh
python3 -m pip install Pillow fontTools Brotli
python3 research-lab/_content/render_cover_type.py
python3 research-lab/_content/build_editorial.py
npm test --prefix research-lab/_content
```

All four covers use OpenAI Sans Bold on a 1254px square canvas, with 190px line advance. KAT covers use 170px type; LPM uses the separately approved larger 240px type. Individual lines are centered by their rendered glyph bounding boxes; the combined glyph block is centered vertically. The command regenerates full-size WebP files and 640px thumbnails and updates the shared typography metadata in covers.json.

## Continue reading

Article recommendations show up to four other articles from the same topic, in the existing catalog order. Current-article links and duplicates are excluded; physics articles have three eligible peers and are not padded with unrelated items. The layout uses four columns at desktop widths, two at 360–1023px, and one below 360px.

## List thumbnails

List view reuses each existing square cover at 128px on desktop, 80px on mobile, and 64px below 360px. Metadata and untruncated titles sit to the right; summaries remain on desktop and are hidden on mobile. Each row stays one accessible article link. Missing covers fall back to a full-width text row. Panel layout is unchanged.
