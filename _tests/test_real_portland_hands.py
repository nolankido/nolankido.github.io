"""Two real narrated poker decision records, separated from later analysis."""
from fractions import Fraction
from pathlib import Path
from html.parser import HTMLParser
import unittest
from test_site import ROOT

URL = "/poker/episodes/portland-meadows-ep1/"
SOURCE = ROOT / "_source/poker/portland-meadows-ep1.html"
HTML = ROOT / "poker/episodes/portland-meadows-ep1/index.html"


class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.ids = {}
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids[attrs["id"]] = self.ids.get(attrs["id"], 0) + 1
        if tag == "a":
            self.links.append(attrs.get("href"))


class RealHandRecordsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.published = HTML.read_text(encoding="utf-8")
        cls.dom = Elements(cls.published)

    def test_two_unique_source_embedded_hand_accounts_and_separate_video_offsets(self):
        self.assertIn(self.source, self.published)
        for anchor in ("hand-64o-record", "hand-77-record",
                       "six-four-decision", "sevens-decision"):
            self.assertEqual(self.dom.ids.get(anchor), 1, anchor)
        self.assertIn("https://www.youtube.com/watch?v=JToB7upHqEM&t=368s", self.dom.links)
        self.assertIn("https://www.youtube.com/watch?v=JToB7upHqEM&t=540s", self.dom.links)
        self.assertIn("The exact tournament calendar date is not established", self.source)
        self.assertIn("The precise tournament calendar date is not independently documented", self.source)

    def test_arithmetic_is_correct_and_does_not_pretend_to_be_a_solver(self):
        self.assertAlmostEqual(float(Fraction(148000, 15000)), 9.87, delta=0.01)
        self.assertEqual(Fraction(585000, 30000), Fraction(39, 2))
        self.assertEqual(Fraction(75000, 30000), Fraction(5, 2))
        for value in ("148,000 / 15,000 = 9.87", "585,000 / 30,000 = 19.5",
                      "75,000 total, or 2.5 BB", "$2,900", "$5,100"):
            self.assertIn(value, self.source)
        for uncertainty in ("not a verified solver result", "complete board",
                            "payout", "calling range", "not a profitability estimate"):
            # A missing full showdown history is a documented limitation.
            self.assertIn(uncertainty, self.source)
        self.assertNotIn("\u2014", self.source)

    def test_poker_hub_and_person_link_to_both_record_anchors(self):
        hub = (ROOT / "poker/index.html").read_text(encoding="utf-8")
        person = (ROOT / "poker/nolan-kido/index.html").read_text(encoding="utf-8")
        for fragment in ("#hand-64o-record", "#hand-77-record"):
            self.assertIn('href="' + URL + fragment + '"', hub)
            self.assertIn('href="' + URL + fragment + '"', person)
            self.assertIn('href="' + fragment + '"', self.source)
        self.assertIn("Video companions", (ROOT / "find/index.html").read_text())
        self.assertNotIn("JToB7upHqEM", (ROOT / "_source/poker/catalog.json").read_text())

    def test_no_invented_suits_board_or_private_solver_results(self):
        for forbidden in ("6♠4♥", "6h4c", "any two cards are GTO", "certified ICM",
                          "opponent's exact range is", "full board was"):
            self.assertNotIn(forbidden, self.source)
        self.assertNotIn("<iframe", self.published)
        self.assertNotIn("<form", self.published)


if __name__ == "__main__":
    unittest.main()
