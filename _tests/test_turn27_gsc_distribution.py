"""Turn 27: portable tests and release inventory for the private GSC comparator."""

import ast
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOWNLOAD = ROOT / "downloads/gsc-period-compare.py"
LIVE = ROOT / "_scripts/check_live.py"
ORIGINAL_TEST = ROOT / "_tests/test_gsc_period_compare.py"


class ComparatorDistributionTests(unittest.TestCase):
    def test_comparator_is_available_at_documented_path(self):
        self.assertTrue(DOWNLOAD.is_file())
        compile(DOWNLOAD.read_text(encoding="utf-8"), str(DOWNLOAD), "exec")

    def test_release_inventory_contains_comparator_once(self):
        source = LIVE.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(LIVE))
        targets = next(n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "targets")
        registered = [n.value for n in ast.walk(targets) if isinstance(n, ast.Constant) and isinstance(n.value, str)
                      and n.value == "downloads/gsc-period-compare.py"]
        self.assertEqual(registered, ["downloads/gsc-period-compare.py"])
        self.assertIn("result['/' + path] = (200, (root / path).read_bytes())", source)
        self.assertIn("body != expected[1]", source)
        self.assertIn("status != expected[0]", source)

    def test_existing_unit_tests_import_script_from_repo_root(self):
        source = ORIGINAL_TEST.read_text(encoding="utf-8")
        self.assertIn('MODULE = ROOT / "downloads" / "gsc-period-compare.py"', source)
        self.assertNotIn('Path(__file__).with_name("gsc-period-compare.py")', source)
        spec = importlib.util.spec_from_file_location("gsc_compare", DOWNLOAD)
        self.assertIsNotNone(spec)
        self.assertTrue(spec.origin.endswith("downloads/gsc-period-compare.py"))

    def test_cli_is_usable_from_repo_root(self):
        completed = subprocess.run([sys.executable, str(DOWNLOAD), "--help"], cwd=ROOT,
                                   text=True, capture_output=True, check=False, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--same-filters-confirmed", completed.stdout)
        self.assertIn("--baseline", completed.stdout)
        self.assertIn("--followup", completed.stdout)


if __name__ == "__main__":
    unittest.main()
