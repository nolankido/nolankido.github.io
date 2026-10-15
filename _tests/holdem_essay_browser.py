"""Beginner-guide reading, changed examples and navigation in a real browser."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json,os
from playwright.sync_api import sync_playwright,expect
from field_guide_browser import QuietHandler,ROOT
from learning_path_browser import SPACING
ROUTE='/poker/no-limit-holdem-guide/'
TITLE='No-limit Hold’em: rules, decisions and long-term thinking'

def position(page, locator):
    # Capture ordinary reading after native disclosure layout and focus scrolling
    # settle. Keep the same strict sticky-header clearance assertion.
    page.evaluate('()=>{document.activeElement.blur();return new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}')
    metrics=locator.evaluate('''async el=>{
        const header=document.querySelector('.site-header');
        window.scrollTo({top:scrollY+el.getBoundingClientRect().top-header.getBoundingClientRect().height-16,behavior:'instant'});
        await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
        return {top:el.getBoundingClientRect().top,header:header.getBoundingClientRect().bottom};
    }''')
    expect(locator).to_be_in_viewport()
    assert metrics['top']>=metrics['header'],metrics

def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    shots=Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots:shots.mkdir(parents=True,exist_ok=True)
    errors=[];report={'viewports':0,'keyboard_checks':0,'arrivals':0,'axe':[]}
    try:
        with sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**opts);context=browser.new_context(reduced_motion='reduce')
            context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            for width in [320,390,768,1440]:
                page.set_viewport_size({'width':width,'height':950});assert page.goto(origin+ROUTE).status==200
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                expect(page.locator('h1')).to_have_text(TITLE)
                expect(page.locator('details.viewer-question')).to_have_count(3)
                expect(page.locator('details.viewer-question[open]')).to_have_count(0)
                expect(page.locator('.reader-outline').first.locator('nav a')).to_have_count(13)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
                if shots and width in [390,1440]:page.screenshot(path=str(shots/f'holdem-opening-{width}.png'))
                page.locator('.reader-outline').first.locator('summary').press('Enter')
                page.locator('.reader-outline').first.locator('a[href="#draws-pot-odds-and-expected-value"]').press('Enter')
                expect(page).to_have_url(origin+ROUTE+'#draws-pot-odds-and-expected-value')
                expect(page.locator('#draws-pot-odds-and-expected-value')).to_be_in_viewport()
                page.locator('nav[aria-label="Drawing and price examples"] a[href="#worked-numerical-example-pot-odds"]').press('Enter')
                expect(page.locator('#worked-numerical-example-pot-odds')).to_be_in_viewport()
                if shots and width in [390,1440]:
                    position(page,page.locator('#worked-numerical-example-pot-odds'));page.screenshot(path=str(shots/f'holdem-price-{width}.png'))
                for q in page.locator('details.viewer-question').all():
                    q.locator('summary').press('Enter');expect(q.locator('div')).to_be_visible();report['keyboard_checks']+=1
                expect(page.locator('#guide-check-call')).to_contain_text('$9 - $2 = $7')
                expect(page.locator('#guide-check-price')).to_contain_text('$40 / $160 = 25%')
                if shots and width in [390,1440]:
                    position(page,page.locator('#guide-check-price'));page.screenshot(path=str(shots/f'holdem-practice-{width}.png'))
                page.add_style_tag(content=SPACING)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),('spacing',width)
                for table in page.locator('table.viewer-table').all():
                    assert table.evaluate('e=>e.getBoundingClientRect().right<=innerWidth+1'),('table',width)
                if os.environ.get('AXE_PATH') and width in [390,1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    bad=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
                    assert not bad,(width,bad);report['axe'].append({'width':width,'violations':bad})
                report['viewports']+=1
            for route in ['/poker/','/poker/topics/learn/','/poker/library/','/poker/start-here/','/poker/holdem-basics/','/poker/free-poker-learning-path/','/notes/']:
                page.goto(origin+route)
                if route=='/notes/':
                    page.locator('#archive-poker summary').press('Enter');expect(page.locator('#archive-poker')).to_have_attribute('open','')
                if route=='/poker/free-poker-learning-path/':
                    overview=page.locator('details.poker-details').filter(has=page.locator('a[href="'+ROUTE+'"]'))
                    expect(overview).to_have_count(1)
                    expect(overview).not_to_have_attribute('open','')
                    overview.locator('summary').press('Enter')
                    expect(overview).to_have_attribute('open','')
                link=page.locator('main a[href="'+ROUTE+'"]').first
                expect(link).to_be_visible();link.press('Enter');page.wait_for_url(origin+ROUTE,wait_until='load');report['arrivals']+=1
            page.goto(origin+'/find/');page.locator('#find-query').fill('draws');page.locator('#find-query').press('Enter')
            link=page.locator('.find-section-matches a[href="'+ROUTE+'#draws-pot-odds-and-expected-value"]')
            expect(link).to_be_visible();link.press('Enter');page.wait_for_url(origin+ROUTE+'#draws-pot-odds-and-expected-value',wait_until='load')
            expect(page.locator('#draws-pot-odds-and-expected-value')).to_be_in_viewport()
            page.locator('#guide-check-call summary').press('Enter')
            repair=page.locator('#guide-check-call a[href="/poker/first-decisions/#chips-owed"]');repair.press('Enter')
            page.wait_for_url(origin+'/poker/first-decisions/#chips-owed',wait_until='load');expect(page.locator('#chips-owed')).to_be_in_viewport()
            page.goto(origin+ROUTE);page.emulate_media(media='print');expect(page.locator('#sources-and-next-steps')).to_be_visible()
            assert page.locator('main input,main form,main textarea').count()==0
            assert page.evaluate('localStorage.length===0 && sessionStorage.length===0') and context.cookies()==[]
            nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':950})
            nojs.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            static=nojs.new_page();static.goto(origin+'/poker/')
            static.locator('main a[href="'+ROUTE+'"]').first.press('Enter');static.wait_for_url(origin+ROUTE,wait_until='load')
            static.locator('.reader-outline').first.locator('summary').press('Enter')
            static.locator('.reader-outline').first.locator('a[href="#put-the-ideas-into-practice"]').press('Enter')
            expect(static.locator('#put-the-ideas-into-practice')).to_be_in_viewport()
            static.locator('#guide-check-price summary').press('Enter');expect(static.locator('#guide-check-price div')).to_be_visible()
            assert static.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert not errors,errors;browser.close()
    finally:server.shutdown();server.server_close()
    print('PASS: beginner overview, keyboard outline and checks, repair route, lossless search, four widths, text spacing, print, no-JavaScript and no new collection surface.')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
