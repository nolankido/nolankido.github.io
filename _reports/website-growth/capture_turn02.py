"""Reproduce the exact homepage compatibility record. Read-only unless --write."""
from __future__ import annotations
import argparse
import difflib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
BASE = '8f63c0436a45256cb2987cd93f77a9ef6e85df1b'
TREE = '016ad310e376ed25b8dd6ec2a8cbdb7d3e691417'
PATHS = ('_source/home.html', '_source/pages.json', 'assets/first-steps.css',
         'index.html', 'creative/index.html', 'sitemap.xml')
SOURCE_PREFIXES = ('_source/', '_scripts/', 'assets/', 'downloads/')
PROTECTED = ('_source/site.json', '_source/layout.html', '_source/identity.json',
             '_source/start-here.html', '_source/privacy.html', 'assets/contact.js',
             'ANALYTICS.md', '_source/poker/free-poker-learning-path.html')
sys.path[:0] = [str(ROOT / '_tests'), str(ROOT / '_scripts')]
from test_site import Page, build


def digest(raw):
    return hashlib.sha256(raw if isinstance(raw, bytes) else raw.encode('utf-8')).hexdigest()


def fingerprint(records):
    return digest(json.dumps(sorted((str(p), digest(v)) for p, v in records.items()), separators=(',', ':')))


def capture(ref=BASE):
    tree = subprocess.check_output(['git', 'rev-parse', ref + '^{tree}'], cwd=ROOT, text=True).strip()
    if tree != TREE:
        raise ValueError('Base tree is not the approved homepage predecessor')
    packed = subprocess.check_output(['git', 'archive', '--format=tar', ref], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(packed)) as archive:
        old = {m.name: archive.extractfile(m).read() for m in archive.getmembers() if m.isfile()}
    sources = {p.relative_to(ROOT).as_posix(): p.read_bytes()
               for folder in SOURCE_PREFIXES for p in (ROOT / folder).rglob('*')
               if p.is_file() and '__pycache__' not in p.parts}
    base_sources = {p: v for p, v in old.items() if p.startswith(SOURCE_PREFIXES)}
    if set(sources) != set(base_sources):
        raise ValueError('Unexpected source inventory change')
    if {p for p in sources if sources[p] != base_sources[p]} != set(PATHS[:3]):
        raise ValueError('Unexpected source, asset or script change')
    outputs = build.build_outputs()
    if any((ROOT / p).read_bytes() != v.encode('utf-8') for p, v in outputs.items()):
        raise ValueError('Rebuild generated files before capturing this candidate')
    base_outputs = {p: old[str(p)] for p in outputs}
    if {str(p) for p, v in outputs.items() if v.encode('utf-8') != base_outputs[p]} != set(PATHS[3:]):
        raise ValueError('Unexpected generated-output change')
    changes = {}
    for path in PATHS:
        before, after = old[path].decode('utf-8'), (ROOT / path).read_text(encoding='utf-8')
        blines, alines = before.splitlines(keepends=True), after.splitlines(keepends=True)
        bpos, apos = [0], [0]
        for line in blines: bpos.append(bpos[-1] + len(line))
        for line in alines: apos.append(apos[-1] + len(line))
        edits = [{'start': apos[c], 'end': apos[d], 'old': before[bpos[a]:bpos[b]], 'new': after[apos[c]:apos[d]]}
                 for tag, a, b, c, d in difflib.SequenceMatcher(a=blines, b=alines, autojunk=False).get_opcodes()
                 if tag != 'equal']
        changes[path] = {'old_sha256': digest(before), 'new_sha256': digest(after), 'edits': edits}
    new_home = next(p for p in build.public_pages() if p['id'] == 'home')
    base_home = next(p for p in json.loads(old['_source/pages.json']) if p['id'] == 'home')
    old_home = dict(new_home, updated=base_home['updated'])
    if any(old_home[k] != v for k, v in base_home.items()):
        raise ValueError('Homepage metadata changed beyond its actual revision date')
    page = Page(old['index.html'].decode('utf-8'))
    return {
        'version': 1, 'base_commit': BASE, 'base_tree': TREE, 'paths': changes,
        'pages': {'home': {'old': old_home, 'new': new_home}},
        'base_output_count': len(base_outputs), 'base_output_fingerprint': fingerprint(base_outputs),
        'base_source_count': len(base_sources), 'base_source_fingerprint': fingerprint(base_sources),
        'base_home_links': sorted({a['href'] for a in page.tags('a') if 'href' in a}),
        'base_home_ids': sorted({a['id'] for _, a in page.elements if 'id' in a}),
        'protected_source_hashes': {p: digest(old[p]) for p in PROTECTED},
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Prepare an unapproved candidate record')
    parser.add_argument('--base-ref', default=BASE, help='Exported workspaces may name a ref with the exact approved tree')
    args = parser.parse_args()
    try:
        expected = json.dumps(capture(args.base_ref), ensure_ascii=False, indent=2) + '\n'
        path = ROOT / '_tests/homepage-growth-change.json'
        if args.write:
            path.write_text(expected, encoding='utf-8')
        elif path.read_text(encoding='utf-8') != expected:
            raise ValueError('The committed compatibility record does not reproduce')
        print('PASS: exact six-file homepage delta; no historical baseline overwritten.')
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        raise SystemExit('Homepage capture failed: ' + str(error))
