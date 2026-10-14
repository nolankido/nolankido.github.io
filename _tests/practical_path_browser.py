"""Native four-stage path, complete workbook, reflow and scoped accessibility."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
import sys
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build
import practical_path

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port)
report={'layouts':0,'text_spacing':0,'journeys':0,'entry_journeys':0,'previews':0,'downloads':0,'axe':[]}
errors=[];writes=[]
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        for scripts in [True,False]:
            ctx=browser.new_context(java_script_enabled=scripts,reduced_motion='reduce')
            ctx.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            ctx.on('request',lambda r:writes.append(r.url) if r.method not in {'GET','HEAD'} else None)
            page=ctx.new_page();page.set_default_timeout(15000)
            page.on('pageerror',lambda e:errors.append(str(e)))
            for width in [320,390,768,1440]:
                page.set_viewport_size({'width':width,'height':950})
                page.goto(base+'/technology/')
                if scripts and width in [390,1440] and os.environ.get('SCREENSHOT_DIR'):
                    out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                    page.evaluate('document.fonts.ready')
                    page.locator('.topic-introduction').screenshot(path=str(out/f'technology-entry-{width}.png'))
                for target,heading,next_link in [
                    ('practical-ai-path','#practical-ai-path-title','.ai-path-steps a[href="/technology/should-i-use-ai/"]'),
                    ('working-examples','#working-examples','.practical-work-grid a[href="/technology/task-brief/"]'),
                    ('technology-path','#technology-path','.everyday-task-grid a[href="/living-well/scattered-notes-to-next-step/"]'),
                    ('technology-reading','#technology-reading-title','#technology-reading a[href="/technology/check-ai-summary/"]'),
                ]:
                    page.goto(base+'/technology/')
                    link=page.locator('.technology-jumps a[href="#'+target+'"]')
                    link.focus();expect(link).to_be_focused();page.keyboard.press('Enter')
                    expect(page).to_have_url(base+'/technology/#'+target)
                    expect(page.locator(heading)).to_be_in_viewport()
                    page.keyboard.press('Tab')
                    expect(page.locator(next_link).first).to_be_focused()
                    expect(page.locator(next_link).first).to_be_in_viewport()
                    report['entry_journeys']+=1
                page.goto(base+'/technology/')
                expect(page.locator('.ai-path-steps li')).to_have_count(4)
                expect(page.locator('#practical-ai-path-title')).to_have_text('Decide. Brief. Check. Measure.')
                details=page.locator('.ai-workbook details');details.locator('summary').focus();page.keyboard.press('Enter')
                expect(details).to_have_attribute('open','')
                assert details.locator('pre').text_content()==(ROOT/practical_path.WORKBOOK).read_text()
                report['previews']+=1
                assert page.evaluate('document.documentElement.scrollWidth')<=width
                report['layouts']+=1
                page.evaluate('css=>{const s=document.createElement("style");s.textContent=css;document.head.appendChild(s)}','*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                assert page.evaluate('document.documentElement.scrollWidth')<=width
                report['text_spacing']+=1
                if scripts and width in [390,1440] and os.environ.get('SCREENSHOT_DIR'):
                    out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                    page.locator('#practical-ai-path').screenshot(path=str(out/f'practical-path-{width}.png'))
                if scripts and width==390 and os.environ.get('AXE_PATH'):
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    audit=page.evaluate("async()=>{const r=await axe.run(document.querySelector('#practical-ai-path'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>v.id),incomplete:r.incomplete.map(v=>v.id)}}")
                    assert not audit['violations'],audit;report['axe'].append(audit)
            page.goto(base+'/technology/#practical-ai-workbook')
            with page.expect_download() as event:page.locator('a[download][href="/downloads/practical-ai-workbook.txt"]').click()
            assert Path(event.value.path()).read_bytes()==(ROOT/practical_path.WORKBOOK).read_bytes()
            report['downloads']+=1
            for entry in practical_path.records(build.public_pages(),ROOT):
                page.goto(base+'/technology/#practical-ai-path')
                link=page.locator('.ai-path-steps a[href="'+entry['path']+'"]')
                with page.expect_navigation(wait_until='load'):link.press('Enter')
                expect(page).to_have_url(base+entry['path']);report['journeys']+=1
            page.goto(base+'/resources/')
            link=page.locator('a[href="/technology/#practical-ai-path"]')
            with page.expect_navigation(wait_until='load'):link.press('Enter')
            expect(page).to_have_url(base+'/technology/#practical-ai-path');report['journeys']+=1
            ctx.close()
        browser.close()
    assert not errors,errors
    assert not writes,writes
    report['status']='pass';print(json.dumps(report,indent=2))
finally:
    server.shutdown();server.server_close()
