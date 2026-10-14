"""Beginner course connections, worked checks and independent preservation."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
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
import poker_beginner_path as path
import poker_checkpoint
import poker_library
import learning_path_history as history
import ranges_history
from test_viewer_guides import Tags, best

ROUTE = '/poker/free-poker-learning-path/'
SOURCE = '_source/poker/free-poker-learning-path.html'
ADDITION = '_source/poker/beginner-learning-path.html'


class LearningPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = ranges_history.pages(build.public_pages())
        cls.current_outputs = build.build_outputs()
        cls.outputs = ranges_history.outputs(cls.current_outputs)
        cls.baseline = json.loads((ROOT / '_tests/learning-path-baseline.json').read_text())
        cls.addition = (ROOT / ADDITION).read_text()
        cls.page = next(p for p in cls.pages if p['path'] == ROUTE)

    def test_complete_predecessor_inventory_and_exact_adapters(self):
        b = self.baseline
        self.assertEqual((len(b['pages']), len(b['outputs']), len(b['files'])), (175, 202, 351))
        self.assertEqual(history.pages(self.pages), b['pages'])
        self.assertEqual(set(map(str, self.outputs)), set(b['outputs']))
        changed = []
        for p, raw in self.outputs.items():
            if sha256(raw.encode()).hexdigest() != b['outputs'][str(p)]: changed.append(str(p))
            self.assertEqual(sha256(history.before(p, raw).encode()).hexdigest(), b['outputs'][str(p)], str(p))
        self.assertEqual(len(changed), 14)
        files = {p.relative_to(ROOT).as_posix() for d in ['_source', 'assets', 'downloads']
                 for p in (ROOT / d).rglob('*') if p.is_file()}
        files = ranges_history.files(files)
        self.assertEqual(files - set(b['files']), {ADDITION, path.DOWNLOAD.lstrip('/'), path.CSS})
        for p, digest in b['files'].items():
            self.assertEqual(sha256(history.before(p, ranges_history.before(p, (ROOT / p).read_bytes()))).hexdigest(), digest, p)

    def test_original_article_sources_assets_downloads_and_other_metadata_are_exact(self):
        # Direct hashes bypass every historical adapter.
        for p, digest in self.baseline['files'].items():
            if p not in {'_source/pages.json', '_source/poker/library.json'}:
                self.assertEqual(sha256(ranges_history.before(p, (ROOT / p).read_bytes())).hexdigest(), digest, p)
        current = {p['id']: p for p in self.pages}
        for old in self.baseline['pages']:
            new = current[old['id']]
            if old['path'] == ROUTE:
                self.assertEqual({k: v for k, v in new.items() if k not in {'seo_title', 'description', 'updated', 'revision'}},
                                 {k: v for k, v in old.items() if k not in {'seo_title', 'description', 'updated', 'revision'}})
                self.assertEqual((new['date'], new['updated']), ('2026-10-08', '2026-10-14'))
            else:
                self.assertEqual(new, old, old['id'])

    def test_old_study_plan_is_exact_and_only_its_existing_feed_item_is_revised(self):
        original = (ROOT / SOURCE).read_text()
        decorated = path.decorate(self.page, original, ROOT)
        self.assertEqual(decorated.replace(self.addition, '', 1), original)
        self.assertEqual(decorated.count(self.addition), 1)
        for feed, old in self.baseline['feed_items'].items():
            now = {i.findtext('link'): ET.tostring(i, encoding='unicode')
                   for i in ET.fromstring(self.outputs[Path(feed)]).findall('./channel/item')}
            self.assertEqual(set(now), set(old), feed)
            for url in old:
                if url == 'https://nolankido.com' + ROUTE:
                    a, b = ET.fromstring(old[url]), ET.fromstring(now[url])
                    for field in ['title', 'link', 'guid', 'pubDate']:
                        self.assertEqual(a.findtext(field), b.findtext(field))
                    self.assertEqual(b.findtext('description'), self.page['description'])
                else:
                    self.assertEqual(now[url], old[url], (feed, url))

    def test_four_complete_readiness_checks_have_exact_repair_destinations(self):
        tags = Tags(self.addition).items
        questions = [a for tag, a in tags if tag == 'details']
        self.assertEqual([a['id'] for a in questions], ['path-check-' + v for v in ['cards', 'starting', 'flop', 'river']])
        self.assertTrue(all('open' not in a for a in questions))
        repairs = ['first-decisions/#chips-owed', 'starting-hand-decisions/#position',
                   'first-flop-decisions/#made-and-drawing', 'turn-and-river-decisions/#catching-a-bluff']
        for a, repair in zip(questions, repairs):
            answer = re.search('id="' + a['id'] + r'".*?<div>(.*?)</div></details>', self.addition, re.S)[1]
            self.assertIn('href="/poker/' + repair + '"', answer)
            self.assertGreater(len(re.sub('<[^>]+>', ' ', answer).split()), 65)
            route, anchor = ('/poker/' + repair).split('#')
            self.assertIn('id="' + anchor + '"', self.outputs[build.output_path(route)])
        self.assertNotRegex(self.addition, r'<(?:script|form|input|iframe)\b')
        self.assertNotIn('\u2014', self.addition)

    def test_worked_checks_have_correct_chips_hand_and_equity(self):
        self.assertEqual(7 - 2, 5)
        self.assertIn('7 - 2 = 5', self.addition)
        cards = 'Ah 9h 9s 6h 2h'.split()
        self.assertEqual(len(cards), len(set(cards)))
        self.assertEqual(best(cards), (1, 9, 14, 6, 2))
        self.assertEqual(sum(c.endswith('h') for c in cards), 4)
        self.assertIn('9-9-A-6-2', self.addition)
        self.assertIn('small blind and big blind still have their initial decisions', self.addition)
        pot, bet, call = 30, 10, 10
        self.assertEqual((pot + bet, pot + bet + call), (40, 50))
        threshold = Fraction(call, pot + bet + call)
        self.assertEqual(threshold, Fraction(1, 5))
        self.assertEqual(threshold * (pot + bet + call) - call, 0)
        self.assertIn('10 / 50 = 20%', self.addition)
        self.assertIn('including ties', self.addition)
        self.assertIn('does not compare calling with every possible raise', self.addition)

    def test_all_four_lessons_have_native_order_current_marker_and_private_download(self):
        routes = ['/poker/' + slug + '/' for slug, _ in path.LESSONS]
        for i, route in enumerate(routes):
            page = next(p for p in self.pages if p['path'] == route)
            nav = path.navigation(page, self.pages)
            tags = Tags(nav).items
            current = [(tag, a) for tag, a in tags if a.get('aria-current') == 'page']
            self.assertEqual(current, [('span', {'aria-current': 'page'})])
            self.assertNotIn('href="' + route + '"', nav)
            lesson_links = [a['href'] for tag, a in tags if tag == 'a' and a['href'] in routes]
            self.assertEqual(lesson_links, [v for v in routes if v != route])
            self.assertIn('Lesson ' + str(i + 1) + ' of 4', nav)
            self.assertIn('href="' + path.PATH + '"', nav)
            self.assertIn('href="' + path.DOWNLOAD + '" download', nav)
            self.assertIn(nav, self.outputs[build.output_path(route)])
        for page in self.pages:
            self.assertEqual(bool(path.navigation(page, self.pages)), page['path'] in routes)
        missing = [p for p in self.pages if p['path'] != routes[-1]]
        with self.assertRaises(ValueError): path.navigation(next(p for p in self.pages if p['path'] == routes[0]), missing)
        with self.assertRaises(ValueError): path.decorate(self.page, '<p>No insertion point.</p>', ROOT)
        once = path.decorate(self.page, (ROOT / SOURCE).read_text(), ROOT)
        with self.assertRaises(ValueError): path.decorate(self.page, once, ROOT)

    def test_worksheet_discovery_reading_estimate_schema_and_live_bytes(self):
        worksheet = (ROOT / path.DOWNLOAD.lstrip('/')).read_bytes()
        self.assertIn(b'What I can explain without looking:', worksheet)
        self.assertEqual(worksheet.count(b'[ ]'), 4)
        for slug, _ in path.LESSONS: self.assertIn(('https://nolankido.com/poker/' + slug + '/').encode(), worksheet)
        targets = check_live.targets()
        self.assertEqual(len(targets), 420)
        self.assertEqual(targets[path.DOWNLOAD], (200, worksheet))
        self.assertEqual(targets['/' + path.CSS], (200, (ROOT / path.CSS).read_bytes()))
        for p in self.pages:
            self.assertEqual('/' + path.CSS + '?v=' in self.outputs[build.output_path(p['path'])], p['path'] in ['/poker/' + slug + '/' for slug, _ in path.LESSONS])
        text = self.outputs[build.output_path(ROUTE)]
        self.assertEqual(targets[ROUTE], (200, self.current_outputs[build.output_path(ROUTE)].encode()))
        self.assertIn(path.PATH, self.outputs[Path('poker/topics/learn/index.html')])
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)[1])
        self.assertEqual((schema['datePublished'], schema['dateModified']), ('2026-10-08', '2026-10-14'))
        entries = poker_library.load(ROOT, build.public_pages())
        entry = next(e for e in entries if e['route'] == ROUTE)
        self.assertEqual(entry['minutes'], poker_library.minutes(poker_checkpoint.decorate(self.page, path.decorate(self.page, (ROOT / SOURCE).read_text(), ROOT), ROOT)))
        self.assertIn('beginner-practice-heading', self.outputs[Path('find/index.html')])
        payload = re.search(r'id="find-section-data">(.*?)</script>', self.outputs[Path('find/index.html')], re.S)[1]
        self.assertLess(len(payload.encode()), 60_000)

    def test_no_new_runtime_and_unrelated_files_remain_exact(self):
        before = history.outputs(self.outputs)
        for file, text in self.outputs.items():
            self.assertEqual(re.findall(r'<script[^>]*src="([^"]+)"', text),
                             re.findall(r'<script[^>]*src="([^"]+)"', before[file]), str(file))
        for p, expected in self.baseline['hosting_files'].items():
            self.assertEqual((ROOT / p).read_text() if (ROOT / p).exists() else None, expected, p)

    def test_unreviewed_mutations_are_never_erased_by_history(self):
        for file, old, new in [('poker/free-poker-learning-path/index.html', '10 / 50 = 20%', '10 / 50 = 50%'),
                               ('poker/turn-and-river-decisions/index.html', 'Lesson 4 of 4', 'Lesson 1 of 4'),
                               ('_source/pages.json', 'Learn Poker for Beginners:', 'Invented qualification:')]:
            raw = self.outputs[Path(file)] if Path(file) in self.outputs else (ROOT / file).read_text()
            changed = raw.replace(old, new, 1)
            self.assertNotEqual(raw, changed)
            self.assertEqual(history.before(file, changed), changed)
        pages = deepcopy(self.pages)
        next(p for p in pages if p['path'] == ROUTE)['description'] = 'Unreviewed claim'
        self.assertIn('Unreviewed claim', [p['description'] for p in history.pages(pages)])
        self.assertEqual(history.before('assets/unrelated.bin', b'\xff\x00'), b'\xff\x00')


if __name__ == '__main__': unittest.main()
