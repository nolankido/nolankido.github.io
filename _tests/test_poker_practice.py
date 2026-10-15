"""Independent mechanics, transfer variants, discovery and exact scope checks."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
import json
import re
import shutil
import unittest
import html5lib
from test_site import ROOT, build
from test_viewer_guides import best, five
import check_live
import poker_course
import poker_finder
import poker_practice as practice
import poker_practice_history as history


class PokerPracticeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.data = practice.load(ROOT)
        cls.b = json.loads((ROOT / '_tests/poker-practice-baseline.json').read_text())

    def test_all_predecessor_inputs_outputs_metadata_and_inventory_are_exact(self):
        self.assertEqual((self.b['commit'], len(self.b['pages']), len(self.b['outputs'])), ('fd9fa67f65c367adba5026c8cc2321e61a0f2f94', 192, 220))
        self.assertEqual(history.pages(self.pages), self.b['pages'])
        old = history.outputs(self.outputs)
        self.assertEqual(set(map(str, old)), set(self.b['outputs']))
        for path, value in old.items():
            self.assertEqual(sha256(value.encode()).hexdigest(), self.b['outputs'][str(path)], path)
        for path, digest in self.b['files'].items():
            self.assertEqual(sha256(history.before(path, (ROOT / path).read_bytes())).hexdigest(), digest, path)
        self.assertEqual(self.b['extras'], {'_reports/search-audit.json': 'e0e97a09a488effcae4c6e0e088df36589ab96985fa7e92a87956149009b3107'})
        for path, digest in self.b['extras'].items():
            self.assertEqual(sha256(history.before(path, (ROOT / path).read_bytes())).hexdigest(), digest, path)
        edited_sources = {'_source/poker/free-poker-learning-path.html', '_source/poker/beginner-learning-path.html', '_source/poker/beginner-checkpoint-route.html', '_source/poker/library.html'}
        for path, digest in self.b['files'].items():
            if path.startswith('_source/poker/') and path.endswith('.html') and path not in edited_sources:
                self.assertEqual(sha256((ROOT / path).read_bytes()).hexdigest(), digest, path)
        self.assertEqual(set(history.change()['new_files']), {practice.DATA, practice.SOURCE, practice.CSS, practice.SCRIPT, '_scripts/poker_practice.py'})
        self.assertEqual(set(history.change()['new_outputs']), {'poker/beginner-practice/index.html'})

    def test_unrelated_mutations_are_not_hidden(self):
        for path in ['_scripts/build.py', '_scripts/poker_course.py', 'poker/free-poker-learning-path/index.html', '_source/pages.json', '_reports/search-audit.json']:
            changed = (ROOT / path).read_bytes() + b'Unreviewed change'
            self.assertEqual(history.before(path, changed), changed)
        added = build.output_path(practice.ROUTE)
        self.assertIn(added, history.outputs({added: self.outputs[added] + 'Unreviewed'}))
        pages = deepcopy(self.pages)
        next(p for p in pages if p['path'] == practice.ROUTE)['description'] += 'Unreviewed'
        self.assertNotEqual(history.pages(pages), self.b['pages'])

    def test_fixed_bank_has_six_models_and_eighteen_different_questions(self):
        units = self.data['units']
        self.assertEqual([u['id'] for u in units], list(practice.UNITS))
        self.assertEqual([u['lesson'] for u in units], [slug for slug, _ in poker_course.LESSONS])
        cases = [c for u in units for c in u['cases']]
        self.assertEqual(len({c['id'] for c in cases}), 18)
        self.assertEqual(len({c['question'] + c['prompt'] for c in cases}), 18)
        for unit in units:
            self.assertEqual(set(c['correct'] for c in unit['cases']), {0,1,2})
            self.assertTrue(unit['rule'] and unit['example']['reason'])
        # The three mixed sets visit every reviewed question exactly once.
        sets = [[units[i]['cases'][(s+i)%3]['id'] for i in [3,0,5,2,1,4]] for s in range(3)]
        self.assertEqual(len(set(sum(sets, []))), 18)

    def test_additional_calls_and_action_order_are_independently_correct(self):
        for unit in self.data['units'][:2]:
            for record in [unit['example'], *unit['cases']]:
                proof = record['proof']
                if proof['type'] == 'call':
                    value = proof['to'] - proof['paid']
                    self.assertEqual(value, proof['answer'])
                    if 'choices' in record:
                        label = record['choices'][record['correct']][0]
                        self.assertEqual(int(re.match(r'\d+', label)[0]), value)
                elif proof['type'] == 'preflop-order':
                    self.assertEqual(proof['remaining'], list(range(proof['seat']+1, 6)))
                elif proof['type'] == 'postflop-order':
                    self.assertEqual(next(i for i in [4,5,0,1,2,3] if i in proof['active']), proof['first'])
                elif proof['type'] == 'response-order':
                    clockwise = [(proof['raiser']+i)%6 for i in range(1,7)]
                    self.assertEqual(next(i for i in clockwise if i in proof['active']), proof['next'])
                else:
                    self.fail('Unreviewed mechanics proof')
                if 'choices' in record and proof['type'] != 'call':
                    names = {'first seat':0,'next seat':1,'cutoff':2,'button':3,'small blind':4,'big blind':5}
                    label = record['choices'][record['correct']][0].lower()
                    named = {seat for name, seat in names.items() if name in label}
                    expected = set(proof['remaining']) if proof['type'] == 'preflop-order' else {proof.get('first', proof.get('next'))}
                    self.assertEqual(named, expected)

    def test_made_hands_draws_river_choices_and_tie_use_an_independent_evaluator(self):
        checked = 0
        for unit in self.data['units'][2:4]:
            for record in [unit['example'], *unit['cases']]:
                available = record['hero'] + record['board']
                self.assertEqual(len(set(available + record.get('opponent', []))), len(available + record.get('opponent', [])))
                score = best(available)
                proof = record['proof']
                if proof['type'] == 'made':
                    self.assertEqual(score[0], proof['category'])
                    counts = [sum(c[1] == suit for c in available) for suit in 'shdc']
                    self.assertEqual(4 in counts, proof['draw_suit'] is not None)
                    if proof['draw_suit']:
                        self.assertEqual(sum(c[1] == proof['draw_suit'] for c in available), 4)
                    if 'choices' in record:
                        prefix = {0:'Ace-high',1:'A pair',3:'Three'}[score[0]]
                        self.assertTrue(record['choices'][record['correct']][0].startswith(prefix))
                else:
                    self.assertEqual(list(score), proof['score'])
                    if proof['type'] == 'tie':
                        self.assertEqual(score, best(record['opponent'] + record['board']))
                        self.assertEqual(score, five(record['board']))
                        self.assertIn('tie', record['choices'][record['correct']][0])
                    elif record.get('id') == 'board-pairs':
                        ranks = record['choices'][record['correct']][0].rstrip('.').split('-')
                        self.assertEqual(ranks, ['K','K','Q','Q','9'])
                    elif record.get('id') == 'four-hearts':
                        selected = record['choices'][record['correct']][0]
                        suits = dict(zip('♠♥♦♣', 'shdc'))
                        cs = [rank + suits[suit] for rank, suit in re.findall(r'([2-9TJQKA])([♠♥♦♣])', selected)]
                        self.assertEqual(len(cs), 5)
                        self.assertTrue(set(cs) <= set(available))
                        self.assertEqual(five(cs), score)
                checked += 1
        self.assertEqual(checked, 8)

    def test_known_card_removal_and_reasoning_limits_are_explicit(self):
        unit = self.data['units'][4]
        model = unit['example']
        self.assertTrue(set(model['proof']['candidate']) & set(model['hero'] + model['board']))
        case = unit['cases'][0]
        known = set(case['hero'] + case['board'])
        valid = [i for i, cs in enumerate(case['proof']['candidates']) if not known.intersection(cs)]
        self.assertEqual(valid, [case['correct']])
        claims = {c['proof']['claim'] for u in self.data['units'][4:] for c in u['cases'] if c['proof']['type'] == 'reasoning'}
        self.assertEqual(claims, {'observation','one-observation','value','bluff','result-not-comparison'})
        # Qualitative conclusions are human-reviewed explanations, not solver grades.
        text = (ROOT / practice.SOURCE).read_text()
        for phrase in ['fictional', 'not recommended betting lines', 'three mixed sets', 'do not validate this course']:
            self.assertIn(phrase, text)

    def test_each_lesson_and_search_reaches_exact_practice_without_answer_spoilers(self):
        doc = html5lib.parse(self.outputs[build.output_path(practice.ROUTE)], namespaceHTMLElements=False)
        ids = {el.get('id') for el in doc.iter()}
        for unit in self.data['units']:
            route = '/poker/' + unit['lesson'] + '/'
            self.assertIn('href="' + practice.lesson_link(unit['lesson']) + '"', self.outputs[build.output_path(route)])
            self.assertIn('practice-' + unit['id'], ids)
        page = next(p for p in self.pages if p['path'] == practice.ROUTE)
        sections = poker_finder.guide_sections(ROOT, page, build.poker_content.load(ROOT))
        sections = {s['anchor']: s['text'] for s in sections}
        for case in [c for u in self.data['units'] for c in u['cases']]:
            anchor = 'exercise-' + case['id']
            self.assertIn(anchor, ids)
            self.assertIn(case['question'], sections[anchor])
            self.assertNotIn(case['reason'], sections[anchor])
            for _, note in case['choices']:
                self.assertNotIn(note, sections[anchor])

    def test_practice_is_a_utility_and_preserves_all_existing_feed_item_identities(self):
        page = next(p for p in self.pages if p['path'] == practice.ROUTE)
        self.assertFalse(page.get('poker_guide'))
        schema = re.search(r'<script type="application/ld\+json">(.*?)</script>', self.outputs[build.output_path(practice.ROUTE)], re.S)[1]
        self.assertEqual(json.loads(schema)['@type'], 'WebPage')
        for path in ['poker/feed.xml','writing.xml']:
            old = ET.fromstring(history.before(path, self.outputs[Path(path)]))
            current = ET.fromstring(self.outputs[Path(path)])
            fields = lambda root: [(x.findtext('guid'),x.findtext('pubDate'),x.findtext('title')) for x in root.findall('./channel/item')]
            self.assertEqual(fields(old), fields(current))

    def test_optional_assets_are_scoped_private_and_verified_live(self):
        target = build.output_path(practice.ROUTE)
        for path, source in self.outputs.items():
            if path.suffix == '.html':
                for asset in [practice.SCRIPT, practice.CSS]:
                    self.assertEqual('/' + asset + '?v=' in source, path == target, path)
        js = (ROOT / practice.SCRIPT).read_text()
        for token in ['fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'document.cookie', 'innerHTML', 'eval(', 'pushState', 'replaceState']:
            self.assertNotIn(token, js)
        targets = check_live.targets()
        self.assertEqual(len(targets), 466)
        for path in [practice.ROUTE, '/' + practice.SCRIPT, '/' + practice.CSS]:
            self.assertIn(path, targets)

    def test_invalid_cards_choices_repairs_and_stage_order_fail_the_build(self):
        variants = []
        bad = deepcopy(self.data); bad['units'][0]['cases'][0]['correct'] = True; variants.append(bad)
        bad = deepcopy(self.data); bad['units'][2]['cases'][0]['hero'][0] = bad['units'][2]['cases'][0]['board'][0]; variants.append(bad)
        bad = deepcopy(self.data); bad['units'][0]['cases'][0]['repair'] = '/poker/first-decisions/#missing'; variants.append(bad)
        bad = deepcopy(self.data); bad['units'][0]['cases'][1]['id'] = bad['units'][0]['cases'][0]['id']; variants.append(bad)
        bad = deepcopy(self.data); bad['units'].reverse(); variants.append(bad)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / '_source/poker', root / '_source/poker')
            for data in variants:
                (root / practice.DATA).write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    practice.load(root)


if __name__ == '__main__':
    unittest.main()
