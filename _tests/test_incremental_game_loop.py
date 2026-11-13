"""Public incremental game design guide, private-safe links, and executable rules."""
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
import build
import check_live
import author_archive

ROUTE = '/creative/incremental-game-loop/'
DOWNLOAD = '/downloads/incremental-game-first-minute-playtest.md'
HTML = 'creative/incremental-game-loop/index.html'


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


class IncrementalGameLoopTests(unittest.TestCase):
    def test_one_dated_article_and_public_canonical(self):
        pages = json.loads(read('_source/pages.json'))
        matches = [p for p in pages if p['id'] == 'incremental-game-loop' or p['path'] == ROUTE]
        self.assertEqual(len(matches), 1)
        page = matches[0]
        self.assertEqual(page['date'], '2026-11-13')
        self.assertEqual(page['section'], 'creative')
        self.assertIs(page['creative_article'], True)
        self.assertEqual(page['source'], 'creative/incremental-game-loop.html')
        self.assertNotIn('updated', page)
        html = read(HTML)
        self.assertIn('rel="canonical" href="https://nolankido.com' + ROUTE + '"', html)
        self.assertIn('article:published_time" content="2026-11-13"', html)
        self.assertNotIn('noindex', html)
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        schema = json.loads(match.group(1))
        self.assertEqual(schema['@type'], 'Article')
        self.assertEqual(schema['datePublished'], '2026-11-13')
        self.assertEqual(schema['author']['@id'], 'https://nolankido.com/about/#nolan-kido')
        self.assertEqual(schema['mainEntity']['@type'], 'SoftwareApplication')
        self.assertEqual(schema['mainEntity']['applicationCategory'], 'GameApplication')
        sitemap = ET.fromstring(read('sitemap.xml'))
        routes = [entry for entry in sitemap.findall('{*}url')
                  if entry.findtext('{*}loc') == 'https://nolankido.com' + ROUTE]
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].findtext('{*}lastmod'), '2026-11-13')

    def test_human_entrypoints_and_search_discovery(self):
        self.assertEqual(read('about/index.html').count('href="' + ROUTE + '"'), 1)
        self.assertGreaterEqual(read('creative/index.html').count('href="' + ROUTE + '"'), 2)
        self.assertGreaterEqual(read('projects/index.html').count('href="' + ROUTE + '"'), 2)
        self.assertIn('href="' + ROUTE + '"', read('notes/index.html'))
        self.assertIn(ROUTE, {p['path'] for p in author_archive.records(build.public_pages(), ROOT)})
        self.assertIn(ROUTE, read('find/index.html'))
        self.assertIn('Game design', read(HTML))
        self.assertIn('Original creative guide', read(HTML))

    def test_rules_ui_accessibility_and_bounded_claims(self):
        html = read(HTML)
        source = read('_source/creative/incremental-game-loop.html')
        js = read('assets/incremental-game-loop.js')
        css = read('assets/incremental-game-loop.css')
        for asset, kind in [('incremental-game-loop.css', 'href'),
                            ('incremental-game-loop.js', 'src')]:
            version = sha256((ROOT / 'assets' / asset).read_bytes()).hexdigest()[:12]
            self.assertIn(f'{kind}="/assets/{asset}?v={version}"', html)
        for element in ('game-lab', 'lab-fallback', 'lab-progress', 'lab-tap', 'lab-pencil',
                        'lab-routine', 'lab-pause', 'lab-reset', 'lab-action-status'):
            self.assertEqual(source.count('id="' + element + '"'), 1)
        for phrase in ('original teaching game', 'not a public release', 'a claim about real player',
                       'not a playtest result', 'No outside participant data', 'not a finished private title',
                       'without JavaScript', 'No login', '150', '10, 17, and 29', '25, 50, and 100'):
            self.assertIn(phrase.casefold(), (source + read('_source/projects.html')).casefold())
        for forbidden in ('localStorage', 'sessionStorage', 'fetch(', 'XMLHttpRequest', 'sendBeacon'):
            self.assertNotIn(forbidden, js)
        self.assertIn('document.hidden', js)
        self.assertIn('aria-live="polite"', html)
        self.assertIn('button:focus-visible', css)
        for private_name in ('federation', 'idlecolor', 'bitegrove', 'byte garden'):
            self.assertNotIn(private_name, (source + read('_source/projects.html') + read('_source/about.html')).casefold())
        for asset in (source, js, css, read(DOWNLOAD.lstrip('/'))):
            self.assertNotIn('\u2014', asset)

    def test_worksheet_and_exact_live_targets(self):
        worksheet = read(DOWNLOAD.lstrip('/'))
        self.assertIn('Blank private-use observation sheet', worksheet)
        self.assertIn('What I actually saw or heard', worksheet)
        self.assertIn('Player\'s words', worksheet)
        self.assertIn('What would disconfirm it', worksheet)
        self.assertIn('consent', worksheet.lower())
        html = read(HTML)
        self.assertIn('href="' + DOWNLOAD + '" download', html)
        targets = check_live.targets()
        for path in [ROUTE, DOWNLOAD, '/assets/incremental-game-loop.js',
                     '/assets/incremental-game-loop.css']:
            with self.subTest(path=path):
                self.assertIn(path, targets)
                self.assertEqual(targets[path][0], 200)
        self.assertEqual(targets[DOWNLOAD][1], worksheet.encode('utf-8'))
        self.assertEqual(build.build_outputs()[Path(HTML)], html)

    def test_browser_game_rules_and_controls_without_external_dependencies(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Node.js optional for local JavaScript behavior check')
        result = subprocess.run([node, str(ROOT / '_tests/incremental_game_loop_smoke.cjs')],
                                cwd=ROOT, text=True, capture_output=True, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stderr + '\n' + result.stdout)
        self.assertIn('browser interactions: PASS', result.stdout)


if __name__ == '__main__':
    unittest.main()
