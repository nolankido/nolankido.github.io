"""Keep six genuine, locally hosted NolanPoker thumbnails paired with their videos.

The dated metadata manifest is a record of a public YouTube oEmbed check,
not a live-video, hand-history, tournament-result or permanent-title audit.
All verification runs offline and never embeds or requests YouTube media.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))

import build
import build_player_profile
import player_sitemap

MANIFEST = ROOT / "_source/poker/nolanpoker-video-thumbnails.json"
HUB = ROOT / "_source/poker/home.html"
PROFILE = ROOT / "_source/poker/nolan-kido-profile.html"
CSS = ROOT / "assets/poker-discovery.css"
EXPECTED_IDS = (
    "-Wm1i70Z3Bs", "qABaiIcvvpU", "I75GOBVXij4",
    "bxpaM_1mWPE", "HE7VDvO9gDU", "edNSD5BjIV8",
)
GALLERY = re.compile(r'<div class="poker-content-grid">(.*?)</div>\s*<p class="small-copy">', re.S)
PROFILE_LIST = re.compile(r'<h2 id="player-vlog-title">.*?<ul>(.*?)</ul>', re.S)


def contract_errors(hub: str, profile: str, css: str, manifest: dict,
                    override: dict[str, bytes] | None = None) -> list[str]:
    errors: list[str] = []
    videos = manifest.get("videos", [])
    if manifest.get("checked_on") != "2026-11-13" or tuple(v.get("video_id") for v in videos) != EXPECTED_IDS:
        errors.append("dated public metadata inventory is missing or reordered")
        return errors
    gallery = GALLERY.search(hub)
    player_list = PROFILE_LIST.search(profile)
    if not gallery or not player_list:
        return errors + ["gallery or player list missing"]
    cards = re.findall(r'<article class="poker-content-card">(.*?)</article>', gallery.group(1), re.S)
    players = re.findall(r'<li>(.*?)</li>', player_list.group(1), re.S)
    if len(cards) != 6 or len(players) != 6:
        return errors + ["there must be six video cards and player links"]
    if 'https://i.ytimg.com' in hub or '<iframe' in gallery.group(1) or 'youtube.com/embed' in gallery.group(1):
        errors.append("public cards may not embed or hotlink YouTube images")
    if 'All six video titles, channel names and thumbnail URLs were checked' not in hub:
        errors.append("public metadata method and scope disappeared")
    if 'A thumbnail is not independent evidence of any result' not in hub:
        errors.append("thumbnail fact boundary disappeared")
    if 'all six public titles, channel names and thumbnail URLs were checked' not in profile:
        errors.append("player profile metadata review disappeared")
    for index, entry in enumerate(videos):
        video_id = entry["video_id"]
        title = entry["title"]
        path = entry["local_path"]
        if entry.get("author_name") != "NolanPoker":
            errors.append("thumbnail cannot be attributed to a different channel")
        if entry.get("thumbnail_url") != f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg":
            errors.append("thumbnail source does not match its video")
        if not path.startswith("assets/poker/video-thumbnails/") or not path.endswith(".jpg"):
            errors.append("unexpected thumbnail storage location")
            continue
        url = f"https://www.youtube.com/watch?v={video_id}"
        image = f'<img src="/{path}" width="480" height="360" alt="" loading="lazy" decoding="async">'
        if cards[index].count('href="' + url + '"') != 1 or title not in cards[index]:
            errors.append("title or video destination does not match verified metadata")
        if image not in cards[index] or cards[index].count('<img ') != 1:
            errors.append("thumbnail, blank alt, lazy loading or reserved dimensions missing")
        if '<span class="poker-video-play" aria-hidden="true">▶</span>' not in cards[index]:
            errors.append("play affordance lost its decorative accessibility state")
        if players[index].count('href="' + url + '"') != 1 or title not in players[index]:
            errors.append("player profile does not carry the checked video title")
        file_bytes = (override or {}).get(path)
        if file_bytes is None:
            file = ROOT / path
            file_bytes = file.read_bytes() if file.is_file() else b""
        if not file_bytes.startswith(b"\xff\xd8\xff") or sha256(file_bytes).hexdigest() != entry.get("sha256"):
            errors.append("locally stored JPEG differs from reviewed public thumbnail")
        if len(file_bytes) > 50000:
            errors.append("thumbnail exceeds the lightweight image budget")
    if '.page-poker #watch .poker-video-thumb { display:block; position:relative; aspect-ratio:16/9;' not in css:
        errors.append("image frame lost its 16:9 crop")
    if '.page-poker #watch .poker-video-thumb img { display:block; width:100%; height:100%; object-fit:cover;' not in css:
        errors.append("thumbnail no longer fits its frame")
    return errors


class NolanPokerThumbnailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub = HUB.read_text(encoding="utf-8")
        cls.profile = PROFILE.read_text(encoding="utf-8")
        cls.css = CSS.read_text(encoding="utf-8")
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_six_source_matched_thumbnails_and_metadata(self):
        self.assertEqual(contract_errors(self.hub, self.profile, self.css, self.manifest), [])
        self.assertNotIn("\u2014", self.hub)
        self.assertNotIn("\u2014", self.profile)

    def test_rendered_gallery_and_player_record_preserve_video_labels(self):
        compiled_hub = (ROOT / "poker/index.html").read_text(encoding="utf-8")
        compiled_player = (ROOT / "poker/nolan-kido/index.html").read_text(encoding="utf-8")
        self.assertEqual(build.build_outputs()[Path("poker/index.html")], compiled_hub)
        self.assertEqual(build_player_profile.render(), compiled_player)
        self.assertEqual(contract_errors(compiled_hub, compiled_player, self.css, self.manifest), [])

    def test_dates_track_real_revision_without_erasing_prior_review(self):
        pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        self.assertEqual(next(p["updated"] for p in pages if p["path"] == "/poker/"), "2026-11-13")
        self.assertEqual(player_sitemap.MODIFIED, "2026-11-13")
        self.assertIn("November 12, 2026", self.hub)
        self.assertIn("November 12, 2026", self.profile)
        self.assertIn('"dateModified": "2026-11-13"', (ROOT / "poker/index.html").read_text(encoding="utf-8"))
        self.assertIn('"dateModified": "2026-11-13"', (ROOT / "poker/nolan-kido/index.html").read_text(encoding="utf-8"))

    def test_broken_provenance_image_and_accessibility_mutations_fail(self):
        original = self.manifest["videos"][0]
        image_path = original["local_path"]
        image_bytes = (ROOT / image_path).read_bytes()
        modified = json.loads(json.dumps(self.manifest))
        modified["videos"][0]["sha256"] = "0" * 64
        mutations = (
            (self.hub.replace('south-point-hot-dogs.jpg" width="480" height="360" alt="" loading="lazy"',
                              'south-point-hot-dogs.jpg" width="480" height="360" alt="" loading="eager"', 1),
             self.profile, self.css, self.manifest, None),
            (self.hub.replace('alt=""', '', 1), self.profile, self.css, self.manifest, None),
            (self.hub, self.profile, self.css, modified, None),
            (self.hub, self.profile, self.css, self.manifest, {image_path: image_bytes + b"tampered"}),
            (self.hub, self.profile, self.css.replace('aspect-ratio:16/9;', '', 1), self.manifest, None),
            (self.hub.replace('A thumbnail is not independent evidence of any result', 'This thumbnail proves the result', 1), self.profile, self.css, self.manifest, None),
        )
        for index, (hub, profile, css, manifest, override) in enumerate(mutations):
            with self.subTest(mutation=index):
                self.assertTrue(contract_errors(hub, profile, css, manifest, override))


if __name__ == "__main__":
    unittest.main()
