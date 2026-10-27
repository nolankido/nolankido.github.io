"""Capsule generation is pinned, repeatable, and rejects unintended scope.

Unit tests use synthetic Git objects so shallow checkouts need no old commits.
Run the freezer's --check separately when the real pinned objects are available.
"""
import base64
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import Mock, patch
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import freeze_scoped_share_change as freezer


class ScopedShareFreezerTests(unittest.TestCase):
    def setUp(self):
        self.html_paths = ['index.html', 'about/index.html'] + [
            f'topic-{number}/index.html' for number in range(82)]
        self.changed = sorted(self.html_paths + list(freezer.AUTHORING_PATHS) + [
            freezer.NEW_ASSET, *freezer.REVIEW_TOOLS, '_tests/review.py'])
        self.parent = {}
        self.release = {}
        for path in self.html_paths:
            src = '/assets/social/nolan-kido-ai.png' if path in {
                'index.html', 'about/index.html'} else '/assets/social/nolan-kido.png'
            self.release[path] = (
                f'<meta property="og:image" content="{src}">\n'
                f'<meta property="og:image:alt" content="{freezer.GENERAL_ALT}">\n'
            ).encode('utf-8')
            self.parent[path] = freezer.reverse_html(path, self.release[path])
        for path in freezer.AUTHORING_PATHS:
            self.parent[path] = ('parent:' + path).encode('utf-8')
            self.release[path] = ('release:' + path).encode('utf-8')
        self.release[freezer.NEW_ASSET] = b'pinned AI share image'

    def git(self, *args):
        if args == ('diff', '--name-only', 'pinned-parent', 'pinned-release'):
            return ('\n'.join(self.changed) + '\n').encode('utf-8')
        if len(args) == 2 and args[0] == 'show':
            revision, path = args[1].split(':', 1)
            sources = {'pinned-parent': self.parent, 'pinned-release': self.release}
            return sources[revision][path]
        raise AssertionError('Unpinned Git read: ' + repr(args))

    def build(self):
        with patch.object(freezer, 'pinned_parent', return_value='pinned-parent'), \
                patch.object(freezer, 'pinned_release', return_value='pinned-release'), \
                patch.object(freezer, 'git', side_effect=self.git), \
                patch.object(Path, 'read_bytes', side_effect=AssertionError('Working-tree read')):
            return freezer.build_record()

    def test_record_is_deterministic_and_reads_only_pinned_git_bytes(self):
        first = self.build()
        self.assertEqual(first, self.build())
        self.assertEqual(first['parent_commit'], freezer.PUBLISHED_PARENT)
        self.assertEqual(first['parent_tree'], freezer.PARENT_TREE)
        self.assertEqual(len(first['paths']), 87)
        self.assertEqual(sum(item['mode'] == 'social-metadata'
                             for item in first['paths'].values()), 84)
        self.assertEqual(first['new_asset'], {
            'path': freezer.NEW_ASSET,
            'sha256': freezer.digest(self.release[freezer.NEW_ASSET]),
        })
        for path, item in first['paths'].items():
            with self.subTest(path=path):
                self.assertEqual(item['current_sha256'], freezer.digest(self.release[path]))
                self.assertEqual(item['parent_sha256'], freezer.digest(self.parent[path]))
                if item['mode'] == 'frozen-predecessor':
                    self.assertEqual(zlib.decompress(base64.b64decode(
                        item['parent_zlib_base64'], validate=True)), self.parent[path])
        self.assertNotIn(freezer.NEW_ASSET, first['paths'])
        self.assertFalse(set(first['paths']) & freezer.REVIEW_TOOLS)

    def test_unknown_production_files_are_rejected_not_frozen(self):
        original = self.changed.copy()
        for path in ['assets/unreviewed.js', '_source/site.json', '_scripts/check_search.py']:
            with self.subTest(path=path):
                self.changed = original + [path]
                with self.assertRaisesRegex(ValueError, 'Unexpected production changes'):
                    self.build()

    def test_scope_requires_all_three_authoring_paths_new_asset_and_84_html_files(self):
        for removed in [freezer.NEW_ASSET, *freezer.AUTHORING_PATHS, 'index.html']:
            with self.subTest(removed=removed):
                with self.assertRaisesRegex(ValueError, 'Unexpected share-card change set'):
                    freezer.production_paths([p for p in self.changed if p != removed])
        for added in ['unexpected/index.html', 'index.html']:
            with self.subTest(added=added):
                with self.assertRaisesRegex(ValueError, 'Unexpected share-card change set'):
                    freezer.production_paths(self.changed + [added])

    def test_html_changes_outside_the_reviewed_transformation_are_rejected(self):
        self.release['index.html'] += b'<p>Unreviewed claim</p>'
        with self.assertRaisesRegex(ValueError, 'Non-reversible scoped share edit: index.html'):
            self.build()

    def test_unchanged_paths_are_rejected(self):
        path = '_source/presentation.json'
        self.release[path] = self.parent[path]
        with self.assertRaisesRegex(ValueError, 'Unchanged file in scope'):
            self.build()

    def test_revision_resolution_requires_an_exact_approved_tree(self):
        failed = SimpleNamespace(returncode=128, stdout='')
        matching = SimpleNamespace(returncode=0, stdout='approved-tree\n')
        with patch.object(freezer.subprocess, 'run', side_effect=[failed, matching]) as run:
            self.assertEqual(freezer.pinned_revision('published', 'equivalent',
                                                     'approved-tree', 'release'), 'equivalent')
            self.assertEqual(run.call_count, 2)
        wrong = SimpleNamespace(returncode=0, stdout='unapproved-tree\n')
        with patch.object(freezer.subprocess, 'run', return_value=wrong):
            with self.assertRaisesRegex(ValueError, 'release tree unavailable or inconsistent'):
                freezer.pinned_revision('published', 'equivalent', 'approved-tree', 'release')

    def test_check_mode_compares_exact_stored_record_without_writing(self):
        stored = freezer.TARGET.read_text(encoding='utf-8')
        record = json.loads(stored)
        self.assertEqual(json.dumps(record, indent=2) + '\n', stored)
        target = Mock()
        target.is_file.return_value = True
        target.read_text.return_value = stored
        with patch.object(freezer, 'build_record', return_value=deepcopy(record)), \
                patch.object(freezer, 'TARGET', target), patch('builtins.print'):
            self.assertEqual(freezer.main(['--check']), 0)
        target.write_text.assert_not_called()

    def test_check_mode_rejects_stale_or_missing_record_without_writing(self):
        record = self.build()
        target = Mock()
        for exists in [True, False]:
            with self.subTest(exists=exists):
                target.is_file.return_value = exists
                target.read_text.return_value = 'stale capsule\n'
                with patch.object(freezer, 'build_record', return_value=record), \
                        patch.object(freezer, 'TARGET', target), patch('builtins.print'):
                    self.assertEqual(freezer.main(['--check']), 1)
                target.write_text.assert_not_called()


if __name__ == '__main__':
    unittest.main()
