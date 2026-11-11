"""Verify routes, paired content, provenance inventory and generated local links.

Run after build_home.py and build_articles.py. Optional --skill-dir additionally
runs the pinned paper-deep-reader strict checks and saves each validation log.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit
from deep_read_content import CONTENT, ROOT, REPORTS, validate_report, markdown

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(); self.path=path; self.ids=[]; self.refs=[]; self.classes=[]; self.images=[]
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); self.classes.extend(a.get('class','').split())
        if 'id' in a:self.ids.append(a['id'])
        if tag=='img':self.images.append(a)
        for attr in ('src','href'):
            if attr in a:self.refs.append(a[attr])


def chapter_digest(markup):
    parts=re.findall(r'<section id="section-\d+".*?</section>',markup,re.S)
    return hashlib.sha256('\n'.join(parts).encode()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--skill-dir',type=Path); args=ap.parse_args()
    papers=json.loads((ROOT/'data.js').read_text().removeprefix('const papers = ').rstrip(';\n'))
    routes={p['image']:p['article'] for p in papers}
    baseline=json.loads((CONTENT/'tests/route-baseline.json').read_text())
    errors=[]
    def check(condition,message):
        if not condition:errors.append(message)
    check(routes==baseline['routes'],'The original 22-route contract changed')
    pages={p:Page(p) for p in [ROOT/'index.html',*[ROOT/route/'index.html' for route in routes.values()]]}
    for file,page in pages.items():
        check(len(page.ids)==len(set(page.ids)),f'Duplicate IDs: {file.relative_to(ROOT)}')
        check('katex-error' not in page.classes,f'Unrendered KaTeX: {file.relative_to(ROOT)}')
        for img in page.images:check(bool(img.get('alt')),f'Image alt missing: {file.relative_to(ROOT)}')
        for value in page.refs:
            u=urlsplit(value)
            if u.scheme or u.netloc:continue
            target=(file.parent/unquote(u.path)).resolve() if u.path else file
            if u.path.startswith('/'):target=(ROOT.parent/unquote(u.path).lstrip('/')).resolve()
            check(target.exists(),f'Missing local target {value}: {file.relative_to(ROOT)}')
            if target.is_dir():target=target/'index.html'
            if u.fragment and target in pages:check(unquote(u.fragment) in pages[target].ids,f'Missing anchor {value}: {file.relative_to(ROOT)}')
    complete=[];blocked=[];total_visuals=key_visuals=pairs=0
    for key,route in routes.items():
        directory=REPORTS/key; page=pages[ROOT/route/'index.html']
        if (directory/'blocker.json').exists():
            blocked.append(key); check('source-gap' in page.classes,f'Missing source-gap notice: {key}')
            check('deep-read' not in page.classes,f'Source-blocked note incorrectly replaced: {key}')
            check(chapter_digest((ROOT/route/'index.html').read_text())==baseline['blocked_chapter_sha256'][key],f'Legacy prose changed: {key}')
            continue
        d=validate_report(json.loads((directory/'report.json').read_text()),key)
        check(d['status']=='complete',f'Incomplete report: {key}')
        check((directory/'report.md').read_text()==markdown(d),f'Markdown stale: {key}')
        check('deep-read' in page.classes,f'Deep-read HTML stale: {key}')
        check(sum(1 for x in page.ids if re.fullmatch(r'section-\d+',x))==6,f'Not six article sections: {key}')
        n=sum('shared' not in block for s in d['sections'] for block in s['blocks']); pairs+=n
        check(page.classes.count('bilingual-block')==n,f'Paired-block count differs: {key}')
        check(page.classes.count('lang-en')==n,f'English block count differs: {key}')
        # Chinese source-note is an extra block outside the paired essay.
        check(page.classes.count('lang-zh')==n+1,f'Chinese block count differs: {key}')
        m=json.loads((directory/'assets/visual_manifest.json').read_text()); sm=json.loads((directory/'source_map.json').read_text())
        total_visuals+=len(m['visuals']);k=sum(bool(v['key']) for v in m['visuals']);key_visuals+=k
        check(sm['visual_coverage']['total_numbered']==len(m['visuals']),f'Inventory count mismatch: {key}')
        check(sm['visual_coverage']['key']==sm['visual_coverage']['key_explained']==k,f'Key visual coverage mismatch: {key}')
        for v in m['visuals']:
            if not v['key']:continue
            check(v['selected_for_report'] and v['visual_verification'] in ['complete','externally-verified'],f'Key visual unverified: {key}/{v.get("id")}')
            check((directory/'assets'/v['selected_asset']).is_file(),f'Missing selected visual: {key}/{v.get("id")}')
        if args.skill_dir:
            cmd=['python3',str(args.skill_dir/'scripts/validate_report.py'),str(directory/'report.md'),'--mode','explain','--manifest',str(directory/'assets/visual_manifest.json'),'--source-map',str(directory/'source_map.json'),'--strict','--preview',str(directory/'report.preview.html')]
            run=subprocess.run(cmd,capture_output=True,text=True);(directory/'validation.txt').write_text(run.stdout+run.stderr);check(run.returncode==0,f'Strict validation failed: {key}')
        complete.append(key)
    result={'routes':len(routes),'complete_reports':len(complete),'source_blocked':blocked,'bilingual_pairs':pairs,'numbered_visuals':total_visuals,'key_visuals_explained':key_visuals,'checked_html_pages':len(pages),'strict_report_checks':'run' if args.skill_dir else 'not requested','errors':errors}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(bool(errors))

if __name__=='__main__':main()
