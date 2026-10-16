"""Connected beginner route: native checks, return links, downloads and privacy."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
from playwright.sync_api import sync_playwright, expect
from field_guide_browser import QuietHandler, ROOT

ROUTE = '/poker/free-poker-learning-path/'
LESSONS = ['first-decisions', 'starting-hand-decisions', 'first-flop-decisions', 'turn-and-river-decisions', 'ranges-for-beginners', 'betting-with-a-purpose']
CHECKS = ['cards', 'starting', 'flop', 'river', 'ranges', 'purpose']
SPACING = '* {line-height:1.5 !important;letter-spacing:.12em !important;word-spacing:.16em !important} p {margin-bottom:2em !important}'


def enter(page,locator):
    locator.scroll_into_view_if_needed()
    locator.focus()
    expect(locator).to_be_focused()
    expect(locator).to_be_in_viewport()
    page.keyboard.press('Enter')


def course_route(page,origin,report,shots=None,width=390):
    page.evaluate('()=>document.fonts.ready.then(()=>true)')
    enter(page,page.locator('.article-body > .link-row .button'))
    expect(page).to_have_url(origin+'/poker/first-decisions/')
    page.wait_for_load_state('domcontentloaded')
    expect(page.locator('#course-first-pass-title')).to_have_text('Start with the short lesson.')
    enter(page,page.locator('#beginner-path-navigation > summary'))
    enter(page,page.locator('#beginner-path-navigation a[href="'+ROUTE+'#beginner-practice"]'))
    expect(page).to_have_url(origin+ROUTE+'#beginner-practice')
    page.wait_for_load_state('domcontentloaded')
    page.evaluate('()=>document.fonts.ready.then(()=>true)')
    expect(page.locator('#beginner-practice-heading')).to_be_in_viewport()
    if shots and width in [390,1440]:
        position(page,page.locator('#beginner-practice-heading'))
        page.screenshot(path=str(shots/f'course-route-map-{width}.png'))
    report['course_entries']+=1
    for target,heading in [('#card-basics','#card-basics-title'),('#first-hand-practice','#course-hand-title'),('#betting-rehearsal','#round-practice-title')]:
        enter(page,page.locator('.course-quick-links a[href="#practice-tools"]'))
        expect(page.locator('#practice-tools')).to_be_in_viewport()
        if shots and width in [390,1440] and target=='#card-basics':
            position(page,page.locator('#practice-tools'))
            page.screenshot(path=str(shots/f'course-route-tools-{width}.png'))
        enter(page,page.locator('.course-tool-menu a[href="'+target+'"]'))
        expect(page.locator(heading)).to_be_in_viewport()
        report['optional_arrivals']+=1
        if target=='#card-basics':
            enter(page,page.locator('.hand-basics-ready a'))
            expect(page).to_have_url(origin+'/poker/first-decisions/')
            page.wait_for_load_state('domcontentloaded')
            page.goto(origin+ROUTE)
            page.evaluate('()=>document.fonts.ready.then(()=>true)')
        elif target=='#first-hand-practice':
            enter(page,page.locator('.course-practice-return a'))
            expect(page.locator('#beginner-practice-heading')).to_be_in_viewport()
        else:
            enter(page,page.locator('#betting-rehearsal a[href="#beginner-practice"]'))
            expect(page.locator('#beginner-practice-heading')).to_be_in_viewport()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
    page.goto(origin+ROUTE)
    page.evaluate('()=>document.fonts.ready.then(()=>true)')


def position(page, locator):
    locator.evaluate("el=>{const h=document.querySelector('.site-header').getBoundingClientRect().height;window.scrollTo({top:scrollY+el.getBoundingClientRect().top-h-16,behavior:'instant'});}")
    expect(locator).to_be_in_viewport()
    assert locator.evaluate("el=>el.getBoundingClientRect().top >= document.querySelector('.site-header').getBoundingClientRect().bottom")


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    shots = Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots: shots.mkdir(parents=True, exist_ok=True)
    report = {'viewport_checks': 0, 'keyboard_answers': 0, 'path_menus': 0, 'lesson_arrivals': 0, 'return_arrivals': 0, 'course_entries':0,'optional_arrivals':0,'axe': []}
    errors = []
    try:
        with sync_playwright() as pw:
            opts = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'): opts['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**opts)
            context = browser.new_context(accept_downloads=True)
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = context.new_page(); page.on('pageerror', lambda e: errors.append(str(e)))
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 900})
                response = page.goto(origin + ROUTE)
                assert response and response.status == 200
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                if shots and width in [390,1440]:
                    page.screenshot(path=str(shots/f'course-route-entry-{width}.png'))
                course_route(page,origin,report,shots,width)
                expect(page.locator('#beginner-practice .viewer-question')).to_have_count(6)
                expect(page.locator('#beginner-practice .viewer-question[open]')).to_have_count(0)
                expect(page.locator('#session-one')).to_have_text('1. Tell the story of one hand.')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                if shots and width in [390, 1440]:
                    position(page, page.locator('#beginner-practice-heading'))
                    page.screenshot(path=str(shots / f'learning-path-overview-{width}.png'))
                for name in CHECKS:
                    q = page.locator('#path-check-' + name)
                    q.locator('summary').focus(); page.keyboard.press('Enter')
                    expect(q.locator('div')).to_be_visible(); report['keyboard_answers'] += 1
                    if name == 'cards' and shots and width in [390, 1440]:
                        position(page, q)
                        page.screenshot(path=str(shots / f'learning-path-answer-{width}.png'))
                expect(page.locator('#path-check-river')).to_contain_text('10 / 50 = 20%')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                page.add_style_tag(content=SPACING)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                report['viewport_checks'] += 3
                if os.environ.get('AXE_PATH') and width in [390, 1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    violations = page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
                    assert not violations, (width, violations)
                    report['axe'].append({'width': width, 'violations': violations})
                for index, slug in enumerate(LESSONS, 1):
                    page.goto(origin + '/poker/' + slug + '/')
                    menu = page.locator('#beginner-path-navigation')
                    expect(menu).not_to_have_attribute('open', '')
                    menu.locator('summary').focus(); page.keyboard.press('Enter')
                    expect(menu.locator('nav')).to_be_visible()
                    expect(menu).to_contain_text('Lesson ' + str(index) + ' of 6')
                    expect(menu.locator('span[aria-current="page"]')).to_have_count(1)
                    expect(menu.locator('a[href="/poker/' + slug + '/"]')).to_have_count(0)
                    report['path_menus'] += 1
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                    page.add_style_tag(content=SPACING)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                    report['viewport_checks'] += 2
                    if index == 3 and shots and width in [390, 1440]:
                        page.goto(origin + '/poker/' + slug + '/')
                        page.evaluate('()=>document.fonts.ready.then(()=>true)')
                        menu.locator('summary').focus(); page.keyboard.press('Enter')
                        position(page, menu)
                        page.screenshot(path=str(shots / f'learning-path-menu-{width}.png'))
            page.goto(origin + '/poker/topics/learn/')
            page.locator('main a[href="' + ROUTE + '#beginner-practice"]').click()
            expect(page).to_have_url(origin + ROUTE + '#beginner-practice')
            for slug in LESSONS:
                page.goto(origin + ROUTE)
                link = page.locator('#beginner-practice li h3 a[href="/poker/' + slug + '/"]')
                link.focus(); page.keyboard.press('Enter')
                expect(page).to_have_url(origin + '/poker/' + slug + '/')
                report['lesson_arrivals'] += 1
                menu = page.locator('#beginner-path-navigation')
                menu.locator('summary').focus(); page.keyboard.press('Enter')
                menu.locator('a[href="' + ROUTE + '#beginner-practice"]').focus(); page.keyboard.press('Enter')
                expect(page).to_have_url(origin + ROUTE + '#beginner-practice')
                report['return_arrivals'] += 1
            for slug in LESSONS[1:]:
                page.goto(origin + '/poker/first-decisions/')
                page.locator('#beginner-path-navigation summary').click()
                page.locator('#beginner-path-navigation a[href="/poker/' + slug + '/"]').click()
                expect(page).to_have_url(origin + '/poker/' + slug + '/')
                report['lesson_arrivals'] += 1
            page.goto(origin + ROUTE)
            with page.expect_download() as event:
                page.locator('#beginner-practice a[download]').click()
            download = event.value
            assert download.suggested_filename == 'poker-beginner-study-card.txt'
            assert Path(download.path()).read_bytes() == (ROOT / 'downloads/poker-beginner-study-card.txt').read_bytes()
            page.emulate_media(media='print')
            expect(page.locator('#beginner-practice-heading')).to_be_visible()
            expect(page.locator('#how-to-use')).to_be_visible()
            page.emulate_media(media='screen')
            assert context.cookies() == []
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
            offline = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 900})
            offline.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            static = offline.new_page(); static.goto(origin + ROUTE)
            course_route(static,origin,report)
            static.locator('#path-check-flop summary').focus(); static.keyboard.press('Enter')
            expect(static.locator('#path-check-flop div')).to_contain_text('9-9-A-6-2')
            static.locator('#path-flop h3 a').focus(); static.keyboard.press('Enter')
            expect(static).to_have_url(origin + '/poker/first-flop-decisions/')
            static.locator('#beginner-path-navigation summary').focus(); static.keyboard.press('Enter')
            expect(static.locator('#beginner-path-navigation nav')).to_be_visible()
            static.locator('#beginner-path-navigation a[href="' + ROUTE + '#beginner-practice"]').focus(); static.keyboard.press('Enter')
            expect(static).to_have_url(origin + ROUTE + '#beginner-practice')
            blocked=browser.new_context(viewport={'width':390,'height':900})
            blocked.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' and r.request.resource_type!='script' else r.abort())
            native=blocked.new_page();native.goto(origin+ROUTE)
            course_route(native,origin,report)
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown(); server.server_close()
    print('PASS: connected beginner route, six readiness checks, six current-page menus, exact private worksheet, print, no-JavaScript and privacy checks.')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
