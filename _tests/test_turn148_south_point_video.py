"""Keep the newly verified NolanPoker link discoverable without inventing video details.

External title and channel ownership were checked against YouTube oEmbed on
November 12, 2026. This test deliberately uses fixed, publicly reviewed
metadata, not a network call, credential, or live-video content assertion.
"""
from __future__ import annotations

from pathlib import Path
import json
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))

import build
import build_player_profile
import player_sitemap

VIDEO = "https://www.youtube.com/watch?v=-Wm1i70Z3Bs"
TITLE = "I Went for $1.50 Hot Dogs... Then Entered a $120 Poker Tournament"
CHECKED = "November 12, 2026"
ORIGINAL = ("qABaiIcvvpU", "I75GOBVXij4", "bxpaM_1mWPE",
            "HE7VDvO9gDU", "edNSD5BjIV8")


def discovery_errors(hub: str, profile: str) -> list[str]:
    """Validate the two visible visitor paths and the evidence boundary."""
    errors = []
    gallery = re.search(r'<div class="poker-content-grid">(.*?)</div>\s*<p class="small-copy">', hub, re.S)
    player_list = re.search(r'<h2 id="player-vlog-title">.*?<ul>(.*?)</ul>', profile, re.S)
    if gallery is None or player_list is None:
        return ["one public video list is missing"]
    cards = re.findall(r'<article class="poker-content-card">(.*?)</article>', gallery.group(1), re.S)
    list_items = re.findall(r'<li>(.*?)</li>', player_list.group(1), re.S)
    if len(cards) != 6 or len(list_items) != 6:
        errors.append("both visitor lists must contain six entries")
    if not cards or not list_items or VIDEO not in cards[0] or VIDEO not in list_items[0]:
        errors.append("the recently checked South Point video must be easy to find")
    for name, section in (("hub", gallery.group(1)), ("profile", player_list.group(1))):
        if section.count('href="' + VIDEO + '"') != 1:
            errors.append(name + " missing or duplicate South Point link")
        if TITLE not in section:
            errors.append(name + " mismatches checked public YouTube title")
        for video_id in ORIGINAL:
            if section.count('watch?v=' + video_id + '"') != 1:
                errors.append(name + " changed an older published video")
        for forbidden in ("<iframe", "youtube.com/embed/", "sub_confirmation=", "utm_"):
            if forbidden in section:
                errors.append(name + " introduced an embedded or tracked link")
        if "not" not in section or "reviewed" not in section:
            errors.append(name + " has no clear source limitation")
    if "Six public video links" not in hub or "Six public video links" not in profile:
        errors.append("public counts disagree")
    if "six linked tournament videos" not in profile:
        errors.append("creator introduction still advertises an older count")
    if CHECKED not in hub or CHECKED not in profile:
        errors.append("public metadata review date is missing")
    if "separately listed Lucky 300 result" not in hub or "separate Lucky 300 result" not in profile:
        errors.append("the different South Point events must not be conflated")
    if "footage" not in hub or "footage" not in profile:
        errors.append("video verification must not be mistaken for a footage audit")
    return errors


class SouthPointVideoDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub_source = (ROOT / "_source/poker/home.html").read_text(encoding="utf-8")
        cls.profile_source = (ROOT / "_source/poker/nolan-kido-profile.html").read_text(encoding="utf-8")
        cls.hub = (ROOT / "poker/index.html").read_text(encoding="utf-8")
        cls.profile = (ROOT / "poker/nolan-kido/index.html").read_text(encoding="utf-8")

    def test_six_public_links_match_in_sources_and_rendered_pages(self):
        for hub, profile in ((self.hub_source, self.profile_source), (self.hub, self.profile)):
            with self.subTest(rendered=hub is self.hub):
                self.assertEqual(discovery_errors(hub, profile), [])
                self.assertNotIn("\u2014", hub)
                self.assertNotIn("\u2014", profile)

    def test_public_metadata_and_sitemap_use_actual_content_revision(self):
        self.assertEqual(build.build_outputs()[Path("poker/index.html")], self.hub)
        self.assertEqual(build_player_profile.render(), self.profile)
        manifest = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        poker = next(page for page in manifest if page["path"] == "/poker/")
        self.assertEqual(poker["updated"], "2026-11-12")
        self.assertEqual(player_sitemap.MODIFIED, "2026-11-12")
        self.assertIn('"dateModified": "2026-11-12"', self.hub)
        self.assertIn('"dateModified": "2026-11-12"', self.profile)
        self.assertEqual(player_sitemap.record(ROOT), (player_sitemap.URL, player_sitemap.MODIFIED))
        records = {entry.findtext("{*}loc"): entry.findtext("{*}lastmod")
                   for entry in ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))}
        self.assertEqual(records["https://nolankido.com/poker/"], "2026-11-12")
        self.assertEqual(records[player_sitemap.URL], "2026-11-12")

    def test_missing_link_wrong_title_or_unverified_claim_fails(self):
        mutations = (
            (self.hub_source.replace(VIDEO, "https://youtube.invalid/watch", 1), self.profile_source),
            (self.hub_source, self.profile_source.replace(TITLE, "An invented YouTube title", 1)),
            (self.hub_source.replace("Six public video links", "Five public video links", 1), self.profile_source),
            (self.hub_source, self.profile_source.replace("separate Lucky 300 result", "same Lucky 300 result", 1)),
            (self.hub_source.replace("The title is confirmed by public YouTube metadata, but the footage, hand details and chapter times have not been independently reviewed here.", "The hands are independently verified.", 1), self.profile_source),
        )
        for hub, profile in mutations:
            with self.subTest(difference=hub != self.hub_source):
                self.assertTrue(discovery_errors(hub, profile))


if __name__ == "__main__":
    unittest.main()
