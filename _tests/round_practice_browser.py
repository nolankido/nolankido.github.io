"""Rehearse different legal lines, recover from errors and retain honest study notes."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
from playwright.sync_api import sync_playwright, expect
from field_guide_browser import QuietHandler, ROOT

ROUTE='/poker/free-poker-learning-path/'


def enter(page, node):
    node.focus();page.keyboard.press('Enter')


def move(page, case, action, amount=None):
    select=case.locator('[data-round-action]');select.select_option(action);select.focus();page.keyboard.press('Tab')
    expect(select).to_have_value(action)
    if amount is not None:
        field=case.locator('[data-round-amount]');field.fill(str(amount))
    enter(page,case.locator('[data-round-move]'))


def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start();origin='http://127.0.0.1:'+str(server.server_port)
    shots=Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots:shots.mkdir(parents=True,exist_ok=True)
    errors=[];report={'widths':[],'fallbacks':0,'deep_links':0,'delayed_font_arrivals':0,'axe':[]}
    try:
        with sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**opts)
            context=browser.new_context(reduced_motion='reduce')
            context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            for width in [320,390,768,1440]:
                page.set_viewport_size({'width':width,'height':950});assert page.goto(origin+ROUTE).status==200
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                root=page.locator('[data-round-practice]');expect(root).to_have_class('round-practice round-enhanced')
                enter(page,page.locator('.course-quick-links a[href="#betting-rehearsal"]'))
                expect(page.locator('#round-practice-title')).to_be_in_viewport()
                assert page.locator('#round-practice-title').evaluate("el=>el.getBoundingClientRect().top >= document.querySelector('.site-header').getBoundingClientRect().bottom")
                expect(root.locator('[data-round-case]:visible')).to_have_count(1)
                requests=[];listener=lambda r:requests.append(r.url);page.on('request',listener)
                pre=root.locator('#round-practice-preflop');feedback=pre.locator('[data-round-feedback]')
                select=pre.locator('[data-round-action]');select.focus();page.keyboard.press('Home');page.keyboard.press('ArrowDown');page.keyboard.press('Tab');expect(select).to_have_value('check')
                enter(page,pre.locator('[data-round-move]'));expect(feedback).to_contain_text('owes 2');expect(pre.locator('[data-round-totals]')).to_contain_text('Pot now: 3.')
                move(page,pre,'call',9);expect(feedback).to_contain_text('2 minus 0 = 2');expect(feedback).to_be_focused();expect(feedback).to_be_in_viewport()
                assert feedback.evaluate("el=>el.getBoundingClientRect().top >= document.querySelector('.site-header').getBoundingClientRect().bottom")
                move(page,pre,'call',2);expect(pre.locator('[data-round-turn]')).to_contain_text('Small blind acts next')
                expect(pre.locator('[data-round-turn]')).to_be_focused()
                move(page,pre,'call',1);expect(pre.locator('[data-round-turn]')).to_contain_text('Big blind acts next')
                expect(pre.locator('[data-round-totals]')).to_contain_text('Pot now: 6.')
                move(page,pre,'raise',4);move(page,pre,'call',4);move(page,pre,'call',4)
                expect(pre.locator('[data-round-turn]')).to_contain_text('Round finished. The flop can be dealt')
                expect(pre.locator('[data-round-totals]')).to_contain_text('Pot before settlement: 18.')
                expect(pre.locator('[data-round-review]')).to_contain_text('Additional call counters')
                enter(page,pre.locator('[data-round-restart]'))
                expect(pre.locator('[data-round-review]')).to_contain_text('Additional call counters')
                expect(pre.locator('[data-round-log] li')).to_have_count(0)
                move(page,pre,'fold');move(page,pre,'fold')
                expect(pre.locator('[data-round-turn]')).to_contain_text('Return 1 uncalled counter, then award the remaining pot of 2.')
                enter(page,root.locator('.round-starts a[href="#round-practice-flop"]'))
                flop=root.locator('#round-practice-flop');expect(flop).to_be_visible();expect(flop.locator('h3')).to_be_focused()
                move(page,flop,'bet',1);expect(flop.locator('[data-round-feedback]')).to_contain_text('minimum opening bet is 2')
                move(page,flop,'check');move(page,flop,'check');move(page,flop,'check')
                expect(flop.locator('[data-round-turn]')).to_contain_text('The turn can be dealt')
                expect(flop.locator('[data-round-totals]')).to_contain_text('Pot before settlement: 6.')
                enter(page,flop.locator('[data-round-restart]'))
                move(page,flop,'check');move(page,flop,'bet',4);move(page,flop,'call',4);move(page,flop,'call',4)
                expect(flop.locator('[data-round-totals]')).to_contain_text('Pot before settlement: 18.')
                enter(page,root.locator('.round-starts a[href="#round-practice-raise"]'))
                raised=root.locator('#round-practice-raise');expect(raised).to_be_visible()
                for value in ['', '1.5','-1','no','1e3']:
                    move(page,raised,'call',value);expect(raised.locator('[data-round-feedback]')).to_contain_text('whole counters')
                    expect(raised.locator('[data-round-totals]')).to_contain_text('Pot now: 20.')
                move(page,raised,'call',10);expect(raised.locator('[data-round-feedback]')).to_contain_text('10 minus 4 = 6')
                move(page,raised,'raise',11);expect(raised.locator('[data-round-feedback]')).to_contain_text('Reach at least 16 total')
                move(page,raised,'raise',12);move(page,raised,'call',6)
                expect(raised.locator('[data-round-totals]')).to_contain_text('Pot before settlement: 38.')
                enter(page,raised.locator('[data-round-restart]'));move(page,raised,'fold')
                expect(raised.locator('[data-round-turn]')).to_contain_text('Return 6 uncalled counters, then award the remaining pot of 14.')
                enter(page,raised.locator('[data-round-worked] > summary'))
                expect(raised.locator('[data-round-review]')).to_contain_text('Used the worked line')
                expect(raised.locator('[data-round-review]')).to_contain_text('The last full raise increment')
                # Returning to a starting point keeps its current line until an explicit restart.
                enter(page,root.locator('.round-starts a[href="#round-practice-preflop"]'))
                expect(pre.locator('[data-round-turn]')).to_contain_text('Hand finished')
                assert not requests,requests;page.remove_listener('request',listener)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                assert page.evaluate('localStorage.length===0 && sessionStorage.length===0')
                if width in [390,1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    violations=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}));}")
                    assert not violations,violations;report['axe'].append({'width':width,'violations':0})
                    if shots:
                        root.scroll_into_view_if_needed();page.screenshot(path=str(shots/f'betting-rehearsal-{width}.png'))
                report['widths'].append(width)
            for slug,case in [('first-decisions','preflop'),('starting-hand-decisions','preflop'),('first-flop-decisions','flop')]:
                page.goto(origin+'/poker/'+slug+'/');enter(page,page.locator('.course-first-pass a[href$="#round-practice-'+case+'"]'))
                target=page.locator('#round-practice-'+case);expect(target).to_be_visible();expect(target.locator('h3')).to_be_focused();expect(target.locator('h3')).to_be_in_viewport();assert target.locator('h3').evaluate("el=>el.getBoundingClientRect().top >= document.querySelector('.site-header').getBoundingClientRect().bottom");expect(target.locator('[data-round-live]')).to_be_visible();expect(target.locator('[data-round-log] li')).to_have_count(0);report['deep_links']+=1
            page.set_viewport_size({'width':390,'height':950})
            for case in ['preflop','flop','raise']:
                page.goto(origin+ROUTE+'#round-practice-'+case)
                heading=page.locator('#round-practice-'+case+' > h3')
                expect(heading).to_be_focused();expect(heading).to_be_in_viewport()
                assert heading.evaluate("el=>el.getBoundingClientRect().top >= document.querySelector('.site-header').getBoundingClientRect().bottom")
                report['deep_links']+=1
            page.reload();expect(page.locator('[data-round-practice]')).to_have_class('round-practice round-enhanced');expect(page.locator('[data-round-case]:visible h3')).to_be_focused();expect(page.locator('[data-round-case]:visible h3')).to_be_in_viewport();expect(page.locator('[data-round-case]:visible [data-round-review]')).to_have_text('')
            page.emulate_media(media='print')
            expect(page.locator('[data-round-case]:visible')).to_have_count(3)
            expect(page.locator('[data-round-native]:visible')).to_have_count(3)
            expect(page.locator('[data-round-live]:visible')).to_have_count(0)
            for detail in page.locator('[data-round-worked] > div').all():expect(detail).to_be_visible()
            page.emulate_media(media='screen');context.close()
            # Native content survives disabled JS, a blocked script and malformed embedded data.
            for mode in ['no-js','blocked','invalid']:
                ctx=browser.new_context(java_script_enabled=mode!='no-js')
                if mode=='blocked':ctx.route('**/assets/poker-round-practice.js*',lambda r:r.abort())
                if mode=='invalid':
                    def invalid(r):
                        response=r.fetch();body=response.text();old='data-round-state="{&quot;street&quot;:&quot;preflop&quot;'
                        assert body.count(old)==1
                        r.fulfill(response=response,body=body.replace(old,'data-round-state="{&quot;street&quot;:&quot;invalid&quot;',1))
                    ctx.route('**/poker/free-poker-learning-path/',invalid)
                fallback=ctx.new_page();fallback.goto(origin+ROUTE)
                expect(fallback.locator('[data-round-case]:visible')).to_have_count(3)
                expect(fallback.locator('[data-round-native]:visible')).to_have_count(3)
                expect(fallback.locator('[data-round-live]:visible')).to_have_count(0)
                detail=fallback.locator('[data-round-worked]').first;enter(fallback,detail.locator('summary'));expect(detail.locator('div')).to_be_visible();ctx.close();report['fallbacks']+=1
            # A learner can start before fonts arrive. Later layout must not take
            # focus away from a control they are already using.
            slow=browser.new_context(viewport={'width':390,'height':950})
            slow.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            held=[];slow.route('**/*.woff2*',lambda r:held.append(r))
            early=slow.new_page();early.goto(origin+ROUTE+'#round-practice-flop',wait_until='domcontentloaded')
            expect(early.locator('[data-round-practice]')).to_have_class('round-practice round-enhanced')
            assert held,'The delayed-font fixture did not intercept a font'
            action=early.locator('#round-practice-flop [data-round-action]');action.focus();expect(action).to_be_focused()
            slow.unroute('**/*.woff2*')
            for request in held:request.continue_()
            early.evaluate('()=>document.fonts.ready.then(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))))')
            expect(action).to_be_focused()
            move(early,early.locator('#round-practice-flop'),'bet',1)
            expect(early.locator('#round-practice-flop [data-round-feedback]')).to_contain_text('minimum opening bet is 2')
            slow.close();report['delayed_font_arrivals']+=1
            browser.close()
        assert not errors,errors
        print(json.dumps({'status':'pass',**report},indent=2))
    finally:server.shutdown()


if __name__=='__main__':main()
