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
from html.parser import HTMLParser
from urllib.parse import urlsplit
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
    # Mirror the generated page rather than a stale, handwritten CSS list.
    # External fonts remain blocked; only checked-out local sheets are inlined.
    class Stylesheets(HTMLParser):
        def __init__(self):
            super().__init__()
            self.hrefs = []
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'link' and 'stylesheet' in attrs.get('rel', '').split():
                self.hrefs.append(attrs.get('href', ''))
    links = Stylesheets()
    links.feed(content)
    sheets = []
    for href in links.hrefs:
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc:
            continue
        sheet = (ROOT / parsed.path.lstrip('/')).resolve()
        if not parsed.path.startswith('/') or not sheet.is_relative_to(ROOT.resolve()) or sheet.suffix != '.css':
            raise ValueError('Unexpected local stylesheet: ' + href)
        sheets.append(sheet.read_text(encoding='utf-8'))
    if not sheets:
        raise ValueError('Generated page has no local stylesheets: ' + route)
    content = re.sub(r'<link rel="stylesheet"[^>]*>', '', content)
    content = re.sub(r'<script src="/assets/contact.js[^>]*></script>', '', content)
    css = '\n'.join(sheets)
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
        if route in ('/contact/', '/poker/school/'):
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
            script = 'assets/poker-school-interest.js' if route == '/poker/school/' else 'assets/contact.js'
            self.page.add_script_tag(content=(ROOT / script).read_text())

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

    def test_poker_school_requires_explicit_consent(self):
        self.render('/poker/school/')
        expect(self.page.locator('#contact-fields')).to_be_enabled()
        self.page.wait_for_function('window.challengeOptions !== undefined')
        self.page.locator('#interest-email').fill('visitor@example.com')
        self.page.evaluate("window.challengeOptions.callback('test-token')")
        self.page.locator('#contact-submit').click()
        self.assertEqual(self.posts, [])
        expect(self.page.locator('#form-success')).to_be_hidden()
        self.page.locator('#interest-consent').check()
        self.page.locator('#interest-goal').select_option('tournaments')
        self.page.locator('#contact-submit').click()
        expect(self.page.locator('#form-success')).to_be_visible()
        self.assertEqual(len(self.posts), 1)
        self.assertEqual(self.posts[0]['interest_action'], 'register')
        self.assertEqual(self.posts[0]['interest_goal'], 'tournaments')
        self.assertEqual(self.posts[0]['consent'], 'explicit opt-in checked')
        self.assertEqual(self.posts[0]['email'], 'visitor@example.com')
        self.assertNotIn('visitor@example.com', self.page.url)

    def test_poker_school_removal_does_not_require_opt_in(self):
        self.render('/poker/school/', width=390)
        self.page.wait_for_function('window.challengeOptions !== undefined')
        self.page.locator('#interest-action').select_option('remove')
        expect(self.page.locator('#interest-consent-group')).to_be_hidden()
        expect(self.page.locator('#interest-goal-group')).to_be_hidden()
        self.page.locator('#interest-email').fill('visitor@example.com')
        self.page.evaluate("window.challengeOptions.callback('test-token')")
        self.page.locator('#contact-submit').click()
        expect(self.page.locator('#form-success')).to_be_visible()
        self.assertEqual(len(self.posts), 1)
        self.assertEqual(self.posts[0]['interest_action'], 'remove')
        self.assertEqual(self.posts[0]['interest_goal'], '')
        self.assertEqual(self.posts[0]['consent'], 'removal request')
        self.assertIn('stop sending', self.posts[0]['message'])

    def test_poker_school_without_scripts_remains_readable(self):
        context = self.browser.new_context(java_script_enabled=False)
        context.route('**/*', lambda r: r.abort())
        page = context.new_page()
        try:
            page.set_content(html_for('/poker/school/'))
            self.assertIn('The free course stays free', page.locator('body').inner_text())
            expect(page.locator('#contact-submit')).to_be_disabled()
            expect(page.locator('noscript')).to_be_visible()
            self.assertGreaterEqual(page.locator('a[href="/poker/free-poker-learning-path/"]').count(), 1)
        finally:
            context.close()

    def school_request(self, action='register'):
        self.render('/poker/school/', width=390)
        self.page.wait_for_function('window.challengeOptions !== undefined')
        self.page.locator('#interest-email').fill('visitor@example.com')
        self.page.locator('#interest-action').select_option(action)
        if action == 'register':
            self.page.locator('#interest-goal').select_option('tournaments')
            self.page.locator('#interest-consent').check()

    def test_poker_school_recovery_names_the_actual_request_button(self):
        for action, label in [('register', 'Request course emails'), ('remove', 'Request removal')]:
            with self.subTest(action=action):
                self.school_request(action)
                self.page.locator('#contact-submit').click()
                expect(self.page.locator('#form-error')).to_contain_text(label)
                self.assertNotIn('Send message', self.page.locator('#form-error').inner_text())
                self.assertEqual(self.posts, [])
                self.verify()
                self.page.evaluate("window.challengeOptions['expired-callback']()")
                self.page.locator('#contact-submit').click()
                expect(self.page.locator('#form-error')).to_contain_text(label)
                self.assertEqual(self.posts, [])

    def test_poker_school_failures_preserve_fields_without_claiming_success(self):
        for state in [400, 429, 500, 'network', 'hang']:
            with self.subTest(state=state):
                self.service = state
                self.school_request()
                self.verify()
                if state == 'hang':
                    self.page.evaluate("const original = window.setTimeout; window.setTimeout = (fn, ms, ...args) => original(fn, ms === 15000 ? 100 : ms, ...args)")
                self.page.locator('#contact-submit').click()
                expect(self.page.locator('#form-error')).to_be_visible()
                expect(self.page.locator('#form-error')).to_contain_text('email address and selections')
                expect(self.page.locator('#interest-email')).to_have_value('visitor@example.com')
                expect(self.page.locator('#interest-goal')).to_have_value('tournaments')
                expect(self.page.locator('#interest-consent')).to_be_checked()
                expect(self.page.locator('#contact-submit')).to_be_enabled()
                expect(self.page.locator('#form-success')).to_be_hidden()
                before = len(self.posts)
                self.page.locator('#contact-submit').click()
                self.assertEqual(len(self.posts), before)

    def test_poker_school_switching_back_to_register_requires_new_consent(self):
        self.school_request()
        self.page.locator('#interest-action').select_option('remove')
        self.page.locator('#interest-action').select_option('register')
        expect(self.page.locator('#interest-consent')).not_to_be_checked()
        self.verify()
        self.page.locator('#contact-submit').click()
        self.assertEqual(self.posts, [])
        self.page.locator('#interest-consent').check()
        self.page.locator('#contact-submit').click()
        expect(self.page.locator('#form-success')).to_be_visible()
        expect(self.page.locator('#form-success')).to_contain_text('not confirmation of addition')

    def test_poker_school_duplicate_submit_is_blocked(self):
        self.service = 'hang'
        self.school_request()
        self.verify()
        self.page.evaluate("const form = document.getElementById('poker-interest-form'); form.requestSubmit(); form.requestSubmit();")
        expect(self.page.locator('#contact-submit')).to_be_disabled()
        expect(self.page.locator('#interest-action')).to_be_disabled()
        self.assertEqual(len(self.posts), 1)
        self.assertEqual(self.posts[0]['interest_goal'], 'tournaments')
        self.assertEqual(self.posts[0]['consent'], 'explicit opt-in checked')

    def test_poker_school_accessibility_and_enlarged_text(self):
        axe_path = os.environ.get('AXE_PATH')
        if not axe_path or not Path(axe_path).is_file():
            self.skipTest('Set AXE_PATH to the pinned axe-core used by Site checks')
        for action in ['register', 'remove']:
            with self.subTest(action=action):
                self.school_request(action)
                self.page.add_script_tag(path=axe_path)
                result = self.page.evaluate("async () => await axe.run(document, {runOnly: ['wcag2a', 'wcag2aa', 'wcag21aa']})")
                self.assertEqual(result['violations'], [])
                self.page.locator('#interest-email').focus()
                self.assertEqual(self.page.evaluate('document.activeElement.id'), 'interest-email')
                self.page.set_viewport_size({'width': 320, 'height': 900})
                self.page.add_style_tag(content='html { font-size: 200% !important; }')
                self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), 320)
                self.page.emulate_media(media='print')
                expect(self.page.locator('#poker-interest-form')).to_be_hidden()
                expect(self.page.locator('#school-plan-title')).to_be_visible()
                self.page.emulate_media(media='screen')

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
        notes = [p['path'] for p in build.public_pages() if p.get('note')]
        original_links = page.locator('#general-notes .note-entry h3 a')
        self.assertEqual(sorted(link.get_attribute('href') for link in original_links.all()), sorted(notes))
        config = json.loads((ROOT / '_source/identity.json').read_text(encoding='utf-8'))
        self.assertEqual(page.locator('.writing-route').count(), len(config['reading_routes']))
        # Curated readings remain in their original order. Technology now also
        # publishes its recorded cases here, including with site scripts disabled.
        # Derive the expected inventory from the manifest, not the renderer.
        cases = sorted((p for p in build.public_pages()
                        if p.get('section') == 'technology' and (p.get('evidence_article') or p.get('worked_guide'))),
                       key=lambda p: (p['date'], p['path']), reverse=True)
        case_paths = [p['path'] for p in cases]
        for route in config['reading_routes']:
            section = page.locator('.writing-route#' + route['id'])
            expect(section).to_be_visible()
            expected = list(route['paths']) + (case_paths if route['id'] == 'technology' else [])
            self.assertEqual([link.get_attribute('href') for link in section.locator('.note-entry h3 a').all()], expected)
        self.assertEqual(page.locator('.note-entry').count(),
                         len(notes) + sum(len(route['paths']) for route in config['reading_routes']) + len(cases))
        context.close()

    def test_mobile_tablet_desktop_layout_and_keyboard(self):
        pages = build.public_pages()
        for width in [320, 390, 768, 1024, 1440]:
            for p in pages:
                with self.subTest(width=width, page=p['path']):
                    self.render(p['path'], width)
                    self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), width)
                    expect(self.page.locator('h1')).to_be_visible()
                    if width == 390 and p['id'] in ['home', 'contact', 'trustworthy-tools', 'poker-school'] and os.environ.get('SCREENSHOT_DIR'):
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
