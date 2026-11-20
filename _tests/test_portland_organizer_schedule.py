"""Verify organizer schedule evidence is distinct from the participant's result claims."""
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

class OrganizerScheduleTests(unittest.TestCase):
    def test_official_source_is_bounded_to_scheduled_terms(self):
        record=json.loads(read("downloads/portland-meadows-organizer-schedule-2026.json"))
        event=record["scheduled_event"]
        self.assertEqual(record["schema"],"portland-meadows-high-noon-organizer-schedule-v1")
        self.assertEqual(record["source"]["publisher"],"Portland Meadows Poker Room")
        self.assertEqual(record["source"]["schedule_page"],1)
        self.assertEqual(record["source"]["event_description_page"],2)
        self.assertIn("Wild%20West%20Schedule%202026.pdf",record["source"]["url"])
        self.assertEqual(event["date"],"2026-08-20")
        self.assertEqual(event["local_start_time"],"12:00")
        self.assertEqual(event["local_registration_close"],"14:15")
        self.assertEqual(event["buy_in_usd"],200)
        self.assertEqual(event["starting_chips"],50000)
        self.assertEqual(event["level_minutes"],15)
        self.assertEqual(event["poker_variant"],"No-Limit Hold'em")
        self.assertTrue(event["reentry_permitted"])
        self.assertEqual(record["festival_wide_published_rules"]["source_page"], 2)
        self.assertFalse(record["festival_wide_published_rules"]["under_the_gun_live_straddle"]["applies_to_narrated_hands_confirmed"])
        self.assertFalse(record["festival_wide_published_rules"]["heads_up_pot_speech_and_card_showing"]["applies_to_narrated_hands_confirmed"])
        for key,value in record["evidence_boundaries"].items():
            if key=="confirms_scheduled_event_and_published_structure":
                self.assertTrue(value)
            else:
                self.assertFalse(value,key)
        self.assertIn("cardplayer.com",record["secondary_schedule"]["url"])
        self.assertNotIn(chr(0x2014),read("downloads/portland-meadows-organizer-schedule-2026.json"))

    def test_public_companion_embeds_new_primary_evidence_without_certifying_result(self):
        source=read("_source/poker/portland-meadows-ep1.html")
        page=read("poker/episodes/portland-meadows-ep1/index.html")
        self.assertEqual(page,build_poker_episode.render())
        self.assertEqual(page.count(source),1)
        self.assertEqual(source.count('id="episode-organizer-schedule"'),1)
        self.assertEqual(source.count('id="episode-organizer-schedule-title"'),1)
        self.assertIn('id="episode-result-source-status"',source)
        self.assertIn('href="/downloads/portland-meadows-result-source-audit-2026-11-20.json"',source)
        for phrase in ("Thursday, August 20, 2026 at noon","15-minute levels",
                       "registration closing at","re-entry permitted",
                       "not a post-event results sheet",
                       "not independently certified by the schedule"):
            self.assertIn(phrase,source)
        for link in (
            'href="/downloads/portland-meadows-organizer-schedule-2026.json" download',
            'href="https://www.cardplayer.com/poker-tournaments/1732464-2026-wild-west-poker-tour"',
            'Wild%20West%20Schedule%202026.pdf',
        ):
            self.assertIn(link,source)
        self.assertIn('datetime="2026-11-02">November 2, 2026',source)
        self.assertIn('datetime="2026-11-20">November 20, 2026',source)
        self.assertEqual(poker_episode.MODIFIED,"2026-11-20")
        self.assertNotIn(chr(0x2014),source)
        self.assertNotIn("<iframe",source.lower())
        for old in ("The exact tournament calendar date is not established",
                    "The precise tournament calendar date is not independently documented"):
            self.assertNotIn(old,source)

    def test_original_scene_and_transcript_review_remain_unverified(self):
        original=json.loads(read("downloads/portland-meadows-ep1-scene-claims.json"))
        self.assertFalse(original["event_calendar_date_independently_verified"])
        self.assertFalse(original["current_public_cut_graphics_checked"])
        self.assertFalse(original["human_release_approval"])
        transcript=json.loads(read("downloads/portland-meadows-public-transcript-audit-2026-11-20.json"))
        self.assertFalse(transcript["current_public_cut_audio_audited"])
        self.assertFalse(transcript["current_public_cut_frames_audited"])
        self.assertFalse(transcript["current_public_cut_human_release_approval"])

    def test_discovery_portfolio_and_source_links(self):
        find=read("find/index.html")
        self.assertIn('"episode-organizer-schedule-title"',find)
        self.assertEqual(build.build_outputs()[Path("find/index.html")],find)
        source=read("_source/ai-in-real-life.html")
        output=read("ai-in-real-life/index.html")
        self.assertIn('href="/poker/episodes/portland-meadows-ep1/#episode-organizer-schedule"',source)
        self.assertEqual(source.count("<h2 "),9)
        a='<section class="section folio-row" id="real-life-creator"'
        b='<section class="section folio-row" id="real-life-everyday"'
        self.assertEqual(source.split(a,1)[1].split(b,1)[0],
                         output.split(a,1)[1].split(b,1)[0])
        self.assertIn("downloads/portland-meadows-organizer-schedule-2026.json",
                      read("_scripts/check_live.py"))
        for feed in ("poker/feed.xml","writing.xml"):
            root=ET.fromstring(read(feed))
            items=[item for item in root.findall("./channel/item")
                   if item.findtext("link")==poker_episode.URL]
            self.assertEqual(len(items),1)
            self.assertEqual(items[0].findtext("pubDate"),"Mon, 02 Nov 2026 00:00:00 GMT")
if __name__=="__main__":
    unittest.main()
