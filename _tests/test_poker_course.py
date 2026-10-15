"""Current course contract, independent hand arithmetic and exact predecessor scope."""
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
import check_live
import poker_course as course
import poker_finder
import poker_course_history as history
import poker_practice_history


def document(source):
    return html5lib.parse(source, namespaceHTMLElements=False)


class PokerCourseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.data = course.load(ROOT)
        cls.baseline = json.loads((ROOT / '_tests/poker-course-baseline.json').read_text())

    def test_complete_predecessor_hashes_and_inventory_are_preserved(self):
        b = self.baseline
        self.assertEqual(b['commit'], '75dabee7daeb0d20bf696c48621b5fe8faf2968a')
        self.assertEqual((len(b['pages']), len(b['outputs'])), (192, 219))
        self.assertEqual(history.pages(self.pages), b['pages'])
        previous = history.outputs(self.outputs)
        self.assertEqual(set(map(str, previous)), set(b['outputs']))
        for path, source in previous.items():
            self.assertEqual(sha256(source.encode()).hexdigest(), b['outputs'][str(path)], path)
        for path, digest in {**b['files'], **b['extras']}.items():
            self.assertEqual(sha256(history.before(path, (ROOT / path).read_bytes())).hexdigest(), digest, path)
        self.assertEqual(set(history.change()['new_files']), {course.DATA, course.CSS, course.SCRIPT, '_scripts/poker_course.py'})
        self.assertEqual(set(history.change()['new_outputs']), {'downloads/poker-beginner-study-card.txt'})
        self.assertEqual([p['id'] for p in poker_practice_history.pages(self.pages)], [p['id'] for p in b['pages']])

    def test_history_never_hides_an_unreviewed_change(self):
        for path in ['poker/free-poker-learning-path/index.html', '_scripts/poker_finder.py', '_source/poker/first-decisions.html', course.CSS]:
            value = (ROOT / path).read_bytes() + b'Unreviewed change'
            self.assertEqual(history.before(path, value), value)
        changed = deepcopy(self.pages)
        next(p for p in changed if p['path'] == course.ROUTE)['description'] += 'Unreviewed change'
        self.assertNotEqual(history.pages(changed), self.baseline['pages'])
        sheet_path = Path('downloads/poker-beginner-study-card.txt')
        sheet = self.outputs[sheet_path]
        self.assertIn(sheet_path, history.outputs({sheet_path: sheet + 'Unreviewed change'}))
        self.assertFalse(history.outputs({sheet_path: history.before(sheet_path, sheet)}))

    def test_no_unrelated_article_or_identity_content_is_edited(self):
        allowed = {course.ROUTE, '/poker/no-limit-holdem-guide/', '/poker/poker-books-and-courses/', '/poker/beginner-checkpoint/'} | {'/poker/' + slug + '/' for slug, _ in course.LESSONS}
        for page in self.pages:
            if page['path'] in allowed:
                continue
            if page.get('poker_guide') or page.get('poker_entry') or page.get('note') or page.get('worked_guide') or page.get('living_well_entry') or page['path'] in {'/', '/about/', '/contact/'}:
                path = build.output_path(page['path'])
                self.assertEqual(sha256(self.outputs[path].encode()).hexdigest(), self.baseline['outputs'][str(path)], page['path'])

    def test_six_stages_share_one_order_and_valid_specific_practice(self):
        overview = document(self.outputs[build.output_path(course.ROUTE)])
        path = next(e for e in overview.iter('section') if e.get('id') == 'beginner-practice')
        self.assertEqual([e.get('href') for h in path.iter('h3') for e in h.iter('a')], ['/poker/' + slug + '/' for slug, _ in course.LESSONS])
        later = next(e for e in overview.iter('section') if e.get('class') == 'course-later')
        self.assertFalse(any(e.get('id') in {'first-hand-practice', 'beginner-practice', 'return-practice'} for e in later.iter()))
        for index, lesson in enumerate(self.data['lessons']):
            doc = document(self.outputs[build.output_path('/poker/' + lesson['slug'] + '/')])
            first = next(e for e in doc.iter('aside') if e.get('class') == 'course-first-pass')
            self.assertIn(f'Stage {index + 1} of 6:', ''.join(first.itertext()))
            self.assertEqual([a.get('href') for ul in first.iter('ul') for a in ul.iter('a')], ['#' + a for a, _ in lesson['first_pass']])
            ids = {e.get('id') for e in doc.iter()}
            self.assertTrue(all(a in ids for a, _ in lesson['first_pass']))
            end = next(e for e in doc.iter('aside') if e.get('class') == 'course-stage-end')
            next_route = '/poker/' + self.data['lessons'][index + 1]['slug'] + '/' if index < 5 else '/poker/beginner-checkpoint/'
            self.assertEqual(next(a.get('href') for a in end.iter('a') if a.get('class') == 'button'), next_route)
            self.assertIn(lesson['recall'], ''.join(end.itertext()))
            route, anchor = lesson['practice'].split('#')
            target = document(self.outputs[build.output_path(route)])
            self.assertEqual(sum(e.get('id') == anchor for e in target.iter()), 1)
            nav = next(e for e in doc.iter('details') if e.get('id') == 'beginner-path-navigation')
            self.assertIn(f'Lesson {index + 1} of 6', ''.join(nav.itertext()))
            self.assertEqual(sum(e.get('aria-current') == 'page' for e in nav.iter()), 1)

    def test_hand_cards_ranks_and_hidden_information_are_correct(self):
        hand = self.data['hand']
        self.assertEqual(len(set(hand['hero'] + hand['opponent'] + hand['board'])), 9)
        self.assertEqual(best(hand['hero'] + hand['board'][:3]), (1, 11, 14, 7, 2))
        self.assertEqual(sum(c[1] == 'h' for c in hand['hero'] + hand['board'][:3]), 4)
        self.assertEqual(best(hand['hero'] + hand['board']), (1, 11, 14, 9, 7))
        self.assertEqual(best(hand['opponent'] + hand['board']), (1, 11, 12, 9, 7))
        self.assertGreater(best(hand['hero'] + hand['board']), best(hand['opponent'] + hand['board']))
        scenes = list(document(course.guided_hand(ROOT)).iter('li'))
        scenes = [s for s in scenes if 'data-course-scene' in s.attrib]
        for index, scene in enumerate(scenes):
            visible_cards = [e.get('aria-label') for e in scene.iter() if e.get('role') == 'img']
            self.assertEqual('Queen of hearts' in visible_cards, index == 5)
            self.assertEqual(len(visible_cards), 2 + hand['scenes'][index]['board_count'] + (2 if index == 5 else 0))
            self.assertTrue(all(' of ' in name for name in visible_cards))

    def test_every_scene_conserves_all_six_starting_stacks(self):
        hand = self.data['hand']
        self.assertEqual(hand['starting_stacks'], [100] * 6)
        for scene in hand['scenes']:
            self.assertEqual(scene['pot'] + scene['hero_behind'] + scene['opponent_behind'] + 99 + 300, 600, scene['id'])
            self.assertEqual(scene['pot'], 100 - scene['hero_behind'] + 100 - scene['opponent_behind'] + 1)
        self.assertEqual([(s['pot'], s['hero_behind'], s['opponent_behind']) for s in hand['scenes']], [(3,100,98),(9,94,98),(13,94,94),(29,90,82),(47,82,72),(57,72,72)])
        self.assertEqual(6 - 2, 4)
        self.assertEqual(12 - 4, 8)
        self.assertEqual(13 + 4 + 12 + 8, 37)
        self.assertEqual(Fraction(10, 37 + 10 + 10), Fraction(10,57))
        self.assertAlmostEqual(100 * 10 / 57, 17.54, places=2)
        self.assertEqual(sum(hand['contributions']), 57)
        winner = hand['hero_seat']
        final = [start - paid + (57 if i == winner else 0) for i, (start, paid) in enumerate(zip(hand['starting_stacks'], hand['contributions']))]
        self.assertEqual(final, [100,100,100,129,99,72])
        self.assertEqual(sum(final), 600)
        self.assertEqual(final[winner] - 100, 29)

    def test_worksheet_is_exact_native_preview_and_generated_download(self):
        sheet = course.workbook(ROOT)
        self.assertEqual(self.outputs[Path('downloads/poker-beginner-study-card.txt')], sheet)
        self.assertEqual((ROOT / 'downloads/poker-beginner-study-card.txt').read_text(), sheet)
        doc = document(self.outputs[build.output_path(course.ROUTE)])
        preview = next(e for e in doc.iter('details') if e.get('id') == 'course-workbook-preview')
        self.assertEqual(next(preview.iter('pre')).text, sheet)
        self.assertEqual(sheet.count('[ ]'), 6)
        self.assertEqual(sheet.count('My first reason:'), 6)
        self.assertNotIn('That matches the explanation', sheet)
        self.assertNotIn('Your stack finishes at 129', sheet)

    def test_search_reaches_each_guided_scene_without_solution_spoilers(self):
        page = next(p for p in self.pages if p['path'] == course.ROUTE)
        sections = poker_finder.guide_sections(ROOT, page, build.poker_content.load(ROOT))
        by_anchor = {s['anchor']: s for s in sections}
        for scene in self.data['hand']['scenes']:
            anchor = 'course-scene-' + scene['id']
            self.assertIn(anchor, by_anchor)
            self.assertIn(scene['question'], by_anchor[anchor]['text'])
            self.assertNotIn(scene['solution'], by_anchor[anchor]['text'])
            for _, feedback in scene['choices']:
                self.assertNotIn(feedback, by_anchor[anchor]['text'])
        self.assertIn('current pot 47', by_anchor['course-scene-river']['text'])

    def test_only_the_course_has_optional_practice_javascript(self):
        lessons = {course.ROUTE} | {'/poker/' + slug + '/' for slug, _ in course.LESSONS}
        paths = {build.output_path(route) for route in lessons}
        for path, source in self.outputs.items():
            if path.suffix == '.html':
                self.assertEqual('/assets/poker-course.js?v=' in source, path == build.output_path(course.ROUTE), path)
                self.assertEqual('/assets/poker-course.css?v=' in source, path in paths, path)
        js = (ROOT / course.SCRIPT).read_text()
        for forbidden in ['fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'document.cookie', 'innerHTML', 'eval(', 'location.hash =', 'pushState', 'replaceState']:
            self.assertNotIn(forbidden, js)
        self.assertIn('/' + course.CSS, check_live.targets())
        self.assertIn('/' + course.SCRIPT, check_live.targets())
        self.assertEqual(len(check_live.targets()), 468)

    def test_invalid_cards_stages_repairs_and_duplicate_scenes_are_rejected(self):
        variants = []
        bad = deepcopy(self.data); bad['hand']['hero'][0] = bad['hand']['board'][0]; variants.append(bad)
        bad = deepcopy(self.data); bad['hand']['scenes'][1]['id'] = bad['hand']['scenes'][0]['id']; variants.append(bad)
        bad = deepcopy(self.data); bad['hand']['scenes'][0]['repair'] = '/poker/first-decisions/#missing'; variants.append(bad)
        bad = deepcopy(self.data); bad['lessons'][0]['first_pass'][0][0] = 'missing'; variants.append(bad)
        bad = deepcopy(self.data); bad['lessons'].reverse(); variants.append(bad)
        bad = deepcopy(self.data); bad['hand']['scenes'][0]['correct'] = True; variants.append(bad)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / '_source/poker', root / '_source/poker')
            for bad in variants:
                (root / course.DATA).write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    course.load(root)


if __name__ == '__main__':
    unittest.main()
