"""Construct actual hands, recover from mistakes and continue the existing course."""
from functools import partial
from http.server import ThreadingHTTPServer
from itertools import combinations
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
from playwright.sync_api import sync_playwright, expect
from field_guide_browser import QuietHandler, ROOT
from learning_path_browser import SPACING
from test_viewer_guides import five, best

ROUTE = '/poker/free-poker-learning-path/'
CASES = json.loads((ROOT/'_source/poker/hand-lab.json').read_text())['cases']


def enter(page, target):
    target.focus(); page.keyboard.press('Enter')


def select(page, item, cards):
    for code in cards:
        field=item.locator('input[data-card="'+code+'"]')
        field.focus(); page.keyboard.press('Space')


def flow_ok(page):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')


def axe(page):
    page.add_script_tag(path=os.environ['AXE_PATH'])
    bad=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
    assert not bad,bad
    return bad


def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    shots=Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots:shots.mkdir(parents=True,exist_ok=True)
    report={'constructed_hands':0,'equivalent_selections':0,'lesson_arrivals':0,'fallbacks':0,'delayed_font_arrivals':0,'axe':[]}
    errors=[]
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
                enter(page,page.locator('.course-entry-actions a[href="#card-basics"]'))
                expect(page.locator('#card-basics-title')).to_be_in_viewport()
                assert page.locator('#card-basics-title').evaluate("el=>el.getBoundingClientRect().top >= document.querySelector('.site-header').getBoundingClientRect().bottom")
                expect(page.locator('.hand-lab-rankings')).not_to_have_attribute('open','')
                enter(page,page.locator('.hand-lab-rankings > summary'))
                expect(page.locator('.hand-lab-rankings .viewer-rankings')).to_be_visible()
                flow_ok(page)
                enter(page,page.locator('.hand-lab-rankings > summary'))
                root=page.locator('[data-hand-lab]')
                expect(root).to_have_class('hand-lab hand-lab-enhanced')
                expect(root.locator('[data-lab-case]:visible')).to_have_count(1)
                requests=[];listener=lambda r:requests.append(r.url);page.on('request',listener)
                for index,case in enumerate(CASES):
                    item=root.locator('#hand-lab-'+case['id'])
                    expect(item).to_be_visible()
                    expect(item.locator('input:checked')).to_have_count(0)
                    expect(item.locator('[data-lab-answer]')).to_be_hidden()
                    expect(root.locator('[data-lab-next]')).to_be_disabled()
                    if index:
                        expect(item.locator('h3')).to_be_focused()
                        assert item.evaluate("el=>el.getBoundingClientRect().top >= document.querySelector('.site-header').getBoundingClientRect().bottom")
                    if index==0:
                        enter(page,item.locator('[data-lab-check]'))
                        expect(item.locator('[data-lab-feedback]')).to_contain_text('exactly five')
                        select(page,item,case['solution'][:4])
                        enter(page,item.locator('[data-lab-check]'))
                        expect(item.locator('[data-lab-feedback]')).to_contain_text('selected 4')
                        expect(root.locator('[data-lab-next]')).to_be_disabled()
                        enter(page,item.locator('[data-lab-clear]'))
                        wrong=next(list(cs) for cs in combinations(case['hero']+case['board'],5) if five(cs)[0]==best(case['hero']+case['board'])[0] and five(cs)<best(case['hero']+case['board']))
                        select(page,item,wrong);enter(page,item.locator('[data-lab-check]'))
                        expect(item.locator('[data-lab-feedback]')).to_contain_text('ranks or side cards are lower')
                        expect(root.locator('[data-lab-next]')).to_be_enabled()
                        enter(page,item.locator('[data-lab-clear]'))
                        expect(item.locator('[data-lab-feedback]')).to_have_text('')
                        expect(root.locator('[data-lab-next]')).to_be_disabled()
                    if case['id']=='board-straight':
                        wrong=next(list(cs) for cs in combinations(case['hero']+case['board'],5) if five(cs)[0]!=case['category'])
                        select(page,item,wrong);enter(page,item.locator('[data-lab-check]'))
                        expect(item.locator('[data-lab-feedback]')).to_contain_text('strongest available category')
                        enter(page,item.locator('[data-lab-hint] > summary'))
                        expect(item.locator('[data-lab-hint] > div')).to_be_visible()
                        enter(page,item.locator('[data-lab-clear]'))
                    if case['id']=='flush':
                        enter(page,item.locator('[data-lab-show]'))
                        expect(item.locator('[data-lab-answer]')).to_be_visible()
                        expect(root.locator('[data-lab-next]')).to_be_enabled()
                    solution=case['solution'] if case['id']!='two-pair' else ['Ac','Ad','Kc','Kd','Th']
                    select(page,item,solution);enter(page,item.locator('[data-lab-check]'))
                    expect(item.locator('[data-lab-feedback]')).to_contain_text('match the strongest available hand')
                    expect(item.locator('[data-lab-answer]')).to_be_visible()
                    if case['id']=='two-pair':report['equivalent_selections']+=1
                    if case['id']=='full-house':
                        enter(page,root.locator('[data-lab-back]'))
                        previous=root.locator('#hand-lab-flush')
                        expect(previous.locator('input:checked')).to_have_count(5)
                        expect(previous.locator('[data-lab-feedback]')).to_contain_text('strongest available hand')
                        enter(page,root.locator('[data-lab-next]'))
                        expect(item.locator('input:checked')).to_have_count(5)
                    flow_ok(page)
                    if shots and width in [390,1440] and case['id']=='two-pair':
                        item.evaluate("el=>scrollTo({top:scrollY+el.getBoundingClientRect().top-document.querySelector('.site-header').getBoundingClientRect().height-20,behavior:'instant'})")
                        page.screenshot(path=str(shots/f'hand-lab-selected-{width}.png'))
                    enter(page,root.locator('[data-lab-next]'))
                    report['constructed_hands']+=1
                expect(root.locator('[data-lab-review]')).to_be_visible()
                expect(root.locator('[data-lab-review-list] > li')).to_have_count(10)
                expect(root.locator('[data-lab-progress]')).to_contain_text('10 of 10')
                expect(root.locator('[data-lab-review-list] > li').nth(0)).to_contain_text('weaker selection')
                expect(root.locator('[data-lab-review-list] > li').nth(4)).to_contain_text('weaker selection')
                expect(root.locator('[data-lab-review-list] > li').nth(5)).to_contain_text('hint or worked solution')
                expect(root.locator('[data-lab-review-list] > li').nth(1)).to_contain_text('A strongest selection was checked before')
                assert not requests,requests
                page.remove_listener('request',listener)
                page.add_style_tag(content=SPACING);flow_ok(page)
                if os.environ.get('AXE_PATH') and width in [390,1440]:report['axe'].append({'width':width,'violations':axe(page)})
                enter(page,root.locator('[data-lab-back]'))
                expect(root.locator('#hand-lab-ace-low input:checked')).to_have_count(5)
                enter(page,root.locator('[data-lab-next]'))
                enter(page,root.locator('[data-lab-restart]'))
                expect(root.locator('input:checked')).to_have_count(0)
                expect(root.locator('[data-lab-review-list] > li')).to_have_count(0)
                expect(root.locator('[data-lab-next]')).to_be_disabled()
            page.goto(origin+ROUTE+'#hand-lab-ace-low')
            root=page.locator('[data-hand-lab]');item=root.locator('#hand-lab-ace-low')
            expect(item).to_be_visible();expect(item.locator('h3')).to_be_in_viewport()
            enter(page,item.locator('[data-lab-show]'));enter(page,root.locator('[data-lab-next]'))
            expect(root.locator('[data-lab-review-list] > li')).to_have_count(1)
            expect(root.locator('[data-lab-progress]')).to_contain_text('1 of 10')
            enter(page,root.locator('[data-lab-review-list] a[href="#hand-lab-ace-low"]'))
            expect(item).to_be_visible();expect(item.locator('h3')).to_be_focused()
            for slug,ident in [('first-decisions','pair'),('first-flop-decisions','three-kind'),('turn-and-river-decisions','two-pair')]:
                page.goto(origin+'/poker/'+slug+'/')
                enter(page,page.locator('.course-lesson-options > summary'))
                href=ROUTE+'#hand-lab-'+ident
                enter(page,page.locator('.course-first-pass a[href="'+href+'"]'))
                expect(page).to_have_url(origin+href)
                expect(page.locator('[data-hand-lab]')).to_have_class('hand-lab hand-lab-enhanced')
                expect(page.locator('#hand-lab-'+ident)).to_be_visible()
                expect(page.locator('#hand-lab-'+ident+' h3')).to_be_in_viewport()
                report['lesson_arrivals']+=1
            page.goto(origin+'/poker/beginner-practice/')
            enter(page,page.locator('main a[href="'+ROUTE+'#card-basics"]'))
            expect(page.locator('#card-basics-title')).to_be_in_viewport()
            page.goto(origin+'/poker/find/')
            page.locator('#finder-search').fill('four matching cards are shared')
            card=page.locator('[data-finder-card]:visible').filter(has=page.locator('h3 a[href="'+ROUTE+'"]'))
            link=card.locator('.finder-jump a')
            expect(link).to_have_attribute('href',ROUTE+'#hand-lab-four-kind')
            enter(page,link)
            expect(page.locator('[data-hand-lab]')).to_have_class('hand-lab hand-lab-enhanced')
            expect(page.locator('[data-lab-case]:visible')).to_have_id('hand-lab-four-kind')
            page.emulate_media(media='print')
            expect(page.locator('[data-lab-case]:visible')).to_have_count(10)
            expect(page.locator('[data-lab-answer]:visible')).to_have_count(10)
            expect(page.locator('.hand-lab-rankings .viewer-rankings')).to_be_visible()
            expect(page.locator('[data-lab-check]:visible')).to_have_count(0)
            expect(page.locator('[data-hand-lab] input:visible')).to_have_count(0)
            page.emulate_media(media='screen')
            assert page.evaluate('localStorage.length===0 && sessionStorage.length===0') and context.cookies()==[]
            for mode in ['no-js','blocked','invalid-bank']:
                fallback=browser.new_context(java_script_enabled=mode!='no-js',viewport={'width':390,'height':950})
                def route(request):
                    u=urlsplit(request.request.url)
                    if u.hostname!='127.0.0.1' or (mode=='blocked' and 'poker-hand-lab.js' in u.path):request.abort()
                    elif mode=='invalid-bank' and u.path==ROUTE:
                        html=(ROOT/'poker/free-poker-learning-path/index.html').read_text()
                        assert html.count('data-solution="As,Ah,Kd,Qs,9h"')==1
                        html=html.replace('data-solution="As,Ah,Kd,Qs,9h"','data-solution="As,Kd,9h,6d,2c"',1)
                        request.fulfill(status=200,content_type='text/html',body=html)
                    else:request.continue_()
                fallback.route('**/*',route)
                native=fallback.new_page();native.goto(origin+ROUTE)
                expect(native.locator('[data-lab-case]:visible')).to_have_count(10)
                expect(native.locator('[data-lab-check]:visible')).to_have_count(0)
                expect(native.locator('[data-hand-lab] input:visible')).to_have_count(0)
                enter(native,native.locator('.hand-lab-rankings > summary'))
                expect(native.locator('.hand-lab-rankings .viewer-rankings')).to_be_visible()
                for ident in ['pair','flush','ace-low']:
                    answer=native.locator('#hand-lab-'+ident+' [data-lab-answer]')
                    enter(native,answer.locator('summary'));expect(answer.locator('div')).to_be_visible()
                flow_ok(native);fallback.close();report['fallbacks']+=1
            for mode in ['settled-arrival','active-control']:
                slow=browser.new_context(viewport={'width':390,'height':950})
                slow.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
                held=[];slow.route('**/*.woff2*',lambda r:held.append(r))
                early=slow.new_page();early.goto(origin+ROUTE+'#hand-lab-pair',wait_until='domcontentloaded')
                early.on('pageerror',lambda e:errors.append(str(e)))
                expect(early.locator('[data-hand-lab]')).to_have_class('hand-lab hand-lab-enhanced')
                assert held,'The delayed-font fixture did not intercept a font'
                control=early.locator('#hand-lab-pair input').first
                if mode=='active-control':
                    control.focus();early.keyboard.press('Space');expect(control).to_be_checked()
                slow.unroute('**/*.woff2*')
                for request in held:request.continue_()
                early.wait_for_load_state('load')
                early.evaluate('()=>document.fonts.ready.then(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))))')
                if mode=='active-control':
                    expect(control).to_be_focused();expect(control).to_be_checked()
                else:
                    title=early.locator('#hand-lab-pair h3')
                    expect(title).to_be_in_viewport()
                    assert title.evaluate("el=>el.getBoundingClientRect().top>=document.querySelector('.site-header').getBoundingClientRect().bottom")
                    if shots:early.screenshot(path=str(shots/'course-route-card-arrival-390.png'))
                slow.close();report['delayed_font_arrivals']+=1
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown();server.server_close()
    print('PASS: 40 keyboard-built hands, equivalent selections, category/kicker feedback, corrected retries, hints, honest partial reviews, course/search arrivals, print, native/fault fallbacks and privacy.')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
