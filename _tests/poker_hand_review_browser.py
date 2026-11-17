"""Offline Chromium QA for hand-review mobile, keyboard and guide journeys.

Run manually on a checked-out site. All requests are intercepted, no external
scripts, media, cookies or services. No GitHub Actions or background scheduler.
"""
from __future__ import annotations

import json
import os


from playwright.sync_api import expect, sync_playwright

from standalone_search_sections_browser import BASE, request_handler

CASES = (
    (
        "/poker/episodes/portland-meadows-ep1/",
        "hand-64o-review",
        "/poker/six-to-ten-bb-tournament-decisions/#bridge-sb",
    ),
    (
        "/poker/episodes/portland-meadows-ep1/",
        "hand-77-review",
        "/poker/short-stack-decisions/#depths",
    ),
    (
        "/poker/episodes/portland-meadows-standoff/",
        "standoff-second-review",
        "/poker/short-stack-decisions/#icm-call",
    ),
)


def layout(page, width, details, summary, next_link):
    metrics = details.evaluate(
        """e => ({
          open: e.open,
          scrollWidth: document.documentElement.scrollWidth,
          viewport: document.documentElement.clientWidth,
          answerPadding: parseFloat(getComputedStyle(e.querySelector('p')).paddingLeft),
          summaryHeight: e.querySelector('summary').getBoundingClientRect().height,
          summaryOutline: getComputedStyle(e.querySelector('summary')).outlineStyle,
          summaryOutlineWidth: parseFloat(getComputedStyle(e.querySelector('summary')).outlineWidth),
          scrollMargin: parseFloat(getComputedStyle(e).scrollMarginTop),
          targeted: e.matches(':target'),
          targetShadow: getComputedStyle(e).boxShadow,
          containerFocusWithin: e.closest('.poker-hand-review-check').matches(':focus-within'),
          containerOutlineWidth: parseFloat(getComputedStyle(e.closest('.poker-hand-review-check')).outlineWidth),
          summaryFocusVisible: e.querySelector('summary').matches(':focus-visible')
        })"""
    )
    link = next_link.evaluate(
        "e => ({height:e.getBoundingClientRect().height,"
        "width:e.getBoundingClientRect().width,"
        "outline:getComputedStyle(e).outlineStyle})"
    )
    assert metrics["open"], (width, page.url, metrics)
    assert metrics["summaryHeight"] >= 44, (width, page.url, metrics)
    assert metrics["summaryFocusVisible"], (width, page.url, "summary not keyboard focused", metrics)
    assert metrics["summaryOutline"] == "solid" and metrics["summaryOutlineWidth"] >= 3, metrics
    assert metrics["containerFocusWithin"] and metrics["containerOutlineWidth"] >= 2, metrics
    assert metrics["answerPadding"] >= 12, (width, page.url, metrics)
    assert metrics["scrollMargin"] >= 100, metrics
    assert metrics["targeted"] and metrics["targetShadow"] != "none", metrics
    assert metrics["scrollWidth"] <= width + 1, (width, page.url, metrics)
    assert link["height"] >= 44 and link["width"] >= 44, (width, page.url, link)
    return {"width": width, "answer_padding": metrics["answerPadding"],
            "link_height": link["height"], "focus_outline": metrics["summaryOutlineWidth"]}


def anchor_arrival(page, width, details):
    placement = details.evaluate("""e => ({
        top: e.getBoundingClientRect().top,
        headerBottom: document.querySelector('.site-header').getBoundingClientRect().bottom,
        scrollWidth: document.documentElement.scrollWidth,
        visible: e.getBoundingClientRect().bottom > 0 && e.getBoundingClientRect().top < innerHeight
    })""")
    assert placement["visible"] and placement["top"] >= placement["headerBottom"] - 2, (
        width, page.url, "fragment hidden behind site header", placement
    )
    assert placement["scrollWidth"] <= width + 1, (width, page.url, placement)
    return placement


def main() -> None:
    report = {"viewports": [], "keyboard_disclosures": 0, "lesson_journeys": 0,
              "keyboard_tab_arrivals": 0, "header_safe_arrivals": 0,
              "external_requests": 0}
    with sync_playwright() as pw:
        launch = {"headless": True}
        if os.environ.get("CHROMIUM_PATH"):
            launch["executable_path"] = os.environ["CHROMIUM_PATH"]
        browser = pw.chromium.launch(**launch)
        try:
            for width in (320, 390, 768, 1440):
                context = browser.new_context(
                    viewport={"width": width, "height": 950},
                    java_script_enabled=False,
                    reduced_motion="reduce",
                    service_workers="block",
                )
                context.route("**/*", request_handler())
                page = context.new_page()
                page.on(
                    "request",
                    lambda request: report.__setitem__(
                        "external_requests", report["external_requests"] +
                        int(not request.url.startswith(BASE + "/"))
                    ),
                )
                for route, target, lesson in CASES:
                    page.goto(BASE + route + "#" + target, wait_until="load")
                    details = page.locator("#" + target)
                    summary = details.locator("summary")
                    next_link = details.locator("xpath=following-sibling::p[1]/a")
                    expect(summary).to_be_visible()
                    expect(next_link).to_be_visible()
                    assert not details.evaluate("e => e.open")
                    anchor_arrival(page, width, details)
                    report["header_safe_arrivals"] += 1
                    # Seed the next known tabbable control, then test a real
                    # backwards Tab rather than assuming scripted .focus()
                    # proves keyboard focus order or :focus-visible styling.
                    next_link.focus()
                    expect(next_link).to_be_focused()
                    page.keyboard.press("Shift+Tab")
                    expect(summary).to_be_focused()
                    assert summary.evaluate("e => e.matches(':focus-visible')"), (
                        width, page.url, target, "summary lacks keyboard focus visibility"
                    )
                    report["keyboard_tab_arrivals"] += 1
                    page.keyboard.press("Enter")
                    result = layout(page, width, details, summary, next_link)
                    report["viewports"].append(result)
                    page.keyboard.press("Space")
                    assert not details.evaluate("e => e.open"), (width, target, "Space failed")
                    report["keyboard_disclosures"] += 1
                    # Forward Tab must reach the next-study link in DOM order.
                    page.keyboard.press("Tab")
                    expect(next_link).to_be_focused()
                    assert next_link.evaluate("e => e.matches(':focus-visible')")
                    assert next_link.evaluate("e => getComputedStyle(e).outlineStyle") == "solid"
                    page.keyboard.press("Enter")
                    expect(page).to_have_url(BASE + lesson)
                    destination = page.locator("#" + lesson.split("#", 1)[1])
                    expect(destination).to_be_visible()
                    assert page.evaluate("document.documentElement.scrollWidth") <= width + 1
                    report["lesson_journeys"] += 1
                assert context.cookies() == []
                context.close()
        finally:
            browser.close()
    assert all(report[key] == 12 for key in (
        "keyboard_disclosures", "lesson_journeys",
        "keyboard_tab_arrivals", "header_safe_arrivals"
    )), report
    assert report["external_requests"] == 0, report
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
