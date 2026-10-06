"""Targeted offline reading and native-disclosure checks; no real analytics events."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright, expect
from browser import html_for

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ['pot-odds-workshop', 'short-stack-decisions', 'tournament-equity', 'range-combinations', 'variance-and-results', 'hand-to-vlog', 'practice-room']

def main():
    with sync_playwright() as pw:
        options = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'): options['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**options)
        context = browser.new_context()
        context.route('**/*', lambda route: route.abort())
        page = context.new_page(); errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        checks = 0
        for width in [320, 390, 768, 1440]:
            page.set_viewport_size({'width': width, 'height': 900})
            for slug in SLUGS:
                page.set_content(html_for('/poker/' + slug + '/'))
                expect(page.locator('h1')).to_have_count(1)
                expect(page.locator('main')).to_be_visible()
                assert page.locator('form').count() == 0
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (slug, width)
                checks += 1
        page.set_viewport_size({'width': 390, 'height': 900})
        page.set_content(html_for('/poker/practice-room/'))
        panels = page.locator('details.workshop-question')
        expect(panels).to_have_count(12)
        for index in range(12):
            panel = panels.nth(index)
            assert panel.get_attribute('open') is None
            summary = panel.locator('summary')
            summary.focus(); summary.press('Enter')
            expect(panel).to_have_attribute('open', '')
            expect(panel.locator('div')).to_be_visible()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            summary.press('Enter')
            assert panel.get_attribute('open') is None
        # Content and native controls still work with JavaScript disabled.
        nojs = browser.new_context(java_script_enabled=False)
        nojs.route('**/*', lambda route: route.abort())
        static = nojs.new_page()
        static.set_content(html_for('/poker/practice-room/'))
        first = static.locator('details.workshop-question').first
        first.locator('summary').click()
        expect(first.locator('div')).to_be_visible()
        nojs.close()
        assert errors == [], errors
        context.close(); browser.close()
    print(f'PASS: {checks} workshop page/viewport checks; 12 keyboard-open/close answers; no-JavaScript reading; all external requests blocked.')

if __name__ == '__main__': main()
