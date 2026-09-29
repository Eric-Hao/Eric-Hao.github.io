"""Deterministic asset URLs keep previews and published pages in sync."""
import hashlib
import re
from urllib.parse import urlsplit

def write_page(destination, markup):
 def version(match):
  attribute, url = match.groups()
  parsed = urlsplit(url)
  if parsed.scheme or parsed.netloc or parsed.path.startswith('/'):
   return match.group(0)
  asset = destination.parent / parsed.path
  digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
  return f'{attribute}="{parsed.path}?v={digest}"'
 markup = re.sub(r'(href|src)="([^"?]+\.(?:css|js))"', version, markup)
 destination.write_text(markup)
