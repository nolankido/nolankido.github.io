"""A release repair must not make unknown changes disappear from old checks."""
from pathlib import Path
import subprocess
import unittest

import turn34_release_integrity_history as history


class ReleaseHistoryTests(unittest.TestCase):
    def test_known_files_restore_the_independent_git_parent(self):
        for path, (previous_sha, current_sha) in history.records()["files"].items():
            with self.subTest(path=path):
                current = (history.ROOT / path).read_bytes()
                self.assertEqual(history.blob(current), current_sha)
                previous = subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT)
                self.assertEqual(history.blob(previous), previous_sha)
                self.assertEqual(history.before(path, current), previous)
                self.assertEqual(history.before(Path(path), current.decode("utf-8")),
                                 previous.decode("utf-8"))
                self.assertEqual(history.before(path, previous), previous)

    def test_unknown_changes_and_wrong_paths_remain_visible(self):
        for path in history.records()["files"]:
            current = (history.ROOT / path).read_bytes()
            for altered in (current + b"UNREVIEWED", current[1:], b"UNREVIEWED" + current):
                self.assertEqual(history.before(path, altered), altered)
            self.assertEqual(history.before("other/" + path, current), current)

    def test_only_exact_new_live_receipts_are_removed_from_historical_views(self):
        for route in history.records()["live_targets"]:
            current = (history.ROOT / route.lstrip("/")).read_bytes()
            self.assertEqual(history.live_targets({route: (200, current)}), {})
            for response in ((404, current), (200, current + b"UNREVIEWED"),
                             (200, current.decode("utf-8"))):
                self.assertEqual(history.live_targets({route: response}), {route: response})

    def test_corrected_metadata_rewinds_only_the_complete_reviewed_record(self):
        previous, current = history.records()["start_here"]
        self.assertEqual(current["updated"], "2026-11-04")
        self.assertEqual(previous["updated"], "2026-10-28")
        self.assertEqual(history.pages([current]), [previous])
        altered = dict(current, title="Unreviewed title")
        self.assertEqual(history.pages([altered]), [altered])


if __name__ == "__main__":
    unittest.main()
