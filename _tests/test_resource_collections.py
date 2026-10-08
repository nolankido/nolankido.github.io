"""Collection discovery, safe rendering, export parity and independent worked examples."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import copy
import json
import tempfile
import unittest
from test_site import ROOT, Page, build
import poker_collections
import poker_resources
import check_live

SLUGS = ('free-poker-learning-path', 'cash-game-study', 'omaha-and-mixed-games', 'poker-books-and-courses', 'poker-research-guide')


def high(cards):
    """Independent five-card ranking for exhaustive Omaha hand construction."""
    ranks = sorted(['23456789TJQKA'.index(c[0]) + 2 for c in cards], reverse=True)
    counts = sorted(((n, r) for r, n in Counter(ranks).items()), reverse=True)
    flush = len({c[1] for c in cards}) == 1
    straight = (5 if ranks == [14, 5, 4, 3, 2] else ranks[0]) if len(set(ranks)) == 5 and (ranks[0] - ranks[-1] == 4 or ranks == [14, 5, 4, 3, 2]) else 0
    if straight and flush: return (8, straight)
    if counts[0][0] == 4: return (7, counts[0][1], counts[1][1])
    if [n for n, _ in counts] == [3, 2]: return (6, counts[0][1], counts[1][1])
    if flush: return (5, *ranks)
    if straight: return (4, straight)
    if counts[0][0] == 3: return (3, *(r for _, r in counts))
    if [n for n, _ in counts][:2] == [2, 2]: return (2, *(r for _, r in counts))
    if counts[0][0] == 2: return (1, *(r for _, r in counts))
    return (0, *ranks)


def lows(cards):
    ranks = sorted([1 if c[0] == 'A' else '23456789TJQK'.index(c[0]) + 2 for c in cards], reverse=True)
    return tuple(ranks) if len(set(ranks)) == 5 and max(ranks) <= 8 else None


class CollectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.pages = build.public_pages()
        cls.resources = poker_resources.load(ROOT)
        cls.collections = poker_collections.load(ROOT, cls.resources, cls.pages)

    def test_every_collection_is_a_substantive_guide_and_reachable(self):
        hub = self.outputs[Path('poker/resource-collections/index.html')]
        for slug in SLUGS:
            route = '/poker/' + slug + '/'
            page = next(p for p in self.pages if p['path'] == route)
            self.assertTrue(page['poker_guide'])
            for output in [hub, self.outputs[Path('poker/index.html')], self.outputs[Path('poker/library/index.html')], self.outputs[Path('sitemap.xml')], self.outputs[Path('poker/feed.xml')]]:
                self.assertIn(route, output)
            self.assertIn(route, check_live.targets())
            source = (ROOT / '_source' / page['source']).read_text()
            self.assertGreater(len(source.split()), 400)
            self.assertIn('fictional', source)
            self.assertIn('Prepared with AI assistance', source)
            content = self.outputs[Path('poker') / slug / 'index.html']
            self.assertIn('reader-outline', content)
            self.assertIn('data-collection-resource', content)
            parsed = Page(content)
            ids = [a['id'] for _, a in parsed.elements if 'id' in a]
            self.assertEqual(len(ids), len(set(ids)))
        catalog = build.poker_content.load(ROOT)
        self.assertTrue(set(SLUGS).isdisjoint(e['slug'] for e in catalog['entries']))

    def test_each_collection_uses_current_metadata_and_preserves_cautions(self):
        values = poker_collections.supplement(self.collections, self.resources)
        by_id = {r['id']: r for r in self.resources}
        for c in self.collections:
            content = values['collection_' + c['id']]
            for ident in c['resource_ids']:
                e = by_id[ident]
                self.assertIn(build.text(e['url']), content)
                self.assertIn(build.text(e['notes']), content)
                self.assertIn(e['reviewed_on'], content)
        changed = copy.deepcopy(self.resources)
        e = next(e for e in changed if e['id'] == self.collections[0]['resource_ids'][0])
        e['title'] = '<script>not executable</script>'
        e['notes'] = '<img onerror="bad()">'
        e['review_method'] = 'index'
        content = poker_collections.supplement(self.collections, changed)['collection_free']
        self.assertIn('&lt;script&gt;', content)
        self.assertNotIn('<script>', content)
        self.assertIn('Search index only', content)

    def test_invalid_collections_are_rejected(self):
        base = {'version': 1, 'entries': copy.deepcopy(self.collections)}
        changes = [lambda d: d.update(version=True),
                   lambda d: d['entries'][0].update(resource_ids=['missing', 'holdem-rules', 'hand-rankings']),
                   lambda d: d['entries'][0].update(resource_ids=['holdem-rules'] * 3),
                   lambda d: d['entries'][0].update(resource_ids=['play-optimal-poker', 'holdem-rules', 'hand-rankings']),
                   lambda d: d['entries'][0].update(slug='../escape'),
                   lambda d: d['entries'][0].update(slug='resource-collections'),
                   lambda d: d['entries'].append(copy.deepcopy(d['entries'][0])),
                   lambda d: d['entries'][0].update(resource_ids=[{}, [], None])]
        for change in changes:
            data = copy.deepcopy(base); change(data)
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp); (root / '_source/poker').mkdir(parents=True)
                (root / '_source/poker/collections.json').write_text(json.dumps(data))
                with self.assertRaises(ValueError): poker_collections.load(root, self.resources, self.pages)

    def test_exports_are_exact_complete_deterministic_and_live_verified(self):
        result = poker_collections.exports(self.resources)
        self.assertEqual(result, poker_collections.exports(list(reversed(self.resources))))
        payload = json.loads(result[Path('downloads/poker-resource-directory.json')])
        self.assertEqual({e['id']: e for e in payload['entries']}, {e['id']: e for e in self.resources})
        self.assertEqual(len(payload['entries']), len(self.resources))
        md = result[Path('downloads/poker-resource-directory.md')]
        for e in self.resources:
            self.assertIn(e['url'], md)
            self.assertIn(e['reviewed_on'], md)
            self.assertIn(e['notes'], md)
        for path, content in result.items():
            self.assertEqual(content, self.outputs[path])
            self.assertIn('/' + str(path), check_live.targets())

    def test_new_batch_records_do_not_relabel_old_reviews(self):
        batch = json.loads((ROOT / '_reports/resource-expansion-batch-004.json').read_text())
        self.assertEqual(len(batch['accepted_ids']), 24)
        self.assertTrue(set(batch['accepted_ids']) <= {r['id'] for r in self.resources})
        for r in self.resources:
            if r['id'] in batch['accepted_ids']:
                self.assertEqual(r['reviewed_on'], '2026-10-08')
                self.assertEqual(r['review_method'], 'page')
        content = self.outputs[Path('poker/resources/index.html')]
        count = len(json.loads((ROOT / '_source/poker/library.json').read_text())['entries'])
        self.assertIn(str(count) + '-guide Poker library', content)
        self.assertNotIn('24-guide Poker library', content)
        self.assertNotIn('31-guide Poker library', content)

    def test_cash_example_and_free_call_price(self):
        pot, bet, call = 80, 40, 40
        gross = pot + bet + call
        rake = min(Fraction(5, 100) * gross, 6)
        award = gross - rake
        self.assertEqual((gross, rake, award), (160, 6, 154))
        self.assertEqual(round(float(100 * call / award), 2), 25.97)
        self.assertEqual(Fraction(1, 4) * award - call, Fraction(-3, 2))
        self.assertEqual(Fraction(30, 60 + 30 + 30), Fraction(1, 4))
        content = self.outputs[Path('poker/cash-game-study/index.html')]
        for literal in ('154', '25.97%', '-1.50'): self.assertIn(literal, content)

    def test_omaha_legal_card_construction_high_low_and_quarters(self):
        board = ['3c', '4d', '8h', 'Ks', 'Kd']
        a = ['As', '2s', 'Kc', 'Qh']; b = ['Ah', '2h', 'Qc', 'Jd']
        self.assertEqual(len(set(board + a + b)), 13)
        def options(hole):
            return [list(x + y) for x in combinations(hole, 2) for y in combinations(board, 3)]
        self.assertEqual(len(options(a)), 60)
        self.assertEqual(max(map(high, options(a)))[:2], (3, 13))
        self.assertGreater(max(map(high, options(a))), max(map(high, options(b))))
        for hole in (a, b):
            self.assertEqual(min(low for hand in options(hole) if (low := lows(hand)) is not None), (8, 4, 3, 2, 1))
        self.assertEqual((200 // 2 + 200 // 4, 200 // 4), (150, 50))
        hole = ['As', 'Kd', 'Qc', 'Jh']; spade_board = ['2s', '7s', '9s', 'Js', '3d']
        hands = [x + y for x in combinations(hole, 2) for y in combinations(spade_board, 3)]
        self.assertTrue(all(len({c[1] for c in h}) != 1 for h in hands))

    def test_no_new_runtime_or_unrequested_personal_material(self):
        for slug in SLUGS + ('resource-collections',):
            source = (ROOT / '_source/poker' / (slug + '.html')).read_text()
            for term in ('<script', '<form', '<iframe', '<input', 'data-umami-event', chr(0x2014)):
                self.assertNotIn(term, source)
        overview = self.outputs[Path('poker/index.html')]
        self.assertIn('href="/poker/resources/"', overview)
        self.assertIn('Find a poker answer', overview)
        self.assertIn('building a vlog', overview)
        self.assertIn('id="watch"', overview)

if __name__ == '__main__': unittest.main(verbosity=2)
