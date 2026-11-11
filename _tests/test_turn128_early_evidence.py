"""Turn 128: put bounded evidence before introductory prose on standalone AI cases."""

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build_local_laptop_case
import build_reply_audit_case


CASES = (
    ("local-ai-gaming-laptop", "local-laptop-intro", "laptop-snapshot-title",
     build_local_laptop_case.render,
     ("No timed model benchmark", "GitHub-hosted Ubuntu CPU runner, not the MSI laptop",
      "no new laptop performance result")),
    ("review-reply-evidence-audit", "reply-audit-intro", "reply-snapshot-title",
     build_reply_audit_case.render,
     ("zero targeted flags", "two missed unsupported offers",
      "No new model calls, human approval")),
)


def arrival_errors(source: str, section_id: str, title_id: str) -> list[str]:
    """Check document order, not viewport pixels or unmeasured user behavior."""
    fragments = (
        '<h2 id="' + section_id + '">',
        '<aside class="case-evidence-snapshot" aria-labelledby="' + title_id + '">',
        '<h3 id="' + title_id + '">Evidence at a glance</h3>',
        '<p class="intro">',
        '<nav class="entry-jumps"',
    )
    if any(source.count(fragment) != 1 for fragment in fragments):
        return ["missing or repeated article arrival element"]
    positions = [source.index(fragment) for fragment in fragments]
    if positions != sorted(positions):
        return ["evidence does not immediately follow the section heading, before the introduction"]
    # The card should be the next content after the heading, not a distant callout.
    after_heading = source.split(fragments[0], 1)[1].split("</h2>", 1)[1]
    if not after_heading.lstrip().startswith(fragments[1]):
        return ["other content interrupts the heading and first evidence summary"]
    return []


class EarlyEvidenceTests(unittest.TestCase):
    def test_source_and_compiled_pages_put_evidence_first(self):
        for slug, section_id, title_id, render, claims in CASES:
            with self.subTest(slug=slug):
                source = (ROOT / "_source/technology" / f"{slug}.html").read_text(encoding="utf-8")
                public = (ROOT / "technology" / slug / "index.html").read_text(encoding="utf-8")
                self.assertEqual(arrival_errors(source, section_id, title_id), [])
                self.assertEqual(arrival_errors(public, section_id, title_id), [])
                self.assertIn(source, public)
                self.assertEqual(render(), public)
                for claim in claims:
                    self.assertEqual(source.count(claim), 1, claim)
                self.assertNotIn(chr(0x2014), source)

    def test_delaying_or_duplicating_the_summary_fails(self):
        for slug, section_id, title_id, _, _ in CASES:
            source = (ROOT / "_source/technology" / f"{slug}.html").read_text(encoding="utf-8")
            marker = '<aside class="case-evidence-snapshot" aria-labelledby="' + title_id + '">'
            delayed = source.replace(marker, '<p class="intro">An unsupported introduction.</p>' + marker, 1)
            duplicated = source.replace(marker, marker + marker, 1)
            with self.subTest(slug=slug):
                self.assertTrue(arrival_errors(delayed, section_id, title_id))
                self.assertTrue(arrival_errors(duplicated, section_id, title_id))


if __name__ == "__main__":
    unittest.main()
