"""Real beginner arrival, keyboard answers, reflow and no-script reading."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
from playwright.sync_api import sync_playwright, expect
from field_guide_browser import QuietHandler, ROOT

ROUTE = '/poker/first-flop-decisions/'
SPACING = '* {line-height:1.5 !important;letter-spacing:.12em !important;word-spacing:.16em !important} p {margin-bottom:2em !important}'


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    shots = Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots: shots.mkdir(parents=True, exist_ok=True)
    report = {'viewport_checks': 0, 'keyboard_answers': 0, 'arrivals': 0, 'axe': []}
    errors = []
    try:
        with sync_playwright() as pw:
            opts = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'): opts['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**opts)
            context = browser.new_context()
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = context.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 900})
                response = page.goto(origin + ROUTE)
                assert response and response.status == 200
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                expect(page.locator('h1')).to_have_text('Your first decisions after the flop.')
                expect(page.locator('details.viewer-question')).to_have_count(8)
                expect(page.locator('details.viewer-question[open]')).to_have_count(0)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), width
                if shots and width in [390, 1440]:
                    page.screenshot(path=str(shots / f'flop-opening-{width}.png'))
                    card_case = page.locator('[data-example="flush-loses"]')
                    card_case.evaluate("el=>{const h=document.querySelector('.site-header').getBoundingClientRect().height;window.scrollTo({top:scrollY+el.getBoundingClientRect().top-h-16,behavior:'instant'});}")
                    assert card_case.evaluate("el=>el.getBoundingClientRect().top >= document.querySelector('.site-header').getBoundingClientRect().bottom")
                    expect(card_case).to_be_in_viewport(ratio=1)
                    page.screenshot(path=str(shots / f'flop-cards-{width}.png'))
                for q in page.locator('details.viewer-question').all():
                    summary = q.locator('summary')
                    summary.focus(); page.keyboard.press('Enter')
                    expect(q.locator('div')).to_be_visible()
                    report['keyboard_answers'] += 1
                    if q.get_attribute('id') == 'check-shared' and shots and width in [390, 1440]:
                        # Cancel smooth motion before recording a viewport.
                        # Center the actual answer, leaving the sticky header clear.
                        q.evaluate('''el=>{const r=el.getBoundingClientRect();
                            const header=document.querySelector('.site-header').getBoundingClientRect().height;
                            const top=Math.max(header+16,(innerHeight-r.height)/2);
                            window.scrollTo({top:scrollY+r.top-top,behavior:'instant'});}''')
                        expect(q.locator('summary')).to_be_in_viewport()
                        expect(q.locator('div')).to_be_in_viewport()
                        assert q.evaluate("el=>el.getBoundingClientRect().top >= document.querySelector('.site-header').getBoundingClientRect().bottom")
                        page.screenshot(path=str(shots / f'flop-answer-{width}.png'))
                expect(page.locator('#check-snapshot')).to_contain_text('12 - 4 = 8')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), ('open', width)
                page.add_style_tag(content=SPACING)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), ('spacing', width)
                report['viewport_checks'] += 3
                if os.environ.get('AXE_PATH') and width in [390, 1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    result = page.evaluate('''async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}''')
                    assert not result, (width, result)
                    report['axe'].append({'width': width, 'violations': result})
            for source, selector in [('/poker/starting-hand-decisions/', 'main a'),
                                     ('/poker/topics/learn/', 'main a'),
                                     ('/poker/free-poker-learning-path/', 'main a')]:
                page.goto(origin + source)
                link = page.locator(selector + '[href="' + ROUTE + '"]:visible').first
                link.focus(); page.keyboard.press('Enter')
                expect(page).to_have_url(origin + ROUTE)
                expect(page.locator('h1')).to_be_visible()
                report['arrivals'] += 1
            for route, field, result in [('/poker/library/', '#library-search', '#library-grid'),
                                         ('/poker/find/', '#finder-search', 'main'),
                                         ('/find/', '#find-query', 'main')]:
                page.goto(origin + route)
                page.locator(field).fill('after the flop'); page.locator(field).press('Enter')
                link = page.locator(result + ' a[href="' + ROUTE + '"]:visible').first
                expect(link).to_be_visible()
                link.focus(); page.keyboard.press('Enter')
                expect(page).to_have_url(origin + ROUTE)
                report['arrivals'] += 1
            assert context.cookies() == []
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
            offline = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 900})
            offline.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            static = offline.new_page()
            static.goto(origin + '/poker/starting-hand-decisions/')
            static.evaluate('()=>document.fonts.ready.then(()=>true)')
            static.locator('.reader-related a[href="' + ROUTE + '"]').focus()
            static.keyboard.press('Enter')
            expect(static).to_have_url(origin + ROUTE)
            static.wait_for_load_state('domcontentloaded')
            expect(static.locator('details.viewer-question')).to_have_count(8)
            static.locator('#check-shared summary').focus(); static.keyboard.press('Enter')
            expect(static.locator('#check-shared div')).to_contain_text('flush loses to a full house')
            assert static.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown(); server.server_close()
    print('PASS: postflop practice works at four widths, with keyboard answers, six discovery routes and no JavaScript.')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
