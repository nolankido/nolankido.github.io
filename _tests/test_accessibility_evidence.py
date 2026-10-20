"""Synthetic contract tests, not a human accessibility or usability study."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from accessibility_evidence import accessibility_status, incomplete_evidence, violation_evidence


def fixture():
    return {'violations': [], 'incomplete': [{
        'id': 'color-contrast', 'impact': 'serious',
        'helpUrl': 'https://example.invalid/not-retained',
        'nodes': [{
            'target': ['.lw-quick-start > p:nth-child(2)'],
            'html': '<p>PRIVATE INPUT</p>', 'failureSummary': 'PRIVATE INPUT',
            'any': [{'id': 'color-contrast', 'message': 'PRIVATE INPUT',
                     'data': {'private': 'PRIVATE INPUT'},
                     'relatedNodes': [{'target': ['.lw-quick-start'],
                                       'html': 'PRIVATE INPUT'}]}],
            'all': [], 'none': [],
        }],
    }]}


class AccessibilityEvidenceTests(unittest.TestCase):
    def save(self, result=None, **kwargs):
        options = dict(page_path='/living-well/weekly-reset/', width=1440,
                       scope='.lw-quick-start', javascript=True)
        options.update(kwargs)
        return incomplete_evidence(fixture() if result is None else result, **options)

    def test_unresolved_rule_keeps_context_targets_and_check_ids(self):
        row = self.save()[0]
        self.assertEqual(row['review_status'], 'manual_review_required')
        self.assertEqual(row['width'], 1440)
        self.assertEqual(row['path'], '/living-well/weekly-reset/')
        self.assertEqual(row['scope'], '.lw-quick-start')
        self.assertIs(row['javascript'], True)
        self.assertEqual(row['nodes'][0]['target'], ['.lw-quick-start > p:nth-child(2)'])
        check = row['nodes'][0]['checks']['any'][0]
        self.assertEqual(check['id'], 'color-contrast')
        self.assertEqual(check['related_targets'], [['.lw-quick-start']])

    def test_html_text_messages_data_and_remote_urls_are_not_copied(self):
        text = json.dumps(self.save())
        self.assertNotIn('PRIVATE INPUT', text)
        self.assertNotIn('example.invalid', text)
        self.assertNotIn('html', text)
        self.assertNotIn('failureSummary', text)

    def test_frame_and_shadow_selector_paths_remain_nested(self):
        result = fixture()
        target = ['iframe#sample', ['x-card', 'span.label']]
        result['incomplete'][0]['nodes'][0]['target'] = target
        self.assertEqual(self.save(result)[0]['nodes'][0]['target'], target)

    def test_all_nodes_and_check_groups_are_retained(self):
        result = fixture()
        node = result['incomplete'][0]['nodes'][0]
        node['all'] = [{'id': 'all-check'}]
        node['none'] = [{'id': 'none-check'}]
        result['incomplete'][0]['nodes'].append(deepcopy(node))
        rows = self.save(result)
        self.assertEqual(len(rows[0]['nodes']), 2)
        self.assertEqual(rows[0]['nodes'][0]['checks']['all'][0]['id'], 'all-check')
        self.assertEqual(rows[0]['nodes'][0]['checks']['none'][0]['id'], 'none-check')

    def test_result_is_independent_and_input_remains_unchanged(self):
        original = fixture()
        before = deepcopy(original)
        saved = self.save(original)
        saved[0]['nodes'][0]['target'].append('changed')
        saved[0]['nodes'][0]['checks']['any'][0]['related_targets'][0].append('changed')
        self.assertEqual(original, before)

    def test_no_incomplete_rules_is_an_empty_record_not_an_approval(self):
        self.assertEqual(self.save({'violations': [], 'incomplete': []}), [])
        self.assertEqual(accessibility_status(2, [], []), 'no_automated_findings')

    def test_no_scan_is_not_run_and_never_pass(self):
        self.assertEqual(accessibility_status(0, [], []), 'not_run')

    def test_incomplete_keeps_manual_review_required(self):
        self.assertEqual(accessibility_status(2, [], self.save()), 'manual_review_required')

    def test_violations_have_precedence_over_incomplete(self):
        self.assertEqual(accessibility_status(2, [{'id': 'failure'}], self.save()),
                         'violations_found')

    def test_finding_without_scan_is_rejected(self):
        with self.assertRaises(ValueError):
            accessibility_status(0, [], self.save())

    def test_invalid_scan_counts_or_findings_are_rejected(self):
        for scans in [-1, True, 1.5, '1']:
            with self.subTest(scans=scans), self.assertRaises(ValueError):
                accessibility_status(scans, [], [])
        for violations, incomplete in [(None, []), ([], {}), ('', [])]:
            with self.assertRaises(ValueError):
                accessibility_status(1, violations, incomplete)

    def test_missing_rule_or_node_details_do_not_disappear(self):
        for key in ['id', 'nodes']:
            result = fixture(); del result['incomplete'][0][key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.save(result)
        result = fixture(); result['incomplete'][0]['nodes'] = []
        with self.assertRaises(ValueError): self.save(result)

    def test_bad_result_or_rule_arrays_are_rejected(self):
        for result in [[], {}, {'violations': [], 'incomplete': None},
                       {'violations': {}, 'incomplete': []},
                       {'violations': [], 'incomplete': ['not-an-object']}]:
            with self.subTest(result=result), self.assertRaises(ValueError):
                self.save(result)

    def test_invalid_targets_related_nodes_and_groups_are_rejected(self):
        for target in [None, [], 'p', [''], [[]], [12]]:
            result = fixture(); result['incomplete'][0]['nodes'][0]['target'] = target
            with self.subTest(target=target), self.assertRaises(ValueError):
                self.save(result)
        for value in [None, 'p', [None], [{'target': []}]]:
            result = fixture()
            result['incomplete'][0]['nodes'][0]['any'][0]['relatedNodes'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.save(result)
        result = fixture(); del result['incomplete'][0]['nodes'][0]['all']
        with self.assertRaises(ValueError): self.save(result)

    def test_invalid_context_cannot_mislabel_the_scope(self):
        for path in ['https://example.invalid/', '//host/path', 'relative', '/?q=private', '/#private']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.save(page_path=path)
        for width in [0, -1, True, 1.5]:
            with self.subTest(width=width), self.assertRaises(ValueError):
                self.save(width=width)
        with self.assertRaises(ValueError): self.save(scope='')
        with self.assertRaises(ValueError): self.save(javascript='true')

    def test_null_impact_is_allowed_but_unknown_impact_is_not(self):
        result = fixture(); result['incomplete'][0]['impact'] = None
        self.assertIsNone(self.save(result)[0]['impact'])
        result['incomplete'][0]['impact'] = 'approved'
        with self.assertRaises(ValueError): self.save(result)


    def violation(self, result):
        return violation_evidence(result, page_path='/living-well/weekly-reset/',
            width=1440, scope='.lw-quick-start', javascript=True)

    def test_violation_report_is_projected_without_raw_payload(self):
        result = fixture()
        result['violations'] = result.pop('incomplete')
        result['incomplete'] = []
        saved = self.violation(result)
        self.assertEqual(saved[0]['review_status'], 'automated_violation')
        self.assertEqual(saved[0]['nodes'][0]['target'], ['.lw-quick-start > p:nth-child(2)'])
        for forbidden in ['PRIVATE INPUT', 'example.invalid', 'html', 'message', 'data', 'failureSummary']:
            self.assertNotIn(forbidden, json.dumps(saved))
        self.assertEqual(accessibility_status(1, saved, []), 'violations_found')

    def test_violation_serialization_does_not_mutate_source(self):
        result = fixture()
        result['violations'] = deepcopy(result['incomplete'])
        before = deepcopy(result)
        saved = self.violation(result)
        saved[0]['nodes'][0]['target'].append('changed')
        self.assertEqual(result, before)

    def test_empty_violations_does_not_create_a_false_failure(self):
        self.assertEqual(self.violation(fixture()), [])

    def test_malformed_violation_nodes_do_not_leak_or_disappear(self):
        result = fixture()
        result['violations'] = [{'id': 'color-contrast', 'nodes': [], 'html': 'PRIVATE INPUT'}]
        with self.assertRaises(ValueError): self.violation(result)

    def test_mixed_failures_and_incomplete_stay_separate_and_redacted(self):
        result = fixture()
        result['violations'] = deepcopy(result['incomplete'])
        result['violations'][0]['id'] = 'other-rule'
        violations, incomplete = self.violation(result), self.save(result)
        self.assertEqual([x['id'] for x in violations], ['other-rule'])
        self.assertEqual([x['id'] for x in incomplete], ['color-contrast'])
        self.assertNotIn('PRIVATE INPUT', json.dumps({'violations': violations, 'incomplete': incomplete}))
        self.assertEqual(accessibility_status(2, violations, incomplete), 'violations_found')


if __name__ == '__main__':
    unittest.main()
