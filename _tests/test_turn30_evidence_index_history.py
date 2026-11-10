"""Turn 30 evidence-index history is pinned to its reviewed Git release."""

from pathlib import Path
import subprocess
import unittest

from reviewed_release import read as reviewed_bytes
import turn27_profile_history as turn27
import turn29_source_notes_history as turn29
import turn30_evidence_index_history as history
import turn31_episode_ledger_history as turn31


# Later approved content, navigation, and metadata revisions changed the
# current files. Their bytes must not be treated as Turn 30 successors.
RELEASE = "0906e6ae2d51b062dd6d3bf34b86d6be6e432657"
RELEASE_TREE = "905851ef0b5a394c7dd65aeba1e518771c737e30"
PARENT_TREE = "a88806d384ee754d06a25fb062d63ce0694dbbb8"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT
    ).decode("ascii").strip()


class EvidenceIndexHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {path: reviewed_bytes(RELEASE, path, pair[1])
                        for path, pair in history.BLOBS.items()}
        cls.parents = {path: reviewed_bytes(history.PARENT, path, pair[0])
                       for path, pair in history.BLOBS.items()}
        cls.current = {path: (history.ROOT / path).read_bytes()
                       for path in history.BLOBS}

    def test_original_evidence_index_release_has_exact_git_provenance(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(set(history.BLOBS), {
            "_source/start-here.html", "start-here/index.html",
            "_source/about.html", "about/index.html",
            "_source/pages.json", "sitemap.xml",
        })
        self.assertEqual(set(self.released), set(history.BLOBS))
        for path, (older, newer) in history.BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.parents[path]), older)
                self.assertEqual(history.blob(self.released[path]), newer)

    def test_exact_original_successors_restore_only_their_parent(self):
        for path, (older, newer) in history.BLOBS.items():
            with self.subTest(path=path):
                released = self.released[path]
                self.assertEqual(history.blob(turn31.before(path, released)), newer)
                previous = history.before(path, released)
                self.assertEqual(history.blob(previous), older)
                self.assertEqual(previous, self.parents[path])
                self.assertEqual(history.before(path, previous), previous)
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, released), previous)
                text = history.before(path, released.decode("utf-8"))
                self.assertIsInstance(text, str)
                self.assertEqual(text, previous.decode("utf-8"))

    def test_registry_and_sitemap_rewind_in_original_release_order(self):
        for path in ("_source/pages.json", "sitemap.xml"):
            with self.subTest(path=path):
                before_29 = reviewed_bytes(turn29.PARENT, path,
                                           turn29.BLOBS[path][0])
                before_27 = reviewed_bytes(turn27.PARENT, path,
                                           turn27.BLOBS[path][0])
                released = self.released[path]
                self.assertEqual(history.before(path, released), self.parents[path])
                self.assertEqual(turn29.before(path, released), before_29)
                self.assertEqual(turn27.before(path, released), before_27)

    def test_unknown_mutations_and_later_edits_remain_visible(self):
        for revision, records in (("release", self.released),
                                  ("today", self.current)):
            for path, raw in records.items():
                for changed in (raw + b"UNREVIEWED", b"UNREVIEWED" + raw,
                                raw[1:], b"\xff\x00"):
                    with self.subTest(revision=revision, path=path,
                                      mutation=history.blob(changed)):
                        self.assertEqual(history.before(path, changed), changed)
                changed_text = raw.decode("utf-8") + "UNREVIEWED"
                self.assertEqual(history.before(path, changed_text), changed_text)
                self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("unknown.bin", b"\xff\x00"), b"\xff\x00")

    def test_only_the_exact_start_here_page_record_is_rewound(self):
        old = dict(history.OLD_PAGE)
        updated = dict(old, updated="2026-11-04")
        self.assertEqual(history.pages([updated]), [old])
        self.assertEqual(history.pages([old]), [old])
        changed = dict(updated, description="UNREVIEWED description")
        self.assertEqual(history.pages([changed]), [changed])
        unrelated = {"id": "not-start-here", "updated": "2026-11-04"}
        self.assertEqual(history.pages([unrelated]), [unrelated])


if __name__ == "__main__":
    unittest.main()
