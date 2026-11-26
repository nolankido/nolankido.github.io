"""Offline controls for author-page crawl completeness and honest failure reporting."""
from contextlib import redirect_stdout
from email.message import Message
from io import BytesIO, StringIO
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import live_indexability_audit as audit


def sitemap(urls):
    return ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + ''.join('<url><loc>' + escape(url) + '</loc></url>' for url in urls) + '</urlset>').encode()


def row(path, **overrides):
    result = dict(path=path, status=200, final_url=audit.BASE + path, canonical=[audit.BASE + path],
                  title='Public page', h1=1, mime='text/html; charset=utf-8', schema_types={'WebPage': 1},
                  robots=[], x_robots=[], internal_links=['/', *audit.BOOK_ROUTES])
    result.update(overrides)
    return result


class Response(BytesIO):
    def __init__(self, raw, url, status=200):
        super().__init__(raw)
        self.url = url
        self.status = status
        self.headers = Message()
        self.headers['Content-Type'] = 'text/html; charset=utf-8'


class LiveAuthorCrawlTests(unittest.TestCase):
    def test_author_catalog_and_each_book_are_required(self):
        self.assertIn('/bio/', audit.SAMPLE)
        self.assertEqual(len(audit.BOOK_ROUTES), 4)
        self.assertTrue(set(audit.BOOK_ROUTES).issubset(audit.SAMPLE))
        paths = ['/', *audit.BOOK_ROUTES]
        self.assertEqual(audit.assess(paths, [row(p) for p in paths], priority=paths, excluded=[])[0], [])

    def test_research_portfolio_and_six_case_records_are_required(self):
        expected = {
            '/about/accounting-research/', '/ai-in-real-life/',
            '/technology/checking-ai-website-changes/',
            '/technology/rightsreceipt-ai-licensing/',
            '/technology/local-ai-review-replies/',
            '/technology/ai-book-continuity-checker/',
            '/technology/ai-poker-video-evidence/',
            '/technology/dinner-on-time/',
        }
        self.assertEqual(set(audit.EVIDENCE_ROUTES), expected)
        self.assertEqual(len(audit.EVIDENCE_ROUTES), len(expected))
        self.assertTrue(expected.issubset(audit.SAMPLE))
        self.assertEqual(len(audit.SAMPLE), len(set(audit.SAMPLE)))
        for path in expected:
            with self.subTest(path=path):
                paths = [p for p in audit.SAMPLE if p != path]
                issues, _ = audit.assess(paths, [row(p) for p in paths], excluded=[])
                self.assertIn([path, 'priority sample missing from sitemap'], issues)
                self.assertIn([path, 'non-200 or fetch error'], issues)

    def test_live_parser_captures_normalized_search_crawler_meta(self):
        for name in ('OAI-SearchBot', ' Googlebot-News ', ' BINGBOT ', 'GPTBot'):
            with self.subTest(name=name):
                parser = audit.PageParser()
                parser.feed(f'<meta name="{name}" content="NONE">')
                parser.close()
                self.assertEqual(parser.robots, [(name.strip().lower(), 'NONE')])
                self.assertTrue(audit.blocks_indexing({'robots': parser.robots}))

    def test_live_parser_retains_duplicate_directives_and_property_variant(self):
        for html in (
            '<meta name="robots" content="noindex"><meta name="ROBOTS" content="index">',
            '<meta name="robots" content="index"><meta name="robots" content="noindex">',
            '<meta property="robots" content="noindex">',
        ):
            with self.subTest(html=html):
                parser = audit.PageParser()
                parser.feed(html)
                parser.close()
                self.assertTrue(audit.blocks_indexing({'robots': parser.robots}))
                if 'property' not in html:
                    self.assertEqual(len(parser.robots), 2)

    def test_live_preview_directives_and_unrelated_metadata_not_indexing_blocks(self):
        for value in ('max-image-preview:none', 'max-image-preview: none',
                      'max-snippet:0', 'nofollow'):
            with self.subTest(value=value):
                parser = audit.PageParser()
                parser.feed(f'<meta name="robots" content="{value}">'
                            '<meta name="description" content="noindex">')
                parser.close()
                self.assertFalse(audit.blocks_indexing({'robots': parser.robots}))
                self.assertFalse(audit.blocks_indexing({'x_robots': [value]}))
        for value in ('OAI-SearchBot: noindex', 'Googlebot-News: none',
                      'GPTBot:NOINDEX', 'robots: noindex'):
            self.assertTrue(audit.blocks_indexing({'x_robots': [value]}), value)

    def test_missing_priority_never_disappears_or_crashes(self):
        missing = audit.BOOK_ROUTES[-1]
        paths = ['/', *audit.BOOK_ROUTES[:-1]]
        problems, _ = audit.assess(paths, [row(p) for p in paths], priority=[*paths, missing], excluded=[])
        self.assertIn([missing, 'priority sample missing from sitemap'], problems)
        self.assertIn([missing, 'non-200 or fetch error'], problems)

    def test_sitemap_rejects_duplicate_foreign_and_noncanonical_urls(self):
        base = audit.BASE
        paths, issues = audit.sitemap_inventory(sitemap([base+'/', base+'/', base+'/books/?x=1',
                                                         'https://example.invalid/', base+'/books', base+'/#x',
                                                         base+'.example.invalid/']))
        self.assertEqual(paths, ['/', '/'])
        self.assertIn(['/', 'duplicate sitemap location'], issues)
        self.assertEqual(sum(i[1] == 'invalid or noncanonical loc' for i in issues), 5)
        for raw in (b'<broken', b'<sitemapindex/>', sitemap([])):
            self.assertTrue(audit.sitemap_inventory(raw)[1])

    def test_none_and_noindex_not_confused_with_image_preview(self):
        for value in ('NOINDEX, follow', 'none', 'googlebot: noindex', 'bingbot:none', 'nofollow noindex'):
            self.assertTrue(audit.blocks_indexing(row('/', x_robots=[value])), value)
        for value in ('max-image-preview:none', 'max-image-preview: none', 'index,follow', 'nofollow'):
            self.assertFalse(audit.blocks_indexing(row('/', x_robots=[value])), value)

    def test_error_or_redirect_pages_cannot_supply_inbound_evidence(self):
        target = audit.BOOK_ROUTES[-1]
        for bad in (row('/', status=404), row('/', final_url=audit.BASE+'/other/'),
                    row('/', html_parser_error='truncated')):
            issues, _ = audit.assess(['/', target], [bad, row(target, internal_links=[])], priority=[], excluded=[])
            self.assertIn([target, 'no incoming links from other crawled pages'], issues)

    def test_disconnected_cycle_is_not_homepage_discovery(self):
        rows = [row('/', internal_links=['/about/']),
                row('/about/', internal_links=['/']),
                row('/a/', internal_links=['/b/']),
                row('/b/', internal_links=['/a/'])]
        paths = [r['path'] for r in rows]
        issues, inbound = audit.assess(paths, rows, priority=paths, excluded=[])
        self.assertEqual(inbound['/a/'], {'/b/'})
        for path in ('/a/', '/b/'):
            self.assertIn([path, 'no internal link path from the homepage through eligible canonical pages'], issues)

    def test_connected_nested_pages_have_no_discovery_errors(self):
        rows = [row('/', internal_links=['/about/']),
                row('/about/', internal_links=['/', '/books/']),
                row('/books/', internal_links=['/about/', '/book/']),
                row('/book/', internal_links=['/books/'])]
        paths = [r['path'] for r in rows]
        self.assertEqual(audit.assess(paths, rows, priority=paths, excluded=[])[0], [])

    def test_invalid_source_pages_cannot_bridge_discovery(self):
        for overrides in (
            dict(status=404),
            dict(final_url=audit.BASE + '/other/'),
            dict(canonical=[audit.BASE + '/other/']),
            dict(canonical=[]),
            dict(mime='application/json'),
            dict(mime='text/htmlfake'),
            dict(html_parser_error='truncated'),
            dict(robots=[('robots', 'noindex')]),
            dict(x_robots=['OAI-SearchBot: noindex']),
        ):
            with self.subTest(overrides=overrides):
                rows = [row('/', internal_links=['/bridge/']),
                        row('/bridge/', internal_links=['/', '/target/'], **overrides),
                        row('/target/', internal_links=['/'])]
                paths = [r['path'] for r in rows]
                issues, inbound = audit.assess(paths, rows, priority=paths, excluded=[])
                self.assertFalse(inbound.get('/target/'))
                self.assertIn(['/target/', 'no incoming links from other crawled pages'], issues)
                self.assertIn(['/target/', 'no internal link path from the homepage through eligible canonical pages'], issues)

    def test_valid_preview_and_charset_remain_eligible(self):
        rows = [row('/', internal_links=['/target/'], mime=' Text/HTML ; charset=utf-8',
                    robots=[('robots', 'max-image-preview: none')]),
                row('/target/', internal_links=['/'])]
        paths = [r['path'] for r in rows]
        self.assertEqual(audit.assess(paths, rows, priority=paths, excluded=[])[0], [])

    def test_missing_home_does_not_allow_a_detached_cycle_to_pass(self):
        rows = [row('/a/', internal_links=['/b/']), row('/b/', internal_links=['/a/'])]
        paths = ['/a/', '/b/']
        issues, _ = audit.assess(paths, rows, priority=['/', *paths], excluded=[])
        self.assertIn(['/', 'priority sample missing from sitemap'], issues)
        for path in paths:
            self.assertIn([path, 'no internal link path from the homepage through eligible canonical pages'], issues)
        self.assertEqual(audit.assess(paths, rows, priority=paths, excluded=[])[0], [])

    def test_excluded_utility_needs_actual_response_and_noindex(self):
        good = row('/404.html', status=404, robots=[('robots', 'noindex,follow')])
        self.assertEqual(audit.assess([], [good], priority=[], excluded=['/404.html'])[0], [])
        missing = row('/find/', status=503, x_robots=['noindex'])
        self.assertIn(['/find/', 'excluded utility fetch/status failure'],
                      audit.assess([], [missing], priority=[], excluded=['/find/'])[0])

    def test_fetch_preserves_real_http_status_and_parser_failure(self):
        url = audit.BASE+'/404.html'
        headers = Message()
        headers['Content-Type'] = 'text/html'
        error = HTTPError(url, 404, 'Not Found', headers, BytesIO(b'<meta name="robots" content="noindex">'))
        with patch.object(audit.urllib.request, 'urlopen', side_effect=error):
            response = audit.fetch('/404.html')
        self.assertEqual(response['status'], 404)
        self.assertTrue(audit.blocks_indexing(response))
        with patch.object(audit.urllib.request, 'urlopen', return_value=Response(b'\xff', audit.BASE+'/')):
            self.assertIn('html_parser_error', audit.fetch('/'))
        with patch.object(audit.urllib.request, 'urlopen', side_effect=URLError('fixture DNS')):
            self.assertIn('error', audit.fetch('/'))

    def test_main_reports_missing_book_and_failed_fetch_without_traceback(self):
        paths = [p for p in audit.SAMPLE if p != audit.BOOK_ROUTES[-1]]
        requested = []
        def fetch(path):
            requested.append(path)
            return {'path': path, 'error': 'fixture DNS'} if path == audit.BOOK_ROUTES[-1] else row(path)
        def open_url(url, **kwargs):
            return Response(sitemap([audit.BASE + p for p in paths]) if url.endswith('sitemap.xml') else b'User-agent: *\nAllow: /\nSitemap: https://nolankido.com/sitemap.xml\n', url)
        with patch.object(audit.urllib.request, 'urlopen', side_effect=open_url), patch.object(audit, 'fetch', side_effect=fetch), redirect_stdout(StringIO()) as output:
            self.assertEqual(audit.main(), 1)
        self.assertIn(audit.BOOK_ROUTES[-1], requested)
        line = next(line for line in output.getvalue().splitlines() if line.startswith('ALL_ISSUES '))
        self.assertIn([audit.BOOK_ROUTES[-1], 'priority sample missing from sitemap'], json.loads(line.split(' ', 1)[1]))
        self.assertIn('RESULT FAIL', output.getvalue())

    def test_committed_robots_policy_and_formatting(self):
        good = (ROOT / 'robots.txt').read_text(encoding='utf-8')
        self.assertEqual(audit.robots_policy_issues(good), [])
        self.assertEqual(audit.robots_policy_issues(
            '\ufeff# comment\r\n USER-AGENT : * \r\n ALLOW: / # comment\r\n'
            'SITEMAP: https://nolankido.com/sitemap.xml\r\n'), [])

    def test_robots_policy_drift_and_invalid_sitemap_declarations(self):
        good = 'User-agent: *\nAllow: /\n\nSitemap: https://nolankido.com/sitemap.xml\n'
        for text in (good.replace('Allow: /', 'Disallow: /'),
                     good + '\nUser-agent: OAI-SearchBot\nDisallow: /\n',
                     good + 'Crawl-delay: 5\n', '', '<html>access denied</html>',
                     good + 'Allow /\n'):
            with self.subTest(text=text):
                self.assertTrue(audit.robots_policy_issues(text))
        for text in (good.split('\n\n')[0],
                     good.replace('https://nolankido.com/sitemap.xml',
                                  'https://example.invalid/sitemap.xml'),
                     good + 'Sitemap: https://nolankido.com/sitemap.xml\n'):
            with self.subTest(text=text):
                self.assertIn(['/robots.txt', 'expected exactly one canonical sitemap declaration'],
                              audit.robots_policy_issues(text))
        self.assertEqual(audit.robots_policy_issues(
            good + '\nUser-agent: GPTBot\nDisallow: /\n'),
            [['/robots.txt', 'crawl rules differ from reviewed allow-all policy; review required']])

    def test_live_main_stops_before_page_fetch_on_robots_policy_drift(self):
        def open_url(url, **kwargs):
            return Response(
                sitemap([audit.BASE + p for p in audit.SAMPLE])
                if url.endswith('sitemap.xml') else
                b'User-agent: *\nDisallow: /\nSitemap: https://nolankido.com/sitemap.xml\n', url)
        with patch.object(audit.urllib.request, 'urlopen', side_effect=open_url), patch.object(audit, 'fetch') as fetch, redirect_stdout(StringIO()) as output:
            self.assertEqual(audit.main(), 1)
        fetch.assert_not_called()
        line = next(line for line in output.getvalue().splitlines() if line.startswith('ALL_ISSUES '))
        self.assertIn(['/robots.txt', 'crawl rules differ from reviewed allow-all policy; review required'],
                      json.loads(line.split(' ', 1)[1]))
        self.assertIn('RESULT FAIL', output.getvalue())

    def test_sitemap_transport_failure_reports_fail(self):
        with patch.object(audit.urllib.request, 'urlopen', side_effect=URLError('fixture DNS')), redirect_stdout(StringIO()) as output:
            self.assertEqual(audit.main(), 1)
        self.assertIn('RESULT FAIL', output.getvalue())


if __name__ == '__main__':
    unittest.main()
