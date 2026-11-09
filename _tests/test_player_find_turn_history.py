"""Exact predecessor guard for the player Find enhancement."""
import subprocess
from tempfile import TemporaryDirectory
import unittest
from pathlib import Path
from unittest.mock import patch
import player_find_turn_history as history
from reviewed_release import read as reviewed_bytes


# Exact reviewed Player Find release, before later independent updates to
# the search index, builders, test files and repository instructions.
PLAYER_FIND_RELEASE = 'a86763f659ddcca81437f34ed78bca8644b631eb'
PLAYER_FIND_PARENT = '5e84640c336fcd470b9e77fa9a3a4ea7f753b944'
PARENT_TREE = '7e9eba0e197fcbf984cd2146961b14ef5aacb932'
RELEASE_BLOBS = {
    'AGENTS.md': '746fdf4ae5ac07c031a2c8a209a90751f2dccc4a',
    '_scripts/build.py': '384f466d218b879faa85854cdeb8c48441e14807',
    '_scripts/local_release_checks.py': 'f26de68056421d1fcf41917951ecb7685bd8b48c',
    '_scripts/player_find.py': '88b63dbd7a0738e14804c97ac82b87343bd6a871',
    '_scripts/site_find.py': '4386c79895d3368c84e903dc676c87bd401adfd2',
    '_source/find.html': 'dc0ecbf8b326125ded9643299e186080a0088a56',
    '_tests/test_player_find.py': 'cba1ab872af3bc6955719e4422be81169f4bfe3c',
    'find/index.html': '9dff44288065aa209061af8b80cc1c3a451224b5',
}


class PlayerFindHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {path: reviewed_bytes(PLAYER_FIND_RELEASE, path, sha)
                        for path, sha in RELEASE_BLOBS.items()}

    def test_original_release_has_its_git_parent_and_exact_added_files(self):
        self.assertEqual(set(RELEASE_BLOBS), set(history.BLOBS) | set(history.ADDED))
        self.assertEqual(subprocess.check_output(
            ['git', 'rev-parse', PLAYER_FIND_RELEASE + '^'], cwd=history.ROOT
        ).decode().strip(), PLAYER_FIND_PARENT)
        self.assertEqual(subprocess.check_output(
            ['git', 'rev-parse', PLAYER_FIND_PARENT + '^{tree}'], cwd=history.ROOT
        ).decode().strip(), PARENT_TREE)
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                predecessor = subprocess.check_output(
                    ['git', 'show', PLAYER_FIND_PARENT + ':' + path], cwd=history.ROOT)
                self.assertEqual(history.blob(predecessor), old_sha)
                self.assertEqual(history.blob(self.released[path]), new_sha)
                self.assertEqual(history.before(path, self.released[path]), predecessor)
        for path, sha in history.ADDED.items():
            with self.subTest(added=path):
                self.assertEqual(history.blob(self.released[path]), sha)
                self.assertEqual(subprocess.check_output(
                    ['git', 'ls-tree', PLAYER_FIND_PARENT, '--', path], cwd=history.ROOT), b'')

    def test_every_approved_file_restores_its_reviewed_git_predecessor(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = self.released[path]
                self.assertEqual(history.blob(current), new_sha)
                earlier = history.before(path, current)
                self.assertEqual(history.blob(earlier), old_sha)
                self.assertEqual(history.before(path, earlier), earlier)
                self.assertEqual(history.before(Path(path), current.decode('utf-8')),
                                 earlier.decode('utf-8'))

    def test_corruption_wrong_file_and_unknown_content_are_not_hidden(self):
        for path in history.BLOBS:
            current = self.released[path]
            for bad in (current + b'UNREVIEWED', b'UNREVIEWED' + current, current[1:]):
                self.assertEqual(history.before(path, bad), bad)
            self.assertEqual(history.before('other/' + path, current), current)
        self.assertEqual(history.before('unknown.bin', bytes([255, 0])), bytes([255, 0]))

    def test_only_exact_added_files_disappear_from_historical_source_view(self):
        for path, sha in history.ADDED.items():
            with self.subTest(path=path):
                current = self.released[path]
                self.assertEqual(history.blob(current), sha)
                self.assertEqual(history.source_records({path: current}), {})
                changed = current + b'UNREVIEWED'
                self.assertEqual(history.source_records({path: changed}), {path: changed})
                with TemporaryDirectory() as temp:
                    target = Path(temp) / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(current)
                    with patch.object(history, 'ROOT', Path(temp)):
                        self.assertEqual(history.files([path, 'other.txt']), ['other.txt'])
                        target.write_bytes(changed)
                        self.assertEqual(history.files([path, 'other.txt']),
                                         [path, 'other.txt'])


if __name__ == '__main__':
    unittest.main()
