"""Capture only this release's declared changes against deployed PR #105.

Earlier baseline files and change records are never rewritten.
"""
from difflib import SequenceMatcher
from hashlib import sha256
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '_scripts'))
import build

BASE = 'ca0264c251f2c999a8375d9e748521fe46ef22fe'
PREFIXES = ('_source/', '_scripts/', 'assets/', 'downloads/')
SOURCE_EDITS = {
    '_scripts/build.py', '_scripts/check_live.py', '_scripts/poker_course.py',
    '_scripts/poker_beginner_path.py', '_source/pages.json', '_source/privacy.html',
    '_source/search-entrypoints.json',
    '_source/poker/beginner-learning-path.html', '_source/poker/study.html',
    'downloads/poker-beginner-study-card.txt',
}
NEW_FILES = {'_scripts/poker_progress.py', 'assets/poker-progress.css', 'assets/poker-progress.js'}
OUTPUT_EDITS = {
    'privacy/index.html', 'poker/study/index.html', 'sitemap.xml',
    'find/index.html', 'poker/find/index.html',
    'poker/free-poker-learning-path/index.html', 'downloads/poker-beginner-study-card.txt',
    *('poker/' + slug + '/index.html' for slug, _ in build.poker_course.LESSONS),
}
EXTRAS = {'README.md', '.github/workflows/site-checks.yml'}
EXTRA_EDITS = {'.github/workflows/site-checks.yml'}


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
    if set(current) - set(original) != NEW_FILES or set(original) - set(current):
        raise ValueError('Unexpected source/asset inventory change')
    changed_sources = {p for p in original if original[p] != current[p]}
    if changed_sources != SOURCE_EDITS:
        raise ValueError('Unexpected source changes: ' + repr(changed_sources))
    outputs = {str(p): s.encode() for p, s in build.build_outputs().items()}
    old_outputs = {p: prior[p] for p in outputs}
    changed_outputs = {p for p in outputs if old_outputs[p] != outputs[p]}
    if changed_outputs != OUTPUT_EDITS:
        raise ValueError('Unexpected output changes: ' + repr(changed_outputs))
    changed_extras = {p for p in EXTRAS if (ROOT / p).read_bytes() != prior[p]}
    if changed_extras != EXTRA_EDITS:
        raise ValueError('Unexpected release-configuration changes')
    baseline = {
        'commit': BASE, 'source_count': len(original), 'output_count': len(old_outputs),
        'source_fingerprint': fingerprint(original), 'output_fingerprint': fingerprint(old_outputs),
        'extras': {p: sha256(prior[p]).hexdigest() for p in sorted(EXTRAS)},
        'teaching_inputs': json.loads(prior['_reports/poker-teaching-review/scope.json'])['source_files'],
        'teaching_fingerprint': json.loads(prior['_reports/poker-teaching-review/scope.json'])['fingerprint'],
    }
    path = ROOT / '_tests/poker-progress-baseline.json'
    encoded = json.dumps(baseline, indent=2) + '\n'
    if path.exists() and path.read_text() != encoded:
        raise ValueError('Do not rewrite a frozen baseline')
    path.write_text(encoded)
    # Raw manifest records and public metadata are different representations.
    # Execute the exact parent metadata pipeline from its archived sources.
    with tempfile.TemporaryDirectory(prefix='poker-progress-parent-') as folder:
        parent_root = Path(folder)
        for path, raw in prior.items():
            if path.startswith(('_source/', '_scripts/')):
                target = parent_root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
        old_pages = {p['id']: p for p in json.loads(subprocess.check_output(
            [sys.executable, '-c', 'import build, json; print(json.dumps(build.public_pages()))'],
            cwd=parent_root / '_scripts'))}
    new_pages = {p['id']: p for p in build.public_pages()}
    if set(old_pages) != set(new_pages):
        raise ValueError('Unexpected public page inventory change')
    changed_pages = {key for key in old_pages if old_pages[key] != new_pages[key]}
    if changed_pages != {'privacy', 'poker-study'}:
        raise ValueError('Unexpected public metadata changes: ' + repr(changed_pages))
    pairs = {key: {'old': old_pages[key], 'new': new_pages[key]} for key in sorted(changed_pages)}
    delta = {'commit': BASE, 'paths': {}, 'pages': pairs,
             'new_files': {p: sha256(current[p]).hexdigest() for p in sorted(NEW_FILES)}}
    for path in sorted(SOURCE_EDITS | OUTPUT_EDITS | EXTRA_EDITS):
        old_raw = prior[path]
        new_raw = current[path] if path in current else outputs[path] if path in outputs else (ROOT / path).read_bytes()
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
    (ROOT / '_tests/poker-progress-change.json').write_text(
        json.dumps(delta, ensure_ascii=False, indent=2) + '\n')
    print('Captured', len(delta['paths']), 'bounded changes and', len(NEW_FILES),
          'new files; preserved', len(original), 'source/assets and', len(outputs), 'outputs')


if __name__ == '__main__':
    capture()
