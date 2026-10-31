"""Later publications remain explicit, exact and independent of old baselines."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import unittest
import sys

import later_release_history as history
import visibility_sprint_history as subsequent_changes
import identity_turn03_history

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))


def release_bytes(path):
    """Inspect this older release after reversing only the reviewed sprint."""
    return subsequent_changes.before(path, (ROOT / path).read_bytes())


class LaterReleaseHistoryTests(unittest.TestCase):
    def test_build_timeout_reversal_restores_the_exact_regional_successor(self):
        import regional_link_history
        current = release_bytes(history.CHECKS_WORKFLOW)
        self.assertEqual(sha256(current).hexdigest(), history.WORKFLOW_AFTER)
        previous = history.before(history.CHECKS_WORKFLOW, current)
        self.assertEqual(sha256(previous).hexdigest(), history.WORKFLOW_BEFORE)
        regional = regional_link_history.change()['paths'][history.CHECKS_WORKFLOW]
        self.assertEqual(history.WORKFLOW_BEFORE, regional['new_sha256'])
        self.assertEqual(sha256(regional_link_history.before(
            history.CHECKS_WORKFLOW, current)).hexdigest(), regional['old_sha256'])
        self.assertEqual(history.before(history.CHECKS_WORKFLOW, previous), previous)
        self.assertEqual(history.before(ROOT / history.CHECKS_WORKFLOW, current.decode()),
                         previous.decode())
        self.assertEqual(current.split(b'  browser:\n', 1)[1],
                         previous.split(b'  browser:\n', 1)[1])

    def test_other_job_timeouts_and_unknown_workflow_bytes_are_not_rewritten(self):
        raw = release_bytes(history.CHECKS_WORKFLOW)
        replacements = (
            (b'    timeout-minutes: 15\n', b'    timeout-minutes: 20\n'),
            (b'    timeout-minutes: 2\n', b'    timeout-minutes: 3\n'),
            (b'    timeout-minutes: 10\n', b'    timeout-minutes: 11\n'),
            (b'    timeout-minutes: 30\n', b'    timeout-minutes: 31\n'),
        )
        for old, new in replacements:
            with self.subTest(timeout=old):
                self.assertEqual(raw.count(old), 1)
                changed = raw.replace(old, new, 1)
                self.assertEqual(history.before(history.CHECKS_WORKFLOW, changed), changed)
        for changed in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw, raw[1:]):
            self.assertEqual(history.before(history.CHECKS_WORKFLOW, changed), changed)
        self.assertEqual(history.before('.github/workflows/other.yml', raw), raw)

    def test_corrupt_timeout_predecessor_and_replacement_fail_closed(self):
        raw = release_bytes(history.CHECKS_WORKFLOW)
        for name, bad in [('WORKFLOW_BEFORE', '0' * 64),
                          ('BUILD_JOB_AFTER', 'not the approved job'),
                          ('BUILD_JOB_BEFORE', 'not the approved predecessor')]:
            with self.subTest(name=name), patch.object(history, name, bad):
                with self.assertRaises(ValueError):
                    history.before(history.CHECKS_WORKFLOW, raw)

    def test_identity_build_has_an_exact_successor_and_predecessor(self):
        current = release_bytes(history.IDENTITY_BUILD)
        self.assertEqual(sha256(current).hexdigest(), history.BUILD_AFTER)
        previous = history.before(history.IDENTITY_BUILD, current)
        self.assertEqual(sha256(previous).hexdigest(), history.BUILD_BEFORE)
        self.assertEqual(history.before(history.IDENTITY_BUILD, previous), previous)
        self.assertEqual(history.before(Path(history.IDENTITY_BUILD), current.decode()), previous.decode())
        self.assertIn("outputs[Path('assets/nolan-kido-identity.jsonld')]", current.decode())
        self.assertNotIn("outputs[Path('assets/nolan-kido-identity.jsonld')]", previous.decode())

    def test_unknown_build_bytes_and_wrong_paths_are_not_rewritten(self):
        raw = release_bytes(history.IDENTITY_BUILD)
        for changed in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw, raw[1:]):
            self.assertEqual(history.before(history.IDENTITY_BUILD, changed), changed)
        self.assertEqual(history.before('other/build.py', raw), raw)
        self.assertEqual(history.before('other.bin', b'\xff\x00'), b'\xff\x00')

    def test_corrupt_build_predecessor_and_insertion_fail_closed(self):
        raw = release_bytes(history.IDENTITY_BUILD)
        for name, bad in [('BUILD_BEFORE', '0' * 64),
                          ('BUILD_INSERTION', 'not the approved insertion')]:
            with self.subTest(name=name), patch.object(history, name, bad):
                with self.assertRaises(ValueError):
                    history.before(history.IDENTITY_BUILD, raw)

    def test_known_added_files_match_the_separate_reviewed_releases(self):
        self.assertEqual(set(history.SOURCE_ADDITIONS), {
            '_source/person-schema.jsonld', 'assets/nolan-kido-identity.jsonld',
            'assets/social/nolan-kido-ai.png',
        })
        for name, expected in history.SOURCE_ADDITIONS.items():
            with self.subTest(name=name):
                reviewed = identity_turn03_history.before(name, (ROOT / name).read_bytes())
                self.assertEqual(sha256(reviewed).hexdigest(), expected)

    def test_output_view_only_omits_the_exact_added_generated_asset(self):
        name = 'assets/nolan-kido-identity.jsonld'
        raw = (ROOT / name).read_text()
        records = {Path(name): raw, Path('unknown.jsonld'): raw,
                   Path('_source/person-schema.jsonld'): (ROOT / '_source/person-schema.jsonld').read_text()}
        original = deepcopy(records)
        restored = history.outputs(records)
        self.assertNotIn(Path(name), restored)
        self.assertEqual(restored[Path('unknown.jsonld')], raw)
        self.assertIn(Path('_source/person-schema.jsonld'), restored)
        self.assertEqual(records, original)
        self.assertEqual(history.outputs(restored), restored)

    def test_source_view_only_omits_known_additions_and_named_test_tools(self):
        records = {name: (ROOT / name).read_bytes() for name in history.SOURCE_ADDITIONS}
        records.update({name: b'test-only tool' for name in history.TEST_UTILITIES})
        records['assets/unreviewed.png'] = b'unreviewed'
        records['_scripts/freeze_unreviewed.py'] = b'unreviewed tool'
        original = deepcopy(records)
        self.assertEqual(history.source_records(records), {
            'assets/unreviewed.png': b'unreviewed',
            '_scripts/freeze_unreviewed.py': b'unreviewed tool',
        })
        self.assertEqual(records, original)
        self.assertEqual(history.TEST_UTILITIES, {
            '_scripts/freeze_brand_positioning_delta.py',
            '_scripts/freeze_scoped_share_change.py',
        })

    def test_mutated_new_files_remain_visible_in_every_inventory(self):
        for name in history.SOURCE_ADDITIONS:
            raw = (ROOT / name).read_bytes() + b'UNREVIEWED'
            with self.subTest(name=name):
                self.assertEqual(history.source_records({name: raw}), {name: raw})
                self.assertEqual(history.outputs({name: raw}), {name: raw})
                with patch.object(Path, 'read_bytes', return_value=raw):
                    self.assertEqual(history.files([name]), [name])

    def test_files_preserve_unknown_paths_and_collection_types(self):
        known = 'assets/nolan-kido-identity.jsonld'
        for values in ([known, 'unreviewed.txt'], {known, 'unreviewed.txt'},
                       (ROOT / known, ROOT / 'unreviewed.txt')):
            with self.subTest(kind=type(values).__name__):
                result = history.files(values)
                self.assertIsInstance(result, type(values))
                self.assertEqual(len(result), 1)
                self.assertEqual(history.key(next(iter(result))), 'unreviewed.txt')

    def test_oldest_common_inventory_chain_preserves_mutated_additions(self):
        import beginner_history
        name = 'assets/nolan-kido-identity.jsonld'
        raw = (ROOT / name).read_text()
        self.assertEqual(beginner_history.outputs({Path(name): raw}), {})
        changed = raw + 'UNREVIEWED'
        self.assertEqual(beginner_history.outputs({Path(name): changed}), {Path(name): changed})
        with patch.object(Path, 'read_bytes', return_value=changed.encode()):
            self.assertEqual(beginner_history.files({name}), {name})

    def test_brand_and_identity_reversal_reach_the_latest_old_history_chain(self):
        import regional_link_history
        import brand_positioning_history
        raw = (ROOT / 'index.html').read_text()
        self.assertEqual(regional_link_history.before('index.html', raw),
                         brand_positioning_history.before('index.html', raw))
        build = (ROOT / history.IDENTITY_BUILD).read_bytes()
        self.assertEqual(regional_link_history.before(history.IDENTITY_BUILD, build),
                         history.before(history.IDENTITY_BUILD, build))
        for changed in (raw + 'UNREVIEWED', 'UNREVIEWED' + raw):
            self.assertEqual(regional_link_history.before('index.html', changed), changed)

    def test_current_live_targets_include_the_separately_checked_new_card(self):
        import check_live
        current = subsequent_changes.live_targets(check_live.targets())
        route = '/assets/social/nolan-kido-ai.png'
        self.assertEqual(len(current), 476)
        self.assertEqual(current[route], (200, (ROOT / route.lstrip('/')).read_bytes()))
        previous = history.live_targets(current)
        self.assertEqual(len(previous), 475)
        self.assertEqual(set(current) - set(previous), {route})
        self.assertIn(route, current)

    def test_live_target_view_does_not_hide_wrong_status_bytes_types_or_routes(self):
        route = '/assets/social/nolan-kido-ai.png'
        raw = (ROOT / route.lstrip('/')).read_bytes()
        for response in ((404, raw), (200, raw + b'UNREVIEWED'), (200, ''),
                         [200, raw], (200, raw, 'extra')):
            records = {route: response}
            self.assertEqual(history.live_targets(records), records)
        unknown = {'/assets/unreviewed.png': (200, raw)}
        self.assertEqual(history.live_targets(unknown), unknown)


if __name__ == '__main__':
    unittest.main()
