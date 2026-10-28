"""Bounded release notifications: use Git fixtures and mocked HTTP only."""
from contextlib import redirect_stdout
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import submit_indexnow as notify

NOW = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)


def page(route, text='A useful result.', title='A practical example', extra='', chrome='Navigation'):
    return ('<!doctype html><html><head><title>' + title + '</title>'
            '<meta name="description" content="A bounded example.">'
            '<link rel="canonical" href="' + notify.ORIGIN + route + '">' + extra +
            '</head><body><nav>' + chrome + '</nav><main id="main"><h1>Example</h1><p>' +
            text + '</p></main><footer>Footer</footer></body></html>')


def sitemap(routes):
    return ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
            ''.join('<url><loc>' + notify.ORIGIN + route + '</loc><lastmod>' + date +
                    '</lastmod></url>' for route, date in routes.items()) + '</urlset>')


class IndexNowTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'tests@example.invalid')
        self.git('config', 'user.name', 'Notification tests')
        self.routes = {route: '2026-10-27' for route in ('/', '/changed/', '/gone/', '/stable/')}
        for route in self.routes:
            self.write(route.lstrip('/') + 'index.html', page(route))
        self.write('sitemap.xml', sitemap(self.routes))
        self.write('404.html', '<html><body>Not found.</body></html>')
        self.write(notify.KEY_FILE, notify.KEY_FILE[:-4])
        self.base = self.save()
        del self.routes['/gone/']
        (self.root / 'gone/index.html').unlink()
        self.routes['/new/'] = '2026-10-28'
        self.write('new/index.html', page('/new/', 'New source-supported material.'))
        self.write('changed/index.html', page('/changed/', 'A corrected result.'))
        self.write('stable/index.html', page('/stable/', extra='<link rel="stylesheet" href="/new.css">',
                                              chrome='An updated shared navigation'))
        self.write('private-not-sitemap/index.html', page('/private-not-sitemap/'))
        self.write('sitemap.xml', sitemap(self.routes))
        self.head = self.save()
        self.calls = []
        self.posts = []
        self.waits = []

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, stderr=subprocess.DEVNULL)

    def write(self, path, value):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value, encoding='utf-8')

    def save(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'Fixture release')
        return self.git('rev-parse', 'HEAD').decode().strip()

    def transport(self, post_responses=None, main=None, key=None, page_status=None, xrobots=None):
        responses = list(post_responses or [(200, {}, b'')])
        def send(method, url, body=None):
            self.calls.append((method, url))
            if method == 'POST':
                self.assertEqual(url, notify.ENDPOINT)
                self.posts.append(json.loads(body))
                value = responses.pop(0)
                if isinstance(value, Exception):
                    raise value
                return value
            if url == notify.MAIN_REF:
                sha = main() if callable(main) else main or self.head
                return 200, {}, json.dumps({'object': {'sha': sha}}).encode()
            if url == notify.ORIGIN + '/' + notify.KEY_FILE:
                return 200, {}, key if key is not None else notify.KEY_FILE[:-4].encode()
            route = notify.route(url)
            file = self.root / (route.lstrip('/') + 'index.html')
            if file.is_file():
                return page_status or 200, {'X-Robots-Tag': xrobots or ''}, file.read_bytes()
            return 404, {}, (self.root / '404.html').read_bytes()
        return send

    def run_submission(self, send=None, **kwargs):
        return notify.run(self.root, self.base, self.head, submit=True,
                          send=send or self.transport(), sleep=self.waits.append, now=lambda: NOW, **kwargs)

    def test_dry_run_selects_only_changed_canonical_pages_and_never_uses_network(self):
        def forbidden(*args):
            self.fail('Dry run attempted network access')
        result = notify.run(self.root, self.base, self.head, send=forbidden, now=lambda: NOW)
        self.assertEqual(result['status'], 'planned')
        self.assertEqual(result['urls'], [
            {'url': notify.ORIGIN + '/changed/', 'change': 'updated'},
            {'url': notify.ORIGIN + '/gone/', 'change': 'deleted'},
            {'url': notify.ORIGIN + '/new/', 'change': 'added'},
        ])
        self.assertEqual(result['attempts'], 0)
        self.assertNotIn(notify.KEY_FILE[:-4], json.dumps(result))

    def test_no_changes_makes_no_request_even_in_submit_mode(self):
        result = notify.run(self.root, self.head, self.head, submit=True,
                            send=lambda *args: self.fail('Empty batch made a request'), now=lambda: NOW)
        self.assertEqual(result['status'], 'nothing_to_submit')

    def test_title_description_main_link_and_structured_changes_are_meaningful(self):
        original = page('/')
        digest = notify.Page(original.encode(), notify.ORIGIN + '/').digest
        for changed in [page('/', title='A clearer title'),
                        original.replace('A bounded example.', 'A more specific description.'),
                        page('/', 'A <a href="/changed/">result</a>.'),
                        page('/', extra='<script type="application/ld+json">{"@type":"WebPage"}</script>')]:
            with self.subTest(changed=changed):
                self.assertNotEqual(notify.Page(changed.encode(), notify.ORIGIN + '/').digest, digest)
        self.assertEqual(notify.Page(page('/', extra='<style>p{color:red}</style>',
                                         chrome='Different chrome').encode(), notify.ORIGIN + '/').digest, digest)

    def test_sitemap_dates_also_select_editorial_changes(self):
        self.routes['/stable/'] = '2026-10-28'
        self.write('sitemap.xml', sitemap(self.routes))
        self.head = self.save()
        changes = notify.select_changes(self.root, self.base, self.head)
        self.assertIn(notify.ORIGIN + '/stable/', [item.url for item in changes])

    def test_exact_commit_ids_and_ancestry_are_required(self):
        for invalid in ['HEAD', '-n1', self.head[:7], 'a' * 40]:
            with self.subTest(invalid=invalid):
                result = notify.run(self.root, self.base, invalid, now=lambda: NOW)
                self.assertEqual(result['status'], 'failed')
        with self.assertRaises(notify.NotificationError):
            notify.select_changes(self.root, self.head, self.base)

    def test_route_validation_rejects_hosts_queries_fragments_and_private_paths(self):
        invalid = [
            'http://nolankido.com/', 'https://example.com/', 'https://www.nolankido.com/',
            'https://nolankido.com:443/', 'https://user@nolankido.com/',
            notify.ORIGIN + '/?x=1', notify.ORIGIN + '/#main', notify.ORIGIN + '//about/',
            notify.ORIGIN + '/_source/', notify.ORIGIN + '/.github/',
            notify.ORIGIN + '/%2e%2e/', notify.ORIGIN + '/a/../', notify.ORIGIN + '/file.txt',
            'https://[invalid/',
        ]
        for url in invalid:
            with self.subTest(url=url), self.assertRaises(notify.NotificationError):
                notify.route(url)

    def test_sitemap_rejects_duplicates_invalid_dates_entities_and_overflow(self):
        valid = sitemap({'/': '2026-10-28'}).encode()
        duplicate = (b'<url><loc>https://nolankido.com/</loc>'
                     b'<lastmod>2026-10-28</lastmod></url>')
        invalid = [valid.replace(b'2026-10-28', b'2026-02-31'),
                   valid.replace(b'</urlset>', duplicate + b'</urlset>'),
                   b'<!DOCTYPE urlset [<!ENTITY x "a">]>' + valid,
                   b'<sitemapindex/>']
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(notify.NotificationError):
                notify.sitemap(value)
        with patch.object(notify, 'MAX_URLS', 1), self.assertRaises(notify.NotificationError):
            notify.sitemap(sitemap({'/': '2026-10-28', '/about/': '2026-10-28'}).encode())

    def test_current_canonical_noindex_and_missing_output_fail_closed(self):
        for altered in [page('/wrong/'), page('/new/', extra='<meta name="robots" content="none">')]:
            self.write('new/index.html', altered)
            self.head = self.save()
            result = self.run_submission()
            self.assertEqual(result['status'], 'failed')
            self.assertFalse(self.posts)
        (self.root / 'new/index.html').unlink()
        self.head = self.save()
        self.assertEqual(self.run_submission()['status'], 'failed')

    def test_removed_sitemap_url_must_be_gone_or_explicitly_noindex(self):
        self.write('gone/index.html', page('/gone/'))
        self.head = self.save()
        self.assertEqual(self.run_submission()['status'], 'failed')
        self.write('gone/index.html', page('/gone/', extra='<meta name="robots" content="noindex">'))
        self.head = self.save()
        changes = notify.select_changes(self.root, self.base, self.head)
        gone = next(item for item in changes if item.url.endswith('/gone/'))
        self.assertEqual((gone.kind, gone.expected_status), ('updated', 200))
        self.assertEqual(self.run_submission()['status'], 'received')

    def test_received_receipt_follows_live_checks_and_is_not_an_indexing_claim(self):
        result = self.run_submission()
        self.assertEqual(result['status'], 'received')
        self.assertFalse(result['indexing_verified'])
        self.assertEqual(result['live_verified_commit'], self.head)
        self.assertEqual(self.calls[-1], ('POST', notify.ENDPOINT))
        self.assertEqual(len(self.posts), 1)
        self.assertEqual(self.posts[0]['host'], 'nolankido.com')
        self.assertEqual(self.posts[0]['keyLocation'], notify.ORIGIN + '/' + notify.KEY_FILE)
        self.assertEqual(self.posts[0]['urlList'], [item['url'] for item in result['urls']])
        self.assertNotIn(notify.KEY_FILE[:-4], json.dumps(result))

    def test_pending_key_receipt_does_not_claim_verified_key_or_indexing(self):
        result = self.run_submission(self.transport([(202, {}, b'')]))
        self.assertEqual(result['status'], 'key_validation_pending')
        self.assertFalse(result['indexing_verified'])
        self.assertIn('key validation', result['message'])

    def test_stale_main_wrong_key_wrong_public_bytes_or_noindex_block_post(self):
        for transport in [self.transport(main=self.base), self.transport(key=b'wrong'),
                          self.transport(page_status=503), self.transport(xrobots='noindex')]:
            with self.subTest(transport=transport):
                result = self.run_submission(transport)
                self.assertEqual(result['status'], 'failed')
                self.assertFalse(self.posts)
        self.git('checkout', '-q', self.base)
        result = self.run_submission()
        self.assertEqual(result['status'], 'failed')
        self.assertFalse(self.posts)

    def test_transient_retry_is_bounded_and_respects_retry_after(self):
        result = self.run_submission(self.transport([
            (429, {'Retry-After': '7'}, b''), (503, {}, b''), (200, {}, b'')]))
        self.assertEqual((result['status'], result['attempts']), ('received', 3))
        self.assertEqual(self.waits, [7, 10])
        self.assertEqual(result['retry_waits_seconds'], self.waits)
        self.assertEqual(len(self.posts), 3)

    def test_timeouts_retry_but_never_exceed_three_attempts(self):
        result = self.run_submission(self.transport([TimeoutError(), TimeoutError(), TimeoutError()]))
        self.assertEqual((result['status'], result['attempts']), ('failed', 3))
        self.assertEqual(self.waits, [5, 10])

    def test_permanent_rejection_or_long_rate_limit_do_not_loop(self):
        for status, headers in [(400, {}), (403, {}), (422, {}),
                                (429, {'Retry-After': '600'}), (429, {})]:
            self.posts.clear()
            self.waits.clear()
            result = self.run_submission(self.transport([(status, headers, b'')]))
            self.assertEqual((result['status'], result['attempts']), ('failed', 1))
            self.assertEqual(result['http_status'], status)
            self.assertEqual(len(self.posts), 1)
            self.assertFalse(self.waits)

    def test_retry_checks_that_main_has_not_advanced(self):
        def current():
            return self.base if self.posts else self.head
        result = self.run_submission(self.transport([(503, {}, b'')], main=current))
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(len(self.posts), 1)

    def test_retry_after_http_date_and_redirects(self):
        self.assertEqual(notify.retry_delay({'Retry-After': 'Wed, 28 Oct 2026 12:00:12 GMT'}, 1,
                                           lambda: NOW), 12)
        with self.assertRaises(notify.NotificationError):
            notify.retry_delay({'Retry-After': 'not a date'}, 1, lambda: NOW)
        with self.assertRaises(notify.NotificationError):
            notify.NoRedirects().redirect_request(None, None, 302, '', {}, 'https://elsewhere.invalid/')

    def test_cli_failure_is_json_and_nonzero(self):
        output = io.StringIO()
        with patch.object(notify, 'ROOT', self.root), patch.object(sys, 'argv', [
                'submit_indexnow.py', '--base', self.base, '--head', 'HEAD']), redirect_stdout(output):
            status = notify.main()
        self.assertEqual(status, 1)
        self.assertEqual(json.loads(output.getvalue())['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
