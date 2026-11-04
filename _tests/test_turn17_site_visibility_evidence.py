"""Turn 17: publicly inspectable evidence for the site's visibility revisions."""
import re
import subprocess
import unittest
from pathlib import Path

import turn17_site_visibility_evidence_history as history
import turn21_poker_vlog_qa_history
import turn23_technology_metadata_history as turn23_history


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "_source/technology/home.html"
PUBLIC = "technology/index.html"
SECTION_ID = "site-visibility-evidence"
TARGETS = (
    "/technology/local-ai-gaming-laptop/",
    "/technology/review-reply-evidence-audit/",
    "/poker/nolan-kido/",
)


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def section(path):
    text = read(path)
    opening = '<section class="section folio-row" id="' + SECTION_ID + '"'
    if text.count(opening) != 1:
        raise AssertionError("Expected one reviewed visibility section in " + path)
    start = text.index(opening)
    return text[start:text.index("</section>", start) + len("</section>")]


class Turn17SiteVisibilityEvidenceTests(unittest.TestCase):
    def test_source_and_generated_release_evidence_match(self):
        self.assertEqual(section(SOURCE), section(PUBLIC))
        for path in (SOURCE, PUBLIC):
            with self.subTest(path=path):
                body = read(path)
                self.assertEqual(body.count('id="' + SECTION_ID + '"'), 1)
                self.assertEqual(body.count('href="#' + SECTION_ID + '"'), 1)
                self.assertLess(body.index('id="small-business-ai-pilot"'),
                                body.index('id="' + SECTION_ID + '"'))
                self.assertLess(body.index('id="' + SECTION_ID + '"'),
                                body.index('id="ai-judgment-across-domains"'))

    def test_sources_and_claims_are_explicit(self):
        body = section(PUBLIC)
        self.assertEqual(len(re.findall(r"<li>", body)), 3)
        for route in TARGETS:
            with self.subTest(route=route):
                self.assertIn('href="' + route + '"', body)
                self.assertTrue((ROOT / route.strip("/") / "index.html").is_file())
        for pr in (170, 171, 172):
            self.assertIn("https://github.com/nolankido/nolankido.github.io/pull/" + str(pr), body)
        self.assertIn("Google's link guidance", body)
        for phrase in ("Not established:", "referral traffic", "AI-generated answers",
                       "not a client case study", "not yet show"):
            self.assertIn(phrase, body)
        self.assertNotIn("\u2014", body)
        self.assertNotIn("guaranteed ranking", body.lower())

    def test_page_identity_and_other_paths_are_preserved(self):
        page = turn23_history.before(PUBLIC, read(PUBLIC))
        self.assertIn('<link rel="canonical" href="https://nolankido.com/technology/">', page)
        self.assertIn('"dateModified": "2026-11-03"', page)
        self.assertEqual(page.count('class="project-card"'), 3)
        for anchor in ("ai-works-human-decides", "small-business-ai-pilot",
                       "ai-judgment-across-domains", "practical-ai-path"):
            self.assertEqual(page.count('id="' + anchor + '"'), 1)

    def test_exact_prior_git_blobs_only(self):
        for path, (old_sha, current_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                raw = turn21_poker_vlog_qa_history.before(path, (ROOT / path).read_bytes())
                self.assertEqual(history.blob(raw), current_sha)
                prior = history.before(path, raw)
                self.assertEqual(history.blob(prior), old_sha)
                self.assertEqual(prior, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=ROOT
                ))
                self.assertEqual(history.before(path, prior), prior)
                self.assertEqual(
                    history.before(Path(path), raw.decode("utf-8")), prior.decode("utf-8")
                )

    def test_unrelated_changes_are_not_erased(self):
        for path in history.BLOBS:
            current = (ROOT / path).read_bytes()
            for mutation in (current + b"OTHER", b"OTHER" + current, current[1:]):
                self.assertEqual(history.before(path, mutation), mutation)
            self.assertEqual(history.before("unknown/" + path, current), current)
        self.assertEqual(history.before("other.bin", bytes([255, 0])), bytes([255, 0]))


if __name__ == "__main__":
    unittest.main()
