"""Full-page hand-review layout and keyboard QA without network navigation.

Read the committed HTML and inline its local styles, then use set_content on an
in-memory Chromium page. This runs even where fake HTTPS origins are blocked.
It tests rendered keyboard controls and target sections, not HTTP navigation.
No login, server, CI service, browser extensions or external network calls.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(os.environ.get("POKER_BROWSER_ROOT", Path(__file__).resolve().parents[1])).resolve()
WIDTHS = (320, 390, 768, 1440)
CASES = (
    ("/poker/episodes/portland-meadows-ep1/", "hand-64o-review",
     "/poker/six-to-ten-bb-tournament-decisions/#bridge-sb"),
    ("/poker/episodes/portland-meadows-ep1/", "hand-77-review",
     "/poker/short-stack-decisions/#depths"),
    ("/poker/episodes/portland-meadows-standoff/", "standoff-second-review",
     "/poker/short-stack-decisions/#icm-call"),
)
STYLESHEET = re.compile(
    r'<link\b(?=[^>]*\brel="stylesheet")(?=[^>]*\bhref="([^"]+)")[^>]*>',
    re.I,
)
SCRIPT = re.compile(r'<script\b[^>]*>[\s\S]*?</script>', re.I)
PRELOAD = re.compile(r'<link\b[^>]*\brel="(?:preload|modulepreload)"[^>]*>', re.I)


def local_document(route: str) -> str:
    """Inline only root-owned CSS in the exact committed page source."""
    path = ROOT / route.strip("/") / "index.html"
    original = path.read_text(encoding="utf-8")
    found = []

    def inline_css(match: re.Match[str]) -> str:
        href = match.group(1)
        url = urlsplit(href)
        if url.scheme or url.netloc or not url.path.startswith("/assets/"):
            raise ValueError("Non-local stylesheet in offline test: " + href)
        file = (ROOT / url.path.lstrip("/")).resolve()
        if not file.is_relative_to(ROOT) or not file.is_file():
            raise ValueError("Missing or escaping stylesheet: " + href)
        css = file.read_text(encoding="utf-8")
        if "</style" in css.lower():
            raise ValueError("CSS contains an unsafe style terminator: " + href)
        found.append(url.path)
        return '<style data-offline-sheet="' + url.path + '">\n' + css + '\n</style>'

    html = STYLESHEET.sub(inline_css, original)
    if len(found) < 4 or "/assets/site-core.css" not in found:
        raise ValueError("Expected committed page and core stylesheet: " + route)
    html = SCRIPT.sub("", html)
    html = PRELOAD.sub("", html)
    if html.count("</head>") != 1:
        raise ValueError("Ambiguous head in local page: " + route)
    # Make fragment arrival deterministic while retaining real layout rules.
    return html.replace("</head>", "<style>html{scroll-behavior:auto!important}</style></head>", 1)


def arrive(page, anchor: str) -> None:
    page.evaluate(
        """id => {
            const el = document.getElementById(id);
            if (!el) throw Error('Missing target '+id);
            location.hash = id;
            el.scrollIntoView({block:'start', behavior:'instant'});
        }""",
        anchor,
    )


def metrics(page, anchor: str) -> dict:
    return page.locator("#" + anchor).evaluate(
        """node => ({
            top: node.getBoundingClientRect().top,
            bottom: node.getBoundingClientRect().bottom,
            headerBottom: document.querySelector('.site-header').getBoundingClientRect().bottom,
            headerHeight: document.querySelector('.site-header').getBoundingClientRect().height,
            scrollWidth: document.documentElement.scrollWidth,
            viewportWidth: document.documentElement.clientWidth,
            visible: node.getBoundingClientRect().bottom > 0 &&
                     node.getBoundingClientRect().top < innerHeight
        })"""
    )


def assert_arrival(page, width: int, anchor: str) -> dict:
    result = metrics(page, anchor)
    assert result["visible"], (width, anchor, "outside viewport", result)
    assert result["top"] >= result["headerBottom"] - 2, (
        width, anchor, "obscured by sticky header", result
    )
    assert result["scrollWidth"] <= width + 1, (
        width, anchor, "horizontal document overflow", result
    )
    return result


def main() -> None:
    report = {"widths": list(WIDTHS), "complete_page_review_checks": 0,
              "keyboard_paths": 0, "destination_checks": 0,
              "blocked_asset_requests": 0, "network_responses": 0,
              "method": "committed full-page HTML and inlined CSS, no HTTP navigation"}
    with sync_playwright() as pw:
        launch = {"headless": True}
        if os.environ.get("CHROMIUM_PATH"):
            launch["executable_path"] = os.environ["CHROMIUM_PATH"]
        browser = pw.chromium.launch(**launch)
        try:
            for width in WIDTHS:
                context = browser.new_context(
                    viewport={"width": width, "height": 950},
                    java_script_enabled=False,
                    reduced_motion="reduce",
                    service_workers="block",
                )

                def block(route):
                    report["blocked_asset_requests"] += 1
                    route.abort()

                context.route("**/*", block)
                page = context.new_page()
                page.on("response", lambda _: report.__setitem__(
                    "network_responses", report["network_responses"] + 1
                ))
                for route, target, lesson in CASES:
                    page.set_content(local_document(route), wait_until="load")
                    page.evaluate("async () => { await document.fonts.ready; }")
                    arrive(page, target)
                    details = page.locator("#" + target)
                    summary = details.locator("summary")
                    link = details.locator("xpath=following-sibling::p[1]/a")
                    expect(summary).to_be_visible()
                    expect(link).to_be_visible()
                    assert not details.evaluate("el => el.open")
                    assert_arrival(page, width, target)
                    report["complete_page_review_checks"] += 1

                    # A backward keyboard Tab must find the actual summary.
                    link.focus()
                    page.keyboard.press("Shift+Tab")
                    expect(summary).to_be_focused()
                    assert summary.evaluate("el => el.matches(':focus-visible')")
                    page.keyboard.press("Enter")
                    assert details.evaluate("el => el.open")
                    style = details.evaluate(
                        """el => ({
                            padding: parseFloat(getComputedStyle(el.querySelector('p')).paddingLeft),
                            focus: getComputedStyle(el.querySelector('summary')).outlineStyle,
                            focusWidth: parseFloat(getComputedStyle(el.querySelector('summary')).outlineWidth),
                            parentFocus: el.closest('.poker-hand-review-check').matches(':focus-within')
                        })"""
                    )
                    assert style["padding"] >= 12 and style["focus"] == "solid", style
                    assert style["focusWidth"] >= 3 and style["parentFocus"], style
                    page.keyboard.press("Space")
                    assert not details.evaluate("el => el.open")
                    page.keyboard.press("Tab")
                    expect(link).to_be_focused()
                    assert link.evaluate("el => el.matches(':focus-visible')")
                    assert link.evaluate("el => el.getBoundingClientRect().height") >= 44
                    assert link.get_attribute("href") == lesson, (target, lesson)
                    report["keyboard_paths"] += 1

                    # Cross-page navigation is deliberately not faked: validate
                    # the real href, then render the committed destination page.
                    parsed = urlsplit(lesson)
                    page.set_content(local_document(parsed.path), wait_until="load")
                    page.evaluate("async () => { await document.fonts.ready; }")
                    arrive(page, parsed.fragment)
                    expect(page.locator("#" + parsed.fragment)).to_be_visible()
                    assert_arrival(page, width, parsed.fragment)
                    report["destination_checks"] += 1
                assert context.cookies() == []
                context.close()
        finally:
            browser.close()
    expected = len(WIDTHS) * len(CASES)
    assert all(report[key] == expected for key in (
        "complete_page_review_checks", "keyboard_paths", "destination_checks"
    )), report
    assert report["network_responses"] == 0, report
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
