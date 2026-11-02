"""Test exact newer profile-link reversal without hiding any unreviewed change."""
from pathlib import Path
import unittest
import profile_links_turn05_history as h
import episode_turn06_history


class ProfileLinksTurn05Tests(unittest.TestCase):
    def test_all_four_exact_published_predecessors_restore(self):
        for path, (before_sha, current_sha) in h.GIT_BLOBS.items():
            with self.subTest(path=path):
                raw = episode_turn06_history.before(path, (h.ROOT / path).read_bytes())
                self.assertEqual(h.digest(raw), current_sha)
                prior = h.before(path, raw)
                self.assertEqual(h.digest(prior), before_sha)
                self.assertNotIn(b'href="/poker/nolan-kido/"', prior)
                self.assertEqual(h.before(path, prior), prior)
                self.assertEqual(h.before(Path(path), raw.decode("utf-8")), prior.decode("utf-8"))

    def test_unreviewed_bytes_wrong_paths_and_types_are_preserved(self):
        for path in h.GIT_BLOBS:
            raw = episode_turn06_history.before(path, (h.ROOT / path).read_bytes())
            for corrupt in (raw + b"UNKNOWN", b"UNKNOWN" + raw, raw[1:]):
                self.assertEqual(h.before(path, corrupt), corrupt)
            self.assertEqual(h.before("misc/" + path, raw), raw)
        self.assertEqual(h.before("misc.bin", bytes([255, 1])), bytes([255, 1]))


if __name__ == "__main__":
    unittest.main()
