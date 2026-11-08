"""Verify Portland Meadows Episode 1 against its original public release."""
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import episode_turn06_history as history
from reviewed_release import read as reviewed_bytes


# This is the complete merged release, not an intermediate working commit.
EPISODE_RELEASE = "a8e920785b8bb6b8fd55fda53b0a3f58fb2e9954"
EPISODE_RELEASE_TREE = "d1e6137d5a0d45493debc032921d9513f1a6d62d"


class Turn06HistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.successors = {
            path: reviewed_bytes(EPISODE_RELEASE, path, current_sha)
            for path, (_, current_sha) in history.BLOBS.items()
        }
        cls.added = {
            path: reviewed_bytes(EPISODE_RELEASE, path, current_sha)
            for path, current_sha in history.ADDED.items()
        }

    def test_complete_release_and_direct_parent_are_the_recorded_git_objects(self):
        self.assertEqual(len(self.successors), 21)
        self.assertEqual(len(self.added), 5)
        self.assertFalse(set(self.successors) & set(self.added))
        self.assertEqual(
            subprocess.check_output(["git", "rev-parse", EPISODE_RELEASE + "^"],
                                    cwd=history.ROOT).decode().strip(),
            history.PARENT)
        self.assertEqual(
            subprocess.check_output(["git", "rev-parse", EPISODE_RELEASE + "^{tree}"],
                                    cwd=history.ROOT).decode().strip(),
            EPISODE_RELEASE_TREE)

    def test_all_reviewed_changes_restore_exact_published_parent(self):
        for path, (old_sha, current_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = self.successors[path]
                self.assertEqual(history.blob(current), current_sha)
                previous = history.before(path, current)
                self.assertEqual(history.blob(previous), old_sha)
                parent = subprocess.check_output(["git", "show", history.PARENT + ":" + path],
                                                 cwd=history.ROOT)
                self.assertEqual(previous, parent)
                self.assertEqual(history.before(path, previous), previous)

    def test_unknown_edits_never_collapse_into_older_release(self):
        for path, raw in self.successors.items():
            for altered in (raw + b"UNKNOWN", b"UNKNOWN" + raw, raw[1:]):
                with self.subTest(path=path, mutation=history.blob(altered)):
                    self.assertEqual(history.before(path, altered), altered)
            self.assertEqual(history.before("unreviewed/" + path, raw), raw)

    def test_new_public_sources_removed_only_from_old_inventories(self):
        for path, sha in history.ADDED.items():
            with self.subTest(path=path):
                current = self.added[path]
                self.assertEqual(history.blob(current), sha)
                self.assertEqual(history.source_records({path: current}), {})
                mutated = current + b"UNREVIEWED"
                self.assertEqual(history.source_records({path: mutated}), {path: mutated})

    def test_five_new_files_do_not_exist_in_the_original_parent(self):
        for path in sorted(self.added):
            with self.subTest(path=path):
                result = subprocess.run(
                    ["git", "cat-file", "-e", history.PARENT + ":" + path],
                    cwd=history.ROOT, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, check=False)
                self.assertNotEqual(result.returncode, 0)

    def test_old_file_inventory_uses_the_reviewed_release_files(self):
        # `history.files` explicitly checks bytes on disk. Materialize only the
        # five verified released files, never the current site versions.
        with TemporaryDirectory(prefix="episode-turn06-fixtures-") as folder:
            fixture_root = Path(folder)
            for path, current in self.added.items():
                target = fixture_root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(current)
            with patch.object(history, "ROOT", fixture_root):
                self.assertEqual(history.files([*self.added, "unreviewed.txt"]),
                                 ["unreviewed.txt"])
                self.assertEqual(history.files((*self.added, "unreviewed.txt")),
                                 ("unreviewed.txt",))
                for path, current in self.added.items():
                    target = fixture_root / path
                    target.write_bytes(current + b"UNREVIEWED")
                    try:
                        self.assertEqual(history.files([path, "unreviewed.txt"]),
                                         [path, "unreviewed.txt"])
                    finally:
                        target.write_bytes(current)

    def test_live_video_route_is_removed_only_when_public_bytes_are_exact(self):
        raw = self.added["poker/episodes/portland-meadows-ep1/index.html"]
        self.assertEqual(history.live_targets({history.EPISODE_ROUTE: (200, raw)}), {})
        for value in ((404, raw), (200, raw + b"UNKNOWN"), (200, "")):
            self.assertEqual(history.live_targets({history.EPISODE_ROUTE: value}),
                             {history.EPISODE_ROUTE: value})


if __name__ == "__main__":
    unittest.main()
