"""Keep legacy disclosure styles from rotating or squeezing report figures."""
import re
import unittest
from pathlib import Path


class FigureStyles(unittest.TestCase):
    def test_report_summary_uses_block_layout(self):
        css = (Path(__file__).resolve().parents[1] / 'styles/editorial.css').read_text()
        self.assertRegex(css, r'\.deep-read \.report-figure summary\s*\{[^}]*display:\s*block;')

    def test_only_report_content_resets_disclosure_rotation(self):
        css = (Path(__file__).resolve().parents[1] / 'styles/editorial.css').read_text()
        self.assertRegex(css, r'\.deep-read \.report-figure summary \.report-image-hint,\s*'
                             r'\.deep-read \.report-figure summary \.report-image-viewport\s*'
                             r'\{\s*transform:\s*none;\s*\}')

    def test_provenance_notices_survive_hidden_sidebar_rule(self):
        css = (Path(__file__).resolve().parents[1] / 'styles/editorial.css').read_text()
        self.assertRegex(css, r'\.article-layout \.prose > \.source-note\s*\{\s*display:\s*block;\s*\}')


if __name__ == '__main__':
    unittest.main()
