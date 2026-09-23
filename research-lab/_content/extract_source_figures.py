"""Extract original source assets safely, preserving vector originals."""
from pathlib import Path
import json,tarfile
import pdfplumber
from PIL import Image
r=Path(__file__).resolve().parents[1];src=Path('/tmp/research-sources');dest=r/'images/source';dest.mkdir(exist_ok=True)
selected={
'cassr':[('images/architecture_final.pdf','Cascaded super-resolution architecture'),('images/quali_final.pdf','Real-world restoration comparisons')],
'agentic_ttt':[('figs/fig_method_overview.pdf','The in-episode adaptation loop'),('figs/fig_diagnostic_2panel.pdf','Repetition and adapter drift diagnostics')],
'mmg2skill':[('figures/mmg2skill_method.pdf','From guide construction to execution and revision'),('figures/revision_dynamics/revision_dynamics.pdf','Performance over successive revision attempts')],
'webcompass':[('figures/overview.pdf','The WebCompass task landscape'),('figures/agent_as_a_judge.pdf','Browser-based agent evaluation')],
'color':[('figure/pipeline.pdf','Spectral misalignment and the ASASR formulation'),('figure/Expr_spectrum.pdf','Visual and spectral fidelity comparisons')],
'tta_flow':[('Figure_2.pdf','ResFlow-Tuner architecture'),('Figure_1.pdf','Synthetic and real-world visual examples')],
'shiftlut':[('Figures/Overview-11-12.pdf','ShiftLUT architecture and spatial shifts'),('Figures/sr_qualitative_results.pdf','Super-resolution visual comparisons')],
'instantvir':[('figs/instantvir-overview4.pdf','Single-step training and causal inference'),('figs/instantvir-randominp.pdf','Video inpainting comparisons')],
'varsr':[('figure/framework.pdf','The VARSR restoration pipeline'),('figure/sota5.pdf','Qualitative comparisons with restoration baselines')],
'tinvblocks':[('pics/T-InvBlock.pdf','The tri-branch invertible block'),('pics/TSAIN_vis.pdf','Reconstruction after JPEG compression')],
'oapt':[('pics/pipeline.pdf','Offset-aware partition transformer'),('pics/gray_visuals.pdf','Double-JPEG restoration comparisons')],
'xpsr':[('figure/model.pdf','Cross-modal semantic guidance and restoration'),('figure/baseline.pdf','Qualitative restoration comparisons')],
'ptmvqa':[('images/framework_0928.png','Combining pretrained representations'),('images/constraint.png','Consistency and separation in quality-aware features')],
'lpm':[('figures/arch.pdf','LPM-Video and its temporal block'),('figures/lpm-pyramid_infer.png','Temporal-pyramid inference for long videos')],
'kat-v25':[('figures/swe_pipeline.pdf','Agentic software-engineering data pipelines'),('figures/benchmark.pdf','Reported SWE and agent benchmark results')],
'kat-v2':[('figures/kwaienv.pdf','KwaiEnv workflow for software engineering'),('figures/kat_benchmark.pdf','Cross-scaffold software-engineering results')]
}
manifest={}
for key,assets in selected.items():
 archive=src/(key+'.tar')
 if not archive.exists():continue
 index=json.loads((src/(key+'.json')).read_text());records=[]
 with tarfile.open(archive) as tar:
  members={m.name.lstrip('./'):m for m in tar if m.isfile()}
  for i,(name,caption) in enumerate(assets):
   if name not in members:print('MISSING',key,name);continue
   raw=tar.extractfile(members[name]).read();suffix=Path(name).suffix.lower();original=dest/f'{key}-{i+1}{suffix}';original.write_bytes(raw)
   if suffix=='.pdf':
    with pdfplumber.open(original) as pdf:
     page=pdf.pages[0];dpi=min(600,4200*72/max(page.width,page.height));im=page.to_image(resolution=dpi,antialias=True).original.convert('RGB')
   else:
    rgba=Image.open(original).convert('RGBA');bg=Image.new('RGBA',rgba.size,'white');bg.alpha_composite(rgba);im=bg.convert('RGB');dpi=None
   full=dest/f'{key}-{i+1}-preview.png';im.save(full,optimize=True);thumb=im.copy();thumb.thumbnail((1800,1800));small=dest/f'{key}-{i+1}.webp';thumb.save(small,quality=92)
   records.append({'original':str(original.relative_to(r)),'full':str(full.relative_to(r)),'thumbnail':str(small.relative_to(r)),'label':caption,'width':im.width,'height':im.height,'source':f'https://arxiv.org/abs/{index["id"]}','sourceArchive':f'https://arxiv.org/src/{index["id"]}','sourceAsset':name,'kind':'vector source PDF' if suffix=='.pdf' else 'original source image','previewDpi':dpi})
 manifest[key]=records
(r/'_content/source-figures.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Extracted',sum(map(len,manifest.values())),'original figure assets from',len(manifest),'papers.')
