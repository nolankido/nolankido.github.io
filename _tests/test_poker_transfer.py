"""Read-only QA of the public draft transfer packet, not a learning outcome."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from contextlib import contextmanager
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("poker_transfer_verify", ROOT / "_reports/poker-transfer/verify.py")
module = module_from_spec(SPEC)
SPEC.loader.exec_module(module)

class PokerTransferTests(unittest.TestCase):
    @contextmanager
    def changed_packet(self, filename, before, after):
        with tempfile.TemporaryDirectory() as folder:
            copied = Path(folder) / "packet"
            shutil.copytree(module.FOLDER, copied)
            target = copied / filename
            source = target.read_text()
            self.assertIn(before, source)
            target.write_text(source.replace(before, after))
            with patch.object(module, "FOLDER", copied):
                yield

    def test_rejects_card_and_source_drift(self):
        with self.changed_packet("cards/S2-B.md", "at least 30 counters each still behind", "no counters behind"):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_wrong_hand_comparison_repair_in_key(self):
        with self.changed_packet("facilitator-key.md", "/poker/hand-rankings/#compare", "/poker/betting-with-a-purpose/#purpose"):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_missing_assisted_attempt_counts(self):
        with self.changed_packet("summary-form.md", "Assisted attempted (any help)", "Hint only"):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_conflated_exposure_fields(self):
        with self.changed_packet("session-form.md", "Prior exposure to this case's answer key: yes / no / unsure", "Prior exposure to a similar problem or answer key: ______"):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_missing_assisted_reasoning_record(self):
        with self.changed_packet("session-form.md", "Assisted reasoning point 3:", "Unscored later result:"):
            with self.assertRaises(AssertionError):
                module.check()

    def test_twelve_transfer_cases_verify_independently(self):
        self.assertEqual(module.check(), 12)

    def test_existing_course_and_saved_progress_are_unmodified(self):
        text = (ROOT / "_reports/poker-transfer/README.md").read_text()
        self.assertIn("No existing site data, pages, scripts, CSS", text)
        self.assertIn("pending", text.lower())
        self.assertEqual(len(module.LESSONS), 6)
        self.assertIn("separate A/B protocol", text)
        self.assertTrue((ROOT / "_reports/poker-transfer/session-form.md").exists())
        self.assertEqual(len(list((ROOT / "_reports/poker-transfer/cards").glob("S?-?.md"))), 12)
        for slug in module.LESSONS:
            self.assertTrue((ROOT / "_source/poker" / (slug + ".html")).exists())

if __name__ == "__main__":
    unittest.main()
