"""PBG-02: offline, aggregate-only poker book acquisition checks."""
import io
import json
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import poker_book_growth_scorecard as score


def observation():
    return {
        "month": "2026-11",
        "property": "nolankido.com",
        "period_verified": True,
        "pageviews": {"/books/": 20,
                      "/books/how-to-play-no-limit-texas-holdem/": 8},
        "events": {
            "poker-book-kindle-amazon-click": {
                "books-catalog": 3, "book-page-hero": 2},
            "one-workflow-kindle-amazon-click": {
                "books-catalog": 1},
            "ai-works-human-decides-kindle-amazon-click": {
                "books-catalog": 0},
        },
    }


class BookBaselineTests(unittest.TestCase):
    def test_missing_is_nullable_not_fake_zero(self):
        result = score.summarize("2026-11")
        self.assertEqual(result["collection"], "not_collected")
        self.assertIsNone(result["pageviews"]["/books/"])
        self.assertIsNone(result["poker_all_placements_total_when_complete"])
        self.assertIsNone(result["poker_book_page_events_per_100_pageviews"])
        self.assertTrue(all(v is None for v in result["unmeasured"].values()))

    def test_complete_aggregate_tracks_events_without_claiming_sales(self):
        result = score.summarize("2026-11", observation())
        self.assertEqual(result["pageviews"]["/books/"], 20)
        self.assertEqual(result["poker_all_placements_total_when_complete"], 5)
        self.assertEqual(result["poker_book_page_events_per_100_pageviews"], 25)
        self.assertEqual(result["amazon_click_events"][
            "ai-works-human-decides-kindle-amazon-click"]["books-catalog"], 0)
        self.assertIsNone(result["unmeasured"]["amazon_book_orders"])

    def test_missing_one_source_cannot_be_summed_as_zero(self):
        obj = observation()
        del obj["events"]["poker-book-kindle-amazon-click"]["books-catalog"]
        result = score.summarize("2026-11", obj)
        self.assertIsNone(result["poker_all_placements_total_when_complete"])
        self.assertEqual(result["amazon_click_events"][
            "poker-book-kindle-amazon-click"]["book-page-hero"], 2)

    def test_zero_pageviews_does_not_produce_fake_rate(self):
        obj = observation()
        obj["pageviews"]["/books/how-to-play-no-limit-texas-holdem/"] = 0
        self.assertIsNone(score.summarize("2026-11", obj)[
            "poker_book_page_events_per_100_pageviews"])

    def test_repeated_click_rate_can_exceed_one_hundred(self):
        obj = observation()
        obj["events"]["poker-book-kindle-amazon-click"]["book-page-hero"] = 9
        self.assertEqual(score.summarize("2026-11", obj)[
            "poker_book_page_events_per_100_pageviews"], 112.5)

    def test_invalid_month_and_property_are_rejected(self):
        for month in ("2026-00", "2026-13", "today", "2026-11-01"):
            with self.subTest(month=month), self.assertRaises(score.ScorecardError):
                score.summarize(month)
        obj = observation()
        obj["property"] = "example.com"
        with self.assertRaises(score.ScorecardError):
            score.summarize("2026-11", obj)

    def test_report_period_must_be_explicitly_verified(self):
        obj = observation()
        obj["period_verified"] = False
        with self.assertRaises(score.ScorecardError):
            score.summarize("2026-11", obj)
        obj = observation()
        obj["month"] = "2026-10"
        with self.assertRaises(score.ScorecardError):
            score.summarize("2026-11", obj)

    def test_unknown_event_source_private_keys_and_bool_are_refused(self):
        bad = []
        a = observation()
        a["events"]["ai-works-human-decides-kindle-amazon-click"]["book-page-hero"] = 3
        bad.append(a)
        a = observation()
        a["events"]["poker-book-kindle-amazon-click"]["books-catalog"] = True
        bad.append(a)
        a = observation()
        a["user_email"] = "private@example.invalid"
        bad.append(a)
        a = observation()
        a["events"]["signup-with-email"] = {"books-catalog": 1}
        bad.append(a)
        for i, obj in enumerate(bad):
            with self.subTest(i=i), self.assertRaises(score.ScorecardError):
                score.summarize("2026-11", obj)

    def test_cli_missing_input_never_fabricates_counts(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = score.main(["--month", "2026-11"])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(data["collection"], "not_collected")
        self.assertIsNone(data["amazon_click_events"][
            "poker-book-kindle-amazon-click"]["book-page-hero"])

    def test_source_links_are_exact_and_privacy_notice_is_truthful(self):
        destinations = {
            "books/index.html": {
                "poker-book-kindle-amazon-click": "B0HSB98324",
                "one-workflow-kindle-amazon-click": "B0HRQNCP7Y",
                "ai-works-human-decides-kindle-amazon-click": "B0HSF8K76R",
            },
            "books/how-to-play-no-limit-texas-holdem/index.html": {
                "poker-book-kindle-amazon-click": "B0HSB98324",
            },
            "books/one-workflow-at-a-time/index.html": {
                "one-workflow-kindle-amazon-click": "B0HRQNCP7Y",
            },
        }
        for relative, mapping in destinations.items():
            html = (ROOT / relative).read_text(encoding="utf-8")
            for event, asin in mapping.items():
                with self.subTest(path=relative, event=event):
                    self.assertEqual(html.count('data-umami-event="' + event + '"'), 1)
                    self.assertIn(asin, html)
            self.assertNotIn("umami.identify(", html)
        privacy = (ROOT / "privacy/index.html").read_text(encoding="utf-8")
        self.assertIn("limited Amazon book-link click events", privacy)
        self.assertIn("A click is not proof of an Amazon purchase", privacy)


if __name__ == "__main__":
    unittest.main()
