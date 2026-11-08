"""Offline browser journeys from Find to validated standalone article sections.

Serve committed files through intercepted requests, not a local HTTP server.
External requests are blocked. No query, cookie or storage is sent remotely.
"""
import json
import mimetypes
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright, expect


ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://nolankido.test'
SEARCH = (ROOT / 'find/index.html').read_text(encoding='utf-8')
CARD_COUNT = SEARCH.count('class="find-item"')
CASES = (
    ('form factor', '/technology/local-ai-gaming-laptop/', 'laptop-hardware', 'technology', 'guide'),
    ('invented offer', '/technology/review-reply-evidence-audit/', 'reply-audit-boundaries', 'technology', 'guide'),
    ('tournament media', '/poker/nolan-kido/', 'creator-introduction-title', 'poker', 'profile'),
    ('final round', '/poker/episodes/portland-meadows-standoff/', 'standoff-format-title', 'poker', 'episode'),
    ('money bubble', '/poker/episodes/portland-meadows-ep1/', 'six-four-decision', 'poker', 'episode'),
)
DATA_BLOCK = re.compile(r'<!-- Search section index: start -->.*?<!-- Search section index: end -->', re.S)


def request_handler(mode='normal'):
    def fulfill(route):
        url = urlsplit(route.request.url)
        if url.scheme != 'https' or url.netloc != 'nolankido.test':
            route.abort()
            return
        path = (ROOT / unquote(url.path).lstrip('/')).resolve()
        if not path.is_relative_to(ROOT):
            route.abort()
            return
        if path.is_dir():
            path /= 'index.html'
        if not path.is_file():
            route.fulfill(status=404, body='Missing local fixture')
            return
        if url.path == '/find/' and mode != 'normal':
            substitute = '' if mode == 'missing' else '<script type="application/json" id="find-section-data">{broken</script>'
            body = DATA_BLOCK.sub(lambda _: substitute, SEARCH).encode('utf-8')
        else:
            body = path.read_bytes()
        route.fulfill(status=200, body=body,
                      content_type=mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
    return fulfill


def open_search(page):
    page.goto(BASE + '/find/', wait_until='load')
    page.evaluate('async () => { await document.fonts.ready; }')
    expect(page.locator('#find-controls')).to_be_visible()


def submit(page, requests, query, path, anchor):
    before = len(requests)
    page.locator('#find-query').fill(query)
    page.locator('#find-query').press('Enter')
    expect(page.locator('#find-results')).to_be_focused()
    link = page.locator('.find-section-matches a[href="' + path + '#' + anchor + '"]')
    expect(link).to_be_visible()
    assert page.url == BASE + '/find/' and len(requests) == before, 'Search must not navigate or make a request'
    assert page.locator('.find-item').evaluate_all(
        '(items) => items.every(item => item.querySelectorAll(".find-section-matches a").length <= 3)')
    return link


def main():
    report = {'keyboard_journeys': 0, 'filter_checks': 0, 'enlarged_result_views': 0,
              'data_fallbacks': 0, 'no_script_routes': 0}
    errors = []
    with sync_playwright() as pw:
        launch = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'):
            launch['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**launch)
        try:
            for width in (320, 390, 768, 1440):
                context = browser.new_context(viewport={'width': width, 'height': 950},
                                              reduced_motion='reduce', service_workers='block')
                context.route('**/*', request_handler())
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                requests = []
                page.on('request', lambda request: requests.append(request.url))
                open_search(page)
                for query, path, anchor, interest, kind in CASES:
                    link = submit(page, requests, query, path, anchor)
                    actual_width = page.evaluate('document.documentElement.scrollWidth')
                    assert actual_width <= width + 1, (width, query, actual_width)
                    link.focus()
                    page.keyboard.press('Enter')
                    page.wait_for_url(BASE + path + '#' + anchor, wait_until='load')
                    page.evaluate('async () => { await document.fonts.ready; }')
                    target = page.locator('#' + anchor)
                    expect(target).to_be_in_viewport()
                    metrics = target.evaluate('''node => ({top: node.getBoundingClientRect().top,
                        header: document.querySelector('.site-header').getBoundingClientRect().bottom})''')
                    assert metrics['top'] >= metrics['header'] - 1, (width, path, metrics)
                    page.go_back(wait_until='load')
                    expect(page.locator('#find-query')).to_have_value('')
                    expect(page.locator('.find-section-matches a')).to_have_count(0)
                    report['keyboard_journeys'] += 1
                assert context.cookies() == []
                assert page.evaluate('localStorage.length + sessionStorage.length') == 0
                context.close()

            context = browser.new_context(viewport={'width': 390, 'height': 950}, reduced_motion='reduce')
            context.route('**/*', request_handler())
            page = context.new_page()
            requests = []
            page.on('request', lambda request: requests.append(request.url))
            page.on('pageerror', lambda error: errors.append(str(error)))
            open_search(page)
            for query, path, anchor, interest, kind in CASES:
                link = submit(page, requests, query, path, anchor)
                page.locator('#find-interest').select_option(interest)
                page.locator('#find-kind').select_option(kind)
                expect(link).to_be_visible()
                page.locator('#find-kind').select_option('identity')
                expect(link).to_be_hidden()
                page.locator('#find-reset').press('Enter')
                expect(page.locator('#find-query')).to_be_focused()
                expect(page.locator('#find-query')).to_have_value('')
                expect(page.locator('#find-interest')).to_have_value('')
                expect(page.locator('#find-kind')).to_have_value('')
                report['filter_checks'] += 1
            for width in (320, 390):
                page.set_viewport_size({'width': width, 'height': 950})
                open_search(page)
                page.add_style_tag(content='html{font-size:200%!important}*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}')
                for query, path, anchor, *_ in CASES:
                    submit(page, requests, query, path, anchor)
                    assert page.evaluate('document.documentElement.scrollWidth') <= width + 1
                    report['enlarged_result_views'] += 1
                if os.environ.get('SCREENSHOT_DIR'):
                    folder = Path(os.environ['SCREENSHOT_DIR'])
                    folder.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(folder / f'standalone-search-{width}-enlarged.png'))
            assert context.cookies() == []
            assert page.evaluate('localStorage.length + sessionStorage.length') == 0
            context.close()

            for mode in ('missing', 'malformed'):
                context = browser.new_context()
                context.route('**/*', request_handler(mode))
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                open_search(page)
                page.locator('#find-query').fill('local AI gaming laptop')
                page.locator('#find-query').press('Enter')
                expect(page.locator('.find-item:visible h3 a[href="/technology/local-ai-gaming-laptop/"]')).to_be_visible()
                expect(page.locator('.find-section-matches a')).to_have_count(0)
                report['data_fallbacks'] += 1
                context.close()

            context = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 950})
            context.route('**/*', request_handler())
            page = context.new_page()
            page.goto(BASE + '/find/', wait_until='load')
            expect(page.locator('#find-controls')).to_be_hidden()
            expect(page.locator('.find-item')).to_have_count(CARD_COUNT)
            for _, path, _, interest, _ in CASES:
                group = page.locator('#browse-' + interest)
                if group.get_attribute('open') is None:
                    group.locator('summary').focus()
                    page.keyboard.press('Enter')
                link = group.locator('h3 a[href="' + path + '"]')
                expect(link).to_be_visible()
                link.focus()
                page.keyboard.press('Enter')
                page.wait_for_url(BASE + path, wait_until='load')
                expect(page.locator('h1')).to_be_visible()
                page.go_back(wait_until='load')
                report['no_script_routes'] += 1
            assert context.cookies() == []
            context.close()
            assert not errors, errors
        finally:
            browser.close()
    report.update(status='pass', native_cards=CARD_COUNT,
                  method='offline Chromium, intercepted local files, external requests blocked')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
