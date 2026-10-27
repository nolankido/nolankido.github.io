"""Read-only local browser checks for field-guide routes, reflow and printable sheets."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from time import monotonic
from urllib.parse import urlsplit
import json
import os
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ('first-live-tournament', 'choosing-a-tournament', 'registration-and-reentry', 'tournament-day', 'recording-hands', 'choosing-study-tools', 'evaluating-poker-advice')
FIRST_EVENT = '/poker/first-live-tournament/'
PLANNER = '/downloads/poker-event-planner.md'
CHECKLISTS = '/poker/tournament-checklists/'
PLAN_DESTINATIONS = (
    '#before-you-go', '#registration', '#taking-a-seat', '#unclear-action',
    '/poker/tournament-day/#breaks', '#a-useful-finish',
)

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
    def copyfile(self, source, outputfile):
        try: super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError): pass


def assert_reflow(page):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')


def wait_for_fonts(page):
    # A loaded document can still be replacing fallback fonts. Poll the native
    # state from the driver, as local_fonts_browser does; no in-page Promise or
    # animation-frame callback is required when page scripts are disabled.
    deadline = monotonic() + 5
    while True:
        status = page.evaluate('document.fonts.status')
        if status == 'loaded':
            return
        assert monotonic() < deadline, ('font readiness timeout', page.url, status)
        page.wait_for_timeout(50)


def goto_ready(page, url):
    page.goto(url)
    wait_for_fonts(page)


def assert_jump_target(page, target):
    """A keyboard jump must leave its heading readable below the sticky header."""
    wait_for_fonts(page)
    expect(target).to_be_visible()
    expect(target).to_be_in_viewport()
    header = page.locator('.site-header')
    if header.is_visible():
        heading_box, header_box = target.bounding_box(), header.bounding_box()
        assert heading_box['y'] >= header_box['y'] + header_box['height'] - 1, (heading_box, header_box)


def assert_first_event_plan(page):
    plan = page.locator('#first-event-plan')
    expect(plan).to_be_visible()
    expect(plan.locator('#first-event-plan-title')).to_be_visible()
    expect(plan.locator('ol > li')).to_have_count(6)
    for destination in PLAN_DESTINATIONS:
        expect(plan.locator(f'a[href="{destination}"]')).to_be_visible()
    expect(page.locator('#questions-to-confirm')).to_be_visible()
    expect(plan.locator(f'a[href="{CHECKLISTS}#event-planner"]')).to_be_visible()
    expect(plan.locator(f'a[download][href="{PLANNER}"]')).to_be_visible()
    assert plan.evaluate('el => el.scrollWidth <= el.clientWidth + 1')
    assert_reflow(page)
    return plan


def download_planner(page, link, report):
    expect(link).to_be_visible()
    link.focus()
    expect(link).to_be_focused()
    expect(link).to_be_in_viewport()
    with page.expect_download() as pending:
        page.keyboard.press('Enter')
    download = pending.value
    assert download.suggested_filename == 'poker-event-planner.md'
    assert Path(download.path()).read_bytes() == (ROOT / PLANNER.lstrip('/')).read_bytes()
    report['planner_downloads'] += 1


def check_first_event_plan(browser, origin, screenshots, errors, report):
    """Exercise the same private planning route with and without page scripts."""
    blank = (ROOT / PLANNER.lstrip('/')).read_text(encoding='utf-8')
    writes = []
    for scripts in (True, False):
        ctx = browser.new_context(java_script_enabled=scripts, accept_downloads=True,
                                  reduced_motion='reduce')
        def route(request):
            if request.request.method not in {'GET', 'HEAD'}:
                writes.append(request.request.url)
            request.continue_() if urlsplit(request.request.url).hostname == '127.0.0.1' else request.abort()
        ctx.route('**/*', route)
        page = ctx.new_page()
        page.on('pageerror', lambda err: errors.append(str(err)))
        for width in (320, 390, 768, 1440):
            print(f'Checking first-event plan: width={width}; page scripts={scripts}', flush=True)
            page.set_viewport_size({'width': width, 'height': 950})
            goto_ready(page, origin + FIRST_EVENT)
            plan = assert_first_event_plan(page)
            assert page.locator('main form, main input, main textarea, main iframe').count() == 0
            report['first_event_layouts'] += 1

            opening = page.locator('a[href="#first-event-plan"]').first
            opening.focus()
            expect(opening).to_be_focused()
            expect(opening).to_be_in_viewport()
            page.keyboard.press('Enter')
            expect(page).to_have_url(origin + FIRST_EVENT + '#first-event-plan')
            assert_jump_target(page, plan.locator('#first-event-plan-title'))
            report['first_event_entry_journeys'] += 1
            if screenshots and scripts and width in (390, 1440):
                page.screenshot(path=str(screenshots / f'first-event-plan-jump-{width}.png'))

            for destination in PLAN_DESTINATIONS:
                goto_ready(page, origin + FIRST_EVENT)
                link = page.locator(f'#first-event-plan a[href="{destination}"]')
                link.focus()
                expect(link).to_be_focused()
                expect(link).to_be_in_viewport()
                page.keyboard.press('Enter')
                target_url = origin + (FIRST_EVENT + destination if destination.startswith('#') else destination)
                expect(page).to_have_url(target_url)
                assert_jump_target(page, page.locator('#' + urlsplit(target_url).fragment))
                report['first_event_step_journeys'] += 1

            goto_ready(page, origin + FIRST_EVENT)
            # add_style_tag waits for a load event that no-script contexts do
            # not dispatch. Apply the same test CSS synchronously, as in the
            # existing answer-review suite, without enabling page scripts.
            page.evaluate('css => { const style = document.createElement("style"); style.textContent = css; document.head.appendChild(style); }',
                          '*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
            plan = assert_first_event_plan(page)
            for item in plan.locator('ol > li').all():
                assert item.evaluate('el => el.scrollWidth <= el.clientWidth + 1')
            report['first_event_spacing'] += 1

            goto_ready(page, origin + FIRST_EVENT)
            page.emulate_media(media='print')
            assert_first_event_plan(page)
            expect(page.locator('#questions-to-confirm')).to_be_visible()
            for item in page.locator('#first-event-plan ol > li').all():
                expect(item).to_be_visible()
            report['first_event_print_layouts'] += 1
            if screenshots and scripts and width == 1440:
                pdf = page.pdf(path=str(screenshots / 'first-event-plan-print.pdf'), format='A4',
                               print_background=True,
                               margin={'top': '15mm', 'bottom': '15mm', 'left': '15mm', 'right': '15mm'})
                assert pdf.startswith(b'%PDF-')
                report['first_event_print_pdf_captures'] += 1
            page.emulate_media(media='screen')
            download_planner(page, page.locator(f'#first-event-plan a[download][href="{PLANNER}"]'), report)

            preview_link = page.locator(f'#first-event-plan a[href="{CHECKLISTS}#event-planner"]')
            preview_link.focus()
            expect(preview_link).to_be_focused()
            expect(preview_link).to_be_in_viewport()
            page.keyboard.press('Enter')
            expect(page).to_have_url(origin + CHECKLISTS + '#event-planner')
            assert_jump_target(page, page.locator('#event-planner'))
            sheet = page.locator('pre.field-sheet').first
            expect(sheet).to_be_visible()
            assert sheet.text_content() == blank
            assert sheet.evaluate('el => el.scrollWidth <= el.clientWidth + 1')
            assert_reflow(page)
            report['planner_preview_journeys'] += 1
            download_planner(page, page.locator(f'a[download][href="{PLANNER}"]'), report)
            page.emulate_media(media='print')
            expect(sheet).to_be_visible()
            assert sheet.text_content() == blank
            assert sheet.evaluate('el => el.scrollWidth <= el.clientWidth + 1')
            assert_reflow(page)
            report['planner_print_layouts'] += 1
            page.emulate_media(media='screen')

            if scripts and width == 390 and os.environ.get('AXE_PATH'):
                for destination in (FIRST_EVENT, CHECKLISTS):
                    goto_ready(page, origin + destination)
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    audit = page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>v.id),incomplete:r.incomplete.map(v=>v.id)}}")
                    assert not audit['violations'], (destination, audit)
                    report['axe'].append({'route': destination, **audit})
            assert ctx.cookies() == []
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
        ctx.close()
    assert not writes, writes


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    screenshots = Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if screenshots: screenshots.mkdir(parents=True, exist_ok=True)
    errors = []
    report = {'existing_route_layouts': 0, 'first_event_layouts': 0,
              'first_event_entry_journeys': 0, 'first_event_step_journeys': 0,
              'first_event_spacing': 0, 'first_event_print_layouts': 0,
              'first_event_print_pdf_captures': 0, 'planner_preview_journeys': 0,
              'planner_downloads': 0, 'planner_print_layouts': 0, 'axe': []}
    try:
        with sync_playwright() as pw:
            opts = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'): opts['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**opts)
            context = browser.new_context()
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = context.new_page()
            page.on('pageerror', lambda err: errors.append(str(err)))
            routes = list(GUIDES) + ['live-tournament-guide', 'tournament-checklists']
            for width in [320, 390, 768, 1280]:
                page.set_viewport_size({'width': width, 'height': 900})
                for slug in routes:
                    response = page.goto(origin + '/poker/' + slug + '/')
                    assert response and response.status == 200, slug
                    assert page.locator('h1').count() == 1, slug
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (slug, width)
                    assert page.locator('main form, main input, main textarea, main iframe').count() == 0, slug
                    report['existing_route_layouts'] += 1
                    if width in [390, 1280] and slug in ['live-tournament-guide', 'choosing-a-tournament', 'tournament-checklists'] and screenshots:
                        page.screenshot(path=str(screenshots / f'poker-field-{slug}-{width}.png'), full_page=True)
            page.goto(origin + '/poker/library/')
            page.locator('[data-filter="tournaments"]').click()
            expect(page.locator('#library-grid a[href="/poker/first-live-tournament/"]')).to_be_visible()
            page.locator('#library-search').fill('reentry')
            expect(page.locator('#library-grid a[href="/poker/registration-and-reentry/"]')).to_be_visible()
            page.locator('#library-reset').click()
            page.goto(origin + '/poker/registration-and-reentry/')
            answer = page.locator('details.viewer-question')
            assert answer.count() == 1
            expect(answer.locator('div')).not_to_be_visible()
            answer.locator('summary').focus()
            page.keyboard.press('Enter')
            expect(answer.locator('div')).to_be_visible()
            page.goto(origin + '/poker/tournament-checklists/')
            page.emulate_media(media='print')
            expect(page.locator('pre.field-sheet:visible')).to_have_count(3)
            for sheet in page.locator('pre.field-sheet').all():
                assert sheet.inner_text().strip().startswith('# ')
                assert sheet.evaluate('(el) => el.scrollWidth <= el.clientWidth + 1')
            assert context.cookies() == []
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
            offline = browser.new_context(java_script_enabled=False)
            offline.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            static = offline.new_page()
            static.goto(origin + '/poker/live-tournament-guide/')
            for slug in GUIDES:
                assert static.locator('a[href="/poker/' + slug + '/"]').count() >= 1
            static.goto(origin + '/poker/tournament-checklists/')
            expect(static.locator('pre.field-sheet')).to_have_count(3)
            offline.close()
            context.close()
            check_first_event_plan(browser, origin, screenshots, errors, report)
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print('PASS: nine new routes at four widths; discovery, keyboard disclosure, print, no-JS and privacy checks.')
    report['status'] = 'pass'
    print(json.dumps(report, indent=2))

if __name__ == '__main__': main()
