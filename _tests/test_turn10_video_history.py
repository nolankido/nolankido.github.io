"""Turn 10 restores historical bytes only for the reviewed video-link repair."""
import subprocess
import unittest
import turn10_video_history as history
import turn31_episode_ledger_history as turn31


class Turn10VideoHistoryTests(unittest.TestCase):
    def test_exact_new_bytes_restore_predecessor(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                raw = (history.ROOT / path).read_bytes()
                self.assertEqual(history.blob(turn31.before(path, raw)), new_sha)
                previous = history.before(path, raw)
                self.assertEqual(history.blob(previous), old_sha)
                self.assertEqual(previous, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT))
                self.assertEqual(history.before(path, previous), previous)

    def test_mutations_and_unrelated_files_are_not_rewritten(self):
        for path in history.BLOBS:
            raw = (history.ROOT / path).read_bytes()
            for altered in (raw + b"unexpected", b"unexpected" + raw, raw[1:]):
                self.assertEqual(history.before(path, altered), altered)
            self.assertEqual(history.before("other/" + path, raw), raw)


if __name__ == "__main__":
    unittest.main()
