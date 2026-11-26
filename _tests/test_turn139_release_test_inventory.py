"""Local Git controls for complete unit and browser release inventories."""
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
from release_test_inventory import browser_inventory, verify_tracked_units


class ReleaseTestInventoryTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.folder = self.root / '_tests'
        self.folder.mkdir()
        self.git('init', '-q')
        for name in ('browser.py', 'alpha_browser.py', 'zeta_browser.py',
                     'test_registered.py', 'test_historical_only.py', 'helper.py'):
            self.write(name)
        self.commit()

    def git(self, *args):
        subprocess.run(['git', '-C', str(self.root), *args], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def commit(self):
        self.git('add', '-A')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '-qm', 'test inventory fixture')

    def write(self, name):
        (self.folder / name).write_text('# fixture\n', encoding='utf-8')

    def test_primary_then_sorted_specialized_browser_suites(self):
        self.assertEqual(browser_inventory(self.root),
                         ['browser.py', 'alpha_browser.py', 'zeta_browser.py'])

    def test_preexisting_primary_deletion_cannot_pass(self):
        (self.folder / 'browser.py').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing committed browser tests: browser.py'):
            browser_inventory(self.root)

    def test_single_specialized_deletion_cannot_pass(self):
        (self.folder / 'alpha_browser.py').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing committed browser tests: alpha_browser.py'):
            browser_inventory(self.root)

    def test_new_local_suite_is_included_and_changes_inventory(self):
        before = browser_inventory(self.root)
        self.write('beta_browser.py')
        after = browser_inventory(self.root)
        self.assertEqual(after, ['browser.py', 'alpha_browser.py', 'beta_browser.py', 'zeta_browser.py'])
        self.assertNotEqual(before, after)

    def test_committed_primary_only_is_not_full_browser_coverage(self):
        for name in ('alpha_browser.py', 'zeta_browser.py'):
            (self.folder / name).unlink()
        self.commit()
        with self.assertRaisesRegex(ValueError, 'primary and specialized'):
            browser_inventory(self.root)

    def test_preexisting_historical_only_unit_deletion_cannot_pass(self):
        (self.folder / 'test_historical_only.py').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing committed unit tests: test_historical_only.py'):
            verify_tracked_units(self.root, ['test_registered.py'])

    def test_full_unit_inventory_accepts_new_local_modules(self):
        self.write('test_new.py')
        verify_tracked_units(self.root, ['test_historical_only.py', 'test_new.py', 'test_registered.py'])

    def test_directory_cannot_substitute_for_browser_script(self):
        path = self.folder / 'alpha_browser.py'
        path.unlink()
        path.mkdir()
        with self.assertRaisesRegex(ValueError, 'Non-regular browser test files: alpha_browser.py'):
            browser_inventory(self.root)

    def test_non_git_directory_cannot_supply_committed_inventory(self):
        with TemporaryDirectory() as empty, self.assertRaisesRegex(ValueError, 'Cannot read committed test inventory'):
            browser_inventory(Path(empty))


if __name__ == '__main__':
    unittest.main()
