"""Turn 53 regression: a real written publication change, not video approval."""
import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PRE = "788e3f44e09d0fc5a93a38bec138867fca492637"
POST = "4f3449cd40cf5b165b756d2c4c2fce9aa3827c67"
BASE = "https://github.com/nolankido/nolankido.github.io/"
BEFORE = BASE + "blob/" + PRE + "/poker/episodes/portland-meadows-ep1/index.html"
AFTER = BASE + "blob/" + POST + "/poker/episodes/portland-meadows-ep1/index.html"
DIFF = BASE + "commit/" + POST
ROUTE = "/technology/ai-poker-video-evidence/"

def read(p):
    return (ROOT / p).read_text(encoding="utf-8")

class PokerPublishedRevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = read("_source/technology/ai-poker-video-evidence.html")
        cls.public = read("technology/ai-poker-video-evidence/index.html")
        cls.ledger = read("downloads/nolanpoker-content-production-evidence-ledger.md")
        cls.transcript = json.loads(read("downloads/portland-meadows-public-transcript-audit-2026-11-20.json"))
        cls.claims = json.loads(read("downloads/portland-meadows-ep1-scene-claims.json"))

    def test_exact_change_and_article_are_linked_without_duplicate_page(self):
        for page in (self.src, self.public):
            self.assertEqual(page.count('id="poker-ai-written-revision"'), 1)
            for url in (BEFORE, AFTER, DIFF):
                self.assertEqual(page.count('href="' + url + '"'), 1)
            self.assertEqual(page.count('href="#poker-ai-written-revision"'), 1)
            self.assertIn('href="/poker/episodes/portland-meadows-ep1/#episode-current-transcript"', page)
        marker='<h3 id="poker-ai-written-revision">'
        self.assertEqual(self.src.split(marker, 1)[1].split('\n  </div>', 1)[0],
                         self.public.split(marker, 1)[1].split('\n  </div>', 1)[0])
        self.assertIn('id="episode-current-transcript"', read("poker/episodes/portland-meadows-ep1/index.html"))

    def test_genuine_written_before_after_has_its_source_and_scope(self):
        self.assertIn("## M. Public written-companion revision", self.ledger)
        for url in (BEFORE, AFTER, DIFF):
            self.assertIn(url, self.ledger)
        for phrase in ("written page", "not a claim that the current YouTube video",
                       "fresh public HTML fetch", "unresolved video review"):
            self.assertIn(phrase.lower(), self.ledger.lower())
        self.assertEqual([x["timecode"] for x in self.transcript["observations"]],
                         ["04:20", "06:27", "07:12", "08:08", "08:52"])
        self.assertEqual(self.claims["scenes"][2]["advertised_first_usd"], 5100)
        self.assertEqual(self.claims["scenes"][2]["received_after_deal_usd"], 2900)

    def test_no_video_frame_or_editor_approval_is_fabricated(self):
        for key in ("current_public_cut_timestamps_checked",
                    "current_public_cut_graphics_checked", "human_release_approval"):
            self.assertIs(self.claims[key], False)
        for key in ("current_public_cut_audio_audited",
                    "current_public_cut_frames_audited",
                    "current_public_cut_graphics_audited",
                    "current_public_cut_human_release_approval"):
            self.assertIs(self.transcript[key], False)
        self.assertIn("sign-in-to-confirm-not-a-bot", self.transcript["player_blocker"])
        for phrase in ("video audio, cards, rights or final human approval was certified",
                       "not a verified edit to the video", "not audio or frame verification"):
            self.assertIn(phrase, self.src)
        self.assertEqual(self.src.count('data-poker-ai-caption="'), 3)

    def test_original_article_identity_and_accurate_freshness(self):
        ps = json.loads(read("_source/pages.json"))
        current = next(x for x in ps if x["id"] == "ai-poker-video-evidence")
        self.assertEqual((current["date"], current["updated"]), ("2026-11-04", "2026-11-20"))
        self.assertEqual(len(re.findall(r'<h2\b', self.src)), 6)
        self.assertEqual(len(re.findall(r'<h2\b', self.public)), 7)
        self.assertEqual(self.public.count('<link rel="canonical" href="https://nolankido.com' + ROUTE + '">'), 1)
        self.assertIn('"datePublished": "2026-11-04"', self.public)
        self.assertIn('"dateModified": "2026-11-20"', self.public)
        self.assertIn("About 10 min read", self.public)
        sitemap = ET.fromstring(read("sitemap.xml"))
        match = [x for x in sitemap if x.findtext("{*}loc") == "https://nolankido.com" + ROUTE]
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0].findtext("{*}lastmod"), "2026-11-20")

    def test_download_and_manual_release_guard_are_registered(self):
        sys.path.insert(0, str(ROOT / "_scripts"))
        import check_live
        self.assertEqual(check_live.targets(ROOT)["/downloads/nolanpoker-content-production-evidence-ledger.md"],
                         (200, (ROOT / "downloads/nolanpoker-content-production-evidence-ledger.md").read_bytes()))
        self.assertIn("test_turn53_poker_published_revision.py", read("_scripts/local_release_checks.py"))
        for value in (self.src,self.ledger):
            self.assertNotIn(chr(0x2014), value)
        workflows = ROOT / ".github/workflows"
        self.assertFalse(workflows.exists() and any(p.is_file() and p.suffix in (".yml", ".yaml") for p in workflows.iterdir()))

    def test_negative_controls_reject_missing_evidence_or_false_approval(self):
        def errors(s):
            bad = []
            for value in (BEFORE, AFTER, DIFF, 'id="poker-ai-written-revision"'):
                if value not in s: bad.append(value)
            if "no actual video audio, cards, rights or final human approval was certified" not in s:
                bad.append("human media gate")
            return bad
        self.assertEqual(errors(self.src), [])
        for variant in (
            self.src.replace(DIFF, "https://example.invalid/unverified"),
            self.src.replace('id="poker-ai-written-revision"', 'id="lost"'),
            self.src.replace("no actual video audio, cards, rights or final human approval was certified", "all frames certified"),
        ):
            self.assertTrue(errors(variant))

if __name__ == "__main__":
    unittest.main()
