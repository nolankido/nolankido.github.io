"""Public contract for the bounded AI-workflow pilot and offline example."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'technology/ai-workflow-pilot/index.html'
ROUTE = '/technology/ai-workflow-pilot/'
SCRIPT = ROOT / 'downloads/ai-workflow-pilot-audit.py'
EXAMPLE = ROOT / 'downloads/ai-workflow-pilot-example.csv'
BLANK = ROOT / 'downloads/ai-workflow-pilot-blank.csv'


class AIWorkflowPilotTests(unittest.TestCase):
    def test_public_page_metadata_and_discovery(self):
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        matches = [p for p in pages if p['path'] == ROUTE or p['id'] == 'ai-workflow-pilot']
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['date'], '2026-11-13')
        self.assertTrue(matches[0]['worked_guide'])
        self.assertFalse(matches[0].get('noindex'))
        html = PAGE.read_text(encoding='utf-8')
        self.assertIn('href="https://nolankido.com/technology/ai-workflow-pilot/"', html)
        self.assertIn('<h1 class="page-title">How to test an AI workflow before adopting it.</h1>', html)
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        article = json.loads(match.group(1))
        self.assertEqual(article['@type'], 'Article')
        self.assertEqual(article['datePublished'], '2026-11-13')
        self.assertIn('href="/assets/visibility-projects.css?v=', html)
        self.assertNotIn('\u2014', html)
        for anchor in ('pilot-answer', 'pilot-recorded-gap', 'pilot-protocol', 'pilot-example',
                       'pilot-kit', 'pilot-decision'):
            with self.subTest(anchor=anchor):
                self.assertEqual(html.count('id="' + anchor + '"'), 1)
        root = ET.fromstring((ROOT / 'sitemap.xml').read_text(encoding='utf-8'))
        namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        sitemap_hits = [entry for entry in root.findall(namespace + 'url')
                        if entry.findtext(namespace + 'loc') == 'https://nolankido.com' + ROUTE]
        self.assertEqual(len(sitemap_hits), 1)
        self.assertEqual(sitemap_hits[0].findtext(namespace + 'lastmod'), '2026-11-13')
        self.assertIn(ROUTE, (ROOT / 'find/index.html').read_text(encoding='utf-8'))
        self.assertIn(ROUTE, (ROOT / 'technology/feed.xml').read_text(encoding='utf-8'))

    def test_worked_example_and_evidence_limits(self):
        source = (ROOT / '_source/technology/ai-workflow-pilot.html').read_text(encoding='utf-8')
        for token in ('fictional', 'a report that my clients adopted AI', 'quality',
                      '139 minutes', '112 minutes', '172 minutes',
                      'NIST', '/technology/local-ai-test-record/',
                      '/downloads/ai-workflow-pilot-blank.csv',
                      '/downloads/ai-workflow-pilot-example.csv',
                      '/downloads/ai-workflow-pilot-audit.py'):
            with self.subTest(token=token):
                self.assertIn(token.lower(), source.lower())
        self.assertNotIn('\u2014', source)
        for route in ('_source/technology/home.html', '_source/technology/ai-time-savings.html',
                      '_source/projects.html'):
            with self.subTest(route=route):
                self.assertIn(ROUTE, (ROOT / route).read_text(encoding='utf-8'))

    def test_downloaded_inputs_are_anonymous_and_match_article(self):
        self.assertTrue(BLANK.is_file())
        with BLANK.open(encoding='utf-8', newline='') as handle:
            self.assertEqual(len(list(csv.DictReader(handle))), 0)
        with EXAMPLE.open(encoding='utf-8', newline='') as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 6)
        self.assertEqual([row['case_id'] for row in rows], ['P01', 'P02', 'P03', 'P04', 'P05', 'P06'])
        self.assertEqual([row['quality_status'] for row in rows].count('rejected'), 1)
        self.assertEqual(sum(int(row['manual_minutes']) for row in rows), 139)
        self.assertEqual(sum(sum(int(row[field]) for field in
                                 ('ai_preparation_minutes', 'ai_review_minutes', 'ai_repair_minutes'))
                             for row in rows), 112)

    def test_checker_reproduces_totals_and_rejects_bad_input(self):
        checks = [
            ([sys.executable, str(SCRIPT), '--self-test'], 0, 'six invalid-input controls'),
            ([sys.executable, str(SCRIPT), '--input', str(EXAMPLE), '--setup-minutes', '45',
              '--upkeep-minutes', '15'], 0, 'Quality gate: NOT MET'),
            ([sys.executable, str(SCRIPT), '--input', str(EXAMPLE), '--setup-minutes', '45'], 2,
             '--upkeep-minutes'),
        ]
        for command, expected_code, expected_text in checks:
            with self.subTest(command=command):
                result = subprocess.run(command, check=False, capture_output=True, text=True,
                                        cwd=ROOT, timeout=20)
                self.assertEqual(result.returncode, expected_code, result.stderr)
                self.assertIn(expected_text, result.stdout + result.stderr)
                if '--input' in command and '--upkeep-minutes' in command:
                    self.assertIn('Manual task total: 139.00 min', result.stdout)
                    self.assertIn('Assisted total: 172.00 min', result.stdout)
                    self.assertIn('Time difference (manual minus assisted): -33.00 min', result.stdout)


if __name__ == '__main__':
    unittest.main()
