"""Living Well reader paths, mobile reflow, keyboard, download and no-JS regressions."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
import sys
from playwright.sync_api import sync_playwright, expect
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import living_well as lw

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def run():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    base = 'http://127.0.0.1:' + str(server.server_port)
    errors, bad_responses, writes, violations = [], [], [], []
    out = Path(os.environ.get('SCREENSHOT_DIR', '/tmp/living-well-previews'))
    out.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as pw:
            opts = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                opts['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**opts)
            context = browser.new_context(accept_downloads=True)
            context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            context.on('request', lambda r: writes.append(r.url) if r.method not in {'GET', 'HEAD'} else None)
            page = context.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('response', lambda r: bad_responses.append(r.url) if r.status >= 400 and urlsplit(r.url).hostname == '127.0.0.1' else None)
            pages = lw.manifest(ROOT)
            for width in [320, 390, 620, 768, 1024, 1440]:
                page.set_viewport_size({'width': width, 'height': 1000})
                for entry in pages:
                    assert page.goto(base + entry['path']).status == 200
                    expect(page.locator('h1')).to_be_visible()
                    assert page.locator('h1').count() == 1
                    assert page.evaluate('document.documentElement.scrollWidth') <= width, (entry['path'], width)
                    expect(page.locator('nav[aria-label="Living Well section"]')).to_be_visible()
                    spacing = page.add_style_tag(content='* { line-height:1.5!important; letter-spacing:.12em!important; word-spacing:.16em!important; } p { margin-bottom:2em!important; }')
                    assert page.evaluate('document.documentElement.scrollWidth') <= width, ('text spacing', entry['path'])
                    spacing.evaluate('(node) => node.remove()')
                    if width == 390:
                        if os.environ.get('AXE_PATH'):
                            page.add_script_tag(path=os.environ['AXE_PATH'])
                            result = page.evaluate("async () => await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa']}})")
                            violations.extend({'path': entry['path'], 'id': v['id'], 'impact': v['impact'], 'nodes': [n['target'] for n in v['nodes']]} for v in result['violations'])
                    if width in [390, 1440] and entry['id'] in {'living-well', 'living-well-weekly-reset', 'living-well-worksheets', 'living-well-field-notes', 'living-well-topics', 'living-well-free-resources', 'living-well-spiritual-curiosity-reading-path', 'living-well-technology-that-helps-you-notice', 'living-well-meditation-without-buying-a-lifestyle', 'living-well-consciousness-which-question', 'living-well-read-a-poem-without-a-lesson', 'living-well-learning-with-ai-without-skipping-understanding', 'living-well-a-tool-you-can-put-down', 'living-well-technology-for-real-life', 'living-well-scattered-notes-to-next-step', 'living-well-shared-plan-people-can-use', 'living-well-did-the-tool-actually-help'}:
                        page.screenshot(path=str(out / (entry['id'] + '-' + str(width) + '.png')), full_page=True)
                page.goto(base + '/')
                boxes = [page.locator('.destination-' + slug).bounding_box() for slug in ['technology', 'living-well', 'poker', 'creative']]
                assert boxes[0]['y'] + boxes[0]['height'] <= boxes[1]['y']
                assert boxes[1]['y'] + boxes[1]['height'] <= boxes[2]['y']
                assert page.evaluate('document.documentElement.scrollWidth') <= width, ('home', width)
                if width in [390, 1440]:
                    page.screenshot(path=str(out / ('living-well-site-home-' + str(width) + '.png')), full_page=True)
            page.goto(base + '/')
            page.locator('.destination-living-well').focus()
            page.keyboard.press('Enter')
            expect(page).to_have_url(base + '/living-well/')
            page.locator('.lw-routes a[href="/living-well/guides/"]').click()
            page.locator('.lw-card a[href="/living-well/weekly-reset/"]').click()
            page.locator('.lw-outline summary').focus()
            page.keyboard.press('Enter')
            expect(page.locator('.lw-outline')).to_have_attribute('open', '')
            page.locator('.lw-outline a[href="#part-2"]').click()
            expect(page).to_have_url(base + '/living-well/weekly-reset/#part-2')
            page.goto(base + '/living-well/')
            page.locator('.lw-primary-links a[href="/living-well/free-resources/"]').focus()
            page.keyboard.press('Enter')
            expect(page).to_have_url(base + '/living-well/free-resources/')
            expect(page.locator('.lw-resource')).to_have_count(66)
            expect(page.locator('.lw-shelf-jumps a')).to_have_count(12)
            page.locator('.lw-shelf-jumps a[href="#shelf-world"]').focus()
            page.keyboard.press('Enter')
            expect(page).to_have_url(base + '/living-well/free-resources/#shelf-world')
            # The complete index keeps every previous anchor; fuller notes live in focused collections.
            for shelf in lw.resources.load(ROOT)['shelves']:
                page.goto(base + lw.resources.collection_route(shelf['id']))
                expect(page.locator('h1')).to_have_text(shelf['title'])
                expect(page.locator('.subsite-links a[aria-current="location"]')).to_have_attribute('href', '/living-well/free-resources/')
                expect(page.locator('.lw-breadcrumb a').last).to_have_attribute('href', '/living-well/free-resources/')
                for card in page.locator('.lw-resource').all():
                    expect(card.locator('.lw-access')).to_be_visible()
                    card.locator('summary').focus()
                    page.keyboard.press('Enter')
                    expect(card.locator('.lw-resource-notes')).to_have_attribute('open', '')
                if shelf['id'] in {'traditions', 'digital-life', 'books-creativity'}:
                    page.screenshot(path=str(out / ('living-well-collection-' + shelf['id'] + '.png')), full_page=True)
            page.goto(base + '/living-well/free-resources/#libby')
            page.locator('#libby .lw-directory-detail a').focus()
            page.keyboard.press('Enter')
            expect(page).to_have_url(base + '/living-well/free-resources/world/#libby')
            page.goto(base + '/living-well/ideas/')
            page.locator('#short-reads').scroll_into_view_if_needed()
            page.locator('a[href="/living-well/read-a-poem-without-a-lesson/"]').focus()
            page.keyboard.press('Enter')
            expect(page.locator('h1')).to_have_text('Read a poem without turning it into a lesson')
            page.locator('.lw-outline summary').click()
            page.locator('.lw-outline a[href="#sources-and-context"]').focus()
            page.keyboard.press('Enter')
            expect(page).to_have_url(base + '/living-well/read-a-poem-without-a-lesson/#sources-and-context')
            page.goto(base + '/living-well/guides/')
            page.locator('a[href="/living-well/meditation-without-buying-a-lifestyle/"]').focus()
            page.keyboard.press('Enter')
            expect(page.locator('h1')).to_have_text('Meditation without buying a lifestyle')
            expect(page.locator('.lw-source-notes')).to_be_visible()
            page.goto(base + '/living-well/')
            page.locator('#technology-in-ordinary-life').scroll_into_view_if_needed()
            page.locator('a[href="/living-well/technology-for-real-life/"]').focus()
            page.keyboard.press('Enter')
            expect(page.locator('h1')).to_have_text('Technology for real life')
            page.wait_for_load_state('load')
            utility_entries = [e for e in lw.load(ROOT) if e.get('utility')]
            for entry in utility_entries:
                page.goto(base + '/living-well/' + entry['slug'] + '/')
                expect(page.locator('.lw-utility-brief')).to_be_visible()
                expect(page.locator('.lw-utility-starter pre')).to_have_text(entry['utility']['starter'])
                page.locator('.lw-outline summary').click()
                page.locator('a[href="#plain-text-starter"]').focus()
                page.keyboard.press('Enter')
                expect(page).to_have_url(base + '/living-well/' + entry['slug'] + '/#plain-text-starter')
                page.locator('.lw-utility-starter summary').focus()
                page.keyboard.press('Enter')
                expect(page.locator('.lw-utility-starter pre')).not_to_be_visible()
                page.keyboard.press('Enter')
                expect(page.locator('.lw-utility-starter pre')).to_be_visible()
            page.goto(base + '/living-well/worksheets/')
            for slug, title, desc, guide, content in lw.SHEETS:
                section = page.locator('section').filter(has=page.locator('h2#' + slug))
                section.locator('summary').focus()
                page.keyboard.press('Enter')
                expect(section.locator('pre')).not_to_be_visible()
                page.keyboard.press('Enter')
                expect(section.locator('pre')).to_be_visible()
                assert section.locator('pre').text_content() == content
                with page.expect_download() as event:
                    section.locator('a[download]').click()
                assert Path(event.value.path()).read_bytes() == content.encode('utf-8')
            page.emulate_media(media='print')
            expect(page.locator('.lw-worksheet-intro')).not_to_be_visible()
            assert page.locator('pre').count() == 5
            for pre in page.locator('pre').all():
                expect(pre).to_be_visible()
            page.emulate_media(media='screen')
            assert page.evaluate('localStorage.length') == 0
            assert page.evaluate('sessionStorage.length') == 0
            assert context.cookies() == []
            nojs = browser.new_context(java_script_enabled=False, accept_downloads=True)
            nojs.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
            plain = nojs.new_page()
            for path in ['/living-well/', '/living-well/guides/', '/living-well/weekly-reset/', '/living-well/worksheets/', '/living-well/field-notes/', '/living-well/free-resources/', '/living-well/spiritual-curiosity-reading-path/', '/living-well/technology-that-helps-you-notice/'] + ['/living-well/' + e['slug'] + '/' for e in json.loads((ROOT / '_source/living-well/expansion.json').read_text())['entries']]:
                assert plain.goto(base + path).status == 200
                expect(plain.locator('h1')).to_be_visible()
            plain.goto(base + '/living-well/free-resources/')
            expect(plain.locator('.lw-resource')).to_have_count(66)
            plain.locator('.lw-shelf-jumps a[href="#shelf-meaning"]').click()
            expect(plain).to_have_url(base + '/living-well/free-resources/#shelf-meaning')
            # Wait for the destination document, not just the changed address.
            # Native focus brings the disclosure into view without altering its state.
            # A real pointer click, with ordinary actionability checks, still opens it.
            navigation_events = []
            def record_navigation(frame):
                if frame == plain.main_frame:
                    navigation_events.append(frame.url)
            plain.on('framenavigated', record_navigation)
            try:
                for attempt in range(3):
                    if attempt:
                        plain.goto(base + '/living-well/free-resources/#libby')
                    plain.locator('#libby .lw-directory-detail a').click()
                    plain.wait_for_url(base + '/living-well/free-resources/world/#libby', wait_until='load')
                    expect(plain.locator('h1')).to_have_text(next(s['title'] for s in lw.resources.load(ROOT)['shelves'] if s['id'] == 'world'))
                    disclosure = plain.locator('#libby summary')
                    expect(disclosure).to_have_count(1)
                    disclosure.focus()
                    expect(disclosure).to_be_focused()
                    expect(disclosure).to_be_in_viewport()
                    disclosure.click()
                    expect(plain.locator('#libby .lw-resource-notes')).to_have_attribute('open', '')
                (out / 'living-well-nojs-navigation.json').write_text(json.dumps({'attempts': 3, 'status': 'passed', 'events': navigation_events}, indent=2) + '\n')
            except Exception:
                (out / 'living-well-nojs-navigation.json').write_text(json.dumps({'status': 'failed', 'url': plain.url, 'events': navigation_events, 'summary_count': plain.locator('#libby summary').count()}, indent=2) + '\n')
                plain.screenshot(path=str(out / 'living-well-nojs-navigation-failure.png'), full_page=True)
                raise
            finally:
                plain.remove_listener('framenavigated', record_navigation)
            for shelf in lw.resources.load(ROOT)['shelves']:
                assert plain.goto(base + lw.resources.collection_route(shelf['id'])).status == 200
                expect(plain.locator('h1')).to_have_text(shelf['title'])
            plain.goto(base + '/living-well/worksheets/')
            expect(plain.locator('pre').first).to_be_visible()
            plain.locator('summary').first.click()
            expect(plain.locator('pre').first).not_to_be_visible()
            plain.locator('summary').first.click()
            expect(plain.locator('pre').first).to_be_visible()
            with plain.expect_download() as event:
                plain.locator('a[download]').first.click()
            assert event.value.suggested_filename == 'living-well-weekly-reset.md'
            for entry in utility_entries:
                plain.goto(base + '/living-well/' + entry['slug'] + '/')
                expect(plain.locator('.lw-utility-brief')).to_be_visible()
                expect(plain.locator('.lw-utility-starter pre')).to_have_text(entry['utility']['starter'])
                plain.locator('.lw-utility-starter summary').focus()
                plain.keyboard.press('Enter')
                expect(plain.locator('.lw-utility-starter pre')).not_to_be_visible()
                plain.keyboard.press('Enter')
                expect(plain.locator('.lw-utility-starter pre')).to_be_visible()
            nojs.close()
            browser.close()
        report = {'pages': len(pages), 'viewport_widths': [320, 390, 620, 768, 1024, 1440], 'axe_enabled': bool(os.environ.get('AXE_PATH')), 'violations': violations, 'javascript_errors': errors, 'failed_local_responses': bad_responses, 'write_requests': writes}
        (out / 'living-well-browser.json').write_text(json.dumps(report, indent=2) + '\n')
        assert not (errors or bad_responses or writes or violations), report
        print('PASS: ' + str(len(pages)) + ' Living Well pages at 6 widths; keyboard paths, 5 exact downloads, print, storage and no-JS checks; axe=' + str(bool(os.environ.get('AXE_PATH'))))
    finally:
        server.shutdown()
        server.server_close()

if __name__ == '__main__':
    run()
