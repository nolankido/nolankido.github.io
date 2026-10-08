"""Directory browser checks without contacting resource providers or sending answers."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import os
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
    def copyfile(self, source, outputfile):
        try: super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError): pass


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    base = 'http://127.0.0.1:' + str(server.server_port)
    try:
        with sync_playwright() as pw:
            options = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'): options['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**options)
            context = browser.new_context()
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = context.new_page(); errors = []; requests = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('request', lambda r: requests.append(r.url))
            response = page.goto(base + '/poker/resources/')
            assert response.status == 200
            expect(page.locator('#resource-controls')).to_be_visible()
            total = page.locator('[data-resource-card]').count()
            baseline = len(requests); original_url = page.url
            cards = page.locator('[data-resource-card]:visible')
            search = page.locator('#resource-search')
            search.fill('ICM'); expect(page.locator('#resource-icm-basics')).to_be_visible()
            page.locator('#resource-controls summary').click()
            page.locator('[data-resource-filter="variants"]').click()
            expect(page.locator('#resource-empty')).to_be_visible()
            page.locator('#resource-reset').click(); expect(search).to_be_focused()
            expect(cards).to_have_count(total)
            page.locator('[data-resource-filter="tools"]').focus(); page.keyboard.press('Space')
            expect(page.locator('[data-resource-filter="tools"]')).to_have_attribute('aria-pressed', 'true')
            expect(page.locator('#resource-flopzilla')).to_be_visible()
            page.locator('#resource-free').click()
            expect(page.locator('#resource-hrc-docs')).to_be_visible()
            expect(page.locator('#resource-flopzilla')).to_be_hidden()
            for access in page.locator('[data-resource-card]:visible').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.access)'):
                assert access == 'Free'
            page.locator('#resource-reset').click()
            for query in ['  oMaHa  ', 'omaha']:
                search.fill(query); expect(page.locator('#resource-omaha-rules')).to_be_visible()
            # Newly covered subjects must be findable without visiting providers.
            for query, ident in [('satellite', 'satellite-guide'), ('badugi', 'pagat-badugi'),
                                 ('hand history', 'phh-format'), ('MIT', 'mit-theory')]:
                search.fill(query)
                expect(page.locator('#resource-' + ident)).to_be_visible()
            search.fill('MIT'); expect(page.locator('#resource-mit-holdem')).to_be_visible()
            search.fill('satellite')
            page.locator('#resource-free').click()
            expect(page.locator('#resource-free')).to_have_attribute('aria-pressed', 'true')
            expect(page.locator('#resource-satellite-guide')).to_be_visible()
            expect(page.locator('#resource-satellite-masterclass')).to_be_hidden()
            page.locator('#resource-reset').click()
            search.fill('<img src=x onerror=alert(1)>')
            expect(page.locator('#resource-empty')).to_be_visible()
            assert page.locator('#poker-resources img').count() == 0
            page.locator('#resource-reset').click()
            expect(cards).to_have_count(total)
            assert page.url == original_url
            assert len(requests) == baseline, requests[baseline:]
            assert page.evaluate('localStorage.length===0 && sessionStorage.length===0')
            assert context.cookies() == []
            # Curated routes must recover a hidden listing and work by keyboard.
            page.locator('#resource-starting-points summary').click()
            expect(page.locator('#resource-starting-points article')).to_have_count(6)
            search.fill('no-match-zzzz'); expect(page.locator('#resource-empty')).to_be_visible()
            destination = page.locator('#resource-starting-points a[href="#resource-pio-quick-start"]')
            destination.focus(); page.keyboard.press('Enter')
            expect(page).to_have_url(base + '/poker/resources/#resource-pio-quick-start')
            expect(page.locator('#resource-pio-quick-start')).to_be_visible()
            expect(cards).to_have_count(total)
            for query, ident in [('Brad Owen', 'brad-owen-wpt-vlog'), ('Wynn', 'wynn-poker'),
                                 ('PLO Mastermind', 'plo-mastermind-blog'), ('2013', 'hpt-rulebooks'),
                                 ('executed', 'treys-evaluator')]:
                search.fill(query); expect(page.locator('#resource-' + ident)).to_be_visible()
            page.locator('#resource-reset').click()
            # A category jump recovers from a no-results filter before navigating.
            search.fill('no-match-zzzz'); expect(page.locator('#resource-empty')).to_be_visible()
            page.locator('.resource-topic-index summary').click()
            page.locator('a[data-resource-jump][href="#events"]').click()
            expect(page).to_have_url(base + '/poker/resources/#events')
            expect(page.locator('#resource-wsop-schedule')).to_be_visible()
            expect(cards).to_have_count(total)
            for width in [320, 390, 768, 1024, 1440]:
                page.set_viewport_size({'width': width, 'height': 1000})
                page.goto(base + '/poker/resources/')
                page.locator('#resource-controls details, #resource-starting-points').evaluate_all('(nodes)=>nodes.forEach(node=>node.open=true)')
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), width
                spacing = page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), ('spacing', width)
                spacing.evaluate('(node)=>node.remove()')
                # Save the expanded new routes using the existing CI artifact folder.
                if os.environ.get('RUNNER_TEMP') and width in [390, 1440]:
                    out = Path(os.environ['RUNNER_TEMP']) / 'poker-reading-previews'
                    out.mkdir(parents=True, exist_ok=True)
                    page.locator('#directory-top').screenshot(path=str(out / f'poker-resource-paths-{width}.png'))
            search.fill('ICM'); expect(page.locator('#resource-omaha-rules')).to_be_hidden()
            page.evaluate('window.dispatchEvent(new Event("beforeprint"))')
            page.emulate_media(media='print')
            expect(page.locator('#resource-omaha-rules')).to_be_visible()
            expect(page.locator('#review-policy')).to_be_visible()
            page.emulate_media(media='screen')
            page.evaluate('window.dispatchEvent(new Event("afterprint"))')
            expect(page.locator('#resource-omaha-rules')).to_be_hidden()
            for nojs in [True, False]:
                fallback = browser.new_context(java_script_enabled=not nojs)
                fallback.route('**/*', lambda r: r.abort() if 'poker-resources.js' in r.request.url or urlsplit(r.request.url).hostname != '127.0.0.1' else r.continue_())
                p = fallback.new_page(); p.goto(base + '/poker/resources/')
                expect(p.locator('#resource-controls')).to_be_hidden()
                expect(p.locator('[data-resource-card]:visible')).to_have_count(total)
                p.locator('#resource-starting-points summary').click()
                p.locator('#resource-starting-points a[href="#resource-brad-owen-wpt-vlog"]').click()
                expect(p.locator('#resource-brad-owen-wpt-vlog')).to_be_visible()
                p.locator('.resource-topic-index summary').click()
                p.locator('a[data-resource-jump][href="#math"]').click()
                expect(p.locator('#resource-pot-odds')).to_be_visible()
                fallback.close()
            if os.environ.get('AXE_PATH'):
                for query in ['', 'no-match-zzzz']:
                    page.goto(base + '/poker/resources/')
                    page.locator('#resource-search').fill(query)
                    if query: expect(page.locator('#resource-empty')).to_be_visible()
                    page.locator('#resource-starting-points summary').click()
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    result = page.evaluate('async()=>await axe.run(document.querySelector("main"))')
                    assert not result['violations'], [(v['id'], v['help']) for v in result['violations']]
            from resource_discovery_checks import check_discovery
            page.goto(base + '/poker/resources/')
            check_discovery(page, ROOT)
            # Actual navigation, bookmarks and back/forward are checked over HTTP in CI.
            page.goto(base + '/poker/resources/#resource-hrc-docs')
            expect(page.locator('#resource-hrc-docs')).to_be_focused()
            page.locator('#resource-search').fill('no-match-zzzz')
            expect(page.locator('#resource-hrc-docs')).to_be_hidden()
            page.locator('#directory-top a[href="#resource-ncpg"]').click()
            expect(page.locator('#resource-ncpg')).to_be_focused()
            page.go_back()
            expect(page.locator('#resource-hrc-docs')).to_be_visible()
            expect(page.locator('#resource-hrc-docs')).to_be_focused()
            page.go_forward()
            expect(page.locator('#resource-ncpg')).to_be_focused()
            assert not errors, errors
            context.close(); browser.close()
        print(f'PASS: {total} external resources, search/topic/free intersections, keyboard filters, empty/reset/XSS recovery, native category and six curated-path jumps, 5 widths with text spacing, print, blocked-script/no-JavaScript access, and no filtering requests, storage, cookies, or URL writes. Provider links were not visited.')
    finally:
        server.shutdown(); server.server_close()

if __name__ == '__main__': main()
