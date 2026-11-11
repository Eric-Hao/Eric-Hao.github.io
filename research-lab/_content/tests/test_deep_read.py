import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from deep_read_content import validate_report, markdown

class DeepReadContract(unittest.TestCase):
    def setUp(self):
        self.report={"schema_version":1,"key":"test","status":"complete","title":{"en":"Test","zh":"测试"},"dek":{"en":"Details","zh":"内容"},"source_note":{"en":"Source","zh":"来源"},"sections":[{"title":{"en":"Section","zh":"章节"},"blocks":[{"en":"Text","zh":"正文"}]} for _ in range(6)]}
    def test_valid_pairs(self):
        self.assertEqual(validate_report(self.report,"test")["key"],"test")
    def test_missing_translation(self):
        self.report['sections'][2]['blocks'][0]['zh']=''
        with self.assertRaises(ValueError):validate_report(self.report)
    def test_exact_six_sections(self):
        self.report['sections'].pop()
        with self.assertRaises(ValueError):validate_report(self.report)
    def test_wrong_key(self):
        with self.assertRaises(ValueError):validate_report(self.report,"other")
    def test_shared_must_not_mix_languages(self):
        self.report['sections'][0]['blocks'][0]['shared']='$$x$$'
        with self.assertRaises(ValueError):validate_report(self.report)
    def test_export_has_six_fixed_headings_and_pairs(self):
        output=markdown(self.report)
        self.assertEqual(output.count('\n## '),6)
        self.assertEqual(output.count('<!-- pair:'),12)
        self.assertIn('核心思想一句话总结',output)

if __name__=='__main__':unittest.main()
