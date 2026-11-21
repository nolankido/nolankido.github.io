"""Turn 58: independently verify 8 BB shove and BB-call branch prices.

Fixed fictional nine-handed BBA model. This is not an action-complete
solver, opponent estimate, a real hand verdict or live-play advice.
"""
from fractions import Fraction as F
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import re
import runpy
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source/poker/six-to-ten-bb-tournament-decisions.html"
PUBLIC = ROOT / "poker/six-to-ten-bb-tournament-decisions/index.html"
SCRIPT = ROOT / "downloads/eight-bb-shove-branch-verify.py"
ROUTE = "/poker/six-to-ten-bb-tournament-decisions/"
DOWNLOAD = "/downloads/eight-bb-shove-branch-verify.py"
PARAGRAPHS = ("bridge-ev-break-even", "bridge-ev-two-prices", "bridge-ev-action-gate")


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids, self.urls = [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.urls.append(attrs["href"])


def paragraph(source, name):
    matches = re.findall(r'<p id="' + re.escape(name) + r'">(.*?)</p>', source, re.S)
    if len(matches) != 1:
        raise ValueError("missing or duplicate modeled paragraph " + name)
    return matches[0]


def errors(page):
    problems = []
    expectations = {
        "bridge-ev-break-even": ("f = 2 / 7", "28.57%", "−0.02 BB", "q = 97 / 245", "39.59%", "+0.05 BB"),
        "bridge-ev-two-prices": ("7 / 17.5 = 40%", "8 / 17.5 = 16 / 35", "45.71%", "not a 40% requirement", "prize-equity"),
        "bridge-ev-action-gate": ("joint", "BTN, SB and BB all fold", "BB alone calls", "2 BB open", "cannot establish", "hypothetical", DOWNLOAD),
    }
    for name, required in expectations.items():
        try:
            body = paragraph(page, name)
        except ValueError as e:
            problems.append(str(e))
            continue
        for word in required:
            if word.lower() not in body.lower():
                problems.append(name + ": missing " + word)
    return problems


def independent_ev(f, q):
    """Add mutually exclusive fold, win-when-called and lose-when-called."""
    f, q = F(f), F(q)
    return f * F(5, 2) + (1 - f) * q * F(19, 2) - (1 - f) * (1 - q) * F(8)


class CutoffShoveAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = SOURCE.read_text(encoding="utf-8")
        cls.pub = PUBLIC.read_text(encoding="utf-8")
        cls.program = SCRIPT.read_text(encoding="utf-8")
        cls.output = json.loads(subprocess.run(
            [sys.executable, str(SCRIPT)], cwd=ROOT, text=True, capture_output=True,
            check=True, timeout=15,
        ).stdout)

    def test_independent_math_and_two_different_player_baselines(self):
        self.assertEqual(F(7) / F(35, 2), F(2, 5))
        self.assertEqual(F(8) / F(35, 2), F(16, 35))
        self.assertNotEqual(F(2, 5), F(16, 35))
        cases = (
            (F(3, 10), F(2, 5), F(1, 20)),
            (F(7, 25), F(2, 5), -F(1, 50)),
            (F(3, 10), F(3, 10), -F(47, 40)),
            (F(2, 7), F(2, 5), 0),
            (F(3, 10), F(97, 245), 0),
        )
        for f, q, expected in cases:
            with self.subTest(f=f, q=q):
                self.assertEqual(independent_ev(f, q), expected)

    def test_public_program_outputs_exact_reconcilable_thresholds(self):
        got = self.output["exact_thresholds"]
        for key, target in (
            ("BB_extra_call_chip_price", F(2, 5)),
            ("CO_win_chance_if_always_called", F(16, 35)),
            ("CO_all_fold_chance_if_called_win_40pct", F(2, 7)),
            ("CO_win_if_called_at_all_fold_30pct", F(97, 245)),
            ("CO_all_fold_chance_if_called_win_30pct", F(11, 21)),
            ("CO_no_equity_all_fold_chance_with_BBA", F(16, 21)),
            ("CO_no_equity_all_fold_chance_without_ante", F(16, 19)),
        ):
            self.assertEqual(F(got[key]), target, key)
        for case in self.output["fictional_sensitivity"].values():
            self.assertEqual(F(case["EV_shove_minus_fold_bb"]),
                             independent_ev(F(case["joint_all_fold_probability"]),
                                            F(case["win_probability_conditional_on_BB_call"])))
        self.assertEqual(F(self.output["contested_pot_if_called_bb"]), F(35, 2))
        self.assertEqual(F(self.output["CO_called_win_net_bb"]), F(19, 2))
        self.assertEqual(F(self.output["CO_called_loss_net_bb"]), -8)

    def test_no_unsupported_inputs_network_or_solved_strategy(self):
        namespace = runpy.run_path(str(SCRIPT), run_name="turn58_import")
        for f, q in ((-F(1, 10), F(1, 2)), (F(1, 2), F(11, 10))):
            with self.assertRaises(ValueError):
                namespace["shove_ev"](f, q)
        with self.assertRaises(ValueError):
            namespace["called_win_break_even"](1)
        self.assertEqual(namespace["fold_break_even"](F(1, 2)), 0)
        self.assertIn("small-open/limp EV", self.output["limits"])
        for banned in ("import requests", "import urllib", "import httpx",
                       "input(", "open(", "write_text(", "write_bytes(", "socket"):
            self.assertNotIn(banned, self.program)

    def test_one_answer_per_anchor_and_source_public_parity(self):
        for doc in (self.src, self.pub):
            self.assertEqual(errors(doc), [])
            links = Links(doc)
            for id_ in PARAGRAPHS:
                self.assertEqual(links.ids.count(id_), 1)
            self.assertEqual(links.urls.count(DOWNLOAD), 1)
            self.assertIn("not a solved strategy", doc.lower())
        for ident in PARAGRAPHS:
            self.assertEqual(paragraph(self.src, ident), paragraph(self.pub, ident))
        self.assertEqual((self.src.count("<h2 "), self.pub.count("<h2 ")), (14, 15))
        self.assertEqual(self.pub.count('class="poker-details viewer-question"'), 9)
        self.assertEqual(self.pub.count('class="short-stack-table" role="region" tabindex="0"'), 4)
        self.assertNotIn(chr(0x2014), self.src)

    def test_publication_metadata_and_reading_estimates_agree(self):
        items = json.loads(read("_source/pages.json"))
        item = next(x for x in items if x["path"] == ROUTE)
        self.assertEqual((item["date"], item["updated"]), ("2026-11-15", "2026-11-20"))
        self.assertIn('article:published_time" content="2026-11-15"', self.pub)
        self.assertIn('article:modified_time" content="2026-11-20"', self.pub)
        self.assertIn('"dateModified": "2026-11-20"', self.pub)
        self.assertIn('datetime="2026-11-18"', self.pub)
        self.assertIn("About 24 min read", self.pub)
        sys.path.insert(0, str(ROOT / "_scripts"))
        import poker_library
        self.assertEqual(poker_library.minutes(self.src), 24)
        library = read("poker/library/index.html")
        card = '<h3><a href="' + ROUTE + '">Six to ten big blinds: the decisions between shove and small raise</a>'
        self.assertIn(card, library)
        self.assertIn("About 24 min read</span></p></article>",
                      library.split(card, 1)[1].split("</article>", 1)[0])
        for topic in ("tournaments", "strategy"):
            html = read("poker/topics/" + topic + "/index.html")
            self.assertIn('href="' + ROUTE + '">Six to ten big blinds: the decisions between shove and small raise</a>'
                          '<span class="topic-meta">Go deeper · About 24 min</span>', html)
        entries = ET.fromstring(read("sitemap.xml"))
        rows = [r for r in entries if r.findtext("{*}loc") == "https://nolankido.com" + ROUTE]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].findtext("{*}lastmod"), "2026-11-20")

    def test_negative_controls_reject_missing_and_misleading_claims(self):
        changes = (
            self.src.replace("45.71%", "40%", 1),
            self.src.replace("f = 2 / 7", "f = 3 / 7", 1),
            self.src.replace("q = 97 / 245", "q = 97 / 240", 1),
            self.src.replace("BB alone calls", "BTN also calls", 1),
            self.src.replace('href="' + DOWNLOAD + '"', 'href="/downloads/missing.py"', 1),
            self.src.replace('id="bridge-ev-action-gate"', 'id="missing"', 1),
        )
        for changed in changes:
            self.assertNotEqual(changed, self.src)
            self.assertTrue(errors(changed))

    def test_exact_public_asset_and_offline_release_registration(self):
        sys.path.insert(0, str(ROOT / "_scripts"))
        import check_live
        self.assertEqual(check_live.targets(ROOT)[DOWNLOAD], (200, SCRIPT.read_bytes()))
        self.assertIn("test_turn58_shove_branch.py", read("_scripts/local_release_checks.py"))
        folder = ROOT / ".github/workflows"
        self.assertFalse(folder.exists() and any(p.is_file() and p.suffix in (".yml", ".yaml")
                                                  for p in folder.iterdir()))


if __name__ == "__main__":
    unittest.main()
