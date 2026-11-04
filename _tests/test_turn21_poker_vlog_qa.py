"""Turn 21: public, source-bounded truth-to-screen QA for poker vlogs."""
import re
import subprocess
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

import turn21_poker_vlog_qa_history as history
import turn22_poker_vlog_fact_gate_history as turn22_history
import turn23_technology_metadata_history as turn23_history

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "_source/technology/home.html"
PUBLIC = "technology/index.html"
SHEET = "downloads/poker-vlog-truth-to-screen-qa.md"
COMPANION = "poker/episodes/portland-meadows-ep1/index.html"
SECTION_ID = "poker-vlog-qa"
RELEASE_BASE = "6aa56f6c37c8492398b2177ba860423232f96c0d"


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def section(path):
    page = read(path)
    marker = '<section class="section folio-row" id="' + SECTION_ID + '"'
    if page.count(marker) != 1:
        raise AssertionError("Missing or duplicate Turn 21 QA section: " + path)
    start = page.index(marker)
    return page[start:page.index("</section>", start) + len("</section>")]


class TagBalance(HTMLParser):
    VOID = {"br", "hr", "img", "input", "meta", "link", "source"}

    def __init__(self):
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise AssertionError("Unbalanced HTML element: " + tag)


class Turn21PokerVlogQATests(unittest.TestCase):
    def test_source_and_generated_section_match_and_are_accessible(self):
        self.assertEqual(section(SOURCE), section(PUBLIC))
        for path in (SOURCE, PUBLIC):
            with self.subTest(path=path):
                body = read(path)
                snip = section(path)
                self.assertEqual(body.count('id="' + SECTION_ID + '"'), 1)
                self.assertEqual(body.count('id="poker-vlog-qa-title"'), 1)
                self.assertIn('aria-labelledby="poker-vlog-qa-title"', snip)
                self.assertIn('role="region"', snip)
                self.assertIn('tabindex="0"', snip)
                self.assertEqual(snip.count('<th scope="col">'), 3)
                self.assertEqual(snip.count('<th scope="row">'), 3)
                self.assertEqual(snip.count('<tr>'), 4)
                self.assertEqual(snip.count('<li>'), 5)
                self.assertIn('href="/' + SHEET + '"', snip)
                self.assertNotIn("\u2014", snip)
                self.assertNotIn("<script", snip.lower())
                self.assertNotIn("<iframe", snip.lower())
                parsed = TagBalance()
                parsed.feed(snip)
                self.assertFalse(parsed.stack, parsed.stack)

    def test_companion_citations_and_careful_math(self):
        companion = read(COMPANION)
        snip = section(PUBLIC)
        for anchor in ("hand-64o-record", "hand-77-record", "event-numbers"):
            with self.subTest(anchor=anchor):
                self.assertEqual(companion.count('id="' + anchor + '"'), 1)
                self.assertIn('/poker/episodes/portland-meadows-ep1/#' + anchor, snip)
        self.assertAlmostEqual(148000 / 15000, 9.87, places=2)
        self.assertEqual(585000 / 30000, 19.5)
        self.assertEqual(75000 / 30000, 2.5)
        for fact in ("9.87 BB", "19.5 BB", "2.5 BB", "$5,100", "$2,900",
                     "not proof that every earlier upload passed", "unknown",
                     "retrospective", "current public upload"):
            self.assertIn(fact.lower(), snip.lower())

    def test_download_is_useful_and_has_boundaries(self):
        self.assertTrue((ROOT / SHEET).is_file())
        sheet = read(SHEET)
        for value in ("SOURCE-BACKED", "RECOLLECTED", "RETROSPECTIVE",
                      "UNKNOWN", "ILLUSTRATIVE", "HOLD", "REVISE", "ACCEPT",
                      "voiceover", "timecodes", "filming", "no account"):
            self.assertIn(value.lower(), sheet.lower())
        for anchor in ("#hand-64o-record", "#hand-77-record", "#event-numbers"):
            self.assertIn(anchor, sheet)
        self.assertIn("148,000 / 15,000 = 9.87 BB", sheet)
        self.assertIn("585k = 19.5 BB", sheet)
        self.assertIn("75k total, 2.5 BB", sheet)
        self.assertNotIn("\u2014", sheet)
        self.assertNotIn("unverified as proven", sheet.lower())

    def test_page_identity_and_generator_remain_in_sync(self):
        published = read(PUBLIC)
        page = turn23_history.before(PUBLIC, published)
        self.assertIn('<link rel="canonical" href="https://nolankido.com/technology/">', page)
        self.assertIn('"dateModified": "2026-11-03"', page)
        self.assertEqual(page.count('class="project-card"'), 3)
        for anchor in ("ai-works-human-decides", "small-business-ai-pilot",
                       "site-visibility-evidence", "ai-judgment-across-domains",
                       "practical-ai-path", SECTION_ID):
            self.assertEqual(page.count('id="' + anchor + '"'), 1)
        sys.path.insert(0, str(ROOT / "_scripts"))
        import build
        self.assertEqual(build.build_outputs()[Path(PUBLIC)], published)

    def test_only_exact_approved_blobs_rewind(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                data = turn22_history.before(path, (ROOT / path).read_bytes())
                self.assertEqual(history.blob(data), new_sha)
                prior = history.before(path, data)
                self.assertEqual(history.blob(prior), old_sha)
                self.assertEqual(prior, subprocess.check_output(
                    ["git", "show", RELEASE_BASE + ":" + path], cwd=ROOT
                ))
                self.assertEqual(history.before(path, prior), prior)
                self.assertEqual(history.before(Path(path), data.decode("utf-8")),
                                 prior.decode("utf-8"))
                for changed in (data + b"extra", b"extra" + data, data[1:]):
                    self.assertEqual(history.before(path, changed), changed)
                self.assertEqual(history.before("not/" + path, data), data)


if __name__ == "__main__":
    unittest.main()
