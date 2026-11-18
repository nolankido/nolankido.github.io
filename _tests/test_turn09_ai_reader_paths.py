"""Protect Turn 09's public local-AI evidence and reader paths."""
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import audit_ai_reader_paths
import check_internal_links


class TestAiReaderPaths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = audit_ai_reader_paths.scan(ROOT)

    def test_target_registry_and_content_links(self):
        self.assertEqual(self.audit['status'], 'pass', self.audit)
        self.assertEqual(self.audit['expected_links_missing'], [])
        self.assertEqual(self.audit['inaccessible_targets'], [])

    def test_comparison_protocol_reachable_without_extra_hops(self):
        by_route = {row['route']: row for row in self.audit['targets']}
        protocol = by_route['/downloads/local-hosted-ai-comparison-protocol.md']
        worksheet = by_route['/downloads/local-hosted-ai-comparison-blank.csv']
        self.assertEqual(protocol['clicks_from_technology'], 1)
        self.assertLessEqual(protocol['clicks_from_home'], 2)
        self.assertLessEqual(worksheet['clicks_from_technology'], 2)
        self.assertGreaterEqual(protocol['content_pages_linking_here'], 4)

    def test_all_public_internal_links_have_registered_targets(self):
        report = check_internal_links.scan(ROOT)
        self.assertEqual(report['status'], 'pass', report['issues'][:10])

    def test_synthetic_operations_case_is_traceable_and_honestly_labeled(self):
        case = json.loads((ROOT / 'downloads/ai-operations-exception-source.json').read_text(encoding='utf-8'))
        notes = {note['id']: note for note in case['notes']}
        self.assertEqual(set(notes), {'S1', 'S2', 'S3'})
        self.assertTrue(case['fictional'])
        self.assertFalse(case['client_or_business_records'])
        self.assertEqual(case['model_execution'], 'not_performed')
        self.assertEqual(case['draft_provenance'], 'deliberately_constructed_illustrative_counterexample')
        self.assertEqual(notes['S1']['quantity_requested'] - notes['S2']['on_hand'], 30)
        self.assertFalse(notes['S1']['pickup_confirmed'])
        self.assertFalse(notes['S2']['supplier_arrival_confirmed'])
        self.assertFalse(notes['S3']['manager_approval_recorded'])
        self.assertFalse(notes['S3']['partial_delivery_customer_agreement_recorded'])
        self.assertEqual(case['fictional_reviewer_decision']['outcome'], 'reject_and_revise')
        page = (ROOT / 'technology/ai-workflow-pilot/index.html').read_text(encoding='utf-8')
        self.assertIn('id="pilot-exception-case"', page)
        self.assertIn('Entirely fictional teaching exercise', page)
        self.assertIn('No actual model produced', ' '.join(case['limitations']))
        self.assertIn('/downloads/ai-operations-exception-source.json', page)
        self.assertIn('/downloads/ai-operations-exception-worksheet.md', page)


if __name__ == '__main__':
    unittest.main()
