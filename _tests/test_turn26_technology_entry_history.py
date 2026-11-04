"""Turn 26 historical comparison only rewinds the exact published entrance."""
from pathlib import Path
import subprocess
import unittest

import turn26_technology_entry_history as history


class TechnologyFirstScreenHistoryTests(unittest.TestCase):
    def test_exact_successor_and_git_predecessor_for_three_files(self):
        self.assertEqual(set(history.BLOBS), {
            "_source/technology/home.html",
            "technology/index.html",
            "find/index.html",
        })
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = (history.ROOT / path).read_bytes()
                self.assertEqual(history.blob(current), new_sha)
                earlier = history.before(path, current)
                self.assertEqual(history.blob(earlier), old_sha)
                self.assertEqual(earlier, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT
                ))
                self.assertEqual(history.before(Path(path), current.decode("utf-8")),
                                 earlier.decode("utf-8"))
                self.assertEqual(history.before(path, earlier), earlier)

    def test_mutated_successors_and_unrelated_files_do_not_appear_historical(self):
        for path in history.BLOBS:
            current = (history.ROOT / path).read_bytes()
            for changed in (current + b"UNKNOWN", b"UNKNOWN" + current, current[1:]):
                self.assertEqual(history.before(path, changed), changed)
            self.assertEqual(history.before("other/" + path, current), current)
        self.assertEqual(history.before("other.bin", b"\xff\x00"), b"\xff\x00")


if __name__ == "__main__":
    unittest.main()
