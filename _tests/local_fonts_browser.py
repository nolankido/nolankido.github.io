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
from time import monotonic
import json,os,sys,faulthandler
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
report={'parity_views':0,'local_fonts_loaded':0,'decoded_files':0,'fallback_views':0,'keyboard_journeys':0,'exact_assets':0,'axe':[]}
errors=[]
SPACING='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}'

def rendered_faces(page,case):
    # Playwright's in-page polling depends on timers/animation frames, which
    # need not run when JavaScript is disabled. Read the native FontFaceSet
    # from the driver instead; retain the same loaded-state requirement.
    deadline=monotonic()+10
    while True:
        state=page.evaluate('({status:document.fonts.status,faces:Array.from(document.fonts,f=>({family:f.family,status:f.status}))})')
        if state['status']=='loaded':return state['faces']
        assert monotonic()<deadline,('font readiness timeout',case,state)
        page.wait_for_timeout(50)

def route_for(requests,old=False,blocked=False):
    def route(r):
        u=urlsplit(r.request.url);requests.append(r.request.url)
        if old and r.request.url in by_url:
            r.fulfill(status=200,content_type='font/woff2',headers={'Access-Control-Allow-Origin':'*'},body=(ROOT/by_url[r.request.url]['path']).read_bytes())
        elif u.hostname=='127.0.0.1':
            if blocked and u.path.startswith('/assets/fonts/'):r.abort();return
            if blocked and r.request.resource_type=='document':
                path=u.path.lstrip('/')+('index.html' if u.path.endswith('/') else '')
                document=(ROOT/path).read_text().replace('</head>','<style>'+SPACING+'</style></head>',1)
                r.fulfill(status=200,content_type='text/html',body=document)
            elif old and (r.request.resource_type=='document' or u.path=='/assets/site-fonts.css'):
                path=u.path.lstrip('/')+('index.html' if u.path.endswith('/') else '')
                r.fulfill(status=200,content_type='text/css' if path.endswith('.css') else 'text/html',body=history.before(path,(ROOT/path).read_bytes()))
            else:r.continue_()
        else:r.abort()
    return route

faulthandler.dump_traceback_later(240,exit=True)
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        # Decode every exact binary separately from the CSS rendering journey.
        # Loading every CSS-connected, unused face via one awaited Promise can
        # stall without a Playwright timeout. These states have explicit bounds.
        decode_context=browser.new_context();decode=decode_context.new_page()
        for entry in record['files']:
            print('FONT_DECODE '+entry['path'],flush=True)
            raw=(ROOT/entry['path']).read_bytes()
            decode.evaluate('(bytes)=>{window.fontProbe=new FontFace("ReviewedFontProbe",new Uint8Array(bytes));window.fontProbe.load().catch(()=>{});}',list(raw))
            decode.wait_for_function('window.fontProbe.status === "loaded" || window.fontProbe.status === "error"',timeout=10000)
            assert decode.evaluate('window.fontProbe.status')=='loaded',entry['path']
            report['decoded_files']+=1
        decode_context.close()
        for scripts in [True,False]:
            for width in [320,390,1440]:
                measurements=[]
                for old in [True,False]:
                    context=browser.new_context(java_script_enabled=scripts,reduced_motion='reduce',viewport={'width':width,'height':950})
                    requests=[];context.route('**/*',route_for(requests,old=old));page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
                    geometry=[]
                    for path in paths:
                        case={'reference':old,'scripts':scripts,'width':width,'path':path}
                        print('FONT_VIEW '+json.dumps(case),flush=True)
                        page.goto(base+path)
                        faces=rendered_faces(page,case)
                        assert len(faces)==38,(case,faces)
                        for family in ['Schibsted Grotesk','Source Serif 4','IBM Plex Mono']:
                            assert any(f['family'].strip("'\"")==family and f['status']=='loaded' for f in faces),(case,family,faces)
                        loaded=sum(f['status']=='loaded' for f in faces)
                        print('FONT_READY '+json.dumps(dict(case,loaded_faces=loaded)),flush=True)
                        if not old:report['local_fonts_loaded']+=loaded
                        expect(page.locator('h1')).to_be_visible()
                        assert page.evaluate('document.documentElement.scrollWidth')<=width,(path,width)
                        geometry.append(page.locator('h1,h2,p,a,summary').evaluate_all('(nodes)=>nodes.map(n=>{const r=n.getBoundingClientRect();const s=getComputedStyle(n);return [n.textContent,r.x,r.y,r.width,r.height,s.fontFamily,s.fontWeight,s.fontStyle]})'))
                        if not old and scripts and width in [390,1440] and path in ['/','/about/','/technology/'] and os.environ.get('SCREENSHOT_DIR'):
                            out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                            page.screenshot(path=str(out/f'local-fonts-{path.strip("/") or "home"}-{width}.png'),full_page=True)
                    external_fonts=[u for u in requests if urlsplit(u).hostname in {'fonts.gstatic.com','fonts.googleapis.com'}]
                    if old:assert external_fonts and set(external_fonts)<=set(by_url)
                    else:
                        assert not external_fonts,external_fonts
                        assert {urlsplit(u).path for u in requests if '/assets/fonts/' in u} <= {'/'+r['path'] for r in record['files']}
                        print('FONT_KEYBOARD '+json.dumps({'scripts':scripts,'width':width}),flush=True)
                        page.goto(base+'/');link=page.locator('.identity-actions a[href="/technology/"]');link.focus();expect(link).to_be_focused();page.keyboard.press('Enter');page.wait_for_url(base+'/technology/');expect(page.locator('h1')).to_be_visible();report['keyboard_journeys']+=1
                        if scripts and width==390 and os.environ.get('AXE_PATH'):
                            page.add_script_tag(path=os.environ['AXE_PATH'])
                            audit=page.evaluate('async()=>{const r=await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa"]}});return {violations:r.violations.map(v=>v.id),incomplete:r.incomplete.map(v=>v.id)}}')
                            assert not audit['violations'],audit;report['axe'].append(audit)
                    font_paths=sorted({by_url[u]['path'] for u in external_fonts}) if old else sorted({urlsplit(u).path.lstrip('/') for u in requests if '/assets/fonts/' in u})
                    measurements.append((geometry,font_paths));context.close()
                assert measurements[0]==measurements[1],('font geometry changed',scripts,width)
                report['parity_views']+=len(paths)
                print('FONT_PARITY '+json.dumps({'scripts':scripts,'width':width}),flush=True)
        for scripts in [True,False]:
            context=browser.new_context(java_script_enabled=scripts,viewport={'width':320,'height':950});requests=[];context.route('**/*',route_for(requests,blocked=True));page=context.new_page()
            for path in paths:
                print('FONT_FALLBACK '+json.dumps({'scripts':scripts,'path':path}),flush=True)
                page.goto(base+path);expect(page.locator('h1')).to_be_visible()
                # The server delivers expanded-spacing CSS without relying on
                # style.onload callbacks in the JavaScript-disabled context.
                spacing=page.locator('p').first.evaluate('(e)=>{const s=getComputedStyle(e);return [s.fontSize,s.letterSpacing,s.wordSpacing,s.lineHeight].map(parseFloat)}')
                assert all(abs(actual-spacing[0]*ratio)<.01 for actual,ratio in zip(spacing[1:],[.12,.16,1.5])),(path,scripts,spacing)
                assert page.evaluate('document.documentElement.scrollWidth')<=320,(path,scripts)
                assert page.evaluate('Array.from(document.fonts).every(f=>f.status!=="loaded")')
                report['fallback_views']+=1
            context.close()
        assets_context=browser.new_context()
        for entry in record['files']+record['licenses']:
            print('FONT_ASSET '+entry['path'],flush=True)
            response=assets_context.request.get(base+'/'+entry['path'])
            assert response.status==200 and sha256(response.body()).hexdigest()==entry['sha256'],entry['path']
            report['exact_assets']+=1
        assets_context.close()
        assert not errors,errors
        browser.close();report['status']='pass';print(json.dumps(report,indent=2))
        if os.environ.get('SCREENSHOT_DIR'):(Path(os.environ['SCREENSHOT_DIR'])/'local-fonts-report.json').write_text(json.dumps(report,indent=2)+'\n')
finally:
    server.shutdown();server.server_close()
    faulthandler.cancel_dump_traceback_later()
