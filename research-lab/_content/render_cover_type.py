"""Render consistent cover typography with the repository's licensed OpenAI Sans.
Requires Pillow, fontTools and Brotli. No network access or model-generated text.
"""
from pathlib import Path
from io import BytesIO
import json
from PIL import Image, ImageOps, ImageFont, ImageDraw
from fontTools.ttLib import TTFont
ROOT = Path(__file__).resolve().parents[1]
SIZE = 1254
FONT_SIZE = 170
LINE_ADVANCE = 190
FONT_SIZE_OVERRIDES = {'lpm': 240}
LABELS = {'kat-v25': ['KAT-Coder', 'V2.5'], 'kat-v25-dev': ['KAT-Coder', 'V2.5 Dev'], 'kat-v2': ['KAT-Coder', 'V2'], 'lpm': ['LPM']}
def main():
    face = TTFont(ROOT / 'fonts/openai/OpenAISans-Bold.woff2')
    face.flavor = None
    buf = BytesIO(); face.save(buf)
    covers = json.loads((ROOT / '_content/covers.json').read_text())
    for key, lines in LABELS.items():
        font_size = FONT_SIZE_OVERRIDES.get(key, FONT_SIZE)
        font = ImageFont.truetype(BytesIO(buf.getvalue()), font_size)
        image = ImageOps.fit(Image.open(ROOT / 'images/covers-index-2026/backgrounds' / (key+'.webp')).convert('RGB'), (SIZE, SIZE), method=Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(image)
        bounds = [draw.textbbox((0, i*LINE_ADVANCE), line, font=font) for i,line in enumerate(lines)]
        top, bottom = min(b[1] for b in bounds), max(b[3] for b in bounds)
        offset_y = (SIZE-(bottom-top))/2-top
        for i, (line,b) in enumerate(zip(lines,bounds)):
            x = (SIZE-(b[2]-b[0]))/2-b[0]
            draw.text((x, offset_y+i*LINE_ADVANCE), line, font=font, fill='#ffffff')
        image.save(ROOT/covers[key]['full'], 'WEBP', quality=90, method=6)
        image.resize((640,640),Image.Resampling.LANCZOS).save(ROOT/covers[key]['thumbnail'],'WEBP',quality=88,method=6)
        covers[key].update(fullWidth=SIZE,fullHeight=SIZE, typography={'family':'OpenAI Sans','style':'Bold','fontSize':font_size,'canvasSize':SIZE,'lineAdvance':LINE_ADVANCE,'align':'center','blockCenter':[.5,.5]})
    (ROOT/'_content/covers.json').write_text(json.dumps(covers,indent=2,ensure_ascii=False)+'\n')
if __name__ == '__main__': main()
