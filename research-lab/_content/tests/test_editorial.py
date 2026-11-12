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
  expected={'kat-v25-dev':'release','kat-v25':'report','color':'publication'}
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

if __name__=='__main__':unittest.main()
