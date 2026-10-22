"""Reproduce one pinned candidate and store Git objects only, never references."""
import base64
from difflib import SequenceMatcher
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.request import Request, urlopen
import zlib

BASE = '564a9d7eaf634497767ade3db4bcb6a3b2bd9c61'
BASE_TREE = '4dae6d006976b880d87d9afd05f3dabe099b491b'
EXPECTED = '75e2d74ad15c5c9cbddb1d4c2d226c60f08d6a44'
PAYLOAD_HASH = 'a21038df182dd5ce63ad5711739ca21d8222f283fd5f11f2cf042d26e5ab4853'
PRODUCTION = ['_source/pages.json', '_source/technology/task-brief.html',
              'sitemap.xml', 'technology/task-brief/index.html']
RECORD = '_tests/task-brief-walkthrough-change.json'
REPOSITORY = 'nolankido/nolankido.github.io'

def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def main():
    directory = Path(sys.argv[1]).resolve()
    encoded = ''.join((directory / f'payload-{i}.txt').read_text().strip() for i in (1, 2, 3))
    raw = zlib.decompress(base64.b64decode(encoded, validate=True))
    assert sha256(raw).hexdigest() == PAYLOAD_HASH, 'Transport digest mismatch'
    payload = json.loads(raw)
    assert (payload['base'], payload['base_tree'], payload['expected_tree']) == (BASE, BASE_TREE, EXPECTED)
    local = '--local' in sys.argv
    source = os.environ.get('LOCAL_BASE', BASE) if local else BASE
    subprocess.run(['git', 'checkout', '--detach', source], check=True)
    assert git('rev-parse', 'HEAD^{tree}') == BASE_TREE
    tracked = git('ls-files', '-z').split('\0')
    inventory = sorted(p for p in tracked if p and not p.startswith(('_tests/', '_reports/')))
    assert len(inventory) == 714
    rows = [(p, sha256(Path(p).read_bytes()).hexdigest()) for p in inventory]
    fingerprint = sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()
    old = {p: Path(p).read_bytes() for p in PRODUCTION}
    old_pages = json.loads(old['_source/pages.json'])
    for name, change in payload['changes'].items():
        path = Path(name)
        assert not path.is_absolute() and '..' not in path.parts
        assert name.startswith(('_tests/', '_reports/', '_source/'))
        if 'new_file' in change:
            assert not path.exists(), name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(change['new_file'], encoding='utf-8')
        else:
            value = path.read_bytes()
            assert sha256(value).hexdigest() == change['old_sha256'], name
            edits = change['edits']
            end = 0
            for edit in edits:
                assert type(edit['start']) is int and type(edit['end']) is int
                assert end <= edit['start'] <= edit['end'] <= len(value)
                assert value[edit['start']:edit['end']] == edit['old'].encode(), name
                end = edit['end']
            for edit in reversed(edits):
                value = value[:edit['start']] + edit['new'].encode() + value[edit['end']:]
            assert sha256(value).hexdigest() == change['new_sha256'], name
            path.write_bytes(value)
    subprocess.run([sys.executable, '_scripts/build.py'], check=True)
    record = {'version': 1, 'base_commit': BASE, 'paths': {}}
    for name in PRODUCTION:
        current = Path(name).read_bytes()
        original_lines, new_lines = old[name].splitlines(keepends=True), current.splitlines(keepends=True)
        offsets = [0]
        for line in new_lines:
            offsets.append(offsets[-1] + len(line))
        edits = []
        for tag, i1, i2, j1, j2 in SequenceMatcher(None, original_lines, new_lines, autojunk=False).get_opcodes():
            if tag != 'equal':
                edits.append([offsets[j1], offsets[j2], base64.b64encode(b''.join(original_lines[i1:i2])).decode()])
        record['paths'][name] = {'old_sha256': sha256(old[name]).hexdigest(),
                                'new_sha256': sha256(current).hexdigest(), 'edits': edits}
    new_pages = json.loads(Path('_source/pages.json').read_text())
    record['page'] = {'old': next(p for p in old_pages if p['id'] == 'task-brief'),
                      'new': next(p for p in new_pages if p['id'] == 'task-brief')}
    record['production_count'] = len(inventory)
    record['production_fingerprint'] = fingerprint
    Path(RECORD).write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    names = sorted(set(payload['changes']) | set(PRODUCTION) | {RECORD})
    assert len(names) == 14
    subprocess.run(['git', 'add', '--', *names], check=True)
    assert git('diff', '--cached', '--name-only').splitlines() == names
    assert git('write-tree') == EXPECTED, 'Candidate differs from reviewed local tree'
    for pattern in ('test_task_brief_walkthrough.py', 'test_task_brief_error_state.py',
                    'test_task_brief_growth.py', 'test_feedback_context.py'):
        subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', '_tests', '-p', pattern, '-v'], check=True)
    subprocess.run([sys.executable, '_scripts/build.py', '--check'], check=True)
    assert git('write-tree') == EXPECTED
    if not local:
        assert os.environ['GITHUB_REPOSITORY'] == REPOSITORY
        token = os.environ['GH_TOKEN']
        def post(endpoint, body):
            req = Request('https://api.github.com/repos/' + REPOSITORY + '/git/' + endpoint,
                data=json.dumps(body).encode(), method='POST',
                headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                         'X-GitHub-Api-Version': '2022-11-28', 'Content-Type': 'application/json'})
            with urlopen(req, timeout=45) as response:
                return json.load(response)
        elements = []
        for name in names:
            value = Path(name).read_bytes()
            expected_blob = sha1(f'blob {len(value)}\0'.encode() + value).hexdigest()
            result = post('blobs', {'content': base64.b64encode(value).decode(), 'encoding': 'base64'})
            assert result['sha'] == expected_blob
            elements.append({'path': name, 'mode': '100644', 'type': 'blob', 'sha': result['sha']})
        tree = post('trees', {'base_tree': BASE_TREE, 'tree': elements})
        assert tree['sha'] == EXPECTED
    receipt = {'base_commit': BASE, 'candidate_tree': EXPECTED, 'paths': names,
               'scope': 'Stored Git objects only. No repository reference changed.'}
    (directory / 'candidate.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)

if __name__ == '__main__':
    main()
