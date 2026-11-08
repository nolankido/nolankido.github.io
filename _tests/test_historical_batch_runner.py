"""The optional local history gate must report gaps instead of hiding failures."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import check_historical_batches as batches  # noqa: E402
import local_release_checks  # noqa: E402


class HistoricalBatchRunnerTests(unittest.TestCase):
    def test_inventory_is_sorted_and_has_no_unrelated_python_files(self):
        names = batches.discover("test_*history*.py")
        self.assertEqual(names, sorted(names))
        self.assertIn("test_later_release_history.py", names)
        self.assertTrue(all(n.startswith("test_") and n.endswith(".py") for n in names))
        for invalid in ("*.py", "../test_*.py", "test_*/test_*.py", "test_*.txt"):
            with self.subTest(pattern=invalid), self.assertRaises(ValueError):
                batches.discover(invalid)

    @patch.object(batches.subprocess, "run")
    def test_success_requires_a_real_nonempty_unittest_result(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, "Ran 3 tests in 0.001s\n\nOK\n")
        result = batches.run_file("test_later_release_history.py", 3)
        self.assertEqual((result["status"], result["tests"]), ("PASS", 3))
        self.assertEqual(run.call_args.kwargs["timeout"], 3)
        run.return_value = subprocess.CompletedProcess([], 0, "Ran 0 tests in 0.000s\n\nOK\n")
        self.assertEqual(batches.run_file("test_empty.py", 3)["status"], "ERROR")
        run.return_value = subprocess.CompletedProcess([], 0, "Nothing actually ran")
        self.assertEqual(batches.run_file("test_invalid.py", 3)["status"], "ERROR")

    @patch.object(batches.subprocess, "run")
    def test_failures_and_timeout_do_not_pass(self, run):
        run.return_value = subprocess.CompletedProcess(
            [], 1, "Ran 2 tests in 0.1s\n\nFAILED (failures=1)\n")
        self.assertEqual(batches.run_file("test_failure.py", 3)["status"], "FAIL")
        run.side_effect = subprocess.TimeoutExpired(
            cmd=[sys.executable], timeout=3, output=b"Still running")
        result = batches.run_file("test_slow.py", 3)
        self.assertEqual(result["status"], "TIMEOUT")
        self.assertIsNone(result["tests"])
        self.assertIn("Still running", result["output"])

    def test_checkpoint_is_valid_json_without_partial_truncation(self):
        with TemporaryDirectory() as temp:
            target = Path(temp) / "reports" / "historical.json"
            batches.checkpoint(target, {"completed": False, "results": [{"status": "FAIL"}]})
            self.assertEqual(json.loads(target.read_text())["results"][0]["status"], "FAIL")
            batches.checkpoint(target, {"completed": True, "results": []})
            self.assertTrue(json.loads(target.read_text())["completed"])
            self.assertFalse(target.with_name(target.name + ".tmp").exists())

    def test_bounded_selection_continues_past_failure_and_reports_uncovered(self):
        files = ["test_a.py", "test_b.py", "test_c.py", "test_d.py"]
        outcomes = [
            {"file": "test_b.py", "status": "FAIL", "tests": 1,
             "seconds": 0.01, "output": "FAIL", "skipped": 0},
            {"file": "test_c.py", "status": "PASS", "tests": 2,
             "seconds": 0.01, "output": "OK", "skipped": 0},
        ]
        output = StringIO()
        with patch.object(batches, "forbid_workflows"), \
                patch.object(batches, "discover", return_value=files), \
                patch.object(batches, "run_file", side_effect=outcomes) as run, \
                redirect_stdout(output):
            code = batches.main(["--start-index", "1", "--file-limit", "2",
                                 "--failure-lines", "0"])
        self.assertEqual(code, 1)
        self.assertEqual([call.args[0] for call in run.call_args_list], files[1:3])
        self.assertIn("2 other matching modules not covered", output.getvalue())

    def test_no_matching_tests_is_an_error(self):
        with patch.object(batches, "forbid_workflows"), \
                patch.object(batches, "discover", return_value=[]), \
                redirect_stderr(StringIO()):
            self.assertEqual(batches.main(["--pattern", "test_missing.py"]), 2)

    def test_very_long_failure_lines_are_bounded_in_console(self):
        output = StringIO()
        result = {"file": "test_a.py", "status": "FAIL", "tests": 1,
                  "seconds": 0.1, "output": "X" * 10000, "skipped": 0}
        with patch.object(batches, "forbid_workflows"), \
                patch.object(batches, "discover", return_value=["test_a.py"]), \
                patch.object(batches, "run_file", return_value=result), \
                redirect_stdout(output):
            self.assertEqual(batches.main(["--all"]), 1)
        self.assertLess(len(output.getvalue()), 1000)
        self.assertIn("9640 chars omitted", output.getvalue())

    def test_full_release_gate_uses_bounded_runner_and_no_actions(self):
        commands = []
        def record(label, command):
            commands.append((label, command))
            return True
        with patch.object(local_release_checks, "forbid_workflows"), \
                patch.object(local_release_checks, "check", side_effect=record), \
                patch.object(sys, "argv", ["local_release_checks.py", "--full"]), \
                redirect_stdout(StringIO()):
            self.assertEqual(local_release_checks.main(), 0)
        full = [args for label, args in commands if label.startswith("Full historical")]
        self.assertEqual(len(full), 1)
        self.assertIn("--all", full[0])
        self.assertIn("--timeout-seconds", full[0])
        self.assertNotIn(".github/workflows", " ".join(full[0]))


if __name__ == "__main__":
    unittest.main()
