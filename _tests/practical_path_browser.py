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
report={'layouts':0,'text_spacing':0,'journeys':0,'entry_journeys':0,'previews':0,'downloads':0,'axe':[],
        'case_disclosures':0,'case_source_journeys':0,'case_decisions':0,'case_downloads':0,
        'case_layouts':0,'case_text_spacing':0}
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
                expect(page.locator('#practical-ai-path .ai-path-steps li')).to_have_count(4)
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
                # Inspect the recorded sources and corrections with native HTML,
                # including fragment navigation that opens a closed disclosure.
                # Reset the earlier text-spacing overrides before the case baseline.
                page.reload()
                page.goto(base+'/technology/#notes-to-plan-case')
                case=page.locator('#notes-to-plan-case')
                sources=case.locator('#notes-case-source-record')
                corrections=case.locator('#notes-case-revisions')
                for disclosure in [sources,corrections]:
                    expect(disclosure).not_to_have_attribute('open','')
                    summary=disclosure.locator('summary')
                    summary.focus();expect(summary).to_be_focused();page.keyboard.press('Enter')
                    expect(disclosure).to_have_attribute('open','')
                    report['case_disclosures']+=1
                expect(sources.locator('q[data-case-source]')).to_have_count(5)
                expect(corrections.locator('[data-case-check]')).to_have_count(5)
                for label,target in [('S1','notes-source-commitments'),('S2','notes-source-action'),
                                     ('S3','notes-source-deadline'),('S4','notes-source-promises'),
                                     ('S5','notes-source-stop')]:
                    sources.locator('summary').press('Enter')
                    expect(sources).not_to_have_attribute('open','')
                    quote=sources.locator('q[data-case-source="'+label+'"]')
                    expect(quote).to_be_hidden()
                    link=corrections.locator('[data-case-check="'+label+'"] a[href="#'+target+'"]')
                    link.focus();expect(link).to_be_focused();page.keyboard.press('Enter')
                    expect(page).to_have_url(base+'/technology/#'+target)
                    expect(sources).to_have_attribute('open','')
                    expect(quote).to_be_visible();expect(quote).to_be_in_viewport()
                    expect(corrections).to_have_attribute('open','')
                    report['case_source_journeys']+=1
                assert page.evaluate('document.documentElement.scrollWidth')<=width,('case',scripts,width)
                report['case_layouts']+=1
                page.evaluate('css=>{const s=document.createElement("style");s.textContent=css;document.head.appendChild(s)}','*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                assert page.evaluate('document.documentElement.scrollWidth')<=width,('case-spacing',scripts,width)
                report['case_text_spacing']+=1
                if scripts and width in [390,1440] and os.environ.get('SCREENSHOT_DIR'):
                    out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                    corrections.screenshot(path=str(out/f'public-source-corrections-{width}.png'))
                if scripts and width==390 and os.environ.get('AXE_PATH'):
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    audit=page.evaluate("async()=>{const r=await axe.run(document.querySelector('#notes-to-plan-case'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>v.id),incomplete:r.incomplete.map(v=>v.id)}}")
                    assert not audit['violations'],audit;report['axe'].append({'scope':'notes-to-plan-case',**audit})
                for disclosure in [sources,corrections]:
                    disclosure.locator('summary').press('Enter')
                    expect(disclosure).not_to_have_attribute('open','')
                decision=case.locator('.entry-jumps a[href="#notes-case-decision"]')
                decision.focus();page.keyboard.press('Enter')
                expect(page).to_have_url(base+'/technology/#notes-case-decision')
                expect(case.locator('#notes-case-decision')).to_be_in_viewport()
                expect(case.locator('ol[aria-label="Your decision before using the note"] > li')).to_have_count(3)
                expect(case.locator('a[download]')).to_be_visible()
                report['case_decisions']+=1
            page.goto(base+'/technology/#notes-case-decision')
            with page.expect_download() as event:page.locator('#notes-to-plan-case a[download]').press('Enter')
            assert event.value.suggested_filename=='practical-ai-workbook.txt'
            assert Path(event.value.path()).read_bytes()==(ROOT/practical_path.WORKBOOK).read_bytes()
            report['case_downloads']+=1
            page.goto(base+'/technology/#practical-ai-workbook')
            with page.expect_download() as event:page.locator('.ai-workbook a[download][href="/downloads/practical-ai-workbook.txt"]').click()
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
