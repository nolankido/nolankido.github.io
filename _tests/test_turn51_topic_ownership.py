"""Turn 51: each AI workflow measurement intent has one principal route.

Run offline from a complete repository:
    python -m unittest discover -s _tests -p test_turn51_topic_ownership.py -v
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

PAIRS = (
    ("_source/technology/home.html", "technology/index.html",
     'To <em>calculate</em> whole-task time',
     '/technology/ai-workflow-pilot/#pilot-protocol'),
    ("_source/technology/ai-time-savings.html", "technology/ai-time-savings/index.html",
     'Which page owns this question?',
     '/technology/ai-workflow-pilot/#pilot-protocol'),
    ("_source/technology/ai-workflow-pilot.html", "technology/ai-workflow-pilot/index.html",
     'Different question, different tool:',
     '/technology/ai-time-savings/'),
)


class TopicOwnershipTests(unittest.TestCase):
    def test_source_and_committed_public_copy_agree(self):
        for source, output, phrase, destination in PAIRS:
            with self.subTest(source=source):
                source_text = (ROOT / source).read_text(encoding="utf-8")
                output_text = (ROOT / output).read_text(encoding="utf-8")
                for text in (source_text, output_text):
                    self.assertEqual(text.count(phrase), 1)
                    self.assertIn('href="' + destination + '"', text)
                    self.assertNotIn('This page proves AI saved time', text)

    def test_distinct_public_canonicals_remain(self):
        for route in ("ai-time-savings", "ai-workflow-pilot"):
            page = (ROOT / "technology" / route / "index.html").read_text(encoding="utf-8")
            canonical = '<link rel="canonical" href="https://nolankido.com/technology/' + route + '/">'
            self.assertEqual(page.count(canonical), 1)

    def test_trial_target_and_original_navigation_survive(self):
        pilot = (ROOT / "technology/ai-workflow-pilot/index.html").read_text(encoding="utf-8")
        calculator = (ROOT / "technology/ai-time-savings/index.html").read_text(encoding="utf-8")
        hub = (ROOT / "technology/index.html").read_text(encoding="utf-8")
        self.assertIn('id="pilot-protocol"', pilot)
        self.assertIn('id="time-workspace"', calculator)
        self.assertIn('id="technology-by-task"', hub)
        self.assertIn('href="/technology/ai-website-visibility/#ai-answer-sprint-panel"', hub)

    def test_topic_map_keeps_source_types_distinct(self):
        report = (ROOT / "_reports/visibility-sprint/seo-geo-turn51-topic-ownership-2026-11-20.md").read_text(encoding="utf-8")
        self.assertIn("No redirects", report)
        self.assertIn("No new canonical", report)
        self.assertIn("not verified as a real-world saving", report)


if __name__ == "__main__":
    unittest.main()
