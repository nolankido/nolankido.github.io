"""First-session guide: explained practice, keyboard reading and integration."""
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
from native_fragment import follow_fragment
ROUTE='/poker/getting-started/'
TITLE='Get started with no-limit Texas Hold’em'

def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    shots=Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots:shots.mkdir(parents=True,exist_ok=True)
    report={'widths':[],'arrivals':0,'axe':[]};errors=[]
    try:
        with sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**opts)
            context=browser.new_context(reduced_motion='reduce')
            context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            for width in [320,390,768,1440]:
                page.set_viewport_size({'width':width,'height':950})
                assert page.goto(origin+ROUTE).status==200
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                expect(page.locator('h1')).to_have_text(TITLE)
                expect(page.locator('.reader-outline').first.locator('nav a')).to_have_count(15)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
                if shots and width in [390,1440]:page.screenshot(path=str(shots/f'getting-started-opening-{width}.png'))
                page.locator('.reader-outline').first.locator('summary').press('Enter')
                follow_fragment(page, page.locator('.reader-outline').first.locator('a[href="#format"]'), '#format')
                table=page.locator('.session-table');table.focus();table.press('ArrowRight')
                if width<768:page.wait_for_function('e=>e.scrollWidth>e.clientWidth && e.scrollLeft>0',arg=table.element_handle())
                follow_fragment(page, page.locator('.reader-outline').first.locator('a[href="#math"]'), '#math')
                question=page.locator('#price-check').locator('..');explanation=question.locator('details > div')
                expect(explanation).not_to_be_visible()
                question.locator('summary').press('Enter');expect(explanation).to_be_visible()
                expect(explanation).to_contain_text('+$2.40')
                if shots and width in [390,1440]:
                    position(page,page.locator('#price-check'));page.screenshot(path=str(shots/f'getting-started-practice-{width}.png'))
                follow_fragment(page, page.locator('.reader-outline').first.locator('a[href="#month"]'), '#month')
                if shots and width in [390,1440]:
                    position(page,page.locator('#month'));page.screenshot(path=str(shots/f'getting-started-month-{width}.png'))
                follow_fragment(page, page.locator('main a[href="#source-tda"]').first, '#source-tda')
                source=page.locator('#source-tda');expect(source).to_be_in_viewport()
                metrics=source.evaluate('''async e=>{
                    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
                    return {top:e.getBoundingClientRect().top,header:document.querySelector('.site-header').getBoundingClientRect().bottom};
                }''')
                assert metrics['top']>=metrics['header'],('citation clearance',width,metrics)
                page.add_style_tag(content=SPACING)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),('spacing',width)
                if os.environ.get('AXE_PATH') and width in [390,1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    bad=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
                    assert not bad,(width,bad);report['axe'].append({'width':width,'violations':bad})
                report['widths'].append(width)
            arrivals=['/poker/','/poker/topics/learn/','/poker/topics/cash-games/','/poker/topics/tournaments/','/poker/library/','/poker/free-poker-learning-path/','/poker/start-here/','/poker/no-limit-holdem-guide/','/poker/first-live-cash-game/','/poker/first-live-tournament/','/poker/comics/','/notes/']
            for route in arrivals:
                page.goto(origin+route)
                if route.startswith('/poker/topics/'):
                    page.locator('details.topic-guides > summary').press('Enter')
                    expect(page.locator('details.topic-guides')).to_have_attribute('open','')
                if route=='/notes/':page.locator('#archive-poker summary').press('Enter')
                link=page.locator('main a[href="'+ROUTE+'"]').first
                expect(link).to_be_visible();link.press('Enter')
                page.wait_for_url(origin+ROUTE,wait_until='load');report['arrivals']+=1
            page.goto(origin+'/find/');page.locator('#find-query').fill('beginner poker');page.locator('#find-query').press('Enter')
            arrival=page.locator('.find-item a[href="'+ROUTE+'"]').first
            expect(arrival).to_be_visible();arrival.press('Enter');page.wait_for_url(origin+ROUTE,wait_until='load')
            page.goto(origin+'/find/');page.locator('#find-query').fill('first month');page.locator('#find-query').press('Enter')
            page.locator('.find-section-matches a[href="'+ROUTE+'#month"]').press('Enter')
            page.wait_for_url(origin+ROUTE+'#month',wait_until='load');expect(page.locator('#month')).to_be_in_viewport()
            assert context.request.get(origin+'/downloads/poker-first-session.md').status==200
            page.emulate_media(media='print');expect(page.locator('#checklist')).to_be_visible()
            expect(page.locator('#price-check').locator('..').locator('details > div')).to_be_visible()
            assert page.locator('main form,main input,main textarea').count()==0
            assert page.evaluate('localStorage.length===0 && sessionStorage.length===0') and context.cookies()==[]
            nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':950})
            nojs.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            static=nojs.new_page();static.goto(origin+ROUTE)
            static.locator('.reader-outline').first.locator('summary').press('Enter')
            static.locator('.reader-outline').first.locator('a[href="#live"]').press('Enter')
            expect(static.locator('#live')).to_be_in_viewport()
            static.locator('#chip-check').locator('..').locator('summary').press('Enter')
            expect(static.locator('#chip-check').locator('..').locator('details')).to_have_attribute('open','')
            assert static.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert not errors,errors;browser.close()
    finally:server.shutdown();server.server_close()
    print('PASS: explained practice, keyboard outline and table scrolling, twelve integrated routes, section search, four widths, text spacing, print, no JavaScript and no data collection.')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
