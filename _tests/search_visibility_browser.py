"""New identity and search entry points: native navigation, reflow, and disclosure."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import argparse
import json
import os
from playwright.sync_api import sync_playwright, expect

from browser import html_for
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--offline', action='store_true', help='Render in-memory when local networking is blocked; skips URL journeys')
args = parser.parse_args()
ROOT = Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass
server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port)
result = {'offline': args.offline, 'layouts': 0, 'text_spacing': 0, 'keyboard_journeys': 0, 'no_script_journeys': 0, 'axe': []}
errors = []
paths = ['/about/', '/technology/', '/technology/task-brief/', '/notes/keep-the-judgment/',
         '/poker/pot-odds-workshop/', '/living-well/did-the-tool-actually-help/']
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, **({'executable_path': os.environ['CHROMIUM_PATH']} if os.environ.get('CHROMIUM_PATH') else {}))
        for javascript in ([True] if args.offline else [True, False]):
            context = browser.new_context(java_script_enabled=javascript)
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = context.new_page()
            def render(path):
                if args.offline:
                    page.set_content(html_for(path))
                else:
                    page.goto(base + path)
            page.on('pageerror', lambda error: errors.append(str(error)))
            for width in [320, 390, 768, 1440]:
                print('Checking layouts:', javascript, width, flush=True)
                page.set_viewport_size({'width': width, 'height': 950})
                for path in paths:
                    render(path)
                    expect(page.locator('h1')).to_be_visible()
                    expect(page.locator('nav[aria-label="Breadcrumb"]')).to_have_count(1)
                    assert page.evaluate('document.documentElement.scrollWidth') <= width, (path, width)
                    result['layouts'] += 1
                    if javascript and width in [390, 1440] and os.environ.get('SCREENSHOT_DIR'):
                        out = Path(os.environ['SCREENSHOT_DIR']); out.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(out/(path.strip('/').replace('/', '-')+'-'+str(width)+'.png')), full_page=True)
                    if javascript and width in [390, 1440] and os.environ.get('AXE_PATH'):
                        page.add_script_tag(path=os.environ['AXE_PATH'])
                        audit = page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>({id:v.id,nodes:v.nodes.length})),incomplete:r.incomplete.map(v=>v.id)}}")
                        assert not audit['violations'], (path, width, audit)
                        result['axe'].append({'path': path, 'width': width, **audit})
                    page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                    assert page.evaluate('document.documentElement.scrollWidth') <= width, ('spacing', path, width)
                    result['text_spacing'] += 1
            if not args.offline:
                page.goto(base + '/technology/')
                link=page.locator('a[href="#working-examples"]');link.focus();page.keyboard.press('Enter')
                expect(page).to_have_url(base+'/technology/#working-examples')
                result['keyboard_journeys'] += 1
                link=page.locator('a[href="/technology/task-brief/#how-it-works"]');link.focus();page.keyboard.press('Enter')
                expect(page).to_have_url(base+'/technology/task-brief/#how-it-works')
                expect(page.locator('#how-it-works')).to_be_visible()
                result['keyboard_journeys'] += 1
                page.locator('nav[aria-label="Breadcrumb"] a[href="/technology/"]').focus();page.keyboard.press('Enter')
                expect(page).to_have_url(base+'/technology/')
                result['keyboard_journeys'] += 1
                page.goto(base+'/poker/pot-odds-workshop/')
                page.locator('.search-author a[rel="author"]').focus();page.keyboard.press('Enter')
                expect(page).to_have_url(base+'/about/')
                expect(page.locator('#try-the-work')).to_be_visible()
                result['keyboard_journeys'] += 1
            if not javascript:
                render('/technology/task-brief/')
                expect(page.locator('#brief-editor')).to_be_hidden()
                expect(page.locator('#brief-unavailable')).to_be_visible()
                expect(page.locator('#brief-blank')).to_be_visible()
                expect(page.locator('#how-it-works')).to_be_visible()
                for path in ['/find/', '/poker/find/', '/living-well/find/']:
                    render(path)
                    assert 'noindex' in page.locator('meta[name="robots"]').get_attribute('content')
                    assert page.locator('main a[href]').count()>5
                    result['no_script_journeys'] += 1
            context.close()
        browser.close()
    assert not errors, errors
    result['status']='pass'
    print(json.dumps(result,indent=2))
finally:
    server.shutdown();server.server_close()
