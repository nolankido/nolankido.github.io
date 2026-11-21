"""Turn 59: cross-check each personal gross cash against this event's payout ladder.

The same invented $39,600 ten-place payout table must supply the prize used
in both the one-entry and two-entry net-cash teaching cases. No real receipts.
"""
from decimal import Decimal as D
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source/poker/tournament-entry-prize-pool-ledger.html"
PUBLIC = ROOT / "poker/tournament-entry-prize-pool-ledger/index.html"
ROUTE = "/poker/tournament-entry-prize-pool-ledger/"
ANCHOR = "ledger-personal-cash-check"
PERSONAL_RESULTS = (
    "$1,000 − $800 − $60 = +$140",
    "$1,000 − $400 − $60 = +$540",
)


class Anchors(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.ids, self.hrefs = [], []
        self.feed(raw)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def payout_table(page):
    """Read only the actual ten-place table, not unrelated amounts in prose."""
    section = re.search(
        r'<h2 id="ledger-payouts">.*?(?=<h2 id="ledger-bounty">)',
        page, re.S,
    )
    if not section:
        raise ValueError("the named payout table is missing")
    rows = re.findall(
        r'<th scope="row">(\d+)(?:st|nd|rd|th)</th>'
        r'<td>\$([\d,]+)</td>',
        section.group(0),
    )
    prizes = {int(position): D(amount.replace(",", "")) for position, amount in rows}
    if len(rows) != 10 or set(prizes) != set(range(1, 11)):
        raise ValueError("payout table must contain one award for places 1 to 10")
    return prizes


def personal_paragraph(page):
    pieces = re.findall(
        r'<p id="ledger-personal-cash-check">(.*?)</p>', page, re.S,
    )
    if len(pieces) != 1:
        raise ValueError("expected one linked personal cash calculation")
    return pieces[0]


def consistency_errors(page):
    errors = []
    try:
        prizes = payout_table(page)
        first = personal_paragraph(page)
    except ValueError as exc:
        return [str(exc)]
    if sum(prizes.values()) != D(39600):
        errors.append("ordinary prize pool no longer balances")
    if min(prizes.values()) != D(1000) or prizes[10] != D(1000):
        errors.append("tenth-place prize differs from personal award")
    if "tenth-place gross finishing prize" not in first or "$1,000" not in first:
        errors.append("personal example is not the actual listed tenth-place cash")
    for formula in PERSONAL_RESULTS:
        if formula not in page:
            errors.append("missing or incorrect personal cash arithmetic: " + formula)
    if "$950" in page or "+$90" in page or "+$490" in page:
        errors.append("obsolete payout incompatible with the ten-place ladder")
    if "−$860" not in first:
        errors.append("zero-payout loss was changed incorrectly")
    if Anchors(page).hrefs.count("#" + ANCHOR) != 1:
        errors.append("payout table does not link to its personal cash check")
    quiz = re.search(
        r'<summary>A player receives the example.s \$1,000 tenth-place award'
        r'.*?</summary><div><p>.*?</p></div></details>',
        page, re.S,
    )
    if not quiz or "No. The modeled pre-tax result is +$140" not in quiz.group(0):
        errors.append("practice question has the wrong gross or net payout")
    return errors


class ConsistentTournamentPayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.public = PUBLIC.read_text(encoding="utf-8")

    def test_all_ten_awards_sum_to_base_pool_and_tenth_is_minimum(self):
        for page in (self.source, self.public):
            amounts = payout_table(page)
            self.assertEqual(sum(amounts.values()), D(39600))
            self.assertEqual(amounts[10], D(1000))
            self.assertEqual(min(amounts.values()), amounts[10])
            self.assertEqual(len(amounts), 10)
            self.assertEqual(consistency_errors(page), [])

    def test_one_and_two_entry_cash_results_use_same_schedule(self):
        gross = payout_table(self.source)[10]
        price = D(400)
        trip = D(60)
        self.assertEqual((gross - 2 * price - trip,
                          gross - price - trip,
                          D(0) - 2 * price - trip), (D(140), D(540), D(-860)))
        for page in (self.source, self.public):
            self.assertIn("A hypothetical person who used only one $400 entry", page)
            self.assertIn("two $400 entries and $60 in trip costs", page)
            for formula in PERSONAL_RESULTS:
                self.assertIn(formula, page)
            self.assertNotIn("$950", page)
            self.assertIn("private finances", page)

    def test_single_source_and_published_same_personal_text_and_link(self):
        self.assertEqual(personal_paragraph(self.source),
                         personal_paragraph(self.public))
        for page in (self.source, self.public):
            self.assertEqual(Anchors(page).ids.count(ANCHOR), 1)
            self.assertEqual(Anchors(page).hrefs.count("#" + ANCHOR), 1)
            self.assertEqual(page.count('class="poker-details viewer-question"'), 8)
            self.assertIn("not a real event", page)
        self.assertEqual((self.source.count("<h2 "), self.public.count("<h2 ")),
                         (10, 11))
        self.assertNotIn(chr(0x2014), self.source)

    def test_original_publication_updated_article_date_and_sitemap(self):
        pages = json.loads(read("_source/pages.json"))
        record = next(p for p in pages if p["path"] == ROUTE)
        self.assertEqual((record["date"], record["updated"]),
                         ("2026-11-15", "2026-11-20"))
        self.assertIn('"datePublished": "2026-11-15"', self.public)
        self.assertIn('"dateModified": "2026-11-20"', self.public)
        self.assertIn('article:published_time" content="2026-11-15"', self.public)
        self.assertIn('article:modified_time" content="2026-11-20"', self.public)
        self.assertIn("About 12 min read", self.public)
        self.assertIn('datetime="2026-11-15"', self.source)
        self.assertIn('datetime="2026-11-20"', self.source)
        sitemap = ET.fromstring(read("sitemap.xml"))
        row = [x for x in sitemap if x.findtext("{*}loc") ==
               "https://nolankido.com" + ROUTE]
        self.assertEqual(len(row), 1)
        self.assertEqual(row[0].findtext("{*}lastmod"), "2026-11-20")
        feed = read("poker/feed.xml")
        self.assertIn("<pubDate>Sun, 15 Nov 2026 00:00:00 GMT</pubDate>", feed)

    def test_negative_controls_catch_bad_awards_and_bad_nets(self):
        cases = (
            self.source.replace("$1,000 − $800 − $60 = +$140",
                                "$950 − $800 − $60 = +$90", 1),
            self.source.replace("$1,000 − $400 − $60 = +$540",
                                "$1,000 − $400 − $60 = +$490", 1),
            self.source.replace(
                '<th scope="row">10th</th><td>$1,000</td>',
                '<th scope="row">10th</th><td>$950</td>', 1),
            self.source.replace('href="#ledger-personal-cash-check"',
                                'href="#missing-check"', 1),
            self.source.replace("No. The modeled pre-tax result is +$140",
                                "No. The modeled pre-tax result is +$90", 1),
        )
        for altered in cases:
            with self.subTest(different=altered != self.source):
                self.assertNotEqual(altered, self.source)
                self.assertTrue(consistency_errors(altered))

    def test_registered_manual_release_without_repo_authored_actions(self):
        runner = read("_scripts/local_release_checks.py")
        self.assertIn("test_turn59_payout_consistency.py", runner)
        actions = ROOT / ".github/workflows"
        self.assertFalse(actions.exists() and any(
            x.is_file() and x.suffix in (".yml", ".yaml")
            for x in actions.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
