# Research Notes

A standalone static research site at https://eric-hao.github.io/research-lab/.
The original academic homepage links here through its September 2026 News entry.

## Content and presentation

21 bilingual paper stories in four topics: Large Language Models, Generative AI,
Super-Resolution & Restoration, and Physics & Fluid Dynamics. Three independent KAT model-release cards precede twelve paper image cards
and six compact restoration entries. Titles open articles;
images open a keyboard-accessible viewer. Every article includes source links,
original paper figures, author information and formatted BibTeX.

Article introductions use accessible HTML challenge/idea cards over four generated
painted backgrounds. Homepage covers use paper-inspired pixel collages. The three
physics covers use procedural Canvas particles; they are conceptual illustrations,
not simulation results. Clicking them opens the paper figure, with a separate
particle-interpretation option. Animation stops offscreen, when the document is
hidden, and for reduced-motion preferences. There are no visible pause controls.

Current assets are resolved by `_content/covers.json` (v5/v6). Old generated artwork
and native Canvas test previews are ignored by Git and retained locally only.
Original paper assets are retained in `images/source/` and `images/figures/`.
Fonts are bundled Lora and Poppins with their SIL Open Font licenses.

## Editing

- `data.js`: metadata, categories and article routes.
- `_content/articles.json`, `_content/zh.json`: English and Chinese text.
- `_content/research-briefs.json`: article opening challenges and ideas.
- `_content/author-roles.json`: roles explicitly documented on the academic homepage.
- `_content/source-figures.json`, `_content/figures.json`: figure sources and extraction metadata.
- `citations/`: BibTeX entries.
- `physics-particles.js`: live physics cover geometry.
- `reader.js`: image viewer and citation copying.
- `brief-layout.js`: responsive half-height dialogue overlap.

Rebuild from the repository root with Python 3.9+:

```sh
python3 research-lab/_content/build_home.py
python3 research-lab/_content/build_articles.py
```

The generated HTML, CSS, JavaScript, fonts and images are served directly by the
existing GitHub Pages site; no additional frontend build is required. `_content`
is authoring material and is excluded automatically by Jekyll's underscore rule.

## Review

Local validation covers all 21 articles, three model releases, 12 image cards, six list entries, local links,
anchors, citation structure and JavaScript syntax. Native Canvas rendering checks
all three physics covers. Browser visual verification is unavailable because the
Tabbit runtime is not connected. The original academic-site files are preserved
except for the requested News link.

## Asset cleanup

Unreferenced generated PNGs, obsolete crops, contact sheets and intermediate
cover prompts were removed in September 2026. Current cover metadata and paper
figure provenance remain alongside the content and build scripts. Rebuilding
produces the identical published HTML. A local archive outside the repository
preserves the removed experiments. Git history is unchanged.

## KAT model pages

`_content/kat-models.json` stores the three release cards and source-attributed
benchmark matrices. `model_components.py` renders shared components. Dev scores
come from the Hugging Face model card; V2.5 and V2 retain the report tables,
missing values, scaffold labels and starred external-source exceptions. Original
report figures remain available at native resolution; Dev explicitly identifies
the shared V2.5 infrastructure figure. No generated benchmark images are used.
