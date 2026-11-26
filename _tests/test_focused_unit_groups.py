"""Exercise actual subprocess results through the default local release check."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '_scripts'))
import local_release_checks as release
import check_historical_batches as batches

PASS = 'import unittest\nclass T(unittest.TestCase):\n def test_pass(self): pass\n'
SKIP = ('import unittest\nclass T(unittest.TestCase):\n'
        ' @unittest.skip("fixture")\n def test_skip(self): self.fail()\n')


class FocusedUnitGroupsTests(unittest.TestCase):
    def run_group(self, sources, pattern='test_*.py', args=None):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root / '_tests'
            folder.mkdir()
            for name, source in sources.items():
                (folder / name).write_text(source, encoding='utf-8')
            output = StringIO()
            command = args if args is not None else ['-m', 'unittest', 'discover', '-s', '_tests', '-p', pattern, '-q']
            with patch.object(release, 'ROOT', root), redirect_stdout(output):
                passed = release.check('Fixture group', command)
            return passed, output.getvalue()

    def test_actual_pass(self):
        passed, output = self.run_group({'test_one.py': PASS})
        self.assertTrue(passed)
        self.assertIn('1 passed, 0 skipped', output)

    def test_all_skipped_cannot_pass(self):
        passed, output = self.run_group({'test_one.py': SKIP})
        self.assertFalse(passed)
        self.assertIn('INCOMPLETE (0 passed, 1 skipped', output)

    def test_wildcard_group_checks_each_module_even_after_failure(self):
        passed, output = self.run_group({'test_a.py': SKIP, 'test_b.py': PASS})
        self.assertFalse(passed)
        self.assertIn('test_a.py: INCOMPLETE', output)
        self.assertIn('test_b.py: PASS', output)
        self.assertLess(output.index('test_a.py:'), output.index('test_b.py:'))

    def test_partial_skip_with_actual_pass_is_reported(self):
        mixed = PASS + 'class S(unittest.TestCase):\n @unittest.skip("fixture")\n def test_skip(self): self.fail()\n'
        passed, output = self.run_group({'test_mixed.py': mixed})
        self.assertTrue(passed)
        self.assertIn('1 passed, 1 skipped', output)

    def test_zero_tests_and_missing_receipts_cannot_pass(self):
        for source in ('# no tests\n', 'import os\nos._exit(0)\n'):
            with self.subTest(source=source):
                passed, output = self.run_group({'test_empty.py': source})
                self.assertFalse(passed)
                self.assertIn('ERROR', output)

    def test_no_matching_module_never_launches_subprocess(self):
        with patch.object(batches.subprocess, 'run') as run:
            passed, output = self.run_group({'test_other.py': PASS}, 'test_missing.py')
        self.assertFalse(passed)
        self.assertIn('no tests match', output)
        run.assert_not_called()

    def test_import_failure_is_reported(self):
        passed, output = self.run_group({'test_broken.py': 'raise RuntimeError("fixture import failure")\n'})
        self.assertFalse(passed)
        self.assertIn('fixture import failure', output)

    def test_invalid_discovery_command_fails_closed(self):
        with patch.object(batches.subprocess, 'run') as run:
            passed, output = self.run_group({}, args=['-m', 'unittest', 'discover', '-s', 'other', '-p', 'test_*.py', '-q'])
        self.assertFalse(passed)
        self.assertIn('unsupported unittest discovery command', output)
        run.assert_not_called()

    def test_per_module_timeout_is_bounded(self):
        with patch.object(batches.subprocess, 'run', side_effect=subprocess.TimeoutExpired('fixture', 90)) as run:
            passed, output = self.run_group({'test_timeout.py': PASS})
        self.assertFalse(passed)
        self.assertIn('TIMEOUT', output)
        self.assertEqual(run.call_args.kwargs['timeout'], 90)

    def test_non_unittest_command_still_uses_direct_exit_status(self):
        for code in (0, 1):
            with self.subTest(code=code), patch.object(release.subprocess, 'run', return_value=subprocess.CompletedProcess([], code)) as run, redirect_stdout(StringIO()):
                self.assertEqual(release.check('Other gate', ['_scripts/build.py', '--check']), code == 0)
                self.assertEqual(run.call_args.args[0], [sys.executable, '_scripts/build.py', '--check'])


if __name__ == '__main__':
    unittest.main()
