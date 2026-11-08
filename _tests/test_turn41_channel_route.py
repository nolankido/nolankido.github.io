"""Visitors can reach the genuine NolanPoker channel without losing evidence routes."""

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))

import build
import build_player_profile
import check_live
from reviewed_release import read as reviewed_bytes
import turn41_channel_route_history as history


CHANNEL = "https://www.youtube.com/@NolanPoker"
VIDEOS = (
    "qABaiIcvvpU", "I75GOBVXij4", "bxpaM_1mWPE",
    "HE7VDvO9gDU", "edNSD5BjIV8",
)


def channel_route_errors(hub: str, player: str) -> list[str]:
    """A deliberately small visitor-route contract; no external YouTube assumptions."""
    errors = []
    intro = hub.split('<section class="section folio-row" id="free-course"', 1)[0]
    watch_parts = hub.split('id="watch"', 1)
    watch = watch_parts[1].split('id="standoff-ak-source-review"', 1)[0] if len(watch_parts) == 2 else ""
    player_parts = player.split('id="player-vlog-title"', 1)
    player_video = player_parts[1].split('</section>', 1)[0] if len(player_parts) == 2 else ""

    if not (intro and watch and player_video):
        errors.append("one of the three viewing routes is missing")
    if '<a href="#watch">Browse the public videos and written companions</a>' not in intro:
        errors.append("first-screen route to the onsite video index is missing")
    if intro.count('href="' + CHANNEL + '"') != 1:
        errors.append("first-screen channel URL missing, duplicated or changed")
    if '<p class="poker-entry-note" id="nolanpoker-channel">' not in watch:
        errors.append("onsite video gallery channel action missing")
    if watch.count('href="' + CHANNEL + '"') != 1 or "subscribe on the NolanPoker YouTube channel" not in watch:
        errors.append("onsite video gallery no longer offers a clear channel subscription path")
    if player_video.count('href="' + CHANNEL + '"') != 1 or "subscribe there" not in player_video:
        errors.append("player profile channel path missing, duplicated or unclear")
    if 'id="watch"' not in hub:
        errors.append("onsite jump target missing")

    for snippet in (intro, watch, player_video):
        if any(x in snippet for x in ("sub_confirmation=", "utm_", "youtube.com/embed/", "<iframe", "onclick=")):
            errors.append("tracking, popup or embedded video added to the follow route")
    for video in VIDEOS:
        if hub.count('href="https://www.youtube.com/watch?v=' + video + '"') < 1:
            errors.append("existing published video disappeared from hub: " + video)
        if player.count('href="https://www.youtube.com/watch?v=' + video + '"') < 1:
            errors.append("existing published video disappeared from profile: " + video)
    return errors


class NolanPokerChannelRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub_source = (ROOT / "_source/poker/home.html").read_text(encoding="utf-8")
        cls.player_source = (ROOT / "_source/poker/nolan-kido-profile.html").read_text(encoding="utf-8")
        cls.hub = (ROOT / "poker/index.html").read_text(encoding="utf-8")
        cls.player = (ROOT / "poker/nolan-kido/index.html").read_text(encoding="utf-8")

    def test_channel_can_be_found_from_each_public_entry_point(self):
        for hub, player in ((self.hub_source, self.player_source), (self.hub, self.player)):
            with self.subTest(rendered=(hub is self.hub)):
                self.assertEqual(channel_route_errors(hub, player), [])
                self.assertNotIn("\u2014", hub)
                self.assertNotIn("\u2014", player)

    def test_builder_and_read_only_public_inventory_match(self):
        self.assertEqual(build.build_outputs()[Path("poker/index.html")], self.hub)
        self.assertEqual(build_player_profile.render(), self.player)
        self.assertEqual(check_live.targets()["/poker/"], (200, self.hub.encode("utf-8")))
        self.assertEqual(check_live.targets()["/poker/nolan-kido/"], (200, self.player.encode("utf-8")))

    def test_misrouted_or_hidden_channel_actions_fail_closed(self):
        for hub, player in (
            (self.hub_source.replace(CHANNEL, "https://www.youtube.com/@OtherChannel", 1), self.player_source),
            (self.hub_source.replace('href="#watch"', 'href="#missing-watch"', 1), self.player_source),
            (self.hub_source.replace("subscribe on the NolanPoker YouTube channel", "view the channel", 1), self.player_source),
            (self.hub_source, self.player_source.replace(CHANNEL, "https://www.youtube.com/@AnotherName", 1)),
            (self.hub_source, self.player_source.replace(CHANNEL, CHANNEL + "?sub_confirmation=1", 1)),
        ):
            with self.subTest(hub_change=hub is not self.hub_source, profile_change=player is not self.player_source):
                self.assertTrue(channel_route_errors(hub, player))

    def test_historical_bridge_restores_only_five_exact_predecessors(self):
        self.assertEqual(len(history.records()["files"]), 5)
        turn41_release = "d5b0a01a0511a1f5bd04332c9c34af681a3cb8e1"
        for path, (before_hash, after_hash) in history.records()["files"].items():
            with self.subTest(path=path):
                current = (ROOT / path).read_bytes()
                turn41 = reviewed_bytes(turn41_release, path, after_hash)
                prior = reviewed_bytes(history.PARENT, path, before_hash)
                self.assertEqual(history.before(path, turn41), prior)
                self.assertEqual(history.before(Path(path), turn41.decode("utf-8")), prior.decode("utf-8"))
                self.assertEqual(history.before(path, turn41 + b"UNREVIEWED"), turn41 + b"UNREVIEWED")
                self.assertEqual(history.before(path, current + b"UNREVIEWED"), current + b"UNREVIEWED")
                self.assertEqual(history.before("unknown/" + path, current), current)


if __name__ == "__main__":
    unittest.main()
