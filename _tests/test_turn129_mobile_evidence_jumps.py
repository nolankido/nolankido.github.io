"""Turn 129: a mobile-first native shortcut to bounded evidence in two cases."""

from hashlib import sha256
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build_local_laptop_case
import build_reply_audit_case


CASES = (
    ("local-ai-gaming-laptop", "laptop-snapshot-title", "2026-11-02",
     build_local_laptop_case.render),
    ("review-reply-evidence-audit", "reply-snapshot-title", "2026-11-05",
     build_reply_audit_case.render),
)


def jump_errors(html: str, title_id: str) -> list[str]:
    """A genuine header shortcut must lead to exactly one in-page summary."""
    errors = []
    hero = '<section class="page-hero shell">'
    jump = '<p class="evidence-top-jump"><a href="#' + title_id + '">Jump to evidence summary</a></p>'
    target = '<h3 id="' + title_id + '">Evidence at a glance</h3>'
    if html.count(hero) != 1 or html.count(jump) != 1 or html.count(target) != 1:
        return ["missing or duplicated shortcut, hero or evidence destination"]
    header_start = html.index(hero)
    header_end = html.index('</section>', header_start)
    if not (header_start < html.index(jump) < header_end < html.index(target)):
        errors.append("shortcut must be in the article hero, before its target")
    if html.count('href="#' + title_id + '"') != 1:
        errors.append("duplicate summary jump")
    return errors


class MobileEvidenceJumpTests(unittest.TestCase):
    def test_native_shortcuts_and_independent_builds(self):
        css_path = ROOT / "assets/standalone-evidence-snapshot.css"
        version = sha256(css_path.read_bytes()).hexdigest()[:12]
        stylesheet = f'/assets/standalone-evidence-snapshot.css?v={version}'
        for slug, title_id, lastmod, render in CASES:
            with self.subTest(slug=slug):
                html = (ROOT / "technology" / slug / "index.html").read_text(encoding="utf-8")
                self.assertEqual(jump_errors(html, title_id), [])
                self.assertEqual(html, render())
                self.assertEqual(html.count(stylesheet), 1)
                self.assertIn('"dateModified": "' + lastmod + '"', html)
                self.assertIn('<link rel="canonical" href="https://nolankido.com/technology/' + slug + '/">', html)

    def test_mobile_only_and_reduced_motion_safe_css(self):
        css = (ROOT / "assets/standalone-evidence-snapshot.css").read_text(encoding="utf-8")
        for fragment in (
            ".evidence-top-jump { display: none; }",
            "@media screen and (max-width: 760px)",
            ".page-local-ai-gaming-laptop .evidence-top-jump",
            ".page-review-reply-evidence-audit .evidence-top-jump",
            "min-height: 44px",
            "scroll-margin-top: 11rem",
            ".case-evidence-snapshot h3:target",
        ):
            self.assertIn(fragment, css)
        self.assertNotIn("scroll-behavior: smooth", css)

    def test_wrong_target_or_shortcut_after_article_is_rejected(self):
        for slug, title_id, _, _ in CASES:
            html = (ROOT / "technology" / slug / "index.html").read_text(encoding="utf-8")
            jump = '<p class="evidence-top-jump"><a href="#' + title_id + '">Jump to evidence summary</a></p>'
            wrong = html.replace(jump, jump.replace(title_id, "missing-anchor"), 1)
            moved = html.replace(jump, "", 1).replace(
                '<article class="local-laptop-case', jump + '<article class="local-laptop-case', 1)
            duplicate = html.replace(jump, jump + jump, 1)
            with self.subTest(slug=slug):
                for damaged in (wrong, moved, duplicate):
                    self.assertTrue(jump_errors(damaged, title_id))


if __name__ == "__main__":
    unittest.main()
