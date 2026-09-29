# Research Notes

Standalone research site at https://eric-hao.github.io/research-lab/, linked from
the academic homepage's navigation, profile and News section.

## Content and design

22 bilingual articles across Large Language Models, Generative AI,
Restoration & Super-Resolution, and Physics & Fluid Dynamics. The homepage has
three KAT release cards, twelve paper image cards and seven restoration rows.
Titles open articles; images open a keyboard-accessible viewer (Escape or click
the image to close). Physics covers open the original paper figure.

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
- `_content/articles.json`, `_content/zh.json`: article text.
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

Rebuild from the repository root with Python 3.9+:

```sh
python3 research-lab/_content/build_home.py
python3 research-lab/_content/build_articles.py
```

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
