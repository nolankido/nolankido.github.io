"""Work previews, direct navigation, feed delivery, and resilient no-script reading.
Use --offline only when local HTTP is unavailable; it cannot verify URL journeys.
"""
import argparse
import base64
import faulthandler
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
from playwright.sync_api import sync_playwright, expect
from browser import html_for

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--offline', action='store_true')
args = parser.parse_args()
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass
server = None
if not args.offline:
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port) if server else ''
paths = ['/', '/technology/', '/notes/', '/follow/', '/technology/checking-ai-website-changes/']
report = {'offline': args.offline, 'layouts': 0, 'spacing': 0, 'images': 0, 'keyboard_journeys': 0, 'feeds': 0, 'axe': []}
errors = []
faulthandler.dump_traceback_later(240, exit=True)
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, **({'executable_path': os.environ['CHROMIUM_PATH']} if os.environ.get('CHROMIUM_PATH') else {}))
        for javascript in [True, False]:
            ctx = browser.new_context(java_script_enabled=javascript, reduced_motion='reduce')
            ctx.route('**/*', lambda r: r.continue_() if not args.offline and urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = ctx.new_page()
            page.set_default_timeout(10000)
            page.set_default_navigation_timeout(15000)
            page.on('pageerror', lambda e: errors.append(str(e)))
            def render(path):
                if args.offline:
                    html = html_for(path)
                    # Inline real committed PNGs in offline mode, not invented placeholders.
                    for image in (ROOT / 'assets/work').glob('*.png'):
                        html = html.replace('/' + image.relative_to(ROOT).as_posix(), 'data:image/png;base64,' + base64.b64encode(image.read_bytes()).decode())
                    page.set_content(html)
                else:
                    page.goto(base + path)
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 1000})
                for path in paths:
                    render(path)
                    expect(page.locator('h1')).to_be_visible()
                    assert page.evaluate('document.documentElement.scrollWidth') <= width, (path, width)
                    report['layouts'] += 1
                    if path == '/technology/':
                        expect(page.locator('.practical-work')).to_have_count(3)
                        for image in page.locator('.work-preview img').all():
                            image.scroll_into_view_if_needed()
                            expect(image).to_be_visible()
                            expect(image).to_have_js_property('naturalWidth', 1044)
                            assert image.get_attribute('alt')
                            report['images'] += 1
                    if javascript and width in [390, 1440] and os.environ.get('SCREENSHOT_DIR'):
                        out = Path(os.environ['SCREENSHOT_DIR']); out.mkdir(parents=True, exist_ok=True)
                        page.evaluate('window.scrollTo(0,0)')
                        page.screenshot(path=str(out / ('discovery-' + (path.strip('/').replace('/', '-') or 'home') + '-' + str(width) + '.png')), full_page=True)
                    if javascript and width in [390, 1440] and os.environ.get('AXE_PATH'):
                        page.add_script_tag(path=os.environ['AXE_PATH'])
                        audit = page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)})),incomplete:r.incomplete.map(v=>v.id)}}")
                        assert not audit['violations'], (path, width, audit)
                        report['axe'].append({'path': path, 'width': width, **audit})
                    # Synchronous injection avoids no-script add_style_tag event hangs.
                    page.evaluate('css=>{const s=document.createElement("style");s.textContent=css;document.head.appendChild(s)}', '*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                    assert page.evaluate('document.documentElement.scrollWidth') <= width, ('spacing', path, width)
                    report['spacing'] += 1
            render('/technology/')
            # Information and actions survive failed/disabled image rendering.
            page.locator('.work-preview img').evaluate_all('(els)=>els.forEach(e=>e.style.display="none")')
            expect(page.locator('.work-action')).to_have_count(3)
            for link in page.locator('.work-action').all():
                expect(link).to_be_visible()
            if not args.offline:
                for path in ['/technology/task-brief/', '/technology/ai-time-savings/', '/technology/checking-ai-website-changes/']:
                    page.goto(base + '/')
                    page.locator('nav[aria-label="Selected practical AI work"] a[href="' + path + '"]').focus()
                    page.keyboard.press('Enter')
                    expect(page).to_have_url(base + path)
                    report['keyboard_journeys'] += 1
                page.goto(base + '/notes/#technology')
                page.locator('.technology-publication a[href="/technology/checking-ai-website-changes/"]').focus(); page.keyboard.press('Enter')
                expect(page).to_have_url(base + '/technology/checking-ai-website-changes/')
                page.locator('.technology-return a[href="/follow/#practical-ai-feed"]').focus(); page.keyboard.press('Enter')
                expect(page).to_have_url(base + '/follow/#practical-ai-feed')
                expect(page.locator('#practical-ai-feed')).to_be_visible()
                report['keyboard_journeys'] += 2
                for path in ['/technology/feed.xml', '/writing.xml']:
                    # Follow the actual anchor and verify the RSS over its real HTTP URL.
                    link = page.locator('main a[href="' + path + '"]').first
                    link.focus(); page.keyboard.press('Enter')
                    expect(page).to_have_url(base + path)
                    response = ctx.request.get(base + path)
                    assert response.status == 200
                    assert response.body() == (ROOT / path.lstrip('/')).read_bytes()
                    items = ET.fromstring(response.body()).findall('./channel/item')
                    assert sum(i.findtext('link') == 'https://nolankido.com/technology/checking-ai-website-changes/' for i in items) == 1
                    report['feeds'] += 1
                    page.goto(base + '/follow/')
                assert page.evaluate('localStorage.length + sessionStorage.length') == 0
                assert not ctx.cookies()
            ctx.close()
        browser.close()
    assert not errors, errors
    report['status'] = 'pass'
    print(json.dumps(report, indent=2))
finally:
    if server:
        server.shutdown(); server.server_close()
    faulthandler.cancel_dump_traceback_later()
