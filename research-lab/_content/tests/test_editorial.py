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
if __name__=='__main__':unittest.main()
