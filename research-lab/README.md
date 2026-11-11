# Research Notes

Standalone research site at https://eric-hao.github.io/research-lab/, linked from
the academic homepage's navigation, profile and News section.

## Content and design

22 bilingual articles across Large Language Models, Generative AI,
Restoration & Super-Resolution, and Physics & Fluid Dynamics. The homepage has
three KAT release cards, twelve paper image cards and seven restoration rows.
Titles open articles; images open a keyboard-accessible viewer (Escape or click
the image to close). Physics covers open the original paper figure.

The 2026-11-11 refactor contains 21 source-checked deep reads and one retained
legacy note (`vortex-bursting`), whose full manuscript could not be verified.
The retained note displays a source-gap notice; its original five chapters are
unchanged. All 22 article URLs, citation blocks and navigation routes remain.

Each complete deep read has six sections: elevator pitch, background and
motivation, core method, experiments and results, contributions and impact, and
conclusion. English and Chinese paragraphs are paired in the canonical source.
Equations are compiled to KaTeX during the build, with accessible MathML and
locally bundled fonts. Verified figures and tables sit next to their reading
guidance, observations and evidence limits. Figures can toggle between fit-width
and original size; large formulas and tables scroll locally. Numerical results
are reported from the cited sources, not independently reproduced experiments.

The page uses a near-white background, Lora serif headings and system sans-serif
supporting text. Covers, release cards and restoration hover surfaces share 12px
corners. Article captions are centered; citations retain compact monospace text.
KAT evaluation tables preserve source settings and use centered cells.

The hero cycles through reasoning, creating and understanding in Lora particle
lettering. Physics covers use procedural Canvas particles. These are conceptual
illustrations, not simulation results. Animations stop offscreen or when the tab
is hidden; reduced-motion preferences show static particles.

## Editing

- `data.js`: paper metadata, categories and article routes.
- `_content/deep-read/<key>/report.json`: source of truth for completed deep
  reads. Every prose block has nonempty `en` and `zh` fields; neutral equations
  or verified images may use `shared`. The schema requires exactly six sections.
- `report.md` is exported from the paired JSON for strict report validation.
  `source_map.json` records the checked source version and claim evidence.
  `assets/visual_manifest.json` inventories numbered source objects and identifies
  the selected, visually reviewed assets. Local downloads, extracted text,
  unselected candidates, previews and scratch scripts are not versioned.
- `_content/deep_read_content.py`: validates the paired content contract and
  exports Markdown. `build_deep_reads.mjs` renders it with the pinned upstream
  engine; `deep_read_security.mjs` restricts link schemes and image paths.
- `_content/rewrites/*.json`: retained legacy prose and fallback. Each entry holds
  `headline`, `dek`, three `keypoints` and five `sections` with English and
  Chinese paragraphs side by side, so a rewrite cannot drift out of parity.
  Edit here, then run `python3 research-lab/_content/merge_articles.py`, which
  regenerates `articles.json` and `zh.json`, syncs `headlineZh` in `data.js` and
  validates that every section has an English counterpart for each paragraph.
- `_content/articles.json`, `_content/zh.json`: generated article text.
- `_content/research-briefs.json`: article opening challenges and ideas.
- `_content/author-roles.json`: documented author roles.
- `_content/covers.json`: current homepage cover selections.
- `_content/source-figures.json`, `_content/figures.json`: paper figure provenance.
- `_content/kat-models.json`: release cards and source-attributed evaluation data.
- `_content/kat-downloads.json`: dated download-count evidence and scope.
- `citations/`: BibTeX entries.
- `app.js`: hero particles and restoration entry animation.
- `physics-particles.js`: physics cover geometry and animation lifecycle.
- `reader.js`: image viewer, article back navigation and citation copying.
- `brief-layout.js`: responsive article opening-card overlap.

Rebuild from the repository root with Python 3.9+ and Node.js 20+:

```sh
npm ci --ignore-scripts --prefix research-lab/_content
python3 research-lab/_content/build_home.py
python3 research-lab/_content/build_articles.py
npm test --prefix research-lab/_content
python3 -m unittest discover -s research-lab/_content/tests -p 'test_*.py'
python3 research-lab/_content/verify_deep_reads.py
```

The builder exports `report.md`, validates and compiles every Markdown block,
externalizes only verified local images to `images/deep-read/`, and copies KaTeX
assets to `fonts/katex/`. It does not need the original PDFs to rebuild an existing
report. The upstream renderer is vendored unchanged from paper-deep-reader
v4.0.1, commit `ab5e934`; attribution and license are in `_content/vendor/`.

To repeat the complete paper-deep-reader checks after editing prose, install that
pinned skill separately and run:

```sh
python3 research-lab/_content/verify_deep_reads.py --skill-dir /path/to/paper-deep-reader
```

The final 2026-11-11 check covered 759 bilingual prose pairs and 338 numbered
source objects, including all 291 designated key objects. All 21 strict report
checks passed with zero errors or warnings. The site checker covers all 23 HTML
pages, route preservation, six-section structure, paired counts, local assets,
anchors, duplicate IDs and the untouched source-blocked chapters. The main site's full production safe build also passed with Ruby 3.2.2,
Bundler 2.2.19 and Jekyll 3.10.0 after configuring the cloud environment; all
43 locked gems were installed without changing `Gemfile.lock`. The resulting
homepage and all 22 research routes passed local link, anchor and asset checks.
The configured toolchain is activated with
`source /workspace/scratch/b7ea28637fb3/cloud-ruby/activate.sh`. Desktop browser QA at a
1168px viewport passed for all 22 articles: no document-wide horizontal overflow,
KaTeX errors or failed loaded image assets. Visual review covered the homepage,
research index, bilingual prose, formulas, KAT tables and source-gap notice.
Figure expansion/collapse, repeated image-viewer opening, Escape/close and article
forward/back navigation passed. The review caught and fixed legacy disclosure
styles rotating and squeezing report figures; two Python regression tests cover
those fixes. Narrow responsive review at 389 CSS pixels, using ordinary browser
zoom, also passed for the homepage, research index and all 22 articles. It caught
and fixed a legacy sidebar rule hiding source notices on narrow screens; the
provenance and source-gap notices now remain visible while the sidebar stays
collapsed. Formula/table overflow remains inside its scroll container. Nine
Python and nine Node tests pass. These are desktop-browser responsive checks,
not real-device or touch emulation tests.

Both builders regenerate `site.css` and fingerprint CSS/JavaScript URLs. Do not
edit generated HTML or CSS. Author styles in `_content/styles/`:

- `design.css`: shared tokens, covers, cards, interactions and responsive layout.
- `editorial.css`: article typography, citations and evaluation tables.
- `legacy-*.css`: compatibility rules; migrate components to the design layer
  when changing them rather than adding overrides here.

Cascade order is `legacy`, `design`, `editorial`, with no runtime CSS imports.
Fonts and images resolve relative to `research-lab/`. Bundled Lora and Poppins
retain their SIL Open Font licenses. Original scientific figures preserve their
aspect ratios and remain in `images/source/` and `images/figures/`.

## KAT model pages

`model_components.py` renders release cards and benchmark matrices. Dev scores
come from its Hugging Face model card; V2.5 and V2 retain report tables, missing
values, scaffold labels and starred external-source exceptions. Display values
use one decimal while JSON retains source precision. Original report figures
remain available; Dev identifies its shared V2.5 infrastructure figure.

## Review and local archive

Review generated pages for local links, anchors, assets, citation structure,
responsive overflow and JavaScript errors. The main academic homepage additionally
requires the repository's Jekyll/Bundler environment to build. Podman can provide
Ruby 3.2.2 and Bundler 2.2.19 without changing the host Ruby installation. Build
with `JEKYLL_ENV=production bundle _2.2.19_ exec jekyll build --safe`; the explicit
empty `baseurl` in `_config.yml` keeps domain-root asset URLs consistent locally.
The Gemfile lists the site's renderer and plugins explicitly; avoid restoring the
`github-pages` umbrella dependency while it pins a vulnerable, unused remote-theme
ZIP library. JSON must remain at version 2.21.2 or newer.
On macOS, a Git archive in `/private/tmp` can avoid Desktop bind-mount issues.

Unused generated covers, candidate prompts and particle previews are stored
outside this repository in the local `../arxiv/research-lab-20260929/` directory.
Its manifest records original paths and SHA-256 checksums for recovery. These
experiments must not be committed or published. Only selected artwork remains
in the website. Earlier experiments also exist in the separate local
`../research-lab-local-archive-20260923/` directory.

The generated site is served directly by GitHub Pages. `_content` is authoring
material, excluded by Jekyll's underscore rule. Keep changes local until the
owner explicitly requests pushing or publishing.
