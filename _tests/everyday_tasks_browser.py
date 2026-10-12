"""Native task journeys, exact worksheet downloads, reflow and no-script use.

--offline checks layout and content only when local networking is unavailable.
HTTP navigation, download bytes, and axe scans remain explicit separate checks.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import argparse
import base64
import faulthandler
import json
import os
import sys
from playwright.sync_api import sync_playwright, expect
from browser import html_for

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import living_well
import living_well_utility as utility
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--offline', action='store_true')
args = parser.parse_args()
entries = [e for e in living_well.load(ROOT) if e.get('utility')]
paths = ['/technology/', '/living-well/worksheets/'] + ['/living-well/' + e['slug'] + '/' for e in entries]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
server = None
if not args.offline:
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port) if server else ''
report = {'offline': args.offline, 'layouts': 0, 'spacing': 0, 'downloads': 0, 'keyboard_journeys': 0, 'axe': []}
errors = []
faulthandler.dump_traceback_later(240, exit=True)
try:
    with sync_playwright() as pw:
        options = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'): options['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**options)
        for javascript in [True, False]:
            ctx = browser.new_context(java_script_enabled=javascript, accept_downloads=True)
            ctx.route('**/*', lambda r: r.continue_() if not args.offline and urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = ctx.new_page();page.set_default_timeout(12000);page.set_default_navigation_timeout(12000)
            page.on('pageerror', lambda e: errors.append(str(e)))
            def render(path):
                if args.offline:
                    document = html_for(path)
                    # Preserve actual checked-in preview assets in no-network reviews.
                    for asset in (ROOT / 'assets/work').glob('*.png'):
                        uri = 'data:image/png;base64,' + base64.b64encode(asset.read_bytes()).decode('ascii')
                        document = document.replace('/' + asset.relative_to(ROOT).as_posix(), uri)
                    page.set_content(document)
                else: page.goto(base + path)
            for width in [320,390,768,1440]:
                page.set_viewport_size({'width':width,'height':1000})
                for path in paths:
                    render(path)
                    expect(page.locator('h1')).to_be_visible()
                    assert page.evaluate('document.documentElement.scrollWidth') <= width, (path,width)
                    report['layouts'] += 1
                    if path in paths[:2]:expect(page.locator('.everyday-task')).to_have_count(7)
                    else:
                        expect(page.locator('.lw-utility-starter pre')).to_be_visible()
                        expect(page.locator('.lw-worksheet-actions a[download]')).to_be_visible()
                    if javascript and width==390 and os.environ.get('AXE_PATH'):
                        page.add_script_tag(path=os.environ['AXE_PATH'])
                        audit=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>({id:v.id,targets:v.nodes.map(n=>n.target)})),incomplete:r.incomplete.map(v=>v.id)}}")
                        assert not audit['violations'],(path,audit)
                        report['axe'].append({'path':path,**audit})
                    if javascript and width in [390,1440] and path in paths[:2] and os.environ.get('SCREENSHOT_DIR'):
                        out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                        page.screenshot(path=str(out/('tasks-'+path.strip('/').replace('/','-')+'-'+str(width)+'.png')),full_page=True)
                    page.evaluate('css=>{const s=document.createElement("style");s.textContent=css;document.head.appendChild(s)}','*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                    assert page.evaluate('document.documentElement.scrollWidth') <= width,('spacing',path,width)
                    report['spacing'] += 1
            for entry in entries:
                path='/living-well/'+entry['slug']+'/'
                render(path)
                expect(page.locator('.lw-utility-starter pre')).to_have_text(entry['utility']['starter'])
                # Both upper and lower download links remain available with JS off.
                links=page.locator('a[download][href="/'+utility.worksheet_path(entry).as_posix()+'"]')
                expect(links).to_have_count(2)
                if not args.offline:
                    for link in links.all():
                        with page.expect_download() as item:link.click()
                        download=item.value
                        assert download.suggested_filename==utility.worksheet_path(entry).name
                        assert Path(download.path()).read_bytes()==entry['utility']['starter'].encode('utf-8')
                        report['downloads'] += 1
                    page.goto(base+'/technology/#technology-path')
                    page.locator('.everyday-task h3 a[href="'+path+'"]').focus();page.keyboard.press('Enter')
                    expect(page).to_have_url(base+path);report['keyboard_journeys']+=1
                    page.locator('.lw-utility-starter a[href="/living-well/worksheets/#everyday-task-sheets"]').focus();page.keyboard.press('Enter')
                    expect(page).to_have_url(base+'/living-well/worksheets/#everyday-task-sheets');report['keyboard_journeys']+=1
                    expect(page.locator('#everyday-task-sheets')).to_be_visible()
                page.emulate_media(media='print');render(path)
                expect(page.locator('.lw-utility-starter pre')).to_be_visible()
                page.emulate_media(media='screen')
            if not args.offline:
                assert page.evaluate('localStorage.length+sessionStorage.length')==0
                assert not ctx.cookies()
            ctx.close()
        browser.close()
    assert not errors,errors
    report['status']='pass';print(json.dumps(report,indent=2))
finally:
    if server:server.shutdown();server.server_close()
    faulthandler.cancel_dump_traceback_later()
