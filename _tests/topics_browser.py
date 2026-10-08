"""Topic navigation, shareable filter state, keyboard and no-JS regressions."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
TOPICS = json.loads((ROOT / '_source/poker/topics.json').read_text())['entries']
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
    def copyfile(self, source, out):
        try: super().copyfile(source, out)
        except (BrokenPipeError, ConnectionResetError): pass

def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    dest = Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if dest: dest.mkdir(parents=True, exist_ok=True)
    errors = []
    with sync_playwright() as pw:
        opts = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'): opts['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**opts)
        context = browser.new_context()
        context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
        page = context.new_page(); page.on('pageerror', lambda e: errors.append(str(e)))
        try:
            for width in (320, 390, 768, 1280):
                page.set_viewport_size({'width': width, 'height': 900})
                for route in ('/poker/', '/poker/topics/', '/poker/find/', '/poker/cash-game-study/', '/poker/topics/cash-games/', '/poker/topics/safer-play/'):
                    page.goto(origin + route)
                    expect(page.locator('h1')).to_have_count(1)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (route, width)
                    if dest and width in (390, 1280) and route in ('/poker/', '/poker/topics/', '/poker/topics/cash-games/'):
                        page.screenshot(path=str(dest / f'poker-topics-{route.strip("/").replace("/", "-")}-{width}.png'), full_page=True)
                    page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), ('spacing', route, width)
            page.set_viewport_size({'width': 1280, 'height': 900})
            # Every published topic link applies exactly its finite membership.
            for t in TOPICS:
                page.goto(origin + '/poker/topics/' + t['id'] + '/')
                group = page.locator('#' + t['id'])
                summary = group.locator('details summary')
                summary.focus(); page.keyboard.press('Enter')
                expect(group.locator('details ul')).to_be_visible()
                group.locator('a[href$="kind=resource"]').click()
                expect(page.locator('#finder-topic')).to_have_value(t['id'])
                expect(page.locator('#finder-kind')).to_have_value('resource')
                page.evaluate('dispatchEvent(new Event("beforeprint"))')
                visible = page.locator('[data-finder-card]:visible')
                assert visible.count() > 0
                assert visible.count() == page.locator('[data-kind="resource"][data-topics~="' + t['id'] + '"]').count()
                assert visible.evaluate_all('(els) => els.every(e => e.dataset.kind === "resource")')
                page.evaluate('dispatchEvent(new Event("afterprint"))')
            # Back/forward, reload, keyboard and privacy all work without server requests.
            page.goto(origin + '/poker/find/#topic=variants&kind=resource')
            traffic = []; page.on('request', lambda r: traffic.append(r.url))
            page.locator('#finder-topic').select_option('study')
            page.locator('#finder-free').check()
            assert '#topic=study&kind=resource&free=1' in page.url
            page.go_back(); expect(page.locator('#finder-free')).not_to_be_checked()
            page.go_back(); expect(page.locator('#finder-topic')).to_have_value('variants')
            page.go_forward(); expect(page.locator('#finder-topic')).to_have_value('study')
            initial = page.url
            page.locator('#finder-search').fill('private query abcxyz')
            page.locator('#finder-search').press('Enter')
            expect(page.locator('#finder-empty')).to_be_visible()
            assert page.url == initial and not traffic
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
            assert context.cookies() == []
            page.locator('#finder-search').focus(); page.keyboard.press('Escape')
            assert page.url == origin + '/poker/find/'
            expect(page.locator('#finder-topic')).to_have_value('all')
            page.goto(origin + '/poker/find/#topic=variants&kind=resource&free=1')
            page.reload(); expect(page.locator('#finder-topic')).to_have_value('variants')
            expect(page.locator('#finder-free')).to_be_checked()
            page.goto(origin + '/poker/find/#topic=%3Cscript%3E&kind=unknown&free=invalid')
            expect(page.locator('#finder-topic')).to_have_value('all')
            expect(page.locator('#finder-kind')).to_have_value('all')
            expect(page.locator('#finder-free')).not_to_be_checked()
            # Clear primary-topic route back out of a guide.
            page.goto(origin + '/poker/cash-game-study/')
            page.locator('nav[aria-label="Breadcrumb"] a[href="/poker/topics/cash-games/"]').click()
            assert page.url.endswith('/poker/topics/cash-games/')
            # New topic map is usable with JavaScript disabled; finder preserves its full index.
            offline = browser.new_context(java_script_enabled=False)
            offline.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            p = offline.new_page(); p.goto(origin + '/poker/topics/')
            expect(p.locator('.topic-card')).to_have_count(10)
            p.locator('h3 a[href="/poker/topics/learn/"]').click()
            expect(p.locator('.topic-source')).to_have_count(3)
            p.locator('#learn summary').click(); expect(p.locator('#learn details ul')).to_be_visible()
            p.goto(origin + '/poker/find/#topic=learn')
            assert p.locator('[data-finder-card]:visible').count() > 200
            expect(p.locator('#finder-controls')).not_to_be_visible()
            offline.close()
            if os.environ.get('AXE_PATH'):
                for route in ('/poker/', '/poker/topics/', '/poker/find/', '/poker/cash-game-study/', '/poker/topics/cash-games/', '/poker/topics/safer-play/'):
                    page.goto(origin + route); page.add_script_tag(path=os.environ['AXE_PATH'])
                    result = page.evaluate('async()=>await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21a","wcag21aa"]}})')
                    assert not result['violations'], (route, result['violations'])
            assert not errors, errors
        finally:
            browser.close(); server.shutdown(); server.server_close()
    print('PASS: 10 topic paths; 4 widths; source membership, keyboard disclosures, breadcrumbs, filter deep links, Back/Forward, reload, query privacy, invalid fragments, no-JS map and finder.')
if __name__ == '__main__': main()
