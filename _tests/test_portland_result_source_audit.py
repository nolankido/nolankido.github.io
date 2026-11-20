"""Check that a bounded 2026 Portland Meadows results search does not certify the player's payout."""
import json
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"_scripts"))
import build_poker_episode
import poker_episode
import build

def read(path):
    return (ROOT/path).read_text(encoding="utf-8")

class ResultSourceAuditTests(unittest.TestCase):
    def test_sources_and_coverage_do_not_establish_a_public_result(self):
        record=json.loads(read("downloads/portland-meadows-result-source-audit-2026-11-20.json"))
        self.assertEqual(record["schema"],"portland-meadows-event-specific-result-source-audit-v1")
        self.assertEqual(record["checked_on"],"2026-11-20")
        self.assertEqual(record["scheduled_local_date"],"2026-08-20")
        self.assertEqual(len(record["sources"]),4)
        self.assertIn("not an exhaustive search",record["scope"])
        self.assertIn("not evidence",record["interpretation"])
        types={x["type"] for x in record["sources"]}
        self.assertEqual(types,{"organizer_schedule","venue_results_directory",
                                "independent_festival_schedule","search_indexed_event_archive"})
        indexed=next(x for x in record["sources"] if x["type"]=="search_indexed_event_archive")
        self.assertIn("January-April",indexed["supports"])
        self.assertIn("Direct archive fetch blocked",indexed["limitation"])
        self.assertNotIn(chr(0x2014),read("downloads/portland-meadows-result-source-audit-2026-11-20.json"))

    def test_reported_deal_not_mislabeled_as_verified(self):
        record=json.loads(read("downloads/portland-meadows-result-source-audit-2026-11-20.json"))
        claims=record["first_person_narration"]
        self.assertEqual(claims["entries"],88)
        self.assertEqual(claims["reported_prize_pool_usd"],17600)
        self.assertEqual(claims["advertised_first_prize_usd"],5100)
        self.assertEqual(claims["post_deal_personal_gross_share_usd"],2900)
        self.assertFalse(claims["independently_verified_for_specific_event"])
        flags=record["verification_flags"]
        self.assertTrue(flags["schedule_independently_confirmed"])
        for name,value in flags.items():
            if name!="schedule_independently_confirmed":
                self.assertFalse(value,name)
        scene=json.loads(read("downloads/portland-meadows-ep1-scene-claims.json"))
        self.assertFalse(scene["current_public_cut_graphics_checked"])
        self.assertFalse(scene["human_release_approval"])
        transcript=json.loads(read("downloads/portland-meadows-public-transcript-audit-2026-11-20.json"))
        self.assertFalse(transcript["current_public_cut_frames_audited"])

    def test_new_source_status_is_indexed_but_original_article_is_preserved(self):
        source=read("_source/poker/portland-meadows-ep1.html")
        html=read("poker/episodes/portland-meadows-ep1/index.html")
        self.assertEqual(html,build_poker_episode.render())
        self.assertEqual(html.count(source),1)
        self.assertEqual(source.count('id="episode-result-source-status"'),1)
        self.assertEqual(source.count('id="episode-result-source-status-title"'),1)
        self.assertIn('href="/downloads/portland-meadows-result-source-audit-2026-11-20.json" download',source)
        self.assertIn("participant",source.lower())
        self.assertIn("Missing external documentation does not mean the account is false",source)
        self.assertIn("January-April",source)
        self.assertIn("Direct access to the archive was restricted",source)
        self.assertNotIn(chr(0x2014),source)
        self.assertNotIn("<iframe",source.lower())
        self.assertEqual(poker_episode.MODIFIED,"2026-11-20")
        self.assertIn('"datePublished": "2026-11-02"',html)
        self.assertIn('"dateModified": "2026-11-20"',html)
        find=read("find/index.html")
        self.assertIn('"episode-result-source-status-title"',find)
        self.assertEqual(build.build_outputs()[Path("find/index.html")],find)
        self.assertIn("downloads/portland-meadows-result-source-audit-2026-11-20.json",
                      read("_scripts/check_live.py"))

    def test_portfolio_and_feeds_preserve_evidence_boundaries(self):
        source=read("_source/ai-in-real-life.html")
        page=read("ai-in-real-life/index.html")
        self.assertIn('href="/poker/episodes/portland-meadows-ep1/#episode-result-source-status"',source)
        self.assertEqual(source.count("<h2 "),9)
        a='<section class="section folio-row" id="real-life-creator"'
        b='<section class="section folio-row" id="real-life-everyday"'
        self.assertEqual(source.split(a,1)[1].split(b,1)[0],page.split(a,1)[1].split(b,1)[0])
        for name in ("poker/feed.xml","writing.xml"):
            root=ET.fromstring(read(name))
            matches=[i for i in root.findall("./channel/item")
                     if i.findtext("link")==poker_episode.URL]
            self.assertEqual(len(matches),1)
            self.assertEqual(matches[0].findtext("pubDate"),"Mon, 02 Nov 2026 00:00:00 GMT")

if __name__=="__main__":
    unittest.main()
