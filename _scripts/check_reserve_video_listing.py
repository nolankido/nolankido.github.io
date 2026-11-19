#!/usr/bin/env python3
"""Check one Reserve NolanPoker title/thumbnail against its local source trail.

Offline by default. --live makes two read-only public YouTube requests. It
checks packaging metadata, never a transcript, scene, hand or tournament result.
No automation, credentials or paid service are involved.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
VIDEO_ID = "edNSD5BjIV8"
VIDEO_URL = "https://www.youtube.com/watch?v=" + VIDEO_ID
THUMBNAIL_URL = f"https://i.ytimg.com/vi/{VIDEO_ID}/hqdefault.jpg"
MANIFEST = Path("_source/poker/nolanpoker-video-thumbnails.json")
LEDGER = Path("downloads/reserve-day1-public-source-ledger.json")
THUMBNAIL = Path("assets/poker/video-thumbnails/reserve-day-1.jpg")
SOURCES = (
    Path("_source/poker/home.html"),
    Path("_source/poker/nolan-kido-profile.html"),
    Path("_source/poker/reserve-day-1.html"),
)


def checked_local(root: Path = ROOT) -> dict:
    """Refuse incomplete, conflicting or stale local evidence, with no network."""
    data = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    matches = [item for item in data["videos"] if item.get("video_id") == VIDEO_ID]
    if len(matches) != 1:
        raise ValueError("Reserve video identity must appear once in public manifest")
    item = matches[0]
    ledger = json.loads((root / LEDGER).read_text(encoding="utf-8"))["video"]
    if (item.get("title") != ledger.get("public_title")
            or item.get("checked_on") != ledger.get("public_title_checked_on")
            or item.get("checked_on") != ledger.get("public_thumbnail_checked_on")
            or item.get("author_name") != "NolanPoker"
            or item.get("thumbnail_url") != THUMBNAIL_URL
            or item.get("local_path") != THUMBNAIL.as_posix()
            or ledger.get("url") != VIDEO_URL
            or ledger.get("current_youtube_cut_compared_with_archive") is not False
            or ledger.get("current_youtube_chapter_offsets_verified") is not False
            or ledger.get("public_metadata_does_not_verify_current_cut") is not True):
        raise ValueError("Reserve title, source date, author or evidence limit disagrees")
    image = (root / THUMBNAIL).read_bytes()
    digest = sha256(image).hexdigest()
    if (not image.startswith(b"\xff\xd8\xff") or len(image) > 50_000
            or digest != item.get("sha256")
            or digest != ledger.get("public_thumbnail_sha256")):
        raise ValueError("Reserve local thumbnail differs from its checked SHA-256")
    for path in SOURCES:
        content = (root / path).read_text(encoding="utf-8")
        if item["title"] not in content or VIDEO_URL not in content:
            raise ValueError("Reserve public title/video must match " + path.as_posix())
        if "\u2014" in content:
            raise ValueError("Published Reserve route cannot introduce em dashes")
    return {"title": item["title"], "checked_on": item["checked_on"],
            "thumbnail_sha256": digest, "video_url": VIDEO_URL}


def checked_remote(checked: dict, read_json, read_bytes) -> dict:
    """Compare only oEmbed identity and the current public thumbnail snapshot."""
    url = "https://www.youtube.com/oembed?" + urlencode({
        "url": VIDEO_URL, "format": "json",
    })
    meta = read_json(url)
    if (meta.get("title") != checked["title"]
            or meta.get("author_name") != "NolanPoker"
            or meta.get("provider_name") != "YouTube"
            or meta.get("thumbnail_url") != THUMBNAIL_URL):
        raise ValueError("Public YouTube metadata moved since the reviewed snapshot")
    remote = read_bytes(THUMBNAIL_URL)
    if sha256(remote).hexdigest() != checked["thumbnail_sha256"]:
        raise ValueError("Public thumbnail changed since the reviewed snapshot")
    return {"metadata": "match", "thumbnail": "match", "scope": "title/channel/artwork only"}


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "NolanKido-public-metadata-check/1.0"})
    with urlopen(request, timeout=12) as response:
        return response.read(80_000)


def fetch_json(url: str) -> dict:
    return json.loads(fetch_bytes(url))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Compare with public YouTube oEmbed and thumbnail now")
    args = parser.parse_args()
    try:
        checked = checked_local()
        if args.live:
            checked["remote"] = checked_remote(checked, fetch_json, fetch_bytes)
        print(json.dumps(checked, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, HTTPError, URLError) as exc:
        print("Reserve video metadata check failed: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
