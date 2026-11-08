"""The completed review record preserves an exact published predecessor."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
import answer_record_history as history
from reviewed_release import read as reviewed_bytes


# Pin the complete published answer-record release, rather than attempting to
# reverse every subsequent public-site update from today's working files.
ANSWER_RECORD_RELEASE = '74e064631e59e7659826144390dc77d49d2022ed'
LATER_PUBLICATION = '116359834b8b48dbd1526c68392d89f9dd7bf1a0'
RELEASE_BLOBS = {
    '_source/pages.json': '9d5e51de1b3e49857bb72d055180fef064e25433',
    '_source/technology/check-ai-answers.html': '9b9471d06d87599f88c34e87aadcc4762fd75b5d',
    'downloads/ai-answer-review.txt': '81a23a26adf3496db9d2d1ba389a1fac707d1e5c',
    'downloads/practical-ai-workbook.txt': '321871d4c24d53777803d86488d190b4b13e07ff',
    'technology/check-ai-answers/index.html': '4f0952f6bf83e0930741235d26fd6eaa4313bca0',
    'technology/index.html': '2955785119fb2ce9d662df747f339e2c60e8ce3f',
    'sitemap.xml': 'ee398d46d96cb8910ee32f91e91ec7fb70c04cef',
}

# Captured separately from `git show b8b4bcd:<path>`, not calculated from the
# reverse-span adapter, so the historical parent has an independent oracle.
PUBLISHED_PARENT_HASHES = {
    '_source/pages.json': '5c8a15936605397bc09a1646c0f860337cc70b62fa55f52cc87101d2e4853c3f',
    '_source/technology/check-ai-answers.html': '033d62ed9d181db6d9a3e8017b582e7c2092792c6c07777d8ebc2e5a83242327',
    'downloads/ai-answer-review.txt': '1f7536ae05f048840810982268585f77fd30f8e447ae4d466b392de989c91dcd',
    'downloads/practical-ai-workbook.txt': 'c793d8d20e0006f522d081d34b901cc97d5bb741c2dd4861e2eceb20b8966e23',
    'technology/check-ai-answers/index.html': '0f77f99ddbd3f43276774052031ff06be662479cda793990d74106ff6902b71b',
    'technology/index.html': 'abc89ca6bfaa2e581bdfe807b2e03559843c9f7837a4eca07b214ce80393d986',
    'sitemap.xml': '1a8d6d06e4fa3f16f90c9b1083eee5cc131285ff28d86be7311cdaa82941476f',
}


class AnswerRecordHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = deepcopy(history.change())
        cls.raw = {name: reviewed_bytes(ANSWER_RECORD_RELEASE, name, RELEASE_BLOBS[name])
                   for name in history.PATHS}
        cls.pages = json.loads(cls.raw['_source/pages.json'])

    def test_seven_current_files_are_bound_to_the_actual_published_parent(self):
        self.assertEqual(set(self.record['paths']), {
            '_source/pages.json', '_source/technology/check-ai-answers.html',
            'downloads/ai-answer-review.txt', 'downloads/practical-ai-workbook.txt',
            'technology/check-ai-answers/index.html', 'technology/index.html',
            'sitemap.xml',
        })
        self.assertEqual(self.record['parent_commit'], 'b8b4bcd45d66178a8aa5868889781ef3311f0a3b')
        self.assertEqual(self.record['parent_tree'], '80a4a92d914cee30d84e8e807f3b4f847fb66ec6')
        for name, item in self.record['paths'].items():
            with self.subTest(path=name):
                self.assertEqual(set(item), {'current_sha256', 'parent_sha256', 'edits'})
                self.assertEqual(history.digest(self.raw[name]), item['current_sha256'])
                self.assertEqual(item['parent_sha256'], PUBLISHED_PARENT_HASHES[name])
                self.assertNotEqual(item['current_sha256'], PUBLISHED_PARENT_HASHES[name])

    def test_original_git_parent_matches_all_seven_restored_predecessors(self):
        parent = self.record['parent_commit']
        self.assertEqual(subprocess.check_output(
            ['git', 'rev-parse', ANSWER_RECORD_RELEASE + '^'], cwd=ROOT).decode().strip(), parent)
        self.assertEqual(subprocess.check_output(
            ['git', 'rev-parse', parent + '^{tree}'], cwd=ROOT).decode().strip(),
            self.record['parent_tree'])
        for name in sorted(history.PATHS):
            with self.subTest(path=name):
                original = subprocess.check_output(['git', 'show', parent + ':' + name], cwd=ROOT)
                self.assertEqual(sha256(original).hexdigest(), PUBLISHED_PARENT_HASHES[name])
                self.assertEqual(history.before(name, self.raw[name]), original)

    def test_next_published_release_composes_only_through_its_reviewed_predecessor(self):
        import first_tournament_plan_history
        for name in ('_source/pages.json', '_source/technology/check-ai-answers.html',
                     'technology/check-ai-answers/index.html', 'technology/index.html', 'sitemap.xml'):
            with self.subTest(path=name):
                later = subprocess.check_output(
                    ['git', 'show', LATER_PUBLICATION + ':' + name], cwd=ROOT)
                self.assertNotEqual(sha256(later).hexdigest(),
                                    self.record['paths'][name]['current_sha256'])
                self.assertEqual(first_tournament_plan_history.before(name, later),
                                 self.raw[name])
                self.assertEqual(history.before(name, later),
                                 history.before(name, self.raw[name]))

    def test_exact_reversal_preserves_types_paths_and_idempotence(self):
        for name, item in self.record['paths'].items():
            raw = self.raw[name]
            old = history.before(name, raw)
            with self.subTest(path=name):
                self.assertIsInstance(old, bytes)
                self.assertEqual(history.digest(old), item['parent_sha256'])
                for path in (name, Path(name), ROOT / name):
                    self.assertEqual(history.before(path, raw), old)
                    text = history.before(path, raw.decode('utf-8'))
                    self.assertIsInstance(text, str)
                    self.assertEqual(text.encode('utf-8'), old)
                    self.assertEqual(history.before(path, old), old)
                    self.assertEqual(history.before(path, text), text)

    def test_unknown_bytes_and_unrelated_paths_never_activate_a_reversal(self):
        for name, raw in self.raw.items():
            midpoint = len(raw) // 2
            for altered in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw, raw[1:],
                            raw[:midpoint] + b'UNREVIEWED' + raw[midpoint:], b'\xff\x00'):
                with self.subTest(path=name, mutation=history.digest(altered)):
                    self.assertEqual(history.before(name, altered), altered)
            text = raw.decode() + 'UNREVIEWED'
            self.assertEqual(history.before(name, text), text)
        raw = self.raw['downloads/ai-answer-review.txt']
        for name in ('downloads/unreviewed.txt', ROOT.parent / 'other/downloads/ai-answer-review.txt'):
            self.assertEqual(history.before(name, raw), raw)

    def test_successor_hash_is_checked_before_corrupt_edits(self):
        name = '_source/pages.json'
        bad = deepcopy(self.record)
        bad['paths'][name].update(current_sha256='0' * 64, edits=None)
        with patch.object(history, 'change', return_value=bad):
            self.assertEqual(history.before(name, self.raw[name]), self.raw[name])
        bad['paths'][name]['current_sha256'] = self.record['paths'][name]['current_sha256']
        changed = self.raw[name] + b'UNREVIEWED'
        with patch.object(history, 'change', return_value=bad):
            self.assertEqual(history.before(name, changed), changed)

    def test_invalid_or_incomplete_reverse_edits_fail_closed(self):
        name = '_source/technology/check-ai-answers.html'
        original = self.record['paths'][name]['edits']
        self.assertGreaterEqual(len(original), 2)
        cases = [[], None, original[1:], [original[0], *original], list(reversed(original))]
        for field, value in (('start', -1), ('start', True),
                             ('end', len(self.raw[name].decode()) + 1),
                             ('end', '1'), ('old', None),
                             ('current_sha256', '0' * 64), ('extra', True)):
            changed = deepcopy(original)
            changed[0][field] = value
            cases.append(changed)
        missing = deepcopy(original)
        del missing[0]['old']
        cases.extend((missing, [None]))
        for index, edits in enumerate(cases):
            bad = deepcopy(self.record)
            bad['paths'][name]['edits'] = edits
            with self.subTest(case=index), patch.object(history, 'change', return_value=bad):
                with self.assertRaises(ValueError):
                    history.before(name, self.raw[name])
        for field in ('parent_sha256', 'old'):
            bad = deepcopy(self.record)
            if field == 'old':
                bad['paths'][name]['edits'][0]['old'] += 'UNREVIEWED'
            else:
                bad['paths'][name][field] = '0' * 64
            with patch.object(history, 'change', return_value=bad):
                with self.assertRaisesRegex(ValueError, 'predecessor digest'):
                    history.before(name, self.raw[name])

    def test_parent_scope_and_metadata_corruption_are_rejected(self):
        cases = []
        for field, value in (('version', True), ('parent_commit', '0' * 40),
                             ('parent_tree', '0' * 40), ('paths', None), ('page', None)):
            bad = deepcopy(self.record)
            bad[field] = value
            cases.append(bad)
        for remove in (True, False):
            bad = deepcopy(self.record)
            if remove:
                del bad['paths']['sitemap.xml']
            else:
                bad['paths']['unreviewed.js'] = bad['paths']['sitemap.xml']
            cases.append(bad)
        for side, field in (('new', 'description'), ('new', 'revision'), ('old', 'revision')):
            bad = deepcopy(self.record)
            bad['page'][side][field] = 'UNREVIEWED'
            cases.append(bad)
        for index, bad in enumerate(cases):
            history.change.cache_clear()
            try:
                with self.subTest(case=index), patch.object(history, 'CHANGE') as location:
                    location.read_text.return_value = json.dumps(bad)
                    with self.assertRaises(ValueError):
                        history.change()
            finally:
                history.change.cache_clear()

    def test_complete_metadata_matches_file_public_view_and_reconstructed_parent(self):
        pair = self.record['page']
        raw_pages = json.loads(self.raw['_source/pages.json'])
        previous = json.loads(history.before('_source/pages.json', self.raw['_source/pages.json']))
        for pages in (raw_pages, self.pages):
            current = next(p for p in pages if p['id'] == 'ai-answer-review')
            self.assertEqual(current, pair['new'])
            restored = history.pages(pages)
            for new, old in zip(pages, restored):
                self.assertEqual(old, pair['old'] if new['id'] == 'ai-answer-review' else new)
        self.assertEqual(next(p for p in previous if p['id'] == 'ai-answer-review'), pair['old'])
        self.assertEqual(pair['old']['date'], '2026-10-12')
        self.assertEqual(pair['new']['date'], '2026-10-12')

    def test_partial_or_changed_metadata_stays_visible_and_inputs_are_copied(self):
        current = self.record['page']['new']
        for field in current:
            missing = deepcopy(current)
            del missing[field]
            for altered in ({**current, field: 'UNREVIEWED'}, missing):
                self.assertEqual(history.pages([altered]), [altered])
        for altered in ({**current, 'noindex': True}, {**current, 'extra_claim': 'UNREVIEWED'}):
            self.assertEqual(history.pages([altered]), [altered])
        saved = deepcopy(self.pages)
        old = history.pages(self.pages)
        self.assertEqual(history.pages(old), old)
        old[0]['title'] = 'Changed only in the returned view'
        self.assertEqual(self.pages, saved)

    def test_new_leaf_composes_through_the_oldest_chain_without_hiding_mutations(self):
        import beginner_history
        import workflow_decision_history
        for name, raw in self.raw.items():
            parent = history.before(name, raw)
            with self.subTest(path=name):
                self.assertEqual(beginner_history.before(name, raw),
                                 beginner_history.before(name, parent))
                for altered in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw):
                    self.assertEqual(beginner_history.before(name, altered), altered)
        self.assertEqual(workflow_decision_history.pages(self.pages),
                         workflow_decision_history.pages(history.pages(self.pages)))
        self.assertEqual(beginner_history.pages(self.pages),
                         beginner_history.pages(history.pages(self.pages)))


if __name__ == '__main__':
    unittest.main()
