"""Offline browser reflow and link checks for standalone evidence summaries."""

import json
import os
from pathlib import Path

from playwright.sync_api import expect, sync_playwright
from standalone_search_sections_browser import BASE, request_handler


PAGES = (
    ("/technology/local-ai-gaming-laptop/", "laptop-snapshot-title",
     ("laptop-evidence", "laptop-measure")),
    ("/technology/review-reply-evidence-audit/", "reply-snapshot-title",
     ("reply-audit-source", "reply-audit-boundaries", "reply-audit-reproduce")),
)
ENLARGED = "html{font-size:200%!important}*{line-height:1.5!important;letter-spacing:.12em!important}"


def main():
    checked = 0
    linked = 0
    with sync_playwright() as pw:
        settings = {"headless": True}
        if os.environ.get("CHROMIUM_PATH"):
            settings["executable_path"] = os.environ["CHROMIUM_PATH"]
        browser = pw.chromium.launch(**settings)
        try:
            for enlarged in (False, True):
                for width in (320, 390, 768, 1440):
                    context = browser.new_context(viewport={"width": width, "height": 850},
                                                  reduced_motion="reduce", service_workers="block",
                                                  java_script_enabled=False)
                    context.route("**/*", request_handler())
                    page = context.new_page()
                    for path, title_id, anchor_ids in PAGES:
                        page.goto(BASE + path, wait_until="load")
                        if enlarged:
                            page.add_style_tag(content=ENLARGED)
                        snapshot = page.locator(".case-evidence-snapshot")
                        expect(snapshot).to_have_count(1)
                        expect(snapshot.get_by_role("heading", name="Evidence at a glance")).to_be_visible()
                        assert snapshot.get_attribute("aria-labelledby") == title_id
                        assert snapshot.locator("dt").count() == 3
                        metrics = snapshot.evaluate("""node => ({
                          width: node.getBoundingClientRect().width,
                          viewport: document.documentElement.clientWidth,
                          scroll: document.documentElement.scrollWidth,
                          navBefore: node.compareDocumentPosition(document.querySelector('.entry-jumps'))
                        })""")
                        assert metrics["scroll"] <= width + 1, (path, enlarged, width, metrics)
                        assert metrics["width"] <= metrics["viewport"] + 1, metrics
                        # DOCUMENT_POSITION_FOLLOWING = 4, so the summary precedes the jump links.
                        assert metrics["navBefore"] & 4, metrics
                        jump_style = page.locator('.entry-jumps').evaluate("""node => ({
                          display: getComputedStyle(node).display,
                          gap: getComputedStyle(node).columnGap,
                          firstHeight: parseFloat(getComputedStyle(node.querySelector('a')).minHeight)
                        })""")
                        assert jump_style['display'] == 'flex', (path, jump_style)
                        assert jump_style['gap'] != 'normal', (path, jump_style)
                        assert jump_style['firstHeight'] >= 44, (path, jump_style)
                        for anchor in anchor_ids:
                            link = snapshot.locator('a[href="#' + anchor + '"]')
                            expect(link).to_have_count(1)
                            assert page.locator('#' + anchor).count() == 1
                            linked += 1
                        if os.environ.get("SCREENSHOT_DIR") and width in (320, 1440) and not enlarged:
                            directory = Path(os.environ["SCREENSHOT_DIR"])
                            directory.mkdir(parents=True, exist_ok=True)
                            page.screenshot(path=str(directory / (title_id + "-" + str(width) + ".png")), full_page=False)
                        checked += 1
                    assert context.cookies() == []
                    context.close()
        finally:
            browser.close()
    print(json.dumps({"status": "pass", "page_layouts": checked, "evidence_links": linked,
                      "widths": [320, 390, 768, 1440], "enlarged_text": True,
                      "network": "offline intercepted fixtures"}))


if __name__ == "__main__":
    main()
