"""Bilingual deep-read source contract and deterministic Markdown export.

The JSON pairs are canonical. report.md is generated for paper-deep-reader's
strict checks; HTML is generated separately from the same pairs for the site.
"""
import argparse
import json
from pathlib import Path

CONTENT = Path(__file__).resolve().parent
ROOT = CONTENT.parent
REPORTS = CONTENT / "deep-read"
TITLES = [
    ("核心思想一句话总结", "Elevator Pitch"),
    ("论文背景与动机", "Background & Motivation"),
    ("核心方法/模型详解", "The Core Method/Model"),
    ("实验与结果分析", "Experiments & Results"),
    ("论文的贡献与影响", "Contribution & Impact"),
    ("结论", "Conclusion"),
]


def paired(value, where):
    if not isinstance(value, dict) or not all(isinstance(value.get(k), str) and value[k].strip() for k in ("en", "zh")):
        raise ValueError(f"{where}: nonempty en and zh strings are required")
    return value


def validate_report(data, expected_key=None):
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported report schema_version")
    if expected_key and data.get("key") != expected_key:
        raise ValueError(f"Report key differs from directory: {expected_key}")
    if data.get("status") not in {"complete", "partial"}:
        raise ValueError("Report status must be complete or partial")
    for field in ("title", "dek", "source_note"):
        paired(data.get(field), field)
    if len(data.get("sections", [])) != 6:
        raise ValueError("Exactly six sections are required")
    for i, section in enumerate(data["sections"], 1):
        paired(section.get("title"), f"section {i} title")
        if not section.get("blocks"):
            raise ValueError(f"Section {i} is empty")
        for j, block in enumerate(section["blocks"], 1):
            if "shared" in block:
                if "en" in block or "zh" in block or not isinstance(block["shared"], str) or not block["shared"].strip():
                    raise ValueError(f"Section {i}, block {j}: invalid shared block")
            else:
                paired(block, f"section {i}, block {j}")
    return data


def markdown(data):
    out = [f"# {data['title']['en']}", data["title"]["zh"], data["source_note"]["en"], data["source_note"]["zh"]]
    for i, section in enumerate(data["sections"], 1):
        # Canonical numbered headings make strict skill validation independent
        # of each paper's optional, more specific subheadings.
        zh, en = TITLES[i - 1]
        out.append(f"## {i}. {zh}（{en}）")
        for j, block in enumerate(section["blocks"], 1):
            if "shared" in block:
                out.append(block["shared"].strip())
            else:
                for language in ("en", "zh"):
                    out.append(f"<!-- pair:{i}-{j}:{language} -->\n\n{block[language].strip()}")
    return "\n\n".join(out) + "\n"


def export(directory):
    path = directory / "report.json"
    data = validate_report(json.loads(path.read_text()), directory.name)
    (directory / "report.md").write_text(markdown(data))
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keys", nargs="*", help="Report keys; omitted means all reports")
    args = parser.parse_args()
    paths = [REPORTS / key for key in args.keys] if args.keys else sorted(p.parent for p in REPORTS.glob("*/report.json"))
    for directory in paths:
        data = export(directory)
        count = sum(len(s["blocks"]) for s in data["sections"])
        print(f"{data['key']}: exported {count} bilingual/shared blocks ({data['status']})")


if __name__ == "__main__":
    main()
