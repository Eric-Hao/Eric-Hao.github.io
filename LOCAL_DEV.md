# Local Development Guide

This is a Jekyll-based personal homepage. Below are instructions for building and previewing it locally on macOS.

## Prerequisites

- **Podman** (or Docker) — used to run Jekyll in a container, avoiding the need to install Ruby/Bundler natively
- **Python 3** — used to serve the built static site for preview

Check Podman availability:
```bash
podman --version   # should show 5.x+
```

If you use Docker instead of Podman, simply replace `podman` with `docker` in all commands below.

## Build

Run Jekyll build inside a container:

```bash
podman run --rm \
  --volume="$PWD:/srv/jekyll:Z" \
  jekyll/jekyll:4.2.2 \
  sh -c "bundle install 2>&1 | tail -1 && bundle exec jekyll build"
```

This generates the static site into the `_site/` directory. Build takes ~30-40 seconds.

## Preview

After building, serve the `_site/` directory with Python's built-in HTTP server:

```bash
cd _site
python3 -m http.server 4000
```

Then open **http://localhost:4000** in your browser.

Press `Ctrl+C` to stop the server.

## Quick Script (Build + Preview)

You can also use the one-liner:

```bash
podman run --rm --volume="$PWD:/srv/jekyll:Z" jekyll/jekyll:4.2.2 \
  sh -c "bundle install 2>&1 | tail -1 && bundle exec jekyll build" \
  && cd _site && python3 -m http.server 4000
```

## Notes

- **Podman on macOS** runs via a VM (libkrun). If `podman machine` is not started, run:
  ```bash
  podman machine start
  ```
- **amd64 emulation warning**: `jekyll/jekyll:4.2.2` is a linux/amd64 image. On Apple Silicon (arm64), Podman will emulate it via QEMU. This works but is slower. The warning `image platform does not match` is harmless.
- **`jekyll serve` doesn't work** in this container due to Ruby 3.x removing `webrick` from the standard library. Using `jekyll build` + Python HTTP server is the workaround.
- **Port conflict**: If port 4000 is already in use, change the port number (e.g., `python3 -m http.server 4001`).

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Permission denied @ dir_s_mkdir - _site` | Run `mkdir -p _site && chmod 777 _site` before building |
| `podman machine not running` | Run `podman machine start` |
| Port 4000 already in use | Use a different port: `python3 -m http.server 4001` |
| Build fails with `no implicit conversion of Hash into Integer` | Don't use `--force_polling` with `jekyll serve`; use `jekyll build` instead |


## Image Optimization

Teaser images are displayed at max 400px width in the browser, but source images can be much larger. To keep page load fast, images should be resized to max 800px wide (2x for retina displays) and compressed.

### Method: macOS `sips` (built-in, no installation needed)

```bash
# Resize a single image to max 800px wide (keeps aspect ratio)
sips --resampleWidth 800 --setProperty formatOptions best images/papers/example.png

# Batch resize all PNGs larger than 500KB in papers/
for f in images/papers/*.png; do
  kb=$(wc -c < "$f" | awk '{printf "%d", $1/1024}')
  if [ $kb -gt 500 ]; then
    echo "Compressing $(basename $f) ($kb KB)..."
    # Back up original first
    cp "$f" images/papers/originals/$(basename $f)
    # Resize and re-encode
    sips --resampleWidth 800 --setProperty formatOptions best "$f" --out "$f"
  fi
done
```

**What this does:**
- `--resampleWidth 800`: Resamples the image so the width is at most 800 pixels, preserving aspect ratio. If the image is already ≤800px wide, it stays unchanged.
- `--setProperty formatOptions best`: Sets PNG compression to the highest (lossless) level. Combined with resampling, this typically reduces file size by 60-80%.
- Original files are backed up to `images/papers/originals/` before modification.

### Other options (if you want even smaller files)

If you install additional tools via Homebrew:

```bash
# Install tools
brew install optipng pngquant

# Lossless PNG optimization (no quality loss, slower)
optipng -o7 images/papers/*.png

# Lossy PNG compression (slight quality loss, much smaller)
pngquant --quality=80-95 --force --ext .png images/papers/*.png
```

### Adding new teaser images

When adding a new paper's teaser image:

1. Place the original image in `images/papers/` as a PNG file
2. If the image is >500KB or >800px wide, run the `sips` compression above
3. Update `_pages/includes/pub.md` to reference the new image
4. Always include `loading='lazy'` in the `<img>` tag for performance:
   ```html
   <img loading='lazy' src='images/papers/new_paper.png' alt="description" width="100%">
   ```