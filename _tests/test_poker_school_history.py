"""Independent proof of the exact new page and lossless older-release views."""
from copy import deepcopy
from hashlib import sha1, sha256
from io import BytesIO
import json
from pathlib import Path
import subprocess
import tarfile
import unittest
from unittest.mock import patch

from test_site import ROOT
import poker_school_history as school
import resource_review_history
import later_release_history as later_history


# The complete original School merge. Modern site files contain independent
# later releases, including the deliberate removal of an old Actions file.
# Read only Git objects; never materialize or execute archived workflows.
SCHOOL_RELEASE = 'd77c48f0839f49a89cf829ce17740d7d847aaf68'
RELEASE_TREE = '0516a44df873ccce8c4ce9924d5fc38d0883edfc'


def git_bytes(commit, path):
    return subprocess.check_output(['git', 'show', commit + ':' + path], cwd=ROOT)


def git_archive_files(commit, paths):
    """Read a bounded immutable tree subset entirely in memory."""
    raw = subprocess.check_output(
        ['git', 'archive', '--format=tar', commit, *sorted(paths)], cwd=ROOT)
    with tarfile.open(fileobj=BytesIO(raw), mode='r:') as archive:
        return {entry.name: archive.extractfile(entry).read()
                for entry in archive if entry.isfile() and '__pycache__' not in Path(entry.name).parts}


def fingerprint(records):
    rows = sorted((str(p), sha256(v if isinstance(v, bytes) else v.encode()).hexdigest())
                  for p, v in records.items())
    return sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()


def blob(raw):
    return sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


class PokerSchoolHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = school.change()
        cls.base = json.loads((ROOT / '_reports/poker-school-main-blobs.json').read_text())
        cls.sources = git_archive_files(SCHOOL_RELEASE,
                                        ('_source', '_scripts', 'assets', 'downloads'))
        output_names = set(cls.data['base_outputs']) | set(cls.data['new_outputs'])
        cls.published_outputs = git_archive_files(SCHOOL_RELEASE, output_names)
        cls.changed = {path: git_bytes(SCHOOL_RELEASE, path)
                       for path in cls.data['paths']}
        cls.published_pages = json.loads(cls.sources['_source/pages.json'])

    def test_archived_school_release_matches_its_parent_tree_and_change_ledger(self):
        self.assertEqual(subprocess.check_output(
            ['git', 'rev-parse', SCHOOL_RELEASE + '^'], cwd=ROOT
        ).decode().strip(), self.data['base_commit'])
        self.assertEqual(subprocess.check_output(
            ['git', 'rev-parse', SCHOOL_RELEASE + '^{tree}'], cwd=ROOT
        ).decode().strip(), RELEASE_TREE)
        self.assertEqual(subprocess.check_output(
            ['git', 'rev-parse', self.data['base_commit'] + '^{tree}'], cwd=ROOT
        ).decode().strip(), self.base['base_tree'])
        self.assertEqual(set(self.published_outputs),
                         set(self.data['base_outputs']) | set(self.data['new_outputs']))
        for path, item in self.data['paths'].items():
            with self.subTest(path=path):
                self.assertEqual(sha256(self.changed[path]).hexdigest(), item['new_sha256'])
                self.assertEqual(sha256(git_bytes(self.data['base_commit'], path)).hexdigest(),
                                 item['old_sha256'])

    def test_all_old_generated_outputs_remain_exact_after_only_the_declared_delta(self):
        released = {Path(path): raw.decode('utf-8')
                    for path, raw in self.published_outputs.items()}
        old = school.outputs(released)
        self.assertEqual(set(map(str, old)), set(self.data['base_outputs']))
        for path, value in old.items():
            self.assertEqual(sha256(value.encode()).hexdigest(), self.data['base_outputs'][str(path)], str(path))
            self.assertEqual(blob(value.encode()), self.base['tracked_base_blobs'][str(path)], str(path))
        self.assertEqual(len(later_history.outputs(released)) - len(old), 1)
        self.assertEqual(set(self.data['new_outputs']), {'poker/school/index.html'})

    def test_all_original_sources_assets_and_downloads_survive(self):
        old = school.source_records(self.sources)
        self.assertEqual(len(old), self.data['base_source_count'])
        self.assertEqual(fingerprint(old), self.data['base_source_fingerprint'])
        for path, raw in old.items():
            self.assertEqual(blob(raw), self.base['tracked_base_blobs'][path], path)

    def test_unknown_edits_cannot_be_hidden_by_the_adapter(self):
        for path, item in self.data['paths'].items():
            raw = self.changed[path]
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
                raw = self.sources[path] if key == 'new_files' else self.published_outputs[path]
                self.assertEqual(sha256(raw).hexdigest(), digest, path)
                self.assertEqual(transform({path: raw}), {})
                unknown = raw + b'UNREVIEWED'
                self.assertEqual(transform({path: unknown}), {path: unknown})
        self.assertEqual(school.source_records({'unexpected': b'new'}), {'unexpected': b'new'})

    def test_only_the_exact_new_metadata_record_is_removed(self):
        # Compare original source manifests directly at the reviewed Git
        # boundary. Today's composed manifest includes later independent
        # article and profile registrations and cannot be this old snapshot.
        records = deepcopy(self.published_pages)
        old = school.pages(records)
        self.assertEqual(old, json.loads(git_bytes(self.data['base_commit'],
                                                  '_source/pages.json')))
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
        # This stored report belongs to the School release. Reconstruct its
        # exact approved index before comparing; keep the original report fixed.
        # Current index behavior has a separate resource-review regression.
        read_text = Path.read_text
        def school_index(path, *args, **kwargs):
            text = read_text(path, *args, **kwargs)
            return resource_review_history.before('poker/find/index.html', text) if path == ROOT / 'poker/find/index.html' else text
        with patch.object(Path, 'read_text', school_index):
            current = evaluation.evaluate()
            previous = evaluation.evaluate(progress_release=True)
        self.assertEqual(current, json.loads((ROOT / '_reports/poker-school/search-results.json').read_text()))
        self.assertEqual(previous, json.loads((ROOT / '_reports/poker-progress/search-results.json').read_text()))
        self.assertEqual(current['target_hits_top_three'], 30)
        self.assertEqual(current['entries'], previous['entries'] + 1)
        # One new page may match behind the first three. Preserve the actual
        # rankings, scores, passages and target outcomes, not an obsolete count.
        self.assertEqual(len(current['results']), len(previous['results']))
        for present, prior in zip(current['results'], previous['results']):
            self.assertEqual({k: v for k, v in present.items() if k != 'matches'},
                             {k: v for k, v in prior.items() if k != 'matches'})
            self.assertIn(present['matches'] - prior['matches'], (0, 1))
        self.assertNotEqual(current['index_sha256'], previous['index_sha256'])
        with self.assertRaises(ValueError):
            evaluation.evaluate(progress_release=True, baseline=True)

    def test_corrupt_reversal_data_is_rejected(self):
        path, item = next(iter(self.data['paths'].items()))
        changed = deepcopy(self.data)
        changed['paths'][path]['edits'][0]['new'] += 'CORRUPT'
        with patch.object(school, 'change', return_value=changed):
            with self.assertRaises(ValueError):
                school.before(path, self.changed[path])
        changed = deepcopy(self.data)
        changed['paths'][path]['old_sha256'] = '0' * 64
        with patch.object(school, 'change', return_value=changed):
            with self.assertRaises(ValueError):
                school.before(path, self.changed[path])


if __name__ == '__main__':
    unittest.main()
