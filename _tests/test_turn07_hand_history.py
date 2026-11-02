"""Turn 7 preserves released historical bytes and rejects unreviewed changes."""
from pathlib import Path
import subprocess
import unittest

import turn07_hand_history as history
import turn08_laptop_history


class Turn07HandHistoryTests(unittest.TestCase):
    def test_every_scoped_changed_file_matches_its_parent_git_blob(self):
        for path, (before_sha, after_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                content = turn08_laptop_history.before(path, (history.ROOT / path).read_bytes())
                self.assertEqual(history.blob(content), after_sha)
                previous = history.before(path, content)
                self.assertEqual(history.blob(previous), before_sha)
                self.assertEqual(previous, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT))
                self.assertEqual(history.before(path, previous), previous)

    def test_unknown_edits_and_other_pathnames_survive(self):
        for path in history.BLOBS:
            raw = turn08_laptop_history.before(path, (history.ROOT / path).read_bytes())
            for changed in (raw + b"UNKNOWN", b"UNKNOWN" + raw, raw[1:]):
                self.assertEqual(history.before(path, changed), changed)
            self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("private.bin", bytes([255, 0])), bytes([255, 0]))

    def test_source_additions_only_disappear_when_exact(self):
        for path, digest in history.ADDED.items():
            with self.subTest(path=path):
                raw = turn08_laptop_history.before(path, (history.ROOT / path).read_bytes())
                self.assertEqual(history.blob(raw), digest)
                self.assertEqual(history.source_records({path: raw}), {})
                altered = raw + b"UNREVIEWED"
                self.assertEqual(history.source_records({path: altered}), {path: altered})
                self.assertEqual(history.files([path, "unrelated.txt"]), ["unrelated.txt"])

    def test_later_live_bytes_rewind_only_when_exact(self):
        for route, path in history.ROUTES.items():
            with self.subTest(route=route):
                raw = turn08_laptop_history.before(path, (history.ROOT / path).read_bytes())
                restored = history.live_targets({route: (200, raw)})
                self.assertEqual(restored[route], (200, history.before(path, raw)))
                for bad in ((200, raw + b"UNKNOWN"), (404, raw), (200, "")):
                    self.assertEqual(history.live_targets({route: bad}), {route: bad})


if __name__ == "__main__":
    unittest.main()
