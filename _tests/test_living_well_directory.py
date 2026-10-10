"""Task directory, historical records, local search and closed validation contracts."""
from copy import deepcopy
from hashlib import sha256
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import living_well as lw
import living_well_directory as directory
import living_well_resources as resources

class DirectoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.extra, cls.library, cls.entries, cls.guides = directory.context(ROOT)
        cls.pages = directory.manifest(ROOT)
        cls.outputs = build.build_outputs()

    def test_scope_and_historical_record_dates(self):
        self.assertEqual(len(self.extra['resources']), 32)
        self.assertEqual(len(self.extra['shelves']), 4)
        self.assertEqual(len(self.extra['tasks']), 9)
        self.assertEqual(len(self.library['resources']), 98)
        self.assertEqual(len(self.library['shelves']), 16)
        self.assertEqual(len(lw.manifest(ROOT)), 75)
        base = json.loads((ROOT / '_source/living-well/resources.json').read_text())
        self.assertEqual(len(base['resources']), 66)
        self.assertEqual(self.library['resources'][:66], base['resources'])
        self.assertEqual(self.library['shelves'][:12], base['shelves'])
        self.assertEqual({e['reviewed_on'] for e in base['resources']}, {'2026-10-09'})
        self.assertEqual({e['reviewed_on'] for e in self.extra['resources']}, {'2026-10-10'})
        self.assertEqual(len(self.guides), 34)

    def test_task_choices_resolve_without_copying_or_ranking_provider_data(self):
        hub = self.outputs[Path('living-well/free-resources/index.html')]
        for task in self.extra['tasks']:
            route = directory.route(task['id'])
            html = self.outputs[build.output_path(route)]
            self.assertIn('href="' + route + '"', hub)
            words = task['purpose'] + task['simplest'] + task['finish'] + ' '.join(c['when'] + c['check'] for c in task['choices']) + ' '.join(s['text'] for s in task['steps'])
            self.assertGreaterEqual(len(words.split()), 190)
            self.assertIn(escape(task['simplest']), html)
            self.assertIn(escape(task['finish']), html)
            for choice in task['choices']:
                entry = self.entries[choice['resource']]
                self.assertIn(escape(choice['when']), html)
                self.assertIn(escape(choice['check']), html)
                self.assertIn(escape(entry['requirements']), html)
                self.assertIn('href="' + escape(entry['entry_url'], quote=True) + '"', html)
                self.assertIn(resources.collection_route(entry['shelf']) + '#' + entry['id'], html)
            self.assertIn('not a ranking from hands-on tests', html)
            for slug in task['guides']:
                self.assertIn('/living-well/' + slug + '/', html)

    def test_new_routes_are_collections_with_sitemap_and_live_checks(self):
        self.assertEqual(len(self.pages), 10)
        for page in self.pages:
            html = self.outputs[build.output_path(page['path'])]
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
            self.assertEqual(schema['@type'], 'CollectionPage')
            self.assertNotIn('datePublished', schema)
            self.assertIn(page['path'], self.outputs[Path('sitemap.xml')])
            self.assertIn(page['path'], check_live.targets())
            self.assertIn('aria-label="Living Well section"', html)
        for name in ('living-well-directory.css', 'living-well-directory.js'):
            self.assertIn('/assets/' + name, check_live.targets())

    def test_finder_contains_exact_static_inventory_and_named_controls(self):
        html = self.outputs[Path('living-well/find/index.html')]
        ids = re.findall(r'id="resource-([a-z0-9-]+)"', html)
        self.assertEqual(set(ids), set(self.entries))
        self.assertEqual(len(ids), 98)
        self.assertEqual(html.count('data-lw-entry '), 98)
        self.assertIn('class="lw-filters" hidden', html)
        self.assertNotRegex(html, r'<(?:form|textarea|iframe)\b')
        for name in ('lw-query', 'lw-collection', 'lw-access'):
            self.assertIn('for="' + name + '"', html)
            self.assertIn('id="' + name + '"', html)
        self.assertIn('maxlength="120"', html)
        self.assertIn('type="button" id="lw-clear"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertNotIn('name="lw-query"', html)

    def test_script_and_styles_are_precisely_page_scoped(self):
        for page in lw.manifest(ROOT):
            html = self.outputs[build.output_path(page['path'])]
            self.assertEqual('src="/assets/living-well-directory.js?' in html, page['path'] == directory.FINDER)
            self.assertEqual('href="/assets/living-well-directory.css?' in html, bool(page.get('directory_kind')))
        js = (ROOT / 'assets/living-well-directory.js').read_text()
        for forbidden in ('fetch(', 'XMLHttpRequest', 'sendBeacon', 'localStorage', 'sessionStorage', 'document.cookie', 'history.', 'location.', 'innerHTML', 'eval(', 'window.open', 'console.log'):
            self.assertNotIn(forbidden, js)
        subprocess.run(['node', '--check', 'assets/living-well-directory.js'], cwd=ROOT, check=True, capture_output=True)
        declared = set(re.findall(r'(--[\w-]+)\s*:', '\n'.join((ROOT / p).read_text() for p in ['styles.css', 'assets/site.css', 'assets/hubs.css', 'assets/living-well.css'])))
        used = set(re.findall(r'var\((--[\w-]+)\)', (ROOT / 'assets/living-well-directory.css').read_text()))
        self.assertEqual(used - declared, set())

    def test_plain_text_cannot_create_markup_or_attribute_injection(self):
        library = deepcopy(self.library)
        sample = '<img src=x onerror="bad()"> & "quoted"'
        library['resources'][0]['title'] = sample
        library['resources'][0]['start'] = sample
        html = directory.finder(library, lw.section)
        self.assertNotIn(sample, html)
        self.assertIn(escape(sample, quote=True), html)
        self.assertNotIn('<img src=x', html)
        extra = deepcopy(self.extra)
        extra['tasks'][0]['purpose'] = sample
        extra['tasks'][0]['choices'][0]['when'] = sample
        with patch.object(directory, 'context', return_value=(extra, self.library, self.entries, self.guides)):
            html = directory.render(ROOT, self.pages[1], lw.section)
        self.assertIn(escape(sample), html)
        self.assertNotIn('<img src=x', html)

    def test_bad_schemas_and_missing_task_references_fail_closed(self):
        variants = []
        for field, value in [('version', True), ('version', 2), ('reviewed_on', '2099-01-01'), ('reviewed_on', '2026-1-1'), ('tasks', [])]:
            d = deepcopy(self.extra); d[field] = value; variants.append(d)
        d = deepcopy(self.extra); d['tasks'].append(deepcopy(d['tasks'][0])); variants.append(d)
        d = deepcopy(self.extra); d['tasks'][0]['id'] = '../elsewhere'; variants.append(d)
        d = deepcopy(self.extra); d['tasks'][0]['choices'][1] = deepcopy(d['tasks'][0]['choices'][0]); variants.append(d)
        d = deepcopy(self.extra); d['tasks'][0]['guides'] = ['weekly-reset'] * 2; variants.append(d)
        d = deepcopy(self.extra); d['tasks'][0]['purpose'] = ''; variants.append(d)
        for d in variants:
            with TemporaryDirectory() as temp:
                root = Path(temp); (root / directory.CATALOG).parent.mkdir(parents=True)
                (root / directory.CATALOG).write_text(json.dumps(d))
                with self.assertRaises(ValueError):
                    directory.read(root)
        for field, value in [('resource', 'missing-resource')]:
            d = deepcopy(self.extra); d['tasks'][0]['choices'][0][field] = value
            with patch.object(directory, 'read', return_value=d):
                with self.assertRaises(ValueError):
                    directory.context(ROOT)
        d = deepcopy(self.extra); d['tasks'][0]['guides'][0] = 'notebook-or-ai'
        with patch.object(directory, 'read', return_value=d):
            with self.assertRaises(ValueError):
                directory.context(ROOT)

    def test_task_selection_guidance_retains_nonsoftware_life_context(self):
        tasks = {t['id']: t for t in self.extra['tasks']}
        self.assertTrue({'learn-and-reflect', 'notice-the-world', 'help-and-connect'} <= set(tasks))
        selected = {c['resource'] for t in tasks.values() for c in t['choices']}
        self.assertTrue({'on-being', 'poetry-unbound', 'ucla-mindful', 'merlin', 'storycorps'} <= selected)
        self.assertIn('not a sufficient backup', self.entries['syncthing']['limit'])
        self.assertIn('not encrypted at rest', self.entries['simplenote']['limit'])
        self.assertIn('business use requires', self.entries['freefilesync']['requirements'])
        self.assertIn('Free public documentation', self.entries['duplicati']['requirements'])
        self.assertIn('hosted', self.entries['cryptpad']['requirements'].lower())

    def test_rendering_is_deterministic_and_original_files_stay_fixed(self):
        self.assertEqual(self.outputs, build.build_outputs())
        for relative, digest in {
            '_source/living-well/resources.json': 'bd8be4e301daad1a5b661ce6580b1040dbf75902a0d6ee5c5a5039378522918a',
            'living-well/feed.xml': '94d241e3797f54abf9f5b35e99a1f1f92cd932d2326c7fdc481fb5a2ce86e094',
            '_source/living-well/discovery.json': '562d0b7cee1bc4213f3a44d6c1c5aa944f47e19d97b6b312d9373b41bf04099f',
        }.items():
            self.assertEqual(sha256((ROOT / relative).read_bytes()).hexdigest(), digest, relative)
        self.assertEqual(len(lw.worksheet_exports()), 5)
        for path, text in lw.worksheet_exports().items():
            self.assertEqual((ROOT / path).read_text(), text)

if __name__ == '__main__':
    unittest.main(verbosity=2)
