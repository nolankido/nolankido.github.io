"""Turn 31 poker episode history uses its exact reviewed Git release."""

from pathlib import Path
import subprocess
import unittest

from reviewed_release import read as reviewed_bytes
import turn27_profile_history as turn27
import turn29_source_notes_history as turn29
import turn30_evidence_index_history as turn30
import turn31_episode_ledger_history as history
import turn32_standoff_source_history as turn32


# Later approved poker companion, sitemap and live-check changes cannot
# serve as immutable snapshots of the original Episode 1 ledger release.
RELEASE = "fab6e73fb93552831b39c9011dca813955224124"
RELEASE_TREE = "2c8d6a884220d663ab3d383698c27d3c3a84ad62"
PARENT_TREE = "905851ef0b5a394c7dd65aeba1e518771c737e30"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT
    ).decode("ascii").strip()


class EpisodeLedgerHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {path: reviewed_bytes(RELEASE, path, pair[1])
                        for path, pair in history.BLOBS.items()}
        cls.parents = {path: reviewed_bytes(history.PARENT, path, pair[0])
                       for path, pair in history.BLOBS.items()}
        cls.current = {path: (history.ROOT / path).read_bytes()
                       for path in history.BLOBS}
        cls.added = {path: reviewed_bytes(RELEASE, path, expected)
                     for path, expected in history.ADDED.items()}

    def test_original_episode_ledger_has_exact_git_provenance(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
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
        self.assertEqual(set(self.released), expected)
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.parents[path]), old_sha)
                self.assertEqual(history.blob(self.released[path]), new_sha)

    def test_only_exact_original_successors_restore_the_parent(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                released = self.released[path]
                self.assertEqual(history.blob(turn32.before(path, released)), new_sha)
                previous = history.before(path, released)
                self.assertEqual(history.blob(previous), old_sha)
                self.assertEqual(previous, self.parents[path])
                self.assertEqual(history.before(path, previous), previous)
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, released), previous)
                text = history.before(path, released.decode("utf-8"))
                self.assertIsInstance(text, str)
                self.assertEqual(text, previous.decode("utf-8"))

    def test_sitemap_history_rewinds_in_original_release_order(self):
        path = "sitemap.xml"
        released = self.released[path]
        before_30 = reviewed_bytes(turn30.PARENT, path, turn30.BLOBS[path][0])
        before_29 = reviewed_bytes(turn29.PARENT, path, turn29.BLOBS[path][0])
        before_27 = reviewed_bytes(turn27.PARENT, path, turn27.BLOBS[path][0])
        self.assertEqual(history.before(path, released), self.parents[path])
        self.assertEqual(turn30.before(path, released), before_30)
        self.assertEqual(turn29.before(path, released), before_29)
        self.assertEqual(turn27.before(path, released), before_27)

    def test_mutations_and_later_edits_are_not_disguised_as_history(self):
        for revision, records in (("release", self.released),
                                  ("today", self.current)):
            for path, raw in records.items():
                for mutant in (raw + b"UNKNOWN", b"UNKNOWN" + raw,
                               raw[1:], b"\xff\x00"):
                    with self.subTest(revision=revision, path=path,
                                      mutation=history.blob(mutant)):
                        self.assertEqual(history.before(path, mutant), mutant)
                changed_text = raw.decode("utf-8") + "UNKNOWN"
                self.assertEqual(history.before(path, changed_text), changed_text)
                self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("binary.bin", b"\xff\x00"), b"\xff\x00")

    def test_added_scene_claims_require_exact_original_public_blob(self):
        name = "downloads/portland-meadows-ep1-scene-claims.json"
        released = self.added[name]
        self.assertEqual(set(history.ADDED), {name})
        self.assertEqual(history.blob(released), history.ADDED[name])
        self.assertTrue(history.is_added_file(name, released))
        self.assertFalse(history.is_added_file(name, released + b"UNREVIEWED"))
        self.assertFalse(history.is_added_file("private/" + name, released))
        absent = subprocess.run(
            ["git", "cat-file", "-e", history.PARENT + ":" + name],
            cwd=history.ROOT, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, check=False
        )
        self.assertNotEqual(absent.returncode, 0)
        today = (history.ROOT / name).read_bytes()
        self.assertEqual(history.is_added_file(name, today),
                         history.blob(today) == history.ADDED[name])


if __name__ == "__main__":
    unittest.main()
