"""Turn 34 release-integrity history uses its exact reviewed Git release."""
from pathlib import Path
import subprocess
import unittest

from reviewed_release import read as reviewed_bytes
import turn31_episode_ledger_history as turn31
import turn32_standoff_source_history as turn32
import turn33_standoff_companion_history as turn33
import turn34_release_integrity_history as history
import turn35_cross_interest_history as newer


RELEASE = "bed0fba458d50c08a2ff5e8679e6d9541a760e74"
RELEASE_TREE = "ad21ba34c92f2bd0b15305147692252b3649c472"
PARENT_TREE = "7249571e01e0c3d293eb06b068af461f2ef8ce9d"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT
    ).decode("ascii").strip()


class ReleaseHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ledger = history.records()
        cls.released = {path: reviewed_bytes(RELEASE, path, pair[1])
                        for path, pair in ledger["files"].items()}
        cls.parents = {path: reviewed_bytes(history.PARENT, path, pair[0])
                       for path, pair in ledger["files"].items()}
        cls.today = {path: (history.ROOT / path).read_bytes()
                     for path in ledger["files"]}
        cls.added = {path: reviewed_bytes(RELEASE, path, sha)
                     for path, sha in ledger["added"].items()}

    def test_original_release_has_exact_git_provenance(self):
        self.assertEqual(history.records()["parent"], history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(len(history.records()["files"]), 19)
        self.assertEqual(set(self.released), set(history.records()["files"]))
        for path, (old_sha, release_sha) in history.records()["files"].items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.parents[path]), old_sha)
                self.assertEqual(history.blob(self.released[path]), release_sha)

    def test_only_exact_original_successors_restore_the_parent(self):
        for path, (previous_sha, release_sha) in history.records()["files"].items():
            with self.subTest(path=path):
                released = self.released[path]
                self.assertEqual(newer.before(path, released), released)
                previous = history.before(path, released)
                self.assertEqual(history.blob(previous), previous_sha)
                self.assertEqual(previous, self.parents[path])
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, released), previous)
                as_text = history.before(path, released.decode("utf-8"))
                self.assertIsInstance(as_text, str)
                self.assertEqual(as_text, previous.decode("utf-8"))
                self.assertEqual(history.before(path, previous), previous)

    def test_live_checker_and_episode_history_rewind_in_release_order(self):
        path = "_scripts/check_live.py"
        released = self.released[path]
        self.assertEqual(history.before(path, released), self.parents[path])
        for earlier in (turn33, turn32, turn31):
            with self.subTest(release=earlier.__name__):
                old = reviewed_bytes(earlier.PARENT, path,
                                     earlier.BLOBS[path][0])
                self.assertEqual(earlier.before(path, released), old)

        episode = "_source/poker/portland-meadows-ep1.html"
        self.assertEqual(history.before(episode, self.released[episode]),
                         self.parents[episode])
        first = reviewed_bytes(turn31.PARENT, episode,
                               turn31.BLOBS[episode][0])
        self.assertEqual(turn31.before(episode, self.released[episode]), first)

    def test_unknown_changes_and_later_edits_remain_visible(self):
        for revision, records in (("release", self.released),
                                  ("today", self.today)):
            for path, raw in records.items():
                for altered in (raw + b"UNREVIEWED", raw[1:],
                                b"UNREVIEWED" + raw, b"\xff\x00"):
                    with self.subTest(revision=revision, path=path,
                                      mutation=history.blob(altered)):
                        self.assertEqual(history.before(path, altered), altered)
                changed_text = raw.decode("utf-8") + "UNREVIEWED"
                self.assertEqual(history.before(path, changed_text), changed_text)
                self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("unknown.bin", b"\xff\x00"), b"\xff\x00")

    def test_only_exact_original_live_receipts_are_removed_from_history(self):
        for route, expected in history.records()["live_targets"].items():
            with self.subTest(route=route):
                original = reviewed_bytes(RELEASE, route.lstrip("/"), expected)
                self.assertEqual(history.blob(original), expected)
                self.assertEqual(history.live_targets({route: (200, original)}), {})
                self.assertEqual(history.live_targets({"else" + route: (200, original)}),
                                 {"else" + route: (200, original)})
                for response in ((404, original), (200, original + b"UNREVIEWED"),
                                 (200, original.decode("utf-8"))):
                    self.assertEqual(history.live_targets({route: response}),
                                     {route: response})

    def test_two_original_new_tests_require_exact_reviewed_blobs(self):
        self.assertEqual(set(self.added), {
            "_tests/test_turn34_release_integrity.py",
            "_tests/test_turn34_release_history.py",
        })
        for path, expected in history.records()["added"].items():
            with self.subTest(path=path):
                released = self.added[path]
                self.assertEqual(history.blob(released), expected)
                self.assertTrue(history.is_added_file(path, released))
                self.assertFalse(history.is_added_file(path, released + b"UNREVIEWED"))
                self.assertFalse(history.is_added_file("else/" + path, released))
                absent = subprocess.run(
                    ["git", "cat-file", "-e", history.PARENT + ":" + path],
                    cwd=history.ROOT, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, check=False
                )
                self.assertNotEqual(absent.returncode, 0)

    def test_corrected_metadata_rewinds_only_the_complete_reviewed_record(self):
        previous, current = history.records()["start_here"]
        self.assertEqual(current["updated"], "2026-11-04")
        self.assertEqual(previous["updated"], "2026-10-28")
        self.assertEqual(history.pages([current]), [previous])
        self.assertEqual(history.pages([previous]), [previous])
        altered = dict(current, title="Unreviewed title")
        self.assertEqual(history.pages([altered]), [altered])


if __name__ == "__main__":
    unittest.main()
