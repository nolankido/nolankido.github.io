"""Current contextual journeys and exact preservation of published PR150."""
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
from urllib.parse import urlsplit
import zlib

import html5lib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
import build
import living_well
import living_well_case_links_history as history
import productivity_history
import visibility_sprint_history

LINKS = {
    'scattered-notes-to-next-step': ['/technology/organize-public-notes/#notes-check'],
    'rough-idea-to-small-creation': ['/technology/ai-book-continuity-checker/#continuity-results'],
    'did-the-tool-actually-help': ['/technology/local-ai-test-record/#local-record-time'],
    'ai-and-personal-productivity': [
        '/technology/local-ai-review-replies/#reply-boundary',
        '/technology/dinner-on-time/#dinner-demo',
        '/technology/ai-weekly-reset/#notes-case-result',
    ],
}
SUBSECTIONS = {
    'use-messages': LINKS['ai-and-personal-productivity'][0],
    'use-meals': LINKS['ai-and-personal-productivity'][1],
    'use-week': LINKS['ai-and-personal-productivity'][2],
}
CONTEXT = {
    LINKS['scattered-notes-to-next-step'][0]: ['recorded example', 'unchanged output', 'AI-assisted source check'],
    LINKS['rough-idea-to-small-creation'][0]: ['findings and mistakes', 'incorrect flags', 'missed issues'],
    LINKS['did-the-tool-actually-help'][0]: ['omits preparation', 'active review', 'manual baseline', 'cannot establish time saved'],
    LINKS['ai-and-personal-productivity'][0]: ['owner approval', 'manual posting', 'historical model examples'],
    LINKS['ai-and-personal-productivity'][1]: ['deterministic', 'simulation', 'does not document a completed meal or measured household benefit'],
    LINKS['ai-and-personal-productivity'][2]: ['recorded editing task', 'not a personal planning trial'],
}
VISIBILITY_CAPSULE_SHA256 = '0b2018bdcf934a2dc6e2b843cb47dd9f28a7f7c754ff26a7209f269b4ec93525'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


class LivingWellCaseLinksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = deepcopy(history.change())
        cls.outputs = build.build_outputs()
        cls.pages = build.public_pages()
        cls.entries = living_well.load(ROOT)
        cls.by_slug = {e['slug']: e for e in cls.entries}
        cls.parent_sources = {name: json.loads(git('show', history.PARENT + ':' + name))
                              for name in history.SOURCES}

    def test_six_contextual_links_reach_real_sections_in_the_current_static_articles(self):
        actual = []
        for slug, destinations in LINKS.items():
            html = self.outputs[Path('living-well') / slug / 'index.html']
            document = html5lib.parse(html, namespaceHTMLElements=False)
            article = next(document.iter('article'))
            links = [a for a in article.iter('a') if a.get('href') in destinations]
            self.assertEqual([a.get('href') for a in links], destinations, slug)
            for link in links:
                href = link.get('href')
                self.assertTrue(''.join(link.itertext()).strip(), href)
                self.assertNotIn('onclick', link.attrib)
                route = urlsplit(href)
                target = html5lib.parse(self.outputs[build.output_path(route.path)], namespaceHTMLElements=False)
                self.assertEqual(sum(e.get('id') == route.fragment for e in target.iter()), 1, href)
                actual.append(href)
        self.assertEqual(len(actual), 6)
        essay = self.by_slug['ai-and-personal-productivity']
        subsections = {sub['id']: sub for section in essay['sections'] for sub in section.get('subsections', [])}
        for ident, href in SUBSECTIONS.items():
            self.assertIn('href="' + href + '"', ' '.join(subsections[ident]['paragraphs']))

    def test_only_six_paragraphs_and_honest_revision_records_are_added(self):
        previous = {e['slug']: e for source in self.parent_sources.values() for e in source['entries']}
        added = []

        def paragraphs(old, new):
            remaining = list(old)
            for paragraph in new:
                if remaining and paragraph == remaining[0]:
                    remaining.pop(0)
                else:
                    added.append(paragraph)
            self.assertEqual(remaining, [], 'Original paragraphs must survive in their original order')

        for pair in self.record['entries']:
            old, new = pair['old'], pair['new']
            slug = new['slug']
            self.assertEqual(old, previous[slug])
            self.assertEqual(new, self.by_slug[slug])
            self.assertEqual({k: v for k, v in old.items() if k not in {'sections', 'updated', 'revision'}},
                             {k: v for k, v in new.items() if k not in {'sections', 'updated', 'revision'}})
            self.assertEqual(len(old['sections']), len(new['sections']))
            for left, right in zip(old['sections'], new['sections']):
                self.assertEqual({k: v for k, v in left.items() if k not in {'paragraphs', 'subsections'}},
                                 {k: v for k, v in right.items() if k not in {'paragraphs', 'subsections'}})
                paragraphs(left['paragraphs'], right['paragraphs'])
                self.assertEqual(len(left.get('subsections', [])), len(right.get('subsections', [])))
                for before, after in zip(left.get('subsections', []), right.get('subsections', [])):
                    self.assertEqual({k: v for k, v in before.items() if k != 'paragraphs'},
                                     {k: v for k, v in after.items() if k != 'paragraphs'})
                    paragraphs(before['paragraphs'], after['paragraphs'])
            self.assertEqual(new['updated'], '2026-10-28')
            html = self.outputs[Path('living-well') / slug / 'index.html']
            self.assertIn(escape(new['revision']), html)
            schema = json.loads(next(e.text for e in html5lib.parse(html, namespaceHTMLElements=False).iter('script')
                                     if e.get('type') == 'application/ld+json'))
            self.assertEqual(schema['datePublished'], new['published'])
            self.assertEqual(schema['dateModified'], '2026-10-28')
        self.assertEqual(len(added), 6)
        self.assertEqual(sum(paragraph.count('<a ') for paragraph in added), 6)
        for paragraph in added:
            self.assertNotIn(chr(8212), paragraph)
        for href, phrases in CONTEXT.items():
            matches = [paragraph for paragraph in added if 'href="' + href + '"' in paragraph]
            self.assertEqual(len(matches), 1, href)
            for phrase in phrases:
                self.assertIn(phrase, matches[0], href)

    def test_capsule_matches_the_actual_published_parent_and_complete_output_inventory(self):
        self.assertEqual(git('rev-parse', history.PARENT + '^{tree}').decode().strip(), history.PARENT_TREE)
        self.assertEqual(len(self.record['parent_outputs']), 229)
        restored = history.outputs(self.outputs)
        self.assertEqual({str(path): history.digest(value) for path, value in restored.items()},
                         self.record['parent_outputs'])
        self.assertEqual(history.outputs(restored), restored)
        for name, item in self.record['paths'].items():
            original = git('show', history.PARENT + ':' + name)
            current = (ROOT / name).read_bytes()
            with self.subTest(path=name):
                self.assertEqual(history.digest(current), item['current_sha256'])
                self.assertEqual(history.digest(original), item['parent_sha256'])
                for path in [name, Path(name), ROOT / name]:
                    self.assertEqual(history.before(path, current), original)
                    self.assertEqual(history.before(path, current.decode()), original.decode())
                    self.assertEqual(history.before(path, original), original)

    def test_exact_record_views_preserve_duplicates_unknown_fields_and_json_types(self):
        for field, restore in [('pages', history.pages), ('entries', history.entries)]:
            current = self.pages if field == 'pages' else self.entries
            by_identity = {r['id' if field == 'pages' else 'slug']: r for r in current}
            for pair in self.record[field]:
                new, old = pair['new'], pair['old']
                identity = 'id' if field == 'pages' else 'slug'
                self.assertEqual(new, by_identity[new[identity]])
                self.assertEqual(restore([new, new]), [old, old])
                self.assertEqual(restore([old]), [old])
                for key in new:
                    mutated = {**new, key: 'UNREVIEWED'}
                    if history.signature(mutated) != history.signature(new):
                        self.assertEqual(restore([mutated]), [mutated])
                for value in [None, True, 1, 1.0]:
                    mutated = {**new, 'unexpected': value}
                    self.assertEqual(restore([mutated]), [mutated])
                unchanged = deepcopy(new)
                restore([new])[0]['unknown'] = 'changed'
                self.assertEqual(new, unchanged)
        self.assertNotEqual(history.signature({'x': True}), history.signature({'x': 1}))
        self.assertNotEqual(history.signature({'x': 1}), history.signature({'x': 1.0}))

    def test_capsule_schema_rejects_unsupported_null_fields(self):
        for field in ['pages', 'entries']:
            record = deepcopy(self.record)
            record[field][0]['new']['unexpected'] = None
            raw = json.dumps(record).encode()
            history.change.cache_clear()
            try:
                with patch.object(history, 'CAPSULE_SHA256', history.digest(raw)), \
                        patch.object(history, 'CHANGE') as location:
                    location.read_bytes.return_value = raw
                    with self.assertRaisesRegex(ValueError, 'record identity'):
                        history.change()
            finally:
                history.change.cache_clear()

    def test_unreviewed_bytes_and_paths_stay_visible_through_both_releases(self):
        for name in self.record['paths']:
            current = (ROOT / name).read_bytes()
            for altered in [current + b'UNREVIEWED', b'UNREVIEWED' + current, current[1:], b'\xff\x00']:
                self.assertIs(history.before(name, altered), altered)
                self.assertIs(visibility_sprint_history.before(name, altered), altered)
            self.assertIs(history.before('unreviewed/' + name, current), current)
            self.assertIs(history.before(ROOT.parent / 'other' / name, current), current)
        name = '_source/living-well/productivity.json'
        self.assertEqual(productivity_history.files([name]), [])
        output = Path('living-well/ai-and-personal-productivity/index.html')
        self.assertEqual(productivity_history.outputs({output: self.outputs[output]}), {})
        altered_output = {output: self.outputs[output] + 'UNREVIEWED'}
        self.assertEqual(productivity_history.outputs(altered_output), altered_output)
        raw = (ROOT / name).read_bytes()
        with patch.object(Path, 'read_bytes', return_value=raw + b'UNREVIEWED'):
            self.assertEqual(productivity_history.files([name]), [name])

    def test_corrupt_capsules_and_predecessor_payloads_fail_closed(self):
        with TemporaryDirectory() as directory:
            changed = Path(directory) / 'changed.json'
            changed.write_bytes(history.CHANGE.read_bytes() + b' ')
            history.change.cache_clear()
            with patch.object(history, 'CHANGE', changed):
                with self.assertRaisesRegex(ValueError, 'capsule digest'):
                    history.change()
            history.change.cache_clear()
        name = next(iter(self.record['paths']))
        current = (ROOT / name).read_bytes()
        for field, value in [('parent_sha256', '0' * 64), ('parent_size', -1),
                             ('parent_zlib_base64', 'invalid base64!'),
                             ('parent_zlib_base64', base64.b64encode(zlib.compress(b'wrong')).decode())]:
            bad = deepcopy(self.record)
            bad['paths'][name][field] = value
            with self.subTest(field=field), patch.object(history, 'change', return_value=bad):
                with self.assertRaises(ValueError):
                    history.before(name, current)
        bad['paths'][name]['current_sha256'] = '0' * 64
        with patch.object(history, 'change', return_value=bad):
            self.assertIs(history.before(name, current), current)

    def test_all_earlier_goldens_and_the_original_visibility_pin_are_unchanged(self):
        names = git('ls-tree', '-r', '--name-only', history.PARENT, '_tests').decode().splitlines()
        goldens = [p for p in names if p.endswith(('-baseline.json', '-change.json'))]
        self.assertGreater(len(goldens), 50)
        for name in goldens:
            self.assertEqual((ROOT / name).read_bytes(), git('show', history.PARENT + ':' + name), name)
        self.assertEqual(history.digest(visibility_sprint_history.CHANGE.read_bytes()), VISIBILITY_CAPSULE_SHA256)
        self.assertEqual(visibility_sprint_history.CAPSULE_SHA256, VISIBILITY_CAPSULE_SHA256)

    def test_new_leaf_is_standard_library_only_and_has_no_runtime_importers(self):
        tree = ast.parse(Path(history.__file__).read_text())
        imports = set()
        for node in ast.walk(tree):
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
                self.assertFalse(any('living_well_case_links_history' in name.split('.') for name in names), str(path))


if __name__ == '__main__':
    unittest.main()
