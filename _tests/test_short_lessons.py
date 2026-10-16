"""Check learning tasks against independent cards and the exact prior release."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import re
import shutil
import unittest
import html5lib
from test_site import ROOT, build
from test_viewer_guides import best
import poker_course
import poker_lessons
import poker_finder
import search_sections
import short_lessons_history as history


class ShortLessonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slugs = [slug for slug, _ in poker_course.LESSONS]
        cls.lessons = poker_lessons.load(ROOT, cls.slugs)
        cls.outputs = build.build_outputs()
        cls.baseline = json.loads((ROOT / '_tests/short-lessons-baseline.json').read_text())

    def test_exact_prior_release_and_inventory_survive_only_the_reviewed_delta(self):
        b = self.baseline
        self.assertEqual((b['commit'], len(b['pages']), len(b['outputs']), len(b['files'])), ('bf9a4ae8a4f6afb173ce309bd18a954718db1eca', 193, 221, 476))
        self.assertEqual(history.pages(build.public_pages()), b['pages'])
        restored = history.outputs(self.outputs)
        self.assertEqual(set(map(str, restored)), set(b['outputs']))
        for path, value in restored.items():
            self.assertEqual(sha256(value.encode()).hexdigest(), b['outputs'][str(path)], str(path))
        for path, digest in {**b['files'], **b['extras']}.items():
            self.assertEqual(sha256(history.before(path, (ROOT / path).read_bytes())).hexdigest(), digest, path)
        actual = {p.relative_to(ROOT).as_posix() for d in ['_source', '_scripts', 'assets', 'downloads'] for p in (ROOT / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        self.assertEqual(history.files(actual), set(b['files']))
        self.assertEqual(set(history.change()['new_files']), {poker_lessons.DATA, '_scripts/poker_lessons.py'})
        self.assertEqual(history.change()['new_pages'], {})
        self.assertEqual(history.change()['new_outputs'], {})

    def test_history_does_not_conceal_unreviewed_content(self):
        for path in ['_scripts/poker_course.py', 'assets/poker-course.css', 'poker/first-decisions/index.html', 'downloads/poker-beginner-study-card.txt']:
            modified = (ROOT / path).read_bytes() + b'Unreviewed change'
            self.assertEqual(history.before(path, modified), modified)
        pages = deepcopy(build.public_pages())
        next(p for p in pages if p['path'] == '/poker/first-decisions/')['description'] += 'Unreviewed change'
        self.assertNotEqual(history.pages(pages), self.baseline['pages'])

    def test_six_native_lessons_offer_a_model_attempt_repair_and_continuation(self):
        for index, lesson in enumerate(self.lessons):
            source = self.outputs[Path('poker') / lesson['slug'] / 'index.html']
            doc = html5lib.parse(source, namespaceHTMLElements=False)
            first = next(e for e in doc.iter('section') if e.get('class') == 'course-first-pass')
            ids = [e.get('id') for e in first.iter()]
            self.assertLess(ids.index('course-lesson-model'), ids.index('course-lesson-try'))
            self.assertLess(ids.index('course-lesson-try'), ids.index('course-lesson-answer'))
            answer = next(e for e in first.iter('details') if e.get('id') == 'course-lesson-answer')
            self.assertNotIn('open', answer.attrib)
            self.assertIn(lesson['attempt']['prompt'], ''.join(first.itertext()))
            self.assertIn(lesson['attempt']['repair'], [a.get('href') for a in answer.iter('a')])
            nav = next(e for e in first.iter('nav') if e.get('class') == 'course-lesson-next')
            expected = '/poker/' + self.slugs[index + 1] + '/' if index < 5 else '/poker/beginner-checkpoint/'
            self.assertEqual(next(nav.iter('a')).get('href'), expected)
            self.assertFalse(list(first.iter('input')) + list(first.iter('textarea')))
            original = (ROOT / '_source/poker' / (lesson['slug'] + '.html')).read_text()
            self.assertEqual(sha256(original.encode()).hexdigest(), self.baseline['files']['_source/poker/' + lesson['slug'] + '.html'])
            for anchor in re.findall(r'\bid="([^"]+)"', original):
                self.assertEqual(source.count('id="' + anchor + '"'), 1)
            self.assertLess(source.index('id="course-lesson-try"'), source.index('id="lesson-reference"'))

    def test_all_changed_hands_and_draws_match_an_independent_ranker(self):
        expectations = {
            0: [(1, 12, 11, 8, 3), (1, 12, 11, 9, 5)],
            2: [(1, 10, 14, 7, 2), (1, 13, 12, 8, 3)],
            3: [(1, 11, 10, 8, 5), (1, 12, 11, 9, 6)],
            4: [(1, 10, 14, 8, 5), (1, 12, 13, 9, 6)],
            5: [(1, 10, 11, 8, 5), (1, 9, 11, 8, 7)]
        }
        for index, ranks in expectations.items():
            for case, expected in zip([self.lessons[index]['worked'], self.lessons[index]['attempt']], ranks):
                self.assertEqual(best([c for g in case['cards'] for c in g['values']]), expected, index)
        for index in [2, 3]:
            for key, suit in [('worked', 'h'), ('attempt', 's')]:
                known = [c for g in self.lessons[index][key]['cards'] for c in g['values']]
                self.assertEqual(sum(c[1] == suit for c in known), 4)

    def test_range_candidates_separate_impossible_legal_and_stronger(self):
        for key in ['worked', 'attempt']:
            case = self.lessons[4][key]
            hero, board = [g['values'] for g in case['cards']]
            legal = [not (set(c['values']) & set(hero + board)) for c in case['candidates']]
            self.assertEqual(legal, [False, True, True])
            stronger = [best(c['values'] + board) > best(hero + board) for c in case['candidates'][1:]]
            self.assertEqual(stronger, [False, True] if key == 'worked' else [True, False])
        for key in ['worked', 'attempt']:
            case = self.lessons[5][key]
            hero, board = [g['values'] for g in case['cards']]
            weak, strong = [c['values'] for c in case['candidates']]
            for candidate in [weak, strong]:
                self.assertFalse(set(candidate) & set(hero + board))
            self.assertLess(best(weak + board), best(hero + board))
            self.assertGreater(best(strong + board), best(hero + board))

    def test_payment_and_price_explanations_count_the_current_round_and_final_pot(self):
        self.assertIn('7 - 0 = 7', ' '.join(self.lessons[0]['attempt']['answer']))
        self.assertIn('6 - 1 = 5', ' '.join(self.lessons[1]['attempt']['answer']))
        for key, earlier_pot, bet, percentage in [('worked', 24, 12, 25), ('attempt', 36, 12, 20)]:
            final_pot = earlier_pot + bet * 2
            self.assertEqual(Fraction(bet, final_pot), Fraction(percentage, 100))
            self.assertIn(f'{bet} / {final_pot} = {percentage}%', ' '.join(self.lessons[3][key]['answer']))

    def test_private_study_card_contains_attempts_without_revealed_solutions(self):
        sheet = poker_course.workbook(ROOT)
        self.assertIn('Qh means queen of hearts', sheet)
        for lesson in self.lessons:
            self.assertIn(lesson['attempt']['prompt'], sheet)
            for answer in lesson['attempt']['answer']:
                self.assertNotIn(answer, sheet)
        doc = html5lib.parse(self.outputs[Path('poker/free-poker-learning-path/index.html')], namespaceHTMLElements=False)
        preview = next(e for e in doc.iter('details') if e.get('id') == 'course-workbook-preview')
        self.assertEqual(next(preview.iter('pre')).text, sheet)

    def test_search_retains_reference_sections_and_excludes_attempt_answers(self):
        pages = build.public_pages()
        index = search_sections.index(self.outputs, pages)
        for lesson in self.lessons:
            route = '/poker/' + lesson['slug'] + '/'
            self.assertIn(['course-first-pass-title', 'Start with the short lesson.'], index[route])
            self.assertIn(['lesson-reference', 'Full explanation and more examples'], index[route])
            text = ' '.join(s['text'] for s in poker_finder.guide_sections(ROOT, next(p for p in pages if p['path'] == route), {}))
            self.assertIn(lesson['idea'], text)
            for answer in lesson['attempt']['answer']:
                self.assertNotIn(answer, text)

    def test_malformed_lessons_fail_instead_of_publishing_broken_exercises(self):
        original = json.loads((ROOT / poker_lessons.DATA).read_text())
        variants = []
        bad = deepcopy(original); bad['version'] = 2; variants.append(bad)
        bad = deepcopy(original); bad['lessons'].reverse(); variants.append(bad)
        bad = deepcopy(original); bad['lessons'][0]['worked']['cards'][0]['values'][0] = '1s'; variants.append(bad)
        bad = deepcopy(original); bad['lessons'][0]['worked']['cards'][1]['values'][0] = 'Qh'; variants.append(bad)
        bad = deepcopy(original); bad['lessons'][0]['attempt']['repair'] = '/poker/first-decisions/#missing'; variants.append(bad)
        bad = deepcopy(original); bad['lessons'][0]['attempt']['prompt'] = ''; variants.append(bad)
        for bad in variants:
            with TemporaryDirectory() as folder:
                root = Path(folder)
                shutil.copytree(ROOT / '_source/poker', root / '_source/poker')
                (root / poker_lessons.DATA).write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    poker_lessons.load(root, self.slugs)

    def test_short_lessons_add_no_script_or_personal_state_and_stay_bounded(self):
        for path, digest in self.baseline['files'].items():
            if path.endswith('.js'):
                self.assertEqual(sha256(history.before(path, (ROOT / path).read_bytes())).hexdigest(), digest, path)
        for lesson in self.lessons:
            self.assertLess(len(json.dumps(lesson).split()), 550)
            self.assertNotIn(chr(0x2014), json.dumps(lesson, ensure_ascii=False))


if __name__ == '__main__':
    unittest.main()
