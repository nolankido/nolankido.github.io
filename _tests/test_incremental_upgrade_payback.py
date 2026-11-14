"""Upgrade payback: real arithmetic, bounded claims, coherent public discovery."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import author_archive
import build
import check_live

ROUTE = '/creative/incremental-upgrade-payback/'
HTML = 'creative/incremental-upgrade-payback/index.html'
WORKSHEET = '/downloads/incremental-upgrade-payback-worksheet.md'


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


class IncrementalUpgradePaybackTests(unittest.TestCase):
    def test_public_article_date_schema_and_sitemap(self):
        pages = json.loads(read('_source/pages.json'))
        matches = [p for p in pages if p['path'] == ROUTE or p['id'] == 'incremental-upgrade-payback']
        self.assertEqual(len(matches), 1)
        page = matches[0]
        self.assertIs(page['creative_article'], True)
        self.assertEqual(page['section'], 'creative')
        self.assertEqual(page['date'], '2026-11-13')
        self.assertNotIn('updated', page)
        html = read(HTML)
        self.assertIn('rel="canonical" href="https://nolankido.com' + ROUTE + '"', html)
        self.assertIn('<meta property="og:type" content="article">', html)
        self.assertIn('article:published_time" content="2026-11-13"', html)
        self.assertNotIn('noindex', html)
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        schema = json.loads(match.group(1))
        self.assertEqual(schema['@type'], 'Article')
        self.assertEqual(schema['datePublished'], '2026-11-13')
        self.assertEqual(schema['author']['@id'], 'https://nolankido.com/about/#nolan-kido')
        self.assertEqual(schema['mainEntity']['@type'], 'SoftwareApplication')
        self.assertEqual(schema['mainEntity']['applicationCategory'], 'EducationalApplication')
        self.assertEqual(schema['mainEntity']['@id'], 'https://nolankido.com' + ROUTE + '#payback-form')
        sitemap = ET.fromstring(read('sitemap.xml'))
        entries = [e for e in sitemap.findall('{*}url')
                   if e.findtext('{*}loc') == 'https://nolankido.com' + ROUTE]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].findtext('{*}lastmod'), '2026-11-13')
        self.assertEqual(build.build_outputs()[Path(HTML)], html)

    def test_reciprocal_reader_and_author_archive_routes(self):
        for page in ('about/index.html', 'creative/index.html', 'projects/index.html',
                     'creative/incremental-game-loop/index.html', 'notes/index.html'):
            with self.subTest(page=page):
                self.assertIn('href="' + ROUTE + '"', read(page))
        self.assertIn(ROUTE, read('find/index.html'))
        archive = author_archive.records(build.public_pages(), ROOT)
        matching = [e for e in archive if e['path'] == ROUTE]
        self.assertEqual(len(matching), 1)
        self.assertEqual(author_archive.label(matching[0]), 'Original creative guide')
        self.assertIn('href="/creative/incremental-game-loop/"', read(HTML))
        self.assertIn('href="' + WORKSHEET + '" download', read(HTML))

    def test_browser_fallback_math_truth_and_no_private_claims(self):
        html = read(HTML)
        source = read('_source/creative/incremental-upgrade-payback.html')
        script = read('assets/incremental-upgrade-payback.js')
        css = read('assets/incremental-upgrade-payback.css')
        for asset, kind in [('incremental-upgrade-payback.css', 'href'),
                            ('incremental-upgrade-payback.js', 'src')]:
            version = sha256((ROOT / 'assets' / asset).read_bytes()).hexdigest()[:12]
            self.assertIn(f'{kind}="/assets/{asset}?v={version}"', html)
        for target in ('payback-form', 'payback-fallback', 'payback-result',
                       'payback-bank', 'payback-taps', 'payback-seconds',
                       'payback-pencil-cost', 'payback-routine-cost', 'payback-feedback',
                       'payback-preset-20', 'payback-preset-60'):
            self.assertEqual(source.count('id="' + target + '"'), 1)
        self.assertIn('class="payback-first-link"', source)
        self.assertIn('href="#payback-compare"', source)
        self.assertIn('Each example restores all five inputs', source)
        self.assertIn('type="button">Try 20 taps', source)
        self.assertIn('type="button">Try 60 taps', source)
        self.assertIn("result.scrollIntoView({block: 'start', behavior: 'instant'})", script)
        self.assertIn("focus({preventScroll: true})", script)
        self.assertIn('Conditional payback against buying nothing', script)
        self.assertIn('comparison.routineMinusPencil === null', script)
        self.assertIn('scroll-margin-top:9rem', css)
        self.assertIn('.payback-first-link a:focus-visible', css)
        for phrase in ('20 taps', '60 taps', '45', '55', '80', '85', '135', '120',
                       'C - R + T - N', 'T is greater than N + 15',
                       'only one purchase', 'not a report of two people playing',
                       'no offline rewards', 'not a forecast', 'not a player-preference verdict',
                       'cannot observe them', 'without it'):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.casefold(), (source + script).casefold())
        for forbidden in ('localStorage', 'sessionStorage', 'fetch(', 'XMLHttpRequest', 'sendBeacon'):
            self.assertNotIn(forbidden, script)
        self.assertIn('aria-live="polite"', html)
        self.assertIn('focus-visible', css)
        for path in ('_source/creative/incremental-upgrade-payback.html',
                     'assets/incremental-upgrade-payback.js',
                     'downloads/incremental-upgrade-payback-worksheet.md'):
            content = read(path)
            self.assertNotIn('\u2014', content)
            for private in ('federation', 'idlecolor', 'bitegrove', 'byte garden'):
                self.assertNotIn(private, content.casefold())

    def test_worksheet_and_verified_get_targets(self):
        worksheet = read(WORKSHEET.lstrip('/'))
        for phrase in ('Blank Comparison Worksheet', 'B - C + 2 x N',
                       'C - R + T - N', 'What the player actually did or said',
                       'Obtain consent', 'No compounding'):
            self.assertIn(phrase.casefold(), worksheet.casefold())
        targets = check_live.targets()
        for path in (ROUTE, WORKSHEET, '/assets/incremental-upgrade-payback.css',
                     '/assets/incremental-upgrade-payback.js'):
            with self.subTest(path=path):
                self.assertIn(path, targets)
                self.assertEqual(targets[path][0], 200)
        self.assertEqual(targets[WORKSHEET][1], worksheet.encode('utf-8'))

    def test_node_math_and_mock_dom(self):
        node = shutil.which('node')
        if node is None:
            self.skipTest('Node.js is optional for this local JavaScript behavior check')
        result = subprocess.run([node, str(ROOT / '_tests/incremental_upgrade_payback_smoke.cjs')],
                                cwd=ROOT, text=True, capture_output=True, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stderr + '\n' + result.stdout)
        self.assertIn('browser form interactions: PASS', result.stdout)


if __name__ == '__main__':
    unittest.main()
