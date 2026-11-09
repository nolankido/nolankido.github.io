"""Test the exact Turn 5 profile-link release, not today's updated pages."""
from pathlib import Path
import subprocess
import unittest
import profile_links_turn05_history as h
from reviewed_release import read as reviewed_bytes


# This original player-profile publication predates many independent edits
# to About and Poker. The test-only reversal adapter is intentionally strict:
# it must receive the complete approved release blob, never modern page bytes.
PROFILE_LINKS_RELEASE = "9dca4e95343abe3355f84f3903185e1bd68a80dc"
PROFILE_LINKS_PARENT = "0d42e340a384e2174291348b9adf13f44e33008e"
RELEASE_TREE = "7c56318078601239790b559e9eedc983f8c49001"
PARENT_TREE = "6f2083fdf0be4e9cbb05ded3b4a7e27a16d7fa74"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=h.ROOT).decode("ascii").strip()


class ProfileLinksTurn05Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {
            path: reviewed_bytes(PROFILE_LINKS_RELEASE, path, pair[1])
            for path, pair in h.GIT_BLOBS.items()
        }
        cls.predecessors = {
            path: reviewed_bytes(PROFILE_LINKS_PARENT, path, pair[0])
            for path, pair in h.GIT_BLOBS.items()
        }

    def test_original_release_and_parent_are_the_reviewed_git_trees(self):
        self.assertEqual(git_revision(PROFILE_LINKS_RELEASE + "^"),
                         PROFILE_LINKS_PARENT)
        self.assertEqual(git_revision(PROFILE_LINKS_RELEASE + "^{tree}"),
                         RELEASE_TREE)
        self.assertEqual(git_revision(PROFILE_LINKS_PARENT + "^{tree}"),
                         PARENT_TREE)
        self.assertEqual(set(h.GIT_BLOBS), {
            "_source/poker/home.html", "poker/index.html",
            "_source/about.html", "about/index.html",
        })

    def test_all_four_exact_published_predecessors_restore(self):
        for path, (before_sha, current_sha) in h.GIT_BLOBS.items():
            with self.subTest(path=path):
                raw = self.released[path]
                self.assertEqual(h.digest(raw), current_sha)
                prior = h.before(path, raw)
                self.assertEqual(h.digest(prior), before_sha)
                self.assertEqual(prior, self.predecessors[path])
                self.assertEqual(raw.count(b'href="/poker/nolan-kido/"'), 1)
                self.assertNotIn(b'href="/poker/nolan-kido/"', prior)
                self.assertEqual(h.before(path, prior), prior)
                self.assertEqual(h.before(Path(path), raw.decode("utf-8")), prior.decode("utf-8"))

    def test_unreviewed_bytes_wrong_paths_and_types_are_preserved(self):
        for path in h.GIT_BLOBS:
            raw = self.released[path]
            for corrupt in (raw + b"UNKNOWN", b"UNKNOWN" + raw, raw[1:]):
                self.assertEqual(h.before(path, corrupt), corrupt)
            self.assertEqual(h.before("misc/" + path, raw), raw)
        self.assertEqual(h.before("misc.bin", bytes([255, 1])), bytes([255, 1]))

    def test_current_about_and_poker_pages_retain_the_profile_link(self):
        for path in h.GIT_BLOBS:
            with self.subTest(path=path):
                current = (h.ROOT / path).read_bytes()
                self.assertEqual(current.count(b'href="/poker/nolan-kido/"'), 1)
        self.assertTrue((h.ROOT / "poker/nolan-kido/index.html").is_file())


if __name__ == "__main__":
    unittest.main()
