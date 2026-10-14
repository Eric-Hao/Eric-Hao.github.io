"""Merge rewritten blog batches into the bilingual content files.

Batch files live in _content/rewrites/ and hold English and Chinese together, so a
rewrite can never drift out of parity. Running this script regenerates
articles.json (English), zh.json (Chinese) and syncs headlineZh in data.js.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / '_content'
BATCHES = CONTENT / 'rewrites'


def load_batches():
    merged = {}
    for path in sorted(BATCHES.glob('*.json')):
        data = json.loads(path.read_text())
        for key, value in data.items():
            if key in merged:
                raise SystemExit(f'{key} appears in more than one batch file')
            merged[key] = value
    return merged


def validate(key, item):
    problems = []
    for field in ('headline', 'headlineZh', 'dek', 'dekZh', 'keypoints', 'sections'):
        if field not in item:
            problems.append(f'missing {field}')
    if len(item.get('sections', [])) != 5:
        problems.append(f"expected 5 sections, found {len(item.get('sections', []))}")
    for index, section in enumerate(item.get('sections', [])):
        if len(section['p']) != len(section['pz']):
            problems.append(
                f"section {index} paragraph mismatch: {len(section['p'])} en / {len(section['pz'])} zh")
        if index and not section.get('h'):
            problems.append(f'section {index} needs an English heading')
        if not section.get('hz'):
            problems.append(f'section {index} needs a Chinese heading')
        for paragraph in section['p'] + section['pz']:
            if '\n' in paragraph:
                problems.append(f'section {index} has an embedded newline')
    if len(item.get('keypoints', [])) != 3:
        problems.append('expected 3 keypoints')
    for point in item.get('keypoints', []):
        if not point.get('en') or not point.get('zh'):
            problems.append('keypoint missing en or zh')
    return problems


def main():
    batches = load_batches()
    if not batches:
        raise SystemExit('No rewrite batches found in _content/rewrites/')

    articles = json.loads((CONTENT / 'articles.json').read_text())
    translations = json.loads((CONTENT / 'zh.json').read_text())

    failures = 0
    for key, item in batches.items():
        problems = validate(key, item)
        if problems:
            failures += 1
            print(f'SKIP {key}: ' + '; '.join(problems))
            continue
        articles[key] = {
            'headline': item['headline'],
            'dek': item['dek'],
            'sections': [[s['h'], '\n\n'.join(s['p'])] for s in item['sections']],
            'keypoints': [p['en'] for p in item['keypoints']],
        }
        translations[key] = {
            'headline': item['headlineZh'],
            'dek': item['dekZh'],
            'sections': [[s['hz'], '\n\n'.join(s['pz'])] for s in item['sections']],
            'keypoints': [p['zh'] for p in item['keypoints']],
        }
        print(f'ok   {key}')

    if failures:
        raise SystemExit(f'{failures} article(s) failed validation; nothing written')

    (CONTENT / 'articles.json').write_text(
        json.dumps(articles, ensure_ascii=False, indent=1) + '\n')
    (CONTENT / 'zh.json').write_text(
        json.dumps(translations, ensure_ascii=False, indent=1) + '\n')

    source = (ROOT / 'data.js').read_text()
    for key, item in batches.items():
        pattern = re.compile(
            r'("image": "%s",.*?"headlineZh": ")(.*?)(")' % re.escape(key), re.S)
        source, count = pattern.subn(lambda m: m.group(1) + item['headlineZh'] + m.group(3), source)
        if count != 1:
            print(f'note: headlineZh not synced for {key}')
    (ROOT / 'data.js').write_text(source)
    print(f'Merged {len(batches)} rewritten blogs.')


if __name__ == '__main__':
    main()
