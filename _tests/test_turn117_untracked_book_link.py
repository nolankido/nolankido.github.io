"""Offline fixture tests for the six native book links, with one untracked route."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import poker_book_click_path_audit as audit

THIRD = 'books/ai-works-human-decides/index.html'
URLS = {
    'one-workflow-at-a-time': 'https://www.amazon.com/One-Workflow-Time-Nolan-Kido-ebook/dp/B0HRQNCP7Y',
    'how-to-play-no-limit-texas-holdem': 'https://www.amazon.com/Play-Limit-Texas-Holdem-Poker-ebook/dp/B0HSB98324',
    'ai-works-human-decides': 'https://www.amazon.com/Works-Human-Decides-Nolan-Kido-ebook/dp/B0HSF8K76R',
}
TRACKER = '<script defer src="https://cloud.umami.is/script.js" data-do-not-track="true" data-exclude-search="true" data-exclude-hash="true"></script>'


class UntrackedBookLinkTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        ledger = {'works': [], 'supplementary_author_supplied_titles': []}
        for slug, url in URLS.items():
            record = {'author_supplied_product_url': url,
                      'author_supplied_asin': url.rsplit('/', 1)[-1],
                      'source_type': 'author_direct', 'format': 'kindle_ebook'}
            if slug == 'ai-works-human-decides':
                record.update(title='AI Works, Human Decides', retailer_verification_status='not_verified', retail_page_inspected=False)
                ledger['supplementary_author_supplied_titles'].append(record)
            else:
                record['status'] = 'not_verified'
                ledger['works'].append({'slug': slug, 'formats': [record]})
        self.write(audit.LEDGER, json.dumps(ledger))
        self.write(audit.PRIVACY, 'limited Amazon book-link click events. A click is not proof of an Amazon purchase')
        for path, rows in audit.ROUTES.items():
            anchors = []
            for slug, event, source in rows:
                tracking = f' data-umami-event="{event}" data-umami-event-source="{source}"' if event else ''
                anchors.append(f'<a href="{URLS[slug]}" rel="noopener noreferrer"{tracking}>Read</a>')
            self.pair(path, '<html><head><script type="application/ld+json">{}</script>'
                      + (TRACKER if any(row[1] for row in rows) else '')
                      + '</head><body>' + ''.join(anchors) + '</body></html>')

    def write(self, relative, content):
        file = self.root / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding='utf-8')

    def pair(self, path, content):
        self.write(path, content)
        self.write(audit.SOURCE_FILES[path], content)

    def modify(self, path, old, new):
        original = (self.root / path).read_text(encoding='utf-8')
        self.assertIn(old, original)
        self.pair(path, original.replace(old, new, 1))

    def test_six_native_contracts_and_separate_tracking_counts(self):
        report = audit.audit(self.root)
        self.assertEqual(report['status'], 'pass', report['errors'])
        self.assertEqual((report['link_contracts_expected'], report['link_contracts_verified']), (6, 6))
        self.assertEqual((report['tracked_link_contracts_expected'], report['tracked_link_contracts_verified']), (5, 5))
        self.assertEqual((report['untracked_link_contracts_expected'], report['untracked_link_contracts_verified']), (1, 1))
        self.assertEqual(len(report['routes']), 4)
        for key in ('analytics_events_received', 'amazon_detail_page_verified', 'attribution_tag_available', 'kdp_attributed_orders'):
            self.assertIsNone(report[key])

    def test_untracked_link_is_required(self):
        self.modify(THIRD, URLS['ai-works-human-decides'], 'https://example.invalid/')
        report = audit.audit(self.root)
        self.assertEqual(report['status'], 'fail')
        self.assertEqual(report['link_contracts_expected'], 6)
        self.assertEqual(report['untracked_link_contracts_verified'], 0)

    def test_untracked_link_rejects_event_and_event_source_even_without_script(self):
        original = (self.root / THIRD).read_text(encoding='utf-8')
        for injected in ('data-umami-event="ai-works-human-decides-kindle-amazon-click"',
                         'data-umami-event-source="books-catalog"', 'data-umami-event'):
            with self.subTest(injected=injected):
                self.pair(THIRD, original.replace('<a ', '<a ' + injected + ' ', 1))
                self.assertEqual(audit.audit(self.root)['status'], 'fail')

    def test_no_new_tracker_or_executable_script_on_third_page(self):
        original = (self.root / THIRD).read_text(encoding='utf-8')
        for injected in (TRACKER, '<script src="https://example.invalid/tracker.js"></script>',
                         '<script>umami . track ("test")</script>', '<script type="application/ld+json" src="https://example.invalid/data"></script>'):
            with self.subTest(injected=injected):
                self.pair(THIRD, original.replace('</head>', injected + '</head>'))
                self.assertEqual(audit.audit(self.root)['status'], 'fail')

    def test_direct_link_must_have_safe_rel_and_no_handler(self):
        original = (self.root / THIRD).read_text(encoding='utf-8')
        for injected in ('rel="noopener"', 'rel="noopener noreferrer" onmousedown="send()"'):
            with self.subTest(injected=injected):
                self.pair(THIRD, original.replace('rel="noopener noreferrer"', injected))
                self.assertEqual(audit.audit(self.root)['status'], 'fail')

    def test_existing_tracked_page_must_keep_privacy_configuration(self):
        self.modify('books/index.html', 'data-do-not-track="true"', 'data-do-not-track="false"')
        self.assertEqual(audit.audit(self.root)['status'], 'fail')

    def test_duplicate_untracked_link_fails_even_with_source_parity(self):
        url = URLS['ai-works-human-decides']
        self.modify(THIRD, '</body>', f'<a href="{url}" rel="noopener noreferrer">Duplicate</a></body>')
        self.assertEqual(audit.audit(self.root)['status'], 'fail')

    def test_missing_third_page_is_not_a_five_link_pass(self):
        (self.root / THIRD).unlink()
        report = audit.audit(self.root)
        self.assertEqual(report['status'], 'fail')
        self.assertEqual(report['link_contracts_expected'], 6)
        self.assertEqual(report['link_contracts_verified'], 5)


if __name__ == '__main__':
    unittest.main()
