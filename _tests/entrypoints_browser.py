"""Actual static entry-point journeys. No live forms, external traffic, or storage."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port)
config = json.loads((ROOT / '_source/entrypoints.json').read_text())
errors, missing, results = [], [], []
try:
    with sync_playwright() as pw:
        options = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'): options['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**options)
        for javascript in [True, False]:
            context = browser.new_context(java_script_enabled=javascript, accept_downloads=True)
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            page = context.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('response', lambda r: missing.append(r.url) if r.status >= 400 and urlsplit(r.url).hostname == '127.0.0.1' else None)
            for group in config['interests']:
                for path in group['paths']:
                    page.goto(base + '/start-here/')
                    link = page.locator('#start-' + group['id'] + ' a[href="' + path + '"]')
                    link.focus(); page.keyboard.press('Enter')
                    expect(page).to_have_url(base + path)
            for group in config['resources']:
                for item in group['links']:
                    page.goto(base + '/resources/')
                    link = page.locator('#resources-' + group['id'] + ' a[href="' + item['path'] + '"]')
                    link.focus(); page.keyboard.press('Enter')
                    expect(page).to_have_url(base + item['path'])
            for slug, choices in config['next_reading'].items():
                for choice in choices:
                    page.goto(base + '/notes/' + slug + '/')
                    link = page.locator('.reader-next a[href="' + choice['path'] + '"]')
                    link.focus(); page.keyboard.press('Enter')
                    expect(page).to_have_url(base + choice['path'])
            task_routes = 0
            role_routes = 0
            quick_downloads = 0
            tool_routes = 0
            for target in ['/technology/task-brief/', '/technology/check-ai-answers/',
                           '/living-well/weekly-reset/', '/poker/first-live-tournament/']:
                page.goto(base + '/start-here/')
                expect(page.locator('.task-route-list > li')).to_have_count(4)
                link = page.locator('.task-route-list a[href="' + target + '"]')
                expect(link).to_be_visible()
                link.focus(); page.keyboard.press('Enter')
                expect(page).to_have_url(base + target)
                expect(page.locator('h1')).to_be_visible()
                task_routes += 1
            for parent, selector, target in [
                ('/find/', '.section-deck a[href="/start-here/#start-tasks-title"]', '/start-here/#start-tasks-title'),
                ('/find/', '.section-deck a[href="/resources/"]', '/resources/'),
                ('/resources/', 'section[aria-labelledby="resources-entry-title"] a[href="/start-here/#start-tasks-title"]', '/start-here/#start-tasks-title'),
            ]:
                page.goto(base + parent)
                link = page.locator(selector)
                expect(link).to_be_visible()
                link.focus(); page.keyboard.press('Enter')
                expect(page).to_have_url(base + target)
                if '#' in target:
                    expect(page.locator('#' + target.split('#')[1])).to_be_visible()
                role_routes += 1
            for target in ['/downloads/ai-task-brief.txt', '/downloads/ai-answer-review.txt',
                           '/downloads/living-well-weekly-reset.md']:
                page.goto(base + '/resources/')
                link = page.locator('section[aria-labelledby="resources-entry-title"] a[download][href="' + target + '"]')
                expect(link).to_be_visible()
                link.focus()
                with page.expect_download() as download:
                    page.keyboard.press('Enter')
                assert download.value.suggested_filename == Path(target).name
                assert Path(download.value.path()).read_bytes() == (ROOT / target.lstrip('/')).read_bytes()
                quick_downloads += 1
            for target in ['/technology/ai-time-savings/', '/poker/hand-rankings/']:
                page.goto(base + '/resources/')
                link = page.locator('section[aria-labelledby="resources-entry-title"] a[href="' + target + '"]')
                expect(link).to_be_visible()
                link.focus(); page.keyboard.press('Enter')
                expect(page).to_have_url(base + target)
                expect(page.locator('h1')).to_be_visible()
                tool_routes += 1
            page.goto(base + '/resources/')
            page.get_by_role('link', name='Thinking worksheets', exact=True).click()
            expect(page).to_have_url(base + '/resources/#thinking-worksheets')
            for slug in ['decision-record', 'tool-trust-check', 'learning-loop']:
                with page.expect_download() as download:
                    page.locator('a[href="/downloads/' + slug + '.md"]').click()
                assert Path(download.value.path()).read_bytes() == (ROOT / 'downloads' / (slug + '.md')).read_bytes()
            study_interest_cases = 0
            # Public invitation is native and available without scripts.
            # Only open the existing form; do not send a test submission.
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width':width,'height':900})
                page.goto(base + '/start-here/')
                invitation = page.locator('#study-interest')
                expect(invitation).to_be_visible()
                expect(invitation.locator('h3#study-interest-title')).to_be_visible()
                link = invitation.locator('a[href="/contact/#study-inquiry"]')
                expect(link).to_be_visible()
                link.focus()
                expect(link).to_be_focused()
                page.keyboard.press('Enter')
                expect(page).to_have_url(base + '/contact/#study-inquiry')
                form = page.locator('#contact-form')
                expect(form).to_be_visible()
                if javascript:
                    expect(page.locator('#contact-context')).to_have_value('Website usability study')
                    expect(page.locator('#study-inquiry')).to_be_visible()
                    expect(page.locator('#contact-message')).to_have_value('')
                else:
                    expect(page.locator('#contact-context')).to_have_value('')
                    expect(page.locator('#study-inquiry')).to_be_hidden()
                    expect(page.locator('#contact-fields')).to_be_disabled()
                expect(form.locator('input[name="name"][required]')).to_have_count(1)
                expect(form.locator('input[name="email"][required]')).to_have_count(1)
                expect(form.locator('textarea[name="message"][required]')).to_have_count(1)
                expect(page.locator('#form-success')).to_be_hidden()
                assert page.evaluate('localStorage.length + sessionStorage.length') == 0
                assert context.cookies() == []
                assert page.evaluate('document.documentElement.scrollWidth') <= width, ('study-interest',width,javascript)
                study_interest_cases += 1
            results.append({'javascript': javascript, 'keyboard_routes': 28, 'downloads': 3, 'task_routes': task_routes, 'role_routes': role_routes, 'quick_downloads': quick_downloads, 'tool_routes': tool_routes, 'study_interest_cases': study_interest_cases})
            context.close()
        context = browser.new_context()
        context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
        page = context.new_page()
        for width in [320, 390, 768, 1024, 1440]:
            page.set_viewport_size({'width':width, 'height':1000})
            for path in ['/start-here/', '/resources/'] + ['/notes/' + slug + '/' for slug in config['next_reading']]:
                page.goto(base + path)
                expect(page.locator('h1')).to_be_visible()
                assert page.evaluate('document.documentElement.scrollWidth') <= width, (path,width)
                for link in page.locator('.entry-links a, .reader-next a').all():
                    expect(link).to_be_visible()
                if width in [390,1440] and os.environ.get('SCREENSHOT_DIR'):
                    out = Path(os.environ['SCREENSHOT_DIR']); out.mkdir(exist_ok=True,parents=True)
                    page.screenshot(path=str(out / ('entry-' + path.strip('/').replace('/','-') + '-' + str(width) + '.png')),full_page=True)
                if os.environ.get('AXE_PATH') and width in [390,1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    audit=page.evaluate("async () => {const r = await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}); return {violations:r.violations.map(x=>({id:x.id,nodes:x.nodes.length})),incomplete:r.incomplete.map(x=>x.id)}}")
                    assert not audit['violations'],(path,width,audit['violations'])
                    results.append({'path':path,'width':width,'accessibility':audit})
                spacing = page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                assert page.evaluate('document.documentElement.scrollWidth') <= width, ('text-spacing',path,width)
                spacing.evaluate('(node)=>node.remove()')
        context.close(); browser.close()
    assert not errors, errors
    assert not missing, missing
    print(json.dumps({'result':'pass','navigation':results[:2],'viewport_checks':40,'text_spacing_checks':40,'accessibility_checks':len(results)-2,'details':results[2:]},indent=2))
finally:
    server.shutdown(); server.server_close()
