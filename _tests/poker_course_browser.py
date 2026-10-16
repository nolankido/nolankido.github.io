"""A beginner can practice, recover, continue, revisit and read without scripts."""
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
DATA = json.loads((ROOT / '_source/poker/beginner-course.json').read_text())
SHORT = json.loads((ROOT / '_source/poker/course-lessons.json').read_text())['lessons']
SPACING = '* {line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important} p {margin-bottom:2em!important}'


def enter(page, locator):
    locator.scroll_into_view_if_needed()
    locator.focus()
    expect(locator).to_be_focused()
    expect(locator).to_be_in_viewport()
    page.keyboard.press('Enter')


def select(page, scene, value):
    scene.locator('input[value="' + str(value) + '"]').focus()
    page.keyboard.press('Space')


def reflow(page):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')


def reveal_short_answer(page):
    # Same-document section navigation preserves native disclosure state.
    answer = page.locator('#course-lesson-answer')
    if answer.get_attribute('open') is None:
        enter(page, answer.locator('summary'))
    expect(answer.locator(':scope > div')).to_be_visible()


def check_position_maps(page, shots=None, width=390):
    maps = page.locator('.course-position-map')
    expect(maps).to_have_count(2)
    expect(page.locator('.course-lesson-model .course-position-orders')).to_be_visible()
    expect(page.locator('#course-lesson-answer .course-position-orders')).to_be_hidden()
    for i, kind in enumerate(['model', 'attempt']):
        fig = maps.nth(i)
        seats = fig.locator('.course-position-seat')
        expect(seats).to_have_count(6)
        expect(seats.locator('strong')).to_have_text(['First seat', 'Next seat', 'Cutoff', 'Button', 'Small blind', 'Big blind'])
        expect(fig.locator('.is-you')).to_contain_text('Button' if i == 0 else 'Small blind')
        expect(fig.locator('.is-you')).to_contain_text('You: your turn')
        expect(fig.locator('.course-position-button')).to_have_text('Dealer button')
        boxes = seats.evaluate_all('els=>els.map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,fits:e.scrollWidth<=e.clientWidth+1}})')
        assert all(b['fits'] for b in boxes), boxes
        # Read clockwise around the visible table, with matching rows on each side.
        assert boxes[0]['x'] < boxes[1]['x'] and abs(boxes[0]['y'] - boxes[1]['y']) < 1, boxes
        assert boxes[1]['y'] < boxes[2]['y'] < boxes[3]['y'], boxes
        assert boxes[4]['x'] < boxes[3]['x'] and abs(boxes[4]['y'] - boxes[3]['y']) < 1, boxes
        assert boxes[0]['y'] < boxes[5]['y'] < boxes[4]['y'] and abs(boxes[5]['y'] - boxes[2]['y']) < 1, boxes
        if shots and width in [390, 1440]:
            fig.screenshot(path=str(shots / f'position-map-{kind}-{width}.png'))
    reflow(page)
    if width == 320:
        spacing = page.add_style_tag(content=SPACING)
        reflow(page)
        assert maps.locator('.course-position-seat').evaluate_all('els=>els.every(e=>e.scrollWidth<=e.clientWidth+1)')
        spacing.evaluate('el=>el.remove()')


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    shots = Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    report = {'guided_hands': 0, 'short_lessons': 0, 'position_maps': 0, 'fresh_lesson_arrivals': 0, 'fallbacks': 0, 'axe': []}
    errors = []
    try:
        with sync_playwright() as pw:
            options = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                options['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**options)
            context = browser.new_context(accept_downloads=True)
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 900})
                response = page.goto(origin + ROUTE)
                assert response and response.status == 200
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                root = page.locator('[data-course-hand]')
                expect(root).to_have_class('course-hand course-enhanced')
                expect(root.locator('[data-course-scene]:visible')).to_have_count(1)
                expect(root.locator('[data-course-back]')).to_be_disabled()
                requests = []
                listener = lambda request: requests.append(request.url)
                page.on('request', listener)
                for index, scene_data in enumerate(DATA['hand']['scenes']):
                    scene = root.locator('#course-scene-' + scene_data['id'])
                    expect(scene).to_be_visible()
                    expect(scene.locator('[data-course-solution]')).to_be_hidden()
                    expect(root.locator('[data-course-progress]')).to_contain_text(f'Scene {index + 1} of 6')
                    expect(scene.locator('.course-counters dd')).to_have_text([str(scene_data[k]) for k in ['pot', 'hero_behind', 'opponent_behind']])
                    if index:
                        expect(scene.locator('h3')).to_be_focused()
                        assert scene.locator('h3').evaluate("el=>el.getBoundingClientRect().top >= document.querySelector('.site-header').getBoundingClientRect().bottom")
                    enter(page, scene.locator('[data-course-check]'))
                    expect(scene.locator('[data-course-status]')).to_contain_text('Choose one answer first')
                    if index < 5:
                        expect(root.locator('[data-course-next]')).to_be_disabled()
                    wrong = (scene_data['correct'] + 1) % 3
                    select(page, scene, wrong)
                    enter(page, scene.locator('[data-course-check]'))
                    expect(scene.locator('[data-course-status]')).to_contain_text('You can retry or continue')
                    expect(scene.locator('[data-choice-note]:visible')).to_have_count(1)
                    expect(scene.locator('[data-choice-note]:visible')).to_contain_text(scene_data['choices'][wrong][1])
                    if index < 5:
                        expect(root.locator('[data-course-next]')).to_be_enabled()
                    select(page, scene, scene_data['correct'])
                    expect(scene.locator('[data-course-solution]')).to_be_hidden()
                    if index < 5:
                        expect(root.locator('[data-course-next]')).to_be_disabled()
                    enter(page, scene.locator('[data-course-check]'))
                    expect(scene.locator('[data-course-status]')).to_contain_text('That matches the explanation')
                    expect(scene.locator('[data-choice-note]:visible')).to_have_count(1)
                    reflow(page)
                    if index == 2:
                        enter(page, root.locator('[data-course-back]'))
                        expect(root.locator('#course-scene-call input:checked')).to_have_value('2')
                        expect(root.locator('#course-scene-call [data-course-solution]')).to_be_visible()
                        enter(page, root.locator('[data-course-next]'))
                        enter(page, scene.locator('[data-course-retry]'))
                        expect(scene.locator('input:checked')).to_have_count(0)
                        expect(scene.locator('input').first).to_be_focused()
                        expect(scene.locator('[data-course-solution]')).to_be_hidden()
                        select(page, scene, scene_data['correct'])
                        enter(page, scene.locator('[data-course-check]'))
                    if index == 4 and shots and width in [390, 1440]:
                        scene.evaluate("el=>scrollTo({top:scrollY+el.getBoundingClientRect().top-document.querySelector('.site-header').getBoundingClientRect().height-20,behavior:'instant'})")
                        page.screenshot(path=str(shots / f'poker-course-river-{width}.png'))
                    if index < 5:
                        enter(page, root.locator('[data-course-next]'))
                expect(root.locator('[data-course-finish]')).to_be_visible()
                expect(root.locator('[data-course-next]')).to_be_hidden()
                assert not requests, requests
                page.remove_listener('request', listener)
                page.add_style_tag(content=SPACING)
                reflow(page)
                if os.environ.get('AXE_PATH') and width in [390, 1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    violations = page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
                    assert not violations, violations
                    report['axe'].append({'width': width, 'violations': violations})
                report['guided_hands'] += 1
            page.goto(origin + ROUTE + '#course-scene-river')
            expect(page.locator('[data-course-scene]:visible')).to_have_id('course-scene-river')
            expect(page.locator('[data-course-finish]')).to_be_hidden()
            page.evaluate("location.hash = 'course-scene-call'")
            expect(page.locator('[data-course-scene]:visible')).to_have_id('course-scene-call')
            page.goto(origin + '/poker/find/')
            page.locator('#finder-search').fill('current pot 47')
            card = page.locator('[data-finder-card]:visible').filter(has=page.locator('h3 a[href="' + ROUTE + '"]'))
            expect(card).to_have_count(1)
            link = card.locator('.finder-jump a')
            expect(link).to_have_attribute('href', ROUTE + '#course-scene-river')
            enter(page, link)
            expect(page.locator('[data-course-hand]')).to_have_class('course-hand course-enhanced')
            expect(page.locator('[data-course-scene]:visible')).to_have_id('course-scene-river')
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 900})
                for index, lesson in enumerate(DATA['lessons']):
                    route = '/poker/' + lesson['slug'] + '/'
                    page.goto(origin + route + '#course-first-pass-title')
                    page.evaluate('()=>document.fonts.ready.then(()=>true)')
                    first = page.locator('.course-first-pass')
                    assert page.evaluate("getComputedStyle(document.documentElement).scrollBehavior === 'auto'")
                    expect(first).to_contain_text(f'Stage {index + 1} of 6')
                    expect(first.locator('#course-lesson-answer > div')).to_be_hidden()
                    expect(first.locator('.course-lesson-options > div')).to_be_hidden()
                    expect(first.locator('input,textarea,button')).to_have_count(0)
                    expect(first.locator('#course-first-pass-title')).to_be_in_viewport()
                    reflow(page)
                    if shots and index == 0 and width in [390, 1440]:
                        page.screenshot(path=str(shots / f'short-lesson-start-{width}.png'))
                    if index == 1:
                        check_position_maps(page, shots, width)
                        report['position_maps'] += 1
                    enter(page, first.locator('#course-lesson-answer > summary'))
                    expect(first.locator('#course-lesson-answer > div')).to_be_visible()
                    if index == 1:
                        expect(first.locator('#course-lesson-answer .course-position-orders')).to_be_visible()
                        if shots and width in [390, 1440]:
                            first.locator('#course-lesson-answer').screenshot(path=str(shots / f'position-map-explanation-{width}.png'))
                    expect(first.locator('#course-lesson-answer a')).to_have_attribute('href', SHORT[index]['attempt']['repair'])
                    if width == 390:
                        enter(page, first.locator('#course-lesson-answer a'))
                        repair = SHORT[index]['attempt']['repair']
                        expect(page).to_have_url(origin + repair)
                        target = page.locator('#' + repair.split('#')[1])
                        expect(target).to_be_in_viewport()
                        assert target.evaluate("el=>el.getBoundingClientRect().top >= document.querySelector('.site-header').getBoundingClientRect().bottom")
                        page.goto(origin + route + '#course-lesson-try')
                        reveal_short_answer(page)
                    if shots and index in [0, 4] and width in [390, 1440]:
                        page.goto(origin + route + '#course-lesson-try')
                        reveal_short_answer(page)
                        page.locator('#course-lesson-try').evaluate("el=>scrollTo({top:scrollY+el.getBoundingClientRect().top-document.querySelector('.site-header').getBoundingClientRect().height-20,behavior:'instant'})")
                        page.screenshot(path=str(shots / f'short-lesson-task-{index + 1}-{width}.png'))
                    if os.environ.get('AXE_PATH') and width in [390, 1440]:
                        page.add_script_tag(path=os.environ['AXE_PATH'])
                        violations = page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
                        assert not violations, violations
                    page.add_style_tag(content=SPACING)
                    reflow(page)
                    enter(page, page.locator('#course-lesson-answer > summary'))
                    expect(page.locator('#course-lesson-answer > div')).to_be_hidden()
                    page.emulate_media(media='print')
                    expect(page.locator('#course-lesson-answer > div')).to_be_visible()
                    if index == 1:
                        expect(page.locator('.course-position-map')).to_have_count(2)
                        expect(page.locator('#course-lesson-answer .course-position-orders')).to_be_visible()
                    page.emulate_media(media='screen')
                    enter(page, page.locator('.course-lesson-next a.button'))
                    expected = '/poker/' + DATA['lessons'][index + 1]['slug'] + '/' if index < 5 else '/poker/beginner-checkpoint/'
                    expect(page).to_have_url(origin + expected)
                    report['short_lessons'] += 1
            for index, lesson in enumerate(DATA['lessons']):
                page.goto(origin + '/poker/' + lesson['slug'] + '/')
                first = page.locator('.course-first-pass')
                expect(first).to_contain_text(f'Stage {index + 1} of 6')
                enter(page, first.locator('.course-lesson-options > summary'))
                enter(page, first.locator('a[href="#' + lesson['first_pass'][0][0] + '"]'))
                expect(page).to_have_url(origin + '/poker/' + lesson['slug'] + '/#' + lesson['first_pass'][0][0])
                expect(page.locator('#' + lesson['first_pass'][0][0])).to_be_in_viewport()
                enter(page, first.locator('a[href="' + lesson['practice'] + '"]'))
                expect(page).to_have_url(origin + lesson['practice'])
                expect(page.locator('#' + lesson['practice'].split('#')[1])).to_be_in_viewport()
                report['fresh_lesson_arrivals'] += 1
                page.goto(origin + '/poker/' + lesson['slug'] + '/')
                enter(page, page.locator('.course-stage-end a.button'))
                expected = '/poker/' + DATA['lessons'][index + 1]['slug'] + '/' if index < 5 else '/poker/beginner-checkpoint/'
                expect(page).to_have_url(origin + expected)
            page.goto(origin + ROUTE)
            enter(page, page.locator('#course-workbook-preview summary'))
            preview = page.locator('#course-workbook-preview pre').inner_text()
            with page.expect_download() as event:
                enter(page, page.locator('#beginner-practice a[download]'))
            assert Path(event.value.path()).read_text() == preview == (ROOT / 'downloads/poker-beginner-study-card.txt').read_text()
            page.emulate_media(media='print')
            expect(page.locator('[data-course-scene]:visible')).to_have_count(6)
            expect(page.locator('[data-course-solution]:visible')).to_have_count(6)
            expect(page.locator('[data-choice-note]:visible')).to_have_count(18)
            expect(page.locator('[data-course-check]:visible')).to_have_count(0)
            page.emulate_media(media='screen')
            assert context.cookies() == []
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
            for scripting in [False, True]:
                fallback = browser.new_context(java_script_enabled=scripting, viewport={'width': 390, 'height': 900})
                fallback.route('**/*', lambda r: r.abort() if 'poker-course.js' in r.request.url or urlsplit(r.request.url).hostname != '127.0.0.1' else r.continue_())
                native = fallback.new_page()
                native.goto(origin + ROUTE)
                expect(native.locator('[data-course-scene]:visible')).to_have_count(6)
                expect(native.locator('[data-course-check]:visible')).to_have_count(0)
                for scene in DATA['hand']['scenes']:
                    solution = native.locator('#course-scene-' + scene['id'] + ' [data-course-solution]')
                    enter(native, solution.locator('summary'))
                    expect(solution.locator('div')).to_be_visible()
                    expect(solution).to_contain_text(scene['solution'])
                reflow(native)
                enter(native, native.locator('#path-cards h3 a'))
                expect(native.locator('.course-first-pass')).to_be_visible()
                enter(native, native.locator('.course-stage-end a.button'))
                expect(native).to_have_url(origin + '/poker/starting-hand-decisions/')
                for index, lesson in enumerate(DATA['lessons']):
                    native.goto(origin + '/poker/' + lesson['slug'] + '/#course-lesson-try')
                    if index == 1:
                        native.evaluate('()=>document.fonts.ready.then(()=>true)')
                        check_position_maps(native)
                        report['position_maps'] += 1
                    expect(native.locator('#course-lesson-answer > div')).to_be_hidden()
                    enter(native, native.locator('#course-lesson-answer > summary'))
                    expect(native.locator('#course-lesson-answer > div')).to_be_visible()
                    enter(native, native.locator('.course-lesson-next a.button'))
                    expected = '/poker/' + DATA['lessons'][index + 1]['slug'] + '/' if index < 5 else '/poker/beginner-checkpoint/'
                    expect(native).to_have_url(origin + expected)
                    native.wait_for_load_state('domcontentloaded')
                    reflow(native)
                fallback.close()
                report['fallbacks'] += 1
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print('PASS: six-scene keyboard practice, mistake feedback, retry, revisit, six-stage progression, exact worksheet, search, print, no-script and privacy.')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
