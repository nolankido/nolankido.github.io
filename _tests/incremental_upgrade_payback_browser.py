"""Offline Chromium smoke for the public payback record and native download.

All site responses are served from committed local files. The saved files in
this test are synthetic and remain in Playwright's temporary download area.
"""
from pathlib import Path
import json
import os

from playwright.sync_api import expect, sync_playwright

from standalone_search_sections_browser import BASE, request_handler


ROUTE = '/creative/incremental-upgrade-payback/'


def check_download(page, snippets):
    with page.expect_download() as pending:
        page.locator('#payback-download').click()
    received = pending.value
    assert received.suggested_filename == 'incremental-upgrade-comparison.md'
    body = Path(received.path()).read_text(encoding='utf-8')
    for snippet in snippets:
        assert snippet in body, (snippet, body)
    return body


def main():
    metrics = {'viewport_checks': 0, 'native_downloads': 0,
               'stale_result_guards': 0, 'no_script_fallbacks': 0}
    errors = []
    with sync_playwright() as pw:
        launch = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'):
            launch['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**launch)
        try:
            for width in (320, 390, 768, 1440):
                context = browser.new_context(viewport={'width': width, 'height': 900},
                                              accept_downloads=True, reduced_motion='reduce',
                                              service_workers='block')
                context.route('**/*', request_handler())
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                requests = []
                page.on('request', lambda request: requests.append(request.url))
                page.goto(BASE + ROUTE, wait_until='load')
                expect(page.locator('#payback-form')).to_be_visible()
                expect(page.locator('#payback-fallback')).to_be_hidden()
                expect(page.locator('#payback-result')).to_be_hidden()
                page.locator('#payback-preset-20').click()
                expect(page.locator('#payback-no-buy')).to_have_text('45')
                expect(page.locator('#payback-pencil-final')).to_have_text('55')
                expect(page.locator('#payback-routine-final')).to_have_text('80')
                expect(page.locator('#payback-download')).to_be_visible()
                check_download(page, ['Starting available sparks (B): 25',
                                      'Planned taps after purchase (N): 20',
                                      '80 sparks', 'Routine minus pencil: 25 sparks'])
                metrics['native_downloads'] += 1

                page.locator('.payback-export summary').click()
                expect(page.locator('#payback-report')).to_be_visible()
                assert 'T = N + R - C = 35 seconds' in page.locator('#payback-report').input_value()
                assert page.evaluate('document.documentElement.scrollWidth') <= width + 1
                metrics['viewport_checks'] += 1

                page.locator('#payback-taps').fill('60')
                expect(page.locator('#payback-result')).to_be_hidden()
                expect(page.locator('#payback-download')).to_be_hidden()
                expect(page.locator('#payback-report')).to_have_value('')
                expect(page.locator('#payback-feedback')).to_contain_text('Inputs changed')
                metrics['stale_result_guards'] += 1
                page.locator('#payback-form button[type="submit"]').click()
                expect(page.locator('#payback-pencil-final')).to_have_text('135')
                expect(page.locator('#payback-routine-final')).to_have_text('120')
                check_download(page, ['Planned taps after purchase (N): 60',
                                      '135 sparks', 'Pencil finishes ahead of routine.'])
                metrics['native_downloads'] += 1

                page.locator('#payback-bank').fill('5')
                page.locator('#payback-form button[type="submit"]').click()
                check_download(page, ['Starting available sparks (B): 5',
                                      'Unavailable: not affordable at start',
                                      'tie threshold: not applicable'])
                metrics['native_downloads'] += 1
                assert page.evaluate('document.documentElement.scrollWidth') <= width + 1
                assert all(request.startswith(BASE) for request in requests), requests
                assert context.cookies() == []
                assert page.evaluate('localStorage.length + sessionStorage.length') == 0
                context.close()

            for width in (320, 1440):
                context = browser.new_context(viewport={'width': width, 'height': 900},
                                              java_script_enabled=False, service_workers='block')
                context.route('**/*', request_handler())
                page = context.new_page()
                page.goto(BASE + ROUTE, wait_until='load')
                expect(page.locator('#payback-form')).to_be_hidden()
                expect(page.locator('#payback-fallback')).to_be_visible()
                expect(page.locator('a[href="/downloads/incremental-upgrade-payback-worksheet.md"]')).to_be_visible()
                assert page.evaluate('document.documentElement.scrollWidth') <= width + 1
                metrics['no_script_fallbacks'] += 1
                context.close()

            assert not errors, errors
        finally:
            browser.close()
    print(json.dumps({'status': 'pass', **metrics,
                      'method': 'Offline Chromium, intercepted local assets, native Blob downloads'}, indent=2))


if __name__ == '__main__':
    main()
