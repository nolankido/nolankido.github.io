"""Document independent festival rules and a prepared, unsent event-results inquiry."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build_poker_episode
import poker_episode

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

class PortlandRulesAndInquiryTests(unittest.TestCase):
    def test_festival_rules_are_published_not_observed_in_hand(self):
        data = json.loads(read("downloads/portland-meadows-organizer-schedule-2026.json"))
        rules = data["festival_wide_published_rules"]
        self.assertEqual(data["scheduled_event"]["date"], "2026-08-20")
        self.assertEqual(rules["source_page"], 2)
        self.assertIn("When heads up in a pot", rules["heads_up_pot_speech_and_card_showing"]["printed_rule"])
        self.assertIn("twice the big blind", rules["under_the_gun_live_straddle"]["printed_rule"])
        self.assertFalse(rules["heads_up_pot_speech_and_card_showing"]["applies_to_narrated_hands_confirmed"])
        self.assertFalse(rules["under_the_gun_live_straddle"]["applies_to_narrated_hands_confirmed"])
        self.assertIn("no such straddle has been identified", rules["strategic_interpretation"])
        for key, value in data["evidence_boundaries"].items():
            if key == "confirms_scheduled_event_and_published_structure":
                self.assertTrue(value)
            else:
                self.assertFalse(value, key)

    def test_public_companion_preserves_exact_author_source_and_hand_limits(self):
        body = read("_source/poker/portland-meadows-ep1.html")
        html = read("poker/episodes/portland-meadows-ep1/index.html")
        self.assertEqual(html, build_poker_episode.render())
        self.assertEqual(html.count(body), 1)
        self.assertIn("Two unusual Wild West rules, and why they matter for hand review.", body)
        self.assertIn("an <strong>under-the-gun live straddle for twice the big blind</strong>", body)
        self.assertIn("No source establishes that a straddle or the card-showing permission was used", body)
        self.assertIn("do not change", body.lower())
        self.assertIn('href="/downloads/portland-meadows-aug20-event-results-confirmation-request.md" download', body)
        self.assertIn("<strong>not been sent</strong>", body)
        self.assertEqual(body.count('id="episode-organizer-schedule"'), 1)
        self.assertEqual(body.count('id="episode-result-source-status"'), 1)
        self.assertIn('datetime="2026-11-02">November 2, 2026', body)
        self.assertIn('datetime="2026-11-20">November 20, 2026', body)
        self.assertNotIn(chr(0x2014), body)
        self.assertNotIn("<iframe", body.lower())
        self.assertNotIn("<form", body.lower())
        self.assertEqual(poker_episode.MODIFIED, "2026-11-20")

    def test_request_not_sent_and_not_cited_as_payment_verification(self):
        doc = read("downloads/portland-meadows-aug20-event-results-confirmation-request.md")
        audit = json.loads(read("downloads/portland-meadows-result-source-audit-2026-11-20.json"))
        status = audit["venue_confirmation_request"]
        self.assertEqual(status["status"], "prepared_not_sent")
        self.assertEqual(status["prepared_date"], "2026-11-20")
        self.assertFalse(status["organizer_reply_received"])
        self.assertFalse(status["organizer_verified_result_or_payment"])
        self.assertFalse(status["private_player_data_to_publish"])
        self.assertIn("503-309-3087", status["verified_contact_method"])
        self.assertIn("https://portlandmeadows.com/hours-%26-location", status["official_contact_page"])
        self.assertIn("Prepared only", doc)
        self.assertIn("No email, call or contact-form request has been sent", doc)
        self.assertIn("88 entries", doc)
        self.assertIn("$17,600", doc)
        self.assertIn("$5,100", doc)
        self.assertIn("$2,900", doc)
        self.assertIn("Do not post", doc)
        self.assertNotIn("@", doc)
        self.assertNotIn(chr(0x2014), doc)
        for key, val in audit["verification_flags"].items():
            if key == "schedule_independently_confirmed":
                self.assertTrue(val)
            else:
                self.assertFalse(val, key)

    def test_live_and_portfolio_discovery_without_new_search_headings(self):
        source = read("_source/ai-in-real-life.html")
        published = read("ai-in-real-life/index.html")
        self.assertIn("heads-up discussion or card showing rule", source)
        self.assertIn("neither of which can be assumed", source)
        before = '<section class="section folio-row" id="real-life-creator"'
        after = '<section class="section folio-row" id="real-life-everyday"'
        self.assertEqual(source.split(before, 1)[1].split(after, 1)[0],
                         published.split(before, 1)[1].split(after, 1)[0])
        self.assertEqual(source.count("<h2 "), 9)
        self.assertIn("downloads/portland-meadows-aug20-event-results-confirmation-request.md",
                      read("_scripts/check_live.py"))
        self.assertIn("## L. Venue records request and festival-specific rule verification",
                      read("downloads/nolanpoker-content-production-evidence-ledger.md"))
        self.assertIn('"episode-result-source-status-title"', read("find/index.html"))
        self.assertIn('"episode-organizer-schedule-title"', read("find/index.html"))
        historical = json.loads(read("downloads/portland-meadows-ep1-scene-claims.json"))
        self.assertFalse(historical["current_public_cut_graphics_checked"])
        self.assertFalse(historical["human_release_approval"])

if __name__ == "__main__":
    unittest.main()
