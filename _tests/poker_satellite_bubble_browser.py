"""Optional local browser smoke for the Turn 12 satellite-bubble guide."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/poker/satellite-bubble-seat-equity/'


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0),
                                 partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    screenshots = Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if screenshots:
        screenshots.mkdir(parents=True, exist_ok=True)
    results = {'tested_widths': [], 'keyboard_reveals': 0,
               'inbound_arrivals': 0, 'works_without_javascript': False}
    errors = []
    try:
        with sync_playwright() as pw:
            args = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                args['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**args)
            context = browser.new_context()
            context.route('**/*', lambda request: request.continue_()
                          if urlsplit(request.request.url).hostname == '127.0.0.1'
                          else request.abort())
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            for width in (320, 390, 768, 1440):
                page.set_viewport_size({'width': width, 'height': 900})
                response = page.goto(origin + ROUTE)
                assert response and response.status == 200
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                expect(page.locator('h1')).to_contain_text('satellite bubble')
                expect(page.locator('details.viewer-question')).to_have_count(8)
                expect(page.locator('details.viewer-question[open]')).to_have_count(0)
                expect(page.locator('.short-stack-table[role="region"]')).to_have_count(3)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), width
                if screenshots and width in (390, 1440):
                    page.screenshot(path=str(screenshots / f'satellite-bubble-{width}.png'))
                for item in page.locator('details.viewer-question').all():
                    item.locator('summary').focus()
                    page.keyboard.press('Enter')
                    expect(item).to_have_attribute('open', '')
                    results['keyboard_reveals'] += 1
                page.add_style_tag(content='* {line-height:1.55!important;letter-spacing:.1em!important} p {margin-bottom:1.5em!important}')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), ('expanded text', width)
                results['tested_widths'].append(width)
            for source in ('/poker/tournament-formats/', '/poker/tournament-equity/',
                           '/poker/six-to-ten-bb-tournament-decisions/',
                           '/poker/short-stack-decisions/',
                           '/poker/choosing-a-tournament/',
                           '/poker/reading-preflop-charts/',
                           '/poker/practice-room/', '/poker/study/',
                           '/poker/library/', '/poker/find/'):
                page.goto(origin + source)
                link = page.locator('main a[href^="' + ROUTE + '"]').first
                expect(link).to_have_count(1)
                link.focus()
                page.keyboard.press('Enter')
                expect(page.locator('h1')).to_contain_text('satellite bubble')
                assert urlsplit(page.url).path == ROUTE, (source, page.url)
                results['inbound_arrivals'] += 1
            assert context.cookies() == []
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
            static = browser.new_context(java_script_enabled=False,
                                         viewport={'width': 320, 'height': 900})
            static.route('**/*', lambda request: request.continue_()
                         if urlsplit(request.request.url).hostname == '127.0.0.1'
                         else request.abort())
            nojs = static.new_page()
            response = nojs.goto(origin + ROUTE)
            assert response and response.status == 200
            expect(nojs.locator('details.viewer-question')).to_have_count(8)
            nojs.locator('details.viewer-question summary').first.focus()
            nojs.keyboard.press('Enter')
            expect(nojs.locator('details.viewer-question').first).to_have_attribute('open', '')
            assert nojs.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            results['works_without_javascript'] = True
            static.close()
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print('PASS: satellite lesson layout, link arrivals and answers checked in browser')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
