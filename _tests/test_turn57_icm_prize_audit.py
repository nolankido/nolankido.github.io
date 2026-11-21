"""Turn 57: exact three-player ICM, prize sensitivity and public audit route."""
from fractions import Fraction as F
from html.parser import HTMLParser
from pathlib import Path
from itertools import permutations
from xml.etree import ElementTree as ET
import json
import re
import runpy
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "downloads/tournament-equity-three-player-verify.py"
SOURCE = ROOT / "_source/poker/tournament-equity.html"
OUTPUT = ROOT / "poker/tournament-equity/index.html"
ROUTE = "/poker/tournament-equity/"
DOWNLOAD = "/downloads/tournament-equity-three-player-verify.py"


class Anchors(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.hrefs = []
        self.feed(raw)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def independent_icm(stacks, payouts):
    """A second finish-order enumeration, independent of the published verifier."""
    active = [i for i, v in enumerate(stacks) if v > 0]
    excluded = [i for i, v in enumerate(stacks) if v == 0]
    assert len(stacks) == len(payouts) == 3 and len(excluded) <= 1
    prize = [F(0)] * 3
    for order in permutations(active):
        remaining = sum(stacks)
        chance = F(1)
        for person in order:
            chance *= F(stacks[person], remaining)
            remaining -= stacks[person]
        for place, person in enumerate(order):
            prize[person] += chance * payouts[place]
    for person in excluded:
        prize[person] = F(payouts[-1])
    assert sum(prize) == sum(payouts)
    return tuple(prize)


def paragraph(html, identifier):
    v = re.findall(r'<p id="' + re.escape(identifier) + r'">(.*?)</p>', html, re.S)
    if len(v) != 1:
        raise ValueError("Expected a single source paragraph: " + identifier)
    return v[0]


def content_errors(html):
    errors = []
    for ident, fragments in {
        "icm-reproduce": ("tournament-equity-three-player-verify.py", "standard-library", "57.14%", "does not"),
        "icm-conservation": ("$100", "$110 / 3", "$32.83", "$30.50", "$36.67", "redistribution"),
        "icm-prize-sensitivity": ("$60 / $40 / $0", "5 / 8 = 62.5%", "+$0.67", "−$1.33", "50%", "same $100"),
    }.items():
        try:
            block = paragraph(html, ident)
            for text in fragments:
                if text.lower() not in block.lower():
                    errors.append(ident + " missing " + text)
        except ValueError:
            errors.append("missing/repeated " + ident)
    return errors


class ThreePlayerICMAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.public = OUTPUT.read_text(encoding="utf-8")
        cls.program = VERIFIER.read_text(encoding="utf-8")
        cls.result = json.loads(subprocess.run(
            [sys.executable, str(VERIFIER)], cwd=ROOT, capture_output=True,
            text=True, check=True, timeout=15,
        ).stdout)

    def test_script_matches_independent_finish_order_arithmetic(self):
        scenarios = self.result["scenarios"]
        stacks = ((10, 10, 10), (20, 0, 10), (0, 20, 10))
        for label, payout, desired in (
            ("standard_50_30_20", (50, 30, 20), F(4, 7)),
            ("front_loaded_60_40_0", (60, 40, 0), F(5, 8)),
            ("winner_only_100_0_0", (100, 0, 0), F(1, 2)),
        ):
            with self.subTest(label=label):
                row = scenarios[label]
                computed = [independent_icm(x, payout) for x in stacks]
                for key, values in zip((
                    "before_prize_equities_exact", "win_prize_equities_exact",
                    "lose_prize_equities_exact",
                ), computed):
                    self.assertEqual([F(x) for x in row[key]], list(values))
                self.assertEqual(F(row["hero_prize_break_even_exact"]), desired)
                self.assertEqual(row["prizes_dollars"], list(payout))
                self.assertEqual(row["equal_chip_transfer_break_even_exact"], "1/2")

    def test_spectator_and_55_percent_conserve_all_prize_value(self):
        row = self.result["hypothetical_55_percent_standard_ladder"]
        self.assertEqual(F(row["hero_fold_equity_exact"]), F(100, 3))
        self.assertEqual(F(row["hero_call_equity_exact"]), F(197, 6))
        self.assertEqual(F(row["hero_call_minus_fold_exact"]), -F(1, 2))
        self.assertEqual(F(row["uninvolved_player_equity_exact"]), F(110, 3))
        self.assertEqual(F(row["uninvolved_player_gain_over_no_gamble_exact"]), F(10, 3))
        self.assertEqual([F(s) for s in row["all_players_expected_prizes_exact"]],
                         [F(197, 6), F(61, 2), F(110, 3)])
        self.assertEqual(sum(F(x) for x in row["all_players_expected_prizes_exact"]), 100)
        self.assertEqual((row["hero_expected_chips"], row["hero_chips_if_fold"]), (11, 10))
        original = F(60, 100) * F(130, 3) + F(40, 100) * 20
        alternative = F(60, 100) * F(160, 3)
        self.assertEqual((original - F(100, 3), alternative - F(100, 3)),
                         (F(2, 3), -F(4, 3)))

    def test_script_has_fixed_public_inputs_and_no_network_or_user_file_writes(self):
        self.assertIn("from fractions import Fraction", self.program)
        self.assertIn("from itertools import permutations", self.program)
        for forbidden in ("import requests", "import urllib", "import httpx",
                          "input(", "open(", "write_text(", "write_bytes(", "argparse", "socket"):
            self.assertNotIn(forbidden, self.program)
        self.assertNotIn(chr(0x2014), self.program)
        module = runpy.run_path(str(VERIFIER), run_name="turn57_import")
        with self.assertRaises(ValueError):
            module["icm_values"]((-1, 11, 20), (50, 30, 20))
        with self.assertRaises(ValueError):
            module["icm_values"]((0, 0, 30), (50, 30, 20))
        with self.assertRaises(ValueError):
            module["icm_values"]((10, 10, 10), (30, 40, 30))
        self.assertEqual(module["verify"]()["checks"],
                         "pass: conserved chips, conserved prize pool and exact ICM thresholds")

    def test_published_source_parity_and_changed_reader_navigation(self):
        self.assertEqual(content_errors(self.source), [])
        self.assertEqual(content_errors(self.public), [])
        for ident in ("icm-reproduce", "icm-conservation", "icm-prize-sensitivity"):
            self.assertEqual(paragraph(self.source, ident), paragraph(self.public, ident))
            self.assertEqual(Anchors(self.source).ids.count(ident), 1)
            self.assertEqual(Anchors(self.public).ids.count(ident), 1)
        self.assertEqual(Anchors(self.source).hrefs.count(DOWNLOAD), 1)
        self.assertEqual(Anchors(self.public).hrefs.count(DOWNLOAD), 1)
        self.assertEqual(Anchors(self.source).hrefs.count("#icm-reproduce"), 1)
        self.assertEqual(len(re.findall(r"<h2\b", self.source)), 7)
        self.assertEqual(len(re.findall(r"<h2\b", self.public)), 8)
        self.assertIn("There are no blinds, antes, dead money, ties", self.source)
        self.assertNotIn(chr(0x2014), self.source)

    def test_published_identity_sitemap_and_derived_reading_minutes(self):
        manifest = json.loads(read("_source/pages.json"))
        page = next(x for x in manifest if x["id"] == "poker-tournament-equity")
        self.assertEqual((page["date"], page["updated"]), ("2026-10-06", "2026-11-20"))
        self.assertEqual(self.public.count('<link rel="canonical" href="https://nolankido.com' + ROUTE + '">'), 1)
        self.assertIn('"datePublished": "2026-10-06"', self.public)
        self.assertIn('"dateModified": "2026-11-20"', self.public)
        self.assertIn("About 7 min read", self.public)
        library = read("poker/library/index.html")
        topic = read("poker/topics/tournaments/index.html")
        self.assertIn('<h3><a href="/poker/tournament-equity/">Chips, prizes and ICM</a></h3>'
                      '<p>Audit a small example where gaining chips reduces modeled prize value.</p>'
                      '<p class="reader-card-meta"><span>Go deeper</span><span>About 7 min read</span></p>', library)
        self.assertIn('<li><a href="/poker/tournament-equity/">Chips, prizes and ICM</a>'
                      '<span class="topic-meta">Go deeper · About 7 min</span></li>', topic)
        sitemap = ET.fromstring(read("sitemap.xml"))
        found = [e for e in sitemap if e.findtext("{*}loc") == "https://nolankido.com" + ROUTE]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].findtext("{*}lastmod"), "2026-11-20")

    def test_negative_controls_find_missing_evidence_or_false_threshold(self):
        cases = (
            self.source.replace('5 / 8 = 62.5%', '4 / 7 = 57.14%', 1),
            self.source.replace('+$0.67', '+$1.67', 1),
            self.source.replace('id="icm-reproduce"', 'id="missing-verifier"', 1),
            self.source.replace('>$110 / 3 ≈ $36.67<', '>$110 / 3 ≈ $37.67<', 1),
        )
        for changed in cases:
            with self.subTest(changed=changed != self.source):
                self.assertNotEqual(changed, self.source)
                self.assertTrue(content_errors(changed) or
                                Anchors(changed).ids.count("icm-reproduce") != 1)

    def test_download_is_in_live_inventory_and_offline_runner(self):
        sys.path.insert(0, str(ROOT / "_scripts"))
        import check_live
        self.assertEqual(check_live.targets(ROOT)[DOWNLOAD], (200, VERIFIER.read_bytes()))
        self.assertIn("test_turn57_icm_prize_audit.py", read("_scripts/local_release_checks.py"))
        actions = ROOT / ".github/workflows"
        self.assertFalse(actions.exists() and any(
            x.is_file() and x.suffix in (".yml", ".yaml") for x in actions.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
