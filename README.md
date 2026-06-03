# Eric-Hao.github.io

> Personal academic homepage built with Jekyll and deployed via GitHub Pages.

<p align="center">
  <a href="https://eric-hao.github.io"><img src="https://img.shields.io/badge/Live%20Site-🎯-blue?style=flat-square" alt="Live Site"></a>
  <a href="https://github.com/Eric-Hao/Eric-Hao.github.io/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"></a>
  <a href="./README_zh.md"><img src="https://img.shields.io/badge/中文-Readme-blue?style=flat-square" alt="中文"></a>
</p>

---

## 📋 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Local Development](#-local-development)
- [Adding Content](#-adding-content)
- [Deployment](#-deployment)
- [License](#-license)

---

## 🧑‍💻 About

Built with [Jekyll](https://jekyllrb.com/) and deployed via **GitHub Pages**, based on the [AcadHomepage](https://github.com/RayeRen/acad-homepage.github.io) template with extensive customizations.

**Live site:** [https://Eric-Hao.github.io](https://Eric-Hao.github.io)

---

## ✨ Features

- **Responsive Design** — Mobile-friendly academic layout with sidebar navigation
- **Multi-section Portfolio** — Bio, News, Publications, Competitions, Projects, Honors, Education
- **Publication Showcase** — Paper teaser images with lazy loading (PNG + WebP retina-ready)
- **Google Scholar Integration** — Automatic citation stats updates via GitHub Actions (daily cron)
- **SEO Optimized** — Google Analytics, Google Search Console, Bing Webmaster, Baidu verification
- **Sitemap & Feeds** — Auto-generated `sitemap.xml` and RSS feed
- **Containerized Development** — Build via Podman/Docker, no local Ruby installation required

---

## 📁 Project Structure

```
.
├── _config.yml                  # Site configuration (author info, SEO, analytics)
├── _data/
│   └── navigation.yml           # Navigation bar links and anchors
├── _includes/                   # Reusable HTML components (head, sidebar, SEO, etc.)
├── _layouts/                    # Page layout templates
├── _pages/
│   ├── about.md                 # Main page entry point (includes all sections)
│   └── includes/
│       ├── intro.md             # Biography
│       ├── news.md              # News items
│       ├── publications.md      # Publication list with paper thumbnails
│       ├── competitions.md      # Competition results
│       ├── projects.md          # Industry projects
│       ├── honors.md            # Awards and honors
│       └── educations.md        # Education history
├── _sass/                       # SCSS stylesheets
├── assets/                      # Static assets (CSS, JS, fonts)
├── images/
│   ├── papers/                  # Publication teaser images (PNG + WebP)
│   ├── competitions/            # Competition teaser images
│   ├── projects/                # Project screenshots
│   ├── eric-hao.jpg             # Profile avatar (JPEG)
│   └── eric-hao.webp            # Profile avatar (WebP)
├── google_scholar_crawler/      # Google Scholar citation scraper (Python)
├── github_myprofile_updater/    # GitHub profile auto-updater
├── .github/workflows/           # GitHub Actions workflows
├── Gemfile                      # Ruby dependencies
├── run_server.sh                # Convenience script for local preview
└── README.md                    # This file
```

---

## 🛠 Tech Stack

| Layer       | Technology                                              |
|-------------|---------------------------------------------------------|
| **Static Site** | [Jekyll](https://jekyllrb.com/) (Ruby)              |
| **Hosting**     | [GitHub Pages](https://pages.github.com/)          |
| **Templating**  | Liquid + YAML front matter                          |
| **Styling**     | SCSS → compressed CSS                               |
| **Markup**      | Markdown (GFM via kramdown)                         |
| **SEO**         | Google Analytics, Search Console, Bing, Baidu       |
| **Automation**  | GitHub Actions (deploy + Google Scholar crawler)     |
| **Local Dev**   | Podman / Docker, Python 3 HTTP server               |

---

## 🚀 Local Development

### Prerequisites

- [**Podman**](https://podman.io/) (or Docker) — runs Jekyll in a container, no local Ruby install needed
- **Python 3** — serves the built static site for preview

```bash
podman --version   # should show 5.x+
```

> **Note:** Replace `podman` with `docker` in all commands if using Docker instead.

### Build

```bash
# Ensure _site directory exists with correct permissions
mkdir -p _site && chmod 777 _site

# Start Podman machine if not running (macOS only)
podman machine start

# Build the site
podman run --rm \
  --volume="$PWD:/srv/jekyll:Z" \
  jekyll/jekyll:4.2.2 \
  sh -c "bundle install 2>&1 | tail -1 && bundle exec jekyll build"
```

Output is generated into `_site/`.

### Preview

```bash
cd _site
python3 -m http.server 4000
```

Open **http://localhost:4000** in your browser. Press `Ctrl+C` to stop.

### One-liner (Build + Preview)

```bash
podman run --rm --volume="$PWD:/srv/jekyll:Z" jekyll/jekyll:4.2.2 \
  sh -c "bundle install 2>&1 | tail -1 && bundle exec jekyll build" \
  && cd _site && python3 -m http.server 4000
```

### Alternative: Native Ruby

A convenience script `run_server.sh` is available for native Ruby (rbenv) or Docker-based serving:

```bash
./run_server.sh
# Choose option 1 for native Ruby, option 2 for Docker
```

### Platform Notes

- **Apple Silicon (arm64):** `jekyll/jekyll:4.2.2` is a linux/amd64 image; Podman emulates it via QEMU. The `image platform does not match` warning is harmless.
- **`jekyll serve` not supported** in this container (Ruby 3.x removed `webrick`). Use `jekyll build` + Python server instead.
- **Port conflict:** Change the port if 4000 is in use: `python3 -m http.server 4001`

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `Permission denied @ dir_s_mkdir - _site` | `mkdir -p _site && chmod 777 _site` |
| `podman machine not running` | `podman machine start` |
| Port 4000 already in use | `python3 -m http.server 4001` |
| `no implicit conversion of Hash into Integer` | Use `jekyll build`, not `jekyll serve` |
| Docker volume mount errors | Omit `:Z` suffix (macOS), use `--volume="$PWD:/srv/jekyll"` |

---

## 📝 Adding Content

### New Publication

1. **Teaser image** — Add to `images/papers/` (PNG + WebP pair)
2. **Entry** — Add to `_pages/includes/publications.md` following the existing `paper-box` pattern
3. **Lazy loading** — Always include `loading="lazy"` on the `<img>` tag

### Image Optimization

Teaser images render at max **400px** width. Keep source images at max **800px** wide (2× retina):

```bash
# Resize a single image (built-in macOS tool, no install needed)
sips --resampleWidth 800 --setProperty formatOptions best images/papers/example.png

# Batch resize all PNGs over 500KB
for f in images/papers/*.png; do
  kb=$(wc -c < "$f" | awk '{printf "%d", $1/1024}')
  if [ $kb -gt 500 ]; then
    sips --resampleWidth 800 --setProperty formatOptions best "$f" --out "$f"
  fi
done
```

For further compression (requires Homebrew):

```bash
brew install optipng pngquant

# Lossless compression
optipng -o7 images/papers/*.png

# Lossy compression (80-95% quality)
pngquant --quality=80-95 --force --ext .png images/papers/*.png
```

### New Profile Avatar

1. Save a JPEG version to `images/eric-hao.jpg`
2. Convert to WebP for next-gen format support:
   ```bash
   brew install webp
   cwebp images/eric-hao.jpg -o images/eric-hao.webp
   ```

---

## 🌐 Deployment

### Automatic

Push to the `main` branch — GitHub Pages builds and deploys automatically via the `pages/pages-build-deployment` workflow.

### Google Scholar Auto-Update

Citation stats are updated **daily at 08:00 UTC** via the `google_scholar_crawler` GitHub Action. This requires:

1. A **`GOOGLE_SCHOLAR_ID`** secret set in repository settings
2. The Python crawler script lives in `google_scholar_crawler/`

### GitHub Profile Auto-Updater

The `github_myprofile_updater/` workflow syncs profile metadata (e.g., pinned repos, bio) to GitHub automatically.

---

## 📄 License

This project is open-sourced under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

<p align="center">
  <sub>Built with ❤️ using Jekyll + GitHub Pages</sub>
</p>