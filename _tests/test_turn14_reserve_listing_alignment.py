"""Turn 14: title and thumbnail drift detection, with no live network in tests."""
from copy import deepcopy
from pathlib import Path
import json
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import check_reserve_video_listing as listing


class ReserveListingAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current = listing.checked_local(ROOT)

    def test_current_public_packaging_is_recorded_in_three_entrypoints(self):
        current = self.current
        self.assertEqual(current["title"],
                         "My Ace-King Reshove in a 3-Way All-In | WSOP Circuit")
        self.assertEqual(current["checked_on"], "2026-11-18")
        self.assertEqual(current["thumbnail_sha256"],
                         "01cb25ef4f2efb238a5180faa478a2275b0e2ded9348c051819d20170c45eb5e")
        self.assertEqual(current["video_url"], listing.VIDEO_URL)
        source = (ROOT / listing.SOURCES[-1]).read_text(encoding="utf-8")
        self.assertIn('href="#reserve-pots"', source)
        self.assertIn("not independent proof of the cards actually dealt", source)
        self.assertIn("did not return transcript text", source)
        self.assertIn("have not independently compared", source)
        hub = (ROOT / listing.SOURCES[0]).read_text(encoding="utf-8")
        player = (ROOT / listing.SOURCES[1]).read_text(encoding="utf-8")
        for html in (hub, player):
            self.assertIn('/poker/episodes/reserve-day-1/#reserve-pots', html)
        self.assertIn('/poker/side-pot-lab/', hub)

    def test_online_contract_simulates_no_drift_without_network(self):
        local = self.current
        image = (ROOT / listing.THUMBNAIL).read_bytes()
        public = {
            "title": local["title"], "author_name": "NolanPoker",
            "provider_name": "YouTube", "thumbnail_url": listing.THUMBNAIL_URL,
        }
        self.assertEqual(listing.checked_remote(local, lambda _: deepcopy(public), lambda _: image),
                         {"metadata": "match", "thumbnail": "match", "scope": "title/channel/artwork only"})
        for field, new in (("title", "A new title"), ("author_name", "Imposter"),
                           ("provider_name", "Unknown"), ("thumbnail_url", "https://other.invalid/x.jpg")):
            with self.subTest(field=field):
                changed = dict(public, **{field: new})
                with self.assertRaisesRegex(ValueError, "metadata moved"):
                    listing.checked_remote(local, lambda _: changed, lambda _: image)
        with self.assertRaisesRegex(ValueError, "Public thumbnail changed"):
            listing.checked_remote(local, lambda _: public, lambda _: image + b"changed")

    def test_local_stale_or_overconfident_records_fail_closed(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            for path in (*listing.SOURCES, listing.MANIFEST, listing.LEDGER, listing.THUMBNAIL):
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, dest)
            self.assertEqual(listing.checked_local(root), self.current)

            manifest_file = root / listing.MANIFEST
            original = manifest_file.read_text(encoding="utf-8")
            manifest_file.write_text(original.replace("My Ace-King Reshove", "Wrong title", 1), encoding="utf-8")
            with self.assertRaises(ValueError):
                listing.checked_local(root)
            manifest_file.write_text(original, encoding="utf-8")

            ledger_file = root / listing.LEDGER
            original_ledger = ledger_file.read_text(encoding="utf-8")
            ledger = json.loads(original_ledger)
            ledger["video"]["current_youtube_cut_compared_with_archive"] = True
            ledger_file.write_text(json.dumps(ledger), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "evidence limit"):
                listing.checked_local(root)
            ledger_file.write_text(original_ledger, encoding="utf-8")

            (root / listing.THUMBNAIL).write_bytes(b"not a jpeg")
            with self.assertRaisesRegex(ValueError, "thumbnail"):
                listing.checked_local(root)


if __name__ == "__main__":
    unittest.main()
