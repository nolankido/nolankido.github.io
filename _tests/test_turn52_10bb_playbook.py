"""Turn 52: independently reproducible three-handed 10 BB ICM and publication route.

Use a distinct closed-form ICM formula to verify the enumerated public script.
All inputs are fictional and fixed. No solver, live hand or remote service.
"""
from fractions import Fraction as F
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import runpy
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import tenbb_companion


def classic_icm_three(stacks, prizes=(100, 60, 40)):
    """Closed-form hero-first/second/third, independent of order enumeration."""
    hero, sb, btn = stacks
    total = hero + sb + btn
    first = F(hero, total)
    second = F(sb, total) * F(hero, total - sb) + F(btn, total) * F(hero, total - btn)
    third = 1 - first - second
    return first * prizes[0] + second * prizes[1] + third * prizes[2]


class Turn52TenBB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (ROOT / "poker/10bb/index.html").read_text(encoding="utf-8")
        cls.script = ROOT / tenbb_companion.CODE
        cls.math = runpy.run_path(str(cls.script))
        cls.output = cls.math["model"]()

    def test_closed_form_independently_reproduces_original_three_player_icm(self):
        self.assertEqual(classic_icm_three((9, 21, 5)), F(64))
        self.assertEqual(classic_icm_three((20, 10, 5)), F(1696, 21))
        self.assertEqual(self.math["icm_value"]((9, 21, 5)), F(64))
        self.assertEqual(self.math["icm_value"]((20, 10, 5)), F(1696, 21))
        self.assertEqual(self.output["fold_prize_exact"], "64")
        self.assertEqual(self.output["win_prize_exact"], "1696/21")
        self.assertEqual(self.output["lose_prize_exact"], "40")

    def test_threshold_and_changed_probabilities_have_exact_values(self):
        self.assertEqual(self.output["icm_break_even_exact"], "63/107")
        self.assertAlmostEqual(self.output["icm_break_even_percent"], 58.87850467289719)
        self.assertEqual(self.output["chip_price_exact"], "9/20")
        self.assertEqual(self.output["extra_call_bb"], 9)
        self.assertEqual(self.output["final_matched_pot_bb"], 20)
        rows = self.output["hypothetical_win_probabilities"]
        self.assertEqual([r["assumed_win_percent"] for r in rows], [45, 50, 55, 60])
        exact = [F(-198, 35), F(-76, 21), F(-166, 105), F(16, 35)]
        self.assertEqual([F(r["icm_call_minus_fold_exact"]) for r in rows], exact)
        self.assertEqual([r["chip_ev_call_vs_fold_bb"] for r in rows], [0, 1, 2, 3])
        self.assertTrue(all(r["icm_call_minus_fold_dollars"] < 0 for r in rows[:3]))
        self.assertGreater(rows[-1]["icm_call_minus_fold_dollars"], 0)

    def test_public_math_is_honest_and_video_original_chapters_stay(self):
        for required in (
            'id="icm-reproduce"', '/downloads/ten-bb-playbook-icm-verify.py',
            '63/107, approximately 58.88%', '13.88 percentage points',
            '45% (chip break-even)', '50% (main lesson)', '55% (final Q6)',
            '60% (changed assumption)', '$58.34', '−$5.66', '$64.46', '+$0.46',
            '/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble',
            'different ICM threshold of about 56.40%', 'not a solver verdict',
            'Video 58:58', '44:09', 'Published <time datetime="2026-11-19"',
        ):
            self.assertIn(required, self.page)
        self.assertEqual(self.page.count('id="icm-reproduce"'), 1)
        self.assertEqual(self.page.count('href="/downloads/ten-bb-playbook-icm-verify.py"'), 1)
        self.assertNotIn(chr(0x2014), self.page)

    def test_manual_registration_is_fail_closed_and_keeps_dates(self):
        record = tenbb_companion.record(ROOT)
        self.assertEqual(record["url"], "https://nolankido.com/poker/10bb/")
        self.assertEqual(record["lastmod"], "2026-11-20")
        self.assertEqual(self.page.count('<meta property="article:published_time" content="2026-11-19">'), 1)
        self.assertEqual(self.page.count('<meta property="article:modified_time" content="2026-11-20">'), 1)
        for tamper in (
            self.page.replace('id="icm-reproduce"', 'id="unapproved"', 1),
            self.page.replace('rel="canonical"', 'rel="alternate"', 1),
            self.page.replace('"dateModified":"2026-11-20"', '"dateModified":"2026-11-19"', 1),
        ):
            with self.subTest(change=tamper != self.page):
                self.assertNotEqual(tamper, self.page)
                with self.assertRaises(ValueError):
                    tenbb_companion.inspect(tamper)

    def test_sitemap_and_read_only_exact_byte_inventory(self):
        root = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        matches = [x for x in root if x.findtext("{*}loc") == tenbb_companion.ORIGIN + tenbb_companion.ROUTE]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].findtext("{*}lastmod"), "2026-11-20")
        import check_live
        targets = check_live.targets(ROOT)
        self.assertEqual(targets["/poker/10bb/"], (200, self.page.encode("utf-8")))
        self.assertEqual(targets["/" + tenbb_companion.CODE], (200, self.script.read_bytes()))
        snapshot = json.loads((ROOT / "_reports/search-audit.json").read_text(encoding="utf-8"))
        self.assertEqual(snapshot["sitemap_urls"], 230)
        self.assertEqual(snapshot["manual_tenbb_pages"], 1)

    def test_private_hands_and_out_of_scope_tool_behaviors_are_absent(self):
        contents = self.script.read_text(encoding="utf-8")
        for bad in ("requests", "urllib", "socket", "subprocess", "input(", "open("):
            self.assertNotIn(bad, contents)
        self.assertIn("unknown", self.output["real_hand_or_solver_verdict"])
        self.assertEqual(self.output["payouts_dollars"], (100, 60, 40))
        self.assertEqual(self.math["CALL_LOSE"], (0, 30, 5))

    def test_release_check_runner_includes_new_contract(self):
        runner = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn52_10bb_playbook.py", runner)
        self.assertIn("['_scripts/build.py', '--check']", runner)
        actions = ROOT / ".github/workflows"
        self.assertFalse(actions.exists() and any(
            x.is_file() and x.suffix.lower() in (".yaml", ".yml") for x in actions.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
