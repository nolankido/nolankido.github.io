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
LESSONS = ['first-decisions', 'starting-hand-decisions', 'first-flop-decisions', 'turn-and-river-decisions']
CHECKS = ['cards', 'starting', 'flop', 'river']
SPACING = '* {line-height:1.5 !important;letter-spacing:.12em !important;word-spacing:.16em !important} p {margin-bottom:2em !important}'


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
    report = {'viewport_checks': 0, 'keyboard_answers': 0, 'path_menus': 0, 'lesson_arrivals': 0, 'return_arrivals': 0, 'axe': []}
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
                expect(page.locator('#beginner-practice .viewer-question')).to_have_count(4)
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
                    expect(menu).to_contain_text('Lesson ' + str(index) + ' of 4')
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
            static.locator('#path-check-flop summary').focus(); static.keyboard.press('Enter')
            expect(static.locator('#path-check-flop div')).to_contain_text('9-9-A-6-2')
            static.locator('#path-flop h3 a').focus(); static.keyboard.press('Enter')
            expect(static).to_have_url(origin + '/poker/first-flop-decisions/')
            static.locator('#beginner-path-navigation summary').focus(); static.keyboard.press('Enter')
            expect(static.locator('#beginner-path-navigation nav')).to_be_visible()
            static.locator('#beginner-path-navigation a[href="' + ROUTE + '#beginner-practice"]').focus(); static.keyboard.press('Enter')
            expect(static).to_have_url(origin + ROUTE + '#beginner-practice')
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown(); server.server_close()
    print('PASS: connected beginner route, four readiness checks, four current-page menus, exact private worksheet, print, no-JavaScript and privacy checks.')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
