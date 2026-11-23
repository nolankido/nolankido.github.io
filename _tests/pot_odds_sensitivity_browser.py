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
                # Test the independently calculated threshold drill with real controls.
                assert page.locator("#boundary-heading").is_visible()
                assert page.locator("[data-drill]").count() == 4
                assert page.locator("#bluff-fold").get_attribute("step") == "0.5"
                page.locator('[data-drill="river"]').click()
                assert page.locator("#river-low").input_value() == "24"
                assert page.locator("#river-high").input_value() == "26"
                assert "-0.40 BB to +0.40 BB" in page.locator("#river-result").inner_text()
                page.locator('[data-drill="raise-low"]').click()
                assert "-0.12 BB" in page.locator("#raise-result").inner_text()
                page.locator('[data-drill="raise-high"]').click()
                assert "+0.26 BB" in page.locator("#raise-result").inner_text()
                page.locator('[data-drill="bluff-zero"]').click()
                assert page.locator("#bluff-fold").input_value() == "37.5"
                assert "0.00 BB, at break-even" in page.locator("#bluff-result").inner_text()
                page.locator("#bluff-fold").press("ArrowRight")
                assert page.locator("#bluff-fold").input_value() == "38"
                assert "+0.08 BB" in page.locator("#bluff-result").inner_text()
                record = page.locator("#study-record")
                assert record.get_attribute("readonly") is not None
                assert "Selected lower 24%, upper 26%" in record.input_value()
                assert "Selected hypothetical showdown equity 27%" in record.input_value()
                assert "Selected hypothetical fold rate 38%" in record.input_value()
                assert "+0.08 BB" in record.input_value()
                assert "UNVERIFIED: No evidence" in record.input_value()
                assert page.locator("#study-select").is_enabled()
                page.locator("#study-select").click()
                assert record.evaluate("(e) => document.activeElement === e && e.selectionStart === 0 && e.selectionEnd === e.value.length")
                # Reset restores the original HTML defaults, all three results,
                # both copies of the study record and keyboard focus.
                reset = page.locator("#study-reset")
                assert reset.is_enabled()
                reset.click()
                for ident, expected in (
                    ("river-low", "22"), ("river-high", "29"),
                    ("raise-equity", "25"), ("bluff-fold", "40")):
                    assert page.locator("#" + ident).input_value() == expected
                assert page.locator("#river-low").is_focused()
                assert "-1.20 BB to +1.60 BB" in page.locator("#river-result").inner_text()
                assert "-0.50 BB" in page.locator("#raise-result").inner_text()
                assert "+0.40 BB" in page.locator("#bluff-result").inner_text()
                assert "Selected lower 22%, upper 29%" in record.input_value()
                assert "Selected hypothetical showdown equity 25%" in record.input_value()
                assert "Selected hypothetical fold rate 40%" in record.input_value()
                assert page.locator("#study-print").text_content() == record.input_value()
                page.emulate_media(media="print")
                assert reset.is_hidden()
                assert page.locator("#study-select").is_hidden()
                assert page.locator("#river-result").is_visible()
                # The scrollable textarea clips later lines in Chromium print.
                # A full, wrapping <pre> is the only printed copy.
                mirror = page.locator("#study-print")
                assert record.is_hidden()
                assert mirror.is_visible()
                assert mirror.text_content() == record.input_value()
                assert "3. PURE BLUFF" in mirror.text_content()
                assert "UNVERIFIED: No evidence" in mirror.text_content()
                assert mirror.evaluate("(e) => getComputedStyle(e).whiteSpace === 'pre-wrap' && getComputedStyle(e).overflowWrap === 'anywhere'")
                assert page.locator("#study-record-panel").evaluate("(e) => getComputedStyle(e).breakInside === 'auto'")
                page.emulate_media(media="screen")
                assert record.is_visible()
                assert mirror.is_hidden()
                assert not errors, (width, errors)
                assert not requests, (width, requests)
                page.close()
                print(f"PASS {width}px: calculations, keyboard, zero requests, no overflow")
            context = browser.new_context(java_script_enabled=False)
            page = context.new_page()
            page.set_content(html, wait_until="load")
            assert not page.locator("#river-low").is_enabled()
            assert page.locator('[data-drill="bluff-zero"]').is_disabled()
            assert page.locator("#study-select").is_disabled()
            assert page.locator("#study-reset").is_disabled()
            assert page.locator("#study-record").get_attribute("readonly") is not None
            assert "Selected lower 22%, upper 29%" in page.locator("#study-record").input_value()
            assert page.locator("#study-print").text_content() == page.locator("#study-record").input_value()
            page.emulate_media(media="print")
            assert page.locator("#study-print").is_visible()
            assert page.locator("#study-record").is_hidden()
            page.emulate_media(media="screen")
            assert page.locator("#boundary-heading").is_visible()
            assert page.locator("noscript").is_visible()
            assert "Interactive controls are unavailable" in page.locator("noscript").inner_text()
            assert "22% to 29%" in page.locator("#river-result").inner_text()
            context.close()
            print("PASS no-JavaScript fallback: clear static math and inactive controls")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
