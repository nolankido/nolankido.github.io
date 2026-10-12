"""Real HTTP journeys for the editorial AI decision guide; external services blocked."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from pathlib import Path
from urllib.parse import urlsplit
import argparse,json,os,sys
parser=argparse.ArgumentParser();parser.add_argument("--offline",action="store_true");args=parser.parse_args()
from browser import html_for
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
PATH='/technology/should-i-use-ai/'
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port)
report={'offline':args.offline,'scenarios':0,'layouts':0,'spacing':0,'downloads':0,'journeys':0,'fallbacks':0,'privacy':0,'axe':[]}
errors=[]
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,**({'executable_path':os.environ['CHROMIUM_PATH']} if os.environ.get('CHROMIUM_PATH') else {}))
        ctx=browser.new_context(accept_downloads=True,reduced_motion='reduce');requests=[]
        def route(r):
            requests.append(r.request.url)
            r.continue_() if not args.offline and urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort()
        ctx.route('**/*',route);page=ctx.new_page();page.set_default_timeout(10000)
        page.on('pageerror',lambda e:errors.append(str(e)))
        def render(p,path,execute=True):
            if args.offline:
                p.set_content(html_for(path))
                if execute and path==PATH:p.add_script_tag(content=(ROOT/'assets/ai-task-choice.js').read_text())
            else:p.goto(base+path)
        def load():render(page,PATH);expect(page.locator('#choice-form')).to_be_visible()
        def choose(**changes):
            values={'goal':'clear','inputs':'allowed','stakes':'low','review':'ready','simpler':'no','scope':'draft',**changes}
            for k,v in values.items():page.locator('#choice-'+k+'-'+v).check()
            page.locator('#choice-form button[type=submit]').click()
        load();page.locator('#choice-form button[type=submit]').focus();page.keyboard.press('Enter')
        expect(page.locator('#choice-result')).to_be_hidden();expect(page.locator('#choice-goal-clear')).to_be_focused()
        expect(page.locator('#choice-error')).to_contain_text('Choose an answer');report['scenarios']+=1
        scenarios=[({},'trial'),({'inputs':'unknown'},'pause'),({'stakes':'high'},'pause'),
                   ({'goal':'unclear'},'prepare'),({'review':'missing'},'prepare'),({'simpler':'yes'},'simpler'),
                   ({'simpler':'unknown'},'simpler'),({'scope':'action'},'prepare')]
        for changes,kind in scenarios:
            choose(**changes);expect(page.locator('#choice-result')).to_have_attribute('data-kind',kind)
            expect(page.locator('#choice-result-title')).to_be_focused();expect(page.locator('#choice-boundary')).to_contain_text('No external action')
            report['scenarios']+=1
        choose(goal='unclear',inputs='restricted',stakes='high',review='missing',simpler='unknown',scope='action')
        expect(page.locator('#choice-reasons li')).to_have_count(6);report['scenarios']+=1
        page.locator('#choice-goal-clear').check();expect(page.locator('#choice-result')).to_be_hidden();expect(page.locator('#choice-result-title')).to_be_empty()
        expect(page.locator('#choice-error')).to_contain_text('Answers changed');report['scenarios']+=1
        choose();page.locator('#choice-form button[type=reset]').click()
        expect(page.locator('#choice-form input:checked')).to_have_count(0);expect(page.locator('#choice-result')).to_be_hidden();report['scenarios']+=1
        # Invalid DOM input must not become a positive suggestion.
        choose();page.locator('#choice-goal-clear').evaluate("el=>el.value='unknown-value'")
        page.locator('#choice-form button[type=submit]').click();expect(page.locator('#choice-result')).to_be_hidden()
        expect(page.locator('#choice-error')).to_contain_text('could not be checked');report['scenarios']+=1
        load();page.wait_for_timeout(100);initial=len(requests);original_url=page.url
        choose();assert len(requests)==initial;assert page.url==original_url
        if not args.offline:assert page.evaluate('localStorage.length+sessionStorage.length')==0;assert ctx.cookies()==[];report['privacy']+=1
        page.evaluate("window.dispatchEvent(new Event('pagehide'))");expect(page.locator('#choice-form input:checked')).to_have_count(0)
        choose();page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))");expect(page.locator('#choice-form input:checked')).to_have_count(0);report['privacy']+=1
        for width in [320,390,768,1440]:
            for state in ['pause','trial']:
                load();page.set_viewport_size({'width':width,'height':1000});choose(inputs='restricted' if state=='pause' else 'allowed')
                assert page.evaluate('document.documentElement.scrollWidth')<=width,(width,state);report['layouts']+=1
                if os.environ.get('SCREENSHOT_DIR') and width in [390,1440]:
                    out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                    page.evaluate('window.scrollTo(0,0)')
                    page.screenshot(path=str(out/f'ai-choice-{state}-{width}.png'),full_page=True)
                if os.environ.get('AXE_PATH') and width==390:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    scan=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)})),incomplete:r.incomplete.map(v=>v.id)}}")
                    report['axe'].append({'state':state,**scan});assert not scan['violations'],scan
                page.locator('.choice-sheet summary').click()
                page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                assert page.evaluate('document.documentElement.scrollWidth')<=width,('spacing',width,state);report['spacing']+=1
        if not args.offline:
            load();choose();page.locator('#choice-route a').focus();page.keyboard.press('Enter');expect(page).to_have_url(base+'/technology/task-brief/');report['journeys']+=1
            for parent in ['/technology/','/resources/','/notes/','/find/']:
                page.goto(base+parent);link=page.locator('main a[href="'+PATH+'"]').first
                link.evaluate('(a)=>{const d=a.closest("details");if(d)d.open=true;}')
                link.focus();page.keyboard.press('Enter')
                expect(page).to_have_url(base+PATH);report['journeys']+=1
            # Native download equals the static on-page template and local bytes.
            page.locator('.choice-sheet summary').click()
            expect(page.locator('.choice-sheet pre')).to_have_text((ROOT/'downloads/should-i-use-ai.txt').read_text())
            with page.expect_download() as item:page.locator('a[download][href="/downloads/should-i-use-ai.txt"]').click()
            assert Path(item.value.path()).read_bytes()==(ROOT/'downloads/should-i-use-ai.txt').read_bytes();report['downloads']+=1
        page.emulate_media(media='print');expect(page.locator('#choice-form')).to_be_hidden()
        page.emulate_media(media='screen');ctx.close()
        for mode in ['disabled','blocked']:
            c=browser.new_context(java_script_enabled=mode!='disabled',accept_downloads=True,reduced_motion='reduce')
            def fallback(r):
                if 'ai-task-choice.js' in r.request.url:r.abort()
                elif not args.offline and urlsplit(r.request.url).hostname=='127.0.0.1':r.continue_()
                else:r.abort()
            c.route('**/*',fallback);p=c.new_page();render(p,PATH,False)
            expect(p.locator('#choice-form')).to_be_hidden();expect(p.locator('#choice-fallback')).to_be_visible()
            expect(p.locator('.choice-rules li')).to_have_count(4);expect(p.locator('.choice-example')).to_have_count(4)
            p.locator('.choice-sheet summary').focus();p.keyboard.press('Enter');expect(p.locator('.choice-sheet pre')).to_be_visible()
            if not args.offline:
                with p.expect_download() as item:p.locator('a[download][href="/downloads/should-i-use-ai.txt"]').click()
                assert Path(item.value.path()).read_bytes()==(ROOT/'downloads/should-i-use-ai.txt').read_bytes();report['downloads']+=1
            for width in [320,390,768,1440]:
                p.set_viewport_size({'width':width,'height':1000});assert p.evaluate('document.documentElement.scrollWidth')<=width;report['layouts']+=1
            c.close();report['fallbacks']+=1
        assert not errors,errors;browser.close()
    print('AI_TASK_CHOICE_REPORT='+json.dumps(report))
finally:server.shutdown();server.server_close()
