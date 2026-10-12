"""Capture the pre-release tree for reproducible historical checks. Run explicitly."""
from pathlib import Path
from hashlib import sha256
from xml.etree import ElementTree as ET
import argparse,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
COMMIT='4f80aeb5b20678d4a95e965043342a3f992eb8ad'
TREE='46d7d7f82f24d7ea11f68fa896e06f62760c033c'
def signature(el):
    return [el.tag,[list(a) for a in sorted(el.attrib.items())],(el.text or '').strip(),[signature(c) for c in el]]
def capture(ref):
    def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
    assert git('rev-parse',ref+'^{tree}').decode().strip()==TREE, 'Baseline tree must be the reviewed production tree'
    def read(path):return git('show',ref+':'+path)
    files=git('ls-tree','-r','--name-only',ref).decode().splitlines()
    b={'files':{p:sha256(read(p)).hexdigest() for p in files if p.startswith(('_source/','assets/','downloads/'))},
       'manifest':json.loads(read('_source/pages.json')),'feeds':{},'bodies':{},'all_bodies':{},'icon':sha256(read('favicon.svg')).hexdigest(),
       'baseline_commit':COMMIT,'baseline_tree':TREE}
    for path in ['feed.xml','poker/feed.xml','living-well/feed.xml','technology/feed.xml','writing.xml']:
        channel=ET.fromstring(read(path)).find('channel')
        b['feeds'][path]={'items':{i.findtext('guid'):signature(i) for i in channel.findall('item')},'channel':[signature(e) for e in channel if e.tag!='item']}
    for path in files:
        if not path.startswith('_') and path.endswith('.html'):
            body=re.search(rb'<body\b[^>]*>(.*?)</body>',read(path),re.S)[1]
            b['all_bodies'][path]=sha256(body).hexdigest()
            if path not in {'notes/index.html','find/index.html'}:b['bodies'][path]=b['all_bodies'][path]
    return b
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--ref',default=COMMIT);args=parser.parse_args()
    (ROOT/'_tests/ai-task-choice-baseline.json').write_text(json.dumps(capture(args.ref),indent=2,sort_keys=True)+'\n')
