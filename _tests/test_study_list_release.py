"""Keep search and teaching evidence intact while improving the private study list."""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
import subprocess
import unittest
from unittest.mock import patch
from test_site import ROOT, build
import poker_study_list_history as history


def load(name, path):
    spec = spec_from_file_location(name, ROOT / path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


capture = load('study_list_capture', '_reports/poker-study-list/capture_history.py')
evaluation = load('study_list_search', '_reports/poker-search-intent/evaluate.py')


class StudyListReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()

    def test_all_existing_search_results_and_passages_remain_identical(self):
        actual = evaluation.evaluate()
        previous = evaluation.evaluate(titles_release=True)
        frozen = json.loads((ROOT / '_reports/poker-search-titles/results.json').read_text())
        self.assertEqual(previous, frozen)
        self.assertEqual(actual, json.loads((ROOT / '_reports/poker-study-list/search-results.json').read_text()))
        for key in ('scope', 'baseline_commit', 'query_sha256', 'entries',
                    'target_hits_top_three', 'total_queries', 'results'):
            self.assertEqual(actual[key], previous[key], key)
        self.assertEqual(actual['target_hits_top_three'], 30)
        current = (ROOT / 'poker/find/index.html').read_text()
        old = history.before('poker/find/index.html', current)
        self.assertEqual(evaluation.Cards(current).rows, evaluation.Cards(old).rows)
        self.assertEqual(len(evaluation.Cards(current).rows), 284)

    def test_frozen_search_releases_replay_in_a_shallow_checkout(self):
        missing = subprocess.CalledProcessError(128, ['git', 'show'])
        with patch.object(evaluation.subprocess, 'check_output', side_effect=missing):
            for flags, path in [
                ({'baseline': True}, '_reports/poker-search-intent/baseline.json'),
                ({'prior_release': True}, '_reports/poker-search-intent/results.json'),
                ({'titles_release': True}, '_reports/poker-search-titles/results.json')]:
                self.assertEqual(evaluation.evaluate(**flags), json.loads((ROOT / path).read_text()))

    def test_only_the_four_reviewed_finder_files_change_from_the_published_parent(self):
        baseline = json.loads((ROOT / '_tests/poker-study-list-baseline.json').read_text())
        self.assertEqual(baseline['commit'], capture.BASE)
        sources = {p.relative_to(ROOT).as_posix(): p.read_bytes() for d in capture.PREFIXES
                   for p in (ROOT / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        outputs = {str(p): value.encode() for p, value in self.outputs.items()}
        self.assertEqual((len(sources), len(outputs)), (baseline['source_count'], baseline['output_count']))
        self.assertEqual(capture.fingerprint({p: history.before(p, raw) for p, raw in sources.items()}),
                         baseline['source_fingerprint'])
        self.assertEqual(capture.fingerprint({p: history.before(p, raw) for p, raw in outputs.items()}),
                         baseline['output_fingerprint'])
        self.assertEqual(set(history.change()['paths']), capture.ALLOWED)

    def test_history_rejects_unreviewed_edits_and_preserves_unrelated_bytes(self):
        for path, item in history.change()['paths'].items():
            raw = (ROOT / path).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), item['new_sha256'])
            self.assertEqual(sha256(history.before(path, raw)).hexdigest(), item['old_sha256'])
            altered = raw + b'Unreviewed'
            self.assertEqual(history.before(path, altered), altered)
        self.assertEqual(history.before('unrelated.bin', b'\xff\x00'), b'\xff\x00')


if __name__ == '__main__':
    unittest.main()
