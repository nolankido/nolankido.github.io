"""Local-only reader journey from Resources to Nolan Kido's creative work."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}'
errors = []
cases = []

try:
    with sync_playwright() as pw:
        options = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'):
            options['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**options)
        for javascript in [True, False]:
            context = browser.new_context(java_script_enabled=javascript)
            context.route('**/*', lambda route: route.continue_()
                          if urlsplit(route.request.url).hostname == '127.0.0.1'
                          else route.abort())
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))

            page.goto(base + '/resources/')
            card = page.locator('#resources-creative')
            expect(card.locator('.entry-links a')).to_have_count(2)
            expect(card.locator('.entry-links a').nth(0)).to_have_attribute('href', '/creative/')
            expect(card.locator('.entry-links a').nth(1)).to_have_attribute(
                'href', '/living-well/free-resources/creative-tools/')
            card.locator('a[href="/creative/"]').focus()
            page.keyboard.press('Enter')
            expect(page).to_have_url(base + '/creative/')
            expect(page.locator('h1')).to_be_visible()

            page.goto(base + '/resources/')
            direct = page.locator('#creative-work-resource-note a[href="/creative/#creative-brief-title"]')
            expect(direct).to_be_visible()
            direct.focus()
            page.keyboard.press('Enter')
            expect(page).to_have_url(base + '/creative/#creative-brief-title')
            heading = page.locator('#creative-brief-title')
            expect(heading).to_be_visible()
            expect(page.locator('#creative-brief-example')).to_be_visible()
            page.wait_for_timeout(400)  # Allow native smooth fragment scroll to settle.
            arrival = heading.evaluate('''el => {
              const rect = el.getBoundingClientRect();
              return {top: rect.top, bottom: rect.bottom, viewport: innerHeight};
            }''')
            assert 0 <= arrival['top'] < arrival['viewport'], (javascript, arrival)

            page.goto(base + '/resources/')
            outside = page.locator('#creative-work-resource-note a[href="/living-well/free-resources/books-creativity/"]')
            outside.focus()
            page.keyboard.press('Enter')
            expect(page).to_have_url(base + '/living-well/free-resources/books-creativity/')
            expect(page.locator('h1')).to_be_visible()

            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 900})
                page.goto(base + '/resources/')
                expect(page.locator('#resources-creative .entry-links a').nth(0)).to_be_visible()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (javascript, width)
                if width == 320 and javascript:
                    spacing = page.add_style_tag(content='''
                      html {font-size: 200% !important}
                      * {line-height: 1.5 !important; letter-spacing: .12em !important;
                         word-spacing: .16em !important}
                    ''')
                    overflows = page.evaluate('''() => ({
                      pageWidth: document.documentElement.scrollWidth,
                      viewportWidth: innerWidth,
                      bodyWidth: document.body.scrollWidth,
                      elements: Array.from(document.querySelectorAll('*'))
                        .map(el => ({tag: el.tagName, id: el.id,
                                     cls: String(el.className).slice(0, 70),
                                     right: Math.round(el.getBoundingClientRect().right),
                                     left: Math.round(el.getBoundingClientRect().left),
                                     scrollWidth: el.scrollWidth, clientWidth: el.clientWidth}))
                        .filter(el => el.right > innerWidth + 1 || el.left < -1 || el.scrollWidth > el.clientWidth + 2)
                        .slice(0, 15)
                    })''')
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (
                        javascript, width, 'enlarged text', overflows)
                    spacing.evaluate('(node) => node.remove()')
                if width == 390 and javascript and os.environ.get('SCREENSHOT_DIR'):
                    destination = Path(os.environ['SCREENSHOT_DIR'])
                    destination.mkdir(parents=True, exist_ok=True)
                    page.locator('#resources-creative').screenshot(path=str(destination / 'resources-creative-card.png'))
                assert page.evaluate('localStorage.length + sessionStorage.length') == 0
                assert context.cookies() == []
            cases.append({'javascript': javascript, 'keyboard_routes': 3, 'viewport_checks': 4})
            context.close()
        browser.close()

    assert not errors, errors
    print(json.dumps({'status': 'pass', 'cases': cases, 'page_errors': errors}, indent=2))
finally:
    server.shutdown()
    server.server_close()
