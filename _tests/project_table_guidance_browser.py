"""Local-only browser check for the project evidence tables on narrow screens."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "/technology/ai-book-continuity-checker/": (
        "continuity-benchmark-table-hint",
    ),
    "/technology/local-ai-review-replies/": (
        "reply-template-table-hint",
        "reply-model-table-hint",
    ),
}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_port}"
errors = []
writes = []
checks = []

try:
    with sync_playwright() as pw:
        options = {"headless": True}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        browser = pw.chromium.launch(**options)
        for javascript in (True, False):
            context = browser.new_context(java_script_enabled=javascript, reduced_motion="reduce")

            def route(request_route):
                request = request_route.request
                if request.method not in ("GET", "HEAD"):
                    writes.append(request.url)
                if urlsplit(request.url).hostname == "127.0.0.1":
                    request_route.continue_()
                else:
                    request_route.abort()

            context.route("**/*", route)
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            for width in (320, 390, 768, 1440):
                page.set_viewport_size({"width": width, "height": 900})
                for path, hints in CASES.items():
                    page.goto(base + path)
                    expect(page.locator("h1")).to_be_visible()
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (path, width)
                    for hint_id in hints:
                        note = page.locator(f"#{hint_id}")
                        expect(note).to_be_visible()
                        expect(note).to_contain_text("swipe sideways")
                        expect(note).to_contain_text("left or right arrow key")
                        region = page.locator(f'.project-table-scroll[aria-describedby="{hint_id}"]')
                        expect(region).to_have_attribute("tabindex", "0")
                        dimension = region.evaluate("node => ({client:node.clientWidth, scroll:node.scrollWidth})")
                        if width in (320, 390):
                            assert dimension["scroll"] > dimension["client"] + 50, (path, width, hint_id, dimension)
                            region.focus()
                            expect(region).to_be_focused()
                            page.keyboard.press("ArrowRight")
                            page.wait_for_function(
                                "selector => document.querySelector(selector).scrollLeft > 0",
                                arg=f'.project-table-scroll[aria-describedby="{hint_id}"]',
                            )
                            assert region.evaluate("node => node.scrollLeft") > 0
                        checks.append({"path": path, "hint": hint_id, "width": width,
                                       "javascript": javascript,
                                       "overflow": dimension["scroll"] > dimension["client"]})
                    page.emulate_media(media="print")
                    for hint_id in hints:
                        expect(page.locator(f"#{hint_id}")).to_be_hidden()
                    page.emulate_media(media="screen")
            assert context.cookies() == []
            assert page.evaluate("localStorage.length + sessionStorage.length") == 0
            context.close()
        browser.close()

    assert not writes, writes
    assert not errors, errors
    print(json.dumps({"status": "pass", "checked": len(checks), "widths": [320, 390, 768, 1440],
                      "keyboard_scrolls": sum(c["width"] in (320, 390) for c in checks),
                      "script_modes": [True, False], "page_errors": errors}, indent=2))
finally:
    server.shutdown()
    server.server_close()
