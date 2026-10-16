"""Six-seat position teaching, native access and the exact published predecessor."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
import html5lib
from test_site import ROOT, build
import poker_course
import poker_lessons
import position_maps_history as history


class PositionMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.baseline = json.loads((ROOT / '_tests/position-maps-baseline.json').read_text())
        cls.route = '/poker/starting-hand-decisions/'
        cls.html = cls.outputs[build.output_path(cls.route)]
        cls.doc = html5lib.parse(cls.html, namespaceHTMLElements=False)
        cls.lesson = poker_lessons.load(ROOT, [s for s, _ in poker_course.LESSONS])[1]

    def test_exact_predecessor_survives_only_the_reviewed_delta(self):
        b = self.baseline
        self.assertEqual((b['commit'], len(b['pages']), len(b['outputs']), len(b['files'])), ('515ca7e2fec02ed8177d3e0aa474a7a28fce5dc6', 193, 221, 480))
        self.assertEqual(history.pages(build.public_pages()), b['pages'])
        restored = history.outputs(self.outputs)
        self.assertEqual(set(map(str, restored)), set(b['outputs']))
        for p, text in restored.items():
            self.assertEqual(sha256(text.encode()).hexdigest(), b['outputs'][str(p)], str(p))
        for p, digest in {**b['files'], **b['extras']}.items():
            self.assertEqual(sha256(history.before(p, (ROOT / p).read_bytes())).hexdigest(), digest, p)
        files = {p.relative_to(ROOT).as_posix() for d in ['_source', '_scripts', 'assets', 'downloads'] for p in (ROOT / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        self.assertEqual(files, set(b['files']))
        self.assertEqual(history.change()['new_pages'], {})
        self.assertEqual(history.change()['new_outputs'], {})
        self.assertEqual(history.change()['new_files'], {})
        for p in ['_scripts/poker_lessons.py', '_source/poker/course-lessons.json', 'assets/poker-course.css', 'poker/starting-hand-decisions/index.html']:
            raw = (ROOT / p).read_bytes() + b'Unreviewed change'
            self.assertEqual(history.before(p, raw), raw)

    def test_existing_lesson_content_scripts_downloads_and_full_articles_are_unchanged(self):
        path = poker_lessons.DATA
        current = json.loads((ROOT / path).read_text())
        original = json.loads(history.before(path, (ROOT / path).read_text()))
        for lesson in current['lessons']:
            for key in ['worked', 'attempt']:
                lesson[key].pop('table', None)
        self.assertEqual(current, original)
        for p, digest in self.baseline['files'].items():
            if p.endswith('.js') or p.startswith('downloads/') or p in ['_source/poker/' + s + '.html' for s, _ in poker_course.LESSONS]:
                self.assertEqual(sha256((ROOT / p).read_bytes()).hexdigest(), digest, p)
        for lesson in poker_lessons.load(ROOT, [s for s, _ in poker_course.LESSONS]):
            self.assertLess(len(json.dumps(lesson).split()), 550)

    def test_maps_expose_every_seat_and_match_both_original_ledgers(self):
        figures = [e for e in self.doc.iter('figure') if e.get('class') == 'course-position-map']
        self.assertEqual(len(figures), 2)
        names = ['First seat', 'Next seat', 'Cutoff', 'Button', 'Small blind', 'Big blind']
        for fig, hero, folded, paid in zip(figures, [3, 4], [[0, 1, 2], [0, 1]], [[0, 0, 0, 0, 1, 2], [0, 0, 6, 6, 1, 2]]):
            rows = list(next(fig.iter('ol')))
            self.assertEqual(len(rows), 6)
            self.assertEqual([next(r.iter('strong')).text for r in rows], names)
            self.assertEqual([i for i, r in enumerate(rows) if 'is-you' in r.get('class', '').split()], [hero])
            self.assertEqual([i for i, r in enumerate(rows) if 'is-folded' in r.get('class', '').split()], folded)
            for i, row in enumerate(rows):
                text = ''.join(row.itertext())
                self.assertIn('Seat ' + str(i + 1) + ' ' + names[i] + ' ', text)
                self.assertIn(' Paid ' + str(paid[i]), text)
                self.assertIn('Seat ' + str(i + 1), text)
                self.assertIn('Paid ' + str(paid[i]), text)
                self.assertIn('You: your turn' if i == hero else 'Folded' if i in folded else 'Already acted' if i < hero else 'Not acted yet', text)
            self.assertIn('Dealer button', ''.join(rows[3].itertext()))
            self.assertIn('button moves', ''.join(fig.itertext()))

    def test_initial_preflop_and_conditional_flop_orders_are_distinct(self):
        orders = [e for e in self.doc.iter('div') if e.get('class') == 'course-position-orders']
        expected = [
            [['Small blind', 'Big blind'], ['Small blind', 'Big blind', 'Button (you)']],
            [['Big blind'], ['Small blind (you)', 'Big blind', 'Cutoff', 'Button']]
        ]
        self.assertEqual(len(orders), 2)
        for group, queues in zip(orders, expected):
            self.assertEqual([[''.join(li.itertext()) for li in ol] for ol in group.iter('ol')], queues)
            self.assertIn('if every live seat continues', ''.join(group.itertext()))
        answer = next(e for e in self.doc.iter('details') if e.get('id') == 'course-lesson-answer')
        self.assertNotIn('open', answer.attrib)
        self.assertIn(orders[1], list(answer.iter()))
        self.assertNotIn(orders[0], list(answer.iter()))
        self.assertIn('a later bet or raise', self.html)

    def test_invalid_position_scenes_fail_before_publishing(self):
        original = json.loads((ROOT / poker_lessons.DATA).read_text())
        variants = []
        for update in [{'hero': True}, {'hero': 6}, {'paid': [0, 0, 0, 0, 1]}, {'paid': [0, 0, 0, 0, 1, 0]}, {'paid': [0, 0, 0, -1, 1, 2]}, {'paid': [0, 0, 100, 0, 1, 2]}, {'folded': [0, 0, 2]}, {'folded': [0, 1, 3]}, {'paid': [1, 0, 0, 0, 1, 2]}, {'extra': 'unreviewed'}]:
            bad = deepcopy(original); bad['lessons'][1]['worked']['table'].update(update); variants.append(bad)
        bad = deepcopy(original); bad['lessons'][1]['attempt']['table']['paid'] = [0, 0, 3, 3, 1, 2]; variants.append(bad)
        bad = deepcopy(original); bad['lessons'][1]['attempt']['table']['paid'][3] = 5; variants.append(bad)
        bad = deepcopy(original); del bad['lessons'][1]['attempt']['table']; variants.append(bad)
        bad = deepcopy(original); bad['lessons'][0]['worked']['table'] = original['lessons'][1]['worked']['table']; variants.append(bad)
        with TemporaryDirectory() as folder:
            root = Path(folder); target = root / '_source/poker'; target.mkdir(parents=True)
            for slug, _ in poker_course.LESSONS:
                (target / (slug + '.html')).write_bytes((ROOT / '_source/poker' / (slug + '.html')).read_bytes())
            for bad in variants:
                (root / poker_lessons.DATA).write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    poker_lessons.load(root, [s for s, _ in poker_course.LESSONS])

    def test_only_revised_lesson_gets_the_new_date(self):
        for index, (slug, _) in enumerate(poker_course.LESSONS):
            doc = html5lib.parse(self.outputs[Path('poker') / slug / 'index.html'], namespaceHTMLElements=False)
            first = next(e for e in doc.iter('section') if e.get('class') == 'course-first-pass')
            note = next(e for e in first.iter('p') if e.get('class') == 'editorial-note')
            self.assertTrue(''.join(note.itertext()).startswith('Updated October ' + ('16' if index == 1 else '15') + ', 2026:'))


if __name__ == '__main__':
    unittest.main()
