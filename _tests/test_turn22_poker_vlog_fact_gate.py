"""Turn 22: exact, offline before-and-after poker-vlog fact gate."""
import json
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

import turn22_poker_vlog_fact_gate_history as history
import turn23_technology_metadata_history as turn23_history

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "_source/technology/home.html"
PUBLIC = "technology/index.html"
WORKSHEET = "downloads/poker-vlog-truth-to-screen-qa.md"
CHECKER = ROOT / "downloads/poker-vlog-fact-gate.py"
SECTION_ID = "poker-vlog-qa-demo"
BASE_COMMIT = "6eed318193a46e0f8480a782a7e6b79544704876"


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def section(path):
    page = read(path)
    marker = '<section class="section folio-row" id="' + SECTION_ID + '"'
    if page.count(marker) != 1:
        raise AssertionError("Missing or duplicate Turn 22 section: " + path)
    start = page.index(marker)
    return page[start:page.index("</section>", start) + len("</section>")]


class Tags(HTMLParser):
    VOID = {"br", "hr", "img", "input", "meta", "link", "source"}

    def __init__(self):
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise AssertionError("Unbalanced HTML tag: " + tag)


class Turn22PokerVlogFactGateTests(unittest.TestCase):
    def test_public_and_source_are_identical_in_the_added_section(self):
        self.assertEqual(section(SOURCE), section(PUBLIC))
        for path in (SOURCE, PUBLIC):
            with self.subTest(path=path):
                body = read(path)
                html = section(path)
                self.assertEqual(body.count('id="' + SECTION_ID + '"'), 1)
                self.assertEqual(body.count('id="poker-vlog-qa"'), 1)
                self.assertIn('aria-labelledby="poker-vlog-qa-demo-title"', html)
                self.assertIn('role="region"', html)
                self.assertIn('tabindex="0"', html)
                self.assertEqual(html.count('<tr>'), 5)
                self.assertEqual(html.count('<th scope="col">'), 3)
                self.assertEqual(html.count('<th scope="row">'), 4)
                self.assertIn('href="/downloads/poker-vlog-fact-gate.py"', html)
                self.assertIn('href="/downloads/poker-vlog-truth-to-screen-qa.md"', html)
                self.assertIn('https://', read("_source/poker/portland-meadows-ep1.html"))
                self.assertNotIn("\u2014", html)
                self.assertNotIn("<script", html.lower())
                self.assertNotIn("<iframe", html.lower())
                parsed = Tags()
                parsed.feed(html)
                self.assertEqual(parsed.stack, [])

    def test_self_test_has_exact_documented_synthetic_outcomes(self):
        run = subprocess.run([sys.executable, str(CHECKER), "--self-test"],
                             capture_output=True, text=True, check=True)
        data = json.loads(run.stdout)
        self.assertTrue(data["self_test_passed"])
        self.assertEqual(data["flags_before"], 7)
        self.assertEqual(data["flags_after"], 0)
        self.assertEqual(len(data["scenes"]), 4)
        expected = [
            {"UNVERIFIED_BOARD", "UNVERIFIED_SUITS"},
            {"OPEN_TO_BB_MISMATCH", "STACK_BB_MISMATCH"},
            {"FACT_CONFLICT"},
            {"STALE_TIMECODE", "UNVERIFIED_SOLVER"},
        ]
        for row, codes in zip(data["scenes"], expected):
            self.assertEqual(set(row["before_codes"]), codes)
            self.assertEqual(row["after_codes"], [])
            self.assertTrue(row["passed"])
        self.assertIn("not model outputs", data["demo"])
        self.assertIn("never approves", data["limit"])

    def test_checker_reads_local_json_and_uses_meaningful_exit_codes(self):
        sample = subprocess.run([sys.executable, str(CHECKER), "--example"],
                                capture_output=True, text=True, check=True)
        doc = json.loads(sample.stdout)
        self.assertEqual(len(doc["scenes"]), 3)
        with tempfile.TemporaryDirectory() as dirname:
            target = Path(dirname) / "local-scenes.json"
            target.write_text(sample.stdout, encoding="utf-8")
            good = subprocess.run([sys.executable, str(CHECKER), "--check", str(target)],
                                  capture_output=True, text=True)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertEqual(json.loads(good.stdout)["findings"], 0)
            doc["scenes"][0]["individual_suits_displayed"] = True
            doc["scenes"][2]["received_after_deal_usd"] = 5100
            target.write_text(json.dumps(doc), encoding="utf-8")
            flagged = subprocess.run([sys.executable, str(CHECKER), "--check", str(target)],
                                     capture_output=True, text=True)
            self.assertEqual(flagged.returncode, 2, flagged.stderr)
            self.assertEqual(json.loads(flagged.stdout)["findings"], 2)
            target.write_text("{ broken", encoding="utf-8")
            bad = subprocess.run([sys.executable, str(CHECKER), "--check", str(target)],
                                 capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            self.assertIn("Input error", bad.stderr)

    def test_worksheet_limits_and_existing_identity(self):
        sheet = read(WORKSHEET)
        for phrase in ("--self-test", "--example", "--check scenes.json",
                       "seven targeted flags", "zero after",
                       "No targeted flags never means approved"):
            self.assertIn(phrase.lower(), sheet.lower())
        self.assertNotIn("\u2014", sheet)
        page = turn23_history.before(PUBLIC, read(PUBLIC))
        self.assertIn('<link rel="canonical" href="https://nolankido.com/technology/">', page)
        self.assertIn('"dateModified": "2026-11-03"', page)
        self.assertEqual(page.count('class="project-card"'), 3)
        companion = read("poker/episodes/portland-meadows-ep1/index.html")
        for anchor in ("hand-64o-record", "hand-77-record", "event-numbers"):
            self.assertIn('id="' + anchor + '"', companion)

    def test_generator_has_the_current_public_output(self):
        sys.path.insert(0, str(ROOT / "_scripts"))
        import build
        self.assertEqual(build.build_outputs()[Path(PUBLIC)], read(PUBLIC))

    def test_sha_gated_history_only_rewinds_exact_known_files(self):
        self.assertTrue(history.is_added_file(CHECKER.relative_to(ROOT), CHECKER.read_bytes()))
        self.assertFalse(history.is_added_file(CHECKER.relative_to(ROOT), CHECKER.read_bytes() + b"x"))
        for path, (previous_sha, current_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = turn23_history.before(path, (ROOT / path).read_bytes())
                self.assertEqual(history.blob(current), current_sha)
                previous = history.before(path, current)
                self.assertEqual(history.blob(previous), previous_sha)
                self.assertEqual(previous, subprocess.check_output(
                    ["git", "show", BASE_COMMIT + ":" + path], cwd=ROOT
                ))
                self.assertEqual(history.before(path, previous), previous)
                self.assertEqual(history.before(Path(path), current.decode("utf-8")),
                                 previous.decode("utf-8"))
                for mutated in (current + b"x", b"x" + current, current[1:]):
                    self.assertEqual(history.before(path, mutated), mutated)
                self.assertEqual(history.before("unrelated/" + path, current), current)


if __name__ == "__main__":
    unittest.main()
