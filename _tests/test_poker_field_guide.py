"""Field-guide publishing, exact worksheet previews and independent arithmetic."""
from fractions import Fraction
from pathlib import Path
from xml.etree import ElementTree as ET
import html
import unittest
from test_site import ROOT, Page, build
import check_live
import poker_library

GUIDES = ('first-live-tournament', 'choosing-a-tournament', 'registration-and-reentry', 'tournament-day', 'recording-hands', 'choosing-study-tools', 'evaluating-poker-advice')
SHEETS = ('poker-event-planner', 'poker-hand-capture', 'poker-resource-check')

class FieldGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.pages = build.public_pages()
        cls.entries = poker_library.load(ROOT, cls.pages)

    def content(self, slug):
        return self.outputs[Path('poker') / slug / 'index.html']

    def test_every_new_guide_is_discoverable_published_and_verified(self):
        hub = self.content('live-tournament-guide')
        feed = ET.fromstring(self.outputs[Path('poker/feed.xml')])
        urls = {entry.findtext('link') for entry in feed.findall('./channel/item')}
        for slug in GUIDES:
            route = '/poker/' + slug + '/'
            page = next(p for p in self.pages if p['path'] == route)
            self.assertTrue(page['poker_guide'])
            self.assertEqual(page['date'], '2026-10-08')
            for output in [hub, self.content('library'), self.outputs[Path('sitemap.xml')]]:
                self.assertIn(route, output)
            self.assertIn('https://nolankido.com' + route, urls)
            self.assertIn(route, check_live.targets())
            content = self.content(slug)
            self.assertIn('Prepared with AI assistance.', content)
            self.assertIn('fictional', content)
            self.assertIn('id="guide-sources"', content)
            self.assertIn('https://', content)
            self.assertIn('reader-outline', content)
        expected = {p['path'] for p in self.pages if p.get('poker_guide')} | {'/poker/reviewing-a-hand/'}
        self.assertEqual({e['route'] for e in self.entries}, expected)
        self.assertEqual(sum(e['topic'] == 'live' for e in self.entries if e['slug'] in GUIDES), 5)

    def test_sheet_styles_are_scoped_and_live_verified(self):
        for path, content in self.outputs.items():
            if path.suffix == '.html':
                self.assertEqual('/assets/poker-fieldguide.css?v=' in content,
                                 path == Path('poker/tournament-checklists/index.html'))
        self.assertIn('/assets/poker-fieldguide.css', check_live.targets())
        css = (ROOT / 'assets/poker-fieldguide.css').read_text()
        self.assertIn('white-space:pre-wrap', css)
        self.assertIn('@media print', css)

    def test_sheets_share_the_exact_downloaded_blank_text(self):
        content = self.content('tournament-checklists')
        for slug in SHEETS:
            blank = (ROOT / 'downloads' / (slug + '.md')).read_text()
            self.assertIn('<pre class="field-sheet">' + html.escape(blank, quote=True) + '</pre>', content)
            self.assertIn('/downloads/' + slug + '.md', check_live.targets())
            self.assertIn('Blank private-use', blank)
        self.assertNotIn('<form', content)
        self.assertNotIn('<input', content)
        self.assertNotIn('<textarea', content)
        self.assertNotIn('<details', content)

    def test_hubs_remain_distinct_from_guides_and_personal_accounts(self):
        for slug in ['live-tournament-guide', 'tournament-checklists']:
            page = next(p for p in self.pages if p['path'] == '/poker/' + slug + '/')
            self.assertFalse(page.get('poker_guide'))
        personal_slugs = {entry['slug'] for entry in build.poker_content.load(ROOT)['entries']}
        self.assertTrue(set(GUIDES).isdisjoint(personal_slugs))
        for path in ['poker/index.html', 'poker/library/index.html', 'poker/study/index.html', 'poker/start-here/index.html']:
            self.assertIn('/poker/live-tournament-guide/', self.outputs[Path(path)])
        self.assertIn('/poker/choosing-study-tools/', self.content('resources'))
        self.assertIn('/poker/evaluating-poker-advice/', self.content('resources'))

    def test_structure_and_fee_examples_are_independently_correct(self):
        self.assertEqual(Fraction(30000, 200), 150)
        self.assertEqual(Fraction(50000, 500), 100)
        self.assertEqual(Fraction(30000, 400), 75)
        self.assertEqual(round(50000 / 1200, 1), 41.7)
        self.assertEqual(round(100 * 50 / (250 + 50), 1), 16.7)
        self.assertEqual(100 * Fraction(50, 250), 20)
        content = self.content('choosing-a-tournament')
        for text in ['150 BB', '100 BB', '75 BB', '41.7 BB', '16.7%', '20%']:
            self.assertIn(text, content)
        self.assertIn('Fictional comparison', content)

    def test_reentry_ledger_counts_all_payments(self):
        entries = 2 * 300
        outing = entries + 90
        self.assertEqual((entries, outing, 500 - entries, 500 - outing), (600, 690, -100, -190))
        content = self.content('registration-and-reentry')
        for text in ['$600', '$690', '$100 tournament loss', '$190 loss']:
            self.assertIn(text, content)
        self.assertIn('ceilings, not targets', content)
        self.assertIn('https://www.ncpgambling.org/help-treatment/', content)

    def test_hand_note_ledger_and_net_gain_agree(self):
        posted = {'small_blind': 500, 'big_blind': 1000, 'ante': 1000}
        raise_total = 2200
        extra_call = raise_total - posted['big_blind']
        contested = sum(posted.values()) + raise_total + extra_call
        uncalled = 1800
        button_start = 32000
        button_end = button_start - raise_total - uncalled + contested + uncalled
        self.assertEqual((extra_call, contested, button_end - button_start), (1200, 5900, 3700))
        self.assertEqual((button_end - button_start) - (raise_total + posted['ante']) - posted['small_blind'], 0)
        content = self.content('recording-hands')
        for text in ['5,900', '3,700', 'uncalled', 'not one of Nolan']:
            self.assertIn(text, content)

    def test_no_runtime_forms_tracking_or_typographic_em_dashes_added(self):
        for slug in list(GUIDES) + ['live-tournament-guide', 'tournament-checklists']:
            source = (ROOT / '_source/poker' / (slug + '.html')).read_text()
            for forbidden in ['<script', '<form', '<iframe', '<input', '<textarea', 'data-umami-event', chr(0x2014)]:
                self.assertNotIn(forbidden, source)
            parsed = Page(self.content(slug))
            ids = [attrs['id'] for _, attrs in parsed.elements if 'id' in attrs]
            self.assertEqual(len(ids), len(set(ids)))

if __name__ == '__main__':
    unittest.main(verbosity=2)
