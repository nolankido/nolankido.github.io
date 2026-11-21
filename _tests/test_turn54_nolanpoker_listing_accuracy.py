"""Turn 54: current public watch-page video titles and source-bounded companion routes.

This test checks committed metadata and HTML. It neither contacts YouTube
nor validates video playback, current-cut chapter offsets or thumbnails.
"""
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "downloads/nolanpoker-video-title-link-audit-2026-11-20.json"
ORIGINAL = ROOT / "_source/poker/nolanpoker-video-thumbnails.json"
HUB_SOURCE = ROOT / "_source/poker/home.html"
HUB = ROOT / "poker/index.html"
EP_SOURCE = ROOT / "_source/poker/portland-meadows-ep1.html"
EP = ROOT / "poker/episodes/portland-meadows-ep1/index.html"
EXPECTED_IDS = ("-Wm1i70Z3Bs", "qABaiIcvvpU", "I75GOBVXij4", "bxpaM_1mWPE", "HE7VDvO9gDU", "edNSD5BjIV8")
COMPANIONS = {
    "qABaiIcvvpU": "/poker/episodes/portland-meadows-ep1/",
    "I75GOBVXij4": "/poker/episodes/portland-meadows-standoff/",
    "edNSD5BjIV8": "/poker/episodes/reserve-day-1/",
}

class PageLinks(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.hrefs = []
        self.feed(raw)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])

def audit_errors(audit, earlier, hub, ep):
    errors = []
    video_rows = audit.get("videos", [])
    previous = earlier.get("videos", [])
    if audit.get("checked_on_hawaii") != "2026-11-20" or len(video_rows) != 6 or len(previous) != 6:
        return ["Unexpected audit date or six-video inventory"]
    if tuple(row.get("video_id") for row in video_rows) != EXPECTED_IDS:
        errors.append("IDs do not match the reviewed featured video roster")
    for row, prev in zip(video_rows, previous):
        ident = row.get("video_id")
        url = "https://www.youtube.com/watch?v=" + str(ident)
        if ident != prev.get("video_id") or row.get("public_title_on_check") != prev.get("title"):
            errors.append("Public title differs from the retained gallery snapshot: " + str(ident))
        if row.get("public_watch_url") != url or row.get("canonical_watch_url_observed") != url:
            errors.append("Watch page URL or canonical mismatched: " + str(ident))
        if url not in PageLinks(hub).hrefs or row.get("public_title_on_check") not in hub:
            errors.append("Gallery video link or label missing: " + str(ident))
        if row.get("companion_route") != COMPANIONS.get(ident):
            errors.append("Companion route is missing or wrongly assigned: " + str(ident))
        for field in ("current_video_frames_checked", "current_audio_checked"):
            if row.get(field) is not False:
                errors.append("Audiovisual check improperly certified: " + str(ident))
    if audit.get("local_thumbnail_snapshots_replaced") is not False or audit.get("public_video_playback_verified") is not False:
        errors.append("Unobserved visual verification promoted to completed")
    if hub.count('id="nolanpoker-current-title-check"') != 1:
        errors.append("Missing or duplicated public audit note")
    if "/downloads/nolanpoker-video-title-link-audit-2026-11-20.json" not in PageLinks(hub).hrefs:
        errors.append("Public audit link missing from gallery")
    if "7 BB and an A-K pot" in ep or "not source-checked written companions" in ep:
        errors.append("Outdated secondary-video labeling or companion status remains")
    for title in (previous[2]["title"], previous[5]["title"]):
        if title not in ep:
            errors.append("Cross-video link title does not match public listing")
    for link in (COMPANIONS["I75GOBVXij4"], COMPANIONS["edNSD5BjIV8"]):
        if link not in PageLinks(ep).hrefs:
            errors.append("Existing source-bounded companion not linked: " + link)
    return errors


class NolanPokerListingAccuracyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.old = json.loads(ORIGINAL.read_text(encoding="utf-8"))
        cls.hub_source = HUB_SOURCE.read_text(encoding="utf-8")
        cls.hub_public = HUB.read_text(encoding="utf-8")
        cls.ep_source = EP_SOURCE.read_text(encoding="utf-8")
        cls.ep_public = EP.read_text(encoding="utf-8")

    def test_six_public_video_titles_current_and_curated(self):
        for site, episode in ((self.hub_source, self.ep_source), (self.hub_public, self.ep_public)):
            self.assertEqual(audit_errors(self.audit, self.old, site, episode), [])
        self.assertEqual(len(self.audit["videos"]), 6)
        self.assertFalse(self.audit["public_video_playback_verified"])
        self.assertFalse(self.audit["local_thumbnail_snapshots_replaced"])
        self.assertIn("Read-only public YouTube watch-page", self.audit["current_source_method"])
        self.assertIn("live channel-byline reauthentication", self.audit["not_claimed"])

    def test_source_and_published_passages_match_without_new_schema(self):
        label = '<p class="small-copy" id="nolanpoker-current-title-check">'
        self.assertEqual(self.hub_source.count(label), 1)
        self.assertEqual(self.hub_public.count(label), 1)
        src = self.hub_source.split(label, 1)[1].split("</p>", 1)[0]
        dst = self.hub_public.split(label, 1)[1].split("</p>", 1)[0]
        self.assertEqual(src, dst)
        needle = "<p><strong>Other public poker uploads:</strong>"
        self.assertEqual(self.ep_source.count(needle), 1)
        self.assertEqual(self.ep_public.count(needle), 1)
        self.assertEqual(self.ep_source.split(needle, 1)[1].split("</p>", 1)[0],
                         self.ep_public.split(needle, 1)[1].split("</p>", 1)[0])
        for p in (self.hub_source, self.ep_source):
            self.assertNotIn(chr(0x2014), p)

    def test_existing_companion_urls_and_transcript_scope_are_real(self):
        sitemap=ET.fromstring((ROOT/"sitemap.xml").read_text(encoding="utf-8"))
        urls=[x.findtext("{*}loc") for x in sitemap]
        for ident, route in COMPANIONS.items():
            self.assertEqual(urls.count("https://nolankido.com" + route), 1, ident)
            html=(ROOT / route.lstrip("/") / "index.html").read_text(encoding="utf-8")
            self.assertIn("https://www.youtube.com/watch?v=" + ident, html)
        self.assertIn('id="episode-current-transcript"', self.ep_public)
        self.assertEqual(
            next(r for r in self.audit["videos"] if r["video_id"]=="qABaiIcvvpU")["current_cut_timestamp_evidence"],
            "viewer_transcript_start_positions_only_not_video_frames")
        self.assertIn("not current", self.audit["videos"][2]["current_cut_timestamp_evidence"])

    def test_audited_titles_are_not_companion_editorial_or_thumbnail_claims(self):
        for row in self.audit["videos"]:
            self.assertIs(row["current_video_frames_checked"], False)
            self.assertIs(row["current_audio_checked"], False)
        self.assertEqual(self.audit["companion_pages_publicly_retrievable_on_check"], 3)
        self.assertEqual(self.audit["current_cut_video_visuals_verified"], 0)
        for fragment in ("not live YouTube embeds", "A thumbnail is not independent evidence of any result"):
            self.assertIn(fragment, self.hub_public)
        for banned in ("certified full video", "solver-approved cut", "verified current-cut chapters"):
            self.assertNotIn(banned, self.audit["title_comparison"])

    def test_negative_controls_catch_wrong_titles_and_missing_companions(self):
        changes=[
            ({**self.audit, "videos":[{**self.audit["videos"][0], "public_title_on_check":"Wrong title"},*self.audit["videos"][1:]]}, self.hub_public, self.ep_public),
            (self.audit, self.hub_public.replace('id="nolanpoker-current-title-check"', 'id="other-note"', 1), self.ep_public),
            (self.audit, self.hub_public, self.ep_public.replace("My Ace-King Reshove in a 3-Way All-In | WSOP Circuit", "7 BB and an A-K pot", 1)),
            (self.audit, self.hub_public, self.ep_public.replace('href="/poker/episodes/reserve-day-1/"', 'href="/poker/"', 1)),
        ]
        for audit,hub,ep in changes:
            with self.subTest(change=ep[-120:]):
                self.assertTrue(audit_errors(audit,self.old,hub,ep))

    def test_public_file_is_in_exact_byte_inventory_and_runner(self):
        sys.path.insert(0,str(ROOT/"_scripts"))
        import check_live
        self.assertEqual(check_live.targets(ROOT)["/downloads/nolanpoker-video-title-link-audit-2026-11-20.json"],
                         (200,AUDIT.read_bytes()))
        self.assertIn("test_turn54_nolanpoker_listing_accuracy.py",(ROOT/"_scripts/local_release_checks.py").read_text(encoding="utf-8"))
        workflows=ROOT/".github/workflows"
        self.assertFalse(workflows.exists() and any(x.is_file() and x.suffix.lower() in (".yaml",".yml") for x in workflows.iterdir()))

if __name__=="__main__":
    unittest.main()
