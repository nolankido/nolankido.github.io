"""Turn 60: a complete, card-filtered Bayes formula instead of a dangling colon.

The prior/action-likelihood example and evidence JSON are fictional. This
checks model arithmetic, not actual opponent frequencies or a solver output.
"""
from fractions import Fraction as F
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source/poker/poker-under-uncertainty.html"
PUBLIC = ROOT / "poker/poker-under-uncertainty/index.html"
EVIDENCE = ROOT / "downloads/poker-under-uncertainty-evidence.json"
ROUTE = "/poker/poker-under-uncertainty/"
FORMULA = "bayes-range-update-formula"
CHECK = "bayes-range-update-check"
REPRO = "/downloads/poker-under-uncertainty-reproduce.py"


class Tags(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def section_text(html, identifier):
    paragraphs = re.findall(r'<p id="' + re.escape(identifier) + r'">(.*?)</p>',
                            html, re.S)
    if len(paragraphs) != 1:
        raise ValueError("Missing or repeated Bayesian explanation")
    return paragraphs[0]


def problems(html):
    errors = []
    try:
        f = section_text(html, FORMULA)
        c = section_text(html, CHECK)
    except ValueError as exc:
        return [str(exc)]
    for term in (
        "posterior_i", "prior_i(K)", "likelihood_i(K)",
        "sum_j [prior_j(K) × likelihood_j(K)]",
        "known cards", "blocked holdings", "zero prior weight",
    ):
        if term not in f:
            errors.append("Missing Bayesian formula term: " + term)
    for term in (
        "0.30 / 0.45 / 0.25", "0.80 / 0.60 / 0.20",
        "0.24 / 0.27 / 0.05", "0.56", "3/7, 27/56 and 5/56",
        "sum to one", "not observed opponent frequencies", REPRO,
    ):
        if term not in c:
            errors.append("Missing or incorrect worked check: " + term)
    if not re.search(
        r"The range-update process can be represented as:</p>\s*<p id="
        r"\"bayes-range-update-formula\">", html,
    ):
        errors.append("The original unfinished formula remains unconnected")
    return errors


class BayesianRangeUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = SOURCE.read_text(encoding="utf-8")
        cls.pub = PUBLIC.read_text(encoding="utf-8")
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))["bayes"]

    def test_exact_three_class_example_reproduced_independently(self):
        prior = [F(x) for x in self.evidence["prior"]]
        likelihood = [F(x) for x in self.evidence["likelihood"]]
        masses = [p * l for p, l in zip(prior, likelihood)]
        self.assertEqual(prior, [F(3, 10), F(9, 20), F(1, 4)])
        self.assertEqual(likelihood, [F(4, 5), F(3, 5), F(1, 5)])
        self.assertEqual(masses, [F(6, 25), F(27, 100), F(1, 20)])
        total = sum(masses)
        self.assertEqual(total, F(14, 25))
        posterior = [weight / total for weight in masses]
        self.assertEqual(posterior, [F(3, 7), F(27, 56), F(5, 56)])
        self.assertEqual([F(x) for x in self.evidence["posterior"]], posterior)
        self.assertEqual(sum(posterior), 1)

    def test_impossible_blocked_hand_gets_zero_weight_before_action(self):
        # Fully synthetic combination counts, distinct from the published bet.
        remaining_combos = (3, 4, 0)
        likelihoods = (F(4, 5), F(3, 5), F(1, 5))
        masses = [n * p for n, p in zip(remaining_combos, likelihoods)]
        self.assertEqual(masses, [F(12, 5), F(12, 5), F(0)])
        normal = [mass / sum(masses) for mass in masses]
        self.assertEqual(normal, [F(1, 2), F(1, 2), F(0)])
        self.assertEqual(sum(normal), 1)

    def test_a_complete_formula_is_published_with_exact_source_parity(self):
        for page in (self.src, self.pub):
            self.assertEqual(problems(page), [])
            tags = Tags(page)
            self.assertEqual(tags.ids.count(FORMULA), 1)
            self.assertEqual(tags.ids.count(CHECK), 1)
            self.assertGreaterEqual(tags.links.count(REPRO), 1)
            self.assertNotIn("solver-approved", page)
        for section in (FORMULA, CHECK):
            self.assertEqual(section_text(self.src, section),
                             section_text(self.pub, section))

    def test_original_math_assets_and_research_boundaries_are_preserved(self):
        self.assertEqual(self.src.count("<math "), 190)
        self.assertEqual(self.pub.count("<math "), 190)
        self.assertEqual((self.src.count("<h2 "), self.pub.count("<h2 ")), (16, 17))
        self.assertIn("not a peer-reviewed research paper", self.src)
        self.assertIn("The deeper lesson is that a blocker", self.src)
        self.assertNotIn(chr(0x2014), section_text(self.src, FORMULA))
        self.assertNotIn("<iframe", section_text(self.src, CHECK))

    def test_current_revision_preserves_original_date_and_minutes(self):
        item = next(p for p in json.loads(read("_source/pages.json"))
                    if p["path"] == ROUTE)
        self.assertEqual((item["date"], item["updated"]),
                         ("2026-10-14", "2026-11-20"))
        self.assertIn('"datePublished": "2026-10-14"', self.pub)
        self.assertIn('"dateModified": "2026-11-20"', self.pub)
        self.assertIn('article:modified_time" content="2026-11-20"', self.pub)
        self.assertIn("About 50 min read", self.pub)
        self.assertIn('Updated <time datetime="2026-11-20">November 20, 2026</time>', self.pub)
        library = read("poker/library/index.html")
        strategy = read("poker/topics/strategy/index.html")
        self.assertIn("About 50 min read", library)
        self.assertIn('href="' + ROUTE + '">Poker under uncertainty: probability, inference and decisions</a>'
                      '<span class="topic-meta">Go deeper · About 50 min</span>', strategy)
        xml = ET.fromstring(read("sitemap.xml"))
        rows = [e for e in xml if e.findtext("{*}loc") == "https://nolankido.com" + ROUTE]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].findtext("{*}lastmod"), "2026-11-20")

    def test_historical_predecessor_suite_still_checks_unmodified_evidence(self):
        old = read("_tests/test_uncertainty.py")
        self.assertIn("history.pages([p for p in self.pages if p['path'] != ROUTE])", old)
        self.assertIn("if p != build.output_path(ROUTE)", old)
        self.assertIn("changed=dict(self.outputs)", old)
        self.assertIn("history.outputs(changed)", old)
        self.assertIn("self.assertEqual(len(math),190)", old)
        self.assertIn("self.assertEqual(len(list(self.main.iter('table'))),11)", old)

    def test_negative_controls_detect_missing_formula_and_drifted_posterior(self):
        cases = (
            self.src.replace('id="bayes-range-update-formula"',
                             'id="omitted-math"', 1),
            self.src.replace("sum_j [prior_j(K) × likelihood_j(K)]",
                             "sum_j prior_j(K)", 1),
            self.src.replace("3/7, 27/56 and 5/56",
                             "3/7, 28/56 and 5/56", 1),
            self.src.replace('href="' + REPRO + '"',
                             'href="/downloads/nonexistent.py"', 1),
            self.src.replace("zero prior weight", "nonzero prior weight", 1),
        )
        for value in cases:
            self.assertNotEqual(value, self.src)
            self.assertTrue(problems(value))

    def test_registered_offline_without_repository_workflows(self):
        checks = read("_scripts/local_release_checks.py")
        self.assertIn("test_turn60_bayes_update.py", checks)
        p = ROOT / ".github/workflows"
        self.assertFalse(p.exists() and any(
            x.is_file() and x.suffix in (".yml", ".yaml") for x in p.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
