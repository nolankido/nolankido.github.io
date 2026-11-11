"""Keep the named practical-AI method reachable from its own case articles."""

import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build

TAGLINE = "AI Works, Human Decides"
TARGET = "/technology/#ai-works-human-decides"
LINK = '<a href="' + TARGET + '">' + TAGLINE + "</a>"

# Last-modified dates established before this editorial cross-link pass.
CASES = {
    "ai-book-continuity-checker": "2026-10-27",
    "ai-poker-video-evidence": "2026-11-04",
    "ai-website-visibility": "2026-11-06",
    "ai-weekly-reset": "2026-10-27",
    "check-ai-answers": "2026-10-27",
    "local-ai-gaming-laptop": "2026-11-02",
    "local-ai-review-replies": "2026-10-27",
    "review-reply-evidence-audit": "2026-11-05",
}
STANDALONE = {"local-ai-gaming-laptop", "review-reply-evidence-audit"}


def method_errors(article: str, method_page: str) -> list[str]:
    errors = []
    if article.count(LINK) != 1:
        errors.append("missing or duplicate canonical method link")
    if "AI Works Human Decides" in article:
        errors.append("outdated unpunctuated brand phrase")
    if method_page.count('id="ai-works-human-decides"') != 1:
        errors.append("missing or duplicate destination anchor")
    return errors


class ArticleMethodLinksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.method_page = (ROOT / "technology/index.html").read_text(encoding="utf-8")
        cls.outputs = build.build_outputs()

    def test_eight_article_sources_and_live_outputs_link_to_the_same_method(self):
        self.assertEqual(len(CASES), 8)
        for slug in CASES:
            with self.subTest(article=slug):
                source = (ROOT / "_source/technology" / (slug + ".html")).read_text(encoding="utf-8")
                relative = Path("technology") / slug / "index.html"
                public = (ROOT / relative).read_text(encoding="utf-8")
                self.assertEqual(method_errors(source, self.method_page), [])
                self.assertEqual(method_errors(public, self.method_page), [])
                self.assertIn('rel="canonical" href="https://nolankido.com/technology/' + slug + '/"', public)
                if slug not in STANDALONE:
                    self.assertEqual(self.outputs[relative], public)

    def test_article_dates_remain_their_prior_public_values(self):
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        lastmods = {entry.findtext("{*}loc"): entry.findtext("{*}lastmod") for entry in sitemap}
        for slug, expected in CASES.items():
            with self.subTest(article=slug):
                self.assertEqual(lastmods["https://nolankido.com/technology/" + slug + "/"], expected)
        manifest = {page["path"]: page for page in json.loads((ROOT / "_source/pages.json").read_text())}
        for slug in CASES.keys() - STANDALONE:
            with self.subTest(article=slug):
                page = manifest["/technology/" + slug + "/"]
                self.assertEqual(page.get("updated", page.get("date")), CASES[slug])

    def test_supporting_section_labels_and_the_primary_method_are_consistent(self):
        self.assertIn('<h2 class="section-title" id="ai-works-human-decides-title">' + TAGLINE + "</h2>", self.method_page)
        laptop = (ROOT / "technology/local-ai-gaming-laptop/index.html").read_text()
        replies = (ROOT / "technology/local-ai-review-replies/index.html").read_text()
        self.assertIn('AI Works, Human Decides / Conclusion', laptop)
        self.assertIn('<p class="section-label">' + TAGLINE + '</p>', replies)
        self.assertNotIn("AI Works Human Decides", laptop)
        self.assertNotIn("AI Works Human Decides", replies)

    def test_broken_article_or_method_links_are_rejected(self):
        article = (ROOT / "technology/ai-poker-video-evidence/index.html").read_text()
        for changed_article, changed_method in (
            (article.replace(TARGET, "/technology/#no-such-method", 1), self.method_page),
            (article.replace(LINK, "AI Works Human Decides", 1), self.method_page),
            (article.replace(LINK, LINK + LINK, 1), self.method_page),
            (article, self.method_page.replace('id="ai-works-human-decides"', 'id="other-method"', 1)),
        ):
            with self.subTest(sample=changed_article[:50], target=changed_method == self.method_page):
                self.assertTrue(method_errors(changed_article, changed_method))


if __name__ == "__main__":
    unittest.main()
