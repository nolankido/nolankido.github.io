"""Record the bounded study-list change against its actual published predecessor.

Historical baselines and previous release deltas are never rewritten.
"""
from difflib import SequenceMatcher
from hashlib import sha256
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '_scripts'))
import build

BASE = 'ff403da6eeb4afbca704e17ce3592a2977011dcd'
PREFIXES = ('_source/', '_scripts/', 'assets/', 'downloads/')
ALLOWED = {'_source/poker/find.html', 'assets/poker-finder.js',
           'assets/poker-finder.css', 'poker/find/index.html'}


def fingerprint(items):
    rows = sorted((str(path), sha256(raw).hexdigest()) for path, raw in items.items())
    return sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()


def capture():
    archive = subprocess.check_output(['git', 'archive', BASE], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as files:
        prior = {m.name: files.extractfile(m).read() for m in files if m.isfile()}
    original = {p: raw for p, raw in prior.items() if p.startswith(PREFIXES)}
    current = {p.relative_to(ROOT).as_posix(): p.read_bytes() for d in PREFIXES
               for p in (ROOT / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    outputs = {str(p): s.encode() for p, s in build.build_outputs().items()}
    if set(original) != set(current):
        raise ValueError('Unexpected source/asset inventory change')
    old_outputs = {p: prior[p] for p in outputs}
    changed = {p for p in original if original[p] != current[p]} | {
        p for p in outputs if old_outputs[p] != outputs[p]}
    if changed != ALLOWED:
        raise ValueError('Expected only the reviewed Finder study-list change: ' + repr(changed))
    baseline = {'commit': BASE, 'source_count': len(original), 'output_count': len(old_outputs),
                'source_fingerprint': fingerprint(original), 'output_fingerprint': fingerprint(old_outputs)}
    path = ROOT / '_tests/poker-study-list-baseline.json'
    encoded = json.dumps(baseline, indent=2) + '\n'
    if path.exists() and path.read_text() != encoded:
        raise ValueError('Do not rewrite a frozen baseline')
    path.write_text(encoded)
    delta = {'commit': BASE, 'paths': {}}
    for path in sorted(ALLOWED):
        old_raw = prior[path]
        new_raw = current[path] if path in current else outputs[path]
        old, new = old_raw.decode(), new_raw.decode()
        aa, bb = old.splitlines(keepends=True), new.splitlines(keepends=True)
        offsets = [0]
        for line in bb:
            offsets.append(offsets[-1] + len(line))
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
            while suffix < min(len(a), len(b)) and a[-suffix-1] == b[-suffix-1]:
                suffix += 1
            if suffix:
                a, b = a[:-suffix], b[:-suffix]
            edits.append({'start': offsets[b1] + prefix, 'end': offsets[b1] + prefix + len(b),
                          'old': a, 'new': b})
        restored = new
        for edit in reversed(edits):
            assert restored[edit['start']:edit['end']] == edit['new']
            restored = restored[:edit['start']] + edit['old'] + restored[edit['end']:]
        assert restored == old
        delta['paths'][path] = {'old_sha256': sha256(old_raw).hexdigest(),
                               'new_sha256': sha256(new_raw).hexdigest(), 'edits': edits}
    (ROOT / '_tests/poker-study-list-change.json').write_text(
        json.dumps(delta, ensure_ascii=False, indent=2) + '\n')
    print('Captured four exact changes; preserved', len(original), 'source/assets and', len(outputs), 'outputs')


if __name__ == '__main__':
    capture()
