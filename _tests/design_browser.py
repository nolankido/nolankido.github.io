"""Exercise real local HTTP pages and downloads. External traffic is blocked unless fonts are explicitly enabled."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from threading import Thread
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass
server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port)
manifest = json.loads((ROOT / '_source/pages.json').read_text())
errors, missing = [], []
with_fonts = os.environ.get('ALLOW_WEB_FONTS') == '1'
try:
    with sync_playwright() as p:
        opts = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'):
            opts['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = p.chromium.launch(**opts)
        context = browser.new_context(accept_downloads=True)
        allowed = {'127.0.0.1'}
        if with_fonts:
            allowed.update({'fonts.googleapis.com', 'fonts.gstatic.com'})
        context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname in allowed else r.abort())
        for width in [320, 390, 768, 1024, 1440]:
            page = context.new_page()
            page.set_viewport_size({'width': width, 'height': 1000})
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('response', lambda r: missing.append(r.url) if r.status >= 400 and urlsplit(r.url).hostname == '127.0.0.1' else None)
            for entry in manifest:
                response = page.goto(base + entry['path'])
                assert response.status == 200, (entry['path'], response.status)
                expect(page.locator('h1')).to_be_visible()
                if with_fonts:
                    page.evaluate('document.fonts.ready')
                    for family in ['Schibsted Grotesk', 'Source Serif 4', 'IBM Plex Mono']:
                        assert page.evaluate("(name) => Array.from(document.fonts).some(f => f.family.includes(name) && f.status === 'loaded')", family), (entry['path'], family)
                assert page.evaluate('document.documentElement.scrollWidth') <= width, (entry['path'], width)
                if entry['id'] == 'resources':
                    for details in page.locator('details').all():
                        details.locator('summary').click()
                    assert page.evaluate('document.documentElement.scrollWidth') <= width
                    expect(page.locator('.worksheet pre').first).to_be_visible()
                if entry['id'] == 'contact':
                    expect(page.locator('#verification-retry')).to_be_visible()
                    expect(page.locator('#contact-submit')).to_be_enabled()
                    expect(page.locator('#form-success')).to_be_hidden()
                if os.environ.get('SCREENSHOT_DIR') and width in [390, 1440] and entry['id'] in ['home', 'about', 'resources', 'contact', 'trustworthy-tools', 'poker', 'poker-hand-review', 'technology', 'creative']:
                    out = Path(os.environ['SCREENSHOT_DIR']); out.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(out / f'{entry["id"]}-{width}.png'), full_page=True)
            page.close()
        page = context.new_page()
        page.goto(base + '/resources/')
        for slug in ['decision-record', 'tool-trust-check', 'learning-loop']:
            with page.expect_download() as info:
                page.locator(f'a[href="/downloads/{slug}.md"]').click()
            download = info.value
            assert download.suggested_filename == slug + '.md'
            assert Path(download.path()).read_bytes() == (ROOT / 'downloads' / (slug + '.md')).read_bytes()
        for width in [320, 390, 768, 1024, 1440]:
            page.set_viewport_size({'width': width, 'height': 1000})
            page.goto(base)
            tech = page.locator('.destination-technology').bounding_box()
            poker = page.locator('.destination-poker').bounding_box()
            creative = page.locator('.destination-creative').bounding_box()
            assert tech['y'] + tech['height'] <= poker['y'], ('technology-first', width)
            if width > 760:
                assert tech['width'] > poker['width'] > creative['width'], ('ranked-widths', width)
                assert poker['x'] < creative['x'], ('secondary-order', width)
            else:
                assert poker['y'] + poker['height'] <= creative['y'], ('mobile-order', width)
            page.locator('.destination-technology').click()
            assert page.url.endswith('/technology/')
            page.locator('a[href="/notes/trustworthy-tools/"]').click()
            assert page.url.endswith('/notes/trustworthy-tools/')
            page.goto(base)
            page.locator('.destination-creative').click()
            assert page.url.endswith('/creative/')
            page.locator('a[href="/notes/generous-explanations/"]').click()
            assert page.url.endswith('/notes/generous-explanations/')
        page.goto(base)
        page.locator('.destination-poker').click()
        assert page.url.endswith('/poker/')
        page.get_by_role('link', name='Read the hand-review guide').click()
        assert page.url.endswith('/poker/reviewing-a-hand/')
        with page.expect_download() as info:
            page.get_by_role('link', name='Download the review sheet').click()
        assert Path(info.value.path()).read_bytes() == (ROOT / 'downloads/poker-hand-review.md').read_bytes()
        page.get_by_role('link', name='Back to poker', exact=True).click()
        assert page.url.endswith('/poker/')
        page.get_by_role('link', name='Nolan Kido home', exact=True).click()
        assert page.url == base + '/'
        page.goto(base)
        page.keyboard.press('Tab'); page.keyboard.press('Enter')
        assert page.evaluate('document.activeElement.id') == 'main'
        assert not errors, errors
        assert not missing, missing
        print(f'PASS: {len(manifest) * 5} real HTTP page/viewport checks, expanded resource previews, 4 byte-matched downloads, navigation, keyboard access, blocked-service recovery. Web fonts enabled: {with_fonts}. No real submissions.')
        browser.close()
finally:
    server.shutdown()
