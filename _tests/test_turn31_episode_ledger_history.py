"""Turn 31 exact older poker companion and manual release snapshots."""
from pathlib import Path
import subprocess
import unittest
import turn31_episode_ledger_history as history
import turn32_standoff_source_history as turn32


class EpisodeLedgerHistoryTests(unittest.TestCase):
    def test_approved_successor_bytes_restore_actual_parent(self):
        expected = {
            "_source/poker/portland-meadows-ep1.html",
            "poker/episodes/portland-meadows-ep1/index.html",
            "_scripts/build_poker_episode.py",
            "_scripts/poker_episode.py",
            "_scripts/player_sitemap.py",
            "_scripts/check_live.py",
            "sitemap.xml",
        }
        self.assertEqual(set(history.BLOBS), expected)
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = (history.ROOT / path).read_bytes()
                self.assertEqual(history.blob(turn32.before(path, current)), new_sha)
                original = history.before(path, current)
                self.assertEqual(history.blob(original), old_sha)
                self.assertEqual(original, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT
                ))
                self.assertEqual(history.before(Path(path), current.decode("utf-8")),
                                 original.decode("utf-8"))
                self.assertEqual(history.before(path, original), original)

    def test_mutated_outputs_are_never_misidentified_as_old_release(self):
        for path in history.BLOBS:
            data = (history.ROOT / path).read_bytes()
            for mutant in (data + b"UNKNOWN", b"UNKNOWN" + data, data[1:]):
                self.assertEqual(history.before(path, mutant), mutant)
            self.assertEqual(history.before("other/" + path, data), data)
        self.assertEqual(history.before("binary.bin", b"\xff\x00"), b"\xff\x00")

    def test_one_bounded_new_download_and_no_filename_only_exemption(self):
        name = "downloads/portland-meadows-ep1-scene-claims.json"
        current = (history.ROOT / name).read_bytes()
        self.assertEqual(set(history.ADDED), {name})
        self.assertTrue(history.is_added_file(name, current))
        self.assertFalse(history.is_added_file(name, current + b"UNREVIEWED"))
        self.assertFalse(history.is_added_file("private/" + name, current))


if __name__ == "__main__":
    unittest.main()
