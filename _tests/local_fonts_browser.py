"""Real typography, exact provider parity and readable blocked-font fallbacks.

External requests are blocked. The old Google-font reference is fulfilled with
its exact checked-in provider bytes. Timings are not a field-performance claim.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
from hashlib import sha256
import json,os,sys
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import font_delivery
import local_fonts_history as history
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port)
record=json.loads((ROOT/font_delivery.LOCAL_PROVENANCE).read_text())
by_url={r['url']:r for r in record['files']}
paths=['/','/about/','/technology/','/notes/keep-the-judgment/','/poker/holdem-basics/','/living-well/did-the-tool-actually-help/']
report={'parity_views':0,'local_fonts_loaded':0,'fallback_views':0,'keyboard_journeys':0,'exact_assets':0,'axe':[]}
errors=[]

def route_for(requests,old=False,blocked=False):
    def route(r):
        u=urlsplit(r.request.url);requests.append(r.request.url)
        if old and r.request.url in by_url:
            r.fulfill(status=200,content_type='font/woff2',body=(ROOT/by_url[r.request.url]['path']).read_bytes())
        elif u.hostname=='127.0.0.1':
            if blocked and u.path.startswith('/assets/fonts/'):r.abort();return
            if old and (r.request.resource_type=='document' or u.path=='/assets/site-fonts.css'):
                path=u.path.lstrip('/')+('index.html' if u.path.endswith('/') else '')
                r.fulfill(status=200,content_type='text/css' if path.endswith('.css') else 'text/html',body=history.before(path,(ROOT/path).read_bytes()))
            else:r.continue_()
        else:r.abort()
    return route

try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        for scripts in [True,False]:
            for width in [320,390,1440]:
                measurements=[]
                for old in [True,False]:
                    context=browser.new_context(java_script_enabled=scripts,reduced_motion='reduce',viewport={'width':width,'height':950})
                    requests=[];context.route('**/*',route_for(requests,old=old));page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
                    geometry=[]
                    for path in paths:
                        page.goto(base+path)
                        # Force each declared subset once: validate every binary decodes,
                        # including glyph ranges not used by a particular English page.
                        loaded=page.evaluate('async()=>{await Promise.all(Array.from(document.fonts,f=>f.load()));await document.fonts.ready;return Array.from(document.fonts).filter(f=>f.status==="loaded").length}')
                        assert loaded==38,(old,scripts,width,path,loaded)
                        if not old:report['local_fonts_loaded']+=loaded
                        expect(page.locator('h1')).to_be_visible()
                        assert page.evaluate('document.documentElement.scrollWidth')<=width,(path,width)
                        geometry.append(page.locator('h1,h2,p,a,summary').evaluate_all('(nodes)=>nodes.map(n=>{const r=n.getBoundingClientRect();const s=getComputedStyle(n);return [n.textContent,r.x,r.y,r.width,r.height,s.fontFamily,s.fontWeight,s.fontStyle]})'))
                        if not old and scripts and width in [390,1440] and path in ['/','/about/','/technology/'] and os.environ.get('SCREENSHOT_DIR'):
                            out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                            page.screenshot(path=str(out/f'local-fonts-{path.strip("/") or "home"}-{width}.png'),full_page=True)
                    external_fonts=[u for u in requests if urlsplit(u).hostname in {'fonts.gstatic.com','fonts.googleapis.com'}]
                    if old:assert len(set(external_fonts))==24
                    else:
                        assert not external_fonts,external_fonts
                        assert len({u for u in requests if '/assets/fonts/' in u})==24
                        page.goto(base+'/');link=page.locator('.identity-actions a[href="/technology/"]');link.focus();expect(link).to_be_focused();page.keyboard.press('Enter');page.wait_for_url(base+'/technology/');expect(page.locator('h1')).to_be_visible();report['keyboard_journeys']+=1
                        if scripts and width==390 and os.environ.get('AXE_PATH'):
                            page.add_script_tag(path=os.environ['AXE_PATH'])
                            audit=page.evaluate('async()=>{const r=await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa"]}});return {violations:r.violations.map(v=>v.id),incomplete:r.incomplete.map(v=>v.id)}}')
                            assert not audit['violations'],audit;report['axe'].append(audit)
                    measurements.append(geometry);context.close()
                assert measurements[0]==measurements[1],('font geometry changed',scripts,width)
                report['parity_views']+=len(paths)
        for scripts in [True,False]:
            context=browser.new_context(java_script_enabled=scripts,viewport={'width':320,'height':950});requests=[];context.route('**/*',route_for(requests,blocked=True));page=context.new_page()
            for path in paths:
                page.goto(base+path);expect(page.locator('h1')).to_be_visible()
                page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                assert page.evaluate('document.documentElement.scrollWidth')<=320,(path,scripts)
                assert page.evaluate('Array.from(document.fonts).every(f=>f.status!=="loaded")')
                report['fallback_views']+=1
            context.close()
        assets_context=browser.new_context()
        for entry in record['files']+record['licenses']:
            response=assets_context.request.get(base+'/'+entry['path'])
            assert response.status==200 and sha256(response.body()).hexdigest()==entry['sha256'],entry['path']
            report['exact_assets']+=1
        assets_context.close()
        assert not errors,errors
        browser.close();report['status']='pass';print(json.dumps(report,indent=2))
        if os.environ.get('SCREENSHOT_DIR'):(Path(os.environ['SCREENSHOT_DIR'])/'local-fonts-report.json').write_text(json.dumps(report,indent=2)+'\n')
finally:server.shutdown();server.server_close()
