"""Real search-to-section keyboard journeys, readable results and data fallback."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import faulthandler,json,os,re
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port)
cases=[('recovery','/living-well/find-the-document-you-need/','part-5'),
       ('bounded job','/notes/keep-the-judgment/','delegate-a-bounded-job'),
       ('commitments','/technology/check-ai-answers/','review-writing'),
       ('manageable shape','/creative/','creative-brief-title'),
       ('practical needs','/poker/poker-rules-and-fair-play/','access-and-support')]
report={'keyboard_journeys':0,'address_journeys':0,'address_filters':0,'address_data_fallbacks':0,'spacing_views':0,'data_fallbacks':0,'no_script_pages':0,'axe':[]}
errors=[]
def route_for(mode='normal'):
    def route(r):
        u=urlsplit(r.request.url)
        if u.hostname!='127.0.0.1':r.abort();return
        if u.path=='/find/' and mode!='normal':
            html=(ROOT/'find/index.html').read_text()
            replacement='' if mode=='missing' else '<script type="application/json" id="find-section-data">{broken</script>'
            html=re.sub(r'<!-- Search section index: start -->.*?<!-- Search section index: end -->',lambda _:replacement,html,flags=re.S)
            r.fulfill(status=200,content_type='text/html',body=html)
        else:r.continue_()
    return route

faulthandler.dump_traceback_later(180,exit=True)
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        for width in [320,390,768,1440]:
            context=browser.new_context(viewport={'width':width,'height':950},reduced_motion='reduce')
            context.route('**/*',route_for());page=context.new_page()
            page.on('pageerror',lambda e:errors.append(str(e)));requests=[];page.on('request',lambda r:requests.append(r.url))
            page.goto(base+'/find/');expect(page.locator('#find-controls')).to_be_visible()
            for query,path,anchor in cases:
                print('SECTION_JOURNEY '+json.dumps({'width':width,'query':query,'path':path,'anchor':anchor}),flush=True)
                before=len(requests)
                page.locator('#find-query').fill(query);page.locator('#find-query').press('Enter')
                expect(page.locator('#find-results')).to_be_focused()
                link=page.locator('.find-section-matches a[href="'+path+'#'+anchor+'"]')
                expect(link).to_be_visible()
                assert page.url==base+'/find/' and len(requests)==before,'Search must cause no URL or network change'
                assert page.locator('.find-item').evaluate_all('(items)=>items.every(i=>i.querySelectorAll(".find-section-matches a").length<=3)')
                if query=='recovery' and width in [390,1440] and os.environ.get('SCREENSHOT_DIR'):
                    out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                    page.evaluate("document.activeElement.blur();window.scrollTo({top:0,behavior:'instant'})")
                    page.screenshot(path=str(out/f'search-sections-{width}.png'),full_page=True)
                link.focus();expect(link).to_be_focused();page.keyboard.press('Enter')
                page.wait_for_url(base+path+'#'+anchor,wait_until='load')
                target=page.locator('#'+anchor);expect(target).to_be_visible();expect(target).to_be_in_viewport()
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                metrics='h=>({top:h.getBoundingClientRect().top,header:document.querySelector(".site-header").getBoundingClientRect().bottom,margin:getComputedStyle(h).scrollMarginTop,padding:getComputedStyle(document.documentElement).scrollPaddingTop,fonts:document.fonts.status})'
                print('SECTION_ARRIVAL '+json.dumps({'width':width,'path':path,**target.evaluate(metrics)}),flush=True)
                try:
                    page.wait_for_function('id=>{const h=document.getElementById(id);return h.getBoundingClientRect().top>=document.querySelector(".site-header").getBoundingClientRect().bottom}',arg=anchor,timeout=5000)
                finally:
                    if os.environ.get('SCREENSHOT_DIR'):
                        page.screenshot(path=str(Path(os.environ['SCREENSHOT_DIR'])/f'section-arrival-{cases.index((query,path,anchor))}-{width}.png'))
                assert target.evaluate('h=>h.getBoundingClientRect().top>=document.querySelector(".site-header").getBoundingClientRect().bottom'),(path,anchor,target.evaluate(metrics))
                report['keyboard_journeys']+=1
                page.go_back(wait_until='load');expect(page.locator('#find-query')).to_have_value('')
                expect(page.locator('.find-section-matches a')).to_have_count(0)
            for query,path in [('AI time savings','/technology/ai-time-savings/'),('poker hand rankings','/poker/hand-rankings/')]:
                before=len(requests)
                page.locator('#find-query').fill(query);page.locator('#find-query').press('Enter')
                expect(page.locator('#find-results')).to_be_focused()
                link=page.locator('.find-item:visible h3 a[href="'+path+'"]');expect(link).to_be_visible()
                assert page.url==base+'/find/' and len(requests)==before
                assert page.evaluate('document.documentElement.scrollWidth')<=width
                if width in [390,1440] and os.environ.get('SCREENSHOT_DIR'):
                    page.evaluate('()=>document.fonts.ready.then(()=>true)')
                    page.evaluate("document.activeElement.blur();window.scrollTo({top:0,behavior:'instant'})")
                    page.screenshot(path=str(Path(os.environ['SCREENSHOT_DIR'])/f'search-address-{path.strip("/").replace("/","-")}-{width}.png'),full_page=True)
                link.focus();page.keyboard.press('Enter');page.wait_for_url(base+path,wait_until='load')
                expect(page.locator('h1')).to_be_visible();report['address_journeys']+=1
                page.go_back(wait_until='load');expect(page.locator('#find-query')).to_have_value('')
            page.locator('#find-query').fill('AI time savings');page.locator('#find-query').press('Enter')
            page.locator('#find-kind').select_option('essay');expect(page.locator('#find-empty')).to_be_visible()
            page.locator('#find-kind').select_option('guide');expect(page.locator('#find-empty')).to_be_visible()
            page.locator('#find-kind').select_option('collection')
            expect(page.locator('.find-item:visible h3 a[href="/technology/ai-time-savings/"]')).to_be_visible()
            page.locator('#find-interest').select_option('poker');expect(page.locator('#find-empty')).to_be_visible()
            page.locator('#find-reset').press('Enter');expect(page.locator('#find-query')).to_be_focused()
            expect(page.locator('#find-query')).to_have_value('');expect(page.locator('#find-interest')).to_have_value('');expect(page.locator('#find-kind')).to_have_value('')
            report['address_filters']+=1
            assert context.cookies()==[]
            assert page.evaluate('localStorage.length+sessionStorage.length')==0
            context.close()
        context=browser.new_context();context.route('**/*',route_for());page=context.new_page()
        for width in [320,390,768,1440]:
            print('SECTION_SPACING '+str(width),flush=True)
            page.set_viewport_size({'width':width,'height':950});page.goto(base+'/find/')
            page.locator('#find-query').fill('recovery');page.locator('#find-query').press('Enter')
            page.evaluate('()=>{const s=document.createElement("style");s.textContent="*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}";document.head.append(s)}')
            assert page.evaluate('document.documentElement.scrollWidth')<=width
            expect(page.locator('.find-section-matches a[href="/living-well/find-the-document-you-need/#part-5"]')).to_be_visible()
            report['spacing_views']+=1
            if width==390 and os.environ.get('AXE_PATH'):
                page.add_script_tag(path=os.environ['AXE_PATH'])
                audit=page.evaluate('async()=>{const r=await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa"]}});return {violations:r.violations.map(v=>v.id),incomplete:r.incomplete.map(v=>v.id)}}')
                assert not audit['violations'],audit;report['axe'].append(audit)
        context.close()
        for mode in ['missing','malformed']:
            print('SECTION_DATA_FALLBACK '+mode,flush=True)
            context=browser.new_context();context.route('**/*',route_for(mode));page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(base+'/find/');page.locator('#find-query').fill('family story');page.locator('#find-query').press('Enter')
            expect(page.locator('.find-item:visible h3 a[href="/living-well/preserve-family-story/"]')).to_be_visible()
            expect(page.locator('.find-section-matches a')).to_have_count(0)
            report['data_fallbacks']+=1
            page.locator('#find-query').fill('AI time savings');page.locator('#find-query').press('Enter')
            expect(page.locator('.find-item:visible h3 a[href="/technology/ai-time-savings/"]')).to_be_visible()
            expect(page.locator('.find-section-matches a')).to_have_count(0)
            report['address_data_fallbacks']+=1;context.close()
        context=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':950});context.route('**/*',route_for());page=context.new_page()
        page.goto(base+'/find/');expect(page.locator('#find-controls')).to_be_hidden()
        expect(page.locator('.find-item')).to_have_count(158)
        page.locator('#browse-technology summary').focus();page.keyboard.press('Enter')
        link=page.locator('#browse-technology h3 a').first;destination=link.get_attribute('href')
        link.focus();page.keyboard.press('Enter');page.wait_for_url(base+destination,wait_until='load');expect(page.locator('h1')).to_be_visible()
        report['no_script_pages']=158;context.close()
        assert not errors,errors
        browser.close();report['status']='pass';print(json.dumps(report,indent=2))
        if os.environ.get('SCREENSHOT_DIR'):(Path(os.environ['SCREENSHOT_DIR'])/'search-sections-report.json').write_text(json.dumps(report,indent=2)+'\n')
finally:
    server.shutdown();server.server_close();faulthandler.cancel_dump_traceback_later()
