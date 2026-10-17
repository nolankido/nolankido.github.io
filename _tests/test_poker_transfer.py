"""Read-only QA of the public draft transfer packet, not a learning outcome."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("poker_transfer_verify", ROOT / "_reports/poker-transfer/verify.py")
module = module_from_spec(SPEC)
SPEC.loader.exec_module(module)

class PokerTransferTests(unittest.TestCase):
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
