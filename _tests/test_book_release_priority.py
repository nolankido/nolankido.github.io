"""Book discovery receipts must include pages, preview cards and evidence assets."""
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_tests'))
import diagnose_live_crawl as live

BOOK_PREVIEWS = {
    '/books/': '/assets/social/reader-creative.png',
    '/books/one-workflow-at-a-time/': '/assets/social/ai-time-savings.png',
    '/books/how-to-play-no-limit-texas-holdem/': '/assets/social/reader-poker-no-limit-holdem-guide.png',
    '/books/ai-works-human-decides/': '/assets/social/keep-the-judgment.png',
}
DISCOVERY_PAGES = {
    '/', '/about/', '/bio/', '/creative/', '/find/', '/notes/keep-the-judgment/',
    '/technology/', '/technology/ai-website-visibility/', *BOOK_PREVIEWS,
}
ASSETS = {
    *BOOK_PREVIEWS.values(), '/assets/nolan-kido-identity.jsonld', '/assets/book-reader-journey.css',
    '/downloads/one-workflow-ai-pilot-worksheet.md', '/downloads/holdem-river-call-check-worksheet.md',
    '/downloads/ai-human-decision-review-worksheet.md', '/downloads/nolan-kido-book-edition-verification.md',
    '/downloads/nolan-kido-book-edition-evidence.json',
}
REQUIRED = DISCOVERY_PAGES | ASSETS


class PriorityControls(unittest.TestCase):
    def inventory(self):
        return {route: (404 if route == '/review-no-such-page-20261005/' else 200, route.encode())
                for route in live.PRIORITY}

    def test_all_discovery_surfaces_and_assets_are_priority_targets(self):
        self.assertEqual(len(live.PRIORITY), len(set(live.PRIORITY)))
        self.assertFalse(REQUIRED - set(live.PRIORITY))

    def test_missing_required_target_blocks_even_explicit_selection(self):
        for route in sorted(REQUIRED):
            inventory = self.inventory()
            del inventory[route]
            with self.subTest(route=route), patch.object(live.check_live, 'targets', return_value=inventory), patch.object(live.check_live, 'check') as check:
                with self.assertRaisesRegex(ValueError, 'Priority release targets are not registered'):
                    live.audit('priority', 1, 0, 1, only=['/'])
                check.assert_not_called()

    def test_complete_synthetic_receipts_cover_all_required_assets(self):
        inventory = self.inventory()
        with patch.object(live.check_live, 'targets', return_value=inventory), patch.object(live.check_live, 'check', return_value=(True, 'fixture exact bytes')):
            report = live.audit('priority', 1, 0, 1)
        self.assertEqual(report['status'], 'pass')
        self.assertEqual(report['total'], len(inventory))
        for route in REQUIRED:
            self.assertEqual(report['verified_routes'][route]['source_sha256'], sha256(inventory[route][1]).hexdigest())

    def test_missing_or_stale_asset_cannot_receive_a_pass_receipt(self):
        inventory = self.inventory()
        for route, message in [('/assets/social/keep-the-judgment.png', 'Response bytes do not match the checked-out release'),
                               ('/downloads/ai-human-decision-review-worksheet.md', 'HTTP 404, expected 200')]:
            with self.subTest(route=route), patch.object(live.check_live, 'targets', return_value=inventory), patch.object(live.check_live, 'check', return_value=(False, message)):
                report = live.audit('priority', 1, 0, 1, only=[route])
                self.assertEqual(report['status'], 'fail')
                self.assertEqual(report['verified_routes'], {})
                self.assertEqual(report['observed_failure_routes'], [route])


class PreviewMetadata(HTMLParser):
    def __init__(self, document):
        super().__init__()
        self.images = {}
        self.feed(document)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            attrs = dict(attrs)
            field = attrs.get('property') or attrs.get('name')
            if field in ('og:image', 'twitter:image'):
                self.images.setdefault(field, []).append(attrs.get('content'))


class FullCheckoutCoverage(unittest.TestCase):
    def test_actual_registered_bytes_and_book_preview_metadata(self):
        inventory = live.check_live.targets(ROOT)
        for route in REQUIRED:
            with self.subTest(route=route):
                path = ROOT / (route.lstrip('/') + ('index.html' if route.endswith('/') else ''))
                self.assertEqual(inventory[route], (200, path.read_bytes()))
        for route, image in BOOK_PREVIEWS.items():
            with self.subTest(book=route):
                document = inventory[route][1].decode('utf-8')
                expected = [live.check_live.ORIGIN + image]
                self.assertEqual(PreviewMetadata(document).images, {'og:image': expected, 'twitter:image': expected})


if __name__ == '__main__':
    unittest.main()
