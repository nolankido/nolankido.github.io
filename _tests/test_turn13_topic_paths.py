"""Turn 13 exposes a bounded cross-topic AI judgment path and preserves history."""
import subprocess
import unittest
from pathlib import Path

import turn13_topic_paths_history as history


ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    ("_source/technology/home.html", "technology/index.html", "ai-judgment-across-domains"),
    ("_source/poker/home.html", "poker/index.html", "poker-ai-judgment"),
)


def section(path, section_id):
    raw = (ROOT / path).read_text(encoding="utf-8")
    marker = '<section class="section folio-row" id="' + section_id + '"'
    assert raw.count(marker) == 1, (path, section_id)
    start = raw.index(marker)
    end = raw.index("</section>", start) + len("</section>")
    return raw[start:end]


class Turn13TopicPathTests(unittest.TestCase):
    def test_source_and_published_sections_match(self):
        for source, published, section_id in PAGES:
            with self.subTest(source=source):
                self.assertEqual(section(source, section_id), section(published, section_id))
                self.assertEqual(
                    (ROOT / source).read_text(encoding="utf-8").count('id="' + section_id + '"'), 1
                )
                self.assertEqual(
                    (ROOT / published).read_text(encoding="utf-8").count('id="' + section_id + '"'), 1
                )

    def test_all_internal_targets_exist_and_public_sections_stay_bounded(self):
        tech = section("technology/index.html", "ai-judgment-across-domains")
        poker = section("poker/index.html", "poker-ai-judgment")
        for target in (
            "technology/checking-ai-website-changes/index.html",
            "technology/review-reply-evidence-audit/index.html",
            "poker/episodes/portland-meadows-ep1/index.html",
            "poker/reviewing-a-hand/index.html",
        ):
            with self.subTest(target=target):
                self.assertTrue((ROOT / target).is_file())
        self.assertIn('href="/technology/#ai-judgment-across-domains"', poker)
        self.assertIn('href="/poker/reviewing-a-hand/"', tech)
        self.assertIn("does not establish a real-world business error rate", tech)
        self.assertIn("do not claim complete, independently verified GTO or ICM solutions", poker)
        for body in (tech, poker):
            self.assertNotIn("\u2014", body)
            self.assertNotIn("guarantee", body.lower())
            self.assertNotIn("proven edge", body.lower())

    def test_exact_prior_git_blobs_only_are_restored(self):
        for path, (old_sha, current_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                raw = (ROOT / path).read_bytes()
                self.assertEqual(history.blob(raw), current_sha)
                prev = history.before(path, raw)
                self.assertEqual(history.blob(prev), old_sha)
                self.assertEqual(prev, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=ROOT
                ))
                self.assertEqual(history.before(path, prev), prev)
                self.assertEqual(
                    history.before(Path(path), raw.decode("utf-8")), prev.decode("utf-8")
                )

    def test_unknown_mutations_are_not_hidden(self):
        for path in history.BLOBS:
            raw = (ROOT / path).read_bytes()
            for mutation in (raw + b"UNREVIEWED", b"UNREVIEWED" + raw, raw[1:]):
                self.assertEqual(history.before(path, mutation), mutation)
            self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("unknown.bin", bytes([255, 0])),
                         bytes([255, 0]))


if __name__ == "__main__":
    unittest.main()
