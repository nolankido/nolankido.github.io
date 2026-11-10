"""Turn 33 history is pinned to its original reviewed companion release."""
from pathlib import Path
import subprocess
import unittest
from xml.etree import ElementTree as ET

from reviewed_release import read as reviewed_bytes
import turn27_profile_history as turn27
import turn29_source_notes_history as turn29
import turn30_evidence_index_history as turn30
import turn31_episode_ledger_history as turn31
import turn32_standoff_source_history as turn32
import turn33_standoff_companion_history as history
import turn34_release_integrity_history as turn34


RELEASE = "80170a3909e2a70fcbbb34ea667953b2af77e45f"
RELEASE_TREE = "7249571e01e0c3d293eb06b068af461f2ef8ce9d"
PARENT_TREE = "679390ecd3328eecb5b868a237bfcc310f50232a"
STANDOFF = "https://nolankido.com/poker/episodes/portland-meadows-standoff/"
EPISODE_ONE = "https://nolankido.com/poker/episodes/portland-meadows-ep1/"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT
    ).decode("ascii").strip()


class StandOffCompanionHistoryTests(unittest.TestCase):
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

    def test_original_standoff_companion_has_exact_git_provenance(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertGreaterEqual(len(history.BLOBS), 18)
        self.assertEqual(set(self.released), set(history.BLOBS))
        for path, (old_sha, release_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.parents[path]), old_sha)
                self.assertEqual(history.blob(self.released[path]), release_sha)

    def test_only_exact_original_successors_restore_the_parent(self):
        for path, (old_sha, release_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                released = self.released[path]
                self.assertEqual(turn34.before(path, released), released)
                previous = history.before(path, released)
                self.assertEqual(history.blob(previous), old_sha)
                self.assertEqual(previous, self.parents[path])
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, released), previous)
                text = history.before(path, released.decode("utf-8"))
                self.assertIsInstance(text, str)
                self.assertEqual(text, previous.decode("utf-8"))
                self.assertEqual(history.before(path, previous), previous)

    def test_sitemap_and_live_checker_rewind_through_original_releases(self):
        for path in ("_scripts/check_live.py", "sitemap.xml"):
            with self.subTest(path=path):
                released = self.released[path]
                before_32 = reviewed_bytes(turn32.PARENT, path,
                                           turn32.BLOBS[path][0])
                self.assertEqual(history.before(path, released), self.parents[path])
                self.assertEqual(turn32.before(path, released), before_32)
                if path == "sitemap.xml":
                    before_31 = reviewed_bytes(turn31.PARENT, path,
                                               turn31.BLOBS[path][0])
                    before_30 = reviewed_bytes(turn30.PARENT, path,
                                               turn30.BLOBS[path][0])
                    before_29 = reviewed_bytes(turn29.PARENT, path,
                                               turn29.BLOBS[path][0])
                    before_27 = reviewed_bytes(turn27.PARENT, path,
                                               turn27.BLOBS[path][0])
                    self.assertEqual(turn31.before(path, released), before_31)
                    self.assertEqual(turn30.before(path, released), before_30)
                    self.assertEqual(turn29.before(path, released), before_29)
                    self.assertEqual(turn27.before(path, released), before_27)

    def test_original_sitemap_and_feeds_registered_one_new_companion(self):
        name = "sitemap.xml"
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

        def urls(xml):
            links = [node.findtext(ns + "loc") for node in ET.fromstring(xml)]
            self.assertEqual(len(links), len(set(links)))
            return links

        previous = urls(self.parents[name])
        released = urls(self.released[name])
        today = urls((history.ROOT / name).read_bytes())
        self.assertNotIn(STANDOFF, previous)
        self.assertEqual(released.count(STANDOFF), 1)
        self.assertEqual(set(released) - set(previous), {STANDOFF})
        self.assertEqual(today.count(STANDOFF), 1)

        for name in ("poker/feed.xml", "writing.xml"):
            with self.subTest(feed=name):
                def items(raw):
                    root = ET.fromstring(raw)
                    nodes = root.findall("./channel/item")
                    links = [node.findtext("link") for node in nodes]
                    self.assertEqual(len(links), len(set(links)))
                    return {node.findtext("link"): node for node in nodes}

                old = items(self.parents[name])
                new = items(self.released[name])
                current = items((history.ROOT / name).read_bytes())
                self.assertNotIn(STANDOFF, old)
                self.assertEqual(set(new) - set(old), {STANDOFF})
                self.assertEqual(new[STANDOFF].findtext("pubDate"),
                                 "Wed, 04 Nov 2026 00:00:00 GMT")
                self.assertEqual(new[EPISODE_ONE].findtext("pubDate"),
                                 old[EPISODE_ONE].findtext("pubDate"))
                self.assertIn(STANDOFF, current)

    def test_unknown_mutations_and_later_edits_are_not_masked(self):
        for revision, records in (("release", self.released),
                                  ("today", self.current)):
            for path, raw in records.items():
                for changed in (raw + b"EXTRA", b"EXTRA" + raw,
                                raw[1:], b"\xff\x00"):
                    with self.subTest(revision=revision, path=path,
                                      mutation=history.blob(changed)):
                        self.assertEqual(history.before(path, changed), changed)
                changed_text = raw.decode("utf-8") + "EXTRA"
                self.assertEqual(history.before(path, changed_text), changed_text)
                self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("unknown.bin", b"\xff\x00"), b"\xff\x00")

    def test_only_exact_original_new_public_files_are_recognized(self):
        required = {
            "_source/poker/portland-meadows-standoff.html",
            "poker/episodes/portland-meadows-standoff/index.html",
            "_scripts/build_standoff_episode.py",
            "_scripts/poker_standoff_episode.py",
        }
        self.assertTrue(required <= set(history.ADDED))
        for path, expected in history.ADDED.items():
            with self.subTest(path=path):
                released = self.added[path]
                self.assertEqual(history.blob(released), expected)
                self.assertTrue(history.is_added_file(path, released))
                self.assertFalse(history.is_added_file(path, released + b"unreviewed"))
                self.assertFalse(history.is_added_file("other/" + path, released))
                absent = subprocess.run(
                    ["git", "cat-file", "-e", history.PARENT + ":" + path],
                    cwd=history.ROOT, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, check=False
                )
                self.assertNotEqual(absent.returncode, 0)
                # Later approved adapters can recognize changed test files.
                # Turn 33's contract is the exact original addition only.


if __name__ == "__main__":
    unittest.main()
