"""Native Weekly Reset worksheet journeys, called by the existing browser suite."""
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit
import json
import os
from playwright.sync_api import expect


def check_weekly_reset(browser, base, root, out):
    sheet = (root / 'downloads/living-well-weekly-reset.md').read_bytes()
    report = {'layouts': 0, 'text_spacing': 0, 'keyboard_toggles': 0,
              'downloads': 0, 'print_checks': 0, 'accessibility_scans': 0,
              'accessibility_incomplete': [], 'javascript_modes': [],
              'worksheet_sha256': sha256(sheet).hexdigest(), 'errors': [],
              'bad_responses': [], 'writes': [], 'violations': []}
    for javascript in (True, False):
        report['javascript_modes'].append(javascript)
        for width in (320, 390, 768, 1440):
            context = browser.new_context(java_script_enabled=javascript,
                accept_downloads=True, viewport={'width': width, 'height': 1000})
            context.route('**/*', lambda route: route.continue_()
                if urlsplit(route.request.url).hostname == '127.0.0.1' else route.abort())
            context.on('request', lambda request: report['writes'].append(request.url)
                if request.method not in {'GET', 'HEAD'} else None)
            page = context.new_page()
            page.on('pageerror', lambda error: report['errors'].append(str(error)))
            page.on('response', lambda response: report['bad_responses'].append(response.url)
                if response.status >= 400 and urlsplit(response.url).hostname == '127.0.0.1' else None)
            try:
                response = page.goto(base + '/living-well/weekly-reset/')
                assert response.status == 200
                starter = page.locator('.lw-quick-start')
                expect(starter).to_be_visible()
                expect(starter.locator('li')).to_have_count(3)
                expect(starter).to_contain_text('Fictional completed mini-note:')
                expect(starter).to_contain_text('existing privacy notice')
                expect(page.locator('form, input, textarea')).to_have_count(0)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                report['layouts'] += 1
                if javascript and width in (390, 1440):
                    page.screenshot(path=str(out / f'weekly-reset-opening-{width}.png'))
                    starter.screenshot(path=str(out / f'weekly-reset-starter-{width}.png'))
                summary = page.locator('#weekly-reset-worksheet summary')
                pre = page.locator('#weekly-reset-worksheet pre')
                expect(pre).not_to_be_visible()
                for visible in (True, False, True):
                    summary.focus()
                    expect(summary).to_be_focused()
                    page.keyboard.press('Enter')
                    if visible: expect(pre).to_be_visible()
                    else: expect(pre).not_to_be_visible()
                    report['keyboard_toggles'] += 1
                assert pre.text_content() == sheet.decode('utf-8')
                # No-script contexts do not dispatch the load event awaited
                # by add_style_tag. Insert through the test driver without
                # enabling page JavaScript, keeping both modes fully tested.
                spacing = page.evaluate_handle(
                    "css => { const style = document.createElement('style'); style.textContent = css; document.head.append(style); return style; }",
                    '* { line-height:1.5!important; letter-spacing:.12em!important; word-spacing:.16em!important; } p { margin-bottom:2em!important; }')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                report['text_spacing'] += 1
                spacing.evaluate('(node) => node.remove()')
                if javascript and width in (390, 1440) and os.environ.get('AXE_PATH'):
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    result = page.evaluate("async () => await axe.run(document.querySelector('.lw-quick-start'), {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa']}})")
                    report['accessibility_scans'] += 1
                    report['violations'].extend(result['violations'])
                    report['accessibility_incomplete'].extend({'width': width, 'id': item['id']} for item in result['incomplete'])
                page.emulate_media(media='print')
                expect(pre).to_be_visible()
                assert pre.text_content() == sheet.decode('utf-8')
                report['print_checks'] += 1
                page.emulate_media(media='screen')
                with page.expect_download() as event:
                    starter.locator('a[download]').click()
                assert event.value.suggested_filename == 'living-well-weekly-reset.md'
                assert Path(event.value.path()).read_bytes() == sheet
                report['downloads'] += 1
                starter.locator('a[href="/living-well/worksheets/#weekly-reset"]').click()
                expect(page).to_have_url(base + '/living-well/worksheets/#weekly-reset')
                section = page.locator('section').filter(has=page.locator('h2#weekly-reset'))
                expect(section).to_have_count(1)
                expect(section.locator('pre')).to_be_visible()
                assert section.locator('pre').text_content() == sheet.decode('utf-8')
                page.emulate_media(media='print')
                expect(page.locator('.lw-worksheet-intro')).not_to_be_visible()
                expect(section.locator('pre')).to_be_visible()
                report['print_checks'] += 1
                page.emulate_media(media='screen')
                with page.expect_download() as event:
                    section.locator('a[download]').click()
                assert Path(event.value.path()).read_bytes() == sheet
                report['downloads'] += 1
                assert context.cookies() == []
                assert page.evaluate('localStorage.length + sessionStorage.length') == 0
                print(json.dumps({'weekly_reset_case': {'width': width, 'javascript': javascript, 'status': 'pass'}}), flush=True)
            except Exception:
                page.screenshot(path=str(out / f'weekly-reset-failure-{width}-{javascript}.png'), full_page=True)
                raise
            finally:
                context.close()
    assert not report['errors'] and not report['bad_responses'] and not report['writes'] and not report['violations'], report
    report['status'] = 'pass'
    (out / 'weekly-reset-browser.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'weekly_reset': report}))
