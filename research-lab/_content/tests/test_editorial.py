import copy, importlib.util, json, pathlib, sys, unittest
CONTENT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(CONTENT))
import build_editorial as b
class EditorialTests(unittest.TestCase):
 def sample(self):return json.loads((CONTENT/'editorial/agentic_ttt.json').read_text())
 def test_valid_record(self):self.assertEqual(b.validate(self.sample())['status'],'complete')
 def test_duplicate_ids_rejected(self):
  r=self.sample();r['sections'][1]['id']=r['sections'][0]['id']
  with self.assertRaises(ValueError):b.validate(r)
 def test_unsafe_figure_rejected(self):
  r=self.sample();s=next(s for s in r['sections'] if 'figure'in s);s['figure']['src']='../../secrets'
  with self.assertRaises(ValueError):b.validate(r)
 def test_unsafe_url_rejected(self):
  with self.assertRaises(ValueError):b.safe_url('javascript:alert(1)')
 def test_non_english_rejected(self):
  r=self.sample();r['title']='中文'
  with self.assertRaises(ValueError):b.validate(r)
 def test_evidence_required(self):
  r=self.sample();r['evidence']=[]
  with self.assertRaises(ValueError):b.validate(r)
 def test_markup_escaped(self):self.assertNotIn('<script>',b.rich('<script>bad</script>'))
 def test_math_and_emphasis(self):
  out=b.rich('A **clear** $x+y$ example');self.assertIn('<strong>clear</strong>',out);self.assertIn('data-math="x+y"',out)
 def test_invalid_figure_position_rejected(self):
  r=self.sample();s=next(s for s in r['sections'] if s.get('figure'));s['figure_after']=len(s['paragraphs'])+1
  with self.assertRaises(ValueError):b.validate(r)
 def test_placement_requires_figure(self):
  r=self.sample();s=next(s for s in r['sections'] if not s.get('figure'));s['figure_after']=1
  with self.assertRaises(ValueError):b.validate(r)
 def test_figure_html_escapes_alt(self):
  f=next(s['figure'] for s in self.sample()['sections'] if s.get('figure')).copy();f['alt']='<script>'
  self.assertNotIn('<script>',b.render_figure(f))
 def test_index_card_metadata(self):
  paper=next(p for p in b.CATALOG if p['image']=='agentic_ttt')
  html=b.card(paper,self.sample(),None)
  for token in ('data-year="2026"','data-category="language"','data-type="report"','articles/agentic-ttt/','class="research-card"'):
   self.assertIn(token,html)
 def test_vortex_source_is_available(self):
  paper=next(p for p in b.CATALOG if p['image']=='vortex-bursting')
  self.assertEqual(b.publication_type(paper),('Publication','publication'))
  self.assertEqual(b.venue_label(paper),'J. Fluid Mech. 2026')
  self.assertEqual(json.loads((CONTENT/'editorial/vortex-bursting.json').read_text())['status'],'complete')
 def test_type_classification(self):
  expected={'kat-v25-dev':'models','kat-v25':'models','lpm':'models','kat-v2':'models','color':'publication'}
  for key,kind in expected.items():
   self.assertEqual(b.publication_type(next(p for p in b.CATALOG if p['image']==key))[1],kind)
 def test_venue_does_not_invent_dates(self):
  p=next(p for p in b.CATALOG if p['image']=='magknot')
  self.assertEqual(b.venue_label(p),'J. Fluid Mech. 2021')
 def test_card_prose_is_escaped(self):
  paper=next(p for p in b.CATALOG if p['image']=='agentic_ttt')
  r=self.sample();r['title']='<script>bad()</script>'
  self.assertNotIn('<script>',b.card(paper,r,None))

class RestoredPreviewTests(unittest.TestCase):
 def test_text_only_home_and_blog_header(self):
  header=b.head('Research Notes','A research index').split('<header class="site-header">',1)[1].split('</header>',1)[0]
  self.assertEqual(header.count('<a '),2)
  self.assertIn('href="../"',header)
  self.assertIn('>Home</text>',header)
  self.assertIn('>Blog</text>',header)
  self.assertNotIn('<path',header)
  self.assertNotIn('>Jinhua Hao',header)
  self.assertNotIn('>Research',header)
 def test_article_home_returns_to_personal_site(self):
  header=b.head('Article','Description','../../','articles/vortex-bursting/').split('<header class="site-header">',1)[1].split('</header>',1)[0]
  self.assertIn('href="../../../"',header)
 def test_index_title_is_research(self):
  source=(CONTENT/'build_editorial.py').read_text()
  self.assertIn('<h1>Research</h1>',source)
  self.assertNotIn('<h1>Research Notes</h1>',source)
 def test_reviewed_vortex_scientific_qualifiers(self):
  record=json.loads((CONTENT/'editorial/vortex-bursting.json').read_text())
  prose=' '.join(p for section in record['sections'] for p in section['paragraphs'])
  self.assertIn('axial magnetic field has a Gaussian radial profile',prose)
  self.assertIn('not a force-balanced equilibrium',prose)
  self.assertIn('not a new conserved quantity',prose)
 def test_seven_authorized_vortex_figures(self):
  record=json.loads((CONTENT/'editorial/vortex-bursting.json').read_text())
  figures=[s['figure'] for s in record['sections'] if s.get('figure')]
  self.assertEqual(len(figures),7)
  for f in figures:
   self.assertTrue(f['src'].endswith('.webp'))
   self.assertFalse(f['sourceUrl'].lower().endswith('.pdf'))
 def test_home_touch_target(self):
  css=(CONTENT/'styles/research.css').read_text()
  self.assertIn('.home-link,.blog-link{',css)
  self.assertIn('min-height:44px',css)

class ResponsiveResearchTests(unittest.TestCase):
 def test_panel_default_in_source_and_script(self):
  source=(CONTENT/'build_editorial.py').read_text()
  js=(CONTENT.parent/'app.js').read_text()
  self.assertIn('class="research-results" data-layout="grid"',source)
  self.assertIn("['grid', 'list'], 'grid'",js)
  self.assertNotIn('localStorage',js)
  self.assertIn("state.view !== 'grid'",js)
 def test_no_footer(self):
  self.assertEqual(b.footer(),'')
  self.assertEqual(b.footer('../../'),'')
 def test_panel_breakpoints(self):
  css=(CONTENT/'styles/research.css').read_text()
  for token in ('repeat(4,minmax(0,1fr))','min-width:768px) and (max-width:1199px','min-width:360px) and (max-width:767px','max-width:359px','repeat(2,minmax(0,1fr))','column-gap:16px','font-size:16px;line-height:1.35','font-size:12px;line-height:1.4'):
   self.assertIn(token,css)

class FeaturedModelsTests(unittest.TestCase):
 def test_featured_order(self):
  self.assertEqual([p['image'] for p in sorted(b.CATALOG,key=b.featured_order)][:4],['kat-v25','kat-v25-dev','kat-v2','lpm'])
 def test_chronological_order_ignores_featured(self):
  models=[p for p in b.CATALOG if p.get('content_type')=='models']
  self.assertEqual([p['image'] for p in sorted(models,key=b.chronological_value,reverse=True)],['kat-v25-dev','lpm','kat-v25','kat-v2'])
 def test_model_dates_and_titles(self):
  expected={'kat-v25':('2026-07-07','release'),'kat-v2':('2026-03-25','release'),'lpm':('2026-07-15','report'),'kat-v25-dev':('2026-07-23','repository')}
  for key,(stamp,kind) in expected.items():
   p=next(p for p in b.CATALOG if p['image']==key)
   self.assertEqual((p['date'],p['date_kind']),(stamp,kind))
   self.assertTrue(p['date_source'].startswith('https://'))
   self.assertEqual(b.card_label(p),'Models')
   d=json.loads((CONTENT/f'editorial/{key}.json').read_text())
   self.assertTrue(d['title'].startswith('Introducing '))
 def test_repository_date_is_not_release(self):
  p=next(p for p in b.CATALOG if p['image']=='kat-v25-dev')
  self.assertEqual(b.venue_label(p),'Repository Jul 23, 2026')
 def test_year_only_dates_not_fabricated(self):
  self.assertEqual(b.chronological_value({'year':2026}),20260000)
 def test_featured_js_default(self):
  js=(CONTENT.parent/'app.js').read_text()
  self.assertIn("sorts.map(input => input.value), 'featured'",js)
  self.assertIn("if (state.sort === 'featured')",js)
  self.assertIn('Number(a.dataset.date)',js)

 def test_actual_javascript_date_sort(self):
  import subprocess,re
  js=(CONTENT.parent/'app.js').read_text()
  body=js.split('const sorted = [...cards].sort((a, b) => {',1)[1].split('\n      });',1)[0]
  cards=[{'dataset':{'title':p['title'],'date':str(b.chronological_value(p)),'featured':str(p.get('featured_rank',999)),'order':str(i),'key':p['image']}} for i,p in enumerate(b.CATALOG) if p.get('content_type')=='models']
  script='const cards='+json.dumps(cards)+';const out={};for(const mode of ["featured","newest","oldest"]){const state={sort:mode};out[mode]=[...cards].sort((a,b)=>{'+body+'}).map(c=>c.dataset.key)};console.log(JSON.stringify(out))'
  out=json.loads(subprocess.check_output(['node','-e',script],text=True))
  self.assertEqual(out['featured'],['kat-v25','kat-v25-dev','kat-v2','lpm'])
  self.assertEqual(out['newest'],['kat-v25-dev','lpm','kat-v25','kat-v2'])
  self.assertEqual(out['oldest'],list(reversed(out['newest'])))
 def test_model_hero_is_selective(self):
  for p in b.CATALOG:
   html=(CONTENT.parent/p['article']/'index.html').read_text()
   self.assertEqual('article-hero model-hero' in html,p.get('content_type')=='models')

class CoverTypographyTests(unittest.TestCase):
 def test_model_covers_share_typography_with_approved_lpm_size(self):
  expected={'family':'OpenAI Sans','style':'Bold','fontSize':170,'canvasSize':1254,'lineAdvance':190,'align':'center','blockCenter':[0.5,0.5]}
  covers=json.loads((CONTENT/'covers.json').read_text())
  for key in ('kat-v25','kat-v25-dev','kat-v2','lpm'):
   self.assertEqual(covers[key]['typography'],dict(expected,fontSize=240 if key=='lpm' else 170))
 def test_renderer_uses_real_font_without_fallback_and_glyph_centering(self):
  import ast
  source=(CONTENT/'render_cover_type.py').read_text()
  tree=ast.parse(source)
  constants={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('SIZE','FONT_SIZE','LINE_ADVANCE')}
  self.assertEqual(constants,{'SIZE':1254,'FONT_SIZE':170,'LINE_ADVANCE':190})
  self.assertIn("'kat-v25-dev': ['KAT-Coder', 'V2.5 Dev']",source)
  self.assertIn("TTFont(ROOT / 'fonts/openai/OpenAISans-Bold.woff2')",source)
  self.assertIn('ImageFont.truetype(BytesIO(buf.getvalue()), font_size)',source)
  self.assertNotIn('load_default',source)
  self.assertFalse(any(isinstance(n,ast.Try) for n in ast.walk(tree)))
  for formula in ('draw.textbbox','(SIZE-(bottom-top))/2-top','(SIZE-(b[2]-b[0]))/2-b[0]'):
   self.assertIn(formula,source)

if __name__=='__main__':unittest.main()
