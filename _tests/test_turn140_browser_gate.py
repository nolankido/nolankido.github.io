"""Regression controls for early local browser capability and execution policy."""
from contextlib import redirect_stdout
from io import StringIO
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import release_browser_gate as gate
import local_release_checks as release


class BrowserGateTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def script(self, content):
        (self.root / 'probe.py').write_text(content, encoding='utf-8')

    def test_browser_child_assertions_are_not_stripped(self):
        self.script('assert False, "must fail even in an optimized environment"\n')
        with patch.dict(os.environ, {'PYTHONOPTIMIZE': '2'}):
            self.assertFalse(gate.run_browser(self.root, 'probe.py'))
            self.assertEqual(os.environ['PYTHONOPTIMIZE'], '2')

    def test_child_requires_repository_and_preserves_browser_selection(self):
        self.script('import os, sys\nassert sys.flags.optimize == 0\n'
                    'assert os.environ["POKER_BROWSER_REQUIRE_REPO"] == "1"\n'
                    'assert os.environ["CHROMIUM_PATH"] == "selected-browser"\n')
        with patch.dict(os.environ, {'PYTHONOPTIMIZE': '2',
                                      'POKER_BROWSER_REQUIRE_REPO': '0',
                                      'CHROMIUM_PATH': 'selected-browser'}):
            self.assertTrue(gate.run_browser(self.root, 'probe.py'))
            self.assertEqual(os.environ['POKER_BROWSER_REQUIRE_REPO'], '0')

    def test_timeout_blocks_release(self):
        self.script('import time\ntime.sleep(30)\n')
        with redirect_stdout(StringIO()) as output:
            self.assertFalse(gate.run_browser(self.root, 'probe.py', timeout=1))
        self.assertIn('exceeded 1s', output.getvalue())

    def test_process_launch_error_blocks_release(self):
        with patch.object(gate.subprocess, 'run', side_effect=OSError('fixture failure')):
            self.assertFalse(gate.run_browser(self.root, 'probe.py'))

    def test_preflight_uses_a_bounded_separate_process(self):
        with patch.object(gate, 'run_browser', return_value=True) as run:
            self.assertTrue(gate.preflight(self.root))
        run.assert_called_once_with(self.root, '_scripts/release_browser_gate.py',
                                    timeout=gate.PREFLIGHT_TIMEOUT)

    def test_failed_preflight_prevents_expensive_release_tasks(self):
        with patch('release_test_inventory.browser_inventory', return_value=['browser.py']), \
                patch.object(gate, 'preflight', return_value=False), \
                patch.object(release, 'check') as check, \
                patch.object(gate, 'run_browser') as run:
            self.assertEqual(release.run_tasks([('Units', ['unit.py'])], browser=True), 2)
        check.assert_not_called()
        run.assert_not_called()

    def test_success_runs_all_browser_scripts_in_original_order(self):
        suites = ['browser.py', 'alpha_browser.py', 'zeta_browser.py']
        events = []
        with patch('release_test_inventory.browser_inventory', return_value=suites), \
                patch.object(gate, 'preflight', side_effect=lambda root: events.append('preflight') or True), \
                patch.object(release, 'check', side_effect=lambda label, args: events.append(label) or True), \
                patch.object(gate, 'run_browser', side_effect=lambda root, script: events.append(Path(script).name) or script != str(Path('_tests') / 'alpha_browser.py')):
            self.assertEqual(release.run_tasks([('Units', ['unit.py'])], browser=True), 1)
        self.assertEqual(events, ['preflight', 'Units', *suites])

    def test_unit_only_mode_does_not_require_browser(self):
        with patch.object(gate, 'preflight') as preflight, patch.object(release, 'check', return_value=True):
            self.assertEqual(release.run_tasks([('Units', ['unit.py'])], browser=False), 0)
        preflight.assert_not_called()


if __name__ == '__main__':
    unittest.main()
