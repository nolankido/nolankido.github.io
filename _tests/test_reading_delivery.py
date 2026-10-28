"""Independent content preservation, local font delivery, and public-link scope."""
import choice_history
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import re
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build, check_live, font_delivery, page_sharing
import visibility_sprint_history
from test_site import Page

PRIVACY_SECTION = '<h2>Keeping and sharing a page</h2><p>Copy-link controls copy only a page\'s permanent address after you press the button. On supported devices, Share page opens your browser\'s sharing interface with the public title and permanent address, not calculator entries or worksheet answers. Your clipboard, browser, and any app you choose have their own data handling. These controls add no sharing analytics events.</p>\n'


def old_privacy(text):
    change = json.loads((ROOT / '_tests/reading-privacy-change.json').read_text())
    if change['new'] not in text or PRIVACY_SECTION not in text:
        raise ValueError('Reviewed privacy disclosure missing')
    return text.replace(change['new'], change['old']).replace(PRIVACY_SECTION, '').replace('Updated October 12, 2026', 'Updated October 6, 2026')


def remove_controls(text):
    return re.sub(re.escape(page_sharing.BEGIN) + r'.*?' + re.escape(page_sharing.END), '', text, flags=re.S)


class ReadingDeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.baseline = json.loads((ROOT / '_tests/reading-delivery-baseline.json').read_text())

    def test_every_original_body_is_preserved_apart_from_explicit_privacy_update(self):
        for path, digest in self.baseline['bodies'].items():
            text = remove_controls(choice_history.before(path,self.outputs[Path(path)]))
            if path == 'privacy/index.html': text = old_privacy(text)
            body = re.search(r'<body\b[^>]*>(.*?)</body>', text, re.S)[1]
            self.assertEqual(sha256(body.encode()).hexdigest(), digest, path)

    def test_original_sources_scripts_identity_downloads_and_feeds_remain_intact(self):
        for path, digest in self.baseline['files'].items():
            raw = choice_history.read(path)
            if path == '_source/privacy.html': raw = old_privacy(raw.decode()).encode()
            elif path == '_source/pages.json':
                entries = json.loads(raw)
                next(p for p in entries if p['id'] == 'privacy')['updated'] = '2026-10-06'
                raw = (json.dumps(entries, indent=2, ensure_ascii=False) + '\n').encode()
            elif path == '_source/presentation.json':
                cfg = json.loads(raw)
                for key in ['ai-time-savings', 'ai-summary-review', 'ai-website-verification']: del cfg['pages'][key]
                raw = (json.dumps(cfg, indent=2) + '\n').encode()
            self.assertEqual(sha256(raw).hexdigest(), digest, path)

    def test_fonts_exactly_match_the_reviewed_provider_css_on_every_page(self):
        text = font_delivery.local_declarations(ROOT)
        self.assertEqual(self.outputs[font_delivery.OUTPUT], text)
        self.assertEqual((ROOT / font_delivery.OUTPUT).read_text(), text)
        for p in self.pages:
            html = self.outputs[build.output_path(p['path'])]
            self.assertEqual(html.count('href="' + font_delivery.href(text) + '"'), 1)
            self.assertNotIn('fonts.googleapis.com', html)
            self.assertNotIn('fonts.gstatic.com', html)
        self.assertEqual(len(re.findall(r'@font-face', text)), 38)
        self.assertEqual(set(re.findall(r'font-display:\s*(\w+)', text)), {'swap'})

    def test_unreviewed_font_css_fails_closed_even_if_a_hash_is_updated(self):
        source = (ROOT / font_delivery.SOURCE).read_text()
        for bad in [source.replace('fonts.gstatic.com', 'example.com'),
                    source.replace('font-display: swap', 'font-display: block'),
                    source + 'body { display:none; }', source + '@import "other.css";',
                    source.replace("'IBM Plex Mono'", "'Unknown Family'")]:
            with TemporaryDirectory() as tmp:
                root = Path(tmp); (root / '_source').mkdir(); (root / '_reports').mkdir()
                (root / font_delivery.SOURCE).write_text(bad)
                record = {'sha256': sha256(bad.encode()).hexdigest(), 'bytes': len(bad.encode())}
                (root / font_delivery.PROVENANCE).write_text(json.dumps(record))
                with self.assertRaises(ValueError): font_delivery.declarations(root)

    def test_changed_font_request_duplicate_and_missing_preconnect_are_rejected(self):
        doc = (ROOT / '_source/layout.html').read_text()
        for text in [doc.replace('display=swap', 'display=block'), doc.replace(font_delivery.PRECONNECT, ''),
                     doc + font_delivery.GOOGLE_LINK.search(doc)[0]]:
            with self.assertRaises(ValueError): font_delivery.apply({Path('test.html'): text}, ROOT)

    def test_one_share_component_only_on_indexable_articles_and_two_tools(self):
        count = 0
        for p in self.pages:
            html = self.outputs[build.output_path(p['path'])]
            expected = page_sharing.eligible(p)
            self.assertEqual(html.count(page_sharing.BEGIN), int(expected), p['path'])
            self.assertEqual(html.count('class="page-share-controls"'), int(expected), p['path'])
            for asset in page_sharing.ASSETS:
                self.assertEqual('/assets/' + asset + '?v=' in html, expected, p['path'])
            if expected:
                count += 1
                self.assertIn('https://nolankido.com' + p['path'], html)
                self.assertEqual(html.count('data-copy-page hidden'), 1)
                self.assertEqual(html.count('data-share-page hidden'), 1)
                if p.get('note'): self.assertEqual(html.count('Keep or share this essay'), 1)
        self.assertEqual(count, 118)
        self.assertEqual(sum(page_sharing.eligible(p) for p in visibility_sprint_history.pages(self.pages)), 112)

    def test_no_runtime_reading_of_private_inputs_or_tracking_in_share_controls(self):
        js = (ROOT / 'assets/page-sharing.js').read_text()
        for forbidden in ['location.', '.value', 'FormData', 'fetch(', 'sendBeacon', 'XMLHttpRequest',
                          'localStorage', 'sessionStorage', 'document.cookie', 'innerHTML', 'execCommand', 'umami.']:
            self.assertNotIn(forbidden, js)
        self.assertIn("link[rel=\"canonical\"]", js)
        self.assertIn('url.search || url.hash', js)
        self.assertIn('navigator.share(data)', js)
        self.assertIn('navigator.clipboard.writeText(address)', js)

    def test_bad_origins_routes_and_duplicate_controls_are_rejected(self):
        p = {'id': 'task-brief', 'path': '/technology/task-brief/'}
        for origin in ['https://example.com', 'http://nolankido.com', 'https://nolankido.com/']:
            with self.assertRaises(ValueError): page_sharing.decorate('Text', p, origin)
        for route in ['/technology/task-brief/?secret=x', '//example.com/', '/technology/task-brief/#secret']:
            with self.assertRaises(ValueError): page_sharing.decorate('Text', {**p, 'path': route}, 'https://nolankido.com')
        with self.assertRaises(ValueError): page_sharing.decorate(page_sharing.BEGIN, p, 'https://nolankido.com')

    def test_three_new_sharing_cards_have_distinct_exact_metadata(self):
        by_id = {p['id']: p for p in self.pages}
        cfg = json.loads((ROOT / '_source/presentation.json').read_text())
        images = []
        for id in ['ai-time-savings', 'ai-summary-review', 'ai-website-verification']:
            p = by_id[id]; html = self.outputs[build.output_path(p['path'])]
            meta = {a.get('name', a.get('property')): a.get('content') for a in Page(html).tags('meta')}
            image = 'https://nolankido.com' + cfg['pages'][id]['src']; images.append(image)
            self.assertEqual(meta['og:image'], image); self.assertEqual(meta['twitter:image'], image)
            self.assertEqual(meta['og:image:alt'], cfg['pages'][id]['alt'])
            self.assertEqual(meta['og:image:width'], '1200'); self.assertEqual(meta['og:image:height'], '630')
        self.assertEqual(len(set(images)), 3)

    def test_live_verifier_includes_every_new_asset(self):
        targets = check_live.targets()
        for path in ['assets/site-fonts.css', 'assets/page-sharing.css', 'assets/page-sharing.js',
                     'assets/social/ai-time-savings.png', 'assets/social/check-ai-summary.png',
                     'assets/social/checking-ai-website-changes.png']:
            self.assertEqual(targets['/' + path], (200, (ROOT / path).read_bytes()))

if __name__ == '__main__': unittest.main(verbosity=2)
