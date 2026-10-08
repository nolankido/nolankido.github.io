"""Browser regressions. Offline rendering with mocked services; no network or live messages.
Install playwright and its Chromium browser, then run python _tests/browser.py.
Set CHROMIUM_PATH to use an existing browser. SCREENSHOT_DIR optionally saves review images.
"""
import base64
import re
import json
import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / '_scripts'))
import build
STUB = """window.turnstile = {
 render(el, options) { window.challengeOptions = options; return 'test-widget'; },
 reset() { window.resetCount = (window.resetCount || 0) + 1; },
 remove() { window.removed = true; }
};"""

def html_for(route):
    relative = route.lstrip('/')
    path = ROOT / (relative + 'index.html' if route.endswith('/') else relative)
    content = path.read_text(encoding='utf-8')
    content = re.sub(r'<link rel="stylesheet"[^>]*>', '', content)
    content = re.sub(r'<script src="/assets/contact.js[^>]*></script>', '', content)
    css = (ROOT / 'styles.css').read_text() + '\n' + (ROOT / 'assets/site.css').read_text() + '\n' + (ROOT / 'assets/hubs.css').read_text()
    if route.startswith('/poker/'):
        css += '\n' + (ROOT / 'assets/poker.css').read_text()
        css += '\n' + (ROOT / 'assets/poker-reader.css').read_text()
    # This harness strips stylesheet links, so include the page-scoped sheet too.
    if route == '/poker/tournament-checklists/':
        css += '\n' + (ROOT / 'assets/poker-fieldguide.css').read_text()
    content = content.replace('</head>', '<style>' + css + '</style></head>')
    for route_name in ['favicon.svg', 'card/qr.svg']:
        data = base64.b64encode((ROOT / route_name).read_bytes()).decode()
        content = content.replace('/' + route_name, 'data:image/svg+xml;base64,' + data)
    return content

class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        options = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'):
            options['executable_path'] = os.environ['CHROMIUM_PATH']
        cls.browser = cls.pw.chromium.launch(**options)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context()
        self.context.route('**/*', lambda route: route.abort())
        self.page = None
        self.service = 200
        self.block_challenge = False
        self.errors = []

    @property
    def posts(self):
        return self.page.evaluate('window.testPosts || []')

    def render(self, route, width=1280):
        if self.page: self.page.close()
        self.page = self.context.new_page()
        self.page.set_viewport_size({'width': width, 'height': 900})
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.set_content(html_for(route))
        if route == '/contact/':
            self.page.evaluate("""config => {
              window.testPosts = [];
              window.testService = config.service;
              window.blockChallenge = config.block;
              const stub = () => { window.turnstile = {
                render(el, options) { window.challengeOptions = options; return 'test-widget'; },
                reset() { window.resetCount = (window.resetCount || 0) + 1; },
                remove() { window.removed = true; }
              }; };
              if (!window.blockChallenge) stub();
              const append = document.head.appendChild.bind(document.head);
              document.head.appendChild = node => {
                if (node.tagName === 'SCRIPT' && node.src.startsWith('https://challenges.cloudflare.com/')) {
                  queueMicrotask(() => {
                    if (window.blockChallenge) node.onerror();
                    else { stub(); node.onload(); }
                  });
                  return node;
                }
                return append(node);
              };
              window.fetch = (url, options) => {
                if (url !== 'https://submit-form.com/uPlTgRTAR') throw new Error('Unexpected destination');
                window.testPosts.push(JSON.parse(options.body));
                if (window.testService === 'network') return Promise.reject(new TypeError('Network error'));
                if (window.testService === 'hang') return new Promise((resolve, reject) => {
                  options.signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
                });
                return Promise.resolve({ok: window.testService >= 200 && window.testService < 300, status: window.testService});
              };
            }""", {'service': self.service, 'block': self.block_challenge})
            self.page.add_script_tag(content=(ROOT / 'assets/contact.js').read_text())

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def contact(self):
        self.render('/contact/')
        expect(self.page.locator('#contact-fields')).to_be_enabled()
        if not self.block_challenge:
            self.page.wait_for_function('window.challengeOptions !== undefined')

    def fill(self):
        self.page.locator('#contact-name').fill('Example Visitor')
        self.page.locator('#contact-email').fill('visitor@example.com')
        self.page.locator('#contact-reason').select_option(label='Other')
        self.page.locator('#contact-message').fill('An illustrative test message, never sent to a real service.')

    def verify(self):
        self.page.evaluate("window.challengeOptions.callback('test-token')")

    def test_missing_token_retry_then_success(self):
        self.contact(); self.fill()
        expect(self.page.locator('#form-success')).to_be_hidden()
        self.page.locator('#contact-submit').click()
        expect(self.page.locator('#form-error')).to_be_visible()
        expect(self.page.locator('#contact-submit')).to_be_enabled()
        self.assertEqual(len(self.posts), 0)
        self.verify(); self.page.locator('#contact-submit').click()
        expect(self.page.locator('#form-success')).to_be_visible()
        expect(self.page.locator('#contact-form')).to_be_hidden()
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'form-success')
        self.assertEqual(len(self.posts), 1)
        self.assertEqual(self.posts[0]['cf-turnstile-response'], 'test-token')
        self.assertEqual(set(self.posts[0]), {'name', 'email', 'reason', 'context', 'message', 'cf-turnstile-response', '_email'})

    def test_required_and_whitespace_validation(self):
        self.contact(); self.verify()
        self.page.locator('#contact-submit').click()
        self.assertEqual(len(self.posts), 0)
        self.fill(); self.page.locator('#contact-name').fill('   ')
        self.page.locator('#contact-submit').click()
        self.assertEqual(len(self.posts), 0)
        expect(self.page.locator('#contact-submit')).to_be_enabled()
        self.page.locator('#contact-name').fill('Visitor')
        self.page.locator('#contact-submit').click()
        expect(self.page.locator('#form-success')).to_be_visible()

    def test_expired_verification(self):
        self.contact(); self.fill(); self.verify()
        self.page.evaluate("window.challengeOptions['expired-callback']()")
        self.page.locator('#contact-submit').click()
        expect(self.page.locator('#contact-submit')).to_be_enabled()
        self.assertEqual(self.posts, [])
        self.page.locator('#verification-retry').click()
        self.assertEqual(self.page.evaluate('window.resetCount'), 1)
        self.verify(); self.page.locator('#contact-submit').click()
        expect(self.page.locator('#form-success')).to_be_visible()

    def test_stale_token_before_submission(self):
        self.contact(); self.fill(); self.verify()
        self.page.evaluate('performance.now = () => 999999999')
        self.page.locator('#contact-submit').click()
        expect(self.page.locator('#form-error')).to_be_visible()
        expect(self.page.locator('#contact-submit')).to_be_enabled()
        self.assertEqual(self.posts, [])
        self.assertEqual(self.page.evaluate('window.resetCount'), 1)

    def test_service_errors_preserve_message(self):
        for status in [400, 429, 500]:
            with self.subTest(status=status):
                self.service = status
                self.contact(); self.fill(); self.verify()
                self.page.locator('#contact-submit').click()
                expect(self.page.locator('#form-error')).to_be_visible()
                expect(self.page.locator('#contact-submit')).to_be_enabled()
                expect(self.page.locator('#form-success')).to_be_hidden()
                expect(self.page.locator('#contact-message')).to_have_value('An illustrative test message, never sent to a real service.')
                before = len(self.posts)
                self.page.locator('#contact-submit').click()
                self.assertEqual(len(self.posts), before)

    def test_network_error_and_timeout(self):
        for state in ['network', 'hang']:
            with self.subTest(state=state):
                self.service = state
                self.contact(); self.fill(); self.verify()
                if state == 'hang':
                    self.page.evaluate('''const original = window.setTimeout; window.setTimeout = (fn, ms, ...args) => original(fn, ms === 15000 ? 100 : ms, ...args)''')
                self.page.locator('#contact-submit').click()
                expect(self.page.locator('#form-error')).to_contain_text('could not confirm')
                expect(self.page.locator('#contact-submit')).to_be_enabled()
                expect(self.page.locator('#form-success')).to_be_hidden()

    def test_general_hello_needs_no_topic_or_context(self):
        self.contact(); self.verify()
        self.page.locator('#contact-name').fill('Example Visitor')
        self.page.locator('#contact-email').fill('visitor@example.com')
        self.page.locator('#contact-message').fill('A simple hello, used only in a mocked test.')
        self.page.locator('#contact-submit').click()
        expect(self.page.locator('#form-success')).to_be_visible()
        self.assertEqual(len(self.posts), 1)
        self.assertEqual(self.posts[0]['reason'], '')
        self.assertEqual(self.posts[0]['context'], '')

    def test_duplicate_submit_prevention(self):
        self.service = 'hang'
        self.contact(); self.fill(); self.verify()
        self.page.evaluate("document.getElementById('contact-form').requestSubmit(); document.getElementById('contact-form').requestSubmit();")
        expect(self.page.locator('#contact-submit')).to_be_disabled()
        self.page.wait_for_timeout(100)
        self.assertEqual(len(self.posts), 1)

    def test_verification_load_failure_can_retry(self):
        self.block_challenge = True
        self.contact(); self.fill()
        expect(self.page.locator('#verification-retry')).to_be_visible()
        self.page.locator('#contact-submit').click()
        expect(self.page.locator('#contact-submit')).to_be_enabled()
        self.block_challenge = False
        self.page.evaluate('window.blockChallenge = false')
        self.page.locator('#verification-retry').click()
        self.page.wait_for_function('window.challengeOptions !== undefined')
        self.verify(); self.page.locator('#contact-submit').click()
        expect(self.page.locator('#form-success')).to_be_visible()

    def test_honeypot_and_challenge_error(self):
        self.contact(); self.fill(); self.verify()
        self.page.evaluate("window.challengeOptions['error-callback']()")
        expect(self.page.locator('#verification-retry')).to_be_visible()
        self.verify()
        self.page.locator('input[name="_honeypot"]').evaluate('(el) => el.checked = true')
        self.page.locator('#contact-submit').click()
        expect(self.page.locator('#form-error')).to_be_visible()
        self.assertEqual(self.posts, [])

    def test_no_javascript_content_and_form_explanation(self):
        context = self.browser.new_context(java_script_enabled=False)
        context.route('**/*', lambda r: r.abort())
        page = context.new_page()
        page.set_content(html_for('/contact/'))
        expect(page.locator('noscript p')).to_be_visible()
        self.assertIn('This form needs JavaScript', page.locator('noscript').text_content())
        expect(page.locator('#contact-submit')).to_be_disabled()
        expect(page.locator('#contact-name')).to_be_disabled()
        expect(page.locator('#form-success')).to_be_hidden()
        page.set_content(html_for('/notes/'))
        self.assertEqual(page.locator('.note-entry').count(), sum(bool(p.get('note')) for p in build.public_pages()))
        context.close()

    def test_mobile_tablet_desktop_layout_and_keyboard(self):
        pages = build.public_pages()
        for width in [320, 390, 768, 1024, 1440]:
            for p in pages:
                with self.subTest(width=width, page=p['path']):
                    self.render(p['path'], width)
                    self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), width)
                    expect(self.page.locator('h1')).to_be_visible()
                    if width == 390 and p['id'] in ['home', 'contact', 'trustworthy-tools'] and os.environ.get('SCREENSHOT_DIR'):
                        out = Path(os.environ['SCREENSHOT_DIR']); out.mkdir(parents=True, exist_ok=True)
                        self.page.screenshot(path=str(out / (p['id'] + '-mobile.png')), full_page=True)
        self.render('/', 1440)
        self.page.keyboard.press('Tab'); self.page.keyboard.press('Enter')
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'main')
        self.page.emulate_media(reduced_motion='reduce')
        self.assertEqual(self.page.evaluate('getComputedStyle(document.documentElement).scrollBehavior'), 'auto')
        if os.environ.get('SCREENSHOT_DIR'):
            self.page.screenshot(path=str(Path(os.environ['SCREENSHOT_DIR']) / 'home-desktop.png'), full_page=True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
