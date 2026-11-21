"""Zero-network regression checks for private first-party visibility scorecards."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'downloads/visibility-private-scorecard.py'
SPEC = importlib.util.spec_from_file_location('visibility_private_scorecard', SCRIPT)
scorecard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scorecard)


class PrivateScorecardTests(unittest.TestCase):
    MONTH = '2026-10'

    def write_json(self, data):
        target = Path(self.tmp.name) / 'private.json'
        target.write_text(json.dumps(data), encoding='utf-8')
        return target

    def setUp(self):
        self.tmp = TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_sources_remain_null_not_zero(self):
        out = scorecard.make_scorecard(self.MONTH, {}, None, None, False)
        self.assertTrue(all(item['value'] is None and item['status'] == 'not_collected'
                            for item in out['metrics'].values()))
        self.assertFalse(out['tool_checked_dashboard_authentication'])

    def test_dashboard_observations_keep_sources_separate(self):
        data = {'month': self.MONTH, 'metrics': {
            'gsc_ai_search_impressions': {'status': 'observed', 'value': 0,
               'property': 'sc-domain:nolankido.com', 'period_verified': True,
               'display_zero_confirmed': True},
            'bing_ai_citations': {'status': 'observed', 'value': 3,
               'property': 'https://nolankido.com/', 'period_verified': True},
            'umami_ai_referral_pageviews': {'status': 'unavailable'},
        }}
        got = scorecard.read_dashboard(self.write_json(data), self.MONTH)
        result = scorecard.make_scorecard(self.MONTH, got, None, None, False)['metrics']
        self.assertEqual(result['gsc_ai_search_impressions'],
                         {'value': 0, 'status': 'observed_operator_confirmed'})
        self.assertEqual(result['bing_ai_citations']['value'], 3)
        self.assertIsNone(result['umami_ai_referral_pageviews']['value'])
        self.assertEqual(result['gsc_ai_discover_impressions']['status'], 'not_collected')

    def test_google_ai_zero_requires_exact_numeric_dashboard_display(self):
        for metric in ('gsc_ai_search_impressions', 'gsc_ai_discover_impressions'):
            item = {'status': 'observed', 'value': 0,
                    'property': 'sc-domain:nolankido.com', 'period_verified': True}
            with self.subTest(metric=metric, scenario='no UI proof'), self.assertRaises(scorecard.IntakeError):
                scorecard.read_dashboard(self.write_json(
                    {'month': self.MONTH, 'metrics': {metric: item}}), self.MONTH)
            for invalid in (False, 'true', 0, None):
                with self.subTest(metric=metric, confirmation=invalid), self.assertRaises(scorecard.IntakeError):
                    scorecard.read_dashboard(self.write_json({
                        'month': self.MONTH, 'metrics': {
                            metric: {**item, 'display_zero_confirmed': invalid}}}), self.MONTH)
            confirmed = {**item, 'display_zero_confirmed': True}
            observed = scorecard.read_dashboard(self.write_json({
                'month': self.MONTH, 'metrics': {metric: confirmed}}), self.MONTH)
            score = scorecard.make_scorecard(self.MONTH, observed, None, None, False)
            self.assertEqual(score['metrics'][metric],
                             {'value': 0, 'status': 'observed_operator_confirmed'})
            # A positive value needs source and period confirmation, not a zero flag.
            positive = {**item, 'value': 11}
            got = scorecard.read_dashboard(self.write_json({
                'month': self.MONTH, 'metrics': {metric: positive}}), self.MONTH)
            self.assertEqual(got[metric]['value'], 11)
            with self.subTest(metric=metric, scenario='surplus zero flag'), self.assertRaises(scorecard.IntakeError):
                scorecard.read_dashboard(self.write_json({
                    'month': self.MONTH, 'metrics': {
                        metric: {**positive, 'display_zero_confirmed': True}}}), self.MONTH)
            missing = scorecard.read_dashboard(self.write_json({
                'month': self.MONTH, 'metrics': {metric: {'status': 'unavailable'}}}), self.MONTH)
            self.assertIsNone(scorecard.make_scorecard(
                self.MONTH, missing, None, None, False)['metrics'][metric]['value'])

    def test_bing_and_umami_zero_counts_do_not_claim_google_display_proof(self):
        for metric, property_name in (
            ('bing_ai_citations', 'https://nolankido.com/'),
            ('umami_ai_referral_pageviews', 'nolankido.com'),
        ):
            entry = {'status': 'observed', 'value': 0, 'property': property_name,
                     'period_verified': True}
            data = {'month': self.MONTH, 'metrics': {metric: entry}}
            self.assertEqual(scorecard.read_dashboard(
                self.write_json(data), self.MONTH)[metric]['value'], 0)
            # Unknown extra fields still fail closed to avoid storing private evidence.
            data['metrics'][metric]['display_zero_confirmed'] = True
            with self.assertRaises(scorecard.IntakeError):
                scorecard.read_dashboard(self.write_json(data), self.MONTH)

    def test_boolean_and_negative_counts_fail(self):
        for bad in (True, -1, '0', 1.5, None):
            data = {'month': self.MONTH, 'metrics': {'bing_ai_citations': {
                'status': 'observed', 'value': bad,
                'property': 'https://nolankido.com/', 'period_verified': True}}}
            with self.subTest(value=bad), self.assertRaises(scorecard.IntakeError):
                scorecard.read_dashboard(self.write_json(data), self.MONTH)

    def test_wrong_property_and_unconfirmed_date_fail(self):
        for prop, confirmed in [('https://another.example/', True),
                                ('https://nolankido.com/', False)]:
            data = {'month': self.MONTH, 'metrics': {'bing_ai_citations': {
                'status': 'observed', 'value': 3, 'property': prop,
                'period_verified': confirmed}}}
            with self.subTest(property=prop, confirmed=confirmed), self.assertRaises(scorecard.IntakeError):
                scorecard.read_dashboard(self.write_json(data), self.MONTH)

    def test_no_invented_zero_for_unavailable_or_not_checked(self):
        for rec in ({'status': 'unavailable', 'value': 0},
                    {'status': 'not_checked', 'value': 0},
                    {'status': 'observed', 'value': 0}):
            data = {'month': self.MONTH, 'metrics': {'bing_ai_citations': rec}}
            with self.assertRaises(scorecard.IntakeError):
                scorecard.read_dashboard(self.write_json(data), self.MONTH)

    def test_rejects_wrong_month_and_extra_private_fields(self):
        for obj in ({'month': '2026-09', 'metrics': {}},
                    {'month': self.MONTH, 'metrics': {}, 'raw_queries': ['secret']},
                    {'month': self.MONTH, 'metrics': {'private_user': {}}}):
            with self.assertRaises(scorecard.IntakeError):
                scorecard.read_dashboard(self.write_json(obj), self.MONTH)

    def test_gsc_requires_verified_property_and_filters(self):
        gsc = {'month': self.MONTH, 'values': {'property_web_clicks': 5,
                 'property_web_impressions': 100,
                 'technology_exported_page_clicks': 4}}
        unverified = scorecard.make_scorecard(self.MONTH, {}, gsc,
                                              'sc-domain:nolankido.com', False)
        self.assertIsNone(unverified['metrics']['gsc_web_clicks']['value'])
        self.assertEqual(unverified['metrics']['gsc_web_clicks']['status'], 'source_unconfirmed')
        confirmed = scorecard.make_scorecard(self.MONTH, {}, gsc,
                                             'sc-domain:nolankido.com', True)
        self.assertEqual(confirmed['metrics']['gsc_web_clicks']['value'], 5)
        self.assertEqual(confirmed['metrics']['technology_exported_page_clicks']['value'], 4)
        with self.assertRaises(scorecard.IntakeError):
            scorecard.make_scorecard(self.MONTH, {}, gsc, 'sc-domain:another.com', True)

    def test_gsc_missing_chart_is_not_property_zero(self):
        gsc = {'month': self.MONTH, 'values': {'property_web_clicks': None,
                 'property_web_impressions': None,
                 'technology_exported_page_clicks': 4}}
        out = scorecard.make_scorecard(self.MONTH, {}, gsc,
                                       'sc-domain:nolankido.com', True)
        self.assertIsNone(out['metrics']['gsc_web_clicks']['value'])
        self.assertEqual(out['metrics']['gsc_web_clicks']['status'], 'not_available')

    def test_cli_with_no_inputs_emits_private_safe_nulls(self):
        p = subprocess.run([sys.executable, str(SCRIPT), '--month', self.MONTH],
                           text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(p.stdout)['month'], self.MONTH)
        self.assertNotIn(str(self.tmp.name), p.stdout)
        self.assertNotIn('private query', p.stdout)

    def test_cli_fails_closed_on_private_bad_json_without_leaking(self):
        target = Path(self.tmp.name) / 'SECRET-file.json'
        target.write_text('{not valid json', encoding='utf-8')
        p = subprocess.run([sys.executable, str(SCRIPT), '--month', self.MONTH,
                            '--dashboard-json', str(target)],
                           text=True, capture_output=True)
        self.assertEqual(p.returncode, 2)
        self.assertNotIn('SECRET-file.json', p.stderr)
        self.assertNotIn('{not valid json', p.stderr)


if __name__ == '__main__':
    unittest.main()
