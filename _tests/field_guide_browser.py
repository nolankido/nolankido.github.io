"""Read-only local browser checks for field-guide routes, reflow and printable sheets."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import os
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ('first-live-tournament', 'choosing-a-tournament', 'registration-and-reentry', 'tournament-day', 'recording-hands', 'choosing-study-tools', 'evaluating-poker-advice')

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
    def copyfile(self, source, outputfile):
        try: super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError): pass

def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    screenshots = Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if screenshots: screenshots.mkdir(parents=True, exist_ok=True)
    errors = []
    try:
        with sync_playwright() as pw:
            opts = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'): opts['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**opts)
            context = browser.new_context()
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = context.new_page()
            page.on('pageerror', lambda err: errors.append(str(err)))
            routes = list(GUIDES) + ['live-tournament-guide', 'tournament-checklists']
            for width in [320, 390, 768, 1280]:
                page.set_viewport_size({'width': width, 'height': 900})
                for slug in routes:
                    response = page.goto(origin + '/poker/' + slug + '/')
                    assert response and response.status == 200, slug
                    assert page.locator('h1').count() == 1, slug
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (slug, width)
                    assert page.locator('main form, main input, main textarea, main iframe').count() == 0, slug
                    if width in [390, 1280] and slug in ['live-tournament-guide', 'choosing-a-tournament', 'tournament-checklists'] and screenshots:
                        page.screenshot(path=str(screenshots / f'poker-field-{slug}-{width}.png'), full_page=True)
            page.goto(origin + '/poker/library/')
            page.locator('[data-filter="live"]').click()
            expect(page.locator('#library-grid a[href="/poker/first-live-tournament/"]')).to_be_visible()
            page.locator('#library-search').fill('reentry')
            expect(page.locator('#library-grid a[href="/poker/registration-and-reentry/"]')).to_be_visible()
            page.locator('#library-reset').click()
            page.goto(origin + '/poker/registration-and-reentry/')
            answer = page.locator('details.viewer-question')
            assert answer.count() == 1
            expect(answer.locator('div')).not_to_be_visible()
            answer.locator('summary').focus()
            page.keyboard.press('Enter')
            expect(answer.locator('div')).to_be_visible()
            page.goto(origin + '/poker/tournament-checklists/')
            page.emulate_media(media='print')
            expect(page.locator('pre.field-sheet:visible')).to_have_count(3)
            for sheet in page.locator('pre.field-sheet').all():
                assert sheet.inner_text().strip().startswith('# ')
                assert sheet.evaluate('(el) => el.scrollWidth <= el.clientWidth + 1')
            assert context.cookies() == []
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
            offline = browser.new_context(java_script_enabled=False)
            offline.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            static = offline.new_page()
            static.goto(origin + '/poker/live-tournament-guide/')
            for slug in GUIDES:
                assert static.locator('a[href="/poker/' + slug + '/"]').count() >= 1
            static.goto(origin + '/poker/tournament-checklists/')
            expect(static.locator('pre.field-sheet')).to_have_count(3)
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print('PASS: nine new routes at four widths; discovery, keyboard disclosure, print, no-JS and privacy checks.')

if __name__ == '__main__': main()
