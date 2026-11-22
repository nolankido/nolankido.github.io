"""Offline keyboard and download journey test for the three primary reader intents.

Uses a loopback-only static server, the checked-in public HTML and real CSS.
Runs with and without site JavaScript at narrow and desktop viewport widths.
No third-party network, login, analytics, form submission or GitHub Actions.
A pass proves local browser interactions only, not live deployment or SEO growth.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
import urllib.request

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WIDTHS = (320, 390, 1440)
CASE = '/technology/checking-ai-website-changes/'
BOOK = '/books/one-workflow-at-a-time/'
POKER = '/poker/10bb/'
RESOURCES = (
    '/downloads/website-check-offline-runbook.md',
    '/downloads/one-workflow-ai-pilot-worksheet.md',
    '/downloads/ten-bb-tournament-checklist.md',
)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def keyboard_open(page, selector, destination):
    link = page.locator(selector).first
    expect(link).to_be_visible()
    link.focus()
    expect(link).to_be_focused()
    page.keyboard.press('Enter')
    expect(page).to_have_url(destination)
    expect(page.locator('main#main')).to_be_visible()
    expect(page.locator('h1')).to_be_visible()


def keyboard_download(page, route, filename):
    link = page.locator(f'main a[href="{route}"][download]').first
    expect(link).to_be_visible()
    link.focus()
    expect(link).to_be_focused()
    with page.expect_download() as event:
        page.keyboard.press('Enter')
    download = event.value
    assert download.suggested_filename == filename, (
        route, download.suggested_filename)
    assert download.failure() is None, (route, download.failure())
    return True


def read_resource(base, route):
    file = ROOT / route.lstrip('/')
    assert file.is_file(), ('missing locally published download', route)
    with urllib.request.urlopen(base + route, timeout=10) as response:
        assert response.status == 200, (route, response.status)
        body = response.read()
    expected = file.read_bytes()
    assert body and body == expected, ('download differs from checked-in bytes', route)
    return len(body)


def check_reflow(page, route, width):
    state = page.evaluate('''() => ({
      viewport: innerWidth,
      scroll: document.documentElement.scrollWidth,
      skip: !!document.querySelector('a.skip-link[href="#main"]')
    })''')
    assert state['viewport'] == width, (route, width, state)
    assert state['scroll'] <= width + 1, (route, width, 'horizontal overflow', state)
    assert state['skip'], (route, 'missing skip link')


def main():
    for route in (CASE, BOOK, POKER, '/', '/start-here/', '/books/', '/poker/'):
        public = ROOT / route.lstrip('/') / 'index.html'
        assert public.is_file(), ('missing required HTML route', route)
    for route in RESOURCES:
        assert (ROOT / route.lstrip('/')).is_file(), route

    server = ThreadingHTTPServer(
        ('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    results = {'browser_paths': 0, 'keyboard_downloads': 0,
               'exact_local_resource_gets': 0,
               'script_modes': ['disabled', 'enabled'],
               'viewports': list(WIDTHS)}
    try:
        for resource in RESOURCES:
            read_resource(base, resource)
            results['exact_local_resource_gets'] += 1

        with sync_playwright() as pw:
            launch = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                launch['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**launch)
            try:
                for scripts_enabled in (False, True):
                    context = browser.new_context(
                        java_script_enabled=scripts_enabled,
                        accept_downloads=True, reduced_motion='reduce')
                    # Permit only this loopback server. Fail closed on every
                    # Google font, analytics, other domain or remote request.
                    context.route('**/*', lambda route: route.continue_()
                                  if urlsplit(route.request.url).hostname == '127.0.0.1'
                                  else route.abort())
                    page = context.new_page()
                    page.set_default_timeout(12000)
                    try:
                        for width in WIDTHS:
                            page.set_viewport_size({'width': width, 'height': 900})

                            # Journey 1a: Home -> documented AI repair -> free runbook.
                            page.goto(base + '/', wait_until='domcontentloaded')
                            check_reflow(page, '/', width)
                            keyboard_open(
                                page,
                                f'main a[href="{CASE}"]',
                                base + CASE)
                            check_reflow(page, CASE, width)
                            keyboard_download(page, RESOURCES[0],
                                              'website-check-offline-runbook.md')
                            results['keyboard_downloads'] += 1
                            results['browser_paths'] += 1

                            # Journey 1b: Start Here -> the same source-backed case.
                            page.goto(base + '/start-here/', wait_until='domcontentloaded')
                            check_reflow(page, '/start-here/', width)
                            keyboard_open(
                                page,
                                f'main .start-release-proof a[href="{CASE}"]',
                                base + CASE)
                            results['browser_paths'] += 1

                            # Journey 2: Books -> actual author book -> free worksheet.
                            page.goto(base + '/books/', wait_until='domcontentloaded')
                            check_reflow(page, '/books/', width)
                            keyboard_open(
                                page,
                                f'main a[href="{BOOK}"]',
                                base + BOOK)
                            check_reflow(page, BOOK, width)
                            keyboard_download(page, RESOURCES[1],
                                              'one-workflow-ai-pilot-worksheet.md')
                            results['keyboard_downloads'] += 1
                            results['browser_paths'] += 1

                            # Journey 3: Poker hub -> written 10 BB guide -> worksheet.
                            page.goto(base + '/poker/', wait_until='domcontentloaded')
                            check_reflow(page, '/poker/', width)
                            keyboard_open(
                                page,
                                'main a[href="/poker/10bb/#practice-title"]',
                                base + POKER + '#practice-title')
                            check_reflow(page, POKER, width)
                            expect(page.locator('#practice-title')).to_be_visible()
                            keyboard_download(page, RESOURCES[2],
                                              'ten-bb-tournament-checklist.md')
                            results['keyboard_downloads'] += 1
                            results['browser_paths'] += 1
                    finally:
                        context.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    results['status'] = 'pass'
    results['scope'] = 'loopback-only browser with real checked-in HTML, CSS and downloads'
    print(json.dumps(results, sort_keys=True))


if __name__ == '__main__':
    main()
