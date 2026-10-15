"""Expanded short-stack lesson: keyboard arithmetic, readable tables and downloads."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json,os
from playwright.sync_api import sync_playwright,expect
from field_guide_browser import QuietHandler,ROOT
from learning_path_browser import SPACING
from holdem_essay_browser import position
from test_short_stack_flagship import ROUTE,ARRIVALS
TITLE='A short stack is a situation, not a chart.'

def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    shots=Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots:shots.mkdir(parents=True,exist_ok=True)
    report={'widths':[],'arrivals':0,'keyboard_checks':0,'scrolling_tables':0,'axe':[]};errors=[];writes=[]
    try:
        with sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**opts);context=browser.new_context(reduced_motion='reduce')
            context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:writes.append(r.url) if r.method not in ['GET','HEAD'] else None)
            for width in [320,390,768,1440]:
                page.set_viewport_size({'width':width,'height':1000})
                assert page.goto(origin+ROUTE).status==200
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                expect(page.locator('h1')).to_have_text(TITLE)
                outline=page.locator('.reader-outline').first
                expect(outline.locator('nav a')).to_have_count(12)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
                if shots and width in [390,1440]:page.screenshot(path=str(shots/f'short-stack-opening-{width}.png'))
                outline.locator('summary').press('Enter');outline.locator('a[href="#models"]').press('Enter')
                expect(page.locator('#models')).to_be_in_viewport()
                q=page.locator('#model-check').locator('..');expect(q.locator('details > div')).not_to_be_visible()
                q.locator('summary').press('Enter');expect(q.locator('details > div')).to_contain_text('two separate specifications')
                outline.locator('a[href="#icm-call"]').press('Enter');expect(page.locator('#icm-call')).to_be_in_viewport()
                region=page.get_by_role('region',name='Four-player ICM outcome comparison')
                expect(region).to_contain_text('$22.946148');expect(region).to_contain_text('$33.603175')
                assert region.evaluate('e=>e.getBoundingClientRect().right<=innerWidth+1 && e.getBoundingClientRect().left>=0'),width
                if region.evaluate('e=>e.scrollWidth>e.clientWidth+1'):
                    region.focus();region.press('ArrowRight')
                    page.wait_for_function('document.querySelector(".short-stack-table").scrollLeft>0')
                    region.evaluate('e=>e.scrollTo({left:0,behavior:"instant"})');report['scrolling_tables']+=1
                if shots and width in [390,1440]:
                    position(page,region);page.screenshot(path=str(shots/f'short-stack-icm-{width}.png'))
                q=page.locator('#icm-check').locator('..');q.locator('summary').press('Enter')
                expect(q.locator('details > div')).to_contain_text('yes for chip EV, no for classic ICM')
                outline.locator('a[href="#study-loop"]').press('Enter');expect(page.locator('#study-loop')).to_be_in_viewport()
                sheet=page.locator('.short-stack-sheet');expect(sheet).to_contain_text('Deal terms, locked awards and residual prizes')
                if shots and width in [390,1440]:
                    position(page,sheet);page.screenshot(path=str(shots/f'short-stack-worksheet-{width}.png'))
                q=page.locator('#ante-check').locator('..');q.locator('summary').press('Enter')
                expect(q.locator('details > div')).to_contain_text('initial pot is 2.5 BB')
                page.locator('main a[href="#source-icm"]').first.press('Enter');source=page.locator('#source-icm');expect(source).to_be_in_viewport()
                metrics=source.evaluate('''async e=>{await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return {top:e.getBoundingClientRect().top,header:document.querySelector('.site-header').getBoundingClientRect().bottom}}''')
                assert metrics['top']>=metrics['header'],('source anchor',width,metrics)
                page.add_style_tag(content=SPACING);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),('spacing',width)
                if os.environ.get('AXE_PATH') and width in [390,1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    bad=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
                    assert not bad,(width,bad);report['axe'].append({'width':width,'violations':bad})
                report['widths'].append(width);report['keyboard_checks']+=3
            for route in ARRIVALS:
                page.goto(origin+route)
                if route.startswith('/poker/topics/'):page.locator('details.topic-guides > summary').press('Enter')
                if route=='/notes/':page.locator('#archive-poker summary').press('Enter')
                link=page.locator('main a[href^="'+ROUTE+'"]').first;expect(link).to_be_visible();link.press('Enter')
                page.wait_for_url('**'+ROUTE+'*',wait_until='load');report['arrivals']+=1
            for query in ['15BB','short stack']:
                page.goto(origin+'/find/');page.locator('#find-query').fill(query);page.locator('#find-query').press('Enter')
                arrival=page.locator('.find-item a[href="'+ROUTE+'"]').first;expect(arrival).to_be_visible();arrival.press('Enter');page.wait_for_url(origin+ROUTE,wait_until='load')
            page.goto(origin+'/poker/find/');page.locator('#finder-search').fill('15BB');page.locator('#finder-search').press('Enter')
            card=page.locator('[data-id="poker-short-stack-decisions"]');expect(card).to_be_visible();card.locator('a[href="'+ROUTE+'"]').first.press('Enter')
            page.wait_for_url(origin+ROUTE,wait_until='load')
            page.goto(origin+'/find/');page.locator('#find-query').fill('classic ICM');page.locator('#find-query').press('Enter')
            page.locator('.find-section-matches a[href="'+ROUTE+'#icm-call"]').press('Enter')
            page.wait_for_url(origin+ROUTE+'#icm-call',wait_until='load');expect(page.locator('#icm-call')).to_be_in_viewport()
            for name in ['poker-short-stack-record.md','short-stack-icm-example.py']:
                download=context.request.get(origin+'/downloads/'+name);assert download.status==200
                assert download.body()==(ROOT/'downloads'/name).read_bytes()
                if name.endswith('.md'):assert page.locator('.short-stack-sheet').text_content()==download.text()
            page.emulate_media(media='print')
            for key in ['model-check','icm-check','ante-check']:expect(page.locator('#'+key).locator('..').locator('details > div')).to_be_visible()
            assert page.locator('main form,main input,main textarea').count()==0
            assert page.evaluate('localStorage.length===0 && sessionStorage.length===0') and context.cookies()==[]
            nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':1000})
            nojs.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            static=nojs.new_page();static.goto(origin+ROUTE)
            static.locator('.reader-outline').first.locator('summary').press('Enter');static.locator('.reader-outline').first.locator('a[href="#depths"]').press('Enter')
            expect(static.locator('#depths')).to_be_in_viewport()
            static.locator('#model-check').locator('..').locator('summary').press('Enter');expect(static.locator('#model-check').locator('..').locator('details')).to_have_attribute('open','')
            expect(static.locator('.short-stack-sheet')).to_contain_text('Who covers whom after dead antes')
            assert static.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert not errors,errors;assert not writes,writes;browser.close()
    finally:server.shutdown();server.server_close()
    if shots:(shots/'short-stack-browser.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
