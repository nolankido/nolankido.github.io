"""Local browser QA for the Turn 11 6–10 BB lesson, if Chromium can start."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/poker/six-to-ten-bb-tournament-decisions/'


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0),
                                 partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    shots = Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    results = {'widths': [], 'keyboard_answers': 0,
               'linked_arrivals': 0, 'no_javascript': False}
    errors = []
    try:
        with sync_playwright() as pw:
            options = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                options['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**options)
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
                expect(page.locator('h1')).to_contain_text('Six to ten big blinds')
                expect(page.locator('details.viewer-question')).to_have_count(9)
                expect(page.locator('details.viewer-question[open]')).to_have_count(0)
                expect(page.locator('div.short-stack-table[role="region"]')).to_have_count(3)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), ('initial', width)
                if shots and width in (390, 1440):
                    page.screenshot(path=str(shots / f'six-to-ten-bb-{width}.png'))
                for item in page.locator('details.viewer-question').all():
                    item.locator('summary').focus()
                    page.keyboard.press('Enter')
                    expect(item).to_have_attribute('open', '')
                    results['keyboard_answers'] += 1
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), ('answers', width)
                page.add_style_tag(content='* {line-height:1.55!important;letter-spacing:.1em!important} p {margin-bottom:1.5em!important}')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), ('large text', width)
                results['widths'].append(width)
            for source in ('/poker/three-to-five-bb-tournament-decisions/',
                           '/poker/short-stack-decisions/',
                           '/poker/facing-preflop-raises/',
                           '/poker/blind-defense/',
                           '/poker/reading-preflop-charts/',
                           '/poker/tournament-equity/',
                           '/poker/position-and-stacks/',
                           '/poker/library/', '/poker/find/'):
                page.goto(origin + source)
                link = page.locator('main a[href^="' + ROUTE + '"]').first
                expect(link).to_have_count(1)
                link.focus()
                page.keyboard.press('Enter')
                expect(page.locator('h1')).to_contain_text('Six to ten big blinds')
                assert urlsplit(page.url).path == ROUTE, (source, page.url)
                results['linked_arrivals'] += 1
            assert context.cookies() == []
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
            offline = browser.new_context(java_script_enabled=False,
                                          viewport={'width': 320, 'height': 900})
            offline.route('**/*', lambda request: request.continue_()
                          if urlsplit(request.request.url).hostname == '127.0.0.1'
                          else request.abort())
            static = offline.new_page()
            response = static.goto(origin + ROUTE)
            assert response and response.status == 200
            expect(static.locator('details.viewer-question')).to_have_count(9)
            static.locator('details.viewer-question summary').first.focus()
            static.keyboard.press('Enter')
            expect(static.locator('details.viewer-question').first).to_have_attribute('open', '')
            assert static.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            results['no_javascript'] = True
            offline.close()
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print('PASS: 6–10 BB lesson reflows, reveals answers and links without external services.')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
