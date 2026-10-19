"""Native navigation, no-script examples, reflow, accessibility and downloads."""
import json
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/technology/check-ai-answers/'


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port)
report = {'layouts': 0, 'text_spacing': 0, 'examples': 0, 'picker_journeys': 0, 'entry_journeys': 0, 'downloads': 0, 'axe': []}
errors = []
writes = []
try:
    with sync_playwright() as pw:
        opts = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'):
            opts['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**opts)
        for scripts in [True, False]:
            ctx = browser.new_context(java_script_enabled=scripts, accept_downloads=True, reduced_motion='reduce')
            def route(r):
                if r.request.method not in {'GET', 'HEAD'}:
                    writes.append(r.request.url)
                r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort()
            ctx.route('**/*', route)
            page = ctx.new_page()
            page.set_default_timeout(15000)
            page.on('pageerror', lambda e: errors.append(str(e)))
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 950})
                page.goto(base + ROUTE)
                expect(page.locator('h1')).to_be_visible()
                expect(page.locator('.review-fast-list > li')).to_have_count(4)
                expect(page.locator('#review-fast-method')).to_be_visible()
                expect(page.locator('.review-verdicts > dt')).to_have_count(3)
                expect(page.locator('main')).to_contain_text('unresolved, not contradicted')
                expect(page.locator('main')).to_contain_text('Send meetup questions to the organizer.')
                expect(page.locator('main')).to_contain_text('That summary is not faithful to its supplied source')
                assert page.evaluate('document.documentElement.scrollWidth') <= width
                links = page.locator('.review-picker a')
                expect(links).to_have_count(6)
                assert all(a.bounding_box()['height'] >= 44 for a in links.all())
                for detail in page.locator('.review-example').all():
                    expect(detail).not_to_have_attribute('open', '')
                    detail.locator('summary').focus()
                    page.keyboard.press('Enter')
                    expect(detail).to_have_attribute('open', '')
                    report['examples'] += 1
                page.locator('.review-sheet summary').focus()
                page.keyboard.press('Enter')
                assert page.locator('.review-sheet pre').text_content() == (ROOT / 'downloads/ai-answer-review.txt').read_text()
                report['layouts'] += 1
                if scripts and width in [390, 1440] and os.environ.get('SCREENSHOT_DIR'):
                    out = Path(os.environ['SCREENSHOT_DIR']); out.mkdir(parents=True, exist_ok=True)
                    page.evaluate('window.scrollTo(0,0)')
                    page.screenshot(path=str(out / f'answer-review-{width}.png'), full_page=True)
                page.evaluate('css=>{const s=document.createElement("style");s.textContent=css;document.head.appendChild(s)}', '*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                assert page.evaluate('document.documentElement.scrollWidth') <= width
                report['text_spacing'] += 1
                if scripts and width == 390 and os.environ.get('AXE_PATH'):
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    audit = page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>v.id),incomplete:r.incomplete.map(v=>v.id)}}")
                    assert not audit['violations'], audit
                    report['axe'].append(audit)
            page.goto(base + ROUTE)
            for a in page.locator('.review-picker a').all():
                target = a.get_attribute('href'); a.focus(); page.keyboard.press('Enter')
                expect(page).to_have_url(base + ROUTE + target)
                expect(page.locator(target)).to_be_visible()
                report['picker_journeys'] += 1
            for parent in ['/', '/technology/', '/resources/', '/notes/', '/find/']:
                page.goto(base + parent)
                a = page.locator('a[href="' + ROUTE + '"]').first
                # Open the native disclosure before activating its secondary link.
                if parent == '/':
                    details = page.locator('details.practical-home')
                    expect(details).not_to_have_attribute('open', '')
                    page.locator('#practical-home-title').focus()
                    page.keyboard.press('Enter')
                    expect(details).to_have_attribute('open', '')
                # The site finder intentionally keeps its native browse groups folded.
                if parent == '/find/':
                    if page.locator('#browse-technology').get_attribute('open') is None:
                        page.locator('#browse-technology summary').focus()
                        page.keyboard.press('Enter')
                expect(a).to_be_visible()
                a.focus(); expect(a).to_be_focused(); page.keyboard.press('Enter')
                expect(page).to_have_url(base + ROUTE)
                report['entry_journeys'] += 1
            for parent in [ROUTE, '/resources/']:
                page.goto(base + parent)
                with page.expect_download() as info:
                    page.locator('a[download][href="/downloads/ai-answer-review.txt"]').click()
                download = info.value
                assert download.suggested_filename == 'ai-answer-review.txt'
                assert Path(download.path()).read_bytes() == (ROOT / 'downloads/ai-answer-review.txt').read_bytes()
                report['downloads'] += 1
            ctx.close()
        browser.close()
    assert not errors, errors
    assert not writes, writes
    report['status'] = 'pass'
    print(json.dumps(report, indent=2))
finally:
    server.shutdown()
    server.server_close()
