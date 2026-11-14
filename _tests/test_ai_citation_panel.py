"""No-network regression coverage for the manual AI citation panel checker."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'downloads/ai-citation-panel-audit.py'
spec = importlib.util.spec_from_file_location('ai_citation_panel_audit', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
FIELDS = module.FIELDS


def sample():
    rows = []
    for assistant in ('ChatGPT Search', 'Perplexity'):
        for prompt in range(1, 9):
            cited = (assistant == 'ChatGPT Search' and prompt == 2) or (assistant == 'Perplexity' and prompt == 6)
            rows.append(dict(date='2026-10-15', prompt_id=str(prompt), assistant=assistant, mode='Search',
                             status='completed', clickable_link_verified='yes' if cited else 'no',
                             linked_url='https://nolankido.com/technology/task-brief/' if cited else '',
                             text_only_mention='yes' if assistant == 'ChatGPT Search' and prompt == 3 else 'no'))
    return rows


class CitationPanelTests(unittest.TestCase):
    def test_complete_synthetic_panel(self):
        r = module.summarize(sample(), '2026-10', 16)
        self.assertEqual(r['status'], 'complete')
        self.assertEqual(r['citations']['cited_trials'], 2)
        self.assertEqual(r['citations']['sample_percent'], 12.5)
        self.assertEqual(r['citations']['text_only_mentions'], 1)
        self.assertEqual(r['coverage']['missing_rows'], 0)
        self.assertEqual(r['coverage']['completed_trials'], 16)
        self.assertEqual(len(r['observed_modes']), 2)
        self.assertNotIn('https://nolankido.com/technology/task-brief/', json.dumps(r))

    def test_incomplete_excluded_from_denominator(self):
        rows = sample()
        rows[0]['status'] = 'incomplete'
        rows[0]['clickable_link_verified'] = 'no'
        rows[0]['linked_url'] = ''
        r = module.summarize(rows, '2026-10', 16)
        self.assertEqual(r['status'], 'partial')
        self.assertEqual(r['citations']['completed_eligible_trials'], 15)
        self.assertEqual(r['citations']['cited_trials'], 2)
        self.assertEqual(r['citations']['sample_percent'], 13.33)
        self.assertEqual(r['coverage']['uncompleted_or_missing'], 1)

    def test_missing_rows_are_not_misses(self):
        r = module.summarize(sample()[:7], '2026-10', 16)
        self.assertEqual(r['coverage']['missing_rows'], 9)
        self.assertEqual(r['citations']['completed_eligible_trials'], 7)

    def test_no_completed_is_unknown_not_zero_rate(self):
        rows = sample()[:2]
        for row in rows:
            row.update(status='not_checked', linked_url='', clickable_link_verified='no', text_only_mention='no')
        r = module.summarize(rows, '2026-10', 8)
        self.assertEqual(r['status'], 'no_completed_trials')
        self.assertIsNone(r['citations']['sample_fraction'])
        self.assertIsNone(r['citations']['sample_percent'])

    def test_strict_host_no_lookalikes(self):
        for url in ['https://nolankido.com.evil.test/path', 'http://nolankido.com/',
                    'https://other.test/?u=nolankido.com', 'https://nolankido.com@evil.test/path',
                    'https://nolankido.com:8443/path', 'javascript:alert(1)',
                    'https://nolankido.com/\nFoo', 'https://other.nolankido.com/']:
            with self.subTest(url=url):
                self.assertFalse(module.verified_site_link(url))
        self.assertTrue(module.verified_site_link('https://nolankido.com/technology/'))
        self.assertTrue(module.verified_site_link('https://www.nolankido.com/'))

    def test_expected_trials_bounds(self):
        for count in (0, 7, 9, 161):
            with self.assertRaises(module.InvalidPanel):
                module.summarize([], '2026-10', count)

    def test_too_many_modes_rejected(self):
        rows = sample()
        with self.assertRaises(module.InvalidPanel):
            module.summarize(rows, '2026-10', 8)

    def test_inconsistent_mode_spelling_rejected(self):
        rows = sample()[:8]
        rows[-1]['assistant'] = 'chatgpt search'
        with self.assertRaises(module.InvalidPanel):
            module.summarize(rows, '2026-10', 8)

    def test_empty_log_no_fabricated_results(self):
        r = module.summarize([], '2026-10', 16)
        self.assertIsNone(r['citations']['sample_percent'])
        self.assertEqual(r['coverage']['missing_rows'], 16)

    def test_rows_and_citation_bounds_via_cli(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'log.csv'
            self.write_csv(path, sample())
            res = subprocess.run([sys.executable, str(SCRIPT), '--month', '2026-10',
                                  '--expected-trials', '16', '--csv', str(path)],
                                 capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, res.stderr)
            result = json.loads(res.stdout)
            self.assertEqual(result['citations']['sample_percent'], 12.5)
            self.assertNotIn('https://nolankido.com/technology/task-brief/', res.stdout)

    def test_public_synthetic_csv_is_reproducible(self):
        source = ROOT / 'downloads/ai-citation-panel-synthetic.csv'
        rows = module.parse_csv(source, '2026-10')
        r = module.summarize(rows, '2026-10', 16)
        self.assertEqual(r['citations']['sample_percent'], 12.5)
        self.assertEqual(r['citations']['text_only_mentions'], 1)
        self.assertEqual(r['coverage']['recorded_rows'], 16)

    def test_blank_csv_represents_no_observations(self):
        source = ROOT / 'downloads/ai-citation-panel-blank.csv'
        rows = module.parse_csv(source, '2026-10')
        self.assertEqual(rows, [])
        r = module.summarize(rows, '2026-10', 16)
        self.assertIsNone(r['citations']['sample_percent'])

    def test_invalid_csv_variants(self):
        variants = []
        row = sample()[0]
        for replacement in (
            {'date': '2026-09-15'}, {'date': '20261015'},
            {'prompt_id': '9'}, {'status': 'unknown'},
            {'clickable_link_verified': 'maybe'},
            {'clickable_link_verified': 'yes', 'linked_url': ''},
            {'clickable_link_verified': 'no', 'linked_url': 'https://nolankido.com/'},
            {'status': 'incomplete', 'clickable_link_verified': 'yes', 'linked_url': 'https://nolankido.com/'},
            {'clickable_link_verified': 'yes', 'linked_url': 'https://nolankido.com.evil.test/'},
            {'clickable_link_verified': 'yes', 'linked_url': 'https://nolankido.com/', 'text_only_mention': 'yes'},
            {'assistant': 'bad\nlabel'},
        ):
            variants.append({**row, **replacement})
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'log.csv'
            for variant in variants:
                with self.subTest(variant=variant):
                    self.write_csv(path, [variant])
                    with self.assertRaises(module.InvalidPanel):
                        module.parse_csv(path, '2026-10')

    def test_duplicate_trial_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'log.csv'
            self.write_csv(path, sample()[:1] * 2)
            with self.assertRaisesRegex(module.InvalidPanel, 'repeated'):
                module.parse_csv(path, '2026-10')

    def test_malformed_csv_header_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'log.csv'
            path.write_text('assistant,mode\nChatGPT Search,Search\n')
            with self.assertRaisesRegex(module.InvalidPanel, 'headers'):
                module.parse_csv(path, '2026-10')

    @staticmethod
    def write_csv(path, rows):
        with path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)


if __name__ == '__main__':
    unittest.main()
