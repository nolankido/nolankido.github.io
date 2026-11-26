"""Real subprocess controls for historical unit test coverage and receipts."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import check_historical_batches as batches


class HistoricalResultContract(unittest.TestCase):
    def run_fixture(self, source):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / '_tests').mkdir()
            (root / '_tests/test_fixture.py').write_text(source, encoding='utf-8')
            with patch.object(batches, 'ROOT', root):
                return batches.run_file('test_fixture.py', 20)

    def test_one_real_pass(self):
        result = self.run_fixture('import unittest\nclass T(unittest.TestCase):\n def test_pass(self): self.assertTrue(True)\n')
        self.assertEqual((result['status'], result['tests'], result['passed'], result['skipped']), ('PASS', 1, 1, 0))

    def test_all_skipped_is_incomplete(self):
        result = self.run_fixture('import unittest\nclass T(unittest.TestCase):\n @unittest.skip("fixture")\n def test_skip(self): self.fail()\n')
        self.assertEqual((result['status'], result['tests'], result['passed'], result['skipped'], result['returncode']), ('INCOMPLETE', 1, 0, 1, 2))

    def test_partial_skip_reports_actual_passes(self):
        result = self.run_fixture('import unittest\nclass T(unittest.TestCase):\n def test_pass(self): pass\n @unittest.skip("fixture")\n def test_skip(self): self.fail()\n')
        self.assertEqual((result['status'], result['tests'], result['passed'], result['skipped']), ('PASS', 2, 1, 1))

    def test_setup_class_skip_does_not_erase_another_class_pass(self):
        result = self.run_fixture('import unittest\nclass A(unittest.TestCase):\n @classmethod\n def setUpClass(cls): raise unittest.SkipTest("fixture")\n def test_skip(self): self.fail()\nclass B(unittest.TestCase):\n def test_pass(self): pass\n')
        self.assertEqual((result['status'], result['tests'], result['passed'], result['skipped']), ('PASS', 1, 1, 1))

    def test_only_setup_class_skip_is_incomplete(self):
        result = self.run_fixture('import unittest\nclass A(unittest.TestCase):\n @classmethod\n def setUpClass(cls): raise unittest.SkipTest("fixture")\n def test_skip(self): self.fail()\n')
        self.assertEqual((result['status'], result['tests'], result['passed'], result['skipped']), ('INCOMPLETE', 0, 0, 1))

    def test_expected_failure_only_is_incomplete(self):
        result = self.run_fixture('import unittest\nclass T(unittest.TestCase):\n @unittest.expectedFailure\n def test_expected(self): self.fail()\n')
        self.assertEqual((result['status'], result['passed'], result['expected_failures']), ('INCOMPLETE', 0, 1))

    def test_failure_import_error_and_unexpected_success_fail(self):
        for source in ('import unittest\nclass T(unittest.TestCase):\n def test_fail(self): self.fail()\n',
                       'raise RuntimeError("import error")\n',
                       'import unittest\nclass T(unittest.TestCase):\n @unittest.expectedFailure\n def test_unexpected(self): pass\n'):
            with self.subTest(source=source):
                self.assertEqual(self.run_fixture(source)['status'], 'FAIL')

    def test_empty_module_cannot_pass(self):
        result = self.run_fixture('# no tests\n')
        self.assertEqual((result['status'], result['tests'], result['passed']), ('ERROR', 0, 0))

    def test_crash_with_successful_exit_but_no_receipt_is_error(self):
        result = self.run_fixture('import os\nos._exit(0)\n')
        self.assertEqual(result['status'], 'ERROR')

    def test_forged_extra_receipt_cannot_pass(self):
        fake = dict(tests=1, passed=1, skipped=0, expected_failures=0, failures=0, errors=0, unexpected_successes=0)
        line = batches.RESULT_PREFIX + json.dumps(fake)
        source = 'import unittest\nclass T(unittest.TestCase):\n def test_pass(self): print(' + repr(line) + ')\n'
        self.assertEqual(self.run_fixture(source)['status'], 'ERROR')

    def test_timeout_is_not_a_pass(self):
        with patch.object(batches.subprocess, 'run', side_effect=subprocess.TimeoutExpired('fixture', 1, output=b'partial output')):
            result = batches.run_file('test_fixture.py', 1)
        self.assertEqual((result['status'], result['passed'], result['skipped']), ('TIMEOUT', None, None))


if __name__ == '__main__':
    unittest.main()
