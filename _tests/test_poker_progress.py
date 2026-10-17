"""Private course progress preserves teaching, old releases and native access."""
from copy import deepcopy
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import unittest
from urllib.parse import urlsplit

from test_site import ROOT, Page, build
import poker_progress_history as history


def load(name, path):
    spec = spec_from_file_location(name, ROOT / path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


capture = load('progress_capture', '_reports/poker-progress/capture_history.py')
live = load('progress_live', '_scripts/check_live.py')
evaluation = load('progress_search', '_reports/poker-search-intent/evaluate.py')


class PokerProgressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.baseline = json.loads((ROOT / '_tests/poker-progress-baseline.json').read_text())

    def test_exact_published_parent_survives_only_the_reviewed_progress_release(self):
        b = self.baseline
        self.assertEqual(b['commit'], 'ca0264c251f2c999a8375d9e748521fe46ef22fe')
        sources = {p.relative_to(ROOT).as_posix(): p.read_bytes() for d in capture.PREFIXES
                   for p in (ROOT / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        old_sources = history.source_records(sources)
        self.assertEqual((len(old_sources), len(self.outputs)), (480, 221))
        self.assertEqual(len(sources), 483)
        self.assertEqual(capture.fingerprint({p: history.before(p, raw) for p, raw in old_sources.items()}), b['source_fingerprint'])
        self.assertEqual(capture.fingerprint({str(p): history.before(str(p), raw.encode()) for p, raw in self.outputs.items()}), b['output_fingerprint'])
        self.assertEqual(set(history.change()['paths']), capture.SOURCE_EDITS | capture.OUTPUT_EDITS | capture.EXTRA_EDITS)
        self.assertEqual(set(history.change()['new_files']), capture.NEW_FILES)
        self.assertEqual(set(history.change()['pages']), {'privacy', 'poker-study'})
        for path, digest in b['extras'].items():
            self.assertEqual(sha256(history.before(path, (ROOT / path).read_bytes())).hexdigest(), digest, path)

    def test_unknown_changes_are_not_removed_from_historical_views(self):
        for path, item in history.change()['paths'].items():
            raw = (ROOT / path).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), item['new_sha256'], path)
            self.assertEqual(sha256(history.before(path, raw)).hexdigest(), item['old_sha256'], path)
            mutation = raw + b'Unreviewed change'
            self.assertEqual(history.before(path, mutation), mutation, path)
        for path, digest in history.change()['new_files'].items():
            raw = (ROOT / path).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), digest, path)
            self.assertEqual(history.source_records({path: raw}), {})
            self.assertEqual(history.source_records({path: raw + b'Unreviewed'}), {path: raw + b'Unreviewed'})
        for key, pair in history.change()['pages'].items():
            self.assertEqual(history.pages([pair['new']]), [pair['old']], key)
            self.assertEqual(pair['old'], dict(pair['new'], updated=pair['old']['updated']), key)
            pages = deepcopy(build.public_pages())
            next(p for p in pages if p['id'] == key)['description'] += ' Unreviewed claim'
            self.assertIn('Unreviewed claim', next(p for p in history.pages(pages) if p['id'] == key)['description'])
        self.assertEqual(history.before('unknown.bin', b'\xff\x00'), b'\xff\x00')

    def test_instructional_material_is_identical_except_the_explicit_operating_notice(self):
        original_sentence = 'The website does not receive this file or save your progress.'
        new_notice = ("The website does not receive this file or your answers.',\n"
                      "             'Optional lesson marks can stay in your browser through the Study desk:',\n"
                      "             'https://nolankido.com/poker/study/#course-progress")
        for path, digest in self.baseline['teaching_inputs'].items():
            current = (ROOT / path).read_bytes()
            if path == '_scripts/poker_course.py':
                previous = history.before(path, current)
                self.assertEqual(previous.decode().count(original_sentence), 1)
                self.assertEqual(current.decode(), previous.decode().replace(original_sentence, new_notice))
            else:
                self.assertEqual(sha256(current).hexdigest(), digest, path)
        sheet_path = 'downloads/poker-beginner-study-card.txt'
        sheet = (ROOT / sheet_path).read_text()
        previous = history.before(sheet_path, sheet)
        self.assertEqual(sheet, previous.replace(original_sentence,
            'The website does not receive this file or your answers.\n'
            'Optional lesson marks can stay in your browser through the Study desk:\n'
            'https://nolankido.com/poker/study/#course-progress'))

    def test_native_course_destinations_scoped_assets_and_live_verification(self):
        study = Page(self.outputs[Path('poker/study/index.html')])
        links = {a.get('href') for a in study.tags('a')}
        reading_paths = {urlsplit(link).path for link in links if link}
        course = json.loads((ROOT / '_source/poker/beginner-course.json').read_text())
        for lesson in course['lessons']:
            self.assertIn('/poker/' + lesson['slug'] + '/', reading_paths)
            self.assertIn(lesson['practice'], links)
        self.assertIn('/downloads/poker-beginner-study-card.txt', links)
        for path, content in self.outputs.items():
            if path.suffix != '.html':
                continue
            scripts = [urlsplit(s['src']).path for s in Page(content).tags('script') if s.get('src')]
            self.assertEqual(scripts.count('/assets/poker-progress.js'), int(path == Path('poker/study/index.html')), str(path))
        targets = live.targets(ROOT)
        for route in ['/poker/study/', '/assets/poker-progress.js', '/assets/poker-progress.css']:
            self.assertIn(route, targets)
        self.assertEqual(len(targets), 475)
        privacy = self.outputs[Path('privacy/index.html')]
        for phrase in ['Optional Poker Foundations progress', 'one entry in your browser', 'without progress events', 'does not upload the file or enable device saving']:
            self.assertIn(phrase, privacy)

    def test_teaching_review_remains_pending_with_the_same_mechanical_evidence(self):
        scope = json.loads((ROOT / '_reports/poker-teaching-review/scope.json').read_text())
        self.assertEqual(scope['human_review'], 'pending')
        self.assertEqual(set(scope['source_files']), set(self.baseline['teaching_inputs']))
        for path, digest in scope['source_files'].items():
            self.assertEqual(sha256((ROOT / path).read_bytes()).hexdigest(), digest)
        changes = {p for p, digest in scope['source_files'].items() if digest != self.baseline['teaching_inputs'][p]}
        self.assertEqual(changes, {'_scripts/poker_course.py'})
        self.assertNotEqual(scope['fingerprint'], self.baseline['teaching_fingerprint'])
        form = (ROOT / '_reports/poker-teaching-review/review-form.md').read_text()
        self.assertEqual(form.count('| unreviewed |'), 18)
        evidence = json.loads((ROOT / '_reports/poker-teaching-review/mechanics.json').read_text())
        self.assertEqual(len(evidence['cases']), 28)

    def test_search_preserves_all_declared_results_and_passages(self):
        current = evaluation.evaluate()
        previous = evaluation.evaluate(study_list_release=True)
        self.assertEqual(previous, json.loads((ROOT / '_reports/poker-study-list/search-results.json').read_text()))
        self.assertEqual(current, json.loads((ROOT / '_reports/poker-progress/search-results.json').read_text()))
        self.assertEqual(set(current), set(previous))
        for key in current:
            if key != 'index_sha256':
                self.assertEqual(current[key], previous[key], key)
        self.assertNotEqual(current['index_sha256'], previous['index_sha256'])
        self.assertEqual((current['entries'], current['target_hits_top_three'], current['total_queries']), (284, 30, 30))


if __name__ == '__main__':
    unittest.main()
