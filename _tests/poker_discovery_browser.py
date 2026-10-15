"""Native hub journeys, section jumps, reflow, no-script reading and accessibility."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
from playwright.sync_api import sync_playwright, expect
from field_guide_browser import QuietHandler, ROOT
from learning_path_browser import SPACING


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    shots = Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    report = {'layouts': 0, 'section_jumps': 0, 'guide_arrivals': 0, 'no_script_arrivals': 0, 'axe': []}
    errors = []
    writes = []
    routes = json.loads((ROOT / '_source/poker/reading-routes.json').read_text())
    try:
        with sync_playwright() as pw:
            opts = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                opts['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**opts)
            context = browser.new_context(reduced_motion='reduce')
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = context.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('request', lambda r: writes.append(r.url) if r.method not in ['GET', 'HEAD'] else None)
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 1000})
                for hub in ['/poker/', '/poker/library/']:
                    assert page.goto(origin + hub).status == 200
                    page.evaluate('() => document.fonts.ready.then(() => true)')
                    expect(page.locator('.poker-goal')).to_have_count(4)
                    expect(page.locator('.poker-long-read')).to_have_count(4)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (hub, width)
                    for target in (['#in-depth', '#after-play', '#watch'] if hub == '/poker/' else ['#in-depth', '#all-guides']):
                        page.locator('.poker-hub-jumps a[href="' + target + '"]').press('Enter')
                        expect(page.locator(target)).to_be_in_viewport()
                        metrics = page.locator(target).evaluate('e => ({top:e.getBoundingClientRect().top,header:document.querySelector(".site-header").getBoundingClientRect().bottom})')
                        assert metrics['top'] >= metrics['header'] - 1, (hub, width, target, metrics)
                        report['section_jumps'] += 1
                    if shots and width in [390, 1440]:
                        page.goto(origin + hub + '#reading-routes')
                        page.screenshot(path=str(shots / ('poker-discovery-' + ('home' if hub == '/poker/' else 'library') + '-' + str(width) + '.png')))
                        page.goto(origin + hub + '#in-depth')
                        page.screenshot(path=str(shots / ('poker-in-depth-' + ('home' if hub == '/poker/' else 'library') + '-' + str(width) + '.png')))
                    page.add_style_tag(content=SPACING)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), ('spacing', hub, width)
                    if os.environ.get('AXE_PATH') and width in [390, 1440]:
                        page.add_script_tag(path=os.environ['AXE_PATH'])
                        bad = page.evaluate("async () => (await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations.map(v => ({id:v.id,nodes:v.nodes.map(n=>n.target)}))")
                        assert not bad, (hub, width, bad)
                        report['axe'].append({'hub': hub, 'width': width, 'violations': bad})
                    report['layouts'] += 1
            for hub in ['/poker/', '/poker/library/']:
                for route in routes['routes']:
                    for link in route['links']:
                        page.goto(origin + hub)
                        path = '/poker/' + link['slug'] + '/'
                        page.locator('.poker-goal a[href="' + path + '"]').press('Enter')
                        page.wait_for_url(origin + path, wait_until='load')
                        expect(page.locator('h1')).to_be_visible()
                        report['guide_arrivals'] += 1
            nojs = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 1000})
            nojs.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            static = nojs.new_page()
            for hub in ['/poker/', '/poker/library/']:
                for item in routes['in_depth']:
                    static.goto(origin + hub)
                    path = '/poker/' + item['slug'] + '/'
                    static.locator('.poker-long-read a[href="' + path + '"]').press('Enter')
                    static.wait_for_url(origin + path, wait_until='load')
                    expect(static.locator('h1')).to_be_visible()
                    report['no_script_arrivals'] += 1
            static.goto(origin + '/poker/library/')
            static.locator('.poker-hub-jumps a[href="#all-guides"]').press('Enter')
            expect(static.locator('#library-controls')).not_to_be_visible()
            assert static.locator('#library-grid [data-library-card]:visible').count() >= 60
            assert not errors, errors
            assert not writes, writes
            assert context.cookies() == []
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    if shots:
        (shots / 'poker-discovery-browser.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
