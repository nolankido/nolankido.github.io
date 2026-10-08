"""Local HTTP checks for collection discovery and narrow-screen teaching examples."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import os
from playwright.sync_api import sync_playwright, expect
ROOT = Path(__file__).resolve().parents[1]
SLUGS = ('resource-collections', 'free-poker-learning-path', 'cash-game-study', 'omaha-and-mixed-games', 'poker-books-and-courses', 'poker-research-guide')
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    screenshots = Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    errors = []
    if screenshots: screenshots.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as pw:
            opts = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'): opts['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**opts)
            context = browser.new_context()
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = context.new_page(); page.on('pageerror', lambda e: errors.append(str(e)))
            for width in (320, 390, 768, 1280):
                page.set_viewport_size({'width': width, 'height': 900})
                for slug in SLUGS:
                    response = page.goto(origin + '/poker/' + slug + '/')
                    assert response and response.status == 200
                    expect(page.locator('h1')).to_have_count(1)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (slug, width)
                    page.add_style_tag(content='* {line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important;} p {margin-bottom:2em!important;}')
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), ('spacing', slug, width)
                    if screenshots and width in (390, 1280) and slug in ('resource-collections', 'omaha-and-mixed-games'):
                        page.screenshot(path=str(screenshots / f'poker-collections-{slug}-{width}.png'), full_page=True)
            page.goto(origin + '/poker/resource-collections/')
            for slug in SLUGS[1:]:
                expect(page.locator('main a[href="/poker/' + slug + '/"]').first).to_be_visible()
            for slug in SLUGS[1:]:
                page.goto(origin + '/poker/' + slug + '/')
                panel = page.locator('details.viewer-question')
                expect(panel.locator('div')).not_to_be_visible()
                panel.locator('summary').focus(); page.keyboard.press('Enter')
                expect(panel.locator('div')).to_be_visible()
                page.keyboard.press('Enter'); expect(panel.locator('div')).not_to_be_visible()
                page.emulate_media(media='print')
                assert page.locator('[data-collection-resource]:visible').count() >= 3
                page.emulate_media(media='screen')
            page.goto(origin + '/poker/cash-game-study/')
            page.locator('a[href="/poker/resources/#resource-stars-rake"]').click()
            expect(page.locator('#resource-stars-rake')).to_be_visible()
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
            assert context.cookies() == []
            static = browser.new_context(java_script_enabled=False)
            static.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            plain = static.new_page()
            for slug in SLUGS:
                plain.goto(origin + '/poker/' + slug + '/')
                expect(plain.locator('h1')).to_be_visible()
            for filename in ('poker-resource-directory.md', 'poker-resource-directory.json'):
                response = context.request.get(origin + '/downloads/' + filename)
                assert response.ok and response.body() == (ROOT / 'downloads' / filename).read_bytes()
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown(); server.server_close()
    print('PASS: six collection routes at four widths, expanded text spacing, five keyboard answers, print, no-JS, exact exports and directory returns.')
if __name__ == '__main__': main()
