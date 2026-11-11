"""Integrate optional, source-verified deep reads with the existing static site."""
import json
import subprocess
from deep_read_content import REPORTS, CONTENT, export


def prepare():
    reports = sorted(REPORTS.glob("*/report.json"))
    if not reports:
        return {}
    for path in reports:
        export(path.parent)
    subprocess.run(["node", str(CONTENT / "build_deep_reads.mjs")], check=True)
    return json.loads((CONTENT / "deep-read-rendered.json").read_text())


def sync_metadata(papers, reports):
    for paper in papers:
        report = reports.get(paper["image"])
        if report:
            paper["headline"] = report["title"]["en"]
            paper["headlineZh"] = report["title"]["zh"]


def source_gap(key):
    """A source-blocked manuscript remains intact, with a clear status notice."""
    path = REPORTS / key / "blocker.json"
    if not path.exists():
        return ""
    return ('<aside class="source-note source-gap" role="note">'
            '<p>Original note retained. A full manuscript is needed before its '
            'methods, figures and results can be independently checked for the deep-read revision.</p>'
            '<p class="zh" lang="zh-CN">保留原笔记。完成深度解读前仍需取得论文全文，'
            '以独立核验方法、图表和结果。</p></aside>')
