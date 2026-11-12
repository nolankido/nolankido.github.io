"""The homepage identifies published research without borrowing its authority for AI."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = "https://onlinelibrary.wiley.com/doi/10.1111/j.1475-679X.2012.00447.x"
MANUSCRIPT = "https://dspace.mit.edu/entities/publication/9e5c8e82-34b0-4931-a8cc-6ea0ae938829"
TITLE = "The Influence of Elections on the Accounting Choices of Governmental Entities."


class HomepageResearchSourceTests(unittest.TestCase):
    def test_homepage_research_card_has_identifiable_public_sources(self):
        for path in ["_source/home.html", "index.html"]:
            with self.subTest(path=path):
                html = (ROOT / path).read_text(encoding="utf-8")
                start = html.index('Research / Publisher record')
                end = html.index('Practical AI / Reproducible audit', start)
                card = html[start:end]
                self.assertIn(f'<a href="{PUBLISHER}">{TITLE}</a>', card)
                self.assertIn("Reining Petacchi and Joseph Weber", card)
                self.assertIn("<em>Journal of Accounting Research</em> in 2012", card)
                self.assertIn(f'<a href="{MANUSCRIPT}">Read the author\'s manuscript at MIT</a>', card)
                self.assertIn("state-government accounting around gubernatorial elections", card)
                self.assertIn("not evidence that my AI projects work", card)
                self.assertNotIn("\u2014", card)

    def test_research_and_project_evidence_stay_distinct(self):
        html = (ROOT / "_source/home.html").read_text(encoding="utf-8")
        section = html.split('id="home-proof-title"', 1)[1].split('id="selected-reading-title"', 1)[0]
        self.assertEqual(section.count('class="identity-reading"'), 3)
        self.assertIn('href="/technology/review-reply-evidence-audit/"', section)
        self.assertIn('href="/poker/nolan-kido/"', section)
        self.assertEqual(section.count(PUBLISHER), 1)
        self.assertEqual(section.count(MANUSCRIPT), 1)


if __name__ == "__main__":
    unittest.main()
