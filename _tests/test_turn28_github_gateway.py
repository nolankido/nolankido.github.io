"""Public GitHub README should lead to actual Nolan Kido work and never suggest forbidden CI."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GithubGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.rules = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    def test_first_screen_centers_name_real_ai_work_and_author_home(self):
        text = self.readme
        self.assertTrue(text.startswith("# Nolan Kido | AI Works, Human Decides\n"))
        start = text.split("## Beginner Poker course", 1)[0]
        self.assertIn("https://nolankido.com/about/", start)
        self.assertIn("https://nolankido.com/technology/local-ai-review-replies/", start)
        self.assertIn("https://nolankido.com/technology/ai-book-continuity-checker/", start)
        self.assertIn("https://nolankido.com/technology/checking-ai-website-changes/", start)
        self.assertIn("https://nolankido.com/poker/nolan-kido/", start)
        self.assertIn("https://doi.org/10.1111/j.1475-679X.2012.00447.x", start)
        self.assertIn("incorrect flags", start)
        self.assertIn("not of AI-product performance", start)
        self.assertIn("not a current university appointment", start)
        self.assertNotIn("AI Startup Founder and Angel Investor", start)
        self.assertNotIn("MIT Research Affiliate", start)
        self.assertNotIn("\u2014", start)

    def test_local_project_cases_and_anchors_really_exist(self):
        cases = {
            "technology/local-ai-review-replies/index.html": "Review Reply Writer",
            "technology/ai-book-continuity-checker/index.html": "Preflight",
            "technology/checking-ai-website-changes/index.html": "347 passing tests",
            "technology/index.html": 'id="identity-claim-audit"',
            "poker/nolan-kido/index.html": "Nolan Kido",
            "about/index.html": "About Nolan Kido",
        }
        for route, fact in cases.items():
            with self.subTest(route=route):
                html = (ROOT / route).read_text(encoding="utf-8")
                self.assertIn(fact, html)

    def test_readme_no_longer_promises_current_workflows_or_auto_indexnow(self):
        text = self.readme
        self.assertIn("no repository-authored GitHub Actions workflows", text)
        self.assertIn("former `site-checks.yml` was intentionally removed", text)
        self.assertIn("No scheduled IndexNow notification", text)
        self.assertIn("python _scripts/build.py --check", text)
        self.assertIn("python _scripts/check_search.py", text)
        self.assertIn("python _tests/check_html5.py", text)
        self.assertIn("python _scripts/check_live.py", text)
        for wrong in (
            "The `Site checks` workflow uses",
            "Both are in Site checks",
            "The search checker runs in Site checks",
            "It is added to Site checks",
            "The notification receipt is retained as an Actions artifact",
            "The full hosted gate includes",
        ):
            self.assertNotIn(wrong, text)
        self.assertIn("Do not create, restore, enable, dispatch, rely on, or use GitHub Actions", self.rules)

    def test_readme_still_keeps_developer_entrypoints(self):
        for heading in (
            "## Beginner Poker course", "## Site architecture",
            "## Edit and publish", "## Release verification",
            "## Technology-first subject hierarchy",
        ):
            self.assertEqual(self.readme.count(heading), 1, heading)
        self.assertIn("AGENTS.md", self.readme)
        self.assertIn("_source/pages.json", self.readme)
        self.assertIn("_scripts/build.py", self.readme)


if __name__ == "__main__":
    unittest.main()
