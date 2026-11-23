"""Turn 96: safeguard an exact invented example of Simpson's paradox.

No real player sample, tracker, remote service, or gameplay tool is used.
Run in a complete checkout with the existing manual release suite.
"""
from fractions import Fraction as F
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import ast
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "downloads/poker-opponent-frequency-verify.py"
WORKBOOK = ROOT / "downloads/poker-opponent-frequency-evidence-workbook.md"


def verifier():
    spec = spec_from_file_location("fixed_position_mix", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Missing standalone mathematical verifier")
    instance = module_from_spec(spec)
    spec.loader.exec_module(instance)
    return instance


class Turn96Standalone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKBOOK.read_text(encoding="utf-8")
        cls.source = SCRIPT.read_text(encoding="utf-8")
        cls.math = verifier()
        cls.report = cls.math.report()["position_mix_reversal"]

    def test_each_group_is_exactly_counted(self):
        a, b = self.report["A"], self.report["B"]
        self.assertEqual(a["earlier"], {"successes": 3, "opportunities": 30, "observed_rate": "10.0%"})
        self.assertEqual(b["earlier"], {"successes": 1, "opportunities": 20, "observed_rate": "5.0%"})
        self.assertEqual(a["later"], {"successes": 8, "opportunities": 20, "observed_rate": "40.0%"})
        self.assertEqual(b["later"], {"successes": 21, "opportunities": 60, "observed_rate": "35.0%"})

    def test_pooled_reversal_with_eligible_opportunities(self):
        self.assertGreater(F(3, 30), F(1, 20))
        self.assertGreater(F(8, 20), F(21, 60))
        self.assertEqual(F(11, 50), F(3+8, 30+20))
        self.assertEqual(F(22, 80), F(1+21, 20+60))
        self.assertLess(F(11, 50), F(22, 80))
        self.assertEqual(self.report["A"]["pooled"],
                         {"successes": 11, "opportunities": 50, "observed_rate": "22.0%"})
        self.assertEqual(self.report["B"]["pooled"],
                         {"successes": 22, "opportunities": 80, "observed_rate": "27.5%"})

    def test_explicit_equal_mix_changes_the_comparison(self):
        self.assertEqual((F(3, 30) + F(8, 20))/2, F(1, 4))
        self.assertEqual((F(1, 20) + F(21, 60))/2, F(1, 5))
        self.assertEqual(self.report["A"]["equal_position_mix_observed_rate"], "25.0%")
        self.assertEqual(self.report["B"]["equal_position_mix_observed_rate"], "20.0%")
        self.assertNotEqual(F(11, 50), F(1, 4))
        self.assertIn("hypothetical 50/50 common mix", self.report["interpretation"])

    def test_workbook_keeps_its_blank_template_and_complete_answer(self):
        titles = [line[:4] for line in self.text.splitlines() if line.startswith("## ")]
        self.assertEqual(titles, ["## 1", "## 2", "## 3", "## 4",
                                  "## 5", "## 6", "## 7", "## 8"])
        for marker in ("Simpson's paradox", "8. In the two-player position-mix example",
                       "8. **Within each fictional position group A", "11 / 50 = **22%**",
                       "22 / 80 = **27.5%**", "25% standardized observed rate",
                       "20% standardized observed rate", "## 7. Blank, private evidence record"):
            self.assertIn(marker, self.text)
        self.assertNotIn(chr(0x2014), self.text)

    def test_no_causal_or_real_player_claims(self):
        for marker in ("two entirely **fictional** players",
                       "not a verified real-world position distribution",
                       "not proof of a true behavioral difference",
                       "not proof about real players",
                       "Preserve denominators"):
            self.assertIn(marker.lower(), self.text.lower())
        self.assertNotIn("<form", self.text.lower())

    def test_cli_modes_and_old_statistics_survive(self):
        for mode in ("--json", "--self-test"):
            completed = subprocess.run([sys.executable, str(SCRIPT), mode],
                                       capture_output=True, text=True, timeout=20, check=True)
            self.assertEqual(completed.stderr, "")
            if mode == "--self-test":
                self.assertIn("PASS: fixed fictional opportunity denominators", completed.stdout)
            else:
                output = json.loads(completed.stdout)
                self.assertEqual(output["position_mix_reversal"], self.report)
                self.assertEqual(output["initial_opportunities"]["observed_rate"], "25.0%")
                self.assertEqual(output["fictional_beta_prior"]["posterior_mean"], "21.43%")

    def test_imports_and_invalid_counts_stay_bounded(self):
        self.assertEqual(self.math.observed_rate(11, 50), F(11, 50))
        for counts in ((31, 30), (-1, 20), (1, 0), (True, 1)):
            with self.assertRaises(ValueError):
                self.math.observed_rate(*counts)
        source_ast = ast.parse(self.source)
        imports = set()
        for node in source_ast.body:
            if isinstance(node, ast.Import):
                imports.update(p.name.split(".")[0] for p in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module.split(".")[0])
        self.assertEqual(imports, {"__future__", "argparse", "fractions",
                                   "json", "math", "statistics"})
        for unsafe in ("requests", "urllib", "socket", "fetch(", "open(",
                       "write_text(", "read_text(", "input(", chr(0x2014)):
            self.assertNotIn(unsafe, self.source)


class Turn96Integration(unittest.TestCase):
    def test_original_guide_links_and_canonical_unchanged(self):
        source = (ROOT / "_source/poker/poker-under-uncertainty.html").read_text(encoding="utf-8")
        html = (ROOT / "poker/poker-under-uncertainty/index.html").read_text(encoding="utf-8")
        label = 'aria-label="Practice opportunity denominators and sample uncertainty"'
        self.assertEqual(source.count(label), 1)
        self.assertEqual(html.count(label), 1)
        self.assertIn('href="/downloads/poker-opponent-frequency-evidence-workbook.md" download', source)
        self.assertIn('href="/downloads/poker-opponent-frequency-verify.py" download', source)
        self.assertIn('rel="canonical" href="https://nolankido.com/poker/poker-under-uncertainty/"', html)

    def test_no_new_sitemap_or_finder_entry(self):
        site_map = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        finder = (ROOT / "poker/find/index.html").read_text(encoding="utf-8")
        self.assertNotIn("poker-opponent-frequency-evidence-workbook.md", site_map)
        self.assertNotIn("poker-opponent-frequency-evidence-workbook.md", finder)
        self.assertIn("301 entries available.", finder)
        inventory = (ROOT / "_scripts/check_live.py").read_text(encoding="utf-8")
        for name in ("poker-opponent-frequency-evidence-workbook.md",
                     "poker-opponent-frequency-verify.py"):
            self.assertEqual(inventory.count("'downloads/" + name + "'"), 1)

    def test_runner_and_no_actions(self):
        runner = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn96_position_mix_reversal.py", runner)
        workflows = ROOT / ".github/workflows"
        self.assertFalse(workflows.exists() and any(
            p.is_file() and p.suffix.lower() in (".yaml", ".yml")
            for p in workflows.iterdir()))


if __name__ == "__main__":
    unittest.main()
