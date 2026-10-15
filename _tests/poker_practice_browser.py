"""Worked-example practice, changed attempts, mixed sets and honest review notes."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
from playwright.sync_api import sync_playwright, expect
from field_guide_browser import QuietHandler, ROOT
from learning_path_browser import SPACING

ROUTE = '/poker/beginner-practice/'
UNITS = json.loads((ROOT / '_source/poker/beginner-practice.json').read_text())['units']


def enter(page, element):
    element.focus()
    page.keyboard.press('Enter')


def choose(page, item, value):
    item.locator('input[value="' + str(value) + '"]').focus()
    page.keyboard.press('Space')


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    shots = Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    report = {'changed_questions': 0, 'mixed_questions': 0, 'lesson_arrivals': 0, 'fallbacks': 0, 'axe': []}
    errors = []
    try:
        with sync_playwright() as pw:
            opts = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                opts['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**opts)
            context = browser.new_context(accept_downloads=True, reduced_motion='reduce')
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 950})
                assert page.goto(origin + ROUTE).status == 200
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                root = page.locator('[data-drill-room]')
                expect(root).to_have_class('drill-room drills-enhanced')
                requests = []
                listener = lambda request: requests.append(request.url)
                page.on('request', listener)
                for unit in UNITS:
                    enter(page, root.locator('[data-drill-skill="' + unit['id'] + '"]'))
                    active = root.locator('#practice-' + unit['id'])
                    expect(page).to_have_url(origin + ROUTE + '#practice-' + unit['id'])
                    expect(active.locator('h2')).to_be_focused()
                    expect(active).to_be_visible()
                    expect(active.locator('[data-drill-model]')).to_have_attribute('open', '')
                    expect(root.locator('[data-drill-case]:visible')).to_have_count(1)
                    for index, case in enumerate(unit['cases']):
                        item = active.locator('#exercise-' + case['id'])
                        expect(item).to_be_visible()
                        expect(item.locator('[data-drill-choices]')).to_be_hidden()
                        expect(item.locator('[data-drill-answer]')).to_be_hidden()
                        expect(root.locator('[data-drill-next]')).to_be_disabled()
                        enter(page, item.locator('[data-drill-choices-button]'))
                        expect(item.locator('input').first).to_be_focused()
                        enter(page, item.locator('[data-drill-check]'))
                        expect(item.locator('[data-drill-status]')).to_contain_text('Choose an answer')
                        if index == 0:
                            wrong = (case['correct'] + 1) % 3
                            choose(page, item, wrong)
                            enter(page, item.locator('[data-drill-check]'))
                            expect(item.locator('[data-drill-note]:visible')).to_have_count(1)
                            expect(item.locator('[data-drill-note]:visible')).to_contain_text(case['choices'][wrong][1])
                            expect(root.locator('[data-drill-next]')).to_be_enabled()
                        choose(page, item, case['correct'])
                        expect(item.locator('[data-drill-answer]')).to_be_hidden()
                        expect(root.locator('[data-drill-next]')).to_be_disabled()
                        enter(page, item.locator('[data-drill-check]'))
                        expect(item.locator('[data-drill-status]')).to_contain_text('Your choice matches')
                        if index == 1:
                            enter(page, root.locator('[data-drill-back]'))
                            previous = active.locator('#exercise-' + unit['cases'][0]['id'])
                            expect(previous.locator('input:checked')).to_have_value(str(unit['cases'][0]['correct']))
                            enter(page, root.locator('[data-drill-next]'))
                            enter(page, item.locator('[data-drill-retry]'))
                            expect(item.locator('input:checked')).to_have_count(0)
                            expect(item.locator('[data-drill-choices]')).to_be_hidden()
                            enter(page, item.locator('[data-drill-choices-button]'))
                            choose(page, item, case['correct'])
                            enter(page, item.locator('[data-drill-check]'))
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (unit['id'], width)
                        if shots and width in [390, 1440] and case['id'] == 'four-hearts':
                            item.evaluate("el=>scrollTo({top:scrollY+el.getBoundingClientRect().top-document.querySelector('.site-header').getBoundingClientRect().height-20,behavior:'instant'})")
                            page.screenshot(path=str(shots / f'beginner-practice-cards-{width}.png'))
                        enter(page, root.locator('[data-drill-next]'))
                        report['changed_questions'] += 1
                    expect(root.locator('[data-drill-summary]')).to_be_visible()
                    expect(root.locator('[data-drill-review-list] > li')).to_have_count(3)
                    expect(root.locator('[data-drill-review-list] > li').first).to_contain_text('Revisit')
                    expect(root.locator('[data-drill-review-list] > li').nth(1)).to_contain_text('an example was shown')
                    # Reopening the current native fragment must start a new visit too.
                    enter(page, root.locator('[data-drill-skill="' + unit['id'] + '"]'))
                    expect(active.locator('h2')).to_be_focused()
                    expect(root.locator('[data-drill-summary]')).to_be_hidden()
                    expect(root.locator('[data-drill-review-list] > li')).to_have_count(0)
                    expect(active.locator('[data-drill-case]:visible')).to_have_id('exercise-' + unit['cases'][0]['id'])
                    expect(active.locator('input:checked')).to_have_count(0)
                    expect(root.locator('[data-drill-next]')).to_be_disabled()
                assert not requests, requests
                page.remove_listener('request', listener)
                page.add_style_tag(content=SPACING)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                if os.environ.get('AXE_PATH') and width in [390, 1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    bad = page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
                    assert not bad, bad
                    report['axe'].append({'width': width, 'violations': bad})
            page.set_viewport_size({'width': 390, 'height': 950})
            page.goto(origin + ROUTE)
            used = []
            for set_number in range(3):
                enter(page, page.locator('[data-drill-mix]'))
                expect(page.locator('[data-drill-progress]')).to_contain_text(f'Mixed set {set_number + 1} of 3')
                for index, unit_index in enumerate([3,0,5,2,1,4]):
                    unit = UNITS[unit_index]
                    case = unit['cases'][(set_number + unit_index) % 3]
                    used.append(case['id'])
                    item = page.locator('#exercise-' + case['id'])
                    expect(item).to_be_visible()
                    expect(page.locator('#practice-' + unit['id'] + ' [data-drill-model]')).to_be_hidden()
                    if index == 0 and set_number == 0:
                        enter(page, page.locator('#practice-' + unit['id'] + ' [data-drill-example-button]'))
                        expect(page.locator('#practice-' + unit['id'] + ' [data-drill-model]')).to_be_visible()
                        enter(page, item.locator('[data-drill-unsure]'))
                        expect(item.locator('[data-drill-status]')).to_contain_text('idea to revisit')
                        expect(item.locator('[data-drill-note]:visible')).to_have_count(0)
                    else:
                        enter(page, item.locator('[data-drill-choices-button]'))
                        choose(page, item, case['correct'])
                        enter(page, item.locator('[data-drill-check]'))
                    enter(page, page.locator('[data-drill-next]'))
                    report['mixed_questions'] += 1
                expect(page.locator('[data-drill-review-list] > li')).to_have_count(6)
                if set_number == 0:
                    expect(page.locator('[data-drill-review-list] > li').first).to_contain_text('Revisit')
                else:
                    expect(page.locator('[data-drill-review-list]')).to_contain_text('without an example shown')
            assert len(set(used)) == 18
            enter(page, page.locator('[data-drill-mix]'))
            expect(page.locator('[data-drill-progress]')).to_contain_text('Mixed set 1 of 3')
            page.emulate_media(media='print')
            expect(page.locator('[data-drill-case]:visible')).to_have_count(18)
            expect(page.locator('[data-drill-model]:visible')).to_have_count(6)
            expect(page.locator('[data-drill-answer]:visible')).to_have_count(18)
            expect(page.locator('[data-drill-note]:visible')).to_have_count(54)
            expect(page.locator('[data-drill-check]:visible')).to_have_count(0)
            page.emulate_media(media='screen')
            for unit in UNITS:
                page.goto(origin + '/poker/' + unit['lesson'] + '/')
                href = ROUTE + '#practice-' + unit['id']
                enter(page, page.locator('.course-first-pass a[href="' + href + '"]'))
                expect(page).to_have_url(origin + href)
                expect(page.locator('[data-drill-room]')).to_have_class('drill-room drills-enhanced')
                expect(page.locator('#practice-' + unit['id'])).to_be_visible()
                expect(page.locator('#practice-' + unit['id'] + '-title')).to_be_in_viewport()
                report['lesson_arrivals'] += 1
            page.goto(origin + '/poker/find/')
            page.locator('#finder-search').fill('raises 17 total')
            card = page.locator('[data-finder-card]:visible').filter(has=page.locator('h3 a[href="' + ROUTE + '"]'))
            link = card.locator('.finder-jump a')
            expect(link).to_have_attribute('href', ROUTE + '#exercise-flop-call')
            enter(page, link)
            expect(page.locator('[data-drill-room]')).to_have_class('drill-room drills-enhanced')
            expect(page.locator('[data-drill-case]:visible')).to_have_id('exercise-flop-call')
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0') and context.cookies() == []
            for scripting in [False, True]:
                fallback = browser.new_context(java_script_enabled=scripting, viewport={'width': 390, 'height': 950})
                fallback.route('**/*', lambda r: r.abort() if 'poker-beginner-practice.js' in r.request.url or urlsplit(r.request.url).hostname != '127.0.0.1' else r.continue_())
                native = fallback.new_page()
                native.goto(origin + ROUTE)
                expect(native.locator('[data-drill-case]:visible')).to_have_count(18)
                expect(native.locator('[data-drill-model]:visible')).to_have_count(6)
                expect(native.locator('[data-drill-check]:visible')).to_have_count(0)
                for ident in ['blind-call','four-hearts','winning-proof']:
                    answer = native.locator('#exercise-' + ident + ' [data-drill-answer]')
                    enter(native, answer.locator('summary'))
                    expect(answer.locator('div')).to_be_visible()
                assert native.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                fallback.close()
                report['fallbacks'] += 1
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown(); server.server_close()
    print('PASS: worked examples, 18 changed questions at four widths, three mixed sets, uncertain answers, honest review, exact lesson/search arrivals, print, native fallbacks and privacy.')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
