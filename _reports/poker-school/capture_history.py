"""Capture or check this one release against its immutable deployed predecessor.

Use --write only while preparing the not-yet-approved Poker School candidate.
Earlier change records and baselines are never rewritten. The default is a
read-only reproduction check and requires the parent Git object locally.
"""
from difflib import SequenceMatcher
from hashlib import sha256
import argparse
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '_scripts'))
import build

BASE = '9021d4604c9427c37dc6c788753ddf9675dfc7ba'
PREFIXES = ('_source', '_scripts', 'assets', 'downloads')
NEW_SOURCES = {'_scripts/poker_school_release.py', '_source/poker/school.html',
               'assets/poker-school-interest.js', 'assets/poker-school.css'}
SOURCE_EDITS = {'_scripts/build.py', '_scripts/check_live.py', '_source/pages.json',
                '_source/poker/home.html', '_source/poker/study.html'}
OUTPUT_EDITS = {'find/index.html', 'poker/find/index.html', 'poker/index.html',
                'poker/study/index.html', 'sitemap.xml'}
EXTRA_EDITS = {'.github/workflows/site-checks.yml', '_reports/search-audit.json',
               '_reports/poker-search-intent/evaluate.py'}
NEW_OUTPUTS = {'poker/school/index.html'}
TARGET = '_tests/poker-school-change.json'


def digest(raw):
    return sha256(raw).hexdigest()


def fingerprint(records):
    pairs = sorted((path, digest(raw)) for path, raw in records.items())
    return digest(json.dumps(pairs, separators=(',', ':')).encode())


def exact_edits(path, old, new):
    split = (lambda s: re.split(r'(?=<)', s)) if path.endswith('.html') else (lambda s: s.splitlines(keepends=True))
    aa, bb = split(old), split(new)
    offsets = [0]
    for part in bb:
        offsets.append(offsets[-1] + len(part))
    edits = []
    for tag, a1, a2, b1, b2 in SequenceMatcher(None, aa, bb, autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        a, b = ''.join(aa[a1:a2]), ''.join(bb[b1:b2])
        prefix = 0
        while prefix < min(len(a), len(b)) and a[prefix] == b[prefix]:
            prefix += 1
        a, b = a[prefix:], b[prefix:]
        suffix = 0
        while suffix < min(len(a), len(b)) and a[-suffix - 1] == b[-suffix - 1]:
            suffix += 1
        if suffix:
            a, b = a[:-suffix], b[:-suffix]
        edits.append({'start': offsets[b1] + prefix, 'end': offsets[b1] + prefix + len(b),
                      'old': a, 'new': b})
    restored = new
    for edit in reversed(edits):
        if restored[edit['start']:edit['end']] != edit['new']:
            raise ValueError('Invalid edit offset: ' + path)
        restored = restored[:edit['start']] + edit['old'] + restored[edit['end']:]
    if restored != old:
        raise ValueError('Lossy predecessor reconstruction: ' + path)
    return edits


def capture(root=ROOT):
    archive = subprocess.check_output(['git', 'archive', BASE], cwd=root)
    with tarfile.open(fileobj=io.BytesIO(archive)) as source:
        prior = {entry.name: source.extractfile(entry).read() for entry in source if entry.isfile()}
    original = {p: raw for p, raw in prior.items() if p.split('/')[0] in PREFIXES}
    current = {p.relative_to(root).as_posix(): p.read_bytes() for folder in PREFIXES
               for p in (root / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    if set(current) - set(original) != NEW_SOURCES or set(original) - set(current):
        raise ValueError('Unexpected source inventory change')
    if {p for p in original if original[p] != current[p]} != SOURCE_EDITS:
        raise ValueError('Unexpected modification of an original source')
    outputs = {str(p): raw.encode() for p, raw in build.build_outputs().items()}
    # Evaluate the actual parent pipeline, not current metadata with a row removed.
    with TemporaryDirectory(prefix='poker-school-parent-') as folder:
        parent = Path(folder)
        for path, raw in prior.items():
            destination = parent / path
            if not destination.resolve().is_relative_to(parent.resolve()):
                raise ValueError('Unsafe archived path')
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
        command = ('import build,json;from pathlib import Path;out=build.build_outputs();'
                   'print(json.dumps({"pages":build.public_pages(),"outputs":list(map(str,out)),'
                   '"drift":[str(p) for p,s in out.items() if (build.ROOT/p).read_text()!=s]}))')
        metadata = json.loads(subprocess.check_output([sys.executable, '-c', command], cwd=parent / '_scripts'))
    if metadata['drift']:
        raise ValueError('The pinned predecessor has uncommitted build output')
    old_outputs = {p: prior[p] for p in metadata['outputs']}
    if set(outputs) - set(old_outputs) != NEW_OUTPUTS or set(old_outputs) - set(outputs):
        raise ValueError('Unexpected generated output inventory')
    if {p for p in old_outputs if old_outputs[p] != outputs[p]} != OUTPUT_EDITS:
        raise ValueError('Unexpected modification of an old generated output')
    old_pages = metadata['pages']
    current_pages = build.public_pages()
    added_pages = [p for p in current_pages if p['id'] not in {q['id'] for q in old_pages}]
    if [p for p in current_pages if p not in added_pages] != old_pages or len(added_pages) != 1 or added_pages[0]['id'] != 'poker-school':
        raise ValueError('Existing page identity or order changed')
    data = {'version': 1, 'base_commit': BASE, 'paths': {},
            'new_files': {p: digest(current[p]) for p in sorted(NEW_SOURCES)},
            'new_outputs': {p: digest(outputs[p]) for p in sorted(NEW_OUTPUTS)},
            'new_pages': added_pages,
            'base_outputs': {p: digest(raw) for p, raw in old_outputs.items()},
            'base_source_count': len(original), 'base_source_fingerprint': fingerprint(original),
            'base_pages_fingerprint': digest(json.dumps(old_pages, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode())}
    for path in sorted(SOURCE_EDITS | OUTPUT_EDITS | EXTRA_EDITS):
        old_raw, new_raw = prior[path], (root / path).read_bytes()
        if old_raw == new_raw:
            raise ValueError('A declared edit did not occur: ' + path)
        data['paths'][path] = {'old_sha256': digest(old_raw), 'new_sha256': digest(new_raw),
                               'edits': exact_edits(path, old_raw.decode(), new_raw.decode())}
    return json.dumps(data, ensure_ascii=False, indent=2) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Write only this unapproved candidate record')
    args = parser.parse_args()
    expected = capture()
    target = ROOT / TARGET
    if args.write:
        target.write_text(expected)
    elif not target.exists() or target.read_text() != expected:
        raise SystemExit('Poker School compatibility record differs from the exact candidate')
    print('Exact parent source, output, metadata and change fingerprints match.')
