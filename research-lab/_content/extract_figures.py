"""Render selected paper figures at 300 dpi; keep extraction provenance."""
from pathlib import Path
import json,sys
import pdfplumber
from PIL import Image
r=Path(__file__).resolve().parents[1];pdfs=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/research-pdfs');out=r/'images/figures';out.mkdir(exist_ok=True)
# PDF page numbers are one-based; boxes are PDF points, top-left coordinates.
selections={
'agentic_ttt':(2,[106,69,506,173],'Figure 1'),
'mmg2skill':(2,[69,73,526,172],'Figure 1'),
'webcompass':(3,[69,73,526,367],'Figure 3'),
'color':(2,[53,63,559,173],'Figure 1'),
'tta_flow':(2,[38,40,376,273],'Figure 1'),
'shiftlut':(3,[55,52,558,348],'Figure 2'),
'instantvir':(2,[56,68,557,384],'Figure 1'),
'varsr':(4,[54,57,560,215],'Figure 1'),
'tinvblocks':(3,[52,46,560,180],'Figure 2'),
'oapt':(2,[132,122,482,267],'Figure 1'),
'cpga':(4,[44,39,568,313],'Figure 3'),
'xpsr':(6,[135,115,479,387],'Figure 2'),
'ptmvqa':(4,[48,59,564,272],'Figure 3'),
'cassr':(2,[33,40,381,195],'Figure 1'),
'magvortex':(8,[88,51,424,203],'Figure 3'),
'vortex':(11,[100,54,395,214],'Figure 2'),
'lpm':(7,[72,49,541,238],'Figure 3')}
sources=json.loads((pdfs/'sources.json').read_text());manifest={}
for key,(n,box,label) in selections.items():
 with pdfplumber.open(pdfs/(key+'.pdf')) as pdf:
  im=pdf.pages[n-1].crop(box).to_image(resolution=300,antialias=True).original.convert('RGB')
  im.save(out/(key+'.png'),optimize=True)
  thumb=im.copy();thumb.thumbnail((1100,1100));thumb.save(out/(key+'.webp'),quality=88)
  manifest[key]={'full':f'images/figures/{key}.png','thumbnail':f'images/figures/{key}.webp','label':label,'page':n,'crop':box,'dpi':300,'width':im.width,'height':im.height,'source':sources[key]}
# Original source image retained when the full PDF is not publicly accessible.
p=r.parent/'images/papers/magknot.png';im=Image.open(p)
manifest['magknot']={'full':'../images/papers/magknot.png','thumbnail':'../images/papers/magknot.webp','label':'Research figure from the original academic homepage','width':im.width,'height':im.height,'source':'https://doi.org/10.1017/jfm.2020.1145','note':'Original 800-pixel asset retained; no higher-resolution PDF available.'}
for key in ['kat-v25-dev','kat-v25','kat-v2']:
 manifest[key]={'full':f'images/{key}-benchmark.svg','thumbnail':f'images/{key}-benchmark.svg','label':'Benchmark comparison redrawn from published results','width':440,'height':440,'source':'https://huggingface.co/Kwaipilot/KAT-Coder-V2.5-Dev' if key.endswith('dev') else ('https://arxiv.org/abs/2607.05471' if key=='kat-v25' else 'https://arxiv.org/abs/2603.27703')}
(r/'_content/figures.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Extracted',len(selections),'high-resolution paper figures; retained one original and three vector benchmark charts.')
