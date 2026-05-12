# Eric-Hao.github.io

Personal academic homepage of **Jinhua Hao (郝进华)**, Research Engineer at Kuaishou Technology.

**Live site:** https://Eric-Hao.github.io

## About

Built with [Jekyll](https://jekyllrb.com/) and deployed via GitHub Pages, based on the [AcadHomepage](https://github.com/RayeRen/acad-homepage.github.io) template with extensive customizations. Features automatic Google Scholar citation updates via GitHub Actions.

## Project Structure

```
_config.yml                  # Site configuration (author info, SEO, analytics)
_data/navigation.yml         # Navigation bar links and anchors
_includes/                   # Reusable HTML components (head, sidebar, SEO, etc.)
_pages/
  about.md                   # Main page entry point (includes all sections)
  includes/
    intro.md                 # Biography
    news.md                  # News items
    publications.md          # Publication list with paper thumbnails
    competitions.md          # Competition results
    projects.md              # Industry projects
    honors.md                # Awards and honors
    educations.md            # Education history
_sass/                       # SCSS stylesheets
images/
  papers/                    # Publication teaser images (PNG + WebP)
  competitions/              # Competition teaser images
  eric-hao.jpg/.webp         # Profile avatar
```

## Local Development

### Prerequisites

- **Podman** (or Docker) — runs Jekyll in a container, no local Ruby install needed
- **Python 3** — serves the built static site for preview

```bash
podman --version   # should show 5.x+
```

Replace `podman` with `docker` in all commands if using Docker instead.

### Build

```bash
# Ensure _site directory exists
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

### Notes

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

## Adding Content

### New publication

1. Add a teaser image to `images/papers/` (PNG + WebP pair)
2. Add an entry to `_pages/includes/publications.md` following the existing `paper-box` pattern
3. Always include `loading="lazy"` on the `<img>` tag

### Image optimization

Teaser images render at max 400px width. Keep source images at max 800px wide (2× retina):

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
optipng -o7 images/papers/*.png                              # lossless
pngquant --quality=80-95 --force --ext .png images/papers/*.png  # lossy
```

## Deployment

Push to `main` branch — GitHub Pages builds and deploys automatically.

Google Scholar citation stats are updated daily at 08:00 UTC via the `google_scholar_crawler` GitHub Action. Requires `GOOGLE_SCHOLAR_ID` set in repository secrets.
