"""The static 404 route helps readers recover without inventing a destination.

Run locally; no browser service, remote request, tracking or CI required.
"""
import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET

from test_site import ROOT, Page, build
import site_find


SOURCE = ROOT / '_source/404.html'
OUTPUT = Path('404.html')


def recovery_contract(html: str) -> None:
    main = re.search(r'<main\b[^>]*>(.*?)</main>', html, re.S)
    page = Page(main.group(1) if main else html)
    ids = [attrs['id'] for _, attrs in page.elements if 'id' in attrs]
    assert len(ids) == len(set(ids)), 'IDs must be unique'
    assert len(page.tags('h1')) == (1 if main else 0), 'Keep the intended page heading structure'
    for anchor in ('missing-page-recovery', 'missing-page-routes'):
        assert ids.count(anchor) == 1, 'Missing recovery heading: ' + anchor
        assert any(tag == 'h2' and attrs.get('id') == anchor for tag, attrs in page.elements), 'Heading must stay a native h2'
    links = [a['href'] for a in page.tags('a')]
    for target in ('/find/', '/start-here/', '/', '/technology/', '/poker/#watch', '/about/', '/contact/'):
        assert links.count(target) == 1, 'Missing or duplicated recovery link: ' + target
    assert len([a for a in page.tags('article') if a.get('class') == 'identity-reading']) == 3, 'Keep three visible routes'
    assert 'id="find-controls"' not in html, 'The 404 should link to Find, not collect a query'
    assert not re.search(r'<(?:form|input|meta[^>]*http-equiv=["\']refresh)', html, re.I), 'No input or redirects on the error page'


class PageRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.html = cls.outputs[OUTPUT]

    def test_static_recovery_is_useful_without_scripts(self):
        recovery_contract(self.html)
        recovery_contract(SOURCE.read_text(encoding='utf-8'))
        self.assertEqual(self.html, (ROOT / OUTPUT).read_text(encoding='utf-8'))

    def test_error_page_keeps_correct_search_metadata(self):
        page = next(p for p in build.public_pages() if p['id'] == '404')
        self.assertEqual(page['path'], '/404.html')
        self.assertTrue(page['noindex'])
        self.assertEqual(page['updated'], '2026-11-11')
        parsed = Page(self.html)
        self.assertIn({'name': 'robots', 'content': 'noindex, follow'}, parsed.tags('meta'))
        self.assertIn({'rel': 'canonical', 'href': 'https://nolankido.com/404.html'}, parsed.tags('link'))
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.html, re.S).group(1))
        self.assertEqual(schema['dateModified'], page['updated'])
        urls = [e.text for e in ET.fromstring(self.outputs[Path('sitemap.xml')]).iter() if e.tag.endswith('}loc')]
        self.assertNotIn('https://nolankido.com/404.html', urls)
        self.assertNotIn('/404.html', {e['path'] for e in site_find.entries(ROOT, build.public_pages())})

    def test_recovery_links_have_public_destinations(self):
        for path in ('find/index.html', 'start-here/index.html', 'index.html', 'technology/index.html', 'poker/index.html', 'about/index.html', 'contact/index.html'):
            self.assertIn(Path(path), self.outputs)
        self.assertIn('id="watch"', self.outputs[Path('poker/index.html')])
        self.assertIn('does not put your search words in the address or save them.', self.html)
        self.assertNotIn('window.location', SOURCE.read_text(encoding='utf-8'))

    def test_negative_controls_reject_false_recovery(self):
        for changed in (self.html.replace('class="button" href="/find/"', 'class="button" href="/missing-search/"', 1),
                        self.html.replace('href="/poker/#watch"', 'href="/poker/#unverified"', 1),
                        self.html.replace('id="missing-page-routes"', 'id="missing-page-recovery"', 1),
                        self.html.replace('class="identity-reading"', 'class="not-a-route"', 1)):
            with self.subTest(mutant=changed[:90]):
                with self.assertRaises(AssertionError):
                    recovery_contract(changed)


if __name__ == '__main__':
    unittest.main()
