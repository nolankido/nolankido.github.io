#!/usr/bin/env python3
"""Offline Chromium verification of the self-contained sensitivity lab.

Run explicitly (or via local_release_checks.py --browser) after installing
Playwright and Chromium locally. Do not rely on GitHub Actions or a server.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source/poker/pot-odds-sensitivity-lab.html"
OUTPUT = ROOT / "downloads/poker-pot-odds-sensitivity-lab.html"


def main():
    html = SOURCE.read_text(encoding="utf-8")
    assert html == OUTPUT.read_text(encoding="utf-8"), "Source and public tool drifted"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for width in (320, 390, 768, 1280):
                page = browser.new_page(viewport={"width": width, "height": 900})
                errors, requests = [], []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.on("request", lambda req: requests.append(req.url))
                page.set_content(html, wait_until="load")
                assert page.locator("h1").inner_text() == "Pot odds sensitivity lab"
                assert page.locator("#river-low").is_enabled()
                assert "22% to 29%:" in page.locator("#river-result").inner_text()
                assert "-1.20 BB to +1.60 BB" in page.locator("#river-result").inner_text()
                assert "-0.50 BB" in page.locator("#raise-result").inner_text()
                assert "+0.40 BB" in page.locator("#bluff-result").inner_text()
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), width
                page.locator("#river-low").fill("35")
                page.locator("#river-high").fill("15")
                assert "15% to 35%" in page.locator("#river-result").inner_text()
                assert "-4.00 BB to +4.00 BB" in page.locator("#river-result").inner_text()
                assert "You reversed the bounds" in page.locator("#river-order-note").inner_text()
                page.locator("#raise-equity").fill("30")
                assert "+1.40 BB" in page.locator("#raise-result").inner_text()
                page.locator("#bluff-fold").fill("30")
                assert "-1.20 BB" in page.locator("#bluff-result").inner_text()
                page.locator("#raise-equity").fill("25")
                page.locator("#raise-equity").focus()
                page.keyboard.press("ArrowRight")
                assert page.locator("#raise-equity").input_value() == "26"
                assert "26%:" in page.locator("#raise-result").inner_text()
                assert not errors, (width, errors)
                assert not requests, (width, requests)
                page.close()
                print(f"PASS {width}px: calculations, keyboard, zero requests, no overflow")
            context = browser.new_context(java_script_enabled=False)
            page = context.new_page()
            page.set_content(html, wait_until="load")
            assert not page.locator("#river-low").is_enabled()
            assert page.locator("noscript").is_visible()
            assert "Interactive controls are unavailable" in page.locator("noscript").inner_text()
            assert "22% to 29%" in page.locator("#river-result").inner_text()
            context.close()
            print("PASS no-JavaScript fallback: clear static math and inactive controls")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
