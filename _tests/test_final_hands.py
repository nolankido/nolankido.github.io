"""Independent card/accounting checks and preservation of the published course."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import shutil
import unittest
import html5lib
from test_site import ROOT, build
from test_viewer_guides import best
import poker_course
import poker_final_hands as final
import poker_finder
import final_hands_history as history


class FinalHandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hands = final.load(ROOT)
        cls.outputs = build.build_outputs()
        cls.baseline = json.loads((ROOT / '_tests/final-hands-baseline.json').read_text())

    def test_exact_predecessor_is_preserved_without_refreshing_old_contracts(self):
        b = self.baseline
        self.assertEqual((b['commit'], len(b['pages']), len(b['outputs']), len(b['files'])), ('b55e003f43f48289ab791683ac7d1583eb79451e', 193, 221, 478))
        self.assertEqual(history.pages(build.public_pages()), b['pages'])
        restored = history.outputs(self.outputs)
        self.assertEqual(set(map(str, restored)), set(b['outputs']))
        for path, text in restored.items():
            self.assertEqual(sha256(text.encode()).hexdigest(), b['outputs'][str(path)], str(path))
        for path, digest in {**b['files'], **b['extras']}.items():
            self.assertEqual(sha256(history.before(path, (ROOT / path).read_bytes())).hexdigest(), digest, path)
        actual = {p.relative_to(ROOT).as_posix() for d in ['_source', '_scripts', 'assets', 'downloads'] for p in (ROOT / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        self.assertEqual(history.files(actual), set(b['files']))
        self.assertEqual(set(history.change()['new_files']), {final.DATA, '_scripts/poker_final_hands.py'})
        self.assertEqual(history.change()['new_pages'], {})
        self.assertEqual(history.change()['new_outputs'], {})

    def test_each_street_and_showdown_match_independent_card_ranking(self):
        expected = [[(1,10,14,7,2), (1,10,14,7,4), (1,10,14,9,7)],
                    [(1,12,13,8,3), (5,13,12,8,5,3), (5,13,12,8,5,3)]]
        for hand, ranks in zip(self.hands, expected):
            for stop, rank in zip(hand['stops'][1:], ranks):
                self.assertEqual(best(hand['hero'] + hand['board'][:stop['board_count']]), rank)
            hero = best(hand['hero'] + hand['board'])
            opponent = best(hand['opponent'] + hand['board'])
            self.assertEqual(hand['winner_seat'], hand['hero_seat'] if hero > opponent else hand['opponent_seat'])
        self.assertEqual(best(self.hands[0]['opponent'] + self.hands[0]['board']), (3,9,10,7))
        self.assertEqual(best(self.hands[1]['opponent'] + self.hands[1]['board']), (5,11,10,8,5,3))

    def test_candidates_are_distinct_alternatives_with_correct_comparisons(self):
        for hand, stronger in zip(self.hands, [[False,True], [True,False]]):
            candidates = hand['stops'][-1]['candidates']
            known = hand['hero'] + hand['board']
            self.assertEqual([bool(set(c['values']) & set(known)) for c in candidates], [True,False,False])
            self.assertEqual([best(c['values'] + hand['board']) > best(known) for c in candidates[1:]], stronger)
        hand = self.hands[1]
        board = hand['board'][:4]
        worse, better = [c['values'] for c in hand['stops'][2]['candidates']]
        self.assertLess(best(worse + board), best(hand['hero'] + board))
        self.assertGreater(best(better + board), best(hand['hero'] + board))

    def test_one_ledger_carries_blinds_and_bets_through_all_four_rounds(self):
        for hand, pots, stacks, price in zip(self.hands, [[3,13,21,28], [9,21,28,42]], [[100,94,90,90], [99,94,87,87]], [Fraction(1,5), Fraction(1,4)]):
            self.assertEqual([sum(s['paid']) for s in hand['stops']], pots)
            self.assertEqual([100-s['paid'][hand['hero_seat']] for s in hand['stops']], stacks)
            for stop in hand['stops']:
                self.assertEqual(sum(100-n for n in stop['paid']) + sum(stop['paid']), 600)
            last = hand['stops'][-1]
            call = last['wager'] - last['street_paid']
            final_pot = sum(hand['finish_paid'])
            self.assertEqual(sum(last['paid']) + call, final_pot)
            self.assertEqual(Fraction(call,final_pot), price)
            ending = [100-n for n in hand['finish_paid']]
            ending[hand['winner_seat']] += final_pot
            self.assertEqual(sum(ending), 600)
            self.assertEqual(ending[hand['hero_seat']], 83 if hand['id']=='a' else 129)
        self.assertEqual([h['stops'][0]['wager'] - h['stops'][0]['street_paid'] for h in self.hands], [2,5])

    def test_future_cards_results_and_feedback_start_closed_without_choices(self):
        doc = html5lib.parse(self.outputs[build.output_path(final.ROUTE)], namespaceHTMLElements=False)
        section = next(e for e in doc.iter('section') if e.get('class')=='course-final')
        details = list(section.iter('details'))
        self.assertEqual(len(details), 17)
        self.assertFalse(any('open' in e.attrib for e in details))
        self.assertFalse(list(section.iter('input')) + list(section.iter('textarea')) + list(section.iter('button')))
        for hand in self.hands:
            for stop in hand['stops']:
                answer = next(e for e in details if e.get('id')=='course-hand-'+hand['id']+'-'+stop['street'].lower()+'-answer')
                self.assertTrue(all(url in [a.get('href') for a in answer.iter('a')] for url, _ in stop['repairs']))
        page = next(p for p in build.public_pages() if p['path']==final.ROUTE)
        passages = poker_finder.guide_sections(ROOT,page,{})
        searchable = ' '.join(s['text'] for s in passages)
        self.assertIn('course-hand', [s['anchor'] for s in passages])
        for hand in self.hands:
            for stop in hand['stops']:
                for answer in stop['answer']:
                    self.assertNotIn(answer, searchable)
            for stop in hand['stops'][1:]:
                self.assertNotIn(stop['setup'], searchable)
            for ending in hand['ending']:
                self.assertNotIn(ending, searchable)

    def test_paper_prompts_match_the_page_without_solutions_or_revealed_opponents(self):
        paper = final.workbook(ROOT)
        self.assertIn(paper, poker_course.workbook(ROOT))
        for hand in self.hands:
            for stop in hand['stops']:
                self.assertIn(stop['setup'], paper)
                self.assertIn(stop['prompt'], paper)
                for answer in stop['answer']:
                    self.assertNotIn(answer, paper)
            for ending in hand['ending']:
                self.assertNotIn(ending, paper)
        for path,digest in self.baseline['files'].items():
            if path.endswith('.js'):
                self.assertEqual(sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)

    def test_bad_cards_ledger_timing_and_repairs_fail_before_publication(self):
        data = json.loads((ROOT/final.DATA).read_text())
        variants = []
        bad = deepcopy(data);bad['hands'][0]['opponent'][0]='Ah';variants.append(bad)
        bad = deepcopy(data);bad['hands'][0]['stops'][0]['board_count']=5;variants.append(bad)
        bad = deepcopy(data);bad['hands'][0]['stops'][1]['paid'][3]=101;variants.append(bad)
        bad = deepcopy(data);bad['hands'][0]['finish_paid'][3]=16;variants.append(bad)
        bad = deepcopy(data);bad['hands'][0]['stops'][0]['repairs'][0][0]='/poker/first-decisions/#missing';variants.append(bad)
        for bad in variants:
            with TemporaryDirectory() as folder:
                root=Path(folder);(root/'_source/poker').mkdir(parents=True)
                for slug,_ in poker_course.LESSONS:
                    shutil.copyfile(ROOT/'_source/poker'/(slug+'.html'),root/'_source/poker'/(slug+'.html'))
                (root/final.DATA).write_text(json.dumps(bad))
                with self.assertRaises(ValueError):final.load(root)
        path='poker/beginner-checkpoint/index.html'
        changed=self.outputs[Path(path)]+'Unreviewed material'
        self.assertEqual(history.before(path,changed),changed)


if __name__=='__main__':unittest.main()
