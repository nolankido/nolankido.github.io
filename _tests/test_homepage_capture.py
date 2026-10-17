"""The one-release preparation checker rejects omissions and extra metadata."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('homepage_capture_checks',
    ROOT / '_reports/website-growth/capture_turn02.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class HomepageCaptureTests(unittest.TestCase):
    def setUp(self):
        self.pages = [{'id': 'home', 'path': '/', 'updated': '2026-10-12'},
                      {'id': 'not-found', 'path': '/404.html', 'noindex': True}]
        self.allowed = deepcopy(self.pages)
        self.allowed[0]['updated'] = '2026-10-17'

    def test_only_the_homepage_date_change_is_accepted_without_mutation(self):
        before = deepcopy(self.pages)
        gate.validate_manifests(self.pages, self.allowed)
        self.assertEqual(self.pages, before)

    def test_added_homepage_noindex_or_other_fields_are_rejected(self):
        for field, value in [('noindex', True), ('canonical', 'https://other.example/')]:
            bad = deepcopy(self.allowed); bad[0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                gate.validate_manifests(self.pages, bad)

    def test_missing_fields_changed_values_and_other_pages_are_rejected(self):
        missing = deepcopy(self.allowed); del missing[0]['path']
        wrong = deepcopy(self.allowed); wrong[0]['path'] = '/elsewhere/'
        other = deepcopy(self.allowed); other[1]['noindex'] = False
        for bad in (missing, wrong, other):
            with self.assertRaises(ValueError):
                gate.validate_manifests(self.pages, bad)

    def test_removed_noindex_page_duplicate_and_reordering_are_rejected(self):
        for bad in (self.allowed[:1], self.allowed + [self.allowed[0]], list(reversed(self.allowed))):
            with self.assertRaises(ValueError):
                gate.validate_manifests(self.pages, bad)

    def test_generated_inventory_checks_the_predecessor_not_a_projection(self):
        previous = ['index.html', '404.html', 'feed.xml', 'sitemap.xml']
        gate.validate_output_inventory(previous, list(reversed(previous)))
        for current in (previous[:-1], [p for p in previous if p != '404.html'], previous + ['new.html']):
            with self.assertRaises(ValueError):
                gate.validate_output_inventory(previous, current)

    def test_root_deployment_changes_and_deletions_fail(self):
        static = ['robots.txt', 'CNAME', '.well-known/security.txt', 'favicon.svg',
                  'favicon.png', '_config.yml']
        previous = {p: b'old' for p in gate.PATHS}
        previous.update({p: b'stable' for p in static})
        current = {**previous, **{p: b'new' for p in gate.PATHS}}
        gate.validate_production_scope(previous, current)
        for name in static:
            for bad in ({**current, name: b'changed'},
                        {p: v for p, v in current.items() if p != name}):
                with self.subTest(path=name), self.assertRaises(ValueError):
                    gate.validate_production_scope(previous, bad)
        with self.assertRaises(ValueError):
            gate.validate_production_scope(previous, {**current, 'unreviewed.html': b'new'})

    def test_tests_and_reports_do_not_change_the_deployment_inventory(self):
        previous = {p: b'old' for p in gate.PATHS}
        current = {p: b'new' for p in gate.PATHS}
        current['_tests/test_new.py'] = b'test'
        current['_reports/report.md'] = b'report'
        gate.validate_production_scope(previous, current)


if __name__ == '__main__':
    unittest.main()
