"""Offline 320 px to desktop verification for the NolanPoker video chooser.

All network requests are intercepted. No YouTube media, analytics or cookies
are loaded, and native fragment navigation works with JavaScript disabled.
"""
from __future__ import annotations

import json
import os

from playwright.sync_api import expect, sync_playwright

from standalone_search_sections_browser import BASE, request_handler

CHOICES = (
    "nolanpoker-deepstack",
    "nolanpoker-standoff",
    "nolanpoker-south-point",
)


def main() -> None:
    report = {"viewport_checks": 0, "keyboard_arrivals": 0, "external_requests": 0}
    with sync_playwright() as pw:
        options = {"headless": True}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        browser = pw.chromium.launch(**options)
        try:
            for width in (320, 390, 768, 1440):
                context = browser.new_context(
                    viewport={"width": width, "height": 950},
                    java_script_enabled=False,
                    reduced_motion="reduce",
                    service_workers="block",
                )
                requests: list[str] = []
                context.route("**/*", request_handler())
                page = context.new_page()
                page.on("request", lambda request: requests.append(request.url))
                page.goto(BASE + "/poker/", wait_until="load")
                expect(page.locator(".poker-video-chooser a")).to_have_count(3)
                assert page.evaluate("document.documentElement.scrollWidth") <= width + 1
                assert page.locator(".poker-video-chooser").is_visible()
                report["viewport_checks"] += 1
                for target_id in CHOICES:
                    page.goto(BASE + "/poker/", wait_until="load")
                    link = page.locator('.poker-video-chooser a[href="#' + target_id + '"]')
                    expect(link).to_be_visible()
                    size = link.evaluate(
                        "node => ({height: node.getBoundingClientRect().height,"
                        " width: node.getBoundingClientRect().width})"
                    )
                    assert size["height"] >= 44 and size["width"] > 44, (width, target_id, size)
                    link.focus()
                    expect(link).to_be_focused()
                    page.keyboard.press("Enter")
                    expect(page).to_have_url(BASE + "/poker/#" + target_id)
                    card = page.locator("#" + target_id)
                    expect(card).to_be_in_viewport()
                    metrics = card.evaluate(
                        "node => ({top: node.getBoundingClientRect().top,"
                        " header: document.querySelector('.site-header').getBoundingClientRect().bottom,"
                        " outline: getComputedStyle(node).outlineStyle})"
                    )
                    assert metrics["top"] >= metrics["header"] - 2, (width, target_id, metrics)
                    assert metrics["outline"] == "solid", (width, target_id, metrics)
                    assert page.evaluate("document.documentElement.scrollWidth") <= width + 1
                    report["keyboard_arrivals"] += 1
                assert all(url.startswith(BASE + "/") for url in requests), requests
                assert context.cookies() == []
                context.close()
        finally:
            browser.close()
    print(json.dumps(report))


if __name__ == "__main__":
    main()
