"""Offline controls for the manual audit preparation and rollback gate.

Fixture scripts simulate exit codes and report bytes, not site audit results.
The real site checks remain mandatory in a complete checkout.
"""
from pathlib import Path
import os
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '_scripts'))
import prepare_local_release as gate


class ReleasePreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.snapshot = self.root / gate.SNAPSHOT
        self.snapshot.parent.mkdir()
        self.before = b'{"status":"pass","sitemap_urls":230,"errors":[]}\n'
        self.after = b'{"status":"pass","sitemap_urls":231,"errors":[]}\n'
        self.snapshot.write_bytes(self.before)
        self.calls = []
        self.fail_step = None
        self.report = self.after
        self.concurrent = False

    def run_fixture(self, root, *args):
        self.assertEqual(root, self.root)
        self.calls.append(args)
        if args[0] == self.fail_step:
            raise gate.ReleaseError('fixture failure')
        if args[0] == '_scripts/check_search.py' and args[1] == '--json':
            Path(args[2]).write_bytes(self.report)
        if args[0] == '_scripts/check_search.py' and args[1] == '--verify-snapshot':
            self.assertEqual(Path(args[2]).read_bytes(), self.report)
        if args[0] == '_scripts/local_release_checks.py':
            self.assertEqual(args[1:], ('--full', '--browser'))
            self.assertEqual(self.snapshot.read_bytes(), self.report)
            if self.concurrent:
                self.snapshot.write_bytes(b'external edit\n')

    def invoke(self, apply=False):
        with patch.object(gate, 'run', side_effect=self.run_fixture):
            return gate.prepare(self.root, apply=apply)

    def test_dry_run_reports_drift_without_mutating_snapshot(self):
        self.assertEqual(self.invoke(), 2)
        self.assertEqual(self.snapshot.read_bytes(), self.before)
        self.assertEqual([x[0] for x in self.calls[:3]],
                         ['_scripts/build_books.py', '_scripts/build.py', '_tests/check_html5.py'])
        self.assertNotIn('_scripts/local_release_checks.py', [x[0] for x in self.calls])

    def test_matching_dry_run_is_not_full_release_pass(self):
        self.report = self.before
        self.assertEqual(self.invoke(), 0)
        self.assertEqual(self.snapshot.read_bytes(), self.before)
        self.assertNotIn('_scripts/local_release_checks.py', [x[0] for x in self.calls])

    def test_successful_apply_promotes_actual_candidate_bytes(self):
        self.assertEqual(self.invoke(apply=True), 0)
        self.assertEqual(self.snapshot.read_bytes(), self.after)
        self.assertEqual(self.calls[-1], ('_scripts/local_release_checks.py', '--full', '--browser'))

    def test_build_failure_stops_before_audit(self):
        self.fail_step = '_scripts/build.py'
        with self.assertRaises(gate.ReleaseError):
            self.invoke(apply=True)
        self.assertEqual(self.snapshot.read_bytes(), self.before)
        self.assertNotIn('_scripts/check_search.py', [x[0] for x in self.calls])

    def test_html5_failure_stops_before_audit(self):
        self.fail_step = '_tests/check_html5.py'
        with self.assertRaises(gate.ReleaseError):
            self.invoke(apply=True)
        self.assertEqual(self.snapshot.read_bytes(), self.before)
        self.assertNotIn('_scripts/check_search.py', [x[0] for x in self.calls])

    def test_nonpassing_or_malformed_report_cannot_replace_snapshot(self):
        for report in (b'not JSON', b'[]', b'{"status":"fail","sitemap_urls":231,"errors":[]}',
                       b'{"status":"pass","sitemap_urls":231,"errors":["bad"]}',
                       b'{"status":"pass","sitemap_urls":true,"errors":[]}',
                       b'{"status":"pass","errors":[]}'):
            with self.subTest(report=report):
                self.report = report
                with self.assertRaises(gate.ReleaseError):
                    self.invoke(apply=True)
                self.assertEqual(self.snapshot.read_bytes(), self.before)

    def test_audit_command_failure_preserves_old_report(self):
        self.fail_step = '_scripts/check_search.py'
        with self.assertRaises(gate.ReleaseError):
            self.invoke(apply=True)
        self.assertEqual(self.snapshot.read_bytes(), self.before)

    def test_full_release_failure_restores_old_report(self):
        self.fail_step = '_scripts/local_release_checks.py'
        with self.assertRaises(gate.ReleaseError):
            self.invoke(apply=True)
        self.assertEqual(self.snapshot.read_bytes(), self.before)

    def test_concurrent_edit_is_not_overwritten(self):
        self.concurrent = True
        with self.assertRaises(gate.ReleaseError):
            self.invoke(apply=True)
        self.assertEqual(self.snapshot.read_bytes(), b'external edit\n')

    def test_repository_workflow_is_refused(self):
        folder = self.root / '.github/workflows'
        folder.mkdir(parents=True)
        (folder / 'ci.yml').write_text('fixture: true\n')
        with self.assertRaises(gate.ReleaseError):
            self.invoke(apply=True)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.snapshot.read_bytes(), self.before)

    def test_missing_snapshot_is_refused(self):
        self.snapshot.unlink()
        with self.assertRaises(gate.ReleaseError):
            self.invoke(apply=True)
        self.assertEqual(self.calls, [])

    def test_atomic_write_does_not_leave_staging_files(self):
        gate.atomic_write(self.snapshot, self.after)
        self.assertEqual(self.snapshot.read_bytes(), self.after)
        self.assertEqual(list(self.snapshot.parent.iterdir()), [self.snapshot])


    def test_atomic_write_preserves_mode(self):
        if os.name == 'nt':
            self.skipTest('POSIX file mode check')
        self.snapshot.chmod(0o644)
        gate.atomic_write(self.snapshot, self.after)
        self.assertEqual(stat.S_IMODE(self.snapshot.stat().st_mode), 0o644)

    def process_fixture(self, *, fail_release):
        scripts = self.root / '_scripts'
        tests = self.root / '_tests'
        scripts.mkdir()
        tests.mkdir()
        for target in (scripts / 'build.py', scripts / 'build_books.py', tests / 'check_html5.py'):
            target.write_text('raise SystemExit(0)\n', encoding='utf-8')
        (scripts / 'check_search.py').write_text(
            'from pathlib import Path\nimport sys\n'
            f'expected = {self.after!r}\n'
            'path = Path(sys.argv[2])\n'
            'if sys.argv[1] == "--json":\n    path.write_bytes(expected)\n'
            'else:\n    raise SystemExit(path.read_bytes() != expected)\n', encoding='utf-8')
        (scripts / 'local_release_checks.py').write_text(
            'from pathlib import Path\nimport sys\n'
            f'expected = {self.after!r}\n'
            'if Path("_reports/search-audit.json").read_bytes() != expected:\n    raise SystemExit(10)\n'
            'if sys.argv[1:] != ["--full", "--browser"]:\n    raise SystemExit(11)\n'
            f'raise SystemExit({int(fail_release)})\n', encoding='utf-8')

    def test_real_subprocess_orchestration_promotes_candidate(self):
        self.process_fixture(fail_release=False)
        self.assertEqual(gate.prepare(self.root, apply=True), 0)
        self.assertEqual(self.snapshot.read_bytes(), self.after)

    def test_real_subprocess_orchestration_rolls_back_failure(self):
        self.process_fixture(fail_release=True)
        with self.assertRaisesRegex(gate.ReleaseError, 'local_release_checks.py'):
            gate.prepare(self.root, apply=True)
        self.assertEqual(self.snapshot.read_bytes(), self.before)


if __name__ == '__main__':
    unittest.main()
