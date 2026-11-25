"""Full release execution must cover every module without duplicate focused runs."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '_scripts'))
import check_historical_batches as batches
from release_unit_plan import full_unit_plan, check_inventory

PASS = 'import unittest\nclass T(unittest.TestCase):\n def test_pass(self): pass\n'


def group(label, pattern):
    return label, ['-m', 'unittest', 'discover', '-s', '_tests', '-p', pattern, '-q']


class FullUnitPlanTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.folder = self.root / '_tests'
        self.folder.mkdir()
        for name in ('test_a.py', 'test_b.py', 'test_c.py'):
            (self.folder / name).write_text(PASS, encoding='utf-8')
        self.names = ['test_a.py', 'test_b.py', 'test_c.py']
        self.pin = self.root / 'inventory.json'
        self.pin.write_text(json.dumps(self.names), encoding='utf-8')

    def run_pinned(self, *extra):
        with patch.object(batches, 'ROOT', self.root), patch.object(batches, 'TESTS', self.folder), \
                patch.object(batches, 'forbid_workflows'), redirect_stdout(StringIO()) as out, \
                redirect_stderr(StringIO()) as err:
            code = batches.main(['--all', '--expected-inventory', str(self.pin), *extra])
        return code, out.getvalue(), err.getvalue()

    def test_plan_preserves_nonunit_checks_and_includes_unregistered_modules(self):
        nonunit = [('Build', ['_scripts/build.py', '--check']), ('HTML5', ['_tests/check_html5.py'])]
        tasks = [nonunit[0], group('A', 'test_a.py'), group('B', 'test_b.py'), nonunit[1]]
        retained, names, groups, covered = full_unit_plan(tasks, self.folder)
        self.assertEqual(retained, nonunit)
        self.assertEqual(names, self.names)
        self.assertEqual((groups, covered), (2, 2))
        self.assertEqual(len(tasks), 4)

    def test_overlapping_patterns_do_not_duplicate_module_coverage(self):
        _, names, groups, covered = full_unit_plan([group('A', 'test_a.py'), group('All', 'test_*.py')], self.folder)
        self.assertEqual(names, self.names)
        self.assertEqual((groups, covered), (2, 3))

    def test_missing_focused_registration_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'not covered'):
            full_unit_plan([group('Missing', 'test_missing.py')], self.folder)

    def test_bad_command_and_empty_inventory_are_refused(self):
        bad = group('A', 'test_a.py')
        bad[1][4] = 'elsewhere'
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            full_unit_plan([bad], self.folder)
        with self.assertRaisesRegex(ValueError, 'No historical'):
            full_unit_plan([], self.root / 'missing')

    def test_exact_pin_rejects_missing_extra_and_invalid_lists(self):
        check_inventory(self.pin, self.names)
        for actual in (self.names[:-1], self.names + ['test_extra.py']):
            with self.subTest(actual=actual), self.assertRaisesRegex(ValueError, 'inventory changed'):
                check_inventory(self.pin, actual)
        for value in ([], ['test_b.py', 'test_a.py'], ['test_a.py', 'test_a.py'], [1], {}):
            with self.subTest(value=value):
                self.pin.write_text(json.dumps(value), encoding='utf-8')
                with self.assertRaises(ValueError):
                    check_inventory(self.pin, self.names)

    def test_real_pinned_run_executes_all_modules_exactly_once(self):
        code, output, _ = self.run_pinned()
        self.assertEqual(code, 0)
        for name in self.names:
            self.assertEqual(output.count('RUN ' + name), 1)
        self.assertIn('3 actual passes', output)

    def test_missing_module_blocks_before_any_execution(self):
        (self.folder / self.names[-1]).unlink()
        with patch.object(batches, 'run_file') as run:
            code, _, err = self.run_pinned()
        self.assertEqual(code, 2)
        self.assertIn('inventory changed', err)
        run.assert_not_called()

    def test_pinned_partial_selection_is_refused(self):
        with patch.object(batches, 'run_file') as run:
            code, _, err = self.run_pinned('--start-index', '1')
        self.assertEqual(code, 2)
        self.assertIn('unfiltered full unit run', err)
        run.assert_not_called()

    def test_module_added_during_real_run_blocks_release(self):
        (self.folder / 'test_c.py').write_text(
            'from pathlib import Path\n' + PASS.replace('def test_pass(self): pass',
            'def test_pass(self): Path("_tests/test_extra.py").write_text("# new module")'), encoding='utf-8')
        code, _, err = self.run_pinned()
        self.assertEqual(code, 2)
        self.assertIn('inventory changed', err)

    def test_failed_historical_only_module_still_fails_release(self):
        (self.folder / 'test_c.py').write_text(PASS.replace('pass\n', 'self.fail()\n'), encoding='utf-8')
        code, output, _ = self.run_pinned()
        self.assertEqual(code, 1)
        self.assertIn('FAIL test_c.py', output)
        self.assertIn('2 actual passes', output)


if __name__ == '__main__':
    unittest.main()
