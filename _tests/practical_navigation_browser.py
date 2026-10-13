"""Search arrivals can move between AI checkpoints with native keyboard links."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os

from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
STAGES=(
    ('/technology/should-i-use-ai/','Decide'),
    ('/technology/task-brief/','Brief'),
    ('/technology/check-ai-answers/','Check'),
    ('/technology/ai-time-savings/','Measure'),
)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass


server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port)
report={'layouts':0,'text_spacing':0,'sibling_journeys':0,'onward_journeys':0,'returns':0,'downloads':0,'print_views':0,'tool_return':0,'axe':[]}
errors=[];writes=[];requests=[]
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        for scripts in [True,False]:
            context=browser.new_context(java_script_enabled=scripts,reduced_motion='reduce',accept_downloads=True)
            context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            context.on('request',lambda r:requests.append(r.url))
            context.on('request',lambda r:writes.append(r.url) if r.method not in {'GET','HEAD'} else None)
            page=context.new_page();page.set_default_timeout(15000)
            page.on('pageerror',lambda error:errors.append(str(error)))
            for path,label in STAGES:
                for width in [320,390,768,1440]:
                    page.set_viewport_size({'width':width,'height':1000})
                    page.goto(base+path,wait_until='load')
                    nav=page.locator('#ai-workflow-navigation')
                    expect(nav.locator('ol li')).to_have_count(4)
                    expect(nav.locator('ol a')).to_have_count(3)
                    expect(nav.locator('[aria-current="page"]')).to_have_count(1)
                    expect(nav.locator('[aria-current="page"]')).to_contain_text(label)
                    expect(nav.locator('[aria-current="page"] a')).to_have_count(0)
                    expect(nav).to_contain_text('Save results in your own notes before moving between pages.')
                    assert page.evaluate('document.documentElement.scrollWidth')<=width
                    report['layouts']+=1
                    if scripts and width in [390,1440] and os.environ.get('SCREENSHOT_DIR'):
                        out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                        name=path.strip('/').split('/')[-1]
                        page.screenshot(path=str(out/f'ai-workflow-arrival-{name}-{width}.png'))
                    page.evaluate('css=>{const s=document.createElement("style");s.textContent=css;document.head.appendChild(s)}','*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                    assert page.evaluate('document.documentElement.scrollWidth')<=width
                    report['text_spacing']+=1
                    if scripts and width==390 and os.environ.get('AXE_PATH'):
                        page.add_script_tag(path=os.environ['AXE_PATH'])
                        audit=page.evaluate("async()=>{const r=await axe.run(document.querySelector('#ai-workflow-navigation'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>v.id),incomplete:r.incomplete.map(v=>v.id)}}")
                        assert not audit['violations'],audit
                        report['axe'].append({'path':path,**audit})
                for destination,_ in STAGES:
                    if destination==path: continue
                    page.goto(base+path,wait_until='load')
                    link=page.locator('#ai-workflow-navigation ol a[href="'+destination+'"]')
                    with page.expect_navigation(wait_until='load'): link.press('Enter')
                    expect(page).to_have_url(base+destination)
                    report['sibling_journeys']+=1
                page.goto(base+path,wait_until='load')
                onward=page.locator('.ai-workflow-onward a')
                destination=onward.get_attribute('href')
                with page.expect_navigation(wait_until='load'): onward.press('Enter')
                expect(page).to_have_url(base+destination)
                report['onward_journeys']+=1
                page.go_back(wait_until='load')
                expect(page).to_have_url(base+path)
                expect(page.locator('#ai-workflow-navigation [aria-current="page"]')).to_contain_text(label)
                report['returns']+=1
                with page.expect_download() as item:
                    page.locator('#ai-workflow-navigation a[download]').click()
                assert Path(item.value.path()).read_bytes()==(ROOT/'downloads/practical-ai-workbook.txt').read_bytes()
                report['downloads']+=1
                page.emulate_media(media='print')
                expect(page.locator('#ai-workflow-navigation')).to_be_hidden()
                expect(page.locator('.ai-workflow-onward')).to_be_hidden()
                expect(page.locator('h1')).to_be_visible()
                report['print_views']+=1
                page.emulate_media(media='screen')
            if scripts:
                page.goto(base+'/technology/task-brief/',wait_until='load')
                page.locator('#brief-goal').fill('PRIVATE-NAVIGATION-FIXTURE')
                link=page.locator('#ai-workflow-navigation a[href="/technology/check-ai-answers/"]')
                with page.expect_navigation(wait_until='load'): link.press('Enter')
                page.go_back(wait_until='load')
                expect(page.locator('#brief-goal')).to_have_value('')
                assert all('PRIVATE-NAVIGATION-FIXTURE' not in url for url in requests)
                assert page.evaluate('localStorage.length+sessionStorage.length')==0
                assert context.cookies()==[]
                report['tool_return']+=1
            context.close()
        browser.close()
    assert not errors,errors
    assert not writes,writes
    report['status']='pass';print(json.dumps(report,indent=2))
finally:
    server.shutdown();server.server_close()
