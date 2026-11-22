"""PBG-06: candidate poker search intents, one primary URL per question family.

All tests are offline. No Search Console or public query volume is inferred.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import poker_beginner_intent_map as route

def evidence() -> dict:
    return json.loads((ROOT / route.MAP).read_text(encoding="utf-8"))

def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class PokerBookIntentTests(unittest.TestCase):
    def test_current_repo_audit_resolves_all_primary_and_secondary_urls(self):
        summary = route.audit(ROOT)
        self.assertEqual(summary["status"], "pass", summary["errors"])
        self.assertEqual(summary["intent_count"], 18)
        self.assertTrue(all(x["source_canonical_present"]
                            for x in summary["checked_routes"]))

    def test_18_separate_intents_have_one_exact_primary_owner(self):
        data = evidence()
        self.assertEqual(route.validate_data(data), [])
        clusters = data["clusters"]
        self.assertEqual(len(clusters), 18)
        self.assertEqual(len({x["id"] for x in clusters}), 18)
        self.assertEqual(len({x["primary"] for x in clusters}), 18)
        self.assertEqual(len({q.lower() for x in clusters
                              for q in x["candidate_questions"]}), 36)

    def test_no_search_clicks_volume_position_or_ai_citations_are_invented(self):
        data = evidence()
        self.assertEqual(data["measurement"]["status"], "not_collected")
        for key in route.OBSERVED_FIELDS:
            self.assertIsNone(data["measurement"][key])
        for item in data["clusters"]:
            for key in ("measured_search_clicks", "measured_impressions",
                        "measured_ai_citations"):
                self.assertIsNone(item[key])
        summary = route.audit(ROOT)
        self.assertIsNone(summary["private_search_data"])
        self.assertIsNone(summary["observed_ai_citations"])

    def test_distinct_book_shop_and_study_answers_avoid_duplicate_targets(self):
        by_id = {x["id"]: x for x in evidence()["clusters"]}
        for id, destination in route.EXPECTED_OWNERS.items():
            self.assertEqual(by_id[id]["primary"], destination)
        self.assertEqual(by_id["book-course-selection"]["secondary"],
                         "/poker/free-poker-learning-path/")
        self.assertEqual(by_id["nolan-book-navigation"]["secondary"],
                         "/poker/poker-books-and-courses/")

    def test_book_choice_page_has_five_actual_native_free_routes(self):
        source = text(route.COURSES)
        published = text(route.PUBLIC)
        self.assertEqual(route.comparison_choice(source),
                         route.comparison_choice(published))
        self.assertEqual(route.LinkReader(route.comparison_choice(source)).links,
                         list(route.FREE_ROUTES))
        for href in route.FREE_ROUTES:
            self.assertIn('href="' + href + '"', route.comparison_choice(source))
            self.assertTrue((ROOT / href.lstrip("/") / "index.html").is_file())
        self.assertNotIn("data-umami-event", route.comparison_choice(source))

    def test_author_book_link_and_original_site_sample_are_not_duplicated(self):
        page = text(route.PUBLIC)
        book = "/books/how-to-play-no-limit-texas-holdem/"
        self.assertEqual(page.count('href="' + book + '"'), 1)
        self.assertEqual(page.count('href="' + book + '#poker-book-first-exercise"'), 1)
        self.assertEqual(page.count('href="/downloads/holdem-river-call-check-worksheet.md"'), 1)
        self.assertIn("not an independent review", page)
        self.assertIn('id="compare-before-paying"', page)
        self.assertIn("No purchase is necessary", page)

    def test_an_unrelated_primary_collision_is_detected(self):
        data = evidence()
        data["clusters"][1]["primary"] = data["clusters"][0]["primary"]
        self.assertTrue(route.validate_data(data))

    def test_broken_author_book_owner_is_detected(self):
        data = evidence()
        target = next(x for x in data["clusters"]
                      if x["id"] == "nolan-book-navigation")
        target["primary"] = "/poker/poker-books-and-courses/"
        self.assertTrue(route.validate_data(data))

    def test_fake_positive_clicks_and_csv_zero_are_detected(self):
        for value in (0, 1, "10", None):
            if value is None:
                continue
            with self.subTest(value=value):
                data = evidence()
                data["measurement"]["gsc_clicks"] = value
                self.assertTrue(route.validate_data(data))
        data = evidence()
        data["clusters"][0]["measured_ai_citations"] = 0
        self.assertTrue(route.validate_data(data))

    def test_duplicate_or_malformed_candidate_question_is_detected(self):
        data = evidence()
        data["clusters"][1]["candidate_questions"][0] = (
            data["clusters"][0]["candidate_questions"][0])
        self.assertTrue(route.validate_data(data))
        data = evidence()
        data["clusters"][0]["candidate_questions"][0] = "poker"
        self.assertTrue(route.validate_data(data))

    def test_competitor_sample_is_bounded_and_not_scoring_claim(self):
        data = evidence()
        c = data["external_context"]
        self.assertTrue(c["qualitative_only"])
        self.assertEqual(c["sampled_on"], "2026-11-22")
        self.assertGreaterEqual(len(c["examples"]), 2)
        self.assertIn("not a rank", c["limits"].lower())
        self.assertNotIn("B0HSB98324", text(route.PUBLIC))

    def test_release_checks_register_intent_map_and_keep_ci_off(self):
        runner = text("_scripts/local_release_checks.py")
        self.assertIn("test_pbg06_beginner_intent_map.py", runner)
        self.assertIn("_scripts/poker_beginner_intent_map.py", runner)
        self.assertIn("['_scripts/build.py', '--check']", runner)
        workflows = ROOT / ".github/workflows"
        self.assertFalse(workflows.exists() and any(
            p.suffix.lower() in {".yaml", ".yml"} for p in workflows.iterdir()))


if __name__ == "__main__":
    unittest.main()
