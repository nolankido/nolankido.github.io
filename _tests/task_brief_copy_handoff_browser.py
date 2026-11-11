"""Offline Chromium regression for a complete and partial native Copy/Paste.

Run explicitly with ``python _tests/task_brief_copy_handoff_browser.py`` or
through ``python _scripts/local_release_checks.py --browser``. The test uses a
fresh, headless browser context and invented task text. No site requests,
external destinations, browser profile, or personal clipboard data are used.
"""

import json
import os
from pathlib import Path
import re

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'technology/task-brief/index.html'
SCRIPT = ROOT / 'assets/task-brief.js'


def offline_html():
    """Keep the committed form and accessibility markup, omit remote assets."""
    html = HTML.read_text(encoding='utf-8')
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.I | re.S)
    html = re.sub(r'<link\b[^>]*>', '', html, flags=re.I)
    return html


def selection(textarea):
    return textarea.evaluate('''node => ({
      start: node.selectionStart,
      end: node.selectionEnd,
      length: node.value.length,
    })''')


def main():
    observed = []
    outbound = []
    with sync_playwright() as pw:
        options = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'):
            options['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**options)
        context = browser.new_context()
        def deny_request(route):
            outbound.append(route.request.url)
            route.abort()

        context.route('**/*', deny_request)
        try:
            page = context.new_page()
            page.set_content(offline_html(), wait_until='domcontentloaded')
            page.add_script_tag(content=SCRIPT.read_text(encoding='utf-8'))
            for field, value in {
                'goal': 'Summarize a fictional planning meeting',
                'materials': 'Invented notes: actions A, B, and C',
                'output': 'A short checklist with a clear stopping point',
                'review': 'Compare the checklist to the invented notes',
                'limits': 'No real names, addresses or client records',
            }.items():
                page.locator('#brief-' + field).fill(value)
            page.locator('#brief-build').click()
            textarea = page.locator('#brief-text')
            cue = page.locator('#brief-selection-cue')
            status = page.locator('#brief-copy-status')
            complete = textarea.input_value()
            assert complete.startswith('PURPOSE\nSummarize a fictional')

            # A real browser-native Ctrl+C follows the product's Select button.
            page.locator('#brief-select').click()
            assert selection(textarea) == {'start': 0, 'end': len(complete), 'length': len(complete)}
            expect(textarea).to_have_attribute('aria-describedby', 'brief-selection-cue brief-text-help')
            expect(status).to_have_attribute('aria-live', 'polite')
            expect(cue).to_contain_text('Selected, not copied')
            textarea.press('ControlOrMeta+C')
            expect(cue).to_contain_text('Copy command detected')
            expect(status).to_contain_text('cannot confirm clipboard contents')
            observed.append('full-selection native Copy status')

            # Paste into another *local in-memory tab* in the same disposable
            # context. This checks the destination, not the page's status text.
            destination = context.new_page()
            destination.set_content('<label for="pasted">Disposable paste target</label>'
                                    '<textarea id="pasted"></textarea>')
            pasted = destination.locator('#pasted')
            pasted.click()
            pasted.press('ControlOrMeta+V')
            assert pasted.input_value() == complete, 'Native clipboard lost text'
            observed.append('complete native paste matches all characters')

            # Use real keyboard selection movement. A first-line selection
            # must warn before and after a native Copy, and its destination
            # must not silently contain the entire brief.
            page.bring_to_front()
            page.locator('#brief-select').click()
            textarea.press('Control+Home')
            textarea.press('Shift+End')
            first_warning = status.inner_text()
            textarea.press('Shift+Left')
            assert status.inner_text() == first_warning, 'Repeated live-status warning'
            partial = selection(textarea)
            assert partial['start'] == 0 and 0 < partial['end'] < len(complete), partial
            expect(cue).to_contain_text('Full brief no longer selected')
            expect(status).to_contain_text('complete brief is no longer selected')
            textarea.press('ControlOrMeta+C')
            expect(status).to_contain_text('Copy command detected with only part')
            destination.bring_to_front()
            pasted.fill('')
            pasted.press('ControlOrMeta+V')
            assert pasted.input_value() == complete[:partial['end']], 'Partial copy boundary mismatch'
            observed.append('partial native paste and warning')

            # Ctrl+A repairs the range without claiming clipboard success.
            page.bring_to_front()
            textarea.press('ControlOrMeta+A')
            assert selection(textarea) == {'start': 0, 'end': len(complete), 'length': len(complete)}
            expect(cue).to_contain_text('Selected, not copied')
            expect(status).to_contain_text('Complete text selected, not copied')
            textarea.press('ControlOrMeta+C')
            destination.bring_to_front()
            pasted.fill('')
            pasted.press('ControlOrMeta+V')
            assert pasted.input_value() == complete
            observed.append('keyboard reselect restores full paste')

            # Editing an input invalidates the export and its selection cue.
            page.bring_to_front()
            page.locator('#brief-goal').fill('A revised fictional goal')
            expect(page.locator('#brief-result')).to_be_hidden()
            expect(cue).to_be_hidden()
            expect(status).to_have_text('')
            expect(textarea).to_have_attribute('aria-describedby', 'brief-text-help')
            observed.append('stale result and cue cleared')
            assert outbound == [], 'Unexpected external requests: ' + repr(outbound)
            assert context.cookies() == []
        finally:
            context.close()
            browser.close()
    print(json.dumps({'status': 'pass', 'checks': observed,
                      'scope': 'headless Chromium; in-memory HTML, local JS, no remote requests'}))


if __name__ == '__main__':
    main()
