"""Turn 16: a bounded, useful small-business AI pilot on the Technology hub."""
import re
import subprocess
import unittest
from pathlib import Path

import turn16_small_business_pilot_history as history
import turn17_site_visibility_evidence_history


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "_source/technology/home.html"
PUBLIC = "technology/index.html"
SECTION_ID = "small-business-ai-pilot"
EXPECTED_LINKS = (
    "/technology/should-i-use-ai/",
    "/technology/task-brief/",
    "/technology/review-reply-evidence-audit/",
    "/technology/ai-time-savings/",
    "/technology/local-ai-review-replies/",
)


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def section(path):
    value = read(path)
    opening = '<section class="section folio-row" id="' + SECTION_ID + '"'
    assert value.count(opening) == 1, path
    start = value.index(opening)
    end = value.index("</section>", start) + len("</section>")
    return value[start:end]


class Turn16SmallBusinessPilotTests(unittest.TestCase):
    def test_source_and_published_section_match_exactly(self):
        self.assertEqual(section(SOURCE), section(PUBLIC))
        for path in (SOURCE, PUBLIC):
            with self.subTest(path=path):
                body = read(path)
                self.assertEqual(body.count('id="' + SECTION_ID + '"'), 1)
                self.assertEqual(body.count('href="#' + SECTION_ID + '"'), 1)
                self.assertIn("How can a small business start using AI on a real workflow?", body)
                self.assertLess(body.index('id="ai-works-human-decides"'),
                                body.index('id="' + SECTION_ID + '"'))
                self.assertLess(body.index('id="' + SECTION_ID + '"'),
                                body.index('id="ai-judgment-across-domains"'))

    def test_auditable_decisions_and_claim_boundaries(self):
        body = section(PUBLIC)
        self.assertEqual(len(re.findall(r"<li>", body)), 5)
        for wording in (
            "unauthorized input",
            "human approval",
            "fictional customer",
            "duplicate charge",
            "unsupported promise",
            "manual fallback",
            "not a production error-rate study",
            "Neither is evidence of client deployment",
            "not a NIST assessment",
        ):
            with self.subTest(wording=wording):
                self.assertIn(wording, body)
        for forbidden in ("\u2014", "guaranteed return", "proven revenue", "certified compliant"):
            self.assertNotIn(forbidden, body.lower())

    def test_internal_links_exist_and_are_semantic(self):
        body = section(PUBLIC)
        for route in EXPECTED_LINKS:
            with self.subTest(route=route):
                self.assertIn('href="' + route + '"', body)
                self.assertTrue((ROOT / route.strip("/") / "index.html").is_file())
        self.assertIn('href="https://www.nist.gov/itl/ai-risk-management-framework"', body)
        public = read(PUBLIC)
        self.assertEqual(public.count('class="project-card"'), 3)
        self.assertEqual(public.count('id="ai-judgment-across-domains"'), 1)

    def test_exact_reviewed_predecessor_only(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                raw = turn17_site_visibility_evidence_history.before(path, (ROOT / path).read_bytes())
                self.assertEqual(history.blob(raw), new_sha)
                old = history.before(path, raw)
                self.assertEqual(history.blob(old), old_sha)
                self.assertEqual(old, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=ROOT
                ))
                self.assertEqual(history.before(path, old), old)
                self.assertEqual(
                    history.before(Path(path), raw.decode("utf-8")), old.decode("utf-8")
                )

    def test_unreviewed_mutations_pass_through(self):
        for path in history.BLOBS:
            raw = (ROOT / path).read_bytes()
            for edited in (raw + b"OTHER", b"OTHER" + raw, raw[1:]):
                self.assertEqual(history.before(path, edited), edited)
            self.assertEqual(history.before("unrelated/" + path, raw), raw)
        self.assertEqual(history.before("other.bin", bytes([0, 255])),
                         bytes([0, 255]))


if __name__ == "__main__":
    unittest.main()
