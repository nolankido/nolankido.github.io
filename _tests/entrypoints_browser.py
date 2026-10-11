"""Actual static entry-point journeys. No live forms, external traffic, or storage."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port)
config = json.loads((ROOT / '_source/entrypoints.json').read_text())
errors, missing, results = [], [], []
try:
    with sync_playwright() as pw:
        options = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'): options['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**options)
        for javascript in [True, False]:
            context = browser.new_context(java_script_enabled=javascript, accept_downloads=True)
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = context.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('response', lambda r: missing.append(r.url) if r.status >= 400 and urlsplit(r.url).hostname == '127.0.0.1' else None)
            for group in config['interests']:
                for path in group['paths']:
                    page.goto(base + '/start-here/')
                    link = page.locator('#start-' + group['id'] + ' a[href="' + path + '"]')
                    link.focus(); page.keyboard.press('Enter')
                    expect(page).to_have_url(base + path)
            for group in config['resources']:
                for item in group['links']:
                    page.goto(base + '/resources/')
                    link = page.locator('#resources-' + group['id'] + ' a[href="' + item['path'] + '"]')
                    link.focus(); page.keyboard.press('Enter')
                    expect(page).to_have_url(base + item['path'])
            for slug, choices in config['next_reading'].items():
                for choice in choices:
                    page.goto(base + '/notes/' + slug + '/')
                    link = page.locator('.reader-next a[href="' + choice['path'] + '"]')
                    link.focus(); page.keyboard.press('Enter')
                    expect(page).to_have_url(base + choice['path'])
            page.goto(base + '/resources/')
            page.get_by_role('link', name='Thinking worksheets', exact=True).click()
            expect(page).to_have_url(base + '/resources/#thinking-worksheets')
            for slug in ['decision-record', 'tool-trust-check', 'learning-loop']:
                with page.expect_download() as download:
                    page.locator('a[href="/downloads/' + slug + '.md"]').click()
                assert Path(download.value.path()).read_bytes() == (ROOT / 'downloads' / (slug + '.md')).read_bytes()
            results.append({'javascript': javascript, 'keyboard_routes': 28, 'downloads': 3})
            context.close()
        context = browser.new_context()
        context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
        page = context.new_page()
        for width in [320, 390, 768, 1024, 1440]:
            page.set_viewport_size({'width':width, 'height':1000})
            for path in ['/start-here/', '/resources/'] + ['/notes/' + slug + '/' for slug in config['next_reading']]:
                page.goto(base + path)
                expect(page.locator('h1')).to_be_visible()
                assert page.evaluate('document.documentElement.scrollWidth') <= width, (path,width)
                for link in page.locator('.entry-links a, .reader-next a').all():
                    expect(link).to_be_visible()
                if width in [390,1440] and os.environ.get('SCREENSHOT_DIR'):
                    out = Path(os.environ['SCREENSHOT_DIR']); out.mkdir(exist_ok=True,parents=True)
                    page.screenshot(path=str(out / ('entry-' + path.strip('/').replace('/','-') + '-' + str(width) + '.png')),full_page=True)
                if os.environ.get('AXE_PATH') and width in [390,1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    audit=page.evaluate("async () => {const r = await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}); return {violations:r.violations.map(x=>({id:x.id,nodes:x.nodes.length})),incomplete:r.incomplete.map(x=>x.id)}}")
                    assert not audit['violations'],(path,width,audit['violations'])
                    results.append({'path':path,'width':width,'accessibility':audit})
                spacing = page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                assert page.evaluate('document.documentElement.scrollWidth') <= width, ('text-spacing',path,width)
                spacing.evaluate('(node)=>node.remove()')
        context.close(); browser.close()
    assert not errors, errors
    assert not missing, missing
    print(json.dumps({'result':'pass','navigation':results[:2],'viewport_checks':40,'text_spacing_checks':40,'accessibility_checks':len(results)-2,'details':results[2:]},indent=2))
finally:
    server.shutdown(); server.server_close()
