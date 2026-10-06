"""Local HTTP checks of the series, answer panels and generated reading outlines.
External requests are blocked. SCREENSHOT_DIR is optional and never a site asset.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import os
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ['/poker/decision-labs/', '/poker/flush-and-redraw/', '/poker/side-pot-lab/']
CASES = {'/poker/flush-and-redraw/': 5, '/poker/side-pot-lab/': 4}

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass
    def copyfile(self, source, outputfile):
        try:
            super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError):
            pass


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    try:
        with sync_playwright() as pw:
            options = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                options['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**options)
            context = browser.new_context()
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            checked = 0
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 1000})
                for route in ROUTES:
                    assert page.goto(origin + route).status == 200
                    expect(page.locator('h1')).to_have_count(1)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (route, width)
                    if route in CASES:
                        panels = page.locator('details.lab-answer')
                        expect(panels).to_have_count(CASES[route])
                        assert page.locator('details.lab-answer[open]').count() == 0
                        outline = page.locator('details.reader-outline')
                        expect(outline).to_have_count(1)
                        outline.locator('summary').focus(); page.keyboard.press('Enter')
                        expect(outline.locator('nav')).to_be_visible()
                        targets = outline.locator('a').evaluate_all('(nodes) => nodes.map(n => n.getAttribute("href"))')
                        assert len(targets) == 5
                        for target in targets:
                            assert page.locator(target).count() == 1
                            assert page.locator(target).evaluate('(node) => !node.closest("details")')
                        outline.locator('a').last.click()
                        assert page.url.endswith(targets[-1])
                        assert page.locator('details.lab-answer[open]').count() == 0
                        for index in range(CASES[route]):
                            panel = panels.nth(index)
                            panel.locator('summary').focus(); page.keyboard.press('Enter')
                            expect(panel.locator(':scope > div')).to_be_visible()
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), ('expanded', route, width)
                        spacing = page.add_style_tag(content='* {line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important} p {margin-bottom:2em!important}')
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), ('spacing', route, width)
                        spacing.evaluate('(node) => node.remove()')
                    if os.environ.get('SCREENSHOT_DIR') and width in [390, 1440]:
                        page.goto(origin + route)
                        output = Path(os.environ['SCREENSHOT_DIR']); output.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(output / (route.strip('/').replace('/', '-') + f'-{width}.png')), full_page=True)
                    checked += 1
            page.goto(origin + '/poker/decision-labs/')
            expect(page.locator('.lab-series-card')).to_have_count(3)
            for route in ['/poker/decision-lab/', '/poker/flush-and-redraw/', '/poker/side-pot-lab/']:
                page.goto(origin + '/poker/decision-labs/')
                page.locator(f'.lab-series-card a[href="{route}"]').click()
                assert page.url == origin + route
            static = browser.new_context(java_script_enabled=False)
            static.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            nojs = static.new_page()
            for route in CASES:
                nojs.goto(origin + route)
                nojs.locator('details.reader-outline > summary').click()
                expect(nojs.locator('details.reader-outline nav')).to_be_visible()
                nojs.locator('details.lab-answer').first.locator('summary').click()
                expect(nojs.locator('details.lab-answer').first.locator(':scope > div')).to_be_visible()
            static.close()
            axe_checks = 0
            if os.environ.get('AXE_PATH'):
                for route in ROUTES:
                    page.goto(origin + route)
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    for expanded in [False, True]:
                        if expanded:
                            page.locator('main details').evaluate_all('(nodes) => nodes.forEach(n => n.open = true)')
                        results = page.evaluate('async () => await axe.run(document.querySelector("main"), {runOnly:{type:"tag", values:["wcag2a","wcag2aa","wcag21aa","wcag22aa"]}})')
                        assert not results['violations'], (route, expanded, [(v['id'], v['help']) for v in results['violations']])
                        axe_checks += 1
            assert not errors, errors
            context.close(); browser.close()
        print(f'PASS: {checked} lab route/viewport checks; nine keyboard answer panels; outline anchors; unchanged Lab 01 URL; no-JavaScript reading; {axe_checks} accessibility scans. External traffic blocked.')
    finally:
        server.shutdown(); server.server_close()

if __name__ == '__main__':
    main()
