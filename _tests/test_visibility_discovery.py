"""Current discovery journeys and exact preservation of published PR151."""
import ast
import base64
from copy import deepcopy
from html import escape
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zlib

import html5lib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
import build
import check_live
import site_find
import visibility_discovery_history as history
import living_well_case_links_history
import visibility_sprint_history

MEMBERSHIPS = {
    '/technology/ai-book-continuity-checker/': ['creative'],
    '/technology/dinner-on-time/': ['living-well'],
    '/technology/ai-weekly-reset/': ['living-well'],
    '/technology/organize-public-notes/': ['living-well'],
    '/living-well/ai-and-personal-productivity/': ['technology'],
}
PROJECTS = [
    '/technology/local-ai-review-replies/',
    '/technology/ai-book-continuity-checker/',
    '/technology/dinner-on-time/',
]
REVISED_IDS = {'home', 'about', 'bio', 'start-here', 'resources', 'technology', 'follow'}
OLD_CAPSULES = {
    '_tests/visibility-sprint-change.json': '0b2018bdcf934a2dc6e2b843cb47dd9f28a7f7c754ff26a7209f269b4ec93525',
    '_tests/living-well-case-links-change.json': 'd370b6a1a3c7d1abfb2f9b991f1cef772ebf05ad9109e9cf7cea2abad98faab8',
}


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def parse(document):
    return html5lib.parse(document, namespaceHTMLElements=False)


class VisibilityDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = deepcopy(history.change())
        cls.outputs = build.build_outputs()
        cls.pages = build.public_pages()
        cls.items = site_find.entries(ROOT, cls.pages)
        cls.parent_paths = set(git('ls-tree', '-r', '--name-only', history.PARENT).decode().splitlines())

    def test_five_relevant_subject_memberships_preserve_each_canonical_result_once(self):
        previous = json.loads(git('show', history.PARENT + ':_source/discovery.json'))
        current = json.loads((ROOT / '_source/discovery.json').read_text())
        self.assertEqual(current['note_interests'], previous['note_interests'])
        self.assertEqual(current['also_in'], {**previous['also_in'], **MEMBERSHIPS})
        self.assertTrue(set(MEMBERSHIPS).isdisjoint(previous['also_in']))
        self.assertEqual(len(self.items), len({item['path'] for item in self.items}))
        rendered = parse(self.outputs[Path('find/index.html')])
        for path, extra in MEMBERSHIPS.items():
            found = [item for item in self.items if item['path'] == path]
            self.assertEqual(len(found), 1, path)
            primary = path.split('/')[1]
            self.assertEqual(found[0]['home'], primary)
            self.assertEqual(found[0]['interests'], [primary, *extra])
            cards = [node for node in rendered.iter('li') if node.get('class') == 'find-item'
                     and any(a.get('href') == path for a in node.findall('./h3/a'))]
            self.assertEqual(len(cards), 1, path)
            self.assertEqual(cards[0].get('data-interests').split(), [primary, *extra])
            for interest in [primary, *extra]:
                self.assertIn(site_find.INTERESTS[interest], ''.join(cards[0].itertext()))

    def test_introduction_pages_have_native_project_routes_and_keep_the_existing_tasks(self):
        for source in ['about', 'bio', 'start-here']:
            document = parse(self.outputs[Path(source) / 'index.html'])
            main = next(document.iter('main'))
            links = [a.get('href') for a in main.iter('a')]
            for path in PROJECTS:
                self.assertIn(path, links, source)
            for element in main.iter():
                self.assertNotIn('onclick', element.attrib)
        for source in ['about', 'start-here']:
            self.assertIn('href="/poker/comics/"', self.outputs[Path(source) / 'index.html'])
        start = parse(self.outputs[Path('start-here/index.html')])
        tasks = next(node for node in start.iter('ul') if node.get('class') == 'task-route-list')
        self.assertEqual([node.find('a').get('href') for node in tasks.findall('li')], [
            '/technology/task-brief/', '/technology/check-ai-answers/',
            '/living-well/weekly-reset/', '/poker/first-live-tournament/',
        ])
        self.assertEqual(sum(node.get('id') == 'start-projects-title' for node in start.iter()), 1)
        self.assertTrue(any(node.get('href') == '#start-projects-title' for node in start.iter('a')))

    def test_resource_records_are_downloadable_and_their_existing_bytes_are_unchanged(self):
        document = parse(self.outputs[Path('resources/index.html')])
        for case, download in [
                ('/technology/organize-public-notes/', 'downloads/public-notes-action-record.txt'),
                ('/technology/local-ai-test-record/', 'downloads/local-ai-test-record.json')]:
            self.assertTrue(any(a.get('href') == case for a in document.iter('a')))
            matches = [a for a in document.iter('a') if a.get('href') == '/' + download]
            self.assertEqual(len(matches), 1)
            self.assertIn('download', matches[0].attrib)
            self.assertEqual((ROOT / download).read_bytes(), git('show', history.PARENT + ':' + download))
        self.assertIn('hosted-runner conditions', ''.join(document.itertext()))

    def test_overview_metadata_revises_seven_existing_pages_without_republishing_articles(self):
        previous = json.loads(git('show', history.PARENT + ':_source/pages.json'))
        current = json.loads((ROOT / '_source/pages.json').read_text())
        self.assertEqual([p['id'] for p in current], [p['id'] for p in previous])
        effective = {page['id']: page for page in self.pages}
        changed = set()
        for old, new in zip(previous, current):
            if old == new:
                continue
            changed.add(new['id'])
            self.assertNotIn('date', new)
            self.assertNotIn('revision', new)
            self.assertEqual(new['updated'], '2026-10-28')
            for field in ['seo_title', 'description']:
                if old[field] != new[field]:
                    self.assertEqual(effective[new['id']][field], new[field], (new['id'], field))
            self.assertEqual({k: v for k, v in old.items() if k not in {'seo_title', 'description', 'updated'}},
                             {k: v for k, v in new.items() if k not in {'seo_title', 'description', 'updated'}})
        self.assertEqual(changed, REVISED_IDS)
        for page in self.pages:
            if page['id'] not in REVISED_IDS:
                continue
            self.assertEqual(page['updated'], '2026-10-28')
            html = self.outputs[build.output_path(page['path'])]
            self.assertIn('<title>' + escape(page['seo_title']) + '</title>', html)
            self.assertIn('<meta name="description" content="' + escape(page['description'], quote=True) + '">', html)
            schema = json.loads(next(e.text for e in parse(html).iter('script')
                                     if e.get('type') == 'application/ld+json'))
            self.assertNotEqual(schema['@type'], 'Article')
            self.assertNotIn('datePublished', schema)
            if page['id'] == 'about':
                self.assertNotIn('dateModified', schema)
            else:
                self.assertEqual(schema['dateModified'], '2026-10-28')
        for name in ['feed.xml', 'writing.xml', 'technology/feed.xml', 'living-well/feed.xml', 'poker/feed.xml']:
            self.assertEqual(self.outputs[Path(name)].encode(), git('show', history.PARENT + ':' + name))
        for name in ['_source/site.json', 'downloads/nolan-kido-short-bio.txt', 'downloads/nolan-kido-long-bio.txt']:
            self.assertEqual((ROOT / name).read_bytes(), git('show', history.PARENT + ':' + name))

    def test_capsule_matches_the_actual_parent_and_complete_render_inventory(self):
        self.assertEqual(git('rev-parse', history.PARENT + '^{tree}').decode().strip(), history.PARENT_TREE)
        self.assertEqual(len(self.record['parent_outputs']), 229)
        restored = history.outputs(self.outputs)
        self.assertEqual({str(p): history.digest(value) for p, value in restored.items()}, self.record['parent_outputs'])
        self.assertEqual(history.outputs(restored), restored)
        for name, item in self.record['paths'].items():
            current = (ROOT / name).read_bytes()
            original = git('show', history.PARENT + ':' + name)
            with self.subTest(path=name):
                self.assertEqual(history.digest(current), item['current_sha256'])
                self.assertEqual(history.digest(original), item['parent_sha256'])
                for path in [name, Path(name), ROOT / name]:
                    self.assertEqual(history.before(path, current), original)
                    self.assertEqual(history.before(path, original), original)
                self.assertEqual(history.before(name, current.decode()), original.decode())

    def test_notification_runs_only_after_exact_live_main_verification(self):
        workflow = (ROOT / '.github/workflows/site-checks.yml').read_text()
        self.assertIn('permissions:\n  contents: read\n', workflow)
        published = workflow.split('  published:\n', 1)[1]
        self.assertIn("if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}", published)
        self.assertIn('persist-credentials: false\n          fetch-depth: 0', published)
        verification, notification = published.split('      - name: Notify IndexNow of verified content changes\n', 1)
        self.assertIn('id: live-release', verification)
        self.assertIn('python _scripts/check_live.py --attempts 10 --interval 10', verification)
        self.assertLess(verification.index('python _scripts/check_live.py'),
                        verification.index('echo "verified-sha=$GITHUB_SHA" >> "$GITHUB_OUTPUT"'))
        self.assertEqual(verification.count('if [ "$current" != "$GITHUB_SHA" ]; then'), 2)
        self.assertIn('if: ${{ steps.live-release.outputs.verified-sha == github.sha }}', notification)
        self.assertIn('continue-on-error: true', notification)
        self.assertIn('INDEXNOW_BASE: ${{ github.event.before }}', notification)
        self.assertIn('INDEXNOW_HEAD: ${{ github.sha }}', notification)
        self.assertIn('python _scripts/submit_indexnow.py --base "$INDEXNOW_BASE" --head "$INDEXNOW_HEAD" --submit', notification)
        self.assertEqual(workflow.count(' --submit'), 1)
        self.assertNotIn('submit_indexnow', workflow.split('  published:\n', 1)[0])
        self.assertNotIn('--baseline', notification)
        self.assertNotIn('sitemap.xml', notification)
        self.assertIn("if: ${{ steps.indexnow.outcome == 'failure' }}", notification)
        self.assertIn('::warning::The website was published and verified, but IndexNow notification did not complete.', notification)
        self.assertIn('name: indexnow-${{ github.sha }}', notification)
        self.assertIn('retention-days: 30', notification)

    def test_exact_additions_are_removed_but_unknown_files_and_responses_remain_visible(self):
        for name, expected in self.record['added_files'].items():
            self.assertNotIn(name, self.parent_paths)
            raw = (ROOT / name).read_bytes()
            self.assertEqual(history.digest(raw), expected)
            self.assertEqual(history.source_records({name: raw}), {})
            for altered in [raw + b'UNREVIEWED', b'UNREVIEWED' + raw, b'\xff\x00']:
                self.assertEqual(history.source_records({name: altered}), {name: altered})
            for paths in [[name, 'unknown.txt'], {name, 'unknown.txt'}, (ROOT / name, ROOT / 'unknown.txt')]:
                restored = history.files(paths)
                self.assertIsInstance(restored, type(paths))
                self.assertEqual([history.key(path) for path in restored], ['unknown.txt'])
            with patch.object(Path, 'read_bytes', return_value=raw + b'UNREVIEWED'):
                self.assertEqual(history.files([name]), [name])
        targets = check_live.targets()
        for route, item in self.record['added_targets'].items():
            response = targets[route]
            self.assertEqual(response[0], item['status'])
            self.assertEqual(history.digest(response[1]), item['sha256'])
            self.assertEqual(history.live_targets({route: response}), {})
            for altered in [(404, response[1]), (200, response[1] + b'UNREVIEWED'),
                            [200, response[1]], (200, ''), (True, response[1])]:
                self.assertEqual(history.live_targets({route: altered}), {route: altered})
        unknown = {'unknown.txt': b'unknown'}
        self.assertEqual(history.source_records(unknown), unknown)
        self.assertEqual(history.outputs(unknown), unknown)

    def test_unknown_byte_and_page_mutations_survive_all_three_release_views(self):
        for name in self.record['paths']:
            current = (ROOT / name).read_bytes()
            for altered in [current + b'UNREVIEWED', b'UNREVIEWED' + current, current[1:], b'\xff\x00']:
                self.assertIs(history.before(name, altered), altered)
                self.assertIs(living_well_case_links_history.before(name, altered), altered)
                self.assertIs(visibility_sprint_history.before(name, altered), altered)
            self.assertIs(history.before('unknown/' + name, current), current)
            self.assertIs(history.before(ROOT.parent / 'other' / name, current), current)
        for pair in self.record['pages']:
            old, new = pair['old'], pair['new']
            self.assertEqual(history.pages([new, new]), [old, old])
            self.assertEqual(history.pages([old]), [old])
            for value in [None, True, 1, 1.0, 'UNREVIEWED']:
                changed = {**new, 'unreviewed': value}
                self.assertEqual(history.pages([changed]), [changed])
            for name in new:
                changed = {**new, name: 'UNREVIEWED'}
                if history.signature(changed) != history.signature(new):
                    self.assertEqual(history.pages([changed]), [changed])
            copied = deepcopy(new)
            history.pages([new])[0]['unreviewed'] = 'new'
            self.assertEqual(new, copied)
        self.assertNotEqual(history.signature({'x': True}), history.signature({'x': 1}))
        self.assertNotEqual(history.signature({'x': 1}), history.signature({'x': 1.0}))
        self.assertNotEqual(history.signature({}), history.signature({'x': None}))

    def test_corrupt_capsules_and_unapproved_schema_fields_fail_closed(self):
        with TemporaryDirectory() as directory:
            changed = Path(directory) / 'changed.json'
            changed.write_bytes(history.CHANGE.read_bytes() + b' ')
            history.change.cache_clear()
            try:
                with patch.object(history, 'CHANGE', changed):
                    with self.assertRaisesRegex(ValueError, 'capsule digest'):
                        history.change()
            finally:
                history.change.cache_clear()
        for field, value in [('version', True), ('parent_commit', '0' * 40)]:
            record = deepcopy(self.record)
            record[field] = value
            self.assert_rejected_record(record)
        record = deepcopy(self.record)
        record['pages'][0]['new']['unreviewed'] = None
        self.assert_rejected_record(record)
        name = next(iter(self.record['paths']))
        current = (ROOT / name).read_bytes()
        for field, value in [('parent_sha256', '0' * 64), ('parent_size', -1),
                             ('parent_zlib_base64', 'not base64!'),
                             ('parent_zlib_base64', base64.b64encode(zlib.compress(b'wrong')).decode())]:
            bad = deepcopy(self.record)
            bad['paths'][name][field] = value
            with self.subTest(field=field), patch.object(history, 'change', return_value=bad):
                with self.assertRaises(ValueError):
                    history.before(name, current)

    def assert_rejected_record(self, record):
        raw = json.dumps(record).encode()
        history.change.cache_clear()
        try:
            with patch.object(history, 'CAPSULE_SHA256', history.digest(raw)), patch.object(history, 'CHANGE') as location:
                location.read_bytes.return_value = raw
                with self.assertRaises(ValueError):
                    history.change()
        finally:
            history.change.cache_clear()

    def test_all_older_capsules_are_unchanged_and_the_new_leaf_has_no_runtime_importers(self):
        goldens = [p for p in self.parent_paths if p.startswith('_tests/')
                   and p.endswith(('-baseline.json', '-change.json'))]
        self.assertGreater(len(goldens), 50)
        for name in goldens:
            self.assertEqual((ROOT / name).read_bytes(), git('show', history.PARENT + ':' + name), name)
        for name, expected in OLD_CAPSULES.items():
            self.assertEqual(history.digest((ROOT / name).read_bytes()), expected)
        imports = set()
        for node in ast.walk(ast.parse(Path(history.__file__).read_text())):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0)
                imports.add(node.module.split('.')[0])
        self.assertFalse(imports - sys.stdlib_module_names)
        for path in (ROOT / '_scripts').rglob('*.py'):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or '', *(alias.name for alias in node.names)]
                else:
                    continue
                self.assertFalse(any('visibility_discovery_history' in name.split('.') for name in names), str(path))


if __name__ == '__main__':
    unittest.main()
