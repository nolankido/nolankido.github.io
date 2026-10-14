"""Real checkpoint arrivals, native answer/repair/retry paths and private workbook."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
from playwright.sync_api import sync_playwright, expect
from field_guide_browser import QuietHandler, ROOT
from learning_path_browser import position, SPACING

ROUTE = '/poker/beginner-checkpoint/'
LESSONS = ['first-decisions','starting-hand-decisions','first-flop-decisions',
           'turn-and-river-decisions','ranges-for-beginners','betting-with-a-purpose']


def main():
    server = ThreadingHTTPServer(('127.0.0.1',0), partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    shots = Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots: shots.mkdir(parents=True,exist_ok=True)
    report = {'viewport_checks':0,'keyboard_answers':0,'lesson_arrivals':0,'search_arrivals':0,'repair_retry':0,'axe':[]}
    errors = []
    try:
        with sync_playwright() as pw:
            opts = {'headless':True}
            if os.environ.get('CHROMIUM_PATH'): opts['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**opts)
            context = browser.new_context(accept_downloads=True)
            context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            page = context.new_page(); page.on('pageerror',lambda e:errors.append(str(e)))
            for width in [320,390,768,1440]:
                page.set_viewport_size({'width':width,'height':900})
                response = page.goto(origin+ROUTE); assert response and response.status==200
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                expect(page.locator('h1')).to_have_text('Can you explain the next hand?')
                expect(page.locator('details.viewer-question')).to_have_count(12)
                expect(page.locator('details.viewer-question[open]')).to_have_count(0)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),width
                if shots and width in [390,1440]:
                    page.screenshot(path=str(shots/f'checkpoint-opening-{width}.png'))
                    example = page.locator('[data-case="draw"] .viewer-example'); position(page,example)
                    cards = example.locator('[role="img"]'); expect(cards).to_have_count(5)
                    for card in cards.all(): expect(card).to_be_in_viewport(ratio=1)
                    page.screenshot(path=str(shots/f'checkpoint-cards-{width}.png'))
                for q in page.locator('details.viewer-question').all():
                    q.locator('summary').focus();page.keyboard.press('Enter')
                    expect(q.locator('div')).to_be_visible();report['keyboard_answers']+=1
                    if q.get_attribute('id')=='answer-four' and shots and width in [390,1440]:
                        position(page,q);expect(q.locator('summary')).to_be_in_viewport()
                        page.screenshot(path=str(shots/f'checkpoint-answer-{width}.png'))
                expect(page.locator('#retry-six')).to_contain_text('(20 - 6) / 2 = 7')
                preview = page.locator('#checkpoint-workbook-preview')
                preview.locator('summary').focus();page.keyboard.press('Enter')
                assert preview.locator('pre').text_content()==(ROOT/'downloads/poker-beginner-checkpoint.txt').read_text()
                expect(preview.locator('pre')).to_be_visible()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),('open',width)
                page.add_style_tag(content=SPACING)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),('spacing',width)
                report['viewport_checks']+=3
                if os.environ.get('AXE_PATH') and width in [390,1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    violations=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
                    assert not violations,(width,violations);report['axe'].append({'width':width,'violations':violations})
            for slug in LESSONS:
                page.goto(origin+'/poker/'+slug+'/')
                link=page.locator('aside[aria-labelledby="beginner-checkpoint-invite"] a[href="'+ROUTE+'"]')
                link.focus();page.keyboard.press('Enter');expect(page).to_have_url(origin+ROUTE)
                report['lesson_arrivals']+=1
            page.goto(origin+'/poker/free-poker-learning-path/')
            link=page.locator('#beginner-next-step a[href="'+ROUTE+'"]')
            link.focus();page.keyboard.press('Enter');expect(page).to_have_url(origin+ROUTE)
            report['lesson_arrivals']+=1
            page.locator('#answer-one summary').focus();page.keyboard.press('Enter')
            link=page.locator('#answer-one a[href="/poker/first-decisions/#chips-owed"]')
            link.focus();page.keyboard.press('Enter');expect(page).to_have_url(origin+'/poker/first-decisions/#chips-owed')
            page.locator('aside[aria-labelledby="beginner-checkpoint-invite"] a[href="'+ROUTE+'"]').focus();page.keyboard.press('Enter')
            expect(page).to_have_url(origin+ROUTE)
            page.locator('#retry-one summary').focus();page.keyboard.press('Enter')
            expect(page.locator('#retry-one div')).to_contain_text('5 - 0 = 5');report['repair_retry']+=1
            for route,field,result in [('/poker/library/','#library-search','#library-grid'),('/poker/find/','#finder-search','main'),('/find/','#find-query','main')]:
                page.goto(origin+route);page.locator(field).fill('beginner checkpoint');page.locator(field).press('Enter')
                link=page.locator(result+' a[href="'+ROUTE+'"]:visible').first
                link.focus();page.keyboard.press('Enter');expect(page).to_have_url(origin+ROUTE)
                report['search_arrivals']+=1
            with page.expect_download() as event:page.locator('main a[download][href="/downloads/poker-beginner-checkpoint.txt"]').click()
            download=event.value
            assert download.suggested_filename=='poker-beginner-checkpoint.txt'
            assert Path(download.path()).read_bytes()==(ROOT/'downloads/poker-beginner-checkpoint.txt').read_bytes()
            page.locator('#study-with-friend summary').focus();page.keyboard.press('Enter')
            expect(page.locator('#study-with-friend div')).to_be_visible()
            expect(page.locator('#feedback')).to_have_text('Help make the next explanation clearer')
            expect(page.locator('main a[href="/contact/"]').first).to_be_visible()
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
            assert context.cookies()==[]
            page.emulate_media(media='print');expect(page.locator('#try')).to_be_visible();page.emulate_media(media='screen')
            offline=browser.new_context(java_script_enabled=False,accept_downloads=True,viewport={'width':390,'height':900})
            offline.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            static=offline.new_page();static.goto(origin+'/poker/free-poker-learning-path/')
            static.locator('#beginner-next-step a[href="'+ROUTE+'"]').focus();static.keyboard.press('Enter')
            expect(static).to_have_url(origin+ROUTE)
            static.locator('#answer-four summary').focus();static.keyboard.press('Enter')
            expect(static.locator('#answer-four div')).to_contain_text('8 / 40 = 20%')
            static.locator('#retry-four summary').focus();static.keyboard.press('Enter')
            expect(static.locator('#retry-four div')).to_contain_text('15 / 60 = 25%')
            static.locator('#checkpoint-workbook-preview summary').focus();static.keyboard.press('Enter')
            assert static.locator('#checkpoint-workbook-preview pre').text_content()==(ROOT/'downloads/poker-beginner-checkpoint.txt').read_text()
            assert static.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            assert not errors,errors;browser.close()
    finally:server.shutdown();server.server_close()
    print('PASS: twelve native answers, six lesson invitations, course/search discovery, repair/retry, exact private workbook, feedback prompts and no-JavaScript reading.')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
