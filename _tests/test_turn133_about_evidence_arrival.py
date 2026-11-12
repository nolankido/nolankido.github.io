"""Turn 133: linked About evidence opens onto proof, then honest limits."""

from hashlib import sha256
import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build


DESTINATION = "/about/#about-evidence-title"
HEADING = '<h2 id="about-evidence-title">A few things you can verify</h2>'
CARDS = '<div class="identity-readings about-evidence-list">'
EXPLANATION = '<p>There are different kinds of evidence behind my work.'
BOUNDARIES = (
    "None of these is a substitute for judging the work itself.",
    "The research concerns governmental accounting, not AI performance.",
    "The AI examples are bounded demonstrations, not audited business outcomes.",
    "Tournament cashes are gross results, not profit.",
)
CASE_SLUGS = (
    "local-ai-review-replies",
    "ai-book-continuity-checker",
    "ai-poker-video-evidence",
)


def arrival_errors(html: str) -> list[str]:
    errors = []
    section = re.search(
        r'<section class="about-evidence" aria-labelledby="about-evidence-title">(.*?)</section>',
        html, re.S,
    )
    if not section:
        return ["bounded evidence section missing"]
    body = section.group(1)
    if body.count(HEADING) != 1 or body.count(CARDS) != 1 or body.count(EXPLANATION) != 1:
        return ["heading, card grid or explanation missing or duplicated"]
    if not body.split(HEADING, 1)[1].lstrip().startswith(CARDS):
        errors.append("source-linked evidence cards are no longer first after the heading")
    end_cards = body.find("</div>", body.find(CARDS))
    if not (body.find(CARDS) < end_cards < body.find(EXPLANATION)):
        errors.append("explanation interrupts or precedes the evidence cards")
    if body.count('<article class="identity-reading">') != 3:
        errors.append("changed number of independently differentiated evidence cards")
    for url in (
        "https://onlinelibrary.wiley.com/doi/10.1111/j.1475-679X.2012.00447.x",
        "/technology/local-ai-review-replies/",
        "/poker/nolan-kido/#player-record-title",
    ):
        if body.count('href="' + url + '"') != 1:
            errors.append("missing or repeated published evidence route: " + url)
    for fact in BOUNDARIES:
        if body.count(fact) != 1:
            errors.append("evidence limit missing or altered: " + fact)
    if "\u2014" in body:
        errors.append("prohibited em dash in visible evidence")
    return errors


def target_style_errors(css: str) -> list[str]:
    selector = ".page-about #about-evidence-title:target"
    blocks = re.findall(re.escape(selector) + r"\s*\{([^}]*)\}", css, re.S)
    if len(blocks) != 1:
        return ["missing or duplicate About-only target highlight"]
    block = blocks[0]
    if "outline: 2px solid var(--red);" not in block or "outline-offset: 4px;" not in block:
        return ["target does not visibly distinguish the evidence heading"]
    if ".page-about h2[id] { scroll-margin-top: 2rem; }" not in css:
        return ["desktop native arrival offset missing"]
    if ".page-about h2[id] { scroll-margin-top: 7rem; }" not in css:
        return ["mobile native arrival offset missing"]
    return []


class AboutEvidenceArrivalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/about.html").read_text(encoding="utf-8")
        cls.public = (ROOT / "about/index.html").read_text(encoding="utf-8")
        cls.css_path = ROOT / "assets/about-reader.css"
        cls.css = cls.css_path.read_text(encoding="utf-8")

    def test_source_and_public_page_lead_with_three_real_evidence_cards(self):
        for page in (self.source, self.public):
            self.assertEqual(arrival_errors(page), [])
            self.assertEqual(page.count('id="about-evidence-title"'), 1)
            self.assertIn('href="#about-evidence-title">Evidence</a>', page)

    def test_new_case_links_land_on_visible_unchanged_about_section(self):
        for slug in CASE_SLUGS:
            for article in (
                ROOT / "_source/technology" / (slug + ".html"),
                ROOT / "technology" / slug / "index.html",
            ):
                with self.subTest(slug=slug, article=str(article.relative_to(ROOT))):
                    self.assertEqual(article.read_text(encoding="utf-8").count('href="' + DESTINATION + '"'), 1)
        self.assertEqual(self.public.count(HEADING), 1)

    def test_scoped_target_style_and_content_versioned_about_page(self):
        self.assertEqual(target_style_errors(self.css), [])
        version = sha256(self.css_path.read_bytes()).hexdigest()[:12]
        self.assertIn(f'href="/assets/about-reader.css?v={version}"', self.public)
        self.assertNotIn("/assets/about-reader.css", (ROOT / "technology/index.html").read_text())

    def test_preserved_identity_dates_and_negative_controls(self):
        self.assertEqual(build.build_outputs()[Path("about/index.html")], self.public)
        pages = {p["path"]: p for p in json.loads((ROOT / "_source/pages.json").read_text())}
        self.assertEqual(pages["/about/"]["updated"], "2026-11-06")
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text())
        dates = {n.findtext("{*}loc"): n.findtext("{*}lastmod") for n in sitemap}
        self.assertEqual(dates["https://nolankido.com/about/"], "2026-11-06")
        self.assertIn('"@id": "https://nolankido.com/about/#nolan-kido"', self.public)
        explanation = re.search(re.escape(EXPLANATION) + r".*?</p>", self.source).group(0)
        backwards = self.source.replace(explanation, "", 1).replace(HEADING, HEADING + explanation, 1)
        broken = self.source.replace(BOUNDARIES[1], "Research proves AI productivity.", 1)
        self.assertTrue(arrival_errors(backwards))
        self.assertTrue(arrival_errors(broken))
        self.assertTrue(target_style_errors(self.css.replace(":target", ":hover", 1)))


if __name__ == "__main__":
    unittest.main()
