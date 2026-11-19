"""Turn 19: frozen answer discovery panel, human observations and privacy gates."""

import csv
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'downloads/ai-answer-sprint-25-audit.py'
PANEL = ROOT / 'downloads/ai-answer-sprint-25-prompts.csv'
BLANK = ROOT / 'downloads/ai-answer-sprint-25-blank.csv'
FROZEN = ROOT / '_reports/visibility-sprint/assistant-answer-panel-v1-2026-11-17.csv'

spec = importlib.util.spec_from_file_location('answer_sprint_25', SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

sys.path.insert(0, str(ROOT / '_scripts'))
import check_live


def row(prompt, *, date='2026-11-18', assistant='Example', mode='Web', status='completed',
        cited='no', url='', mentioned='no', correct='verified', completed='yes'):
    if status != 'completed':
        cited, url, mentioned, correct, completed = '', '', '', '', ''
    return [date, prompt, assistant, mode, status, cited, url, mentioned, correct, completed]


def csv_text(rows):
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(audit.OBSERVATION_FIELDS)
    writer.writerows(rows)
    return out.getvalue()


class FrozenAnswerPanelTests(unittest.TestCase):
    def test_freeze_matches_sprint_original_and_real_paths(self):
        self.assertEqual(PANEL.read_bytes(), FROZEN.read_bytes())
        prompts = audit.load_prompts(PANEL)
        self.assertEqual(len(prompts), 25)
        self.assertEqual(sum(p['segment'] == 'nonbranded' for p in prompts.values()), 20)
        self.assertEqual(sum(p['segment'] == 'branded' for p in prompts.values()), 5)
        self.assertEqual(prompts['NB01']['expected_url_path'], '/technology/check-ai-answers/')
        self.assertEqual(prompts['BR01']['expected_url_path'], '/about/')
        self.assertEqual(prompts['BR02']['expected_url_path'], '/projects/')
        for p in prompts.values():
            self.assertTrue((ROOT / p['expected_url_path'].lstrip('/') / 'index.html').exists())

    def test_read_only_targets_and_blank_missing_is_not_zero(self):
        targets = check_live.targets()
        for path in (SCRIPT, PANEL, BLANK):
            route = '/' + str(path.relative_to(ROOT)).replace('\\', '/')
            self.assertEqual(targets[route], (200, path.read_bytes()))
        self.assertEqual(BLANK.read_text().strip(), ','.join(audit.OBSERVATION_FIELDS))
        result = audit.summarize([], '2026-11', 2, audit.load_prompts(PANEL))
        self.assertEqual(result['status'], 'no_completed_trials')
        self.assertEqual(result['coverage']['missing_rows'], 50)
        self.assertIsNone(result['segments']['nonbranded']['sample_fraction'])
        self.assertIsNone(result['segments']['branded']['sample_fraction'])
        self.assertEqual(result['segments']['nonbranded']['uncompleted_or_missing'], 40)
        self.assertEqual(result['segments']['branded']['uncompleted_or_missing'], 10)

    def test_synthetic_partial_trial_keeps_brand_and_expected_page_separate(self):
        rows = [
            row('NB01', cited='yes', url='https://nolankido.com/technology/check-ai-answers/#check-method'),
            row('NB02', cited='yes', url='https://nolankido.com/about/'),
            row('NB03', mentioned='yes', correct='incorrect', completed='no'),
            row('NB04', status='incomplete'),
            row('BR01', cited='yes', url='https://www.nolankido.com/about/#about-evidence-title'),
            row('BR02', mentioned='yes', correct='partial', completed='partial'),
        ]
        with tempfile.TemporaryDirectory() as temp:
            private_file = Path(temp) / 'private.csv'
            private_file.write_text(csv_text(rows), encoding='utf-8')
            observed = audit.load_observations(private_file, '2026-11', audit.load_prompts(PANEL))
            result = audit.summarize(observed, '2026-11', 1, audit.load_prompts(PANEL))
            self.assertEqual(result['coverage']['completed_trials'], 5)
            self.assertEqual(result['coverage']['uncompleted_or_missing'], 20)
            self.assertEqual(result['coverage']['incomplete_rows'], 1)
            nb = result['segments']['nonbranded']
            self.assertEqual((nb['completed_trials'], nb['cited_trials'], nb['expected_page_cited_trials'],
                              nb['other_site_page_cited_trials'], nb['text_only_mentions']), (3, 2, 1, 1, 1))
            self.assertEqual(nb['sample_percent'], 66.67)
            branded = result['segments']['branded']
            self.assertEqual((branded['completed_trials'], branded['cited_trials'],
                              branded['expected_page_cited_trials'], branded['text_only_mentions']), (2, 1, 1, 1))
            self.assertEqual(branded['sample_percent'], 50)
            self.assertNotIn('https://nolankido.com/about/', json.dumps(result))

    def test_complete_fictional_panel_uses_twenty_and_five_denominators(self):
        prompts = audit.load_prompts(PANEL)
        rows = []
        for ident, meta in prompts.items():
            cited = ident in ('NB01', 'BR01')
            rows.append(row(ident, cited='yes' if cited else 'no',
                            url='https://nolankido.com' + meta['expected_url_path'] if cited else ''))
        with tempfile.TemporaryDirectory() as temp:
            private_file = Path(temp) / 'fictional.csv'
            private_file.write_text(csv_text(rows), encoding='utf-8')
            result = audit.summarize(
                audit.load_observations(private_file, '2026-11', prompts), '2026-11', 1, prompts)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['coverage']['completed_trials'], 25)
        self.assertEqual(result['segments']['nonbranded']['sample_percent'], 5)
        self.assertEqual(result['segments']['branded']['sample_percent'], 20)
        self.assertEqual(result['segments']['nonbranded']['expected_page_cited_trials'], 1)
        self.assertEqual(result['segments']['branded']['expected_page_cited_trials'], 1)

    def test_rejects_spoofs_duplicates_invalid_outcomes_and_prompt_edits(self):
        valid = row('NB01', cited='yes', url='https://nolankido.com/technology/check-ai-answers/')
        cases = [
            [row('NB01', cited='yes', url='https://nolankido.com.attacker.example/about/')],
            [row('NB01', cited='yes', url='http://nolankido.com/about/')],
            [row('NB01', cited='yes', url='https://person@nolankido.com/about/')],
            [row('NB01', cited='no', url='https://nolankido.com/about/')],
            [row('NB01', cited='yes', url='https://nolankido.com/about/', mentioned='yes')],
            [row('NB99')],
            [row('NB01', date='2026-10-18')],
            [row('NB01', status='incomplete')[:-1] + ['yes']],
            [valid, valid],
        ]
        with tempfile.TemporaryDirectory() as temp:
            private_file = Path(temp) / 'private.csv'
            for rows in cases:
                with self.subTest(case=rows):
                    private_file.write_text(csv_text(rows), encoding='utf-8')
                    with self.assertRaises(audit.InvalidPanel):
                        audit.load_observations(private_file, '2026-11', audit.load_prompts(PANEL))
            modified = Path(temp) / 'tampered-prompts.csv'
            modified.write_bytes(PANEL.read_bytes().replace(b'What can a small', b'How can a small', 1))
            with self.assertRaisesRegex(audit.InvalidPanel, 'differs from frozen'):
                audit.load_prompts(modified)
        with self.assertRaises(audit.InvalidPanel):
            audit.summarize([dict(zip(audit.OBSERVATION_FIELDS, valid))], '2026-11', 0, audit.load_prompts(PANEL))

    def test_public_answer_and_resource_routes_are_present_and_dated(self):
        source = (ROOT / '_source/technology/ai-website-visibility.html').read_text()
        published = (ROOT / 'technology/ai-website-visibility/index.html').read_text()
        for html in (source, published):
            self.assertEqual(html.count('id="ai-answer-sprint-panel"'), 1)
            self.assertIn('href="#ai-answer-sprint-panel"', html)
            self.assertIn('Freeze the questions before testing', html)
            self.assertIn('sample_fraction: null', html)
            self.assertIn('eight unbranded questions', html)
            for name in (SCRIPT.name, PANEL.name, BLANK.name):
                self.assertIn('href="/downloads/' + name + '" download', html)
        self.assertIn('href="https://nolankido.com/technology/ai-website-visibility/"', published)
        for path in ('_source/resources.html', 'resources/index.html',
                     '_source/technology/home.html', 'technology/index.html'):
            self.assertIn('href="/technology/ai-website-visibility/#ai-answer-sprint-panel"',
                          (ROOT / path).read_text(), path)
        records = json.loads((ROOT / '_source/pages.json').read_text())
        case = next(p for p in records if p['id'] == 'ai-website-visibility')
        self.assertEqual(case['date'], '2026-11-03')
        self.assertGreaterEqual(case['updated'], '2026-11-18')
        for path in (SCRIPT, PANEL, BLANK):
            self.assertNotIn('—', path.read_text())

    def test_older_eight_prompt_method_still_passes_its_fictional_sample(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'downloads/ai-citation-panel-audit.py'),
             '--month', '2026-10', '--expected-trials', '16',
             '--csv', str(ROOT / 'downloads/ai-citation-panel-synthetic.csv')],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        observed = json.loads(result.stdout)
        self.assertEqual(observed['coverage']['completed_trials'], 16)
        self.assertEqual(observed['citations']['cited_trials'], 2)
        self.assertEqual(observed['citations']['sample_percent'], 12.5)


if __name__ == '__main__':
    unittest.main()
