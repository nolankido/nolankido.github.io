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
from field_guide_browser import QuietHandler, ROOT, assert_jump_target, wait_for_fonts
from learning_path_browser import SPACING
from test_viewer_guides import five, best

ROUTE = '/poker/free-poker-learning-path/'
RANKINGS = '/poker/hand-rankings/'
STUDY_CARD = '/downloads/poker-beginner-study-card.txt'
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


def follow_native_link(page, link, url, target):
    """Observe the native arrival before any later control moves the viewport."""
    expect(link).to_be_visible()
    link.focus()
    expect(link).to_be_focused()
    expect(link).to_be_in_viewport()
    page.keyboard.press('Enter')
    expect(page).to_have_url(url)
    page.wait_for_load_state('load')
    assert_jump_target(page, target)


def assert_reference_practice(page):
    section = page.locator('section#practice-next')
    expect(section).to_be_visible()
    expect(section.locator('h2#practice-next-title')).to_have_text('Build one different hand yourself.')
    expect(section.locator(f'a[href="{ROUTE}#card-basics"]')).to_have_text('Practice choosing the best five cards')
    for item in section.locator('p, a').all():
        expect(item).to_be_visible()
        assert item.evaluate('el => el.scrollWidth <= el.clientWidth + 1')
    assert section.evaluate('el => el.scrollWidth <= el.clientWidth + 1')
    flow_ok(page)
    return section


def assert_course_font_mode(page, scripts):
    fonts = page.evaluate('''() => ({
        noScripts: matchMedia('(scripting: none)').matches,
        body: ['--sans', '--serif', '--mono'].map(name => getComputedStyle(document.body).getPropertyValue(name)),
        root: ['--sans', '--serif', '--mono'].map(name => getComputedStyle(document.documentElement).getPropertyValue(name)),
        requests: performance.getEntriesByType('resource').filter(item => item.name.includes('.woff')).map(item => item.name)
    })''')
    assert fonts['noScripts'] == (not scripts), fonts
    if scripts:
        assert fonts['body'] == fonts['root'], fonts
    else:
        assert all(body != root for body, root in zip(fonts['body'], fonts['root'])), fonts
        assert not fonts['requests'], fonts


def check_reference_practice(browser, origin, shots, errors, report):
    """Continue from the ranking reference into one existing changed hand."""
    writes = []
    def route(request):
        if request.request.method not in {'GET', 'HEAD'}:
            writes.append(request.request.url)
        request.continue_() if urlsplit(request.request.url).hostname == '127.0.0.1' else request.abort()
    for scripts in (True, False):
        context = browser.new_context(java_script_enabled=scripts, accept_downloads=True,
                                      reduced_motion='reduce')
        context.route('**/*', route)
        page = context.new_page()
        page.on('pageerror', lambda err: errors.append(str(err)))
        for width in (320, 390, 768, 1440):
            print(f'Checking reference-to-practice: width={width}; page scripts={scripts}', flush=True)
            page.set_viewport_size({'width': width, 'height': 950})
            assert page.goto(origin + RANKINGS).status == 200
            wait_for_fonts(page)
            section = assert_reference_practice(page)
            jump = page.locator('.poker-jump a[href="#practice-next"]')
            expect(jump).to_have_text('Practice next')
            follow_native_link(page, jump, origin + RANKINGS + '#practice-next',
                               section.locator('#practice-next-title'))
            report['reference_jumps'] += 1
            if shots and scripts and width in (390, 1440):
                page.screenshot(path=str(shots / f'hand-ranking-practice-next-{width}.png'))

            follow_native_link(page, section.locator(f'a[href="{ROUTE}#card-basics"]'),
                               origin + ROUTE + '#card-basics', page.locator('#card-basics-title'))
            assert_course_font_mode(page, scripts)
            report['reference_course_arrivals'] += 1
            lab = page.locator('[data-hand-lab]')
            first = CASES[0]
            item = lab.locator('#hand-lab-' + first['id'])
            answer = item.locator('[data-lab-answer]')
            expect(item).to_be_visible()
            if scripts:
                expect(lab).to_have_class('hand-lab hand-lab-enhanced')
                expect(lab.locator('[data-lab-case]:visible')).to_have_count(1)
                expect(item.locator('input:checked')).to_have_count(0)
                select(page, item, first['solution'])
                enter(page, item.locator('[data-lab-check]'))
                expect(item.locator('input:checked')).to_have_count(5)
                expect(item.locator('[data-lab-feedback]')).to_contain_text('match the strongest available hand')
                expect(lab.locator('[data-lab-next]')).to_be_enabled()
                report['reference_practice_hands'] += 1
            else:
                expect(lab.locator('[data-lab-case]:visible')).to_have_count(10)
                expect(lab.locator('input:visible, [data-lab-check]:visible')).to_have_count(0)
                expect(answer).not_to_have_attribute('open', '')
                enter(page, answer.locator('summary'))
                report['reference_native_answers'] += 1
            expect(answer.locator(':scope > div')).to_be_visible()
            expect(answer.locator(':scope > div')).to_contain_text(first['reason'])
            flow_ok(page)
            assert page.evaluate('localStorage.length===0 && sessionStorage.length===0')
            assert context.cookies() == []

            # Keep reflow and print probes outside the uninterrupted reading
            # journey so media changes cannot affect the course arrival.
            assert page.goto(origin + RANKINGS).status == 200
            wait_for_fonts(page)
            section = assert_reference_practice(page)
            follow_native_link(page, section.locator('a[href="#ties"]'), origin + RANKINGS + '#ties',
                               page.locator('#ties'))
            follow_native_link(page, page.locator('.poker-jump a[href="#practice-next"]'),
                               origin + RANKINGS + '#practice-next', section.locator('#practice-next-title'))
            report['reference_repair_journeys'] += 1

            # Test spacing synchronously: no-script documents do not dispatch
            # the load event awaited by add_style_tag.
            page.evaluate('css => { const style = document.createElement("style"); style.id = "reference-test-spacing"; style.textContent = css; document.head.appendChild(style); }', SPACING)
            assert_reference_practice(page)
            report['reference_spacing_layouts'] += 1
            page.evaluate('document.getElementById("reference-test-spacing").remove()')
            page.emulate_media(media='print')
            assert_reference_practice(page)
            report['reference_print_layouts'] += 1
            if shots and scripts and width == 1440:
                pdf = page.pdf(path=str(shots / 'hand-ranking-practice-next-print.pdf'), format='A4',
                               print_background=True,
                               margin={'top': '15mm', 'bottom': '15mm', 'left': '15mm', 'right': '15mm'})
                assert pdf.startswith(b'%PDF-')
                report['reference_print_pdf_captures'] += 1
            page.emulate_media(media='screen')

            # The same existing blank file is checked once per script mode.
            if width == 390:
                download_link = section.locator(f'a[download][href="{STUDY_CARD}"]')
                download_link.focus()
                expect(download_link).to_be_focused()
                expect(download_link).to_be_in_viewport()
                with page.expect_download() as pending:
                    page.keyboard.press('Enter')
                download = pending.value
                assert download.suggested_filename == 'poker-beginner-study-card.txt'
                assert Path(download.path()).read_bytes() == (ROOT / STUDY_CARD.lstrip('/')).read_bytes()
                report['reference_study_downloads'] += 1
        context.close()

    # A late font definition must not move the no-script course introduction
    # away from its native fragment. Hold the real stylesheet response, then
    # release it without injecting CSS or correcting the browser's scroll.
    print('Checking no-script reference arrival with delayed font definitions', flush=True)
    delayed = browser.new_context(java_script_enabled=False, reduced_motion='reduce',
                                  viewport={'width': 768, 'height': 950})
    delayed.route('**/*', route)
    native = delayed.new_page()
    native.on('pageerror', lambda err: errors.append(str(err)))
    assert native.goto(origin + RANKINGS).status == 200
    wait_for_fonts(native)
    follow_native_link(native, native.locator('.poker-jump a[href="#practice-next"]'),
                       origin + RANKINGS + '#practice-next', native.locator('#practice-next-title'))
    held = []
    delayed.route('**/site-fonts.css*', lambda request: held.append(request))
    link = native.locator(f'#practice-next a[href="{ROUTE}#card-basics"]')
    link.focus()
    expect(link).to_be_focused()
    expect(link).to_be_in_viewport()
    with native.expect_navigation(wait_until='domcontentloaded'):
        native.keyboard.press('Enter')
    assert held, 'The no-script delayed-font fixture did not intercept the font stylesheet'
    delayed.unroute('**/site-fonts.css*')
    for request in held:
        request.continue_()
    native.wait_for_load_state('load')
    expect(native).to_have_url(origin + ROUTE + '#card-basics')
    assert_jump_target(native, native.locator('#card-basics-title'))
    assert_course_font_mode(native, False)
    if shots:
        native.screenshot(path=str(shots / 'hand-ranking-native-delayed-arrival-768.png'))
    answer = native.locator('#hand-lab-' + CASES[0]['id'] + ' [data-lab-answer]')
    enter(native, answer.locator('summary'))
    expect(answer.locator(':scope > div')).to_be_visible()
    expect(answer.locator(':scope > div')).to_contain_text(CASES[0]['reason'])
    flow_ok(native)
    assert native.evaluate('localStorage.length===0 && sessionStorage.length===0')
    assert delayed.cookies() == []
    report['reference_delayed_font_arrivals'] += 1
    delayed.close()
    assert not writes, writes


def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    shots=Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots:shots.mkdir(parents=True,exist_ok=True)
    report={'constructed_hands':0,'equivalent_selections':0,'lesson_arrivals':0,'fallbacks':0,'delayed_font_arrivals':0,
            'reference_jumps':0,'reference_repair_journeys':0,'reference_course_arrivals':0,
            'reference_practice_hands':0,'reference_native_answers':0,'reference_spacing_layouts':0,
            'reference_print_layouts':0,'reference_print_pdf_captures':0,'reference_study_downloads':0,
            'reference_delayed_font_arrivals':0,'axe':[]}
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
            check_reference_practice(browser, origin, shots, errors, report)
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown();server.server_close()
    print('PASS: 40 keyboard-built hands, equivalent selections, category/kicker feedback, corrected retries, hints, honest partial reviews, course/search arrivals, reference-to-practice keyboard journeys, print, native/fault fallbacks and privacy.')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
