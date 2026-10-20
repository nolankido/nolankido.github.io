"""Focused Google robots grouping and catch-all policy regression contracts.

Primary references (checked October 19, 2026):
https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec
https://www.rfc-editor.org/rfc/rfc9309.html#section-2.2.4

Google ignores fields other than user-agent, allow and disallow for grouping.
In particular an extension must not silently split consecutive agent headers.
This is a bounded site policy against wildcard catch-all Disallow directives,
not a general RFC-complete URL permission evaluator or an indexing check.
"""
import json
from pathlib import Path
import tempfile
import unittest

import check_discovery as guard


def blocked(text):
    """Use the same comment stripping and whitespace handling as guard.check."""
    lines = [line.split('#', 1)[0].strip() for line in text.splitlines()]
    return guard.wildcard_root_blocked(lines)


class RobotsPolicyContractTests(unittest.TestCase):
    def test_catch_all_forms_include_end_anchored_wildcards(self):
        for path in ('/', '/*', '/**', '/*$', '/**$', '/***$'):
            with self.subTest(path=path):
                self.assertTrue(blocked('User-agent: *\nDisallow: ' + path))

    def test_root_only_and_specific_paths_are_not_catch_all(self):
        for path in ('', '/$', '/private/', '/private/*$', '/*.pdf$', '/%2A$'):
            with self.subTest(path=path):
                self.assertFalse(blocked('User-agent: *\nDisallow: ' + path))

    def test_unsupported_records_do_not_split_agent_headers(self):
        for record in ('Crawl-delay: 10', 'Request-rate: 1/10',
                       'Sitemap: https://nolankido.com/sitemap.xml',
                       'X-extension: value'):
            with self.subTest(record=record):
                self.assertTrue(blocked(
                    'User-agent: *\n' + record
                    + '\nUser-agent: NamedBot\nDisallow: /\n'
                ))

    def test_real_rules_separate_the_next_named_group(self):
        for record in ('Crawl-delay: 10', 'Request-rate: 1/10',
                       'Sitemap: https://nolankido.com/sitemap.xml'):
            with self.subTest(record=record):
                self.assertFalse(blocked(
                    'User-agent: *\nAllow: /\n' + record
                    + '\nUser-agent: NamedBot\nDisallow: /*$\n'
                ))

    def test_named_crawler_only_does_not_imply_wildcard(self):
        self.assertFalse(blocked('User-agent: NamedBot\nDisallow: /*$\n'))
        self.assertFalse(blocked(
            'User-agent: NamedBot\nDisallow: /\n'
            'User-agent: *\nAllow: /\n'
        ))

    def test_consecutive_agents_and_later_wildcard_groups_are_checked(self):
        self.assertTrue(blocked(
            'User-agent: NamedBot\nUser-agent: *\nDisallow: /*$\n'
        ))
        self.assertTrue(blocked(
            'User-agent: *\nAllow: /\n'
            'User-agent: NamedBot\nDisallow: /private/\n'
            'User-agent: *\nDisallow: /*$\n'
        ))

    def test_comments_case_and_orphan_rules(self):
        self.assertTrue(blocked(
            '  UsEr-AgEnT: * # public crawlers\n  DiSaLlOw: /*$ # maintenance\n'
        ))
        self.assertFalse(blocked('# User-agent: *\nDisallow: /*$\n'))
        self.assertFalse(blocked('Disallow: /*$\nUser-agent: *\nAllow: /\n'))

    def test_allow_does_not_waive_the_documented_site_policy(self):
        # This deliberately tests the guard's policy, not RFC allow precedence.
        self.assertTrue(blocked('User-agent: *\nDisallow: /*$\nAllow: /\n'))

    def test_complete_guard_rejects_anchored_block_on_synthetic_pages(self):
        # Self-contained end-to-end fixture, not a claim about deployed pages.
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            urls = []
            for route in guard.ROUTES:
                canonical = guard.ORIGIN + route
                path = root / route.lstrip('/') / 'index.html'
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    '<html><head><title>A synthetic priority-page fixture</title>'
                    '<meta name="description" content="A synthetic description for '
                    'testing local discovery rules, not actual website content.">'
                    '<link rel="canonical" href="' + canonical + '">'
                    '<meta property="og:url" content="' + canonical + '">'
                    '<script type="application/ld+json">'
                    + json.dumps({'@type': 'WebPage', 'url': canonical})
                    + '</script></head><body><h1>Fixture</h1></body></html>',
                    encoding='utf-8',
                )
                urls.append('<url><loc>' + canonical
                            + '</loc><lastmod>2026-10-17</lastmod></url>')
            (root / 'sitemap.xml').write_text(
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                + ''.join(urls) + '</urlset>', encoding='utf-8',
            )
            (root / 'poker/index.html').write_text(
                ''.join('<a href="' + route + '">Reference</a>'
                        for route in guard.POKER_LINKS), encoding='utf-8',
            )
            robots = root / 'robots.txt'
            sitemap = '\nSitemap: https://nolankido.com/sitemap.xml\n'
            robots.write_text('User-agent: *\nAllow: /\n' + sitemap, encoding='utf-8')
            self.assertEqual(guard.check(root)['priority_pages'], 7)
            robots.write_text('User-agent: *\nDisallow: /*$\n' + sitemap, encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'blanket root Disallow'):
                guard.check(root)


if __name__ == '__main__':
    unittest.main()
