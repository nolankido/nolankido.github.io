"""Turn 63: every registered browser-facing HTML download receives HTML5 QA.

Downloadable practice and NolanPoker review documents are not canonical
sitemap pages. Keep their privacy/crawler policy while parsing their HTML.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
sys.path.insert(0, str(ROOT / "_tests"))
import check_html5


DOWNLOADS = {
    "/downloads/poker-hand-review-practice-01.html",
    "/downloads/poker-hand-review-practice-01-key.html",
    "/downloads/nolanpoker-local-video-qa.html",
    "/downloads/nolanpoker-public-youtube-review.html",
}


class PublicDownloadHtml5Tests(unittest.TestCase):
    def test_four_registered_public_html_downloads_have_full_html5_coverage(self):
        paths = check_html5.public_html_download_paths(ROOT)
        self.assertEqual(set(paths), DOWNLOADS)
        for route, relative in paths.items():
            with self.subTest(route=route):
                self.assertEqual(relative, Path(route.lstrip("/")))
                content = (ROOT / relative).read_text(encoding="utf-8")
                self.assertTrue(content.lstrip().lower().startswith("<!doctype html"))
                self.assertIn('<meta name="robots" content="noindex,', content)
                self.assertEqual(check_html5.parse_errors(content), [])

    def test_downloads_do_not_become_canonical_sitemap_pages(self):
        import build
        pages = check_html5.publication_paths(ROOT, build.public_pages())
        self.assertFalse(DOWNLOADS & set(pages))
        xml = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        for route in DOWNLOADS:
            with self.subTest(route=route):
                self.assertNotIn("https://nolankido.com" + route, xml)

    def test_malformed_download_is_detected_by_actual_parser(self):
        source = (ROOT / "downloads/poker-hand-review-practice-01.html").read_text(encoding="utf-8")
        self.assertEqual(source.count("</main>"), 1)
        tampered = source.replace("</main>", "</div></main>", 1)
        self.assertNotEqual(tampered, source)
        self.assertNotEqual(check_html5.parse_errors(tampered), [])

    def test_download_inventory_rejects_missing_changed_or_non_html_bytes(self):
        document = b'<!doctype html><html lang="en"><head><title>Test</title></head><body><main>OK</main></body></html>'
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "downloads/release-probe.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(document)
            inventory = {"/downloads/release-probe.html": (200, document)}
            with patch.object(check_html5.check_live, "targets", return_value=inventory):
                self.assertEqual(check_html5.public_html_download_paths(root),
                                 {"/downloads/release-probe.html": Path("downloads/release-probe.html")})
                target.write_bytes(document + b"unexpected")
                with self.assertRaisesRegex(ValueError, "bytes disagree"):
                    check_html5.public_html_download_paths(root)
                target.unlink()
                with self.assertRaisesRegex(ValueError, "bytes disagree"):
                    check_html5.public_html_download_paths(root)
            target.write_bytes(b'<html><body>missing doctype</body></html>')
            with patch.object(check_html5.check_live, "targets",
                              return_value={"/downloads/release-probe.html": (200, target.read_bytes())}):
                with self.assertRaisesRegex(ValueError, "complete HTML5"):
                    check_html5.public_html_download_paths(root)

    def test_non_download_html_and_traversal_are_not_accepted(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            inventory = {
                "/documents/about.html": (200, b"<!doctype html><html></html>"),
                "/downloads/../private.html": (200, b"<!doctype html><html></html>"),
            }
            with patch.object(check_html5.check_live, "targets", return_value=inventory):
                with self.assertRaisesRegex(ValueError, "Invalid public HTML download target"):
                    check_html5.public_html_download_paths(root)

    def test_default_manual_runner_includes_html_download_regression(self):
        runner = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn63_public_html_downloads.py", runner)
        self.assertIn("['_tests/check_html5.py']", runner)
        workflows = ROOT / ".github/workflows"
        self.assertFalse(workflows.exists() and any(
            p.is_file() and p.suffix.lower() in (".yml", ".yaml") for p in workflows.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
