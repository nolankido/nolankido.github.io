"""Turn 27 predecessor checks: exact reviewed blobs, unchanged unknown edits."""
from pathlib import Path
import subprocess
import unittest

import turn27_profile_history as history
import turn29_source_notes_history as turn29


class ProfileKitHistoryTests(unittest.TestCase):
    def test_only_known_files_restore_prior_reviewed_blob(self):
        self.assertEqual(set(history.BLOBS), {
            "_source/bio.html", "bio/index.html", "_source/pages.json", "sitemap.xml"
        })
        for path, (older, newer) in history.BLOBS.items():
            with self.subTest(path=path):
                raw = (history.ROOT / path).read_bytes()
                self.assertEqual(history.blob(turn29.before(path, raw)), newer)
                previous = history.before(path, raw)
                self.assertEqual(history.blob(previous), older)
                self.assertEqual(previous, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT
                ))
                self.assertEqual(history.before(Path(path), raw.decode("utf-8")),
                                 previous.decode("utf-8"))
                self.assertEqual(history.before(path, previous), previous)

    def test_unknown_mutations_and_wrong_paths_remain_visible(self):
        for path in history.BLOBS:
            raw = (history.ROOT / path).read_bytes()
            for changed in (raw + b"UNREVIEWED", b"UNREVIEWED" + raw, raw[1:]):
                self.assertEqual(history.before(path, changed), changed)
            self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("unknown.bin", b"\xff\x00"), b"\xff\x00")

    def test_profile_kit_is_only_excluded_with_its_exact_new_bytes(self):
        name = "downloads/nolan-kido-public-profile-kit.md"
        raw = (history.ROOT / name).read_bytes()
        self.assertEqual(set(history.ADDED), {name})
        self.assertTrue(history.is_added_file(name, raw))
        self.assertFalse(history.is_added_file(name, raw + b"EXTRA"))
        self.assertFalse(history.is_added_file("other/" + name, raw))

    def test_only_complete_bio_record_reverts_to_previous_date(self):
        before = dict(history.OLD_BIO)
        after = dict(before, updated="2026-11-04")
        self.assertEqual(history.pages([after]), [before])
        self.assertEqual(history.pages([before]), [before])
        changed = {**after, "description": "UNREVIEWED"}
        self.assertEqual(history.pages([changed]), [changed])
        self.assertEqual(history.pages([{"id": "other", "updated": "2026-11-04"}]),
                         [{"id": "other", "updated": "2026-11-04"}])


if __name__ == "__main__":
    unittest.main()
