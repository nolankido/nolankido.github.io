"""Reproduce exact reviewed source and store objects, never update a release ref."""
from pathlib import Path
from hashlib import sha1, sha256
import base64
import json
import os
import subprocess
import urllib.request
import zlib

BASE = '9c77098763f7f7e43d80a8e6994283484593b78e'
BASE_TREE = 'f1ba18274110fd1d9bd470ada5f3b7d064b21d13'
EXPECTED_TREE = '5813b88bf927256f8aba942952511741527a85f5'
REPO = 'nolankido/nolankido.github.io'
ROOT = Path.cwd()

def output(*args):
    return subprocess.check_output(args, text=True).strip()

def run(*args):
    subprocess.run(args, check=True)

def replace(path, before, after):
    target = ROOT / path
    text = target.read_text(encoding='utf-8')
    if text.count(before) != 1:
        raise ValueError('Ambiguous source replacement: ' + path)
    target.write_text(text.replace(before, after, 1), encoding='utf-8')

def safe_path(name):
    path = Path(name)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('Unsafe payload path')
    return ROOT / path

assert output('git', 'rev-parse', 'HEAD') == BASE
assert output('git', 'rev-parse', 'HEAD^{tree}') == BASE_TREE
assert output('git', 'status', '--porcelain') == ''
compressed = Path(os.environ['INPUT_PAYLOAD']).read_bytes()
assert sha256(compressed).hexdigest() == 'efc50174782442705657e6ea886d97f7791fb4711e378fcb8dc421c671ecb87c'
payload = json.loads(zlib.decompress(compressed))
assert payload['expected_tree'] == 'bcb41f9947e85c20b4dcf6988b79790a5ae1b651'
exec(compile(payload['scripts']['apply_catalog.py'], 'apply_catalog.py', 'exec'), {'__name__': '__main__'})
run('python', '_scripts/build.py')
exec(compile(payload['scripts']['add_history.py'], 'add_history.py', 'exec'), {'__name__': '__main__'})
for name, text in payload['files'].items():
    path = safe_path(name)
    if path.exists():
        raise ValueError('New candidate file already exists: ' + name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
for name in ('_tests/task_brief_walkthrough_history.py', '_tests/rules_reference_history.py'):
    replace(name, 'import json\n', 'import json\nimport resource_review_history\n')
replace('_tests/task_brief_walkthrough_history.py', 'def before(path, data):\n',
        'def before(path, data):\n    data = resource_review_history.before(path, data)\n')
replace('_tests/rules_reference_history.py', 'def resources(records):\n',
        'def resources(records):\n    records = resource_review_history.resources(records)\n')
replace('_tests/test_rules_reference.py', 'import rules_reference_history as history\n',
        'import rules_reference_history as history\nimport resource_review_history\n')
replace('_tests/test_rules_reference.py', "changed = [e['id'] for e in self.resources if e != prior[e['id']]]",
        "changed = [e['id'] for e in resource_review_history.resources(self.resources) if e != prior[e['id']]]")
replace('_tests/test_resource_collections.py', 'import unittest\n',
        'import unittest\nimport resource_review_history\n')
replace('_tests/test_resource_collections.py', "for r in self.resources:\n            if r['id'] in batch['accepted_ids']:",
        "for r in resource_review_history.resources(self.resources):\n            if r['id'] in batch['accepted_ids']:")
run('git', 'add', '--', *payload['changed_paths'])
assert output('git', 'write-tree') == payload['expected_tree']
run('python', os.environ['CORRECTION_SCRIPT'])
paths = sorted(payload['changed_paths'] + ['_tests/test_poker_school_history.py'])
run('git', 'add', '--', *paths)
assert sorted(output('git', 'diff', '--cached', '--name-only').splitlines()) == paths
assert output('git', 'write-tree') == EXPECTED_TREE
assert output('git', 'diff', '--name-only') == ''
run('python', '_scripts/build.py', '--check')
for suite in ('test_resource_review_20261023.py', 'test_rules_reference.py',
              'test_resource_collections.py', 'test_poker_school_history.py',
              'test_task_brief_walkthrough.py'):
    run('python', '-m', 'unittest', 'discover', '-s', '_tests', '-p', suite, '-v')
assert output('git', 'write-tree') == EXPECTED_TREE
assert output('git', 'diff', '--name-only') == ''

# The token stays in memory and is used solely for creating immutable objects.
# No commits, branches, release references, visibility or settings are changed.
token = os.environ['GH_TOKEN']
def post(endpoint, data):
    request = urllib.request.Request('https://api.github.com/repos/' + REPO + '/git/' + endpoint,
        data=json.dumps(data).encode(), method='POST', headers={
            'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json',
            'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28',
            'User-Agent': 'nk-bounded-resource-preparation'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)
elements = []
for name in paths:
    raw = safe_path(name).read_bytes()
    expected = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    actual = post('blobs', {'content': base64.b64encode(raw).decode(), 'encoding': 'base64'})['sha']
    assert actual == expected, name
    elements.append({'path': name, 'mode': '100644', 'type': 'blob', 'sha': actual})
tree = post('trees', {'base_tree': BASE_TREE, 'tree': elements})['sha']
assert tree == EXPECTED_TREE
receipt = Path(os.environ['RECEIPT_DIR']); receipt.mkdir(parents=True, exist_ok=True)
(receipt / 'prepared-resource-review.json').write_text(json.dumps({
    'base_commit': BASE, 'base_tree': BASE_TREE, 'candidate_tree': tree,
    'changed_paths': paths, 'focused_suites_passed': 5,
    'release_refs_changed': False, 'full_release_qualification': False}, indent=2) + '\n')
print('PREPARED_RESOURCE_TREE=' + tree)
