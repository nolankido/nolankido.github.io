"""Reject stale generated Poker HTML without deleting or rewriting any file.

These tests exercise the real build entry point and filesystem traversal with a
small injected output map. Browser behavior and live pages are unchanged.
"""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from test_site import build


class PokerReleaseSafetyTests(unittest.TestCase):
    def run_build(self, root, outputs, check=False):
        out, err = StringIO(), StringIO()
        args = ['build.py', '--check'] if check else ['build.py']
        with patch.object(build, 'ROOT', root), \
                patch.object(build, 'build_outputs', return_value=outputs), \
                patch('sys.argv', args), redirect_stdout(out), redirect_stderr(err):
            code = build.main()
        return code, out.getvalue(), err.getvalue()

    def put(self, root, name, content):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def test_removed_study_guide_is_rejected_in_check_and_build_modes(self):
        for check in [True, False]:
            with self.subTest(check=check), TemporaryDirectory() as temp:
                root = Path(temp)
                stale = self.put(root, 'poker/retired-guide/index.html', build.MARKER + '\nOld study guide')
                before = stale.read_bytes()
                code, _, err = self.run_build(root, {}, check)
                self.assertEqual(code, 1)
                self.assertIn('Orphaned poker page: poker/retired-guide/index.html', err)
                self.assertEqual(stale.read_bytes(), before)

    def test_removed_hubs_nested_guides_and_legacy_families_are_rejected(self):
        for name in ['poker/index.html', 'poker/old-library/index.html',
                     'poker/labs/retired/example/index.html', 'poker/legacy.html',
                     'poker/episodes/retired/index.html', 'poker/hands/retired/index.html',
                     'poker/stories/retired/index.html']:
            with self.subTest(path=name), TemporaryDirectory() as temp:
                root = Path(temp)
                self.put(root, name, build.MARKER)
                code, _, err = self.run_build(root, {}, check=True)
                self.assertEqual(code, 1)
                self.assertIn(name, err)

    def test_valid_current_generated_outputs_are_accepted(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            outputs = {Path(name): build.MARKER + '\nCurrent page'
                       for name in ['index.html', 'poker/index.html', 'poker/study/index.html',
                                    'poker/labs/current/index.html']}
            for name, value in outputs.items():
                self.put(root, name, value)
            for check in [True, False]:
                with self.subTest(check=check):
                    code, out, err = self.run_build(root, outputs, check)
                    self.assertEqual(code, 0, err)
                    self.assertIn('0 changes.', out)

    def test_orphan_refusal_happens_before_any_other_output_is_rebuilt(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            changed = self.put(root, 'poker/study/index.html', build.MARKER + '\nOld content')
            stale = self.put(root, 'poker/retired-guide/index.html', build.MARKER + '\nRetired')
            before = {p: p.read_bytes() for p in [changed, stale]}
            outputs = {Path('poker/study/index.html'): build.MARKER + '\nChanged content',
                       Path('poker/new-guide/index.html'): build.MARKER + '\nNew guide'}
            code, _, err = self.run_build(root, outputs)
            self.assertEqual(code, 1)
            self.assertIn('Review and remove', err)
            self.assertEqual(before, {p: p.read_bytes() for p in before})
            self.assertFalse((root / 'poker/new-guide/index.html').exists())

    def test_manual_html_non_html_assets_and_other_sections_are_untouched(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            files = [self.put(root, 'poker/manual/index.html', '<h1>Manually maintained</h1>'),
                     self.put(root, 'poker/reference.txt', build.MARKER),
                     self.put(root, 'technology/legacy/index.html', build.MARKER)]
            before = {p: p.read_bytes() for p in files}
            for check in [True, False]:
                code, _, err = self.run_build(root, {}, check)
                self.assertEqual(code, 0, err)
                self.assertEqual(before, {p: p.read_bytes() for p in files})

    def test_no_poker_directory_remains_a_valid_small_build(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            code, _, err = self.run_build(root, {Path('index.html'): 'Homepage'})
            self.assertEqual(code, 0, err)
            self.assertEqual((root / 'index.html').read_text(), 'Homepage')

    def test_multiple_stale_pages_report_the_first_sorted_path(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            self.put(root, 'poker/z-old/index.html', build.MARKER)
            self.put(root, 'poker/a-old/index.html', build.MARKER)
            code, _, err = self.run_build(root, {}, check=True)
            self.assertEqual(code, 1)
            self.assertIn('poker/a-old/index.html', err)
            self.assertNotIn('poker/z-old/index.html', err)


if __name__ == '__main__':
    unittest.main(verbosity=2)
