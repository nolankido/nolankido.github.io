#!/usr/bin/env python3
"""Read-only validation of three first-party Amazon Kindle click paths.

No network, analytics calls, purchases, redirects or emitted events.
Checks exact author-provided links against the public edition ledger.
An HTML href and tracking attributes do NOT establish that an event was
ingested, the Amazon listing is purchasable, or a KDP order was placed.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

from poker_book_growth_scorecard import EVENTS

ROOT = Path(__file__).resolve().parents[1]
LEDGER = "downloads/nolan-kido-book-edition-evidence.json"
PRIVACY = "privacy/index.html"
ASINS = {
    "one-workflow-at-a-time": "B0HRQNCP7Y",
    "how-to-play-no-limit-texas-holdem": "B0HSB98324",
    "ai-works-human-decides": "B0HSF8K76R",
}
ROUTES = {
    "books/index.html": (
        ("one-workflow-at-a-time", "one-workflow-kindle-amazon-click", "books-catalog"),
        ("how-to-play-no-limit-texas-holdem", "poker-book-kindle-amazon-click", "books-catalog"),
        ("ai-works-human-decides", "ai-works-human-decides-kindle-amazon-click", "books-catalog"),
    ),
    "books/one-workflow-at-a-time/index.html": (
        ("one-workflow-at-a-time", "one-workflow-kindle-amazon-click", "book-page-hero"),
    ),
    "books/how-to-play-no-limit-texas-holdem/index.html": (
        ("how-to-play-no-limit-texas-holdem", "poker-book-kindle-amazon-click", "book-page-hero"),
    ),
}
SOURCE_FILES = {
    "books/index.html": "_source/books/index.html",
    "books/one-workflow-at-a-time/index.html": "_source/books/one-workflow-at-a-time.html",
    "books/how-to-play-no-limit-texas-holdem/index.html":
        "_source/books/how-to-play-no-limit-texas-holdem.html",
}


class Anchors(HTMLParser):
    def __init__(self, doc: str):
        super().__init__(convert_charrefs=True)
        self.links: list[dict] = []
        self.feed(doc)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs))


def text_file(root: Path, path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def author_destinations(data: dict) -> dict[str, str]:
    """Map only precisely supplied ASINs, not independently verified Amazon metadata."""
    selected = {}
    works = data.get("works")
    supplements = data.get("supplementary_author_supplied_titles")
    if not isinstance(works, list) or not isinstance(supplements, list):
        raise ValueError("Invalid public edition ledger")
    for work in works:
        if not isinstance(work, dict):
            raise ValueError("Invalid source work")
        kindle = next((f for f in work.get("formats", ())
                       if isinstance(f, dict) and f.get("format") == "kindle_ebook"), {})
        slug = work.get("slug")
        if slug in ASINS:
            if kindle.get("source_type") != "author_direct" or kindle.get("status") != "not_verified":
                raise ValueError("Invalid author-provided source label")
            selected[slug] = (kindle.get("author_supplied_product_url"),
                              kindle.get("author_supplied_asin"))
    for item in supplements:
        if not isinstance(item, dict):
            raise ValueError("Invalid supplementary edition")
        if item.get("title") == "AI Works, Human Decides":
            if (item.get("source_type") != "author_direct"
                    or item.get("retailer_verification_status") != "not_verified"
                    or item.get("retail_page_inspected") is not False):
                raise ValueError("Invalid supplementary Kindle provenance")
            selected["ai-works-human-decides"] = (
                item.get("author_supplied_product_url"), item.get("author_supplied_asin"))
    if set(selected) != set(ASINS):
        raise ValueError("Missing or unexpected supplied Kindle records")
    links = {}
    for slug, (url, asin) in selected.items():
        if asin != ASINS[slug] or not isinstance(url, str):
            raise ValueError("Supplied ASIN does not match the reviewed book")
        parts = urlsplit(url)
        if (parts.scheme != "https" or parts.hostname != "www.amazon.com"
                or parts.port is not None or parts.username is not None
                or parts.password is not None or parts.query or parts.fragment
                or not parts.path.endswith("/dp/" + asin)
                or not re.fullmatch(r"B0[A-Z0-9]{8}", asin)):
            raise ValueError("Supplied Amazon URL is not the reviewed direct product link")
        links[slug] = url
    if len(set(links.values())) != len(links):
        raise ValueError("Two books share an unexpected Amazon destination")
    return links


def audit(root: Path = ROOT) -> dict:
    failures = []
    urls = {}
    try:
        urls = author_destinations(json.loads(text_file(root, LEDGER)))
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        failures.append("edition_ledger: " + type(exc).__name__)
    checked = []
    if urls:
        for path, expectations in ROUTES.items():
            details = {"route": "/" + path.replace("index.html", ""),
                       "expected_book_links": len(expectations),
                       "valid_link_contracts": 0, "public_source_equal": False}
            try:
                html = text_file(root, path)
                source = text_file(root, SOURCE_FILES[path])
                details["public_source_equal"] = html == source
                if not details["public_source_equal"]:
                    failures.append(path + ": source and published HTML differ")
                tracker = re.findall(
                    r'<script\b[^>]*src="https://cloud\.umami\.is/script\.js"[^>]*>',
                    html)
                if len(tracker) != 1 or not all(
                    f'data-{key}="true"' in tracker[0]
                    for key in ("do-not-track", "exclude-search", "exclude-hash")
                ):
                    failures.append(path + ": missing or duplicated approved tracker")
                elements = Anchors(html).links
                tagged = [link for link in elements if "data-umami-event" in link]
                destinations = [link for link in elements
                                if (link.get("href") or "").startswith("https://www.amazon.com/")]
                if len(tagged) != len(expectations) or len(destinations) != len(expectations):
                    failures.append(path + ": unexpected tracking or Amazon anchor count")
                for slug, event, source_name in expectations:
                    matches = [link for link in destinations if link.get("href") == urls[slug]]
                    if len(matches) != 1:
                        failures.append(path + ": wrong or missing destination for " + slug)
                        continue
                    link = matches[0]
                    if (link.get("data-umami-event") != event
                            or link.get("data-umami-event-source") != source_name
                            or event not in EVENTS
                            or source_name not in EVENTS[event]
                            or len(event) > 50
                            or not {"noopener", "noreferrer"}.issubset(
                                set((link.get("rel") or "").split()))
                            or "onclick" in link):
                        failures.append(path + ": invalid event or link metadata for " + slug)
                        continue
                    details["valid_link_contracts"] += 1
                if "umami.track(" in html:
                    failures.append(path + ": duplicate explicit analytics call")
            except (OSError, UnicodeError, ValueError) as exc:
                failures.append(path + ": " + type(exc).__name__)
            checked.append(details)
    try:
        privacy = text_file(root, PRIVACY)
        if ("limited Amazon book-link click events" not in privacy
                or "A click is not proof of an Amazon purchase" not in privacy):
            failures.append("privacy: click-event disclosure absent")
    except (OSError, UnicodeError):
        failures.append("privacy: unreadable")
    return {
        "status": "pass" if not failures else "fail",
        "scope": "read_only_local_link_contracts",
        "routes": checked,
        "link_contracts_expected": 5,
        "link_contracts_verified": sum(x["valid_link_contracts"] for x in checked),
        "author_supplied_asins": dict(ASINS),
        "analytics_events_received": None,
        "amazon_detail_page_verified": None,
        "attribution_tag_available": None,
        "kdp_attributed_orders": None,
        "errors": failures,
        "interpretation": (
            "The direct href works independently of the optional Umami script. "
            "This local audit does not click the link, load Amazon or collect sales evidence."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Reviewed site checkout")
    args = parser.parse_args(argv)
    result = audit(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
