"""Turn 32 history checks its original release, not newer Poker edits."""
from pathlib import Path
import subprocess
import unittest

from reviewed_release import read as reviewed_bytes
import turn27_profile_history as turn27
import turn29_source_notes_history as turn29
import turn30_evidence_index_history as turn30
import turn31_episode_ledger_history as turn31
import turn32_standoff_source_history as history
import turn33_standoff_companion_history as turn33


RELEASE = "04a452d5806799778d7ae040549ffceec78871af"
RELEASE_TREE = "679390ecd3328eecb5b868a237bfcc310f50232a"
PARENT_TREE = "2c8d6a884220d663ab3d383698c27d3c3a84ad62"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT
    ).decode("ascii").strip()


class StandOffSourceHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {path: reviewed_bytes(RELEASE, path, pair[1])
                        for path, pair in history.BLOBS.items()}
        cls.parents = {path: reviewed_bytes(history.PARENT, path, pair[0])
                       for path, pair in history.BLOBS.items()}
        cls.current = {path: (history.ROOT / path).read_bytes()
                       for path in history.BLOBS}
        cls.added = {path: reviewed_bytes(RELEASE, path, blob)
                     for path, blob in history.ADDED.items()}

    def test_original_standoff_release_has_exact_git_provenance(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(set(history.BLOBS), {
            "_source/poker/home.html", "poker/index.html",
            "_source/pages.json", "sitemap.xml", "_scripts/check_live.py",
        })
        self.assertEqual(set(self.released), set(history.BLOBS))
        for path, (before_sha, after_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.parents[path]), before_sha)
                self.assertEqual(history.blob(self.released[path]), after_sha)

    def test_only_complete_original_successors_restore_the_parent(self):
        for path, (before_sha, after_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                released = self.released[path]
                self.assertEqual(turn33.before(path, released), released)
                earlier = history.before(path, released)
                self.assertEqual(history.blob(earlier), before_sha)
                self.assertEqual(earlier, self.parents[path])
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, released), earlier)
                text = history.before(path, released.decode("utf-8"))
                self.assertIsInstance(text, str)
                self.assertEqual(text, earlier.decode("utf-8"))
                self.assertEqual(history.before(path, earlier), earlier)

    def test_registry_and_sitemap_rewind_in_original_release_order(self):
        for path in ("_source/pages.json", "sitemap.xml"):
            with self.subTest(path=path):
                released = self.released[path]
                before_30 = reviewed_bytes(turn30.PARENT, path,
                                           turn30.BLOBS[path][0])
                before_29 = reviewed_bytes(turn29.PARENT, path,
                                           turn29.BLOBS[path][0])
                before_27 = reviewed_bytes(turn27.PARENT, path,
                                           turn27.BLOBS[path][0])
                self.assertEqual(history.before(path, released), self.parents[path])
                if path == "sitemap.xml":
                    before_31 = reviewed_bytes(turn31.PARENT, path,
                                               turn31.BLOBS[path][0])
                    self.assertEqual(turn31.before(path, released), before_31)
                self.assertEqual(turn30.before(path, released), before_30)
                self.assertEqual(turn29.before(path, released), before_29)
                self.assertEqual(turn27.before(path, released), before_27)

    def test_mutations_and_later_edits_remain_visible(self):
        for revision, records in (("release", self.released),
                                  ("today", self.current)):
            for path, data in records.items():
                for modified in (data + b"OTHER", b"OTHER" + data,
                                 data[1:], b"\xff\x00"):
                    with self.subTest(revision=revision, path=path,
                                      mutation=history.blob(modified)):
                        self.assertEqual(history.before(path, modified), modified)
                changed_text = data.decode("utf-8") + "OTHER"
                self.assertEqual(history.before(path, changed_text), changed_text)
                self.assertEqual(history.before("other/" + path, data), data)
        self.assertEqual(history.before("binary.bin", b"\xff\x00"), b"\xff\x00")

    def test_two_original_public_downloads_are_sha_pinned(self):
        self.assertEqual(set(history.ADDED), {
            "downloads/portland-meadows-standoff-ak-source-ledger.json",
            "downloads/portland-meadows-standoff-ak-gate.py",
        })
        for path, expected in history.ADDED.items():
            with self.subTest(path=path):
                data = self.added[path]
                self.assertEqual(history.blob(data), expected)
                self.assertTrue(history.is_added_file(path, data))
                self.assertFalse(history.is_added_file(path, data + b"unreviewed"))
                self.assertFalse(history.is_added_file("not/" + path, data))
                absent = subprocess.run(
                    ["git", "cat-file", "-e", history.PARENT + ":" + path],
                    cwd=history.ROOT, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, check=False
                )
                self.assertNotEqual(absent.returncode, 0)
                today = (history.ROOT / path).read_bytes()
                self.assertEqual(history.is_added_file(path, today),
                                 history.blob(today) == expected)

    def test_manifest_predecessor_is_only_the_exact_poker_record(self):
        old = dict(history.OLD_POKER)
        current = dict(old, updated="2026-11-04")
        self.assertEqual(history.pages([current]), [old])
        self.assertEqual(history.pages([old]), [old])
        mutated = dict(current, description="unreviewed copy")
        self.assertEqual(history.pages([mutated]), [mutated])


if __name__ == "__main__":
    unittest.main()
