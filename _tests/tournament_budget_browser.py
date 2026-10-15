"""Tournament budgets: reading, reserves, worksheet, search and accessible navigation."""
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
ROUTE='/poker/tournament-trip-budget/'
TITLE='What does a $400 poker tournament really cost?'

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
                page.set_viewport_size({'width':width,'height':1000})
                assert page.goto(origin+ROUTE).status==200
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                expect(page.locator('h1')).to_have_text(TITLE)
                expect(page.locator('.reader-outline').first.locator('nav a')).to_have_count(12)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
                if shots and width in [390,1440]:page.screenshot(path=str(shots/f'tournament-budget-opening-{width}.png'))
                outline=page.locator('.reader-outline').first
                outline.locator('summary').press('Enter')
                outline.locator('a[href="#three-numbers"]').press('Enter')
                expect(page.locator('#three-numbers')).to_be_in_viewport()
                table=page.locator('.budget-comparison');table.focus();table.press('ArrowRight')
                if width<768:page.wait_for_function('e=>e.scrollWidth>e.clientWidth && e.scrollLeft>0',arg=table.element_handle())
                outline.locator('a[href="#overnight"]').press('Enter')
                expect(page.locator('#overnight')).to_be_in_viewport()
                overnight=page.locator('table').filter(has=page.locator('caption',has_text='Overnight plan'))
                if shots and width in [390,1440]:
                    position(page,overnight);page.screenshot(path=str(shots/f'tournament-budget-overnight-{width}.png'))
                question=page.locator('#reserve-check').locator('..');explanation=question.locator('details > div')
                expect(explanation).not_to_be_visible()
                question.locator('summary').press('Enter');expect(explanation).to_be_visible()
                expect(explanation).to_contain_text('$649.75')
                page.locator('#payout-check').locator('..').locator('summary').press('Enter')
                expect(page.locator('#payout-check').locator('..').locator('details > div')).to_contain_text('−$534.25')
                outline.locator('a[href="#worksheet"]').press('Enter')
                expect(page.locator('#worksheet')).to_be_in_viewport()
                if shots and width in [390,1440]:
                    position(page,page.locator('#worksheet'));page.screenshot(path=str(shots/f'tournament-budget-worksheet-{width}.png'))
                page.locator('main a[href="#source-structures"]').first.press('Enter')
                source=page.locator('#source-structures');expect(source).to_be_in_viewport()
                metrics=source.evaluate('''async e=>{
                    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
                    return {top:e.getBoundingClientRect().top,header:document.querySelector('.site-header').getBoundingClientRect().bottom};
                }''')
                assert metrics['top']>=metrics['header'],('source anchor',width,metrics)
                page.add_style_tag(content=SPACING)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),('spacing',width)
                if os.environ.get('AXE_PATH') and width in [390,1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    bad=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
                    assert not bad,(width,bad);report['axe'].append({'width':width,'violations':bad})
                report['widths'].append(width)
            arrivals=['/poker/','/poker/topics/tournaments/','/poker/topics/places-to-play/','/poker/topics/safer-play/','/poker/library/','/poker/live-tournament-guide/','/poker/choosing-a-tournament/','/poker/registration-and-reentry/','/poker/first-live-tournament/','/poker/getting-started/','/poker/tournament-checklists/','/notes/']
            for route in arrivals:
                page.goto(origin+route)
                if route.startswith('/poker/topics/'):
                    page.locator('details.topic-guides > summary').press('Enter')
                if route=='/notes/':page.locator('#archive-poker summary').press('Enter')
                link=page.locator('main a[href^="'+ROUTE+'"]').first
                expect(link).to_be_visible();link.press('Enter')
                page.wait_for_url('**'+ROUTE+'*',wait_until='load');report['arrivals']+=1
            page.goto(origin+'/find/');page.locator('#find-query').fill('tournament budget');page.locator('#find-query').press('Enter')
            arrival=page.locator('.find-item a[href="'+ROUTE+'"]').first
            expect(arrival).to_be_visible();arrival.press('Enter');page.wait_for_url(origin+ROUTE,wait_until='load')
            page.goto(origin+'/find/');page.locator('#find-query').fill('opportunity cost');page.locator('#find-query').press('Enter')
            page.locator('.find-section-matches a[href="'+ROUTE+'#time"]').press('Enter')
            page.wait_for_url(origin+ROUTE+'#time',wait_until='load');expect(page.locator('#time')).to_be_in_viewport()
            download=context.request.get(origin+'/downloads/poker-tournament-trip-budget.md')
            assert download.status==200
            assert page.locator('.budget-sheet').text_content()==download.text()
            page.emulate_media(media='print');expect(page.locator('#worksheet')).to_be_visible()
            expect(page.locator('#fee-check').locator('..').locator('details > div')).to_be_visible()
            assert page.locator('main form,main input,main textarea').count()==0
            assert page.evaluate('localStorage.length===0 && sessionStorage.length===0') and context.cookies()==[]
            nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':1000})
            nojs.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            static=nojs.new_page();static.goto(origin+ROUTE)
            static.locator('.reader-outline').first.locator('summary').press('Enter')
            static.locator('.reader-outline').first.locator('a[href="#overnight"]').press('Enter')
            expect(static.locator('#overnight')).to_be_in_viewport()
            static.locator('#reserve-check').locator('..').locator('summary').press('Enter')
            expect(static.locator('#reserve-check').locator('..').locator('details')).to_have_attribute('open','')
            expect(static.locator('.budget-sheet')).to_contain_text('PRE-TAX TRIP RESULT')
            assert static.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert not errors,errors;browser.close()
    finally:server.shutdown();server.server_close()
    if shots:(shots/'tournament-budget-browser.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
