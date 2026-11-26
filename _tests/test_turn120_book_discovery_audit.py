"""Cross-inventory book metadata and date guards, with offline mutation tests."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
from book_discovery_audit import discovery_errors

BASE = 'https://nolankido.com'
NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'


def records():
    return [
        dict(url=BASE + '/books/', title='Books by Nolan Kido',
             description='Three original nonfiction books.', modified='2026-11-24'),
        dict(url=BASE + '/books/one-workflow-at-a-time/', title='One Workflow at a Time',
             description='A practical AI pilot guide.', modified='2026-11-22'),
        dict(url=BASE + '/books/how-to-play-no-limit-texas-holdem/', title='How to Play No-Limit Texas Hold’em',
             description='A beginner poker guide.', modified='2026-11-22'),
        dict(url=BASE + '/books/ai-works-human-decides/', title='AI Works, Human Decides',
             description='Keep responsibility for AI-assisted tasks.', modified='2026-11-24'),
    ]


def xml(rows):
    root = ET.Element('{' + NS + '}urlset')
    for record in rows:
        url = ET.SubElement(root, '{' + NS + '}url')
        ET.SubElement(url, '{' + NS + '}loc').text = record['url']
        ET.SubElement(url, '{' + NS + '}lastmod').text = record['modified']
    return root


class BookDiscoveryFixtureTests(unittest.TestCase):
    def setUp(self):
        self.rows = records()
        self.sitemap = xml(self.rows)
        self.titles = ['Practical AI Projects', 'About Nolan Kido']
        self.descriptions = ['Explore recorded AI work.', 'Read about the author.']

    def check(self):
        return discovery_errors(self.rows, self.sitemap, self.titles, self.descriptions)

    def test_all_four_exact_records_pass_without_mutation(self):
        original = deepcopy((self.rows, self.titles, self.descriptions))
        sitemap = ET.tostring(self.sitemap)
        self.assertEqual(self.check(), [])
        self.assertEqual((self.rows, self.titles, self.descriptions), original)
        self.assertEqual(ET.tostring(self.sitemap), sitemap)

    def test_generated_page_title_and_description_collisions(self):
        self.titles.append('  AI WORKS,  HUMAN DECIDES ')
        self.descriptions.append('A practical AI pilot guide.')
        issues = self.check()
        self.assertEqual(len(issues), 2)
        self.assertIn(self.rows[3]['url'] + ': book search title is empty or duplicates another page', issues)
        self.assertIn(self.rows[1]['url'] + ': book search description is empty or duplicates another page', issues)

    def test_unicode_compatibility_and_case_variants_are_not_unique(self):
        self.titles.append('ＡＩ Works, Human Decides')
        self.assertIn(self.rows[3]['url'] + ': book search title is empty or duplicates another page', self.check())

    def test_duplicate_book_titles_and_descriptions(self):
        self.rows[0]['title'] = self.rows[1]['title']
        self.rows[2]['description'] = self.rows[3]['description']
        self.assertEqual(len(self.check()), 4)

    def test_missing_and_duplicate_locations(self):
        self.sitemap.remove(self.sitemap[-1])
        self.sitemap.append(deepcopy(self.sitemap[0]))
        issues = self.check()
        self.assertEqual(len(issues), 2)
        self.assertIn(self.rows[3]['url'] + ': book needs exactly one sitemap URL record', issues)
        self.assertIn(self.rows[0]['url'] + ': book needs exactly one sitemap URL record', issues)

    def test_multiple_locs_in_one_record_fail(self):
        ET.SubElement(self.sitemap[1], '{' + NS + '}loc').text = BASE + '/unexpected/'
        self.assertEqual(self.check(), [self.rows[1]['url'] + ': book needs exactly one sitemap URL record'])

    def test_wrong_missing_and_duplicate_lastmod(self):
        self.sitemap[0].find('{*}lastmod').text = '2099-01-01'
        self.sitemap[1].remove(self.sitemap[1].find('{*}lastmod'))
        ET.SubElement(self.sitemap[2], '{' + NS + '}lastmod').text = self.rows[2]['modified']
        self.assertEqual(self.check(), [row['url'] + ': book sitemap lastmod must match the reviewed revision date' for row in self.rows[:3]])

    def test_empty_metadata_fails_and_absent_optional_inventory_is_safe(self):
        self.rows[0]['title'] = ''
        self.rows[1]['description'] = None
        self.assertEqual(len(self.check()), 2)
        self.assertEqual(discovery_errors([], self.sitemap, self.titles, self.descriptions), [])


class BookDiscoveryCheckoutTests(unittest.TestCase):
    def test_current_site_search_audit_enforces_all_book_contracts(self):
        import book_pages
        import build
        import check_search
        report = check_search.audit(ROOT, build.public_pages(), book_pages.ORIGIN)
        self.assertEqual(report['status'], 'pass', report['errors'])
        self.assertEqual(report['manual_book_pages'], len(book_pages.BOOKS))
        self.assertEqual(report['manual_book_hubs'], 1)
        self.assertIn('discovery_errors(', (ROOT / '_scripts/check_search.py').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
