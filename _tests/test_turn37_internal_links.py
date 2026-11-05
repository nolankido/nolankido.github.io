"""Static navigation checks detect real errors without flagging Finder state."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import check_live
import check_internal_links as links
import turn37_link_integrity_history as history
import turn38_home_proof_history as successor


class InternalLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = check_live.targets()
        cls.finder = (ROOT / 'poker/find/index.html').read_text(encoding='utf-8')
        cls.script = (ROOT / 'assets/poker-finder.js').read_text(encoding='utf-8')

    def check_changed_page(self, fragment: str):
        inventory = dict(self.inventory)
        status, original = inventory['/about/']
        inventory['/about/'] = (status, original.replace(
            b'</main>', fragment.encode('utf-8') + b'</main>', 1))
        with patch.object(links.check_live, 'targets', return_value=inventory):
            return links.scan()

    def test_every_registered_public_page_link_and_fragment(self):
        report = links.scan()
        self.assertEqual(report['status'], 'pass')
        self.assertEqual(report['issues'], [])
        self.assertGreaterEqual(report['html_pages'], 200)
        self.assertGreaterEqual(report['internal_links'], 10000)
        self.assertGreaterEqual(report['fragment_links'], 3000)
        self.assertGreaterEqual(report['finder_state_links'], 50)

    def test_advertised_download_is_in_public_byte_inventory(self):
        path = '/downloads/reply-audit-boundary-probes.py'
        self.assertEqual(self.inventory[path], (200, (ROOT / path.lstrip('/')).read_bytes()))
        self.assertIn(path.encode(), (ROOT / 'technology/review-reply-evidence-audit/index.html').read_bytes())

    def test_unknown_route_fails_closed(self):
        report = self.check_changed_page('<a href="/does-not-exist-2026/">Broken</a>')
        self.assertEqual(report['status'], 'fail')
        self.assertIn('unregistered-public-target', [x['reason'] for x in report['issues']])

    def test_unknown_fragment_fails_closed(self):
        report = self.check_changed_page('<a href="#not-an-about-section-999">Broken</a>')
        self.assertEqual(report['status'], 'fail')
        self.assertIn('missing-fragment', [x['reason'] for x in report['issues']])

    def test_duplicate_id_fails_closed(self):
        report = self.check_changed_page('<div id="about-evidence-title">duplicate</div>')
        self.assertEqual(report['status'], 'fail')
        self.assertIn('duplicate-id', [x['reason'] for x in report['issues']])

    def test_real_finder_states_are_not_mistaken_for_dom_anchors(self):
        self.assertTrue(links.is_finder_state('topic=learn&kind=resource', self.finder, self.script))
        self.assertTrue(links.is_finder_state('topic=study', self.finder, self.script))
        self.assertTrue(links.is_finder_state('kind=guide&free=1', self.finder, self.script))
        for fragment in ('topic=not-a-topic', 'kind=other', 'free=0', 'q=private-search',
                         'topic=learn&topic=study', 'topic', ''):
            with self.subTest(fragment=fragment):
                self.assertFalse(links.is_finder_state(fragment, self.finder, self.script))

    def test_filter_exception_requires_actual_existing_script_support(self):
        self.assertFalse(links.is_finder_state('topic=learn', self.finder, ''))
        self.assertFalse(links.is_finder_state('topic=learn', '<select></select>', self.script))
        report = self.check_changed_page('<a href="/poker/find/#topic=not-real">Broken state</a>')
        self.assertEqual(report['status'], 'fail')
        self.assertIn('missing-fragment', [x['reason'] for x in report['issues']])

    def test_external_links_are_ignored_not_fetched(self):
        report = self.check_changed_page('<a href="https://example.org/#anything">Outside</a>')
        self.assertEqual(report['status'], 'pass')
        self.assertEqual(report['issues'], [])


class InternalLinkHistoryTests(unittest.TestCase):
    def test_exact_predecessors_are_rewindable_for_historical_tests(self):
        for name, (old, new) in history.records()['files'].items():
            with self.subTest(path=name):
                current = (ROOT / name).read_bytes()
                prior = subprocess.check_output(['git', 'show', history.PARENT + ':' + name], cwd=ROOT)
                self.assertEqual(history.blob(successor.before(name, current)), new)
                self.assertEqual(history.blob(prior), old)
                self.assertEqual(history.before(name, current), prior)

    def test_unknown_changes_are_not_hidden(self):
        for name in history.records()['files']:
            current = (ROOT / name).read_bytes()
            self.assertEqual(history.before(name, current + b'OTHER'), current + b'OTHER')
            self.assertEqual(history.before('other/' + name, current), current)

    def test_only_exact_new_files_are_identified(self):
        for name, expected in history.records()['added'].items():
            current = (ROOT / name).read_bytes()
            self.assertEqual(history.blob(successor.before(name, current)), expected)
            self.assertTrue(history.is_added_file(name, current))
            self.assertFalse(history.is_added_file(name, current + b'OTHER'))
        self.assertFalse(history.is_added_file('missing.py', b''))

    def test_only_exact_download_is_omitted_from_prior_public_inventory(self):
        route = history.TARGET_ROUTE
        expected = (ROOT / route.lstrip('/')).read_bytes()
        self.assertEqual(history.blob(expected), history.records()['verified_download'])
        self.assertEqual(history.live_targets({route: (200, expected)}), {})
        altered = {route: (200, expected + b'OTHER')}
        self.assertEqual(history.live_targets(altered), altered)
        self.assertEqual(history.live_targets({route: (404, expected)}), {route: (404, expected)})


if __name__ == '__main__':
    unittest.main()
