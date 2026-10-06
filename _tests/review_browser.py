"""Whole-site browser audit. No external traffic or real form submissions.
AXE_PATH must identify a locally installed axe-core script. --report-only records baseline failures.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlsplit
import argparse
import json
import os
import sys
import html5lib
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / '_scripts'))
import build
WIDTHS = [320, 390, 520, 760, 768, 1024, 1440]
SPACING = '* { line-height: 1.5 !important; letter-spacing: .12em !important; word-spacing: .16em !important; } p { margin-bottom: 2em !important; }'
STUB = r'''config => {
 window.audit = {posts: [], renders: 0, options: null, oldOptions: null, status: 200, redirect: false};
 window.turnstile = {
   render(el, options) {
     audit.renders++; audit.oldOptions = audit.options; audit.options = options;
     if (config.undefinedFirst && audit.renders === 1) return undefined;
     if (config.widgetBox) { el.innerHTML = '<div title="Verification example" style="width:' + (options.size === 'compact' ? 150 : 300) + 'px;height:40px">Verification example</div>'; }
     return 'widget-' + audit.renders;
   },
   reset() { if (audit.throwReset) { audit.throwReset = false; throw new Error('stale widget'); } },
   remove() {}, ready(callback) { callback(); }
 };
 window.fetch = async (url, options) => {
   audit.posts.push(JSON.parse(options.body));
   return {ok: audit.status >= 200 && audit.status < 300, status: audit.status, redirected: audit.redirect};
 };
}'''

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args()
    axe_path = Path(os.environ['AXE_PATH'])
    assert axe_path.is_file(), 'A locally installed axe-core script is required'
    pages = build.public_pages()
    failures, notes = [], []
    def check(name, predicate):
        try:
            if not predicate():
                failures.append({'check': name})
        except Exception as exc:
            failures.append({'check': name, 'error': str(exc)[:300]})
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    base = 'http://127.0.0.1:' + str(server.server_port)
    try:
        for entry in pages:
            relative = entry['path'].lstrip('/') + ('index.html' if entry['path'].endswith('/') else '')
            parser5 = html5lib.HTMLParser(strict=False)
            parser5.parse((ROOT / relative).read_text())
            if parser5.errors:
                failures.append({'check': 'html5:' + entry['path'], 'errors': parser5.errors})
        with sync_playwright() as p:
            opts = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                opts['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = p.chromium.launch(**opts)
            context = browser.new_context(accept_downloads=True)
            context.route('**/*', lambda route: route.continue_() if urlsplit(route.request.url).hostname == '127.0.0.1' else route.abort())
            page = context.new_page()
            page.on('pageerror', lambda error: failures.append({'check': 'pageerror', 'error': str(error)}))
            for width in WIDTHS:
                page.set_viewport_size({'width': width, 'height': 900})
                for entry in pages:
                    response = page.goto(base + entry['path'])
                    check('http:' + entry['path'], lambda: response.status == 200)
                    check('layout:' + entry['path'] + ':' + str(width), lambda: page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
                    if entry['id'] == 'resources':
                        page.locator('details').evaluate_all('(nodes) => nodes.forEach(n => n.open = true)')
                    if width in [320, 1440]:
                        page.add_script_tag(path=str(axe_path))
                        results = page.evaluate('''async () => {
                          const result = await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']}});
                          return {violations: result.violations.map(v => ({id:v.id, impact:v.impact, nodes:v.nodes.map(n => ({target:n.target, failure:n.failureSummary}))})), incomplete: result.incomplete.map(v => v.id)};
                        }''')
                        if results['violations']:
                            failures.append({'check': 'axe:' + entry['path'] + ':' + str(width), 'violations': results['violations']})
                        if results['incomplete']:
                            notes.append({'page': entry['path'], 'manual_review': results['incomplete']})
                    page.add_style_tag(content=SPACING)
                    if not page.evaluate('document.documentElement.scrollWidth <= innerWidth'):
                        failures.append({'check': 'text-spacing:' + entry['path'] + ':' + str(width), 'overflow': page.evaluate('Array.from(document.querySelectorAll("body *")).filter(e => {const r=e.getBoundingClientRect(); return r.width && (r.right > innerWidth + 1 || r.left < -1) && !e.classList.contains("skip-link")}).slice(0,8).map(e=>e.tagName+"."+e.className)')})
            page.close()

            def contact(config=None):
                test = context.new_page()
                test.set_viewport_size({'width': 1440, 'height': 900})
                test.add_init_script('(' + STUB + ')(' + json.dumps(config or {}) + ')')
                test.goto(base + '/contact/')
                test.locator('#contact-name').fill('Example Visitor')
                test.locator('#contact-email').fill('visitor@example.com')
                test.locator('#contact-message').fill('Mocked review only. Never sent to the real service.')
                return test

            test = contact({'undefinedFirst': True})
            check('render-undefined-offers-retry', lambda: test.locator('#verification-retry').is_visible())
            if test.locator('#verification-retry').is_visible():
                test.locator('#verification-retry').click()
            check('render-undefined-remounts', lambda: test.evaluate('audit.renders >= 2'))
            test.close()

            test = contact()
            test.evaluate("audit.options.callback('test-token'); audit.throwReset = true; audit.options['expired-callback']()")
            test.locator('#verification-retry').click()
            check('stale-widget-reset-recovers', lambda: test.evaluate('audit.renders >= 2'))
            test.close()

            test = contact({'widgetBox': True})
            test.set_viewport_size({'width': 320, 'height': 900})
            test.wait_for_timeout(100)
            check('verification-fits-after-resize', lambda: test.evaluate('document.documentElement.scrollWidth <= innerWidth'))
            test.close()

            test = contact()
            test.evaluate("audit.options.callback('test-token'); audit.status = 500")
            test.locator('#contact-submit').click()
            test.wait_for_timeout(50)
            check('server-error-does-not-promise-nondelivery', lambda: 'could not confirm' in test.locator('#form-error').inner_text())
            check('server-error-preserves-message', lambda: test.locator('#contact-message').input_value().startswith('Mocked review'))
            test.close()

            test = contact()
            test.evaluate("audit.options.callback('test-token'); audit.redirect = true")
            test.locator('#contact-submit').click()
            test.wait_for_timeout(50)
            check('redirect-cannot-display-success', lambda: test.locator('#form-success').is_hidden())
            test.close()

            test = context.new_page()
            test.route('**/assets/contact.js*', lambda route: route.abort())
            test.goto(base + '/contact/')
            fallback = test.locator('#contact-initialization')
            check('missing-contact-script-explains-recovery', lambda: fallback.count() == 1 and fallback.is_visible())
            test.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    report = {'pages': len(pages), 'viewport_checks': len(pages) * len(WIDTHS), 'axe_checks': len(pages) * 2, 'failures': failures, 'manual_review_notes': notes}
    print('REVIEW_REPORT=' + json.dumps(report, ensure_ascii=False), flush=True)
    if os.environ.get('REVIEW_OUTPUT'):
        Path(os.environ['REVIEW_OUTPUT']).write_text(json.dumps(report, indent=2), encoding='utf-8')
    if failures and not args.report_only:
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(run())
