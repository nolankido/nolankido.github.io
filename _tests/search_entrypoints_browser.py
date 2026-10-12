"""Reader entry layouts, metadata, navigation and same-origin preview bytes."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
import sys
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import search_entrypoints
pages = build.public_pages()
reviewed = [p for p in pages if p['id'] in search_entrypoints.HUBS]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port)
report = {'layouts': 0, 'text_spacing': 0, 'journeys': 0, 'preview_bytes': 0, 'axe': []}
errors = []
writes = []
try:
    with sync_playwright() as pw:
        opts = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'): opts['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**opts)
        for scripts in [True, False]:
            ctx = browser.new_context(java_script_enabled=scripts, reduced_motion='reduce')
            def route(r):
                if r.request.method not in {'GET', 'HEAD'}: writes.append(r.request.url)
                r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort()
            ctx.route('**/*', route)
            page = ctx.new_page(); page.set_default_timeout(15000)
            page.on('pageerror', lambda e: errors.append(str(e)))
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 950})
                for entry in reviewed:
                    page.goto(base + entry['path'])
                    expect(page.locator('h1')).to_have_text(entry['title'])
                    expect(page.locator('.entry-summary')).to_be_visible()
                    expect(page.locator('.entry-summary')).to_have_text(entry['description'])
                    expect(page).to_have_title(entry['seo_title'])
                    assert page.evaluate('document.documentElement.scrollWidth') <= width
                    report['layouts'] += 1
                    if scripts and width in [390, 1440] and entry['id'] in {'living-well-guides', 'poker-library', 'notes'} and os.environ.get('SCREENSHOT_DIR'):
                        out = Path(os.environ['SCREENSHOT_DIR']); out.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(out / f'entry-{entry["id"]}-{width}.png'), full_page=True)
                    page.evaluate('css=>{const s=document.createElement("style");s.textContent=css;document.head.appendChild(s)}', '*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                    assert page.evaluate('document.documentElement.scrollWidth') <= width
                    report['text_spacing'] += 1
                    if scripts and width == 390 and entry['id'] in {'living-well-guides', 'poker-library', 'creative'} and os.environ.get('AXE_PATH'):
                        page.add_script_tag(path=os.environ['AXE_PATH'])
                        audit = page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>v.id),incomplete:r.incomplete.map(v=>v.id)}}")
                        assert not audit['violations'], audit
                        report['axe'].append({'path': entry['path'], **audit})
            for parent, target in [('/', '/living-well/'), ('/', '/creative/'), ('/living-well/', '/living-well/guides/'), ('/living-well/', '/living-well/worksheets/'), ('/poker/', '/poker/library/')]:
                page.goto(base + parent)
                link = page.locator('a[href="' + target + '"]').first
                link.focus(); page.keyboard.press('Enter'); expect(page).to_have_url(base + target)
                expect(page.locator('.entry-summary')).to_be_visible(); report['journeys'] += 1
            if scripts:
                records = json.loads((ROOT / '_source/reader-previews.json').read_text())['pages']
                for record in records.values():
                    response = ctx.request.get(base + record['src'])
                    assert response.status == 200
                    assert response.body() == (ROOT / record['src'].lstrip('/')).read_bytes()
                    report['preview_bytes'] += 1
            ctx.close()
        browser.close()
    assert not errors, errors
    assert not writes, writes
    report['status'] = 'pass'; print(json.dumps(report, indent=2))
finally:
    server.shutdown(); server.server_close()
