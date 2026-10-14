"""Beginner lesson correctness and independent protection of the prior release."""
from copy import deepcopy
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import beginner_history as history
import preflop_history
from test_viewer_guides import Tags, best, five

ROUTE = '/poker/first-decisions/'
CHECKS = ['suited', 'kicker', 'facing-bet', 'checked-to', 'big-blind', 'call',
          'new-street', 'min-raise', 'another-turn', 'one-hole', 'board', 'full-hand']
ASIDE = '<aside class="viewer-example" aria-labelledby="first-decisions-start"><h2 id="first-decisions-start">Completely new? Practice the first decisions.</h2><p>Before calculating percentages, learn which actions are legal, what a call adds and which five cards play. <a href="/poker/first-decisions/">Start with eight beginner lessons and twelve explained checkpoints</a>, then return here when the mechanics feel familiar.</p></aside>\n'
OLD_CARD = '<a href="/poker/free-poker-learning-path/"><span class="note-category">Learn</span><strong>I am new to poker</strong><span>A small, free learning path. No purchase or playing account needed.</span></a>'
NEW_CARD = '<a href="/poker/first-decisions/"><span class="note-category">Learn</span><strong>I am new to poker</strong><span>Eight short lessons and twelve explained practice questions. No wager or account needed.</span></a>'


def feed_records(xml):
    return {i.findtext('link'): ET.tostring(i, encoding='unicode')
            for i in ET.fromstring(xml).findall('./channel/item')}


class BeginnerDecisionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = preflop_history.pages(build.public_pages())
        cls.current_outputs = build.build_outputs()
        cls.outputs = preflop_history.outputs(cls.current_outputs)
        cls.text = cls.outputs[build.output_path(ROUTE)]
        cls.source = (ROOT / '_source/poker/first-decisions.html').read_text()
        cls.baseline = json.loads((ROOT / '_tests/beginner-decisions-baseline.json').read_text())

    def test_exact_new_inventory_and_all_predecessor_hashes(self):
        b = self.baseline
        self.assertEqual((len(b['pages']), len(b['outputs']), len(b['files'])), (171, 198, 343))
        self.assertEqual(history.pages(self.pages), b['pages'])
        self.assertEqual(len(self.pages), 172)
        outputs = history.outputs(self.outputs)
        self.assertEqual(set(map(str, outputs)), set(b['outputs']))
        for p, value in outputs.items():
            self.assertEqual(sha256(value.encode()).hexdigest(), b['outputs'][str(p)], str(p))
        files = {p.relative_to(ROOT).as_posix() for d in ['_source', 'assets', 'downloads']
                 for p in (ROOT / d).rglob('*') if p.is_file()}
        files = preflop_history.files(files)
        self.assertEqual(files - set(b['files']), {'_source/poker/first-decisions.html', 'assets/social/reader-poker-first-decisions.png'})
        changed = set()
        for p, digest in b['files'].items():
            raw = preflop_history.before(p, (ROOT / p).read_bytes())
            if sha256(raw).hexdigest() != digest:
                changed.add(p)
            self.assertEqual(sha256(history.before(p, raw)).hexdigest(), digest, p)
        self.assertEqual(changed, {'_source/pages.json', '_source/poker/home.html', '_source/poker/free-poker-learning-path.html',
                                   '_source/poker/library.json', '_source/poker/topics.json', '_source/reader-previews.json'})

    def test_old_article_prose_and_metadata_survive_without_a_historical_adapter(self):
        # These literal removals are independent of the frozen general reversal.
        p = '_source/poker/free-poker-learning-path.html'
        raw = (ROOT / p).read_text()
        self.assertEqual(raw.count(ASIDE), 1)
        self.assertEqual(sha256(raw.replace(ASIDE, '', 1).encode()).hexdigest(), self.baseline['files'][p])
        p = '_source/poker/home.html'
        raw = (ROOT / p).read_text()
        self.assertEqual(raw.count(NEW_CARD), 1)
        self.assertEqual(sha256(raw.replace(NEW_CARD, OLD_CARD, 1).encode()).hexdigest(), self.baseline['files'][p])
        current = {p['id']: p for p in self.pages}
        for old in self.baseline['pages']:
            self.assertEqual(current[old['id']], old)
            if old['source'] in ['poker/home.html', 'poker/free-poker-learning-path.html']:
                continue
            path = '_source/' + old['source']
            self.assertEqual(sha256((ROOT / path).read_bytes()).hexdigest(), self.baseline['files'][path], path)

    def test_existing_catalog_records_and_feed_items_are_exact(self):
        old = self.baseline['catalogs']
        for path in ['_source/poker/library.json', '_source/reader-previews.json']:
            now = json.loads(preflop_history.before(path, (ROOT / path).read_text()))
            if path.endswith('library.json'):
                now['entries'] = [g for g in now['entries'] if g['slug'] != 'first-decisions']
            else:
                del now['pages']['poker-first-decisions']
            self.assertEqual(now, old[path], path)
        for path, prior in self.baseline['feed_items'].items():
            now = feed_records(self.outputs[Path(path)])
            self.assertEqual({k: now[k] for k in prior}, prior, path)
            self.assertEqual(set(now) - set(prior), {'https://nolankido.com' + ROUTE} if path in ['poker/feed.xml', 'writing.xml'] else set())

    def test_twelve_native_checkpoints_have_complete_explanations_and_sources(self):
        tags = Tags(self.source).items
        questions = [a for tag, a in tags if tag == 'details']
        self.assertEqual([a['id'] for a in questions], ['check-' + c for c in CHECKS])
        self.assertTrue(all('open' not in a for a in questions))
        self.assertEqual(len([a for tag, a in tags if tag == 'h2']), 10)
        for label in CHECKS:
            answer = re.search(r'id="check-' + label + r'".*?<div>(.*?)</div></details>', self.source, re.S)[1]
            self.assertGreater(len(re.sub('<[^>]+>', '', answer).split()), 35, label)
        cards = [a for _, a in tags if a.get('role') == 'img']
        self.assertEqual(len(cards), 31)
        self.assertTrue(all(' of ' in a.get('aria-label', '') for a in cards))
        for phrase in ['Every scene below is fictional', 'no wager, account or purchase', 'Prepared with AI assistance',
                       'October 14, 2026', 'pokertda.com/view-poker-tda-rules/', 'pokerstars.com/poker/games/texas-holdem/']:
            self.assertIn(phrase, self.source)
        self.assertNotRegex(self.source, r'<(?:script|form|input|iframe)\b')
        self.assertNotIn('\u2014', self.source)

    def test_best_five_answers_by_exhaustive_card_enumeration(self):
        cases = {a['data-example']: a for _, a in Tags(self.source).items if 'data-example' in a}
        expected = {'domination': (1, 14, 11, 9, 7), 'one-hole': (2, 14, 13, 8), 'board-plays': (4, 12)}
        for name, case in cases.items():
            hole = case['data-hole'].split(); board = case['data-board'].split()
            other = case.get('data-opponent', '').split()
            self.assertEqual(len(set(hole + board + other)), len(hole + board + other))
            self.assertEqual(best(hole + board), expected[name])
            winning = [c for c in combinations(hole + board, 5) if five(c) == expected[name]]
            if name in ['one-hole', 'board-plays']:
                required = 1 if name == 'one-hole' else 0
                self.assertTrue(all(len(set(c) & set(hole)) == required for c in winning))
            if name == 'domination':
                self.assertGreater(best(other + board), best(hole + board))
            if name == 'board-plays':
                self.assertEqual(best(other + board), best(hole + board))
        for phrase in ['A-A-J-9-7', 'A-A-K-J-9', 'A-A-K-K-8', 'Q-J-T-9-8']:
            self.assertIn(phrase, self.source)

    def test_full_hand_conserves_chips_and_raise_arithmetic_matches_rules(self):
        paid = {'first': 0, 'button': 6, 'small': 1, 'big': 6}
        self.assertEqual(sum(paid.values()), 13)
        paid['button'] += 4; paid['big'] += 4
        pot = sum(paid.values())
        self.assertEqual(pot, 21)
        balances = {p: 100 - n + (pot if p == 'button' else 0) for p, n in paid.items()}
        self.assertEqual(balances, {'first': 100, 'button': 111, 'small': 99, 'big': 90})
        self.assertEqual(sum(balances.values()), 400)
        board = 'Ks 8c 3d 7h 2s'.split()
        self.assertEqual(best('Kh Jd'.split() + board), (1, 13, 11, 8, 7))
        self.assertEqual(best('Kc Td'.split() + board), (1, 13, 10, 8, 7))
        for phrase in ['13 = 6 + 6 + 1', 'K-K-J-8-7', 'K-K-T-8-7', '<strong>111</strong>', 'gain of 11']:
            self.assertIn(phrase, self.source)
        self.assertEqual(6 + (6 - 2), 10)
        self.assertEqual(12 - 4, 8)
        for phrase in ['making 10 total', 'B faces 8 more', '6 total minus your existing 2', 'pot is 6: three contributions of 2']:
            self.assertIn(phrase, self.source)

    def test_discovery_schema_and_live_targets_include_the_new_guide(self):
        for path in ['poker/index.html', 'poker/library/index.html', 'poker/topics/learn/index.html',
                     'poker/free-poker-learning-path/index.html', 'poker/find/index.html', 'find/index.html', 'sitemap.xml']:
            self.assertIn(ROUTE, self.outputs[Path(path)], path)
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.text, re.S)[1])
        self.assertEqual(schema['@type'], 'Article')
        self.assertEqual(schema['datePublished'], '2026-10-14')
        self.assertEqual(schema['author']['name'], 'Nolan Kido')
        self.assertNotIn('image', schema)
        self.assertIn('Poker for Beginners: First Decisions &amp; Practice', self.text)
        targets = check_live.targets()
        self.assertEqual(targets[ROUTE], (200, self.current_outputs[build.output_path(ROUTE)].encode()))
        self.assertEqual(targets['/assets/social/reader-poker-first-decisions.png'][0], 200)
        find = self.outputs[Path('find/index.html')]
        prior = history.before('find/index.html', find)
        self.assertLess(len(find.encode()) - len(prior.encode()), 2048)
        payload = lambda s: re.search(r'id="find-section-data">(.*?)</script>', s, re.S)[1]
        self.assertLess(len(payload(find).encode()) - len(payload(prior).encode()), 1024)

    def test_frozen_history_cannot_hide_unreviewed_changes(self):
        for path, old, new in [('poker/first-decisions/index.html', '111', '112'),
                               ('poker/free-poker-learning-path/index.html', 'You do not need to buy a course', 'You must buy a course'),
                               ('_source/pages.json', 'Your first poker decisions.', 'Invented expertise')]:
            raw = self.outputs[Path(path)] if path in map(str, self.outputs) else (ROOT / path).read_text()
            changed = raw.replace(old, new, 1)
            self.assertNotEqual(changed, raw)
            self.assertEqual(history.before(path, changed), changed)
            if path == history.OUTPUT:
                self.assertIn(Path(path), history.outputs({Path(path): changed}))
        records = deepcopy(self.pages)
        next(p for p in records if p['id'] == history.ID)['description'] = 'An unsupported claim'
        self.assertEqual(len(history.pages(records)), 172)
        self.assertEqual(history.before('assets/unrelated.bin', b'\xff\x00'), b'\xff\x00')


if __name__ == '__main__':
    unittest.main()
