"""One-use, fail-closed task-search correction for the owner-approved PR 31."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PARENT = '3b8a48a640e34506b846b77f237df903c7849e20'
parent = subprocess.check_output(['git', 'rev-parse', 'HEAD^'], cwd=ROOT, text=True).strip()
if parent != EXPECTED_PARENT:
    raise SystemExit('Refusing to patch an unexpected parent commit')


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    content = target.read_text(encoding='utf-8')
    if content.count(old) != 1:
        raise SystemExit('Expected exactly one source match: ' + path)
    target.write_text(content.replace(old, new, 1), encoding='utf-8')


module = '_scripts/living_well_directory.py'
replace_once(module, 'return finder(library, section)', "return finder(library, section, data['tasks'])")
replace_once(module, 'def finder(library: dict, section) -> str:', '''def task_search_terms(tasks: list[dict]) -> dict[str, str]:
    """Index only the public task associations selected for each resource."""
    terms: dict[str, list[str]] = {}
    for task in tasks:
        shared = [task['id'], task['id'].replace('-', ' '), task['title'], task['description']]
        for choice in task['choices']:
            terms.setdefault(choice['resource'], []).extend([*shared, choice['when'], choice['check']])
    return {key: ' '.join(parts) for key, parts in terms.items()}


def finder(library: dict, section, tasks: list[dict] | None = None) -> str:''')
replace_once(module, "    results = []\n    for e in entries:", "    task_terms = task_search_terms(tasks or [])\n    results = []\n    for e in entries:")
replace_once(module,
    "        terms = ' '.join([e['start'], e['limit'], e['format'], e['creator'], shelves[e['shelf']]['title']])",
    "        parts = [e['start'], e['limit'], e['format'], e['creator'], shelves[e['shelf']]['title']]\n        if e['id'] in task_terms:\n            parts.append(task_terms[e['id']])\n        terms = ' '.join(parts)")

tests = '_tests/test_living_well_directory.py'
replace_once(tests, 'from html import escape', 'from html import escape\nfrom html.parser import HTMLParser')
replace_once(tests, 'class DirectoryTests(unittest.TestCase):', '''class FinderTerms(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.terms = {}
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article' and 'data-lw-entry' in attrs:
            self.terms[attrs['id'].removeprefix('resource-')] = attrs['data-terms']


class DirectoryTests(unittest.TestCase):''')
replace_once(tests, '    def test_script_and_styles_are_precisely_page_scoped(self):', '''    def test_every_task_and_choice_is_in_its_resources_search_metadata(self):
        terms = FinderTerms(self.outputs[Path('living-well/find/index.html')]).terms
        self.assertEqual(set(terms), set(self.entries))
        for task in self.extra['tasks']:
            for choice in task['choices']:
                with self.subTest(task=task['id'], resource=choice['resource']):
                    for value in (task['id'], task['id'].replace('-', ' '), task['title'],
                                  task['description'], choice['when'], choice['check']):
                        self.assertIn(value, terms[choice['resource']])

    def test_task_associations_do_not_leak_into_unrelated_resources(self):
        tasks = deepcopy(self.extra['tasks'])
        for number, task in enumerate(tasks):
            task['title'] = 'unique-task-marker-' + str(number)
        terms = FinderTerms(directory.finder(self.library, lw.section, tasks)).terms
        for task in tasks:
            chosen = {choice['resource'] for choice in task['choices']}
            for key in self.entries:
                self.assertEqual(task['title'] in terms[key], key in chosen, (task['id'], key))
        self.assertEqual(directory.task_search_terms([]), {})

    def test_task_search_metadata_is_escaped_as_literal_text(self):
        tasks = deepcopy(self.extra['tasks'])
        sample = '<img src=x onerror="bad()"> & "quoted"'
        tasks[0]['title'] = sample
        tasks[0]['description'] = sample
        tasks[0]['choices'][0]['when'] = sample
        tasks[0]['choices'][0]['check'] = sample
        html = directory.finder(self.library, lw.section, tasks)
        self.assertNotIn(sample, html)
        self.assertIn(escape(sample, quote=True), html)
        self.assertNotIn('<img src=x', html)
        terms = FinderTerms(html).terms
        self.assertEqual(set(terms), set(self.entries))
        self.assertIn(sample, terms[tasks[0]['choices'][0]['resource']])

    def test_script_and_styles_are_precisely_page_scoped(self):''')

browser = '_tests/living_well_directory_browser.py'
replace_once(browser,
    "        query = page.get_by_label('A topic, task, or resource name')\n        query.fill('ÓBSIDIAN')",
    '''        query = page.get_by_label('A topic, task, or resource name')
        tasks = json.loads((root / '_source/living-well/directory.json').read_text())['tasks']
        for task in tasks:
            for value in (task['id'].replace('-', ' '), task['title']):
                query.fill(value)
                for choice in task['choices']:
                    expect(page.locator('#resource-' + choice['resource'])).to_be_visible()
        query.fill('share and coordinate')
        expect(page.locator('[data-lw-entry]:visible')).to_have_count(5)
        for key in ('google-keep', 'apple-notes-sharing', 'cryptpad', 'localsend', 'living-room-conversations'):
            expect(page.locator('#resource-' + key)).to_be_visible()
        page.get_by_label('Collection', exact=True).select_option('notes-documents')
        page.get_by_label('Entry access').select_option('web')
        expect(page.locator('[data-lw-entry]:visible')).to_have_count(2)
        expect(page.locator('#resource-google-keep')).to_be_visible()
        expect(page.locator('#resource-apple-notes-sharing')).to_be_visible()
        page.get_by_label('Entry access').select_option('account')
        expect(page.locator('[data-lw-entry]:visible')).to_have_count(0)
        expect(page.locator('#lw-empty')).to_be_visible()
        page.get_by_role('button', name='Clear filters').click()
        expect(query).to_be_focused()
        expect(page.locator('[data-lw-entry]:visible')).to_have_count(98)
        query.fill('ÓBSIDIAN')''')
replace_once(browser,
    "            'inventory': 98, 'passed': True, 'literal_query_test': True,",
    "            'inventory': 98, 'passed': True, 'literal_query_test': True,\n            'task_paths_checked': len(tasks), 'task_queries_checked': 2 * len(tasks),\n            'share_and_coordinate_results': 5,")

subprocess.run(['python', '_scripts/build.py'], cwd=ROOT, check=True)
allowed = {module, tests, browser, 'living-well/find/index.html'}
changed = set(subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True).splitlines())
if changed != allowed:
    raise SystemExit('Unexpected changed-file set: ' + repr(changed))
subprocess.run(['python', '_scripts/build.py', '--check'], cwd=ROOT, check=True)
subprocess.run(['python', '-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_*.py', '-v'], cwd=ROOT, check=True)
print('TASK_SEARCH_PATCH_VERIFIED: source, generated finder, and full unit suite')
