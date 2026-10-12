"""Capture from a separately checked-out original release, never edited output."""
from pathlib import Path
import argparse,hashlib,json,re
parser=argparse.ArgumentParser()
parser.add_argument('--original-root',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
root=args.original_root.resolve()
if root==Path(__file__).resolve().parents[1]:
    raise ValueError('Use an independent original checkout, not the working tree')
record={'base_commit':'0ffc618d4b2b390f61dccde466aca60375600d43','base_tree':'430acf15437692935bb2662dda21255415aa5a76','bodies':{},'files':{},'manifest':json.loads((root/'_source/pages.json').read_text())}
source=(root/'_source/technology/home.html').read_text()
record['original_technology_panel']=re.search(r'<!-- AI task choice: start -->\n.*?<!-- AI task choice: end -->\n',source,re.S)[0]
record['technology_schema']=re.search(r'<script type="application/ld\+json">.*?</script>',(root/'technology/index.html').read_text(),re.S)[0]
for p in root.rglob('*'):
    if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts:continue
    rel=p.relative_to(root).as_posix()
    if rel.endswith('.html') and not rel.startswith('_'):
        body=re.search(r'<body\b[^>]*>(.*?)</body>',p.read_text(),re.S)
        if body:record['bodies'][rel]=hashlib.sha256(body[1].encode()).hexdigest()
    if rel.startswith(('_source/','assets/','downloads/')) or rel in ['feed.xml','writing.xml','technology/feed.xml','poker/feed.xml','living-well/feed.xml']:
        record['files'][rel]=hashlib.sha256(p.read_bytes()).hexdigest()
assert len(record['bodies'])==170 and len(record['files'])==221
args.output.write_text(json.dumps(record,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
