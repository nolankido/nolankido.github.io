"""Offline native arrivals on the profile and reply audit, including large text.

Only local files are served. The optional screenshot directory contains QA
images, not user data. No account, HTTP server or external service is needed.
"""
import json
import os
from pathlib import Path
import time
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

from standalone_search_sections_browser import BASE, ROOT, request_handler, submit


PAGES = (
    ('/technology/review-reply-evidence-audit/', '.reply-independent-case',
     'invented offer', 'reply-audit-boundaries'),
    ('/poker/nolan-kido/', '.poker-player-profile',
     'tournament media', 'creator-introduction-title'),
)
ENLARGED = ('html{font-size:200%!important}'
            '*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}')


def serve(enlarged, fonts):
    original = request_handler()

    def fulfill(route):
        url = urlsplit(route.request.url)
        if fonts == 'fallback' and route.request.resource_type == 'font':
            route.abort()
        elif (enlarged and url.scheme == 'https' and url.netloc == 'nolankido.test'
              and url.path in {'/find/', *(item[0] for item in PAGES)}):
            path = ROOT / url.path.lstrip('/') / 'index.html'
            text = path.read_text(encoding='utf-8')
            assert text.count('</head>') == 1
            text = text.replace('</head>', '<style>' + ENLARGED + '</style></head>', 1)
            route.fulfill(status=200, body=text.encode('utf-8'), content_type='text/html')
        else:
            original(route)

    return fulfill


def ready(page, fonts):
    # Poll from the runner: a pending page promise can stall when page scripts
    # are disabled. Fail explicitly rather than leave an unbounded font wait.
    deadline = time.monotonic() + 10
    page.evaluate('document.body.getBoundingClientRect().height')
    while True:
        value = page.evaluate('''() => ({status: document.fonts.status,
            loaded: Array.from(document.fonts).filter(face => face.status === 'loaded').length})''')
        if value['status'] == 'loaded' and (fonts == 'fallback' or value['loaded'] > 0):
            assert value['loaded'] == 0 if fonts == 'fallback' else value['loaded'] > 0
            return
        if time.monotonic() >= deadline:
            raise AssertionError(('Local fonts did not settle', page.url, fonts, value))
        time.sleep(.02)


def clear_target(page, anchor, width):
    node = page.locator('#' + anchor)
    expect(node).to_be_in_viewport()
    value = node.evaluate('''node => ({top: node.getBoundingClientRect().top,
        header: document.querySelector('.site-header').getBoundingClientRect().bottom,
        scrollWidth: document.documentElement.scrollWidth,
        margin: getComputedStyle(node).scrollMarginTop})''')
    assert value['top'] >= value['header'] - 1, (page.url, width, anchor, value)
    assert value['scrollWidth'] <= width + 1, (page.url, width, value)
    return value


def native_fragment(page, path, anchor, fonts):
    page.goto(BASE + path + '#' + anchor, wait_until='load')
    ready(page, fonts)


def main():
    report = {'page_layouts': 0, 'heading_arrivals': 0, 'legacy_arrivals': 0,
              'keyboard_skip_links': 0, 'enlarged_search_journeys': 0}
    samples = []
    errors = []
    with sync_playwright() as pw:
        launch = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'):
            launch['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**launch)
        try:
            for fonts in ('committed', 'fallback'):
                for enlarged in (False, True):
                    context = browser.new_context(viewport={'width': 320, 'height': 950},
                                                  java_script_enabled=False,
                                                  reduced_motion='reduce', service_workers='block')
                    context.route('**/*', serve(enlarged, fonts))
                    page = context.new_page()
                    page.set_default_timeout(10000)
                    for width in (320, 390, 620, 768, 1024, 1440):
                        page.set_viewport_size({'width': width, 'height': 950})
                        for path, article, _, sample_anchor in PAGES:
                            page.goto(BASE + path, wait_until='load')
                            ready(page, fonts)
                            assert page.evaluate('document.documentElement.scrollWidth') <= width + 1
                            anchors = page.locator(article + ' h2[id]').evaluate_all('(nodes) => nodes.map(node => node.id)')
                            assert len(anchors) == (9 if 'reply-' in path else 6)
                            report['page_layouts'] += 1
                            for anchor in anchors:
                                native_fragment(page, path, anchor, fonts)
                                metrics = clear_target(page, anchor, width)
                                report['heading_arrivals'] += 1
                                if enlarged and width == 320 and anchor == sample_anchor:
                                    samples.append(dict(fonts=fonts, path=path, **metrics))
                            if path == '/poker/nolan-kido/':
                                native_fragment(page, path, 'creator-introduction', fonts)
                                clear_target(page, 'creator-introduction', width)
                                report['legacy_arrivals'] += 1
                            page.goto(BASE + path, wait_until='load')
                            ready(page, fonts)
                            page.locator('.skip-link').focus()
                            page.keyboard.press('Enter')
                            expect(page.locator('#main')).to_be_focused()
                            clear_target(page, 'main', width)
                            report['keyboard_skip_links'] += 1
                    assert context.cookies() == []
                    context.close()
                    print(json.dumps(dict(fonts=fonts, enlarged=enlarged, **report)), flush=True)

                context = browser.new_context(viewport={'width': 320, 'height': 950},
                                              reduced_motion='reduce', service_workers='block')
                context.route('**/*', serve(True, fonts))
                page = context.new_page()
                page.set_default_timeout(10000)
                page.on('pageerror', lambda error: errors.append(str(error)))
                requests = []
                page.on('request', lambda request: requests.append(request.url))
                for width in (320, 390, 768, 1440):
                    page.set_viewport_size({'width': width, 'height': 950})
                    for path, _, query, anchor in PAGES:
                        page.goto(BASE + '/find/', wait_until='load')
                        ready(page, fonts)
                        link = submit(page, requests, query, path, anchor)
                        link.focus()
                        page.keyboard.press('Enter')
                        page.wait_for_url(BASE + path + '#' + anchor, wait_until='load')
                        ready(page, fonts)
                        clear_target(page, anchor, width)
                        assert page.evaluate('localStorage.length + sessionStorage.length') == 0
                        report['enlarged_search_journeys'] += 1
                        if os.environ.get('SCREENSHOT_DIR') and fonts == 'committed' and width in (320, 1440):
                            folder = Path(os.environ['SCREENSHOT_DIR'])
                            folder.mkdir(parents=True, exist_ok=True)
                            name = 'reply' if 'reply-' in path else 'profile'
                            page.screenshot(path=str(folder / f'{name}-arrival-{width}-enlarged.png'))
                assert context.cookies() == []
                context.close()
            assert not errors, errors
        finally:
            browser.close()
    print(json.dumps(dict(status='pass', **report, narrow_enlarged_samples=samples,
                          method='offline Chromium; committed and fallback fonts; no remote requests'), indent=2))


if __name__ == '__main__':
    main()
