"""Offline regression checks; importing scholarly catches incompatible dependencies."""

import contextlib
import copy
import io
import json
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

# Keep the real import: mocking the module would hide the #759 failure.
from scholarly import scholarly
from bibtexparser.bibdatabase import BibDatabase


class CrawlerTests(unittest.TestCase):
    def test_dependency_api(self):
        self.assertEqual(BibDatabase().entries, [])
        self.assertTrue(callable(scholarly.search_author_id))
        self.assertTrue(callable(scholarly.fill))

    def test_outputs_keep_expected_schema(self):
        author = {
            'name': 'Test Author',
            'citedby': 42,
            'publications': [{'author_pub_id': 'test:paper', 'num_citations': 7}],
        }
        script = Path(__file__).with_name('main.py').resolve()
        original_directory = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                with patch.dict(os.environ, {'GOOGLE_SCHOLAR_ID': 'test'}), \
                     patch.object(scholarly, 'search_author_id', return_value=copy.deepcopy(author)) as search, \
                     patch.object(scholarly, 'fill') as fill, \
                     contextlib.redirect_stdout(io.StringIO()):
                    runpy.run_path(str(script), run_name='__main__')
                search.assert_called_once_with('test')
                self.assertEqual(fill.call_args.kwargs['sections'],
                                 ['basics', 'indices', 'counts', 'publications'])
                data = json.loads(Path('results/gs_data.json').read_text())
                self.assertEqual(data['citedby'], 42)
                self.assertEqual(data['publications']['test:paper']['num_citations'], 7)
                self.assertTrue(data['updated'])
                shield = json.loads(Path('results/gs_data_shieldsio.json').read_text())
                self.assertEqual(shield, {'schemaVersion': 1, 'label': 'citations', 'message': '42'})
            finally:
                os.chdir(original_directory)


if __name__ == '__main__':
    unittest.main()
