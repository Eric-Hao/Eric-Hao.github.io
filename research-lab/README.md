# Research Lab

An English-only research journal at `/research-lab/`, covering language models,
generative vision, restoration, and fluid dynamics. All 22 established article
URLs are preserved.

## Editorial rebuild

The current edition contains 21 newly written explanations based directly on
original papers or the release's model card, approximately 19,400 words in total.
No previous article prose is used by the authoring pipeline. The remaining route,
`vortex-bursting`, is a short source-availability page: a matching original
manuscript could not be located, so its previous scientific narrative is not
republished. An original PDF or verified publisher/author link is needed.

Each article uses four to seven sections suited to its argument rather than a fixed chapter template:
research question, mechanism, evidence, and limits. The selected source figures
are explained where they support the argument. Numerical comparisons retain
benchmark settings and distinguish reported results from independent replication.
Source inconsistencies are identified rather than silently corrected.

The visual design uses an off-white canvas, restrained rules, serif titles,
compact topic filters, and a narrow reading column. Full paper identity and author credit appear near the title; an accessible collapsible contents panel remains available on narrow screens. At widths of 1100px and above,
the illustrated index contains five cards per row, with compact 4:3 thumbnails on desktop. Coverless entries use two
columns on desktop. Narrow layouts use two illustrated columns and one text
column. There is no animated or black hero. Existing conceptual cover artwork is
retained as illustration; article figures come from the original research.

## Source of truth

- `_content/editorial/catalog.json`: bibliographic metadata and established routes.
- `_content/editorial/<key>.json`: independent English article, figure provenance,
  primary-source references, and claim-level page/table/section evidence pointers.
- `_content/build_editorial.py`: the only page builder. The old `build_home.py`
  and `build_articles.py` commands are compatibility entry points to this builder.
- `_content/styles/research.css`: all page styles. `site.css` is generated.
- `_content/render_math.mjs`: a small KaTeX-only build step. It does not use the
  previous paper-reading skill or its renderer.
- `app.js`: accessible filtering, search, figure dialogs, citation copying, and
  reading-section highlighting. No external JavaScript is loaded.
- `citations/`: original BibTeX entries. The source-unavailable entry does not
  offer an unverified citation for copying.
- `_content/source-figures.json`: retained source-asset provenance. Original
  source PDFs and extracted text are local research inputs, not required to build.

Obsolete bilingual prose, template builders, and the previous vendored renderer
have been retired from the active pipeline. Git history retains earlier versions.
Source figures can be positioned between the paragraphs that explain them, and selected opening sections can appear as unboxed introductory prose. All writing is safely escaped; optional inline emphasis and mathematics are the
only supported prose formatting. Links are limited to HTTP(S), image paths stay
inside the site, and all formulas are compiled with KaTeX trust disabled.

## Build and test

From the repository root, with Python 3.9+ and Node 20+:

```sh
npm ci --ignore-scripts --prefix research-lab/_content
python3 research-lab/_content/build_editorial.py
npm test --prefix research-lab/_content
```

The test command runs eleven authoring/security unit tests and the static site
checker. It verifies all 23 pages, 22 preserved routes, English-only text, figure
paths, references, anchors, duplicate IDs, math compilation, source notices, and
index completeness. The verified rebuild passes 1,310 static checks.

The full site's production build uses its existing locked Ruby/Jekyll environment:

```sh
source /workspace/scratch/b7ea28637fb3/cloud-ruby/activate.sh
JEKYLL_ENV=production bundle _2.2.19_ exec jekyll build --safe
```

Browser QA uses the supported internal managed preview, not a public deployment.
Desktop (1168 CSS pixels) and narrow (389 CSS pixels using browser zoom) reviews
cover all article routes, page overflow, loaded images, math, and source notices.
The index's five/two-column desktop layout, topic/search/reset controls, repeated
figure opening, Escape/close, focus restoration, and citation copying are checked.
The narrow review is responsive desktop-browser testing, not real-device testing.

## Publishing

Keep changes local until the owner approves publication. A local preview does not
change GitHub Pages. When publication is approved, build and verify the final tree
again, then confirm the exact remote commit and deployment outcome.
