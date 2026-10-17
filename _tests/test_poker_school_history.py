"""Independent proof of the exact new page and lossless older-release views."""
from copy import deepcopy
from hashlib import sha1, sha256
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from test_site import ROOT, build
import poker_school_history as school


def fingerprint(records):
    rows = sorted((str(p), sha256(v if isinstance(v, bytes) else v.encode()).hexdigest())
                  for p, v in records.items())
    return sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()


def blob(raw):
    return sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


class PokerSchoolHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.data = school.change()
        cls.base = json.loads((ROOT / '_reports/poker-school-main-blobs.json').read_text())

    def test_all_old_generated_outputs_remain_exact_after_only_the_declared_delta(self):
        old = school.outputs(self.outputs)
        self.assertEqual(set(map(str, old)), set(self.data['base_outputs']))
        for path, value in old.items():
            self.assertEqual(sha256(value.encode()).hexdigest(), self.data['base_outputs'][str(path)], str(path))
            self.assertEqual(blob(value.encode()), self.base['tracked_base_blobs'][str(path)], str(path))
        self.assertEqual(len(self.outputs) - len(old), 1)
        self.assertEqual(set(self.data['new_outputs']), {'poker/school/index.html'})

    def test_all_original_sources_assets_and_downloads_survive(self):
        actual = {p.relative_to(ROOT).as_posix(): p.read_bytes()
                  for folder in ('_source', '_scripts', 'assets', 'downloads')
                  for p in (ROOT / folder).rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts}
        old = school.source_records(actual)
        self.assertEqual(len(old), self.data['base_source_count'])
        self.assertEqual(fingerprint(old), self.data['base_source_fingerprint'])
        for path, raw in old.items():
            self.assertEqual(blob(raw), self.base['tracked_base_blobs'][path], path)

    def test_unknown_edits_cannot_be_hidden_by_the_adapter(self):
        for path, item in self.data['paths'].items():
            raw = (ROOT / path).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), item['new_sha256'], path)
            old = school.before(path, raw)
            self.assertEqual(sha256(old).hexdigest(), item['old_sha256'], path)
            self.assertEqual(blob(old), self.base['tracked_base_blobs'][path], path)
            for changed in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw, raw[1:]):
                self.assertEqual(school.before(path, changed), changed, path)
            self.assertEqual(school.before(path, old), old, path)
        self.assertEqual(school.before('unrelated.bin', b'\xff\0'), b'\xff\0')

    def test_only_byte_identical_added_files_are_excluded_from_old_views(self):
        for key in ('new_files', 'new_outputs'):
            transform = school.source_records if key == 'new_files' else school.outputs
            for path, digest in self.data[key].items():
                raw = (ROOT / path).read_bytes()
                self.assertEqual(sha256(raw).hexdigest(), digest, path)
                self.assertEqual(transform({path: raw}), {})
                unknown = raw + b'UNREVIEWED'
                self.assertEqual(transform({path: unknown}), {path: unknown})
        self.assertEqual(school.source_records({'unexpected': b'new'}), {'unexpected': b'new'})

    def test_only_the_exact_new_metadata_record_is_removed(self):
        records = build.public_pages()
        old = school.pages(records)
        encoded = json.dumps(old, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
        self.assertEqual(sha256(encoded).hexdigest(), self.data['base_pages_fingerprint'])
        self.assertEqual(len(records) - len(old), 1)
        record = deepcopy(self.data['new_pages'][0])
        self.assertEqual(school.pages([record]), [])
        record['description'] += ' Unreviewed promise'
        self.assertEqual(school.pages([record]), [record])
        records[0]['title'] += ' Unreviewed'
        self.assertEqual(school.pages(records)[0], records[0])

    def test_current_search_has_its_own_report_without_rewriting_the_prior_release(self):
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location('school_search_check', ROOT / '_reports/poker-search-intent/evaluate.py')
        evaluation = module_from_spec(spec)
        spec.loader.exec_module(evaluation)
        current = evaluation.evaluate()
        previous = evaluation.evaluate(progress_release=True)
        self.assertEqual(current, json.loads((ROOT / '_reports/poker-school/search-results.json').read_text()))
        self.assertEqual(previous, json.loads((ROOT / '_reports/poker-progress/search-results.json').read_text()))
        self.assertEqual(current['target_hits_top_three'], 30)
        self.assertEqual(current['results'], previous['results'])
        self.assertNotEqual(current['index_sha256'], previous['index_sha256'])
        with self.assertRaises(ValueError):
            evaluation.evaluate(progress_release=True, baseline=True)

    def test_corrupt_reversal_data_is_rejected(self):
        path, item = next(iter(self.data['paths'].items()))
        changed = deepcopy(self.data)
        changed['paths'][path]['edits'][0]['new'] += 'CORRUPT'
        with patch.object(school, 'change', return_value=changed):
            with self.assertRaises(ValueError):
                school.before(path, (ROOT / path).read_bytes())
        changed = deepcopy(self.data)
        changed['paths'][path]['old_sha256'] = '0' * 64
        with patch.object(school, 'change', return_value=changed):
            with self.assertRaises(ValueError):
                school.before(path, (ROOT / path).read_bytes())


if __name__ == '__main__':
    unittest.main()
