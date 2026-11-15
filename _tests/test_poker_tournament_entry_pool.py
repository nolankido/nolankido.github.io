"""Turn 14: independent tests for tournament entry, fee and prize-pool accounting."""

from decimal import Decimal
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph


def event_buckets(paid_entries, ordinary, bounty, fee):
    """Compute event receipts and obligations from independently provided units."""
    counts = tuple(Decimal(str(amount)) * paid_entries
                   for amount in (ordinary, bounty, fee))
    return sum(counts), counts


class TournamentEntryPoolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slug = 'tournament-entry-prize-pool-ledger'
        cls.route = f'/poker/{cls.slug}/'
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']
        cls.source = (ROOT / '_source/poker' / (cls.slug + '.html')).read_text()

    def test_single_canonical_source_and_discovery(self):
        records = [page for page in self.pages if page['path'] == self.route]
        self.assertEqual(len(records), 1)
        self.assertTrue(records[0]['poker_guide'])
        self.assertEqual(records[0]['date'], '2026-11-15')
        self.assertIn('https://nolankido.com' + self.route, self.article)
        self.assertIn('"datePublished": "2026-11-15"', self.article)
        for filename in ('poker/library/index.html', 'poker/find/index.html',
                         'poker/topics/tournaments/index.html',
                         'poker/topics/places-to-play/index.html',
                         'poker/feed.xml', 'writing.xml', 'sitemap.xml'):
            self.assertIn(self.route, self.outputs[Path(filename)], filename)

    def test_regular_event_equal_price_entries_reconcile(self):
        unique_people, reentries = 100, 20
        paid_entries = unique_people + reentries
        total, (ordinary, bounty, fees) = event_buckets(paid_entries, 330, 0, 70)
        self.assertEqual(paid_entries, 120)
        self.assertEqual((total, ordinary, bounty, fees), (48000, 39600, 0, 8400))
        self.assertEqual(ordinary + fees, 48000)
        for text in ('$48,000', '$39,600', '$8,400', '100 unique players',
                     '20 of them re-enter exactly once'):
            self.assertIn(text, self.source)

    def test_fee_percent_denominators_are_distinct(self):
        fee = Decimal(70)
        full = Decimal(400)
        ordinary = Decimal(330)
        self.assertEqual(fee / full * 100, Decimal('17.5'))
        self.assertTrue(Decimal('21.21') < fee / ordinary * 100 < Decimal('21.22'))
        self.assertIn('17.5% of the $400 total entry', self.source)
        self.assertIn('21.21% of the $330 ordinary prize contribution', self.source)

    def test_guarantee_overlay_and_total_funding_conserve_money(self):
        contributions = 120 * 330
        guarantee = 50000
        overlay = max(0, guarantee - contributions)
        self.assertEqual(overlay, 10400)
        self.assertEqual(48000 + overlay, guarantee + 120 * 70)
        self.assertEqual(48000 + overlay, 58400)
        self.assertIn('$10,400 overlay', self.source)
        self.assertIn('$58,400', self.source)
        self.assertIn('ordinary finishing-position prizes, explicitly excluding fees and bounties', self.source)

    def test_whole_entry_threshold_for_defined_guarantee(self):
        ordinary_contribution = 330
        guarantee = 50000
        threshold = (guarantee + ordinary_contribution - 1) // ordinary_contribution
        self.assertEqual(threshold, 152)
        self.assertEqual((threshold - 1) * ordinary_contribution, 49830)
        self.assertEqual(threshold * ordinary_contribution, 50160)
        self.assertIn('151 entries × $330 = $49,830', self.source)
        self.assertIn('152 entries × $330 = $50,160', self.source)
        self.assertIn('different calculation is required', self.source)

    def test_entire_payout_ladder_uses_only_base_ordinary_pool(self):
        payouts = (12000, 8000, 5500, 4000, 3000, 2000, 1600, 1300, 1200, 1000)
        self.assertEqual(sum(payouts), 39600)
        for amount in payouts:
            self.assertIn(f'${amount:,}', self.source)
        self.assertIn('un-guaranteed $39,600', self.source)
        self.assertIn('cannot silently stand in for it', self.source)

    def test_knockout_event_has_three_independently_funded_buckets(self):
        total, (ordinary, bounties, fees) = event_buckets(80, 230, 100, 70)
        self.assertEqual((total, ordinary, bounties, fees),
                         (32000, 18400, 8000, 5600))
        self.assertEqual(ordinary + bounties + fees, total)
        for number in ('$18,400', '$8,000', '$5,600', '$32,000'):
            self.assertIn(number, self.source)
        self.assertIn('do not add another $8,000', self.source.lower())
        self.assertIn('rounding and a combined-pools guarantee', self.source)

    def test_personal_net_prizes_are_not_the_event_pool(self):
        entry_total = 2 * 400
        trip = 60
        winnings = 950
        self.assertEqual(winnings - entry_total - trip, 90)
        self.assertEqual(0 - entry_total - trip, -860)
        self.assertEqual(winnings - 400 - trip, 490)
        self.assertIn('$950 − $800 − $60 = +$90', self.source)
        self.assertIn('$950 − $400 − $60 = +$490', self.source)
        self.assertIn('private finances', self.source)

    def test_accessible_reveals_tables_and_source_boundaries(self):
        self.assertEqual(self.source.count('class="poker-details viewer-question"'), 8)
        self.assertEqual(self.source.count('class="short-stack-table" role="region" tabindex="0"'), 3)
        self.assertEqual(self.source.count('class="short-stack-scroll-hint"'), 3)
        self.assertIn('poker-short-stack.css?v=', self.article)
        self.assertIn('Prepared with AI assistance', self.source)
        self.assertIn('not a real event', self.source)
        self.assertNotIn('\N{EM DASH}', self.source)
        for fragment in ('#ledger-terms', '#ledger-ordinary', '#ledger-guarantee',
                         '#ledger-payouts', '#ledger-bounty', '#ledger-player',
                         '#ledger-practice', '#ledger-worksheet'):
            self.assertIn(fragment, self.source)
        for official in ('assets.wsopcdn.com/wsop/70956034-',
                         'wsop.com/pdfs/structuresheets/structure_5765_24602.pdf',
                         'pokerstars.com/help/articles/buy-in-allocation/',
                         'pokerstars.com/help/articles/trn-knockout/'):
            self.assertIn(official, self.source)

    def test_public_blank_sheet_is_reusable_and_linked(self):
        worksheet_path = ROOT / 'downloads/poker-tournament-prize-pool-ledger.md'
        worksheet = worksheet_path.read_text()
        self.assertTrue(worksheet.startswith('# Tournament entry and prize-pool'))
        self.assertIn('Unique first entrants', worksheet)
        self.assertIn('Actual cash result before any taxes', worksheet)
        self.assertIn('source or uncertainty', worksheet.lower())
        self.assertIn('/downloads/poker-tournament-prize-pool-ledger.md', self.source)

    def test_contextual_inbound_guides_and_graph_reachability(self):
        graph = poker_link_graph.scan(ROOT)
        record = next(row for row in graph['records'] if row['slug'] == self.slug)
        for source in ('choosing-a-tournament', 'tournament-formats',
                       'registration-and-reentry', 'bounty-knockout-equity',
                       'tournament-equity', 'tournament-trip-budget',
                       'first-live-tournament'):
            self.assertIn('/poker/' + source + '/', record['prose_inbound_guides'])
        self.assertIn(self.route, (ROOT / '_source/poker/study.html').read_text())
        self.assertTrue(record['reachable_from_poker_entrypoints'])
        self.assertGreaterEqual(record['inbound_count'], 7)
        self.assertGreaterEqual(record['outbound_count'], 6)
        self.assertEqual(sum(not r['reachable_from_poker_entrypoints']
                             for r in graph['records']), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
