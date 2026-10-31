"""Exact, test-only predecessor accounting for the stale-location cleanup."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_tests'))
import identity_turn03_history as history


class IdentityTurn03HistoryTests(unittest.TestCase):
    def test_only_the_two_reviewed_identity_files_restore_previous_bytes(self):
        self.assertEqual(set(history.REVISIONS), {
            '_source/person-schema.jsonld', 'assets/nolan-kido-identity.jsonld'})
        for name, (previous_sha, current_sha) in history.REVISIONS.items():
            with self.subTest(path=name):
                current = (ROOT / name).read_bytes()
                self.assertEqual(history.digest(current), current_sha)
                old = history.before(name, current)
                self.assertEqual(history.digest(old), previous_sha)
                self.assertIn(b'Honolulu', old)
                self.assertNotIn(b'"homeLocation"', current)
                self.assertEqual(history.before(name, old), old)
                self.assertEqual(history.before(ROOT / name, current.decode()), old.decode())

    def test_unreviewed_changes_and_wrong_paths_remain_visible(self):
        for name in history.REVISIONS:
            current = (ROOT / name).read_bytes()
            for changed in (b'UNREVIEWED' + current, current + b'UNREVIEWED', current[1:]):
                self.assertIs(history.before(name, changed), changed)
            self.assertIs(history.before('other/' + name, current), current)

    def test_corrupt_predecessor_digest_fails_closed(self):
        name = '_source/person-schema.jsonld'
        current = (ROOT / name).read_bytes()
        with patch.dict(history.REVISIONS, {name: ('0' * 64, history.digest(current))}):
            with self.assertRaisesRegex(ValueError, 'predecessor digest'):
                history.before(name, current)

    def test_older_output_capsules_receive_only_reviewed_predecessor_bytes(self):
        import visibility_discovery_history
        import living_well_case_links_history
        import visibility_sprint_history

        path = Path('assets/nolan-kido-identity.jsonld')
        current = (ROOT / path).read_bytes()
        old = history.before(path, current)
        for release in (visibility_discovery_history, living_well_case_links_history,
                        visibility_sprint_history):
            with self.subTest(release=release.__name__):
                self.assertEqual(release.outputs({path: current}), {path: old})
                self.assertEqual(release.outputs({path: old}), {path: old})
                unreviewed = current + b'UNREVIEWED'
                self.assertEqual(release.outputs({path: unreviewed}),
                                 {path: unreviewed})


if __name__ == '__main__':
    unittest.main()
