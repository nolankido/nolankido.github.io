"""Turn 32 only rewinds exact reviewed complete Git blobs and downloads."""
from pathlib import Path
import subprocess
import unittest

import turn32_standoff_source_history as history


class StandOffSourceHistoryTests(unittest.TestCase):
    def test_predecessor_blobs_are_exact(self):
        self.assertEqual(set(history.BLOBS), {
            "_source/poker/home.html", "poker/index.html",
            "_source/pages.json", "sitemap.xml", "_scripts/check_live.py",
        })
        for path, (before_sha, after_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                data = (history.ROOT / path).read_bytes()
                self.assertEqual(history.blob(data), after_sha)
                earlier = history.before(path, data)
                self.assertEqual(history.blob(earlier), before_sha)
                self.assertEqual(earlier, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT
                ))
                self.assertEqual(history.before(Path(path), data.decode("utf-8")),
                                 earlier.decode("utf-8"))
                self.assertEqual(history.before(path, earlier), earlier)

    def test_mutations_and_unknown_files_remain_visible(self):
        for path in history.BLOBS:
            data = (history.ROOT / path).read_bytes()
            for modified in (data + b"OTHER", b"OTHER" + data, data[1:]):
                self.assertEqual(history.before(path, modified), modified)
            self.assertEqual(history.before("other/" + path, data), data)
        self.assertEqual(history.before("binary.bin", b"\xff\x00"), b"\xff\x00")

    def test_two_public_downloads_are_sha_pinned(self):
        self.assertEqual(set(history.ADDED), {
            "downloads/portland-meadows-standoff-ak-source-ledger.json",
            "downloads/portland-meadows-standoff-ak-gate.py",
        })
        for path in history.ADDED:
            with self.subTest(path=path):
                data = (history.ROOT / path).read_bytes()
                self.assertTrue(history.is_added_file(path, data))
                self.assertFalse(history.is_added_file(path, data + b"unreviewed"))
                self.assertFalse(history.is_added_file("not/" + path, data))

    def test_manifest_predecessor_is_only_the_exact_poker_record(self):
        old = dict(history.OLD_POKER)
        current = dict(old, updated="2026-11-04")
        self.assertEqual(history.pages([current]), [old])
        self.assertEqual(history.pages([old]), [old])
        mutated = dict(current, description="unreviewed copy")
        self.assertEqual(history.pages([mutated]), [mutated])


if __name__ == "__main__":
    unittest.main()
