"""Source and publication regression for the current public Portland transcript bridge."""
import json
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"_scripts"))
import build
import build_poker_episode
import poker_episode

def read(path):
    return (ROOT/path).read_text(encoding="utf-8")

class PublicTranscriptBridgeTests(unittest.TestCase):
    def test_author_and_published_page_bounded(self):
        source=read("_source/poker/portland-meadows-ep1.html")
        page=read("poker/episodes/portland-meadows-ep1/index.html")
        self.assertEqual(page,build_poker_episode.render())
        self.assertEqual(page.count(source),1)
        self.assertIn('datetime="2026-11-02">November 2, 2026',source)
        self.assertIn('datetime="2026-11-20">November 20, 2026',source)
        self.assertEqual(poker_episode.MODIFIED,"2026-11-20")
        self.assertIn('"datePublished": "2026-11-02"',page)
        self.assertIn('"dateModified": "2026-11-20"',page)
        self.assertEqual(source.count('id="episode-current-transcript"'),1)
        self.assertEqual(source.count('id="episode-result-source-status"'),1)
        self.assertEqual(source.count('id="episode-organizer-schedule"'),1)
        self.assertIn('href="/downloads/portland-meadows-organizer-schedule-2026.json"',source)
        self.assertEqual(source.count('id="episode-current-transcript-title"'),1)
        for seconds in (211,260,387,432,488,532):
            self.assertIn('href="https://www.youtube.com/watch?v=qABaiIcvvpU&t='+str(seconds)+'s"',source)
        self.assertIn("does <strong>not</strong> identify the street",source)
        self.assertIn("the <strong>big blind</strong>",source)
        self.assertIn("not verified against the current public cut",source)
        self.assertNotIn(chr(0x2014),source)
        self.assertNotIn("<iframe",source)
        self.assertNotIn("<form",source)

    def test_observed_transcript_does_not_certify_cards_or_strategy(self):
        audit=json.loads(read("downloads/portland-meadows-public-transcript-audit-2026-11-20.json"))
        facts=audit["targeted_caption_context_check"]
        self.assertEqual(audit["video_id"],"qABaiIcvvpU")
        self.assertEqual(facts["sevens_at_6_27"]["excerpt"],"Small blind folds")
        self.assertFalse(facts["sevens_at_6_27"]["actual_position_independently_verified_by_video"])
        self.assertEqual(facts["six_four_at_4_34"]["excerpt"],"a four comes")
        self.assertFalse(facts["six_four_at_4_34"]["street_verified"])
        self.assertFalse(facts["advertised_5100"]["current_cut_visual_verified"])
        for key in ("current_public_cut_audio_audited","current_public_cut_frames_audited","current_public_cut_human_release_approval"):
            self.assertFalse(audit[key])
        original=json.loads(read("downloads/portland-meadows-ep1-scene-claims.json"))
        self.assertFalse(original["current_public_cut_graphics_checked"])
        self.assertFalse(original["human_release_approval"])

    def test_discovery_modified_and_publication_preserved(self):
        sitemap=read("sitemap.xml")
        self.assertIn('<loc>https://nolankido.com/poker/episodes/portland-meadows-ep1/</loc>\n    <lastmod>2026-11-20</lastmod>',sitemap)
        self.assertEqual(build.build_outputs()[Path("sitemap.xml")],sitemap)
        find=read("find/index.html")
        self.assertIn('"episode-current-transcript-title"',find)
        self.assertEqual(build.build_outputs()[Path("find/index.html")],find)
        source=read("_source/ai-in-real-life.html")
        compiled=read("ai-in-real-life/index.html")
        self.assertIn('href="/poker/episodes/portland-meadows-ep1/#episode-current-transcript"',source)
        a='<section class="section folio-row" id="real-life-creator"'
        b='<section class="section folio-row" id="real-life-everyday"'
        self.assertEqual(source.split(a,1)[1].split(b,1)[0],compiled.split(a,1)[1].split(b,1)[0])
        for filename in ("poker/feed.xml","writing.xml"):
            root=ET.fromstring(read(filename))
            items=[v for v in root.findall("./channel/item") if v.findtext("link")==poker_episode.URL]
            self.assertEqual(len(items),1)
            self.assertEqual(items[0].findtext("pubDate"),"Mon, 02 Nov 2026 00:00:00 GMT")

if __name__=="__main__":
    unittest.main()
