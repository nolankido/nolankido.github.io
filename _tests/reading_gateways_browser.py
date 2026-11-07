"""Local-only checks for Start Here and Writing at large text sizes."""
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
            layout_checks = 0
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 900})
                for path in ['/start-here/', '/notes/']:
                    page.goto(base + path)
                    expect(page.locator('h1')).to_be_visible()
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (
                        javascript, width, path, 'normal text')
                    if width == 320 and javascript:
                        enlarged = page.add_style_tag(content='''
                          html { font-size: 200% !important; }
                          * { line-height: 1.5 !important; letter-spacing: .12em !important;
                              word-spacing: .16em !important; }
                        ''')
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (
                            javascript, width, path, 'enlarged text')
                        links = page.evaluate('''() => Array.from(document.querySelectorAll('.nav-links li'))
                          .map(li => ({label: li.textContent.trim(), available: li.clientWidth,
                                       required: li.scrollWidth}))''')
                        assert all(link['required'] <= link['available'] + 1 for link in links), (
                            javascript, width, path, 'overlapping navigation labels', links)
                        enlarged.evaluate('(node) => node.remove()')
                    layout_checks += 1

            page.goto(base + '/start-here/')
            notes_link = page.locator('a[href="/notes/"]').first
            notes_link.focus()
            page.keyboard.press('Enter')
            expect(page).to_have_url(base + '/notes/')

            topic = page.locator('nav[aria-label="Writing topics"] a[href="#technology"]')
            topic.focus()
            page.keyboard.press('Enter')
            expect(page).to_have_url(base + '/notes/#technology')
            expect(page.locator('#technology')).to_be_visible()

            essay = page.locator('#technology a[href="/notes/keep-the-judgment/"]').first
            essay.focus()
            page.keyboard.press('Enter')
            expect(page).to_have_url(base + '/notes/keep-the-judgment/')
            expect(page.locator('h1')).to_be_visible()

            assert page.evaluate('localStorage.length + sessionStorage.length') == 0
            assert context.cookies() == []
            cases.append({'javascript': javascript, 'layout_checks': layout_checks,
                          'keyboard_routes': 3})
            context.close()
        context = browser.new_context(viewport={'width': 320, 'height': 900},
                                      reduced_motion='reduce')
        context.route('**/*', lambda route: route.continue_()
                      if urlsplit(route.request.url).hostname == '127.0.0.1'
                      else route.abort())
        page = context.new_page()
        for path, selector, target in [
            ('/start-here/', 'a[href="#start-routes-title"]', '#start-routes-title'),
            ('/notes/', 'nav[aria-label="Writing topics"] a[href="#technology"]', '#technology'),
        ]:
            page.goto(base + path)
            page.add_style_tag(content='''
              html { font-size: 200% !important; }
              * { line-height: 1.5 !important; letter-spacing: .12em !important;
                  word-spacing: .16em !important; }
            ''')
            page.locator(selector).first.focus()
            page.keyboard.press('Enter')
            expect(page).to_have_url(base + path + target)
            position = page.evaluate('''selector => {
              const header = document.querySelector('.site-header').getBoundingClientRect();
              const heading = document.querySelector(selector).getBoundingClientRect();
              return {headerBottom: header.bottom, targetTop: heading.top};
            }''', target)
            assert position['targetTop'] >= position['headerBottom'] - 1, (
                path, target, position)
        context.close()
        browser.close()
    assert not errors, errors
    print(json.dumps({'status': 'pass', 'cases': cases,
                      'enlarged_fragment_arrivals': 2, 'page_errors': errors}, indent=2))
finally:
    server.shutdown()
    server.server_close()
