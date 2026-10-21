"""Isolated transfer helper. Never merge this file or its workflow."""
from pathlib import Path
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys

BASE = '82c0a82df9969c2255e3c3ebbaacf290faeef78e'
BASE_TREE = '01a2456802afc4594015d57f0319406c2564fa26'
TREE = '4dae6d006976b880d87d9afd05f3dabe099b491b'
ROOT = Path.cwd()
TEMP = Path(os.environ['RUNNER_TEMP'])
ADDED = ['_tests/task_brief_error_history.py', '_tests/task-brief-error-change.json',
         '_tests/test_task_brief_error_state.py', '_reports/website-growth/turn-15-task-brief-error-state.md']
PATHS = sorted(ADDED + ['assets/task-brief.js', 'technology/task-brief/index.html',
                       '_tests/feedback_context_history.py', '_tests/test_feedback_context.py',
                       '_tests/test_task_brief_growth.py', '_tests/task_brief_browser.py'])


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def replace(path, old, new):
    file = ROOT / path
    content = file.read_text(encoding='utf-8')
    if content.count(old) != 1:
        raise ValueError('Ambiguous predecessor: ' + path)
    file.write_text(content.replace(old, new, 1), encoding='utf-8')


def api(endpoint, payload):
    run = subprocess.run(['gh', 'api', '--method', 'POST',
                          'repos/' + os.environ['GITHUB_REPOSITORY'] + '/git/' + endpoint,
                          '--input', '-'], input=json.dumps(payload), text=True,
                         capture_output=True, check=True)
    return json.loads(run.stdout)


assert git('rev-parse', 'HEAD') == BASE
if '--publish' not in sys.argv:
    for path in ADDED:
        shutil.copyfile(TEMP / 'brief-inputs' / path, ROOT / path)
    replace('assets/task-brief.js',
            "      input.removeAttribute('aria-invalid');\n      get(key + '-error').hidden = true;",
            "      input.removeAttribute('aria-invalid');\n      get(key + '-error').textContent = '';\n      get(key + '-error').hidden = true;")
    replace('_tests/feedback_context_history.py', 'import json\n',
            'import json\nimport task_brief_error_history\n')
    replace('_tests/feedback_context_history.py', 'def before(path, data):\n',
            'def before(path, data):\n    data = task_brief_error_history.before(path, data)\n')
    replace('_tests/test_feedback_context.py', 'import feedback_context_history as history\n',
            'import feedback_context_history as history\nimport task_brief_error_history\n')
    replace('_tests/test_feedback_context.py', '            new = self.outputs[path]\n',
            '            new = task_brief_error_history.before(path, self.outputs[path])\n')
    replace('_tests/test_feedback_context.py', '            raw = (ROOT / path).read_bytes()\n',
            '            raw = task_brief_error_history.before(path, (ROOT / path).read_bytes())\n')
    replace('_tests/test_task_brief_growth.py', 'import turn04_public_source_history\n',
            'import turn04_public_source_history\nimport task_brief_error_history\n')
    replace('_tests/test_task_brief_growth.py', "        raw=(ROOT/'assets/task-brief.js').read_bytes()\n",
            "        raw=task_brief_error_history.before('assets/task-brief.js', (ROOT/'assets/task-brief.js').read_bytes())\n")
    anchor = "    page.locator('[data-brief-example=\"writing\"] summary').click()\n"
    addition = '''    # An explicitly described hidden error still contributes to the browser's
    # accessible description. Editing must clear its text, not only hide it.
    report['error_description_checks'] = 0
    for key in ['goal', 'materials', 'output', 'review']:
        field = page.locator('#brief-' + key)
        help_text = page.locator('#brief-' + key + '-help').inner_text()
        expect(field).to_have_accessible_description(help_text + ' Add a short answer to this required field.')
        field.fill('Fictional ' + key + ' for a sorting checklist.')
        expect(field).to_have_accessible_description(help_text)
        expect(page.locator('#brief-' + key + '-error')).to_have_text('')
        expect(page.locator('#brief-' + key + '-error')).to_be_hidden()
        assert field.get_attribute('aria-invalid') is None
        report['error_description_checks'] += 1
    # Clearing a prior warning does not mean an unfinished field is validated.
    # A fresh Assemble must still report whitespace-only required content.
    page.locator('#brief-review').fill('   ')
    page.locator('#brief-build').click()
    expect(page.locator('#brief-review')).to_be_focused()
    expect(page.locator('#brief-review')).to_have_attribute('aria-invalid', 'true')
    page.locator('#brief-review').fill('Compare every item with the supplied source.')
    expect(page.locator('#brief-review')).to_have_accessible_description(page.locator('#brief-review-help').inner_text())
    report['error_description_checks'] += 1
    # Programmatic length injection exercises the optional field's existing
    # validator without changing its normal native maxlength restriction.
    page.locator('#brief-limits').evaluate("node => { node.value = 'x'.repeat(601); }")
    page.locator('#brief-build').click()
    expect(page.locator('#brief-limits')).to_have_attribute('aria-invalid', 'true')
    expect(page.locator('#brief-limits')).to_have_accessible_description(
        page.locator('#brief-limits-help').inner_text() + ' Shorten this to 600 characters or fewer.')
    page.locator('#brief-limits').fill('')
    expect(page.locator('#brief-limits')).to_have_accessible_description(page.locator('#brief-limits-help').inner_text())
    expect(page.locator('#brief-limits-error')).to_have_text('')
    page.locator('#brief-build').click()
    expect(page.locator('#brief-result')).to_be_visible()
    report['error_description_checks'] += 1
    page.locator('#brief-clear').click()
    page.locator('#brief-confirm-yes').click()
'''
    replace('_tests/task_brief_browser.py', anchor, addition + anchor)
    subprocess.run(['python', '_scripts/build.py'], check=True)
    subprocess.run(['git', 'add', '--', *PATHS], check=True)

assert git('diff', '--cached', '--name-only').splitlines() == PATHS
assert git('write-tree') == TREE, 'Candidate tree differs from the local reviewed tree'
if '--publish' in sys.argv:
    entries = []
    for path in PATHS:
        data = (ROOT / path).read_bytes()
        expected = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        actual = api('blobs', {'content': base64.b64encode(data).decode(), 'encoding': 'base64'})['sha']
        assert actual == expected, path
        entries.append({'path': path, 'sha': actual, 'mode': '100644', 'type': 'blob'})
    actual_tree = api('trees', {'base_tree': BASE_TREE, 'tree': entries})['sha']
    assert actual_tree == TREE
    receipt = {'base_commit': BASE, 'candidate_tree': actual_tree, 'paths': PATHS,
               'scope': 'Git objects only; no branch, main, or PR reference changed',
               'qualification': 'focused checks only; full candidate CI and review still required'}
    (TEMP / 'prepared-brief-error.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
else:
    print('REPRODUCED_CANDIDATE_TREE=' + TREE)
