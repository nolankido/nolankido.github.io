"""Offline, full-content viewport QA for script-free poker practice reading views.

Reads committed HTML, no fake HTTPS origin or local web server. Requests are
aborted. Uses installed Chromium when the Playwright-managed browser is absent.
Manual run: python _tests/poker_review_readable_browser.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ROUTES = (
    ("downloads/poker-hand-review-practice-01.html", "questions"),
    ("downloads/poker-hand-review-practice-01-key.html", "checking_key"),
)
WIDTHS = (320, 390, 768, 1440)


def executable() -> str | None:
    configured = os.environ.get("CHROMIUM_PATH")
    if configured:
        if not Path(configured).is_file():
            raise FileNotFoundError("CHROMIUM_PATH does not exist: " + configured)
        return configured
    return (shutil.which("chromium") or shutil.which("chromium-browser") or
            shutil.which("google-chrome") or shutil.which("google-chrome-stable"))


def dimensions(page) -> dict:
    return page.evaluate("""() => ({
        pageWidth: document.documentElement.scrollWidth,
        viewportWidth: document.documentElement.clientWidth,
        contentWidth: document.querySelector('.practice-doc').getBoundingClientRect().width,
        maxCardRight: Math.max(0, ...Array.from(document.querySelectorAll('.audit-card'),
                    el => el.getBoundingClientRect().right)),
        minCardLeft: Math.min(innerWidth, ...Array.from(document.querySelectorAll('.audit-card'),
                    el => el.getBoundingClientRect().left))
    })""")


def main() -> None:
    report = {"sizes": list(WIDTHS), "full_page_layout_checks": 0,
              "reader_focus_checks": 0, "five_checkbox_checks": 0,
              "return_to_questions": 0, "blocked_asset_requests": 0,
              "network_responses": 0, "method": "actual committed HTML, offline in-memory Chromium"}
    with sync_playwright() as pw:
        launch = {"headless": True}
        local_chromium = executable()
        if local_chromium:
            launch["executable_path"] = local_chromium
        report["browser_executable"] = local_chromium or "Playwright managed default"
        browser = pw.chromium.launch(**launch)
        try:
            for width in WIDTHS:
                ctx = browser.new_context(
                    viewport={"width": width, "height": 900},
                    java_script_enabled=False,
                    reduced_motion="reduce",
                    service_workers="block",
                )

                def abort(route):
                    report["blocked_asset_requests"] += 1
                    route.abort()

                ctx.route("**/*", abort)
                page = ctx.new_page()
                page.on("response", lambda _: report.__setitem__(
                    "network_responses", report["network_responses"] + 1))
                for file, kind in ROUTES:
                    page.set_content((ROOT / file).read_text(encoding="utf-8"), wait_until="load")
                    expect(page.locator("main h1")).to_be_visible()
                    expect(page.locator("main h2")).to_have_count(8 if kind == "questions" else 7)
                    layout = dimensions(page)
                    assert layout["pageWidth"] <= width + 1, (
                        width, kind, "horizontal document overflow", layout)
                    assert layout["contentWidth"] <= width + 1, (
                        width, kind, "article not responsive", layout)
                    if kind == "questions":
                        expect(page.locator(".audit-card")).to_have_count(0)
                        expect(page.locator(
                            'article a[href="/downloads/poker-hand-review-practice-01-key.html"]'
                        )).to_have_count(1)
                        expect(page.locator(
                            '.actions a[href="/downloads/poker-hand-review-practice-01.md"]'
                        )).to_have_count(1)
                    else:
                        expect(page.locator(".audit-card")).to_have_count(14)
                        assert layout["maxCardRight"] <= width + 1, (width, kind, layout)
                        assert layout["minCardLeft"] >= -1, (width, kind, layout)
                        expect(page.locator("input[type=checkbox]")).to_have_count(5)
                        expect(page.locator(
                            '.actions a[href="/downloads/poker-hand-review-practice-01.html"]'
                        )).to_be_visible()
                        page.locator("input[type=checkbox]").first.check()
                        assert page.locator("input[type=checkbox]").first.is_checked()
                        report["five_checkbox_checks"] += 1
                        report["return_to_questions"] += 1

                    # True Tab transition, not just a scripted focus assertion.
                    top = page.locator(".top nav a")
                    expect(top).to_have_count(2)
                    top.first.focus()
                    page.keyboard.press("Tab")
                    expect(top.nth(1)).to_be_focused()
                    assert top.nth(1).evaluate(
                        "e => getComputedStyle(e).outlineStyle") == "solid"
                    report["reader_focus_checks"] += 1
                    report["full_page_layout_checks"] += 1

                    if os.environ.get("SCREENSHOT_DIR") and width in (320, 390):
                        dest = Path(os.environ["SCREENSHOT_DIR"])
                        dest.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(dest / f"practice-reader-{kind}-{width}.png"),
                                        full_page=True)
                assert ctx.cookies() == []
                ctx.close()
        finally:
            browser.close()
    assert report["full_page_layout_checks"] == 8, report
    assert report["reader_focus_checks"] == 8, report
    assert report["five_checkbox_checks"] == 4, report
    assert report["return_to_questions"] == 4, report
    assert report["network_responses"] == 0, report
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
