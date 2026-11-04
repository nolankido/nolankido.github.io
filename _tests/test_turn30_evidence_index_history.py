"""Turn 30: old source and public bytes, with no mutation laundering."""
from pathlib import Path
import subprocess
import unittest

import turn30_evidence_index_history as history
import turn31_episode_ledger_history as turn31


class EvidenceIndexHistoryTests(unittest.TestCase):
    def test_exact_six_successors_have_identical_parent_blobs(self):
        self.assertEqual(set(history.BLOBS), {
            "_source/start-here.html", "start-here/index.html",
            "_source/about.html", "about/index.html",
            "_source/pages.json", "sitemap.xml",
        })
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = (history.ROOT / path).read_bytes()
                self.assertEqual(history.blob(turn31.before(path, current)), new_sha)
                original = history.before(path, current)
                self.assertEqual(history.blob(original), old_sha)
                self.assertEqual(original, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT
                ))
                self.assertEqual(history.before(Path(path), current.decode("utf-8")),
                                 original.decode("utf-8"))
                self.assertEqual(history.before(path, original), original)

    def test_unrecognized_edits_do_not_become_old_releases(self):
        for path in history.BLOBS:
            raw = (history.ROOT / path).read_bytes()
            for changed in (raw + b"EXTRA", b"EXTRA" + raw, raw[1:]):
                self.assertEqual(history.before(path, changed), changed)
            self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("unknown.bin", b"\xff\x00"), b"\xff\x00")

    def test_only_the_exact_start_here_page_record_is_rewound(self):
        old = dict(history.OLD_PAGE)
        updated = dict(old, updated="2026-11-04")
        self.assertEqual(history.pages([updated]), [old])
        self.assertEqual(history.pages([old]), [old])
        changed = dict(updated, description="UNREVIEWED description")
        self.assertEqual(history.pages([changed]), [changed])
        self.assertEqual(history.pages([{"id": "not-start-here", "updated": "2026-11-04"}]),
                         [{"id": "not-start-here", "updated": "2026-11-04"}])


if __name__ == "__main__":
    unittest.main()
