"""Fresh practice, exact misconception repairs and independent preservation."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import re
import sys
import unittest
import html5lib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import poker_checkpoint as checkpoint
import poker_beginner_path
import poker_library
import checkpoint_history as history
from test_viewer_guides import Tags, best

LABELS = ['one', 'two', 'three', 'four', 'five', 'six']
REPAIRS = ['/poker/first-decisions/#chips-owed', '/poker/starting-hand-decisions/#position',
           '/poker/first-flop-decisions/#made-and-drawing', '/poker/turn-and-river-decisions/#catching-a-bluff',
           '/poker/ranges-for-beginners/#known-and-possible', '/poker/betting-with-a-purpose/#value']


class CheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.source = (ROOT / '_source/poker/beginner-checkpoint.html').read_text()
        cls.text = cls.outputs[build.output_path(checkpoint.ROUTE)]
        cls.baseline = json.loads((ROOT / '_tests/checkpoint-baseline.json').read_text())
        cls.tree = html5lib.parseFragment(cls.source, namespaceHTMLElements=False)
        cls.scenes = [s for s in cls.tree.iter('section') if s.get('data-case')]

    def test_baseline_and_every_previous_input_survive_exact_reviewed_changes(self):
        b = self.baseline
        self.assertEqual((b['commit'], len(b['pages']), len(b['outputs'])),
                         ('7d8bf3fddc63fe1cc1fd5f1751fcda93823527e5', 177, 204))
        self.assertEqual(history.pages(self.pages), b['pages'])
        restored = history.outputs(self.outputs)
        self.assertEqual(set(map(str, restored)), set(b['outputs']))
        for path, text in restored.items():
            self.assertEqual(sha256(text.encode()).hexdigest(), b['outputs'][str(path)], str(path))
        mutable = {'_source/pages.json', '_source/poker/library.json', '_source/poker/topics.json',
                   '_source/reader-previews.json', '_scripts/build.py', '_scripts/poker_library.py',
                   '_scripts/poker_reading.py', '_scripts/check_live.py'}
        for path, digest in b['files'].items():
            raw = (ROOT / path).read_bytes()
            if path not in mutable: self.assertEqual(sha256(raw).hexdigest(), digest, path)
            self.assertEqual(sha256(history.before(path, raw)).hexdigest(), digest, path)

    def test_only_the_learning_path_record_changes_and_existing_feed_identity_survives(self):
        by_id = {p['id']: p for p in self.pages}
        for old in self.baseline['pages']:
            now = by_id[old['id']]
            if old['path'] == '/poker/free-poker-learning-path/':
                self.assertEqual({k:v for k,v in now.items() if k not in {'description','revision'}},
                                 {k:v for k,v in old.items() if k not in {'description','revision'}})
            else: self.assertEqual(now, old, old['id'])
            path = '_source/' + old['source']
            self.assertEqual(sha256((ROOT / path).read_bytes()).hexdigest(), self.baseline['files'][path], path)
        restored = history.outputs(self.outputs)
        for path in ['feed.xml','poker/feed.xml','technology/feed.xml','living-well/feed.xml','writing.xml']:
            records = lambda text: {i.findtext('link'): ET.tostring(i, encoding='unicode')
                                    for i in ET.fromstring(text).findall('./channel/item')}
            old, now = records(restored[Path(path)]), records(self.outputs[Path(path)])
            for url, raw in old.items():
                if url == 'https://nolankido.com/poker/free-poker-learning-path/':
                    a, b = ET.fromstring(raw), ET.fromstring(now[url])
                    for field in ['title','link','guid','pubDate']: self.assertEqual(a.findtext(field), b.findtext(field))
                    self.assertEqual(b.findtext('description'), by_id['poker-free-poker-learning-path']['description'])
                else: self.assertEqual(now[url], raw, (path,url))
            self.assertEqual(set(now)-set(old), {'https://nolankido.com'+checkpoint.ROUTE}
                             if path in ['poker/feed.xml','writing.xml'] else set(), path)

    def test_six_choices_have_varied_keys_explanations_repairs_and_changed_retries(self):
        self.assertEqual(len(self.scenes), 6)
        keys = []
        for scene, label, repair in zip(self.scenes, LABELS, REPAIRS):
            self.assertEqual(len(scene.find('ol').findall('li')), 3)
            answers = {d.get('id'):d for d in scene.findall('details')}
            self.assertEqual(set(answers), {'answer-'+label,'retry-'+label})
            first = answers['answer-'+label]
            key = next(first.iter('strong')).text[0];keys.append(key)
            text = ' '.join(first.itertext())
            for other in set('ABC')-{key}: self.assertIn(other+' ', text)
            self.assertIn(repair, [a.get('href') for a in first.iter('a')])
            self.assertGreater(len(' '.join(answers['retry-'+label].itertext()).split()), 35)
            self.assertTrue(any('Changed situation' in ''.join(p.itertext()) for p in scene.findall('p')))
            self.assertFalse(any('open' in d.attrib for d in answers.values()))
        self.assertEqual(keys, list('BCABCA'))
        self.assertIn('sure,” “partly sure” or “guessing', self.source)

    def test_calls_use_the_current_street_and_position_keeps_the_blinds_pending(self):
        scene = self.scenes[0]
        total, posted = int(scene.get('data-total')), int(scene.get('data-posted'))
        self.assertEqual(total-posted, 6)
        self.assertEqual(total+posted, 10)
        self.assertIn('8 - 2 = 6', self.source)
        self.assertIn('5 - 0 = 5', self.source)
        order = ['first','second','cutoff','button','small blind','big blind']
        self.assertEqual(order[order.index('button')+1:], ['small blind','big blind'])
        for phrase in ['The blinds still have decisions', 'This flop betting round is complete',
                       'Both remaining players checked without a wager']:
            self.assertIn(phrase, self.source)

    def test_made_hand_and_draw_are_correct_before_and_after_the_turn(self):
        scene = self.scenes[2]
        hole, board = scene.get('data-hole').split(), scene.get('data-board').split()
        turn = scene.get('data-turn')
        self.assertEqual(len(set(hole+board+[turn])), 6)
        self.assertEqual(best(hole+board), (1,12,13,8,3))
        self.assertEqual(best(hole+board+[turn]), (1,12,13,8,5))
        self.assertEqual(sum(c.endswith('s') for c in hole+board), 4)
        self.assertEqual(sum(c.endswith('s') for c in hole+board+[turn]), 4)
        self.assertIn('Q-Q-K-8-3', self.source);self.assertIn('Q-Q-K-8-5', self.source)
        cards = [a for _,a in Tags(self.source).items if a.get('role')=='img']
        self.assertEqual(len(cards), 5)
        self.assertTrue(all(' of ' in c['aria-label'] for c in cards))

    def test_call_prices_change_with_the_relative_bet_without_estimating_equity(self):
        scene = self.scenes[3]
        for prefix, expected in [('',Fraction(1,5)), ('retry-',Fraction(1,4))]:
            pot, bet = int(scene.get('data-'+prefix+'pot')), int(scene.get('data-'+prefix+'bet'))
            current, final = pot+bet, pot+2*bet
            self.assertEqual(Fraction(bet,final), expected)
            self.assertNotEqual(Fraction(bet,current), expected)
            self.assertEqual(expected*final-bet, 0)
        for phrase in ['8 / 40 = 20%', '15 / 60 = 25%', 'is a measured chance', 'Include ties']:
            self.assertIn(phrase, self.source)

    def test_range_possibility_and_the_checked_strong_hand_are_physically_valid(self):
        scene = self.scenes[4]
        known = scene.get('data-hole').split()+scene.get('data-board').split()
        self.assertEqual(len(set(known)), 7)
        self.assertTrue(set(known)&set(scene.get('data-impossible').split()))
        for key in ['data-possible','data-strong']:
            self.assertEqual(len(set(known+scene.get(key).split())), 9)
        board = scene.get('data-board').split()
        self.assertEqual(best(scene.get('data-strong').split()+board), (3,12,9,6))
        self.assertGreater(best(scene.get('data-strong').split()+board), best(known))
        self.assertIn('One reveal does not determine the probabilities', self.source)

    def test_the_restricted_value_comparison_counts_returned_chips_correctly(self):
        scene = self.scenes[5]
        hole, board = scene.get('data-hole').split(), scene.get('data-board').split()
        worse, better = scene.get('data-worse').split(), scene.get('data-better').split()
        self.assertEqual(best(hole+board), (1,10,11,8,5))
        self.assertGreater(best(hole+board), best(worse+board));self.assertLess(best(hole+board), best(better+board))
        for hand in [worse,better]: self.assertEqual(len(set(hole+board+hand)), 9)
        pot, bet, stack = int(scene.get('data-pot')), int(scene.get('data-bet')), 100
        check = Fraction(pot,2)
        fold_net = (stack-bet)+(pot+bet)-stack
        loss_net = (stack-bet)-stack
        self.assertEqual((check,Fraction(fold_net+loss_net,2)), (10,7))
        for formula in ['(20 + 0) / 2 = 10','(20 - 6) / 2 = 7']:
            self.assertIn(formula, self.source)

    def test_workbook_prompts_preview_and_optional_feedback_are_exact_and_private(self):
        workbook = (ROOT / checkpoint.SHEET).read_text()
        rendered = html5lib.parse(self.text, namespaceHTMLElements=False)
        preview = next(p for p in rendered.iter('pre') if p.get('class')=='worksheet-preview')
        self.assertEqual(''.join(preview.itertext()), workbook)
        clean = lambda e: re.sub(r'\s+',' ',' '.join(e.itertext())).strip()
        for scene in self.scenes:
            for choice in scene.find('ol').findall('li'): self.assertIn(clean(choice),workbook)
            changed = next(p for p in scene.findall('p') if clean(p).startswith('Changed situation'))
            self.assertIn(clean(changed),workbook)
        self.assertEqual(workbook.count('My first letter:'),6)
        self.assertEqual(workbook.count('My retry answer and reason:'),6)
        self.assertIn('No workbook is sent automatically',workbook)
        for phrase in ['name and email','No workbook answers are sent automatically','Feedback is optional',
                       'What I was trying to understand','No participant results']:
            self.assertIn(phrase,self.source)
        self.assertNotRegex(self.source,r'<(?:script|form|input|textarea|iframe)\b')
        for path in ['assets/contact.js','_source/contact.html','_source/privacy.html']:
            self.assertEqual(sha256((ROOT/path).read_bytes()).hexdigest(),self.baseline['files'][path])

    def test_six_lesson_arrivals_course_links_live_targets_and_unreviewed_changes(self):
        for route in checkpoint.LESSONS:
            text=self.outputs[build.output_path(route)]
            self.assertIn('id="beginner-checkpoint-invite"',text);self.assertIn(checkpoint.ROUTE,text)
        for path in ['poker/free-poker-learning-path/index.html','poker/topics/learn/index.html',
                     'poker/library/index.html','poker/find/index.html','find/index.html','notes/index.html','sitemap.xml']:
            self.assertIn(checkpoint.ROUTE,self.outputs[Path(path)],path)
        for _,a in Tags(self.source).items:
            href=a.get('href','')
            if href.startswith('/poker/') and '#' in href:
                route,anchor=href.split('#');self.assertIn('id="'+anchor+'"',self.outputs[build.output_path(route)],href)
        targets=check_live.targets();self.assertEqual(len(targets),416)
        self.assertEqual(targets['/'+checkpoint.SHEET],(200,(ROOT/checkpoint.SHEET).read_bytes()))
        self.assertEqual(targets[checkpoint.ROUTE],(200,self.text.encode()))
        body=(ROOT/'_source/poker/free-poker-learning-path.html').read_text()
        free=next(p for p in self.pages if p['path']=='/poker/free-poker-learning-path/')
        entries=poker_library.load(ROOT,self.pages)
        decorated=checkpoint.decorate(free,poker_beginner_path.decorate(free,body,ROOT),ROOT)
        self.assertEqual(next(e['minutes'] for e in entries if e['route']==free['path']),poker_library.minutes(decorated))
        raw=self.outputs[Path('poker/betting-with-a-purpose/index.html')]
        changed=raw.replace('32.5 - 30 = 2.5','32.5 - 30 = 25',1)
        self.assertNotEqual(raw,changed);self.assertEqual(history.before('poker/betting-with-a-purpose/index.html',changed),changed)
        records=deepcopy(self.pages);next(p for p in records if p['id']=='poker-free-poker-learning-path')['description']='Invented success rate'
        self.assertIn('Invented success rate',[p['description'] for p in history.pages(records)])


if __name__ == '__main__': unittest.main()
