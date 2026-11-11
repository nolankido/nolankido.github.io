"""Offline text-enlargement and keyboard-fragment check for the AI task brief.

Renders the committed page using locally injected styles. The builder script,
remote fonts, remote requests and persistent storage are not used here. A
second pass injects the existing local builder script to exercise its preview.
"""

import json
import os
from pathlib import Path
import re

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / 'technology/task-brief/index.html'
STYLES = re.compile(r'<link rel="stylesheet" href="(/assets/[^\"]+)"')
LINKS = re.compile(r'<link\b[^>]*>')
SCRIPTS = re.compile(r'<script\b[^>]*\bsrc="[^"]+"[^>]*></script>')
LARGE_TEXT = (
    'html { font-size: 200% !important; }'
    '* { line-height: 1.5 !important; letter-spacing: .12em !important;'
    ' word-spacing: .16em !important; }'
)


def append_style(page, css):
    page.evaluate('''css => {
      const node = document.createElement('style');
      node.textContent = css;
      document.head.append(node);
    }''', css)


def main():
    original = ROUTE.read_text(encoding='utf-8')
    styles = [
        (ROOT / name.split('?', 1)[0].lstrip('/')).read_text(encoding='utf-8')
        for name in STYLES.findall(original)
    ]
    html = SCRIPTS.sub('', LINKS.sub('', original))
    checks = 0
    fragments = 0
    interactive = 0
    with sync_playwright() as pw:
        launch = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'):
            launch['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**launch)
        context = browser.new_context(java_script_enabled=False, reduced_motion='reduce')
        context.route('**/*', lambda route: route.abort())

        def render(width, large):
            page = context.new_page()
            page.set_viewport_size({'width': width, 'height': 900})
            page.set_content(html, wait_until='domcontentloaded')
            for css in styles:
                append_style(page, css)
            if large:
                append_style(page, LARGE_TEXT)
            return page

        try:
            for width, large in [
                (320, False), (390, False), (620, False),
                (768, False), (1024, False), (1440, False),
                (320, True), (390, True), (620, True),
                (768, True), (1024, True), (1440, True),
            ]:
                page = render(width, large)
                state = page.evaluate('''() => {
                  const nodes = [...document.querySelectorAll('.nav-links li')];
                  const rects = nodes.map(el => el.getBoundingClientRect());
                  const collisions = [];
                  for (let a = 0; a < rects.length; a++) {
                    for (let b = a + 1; b < rects.length; b++) {
                      const dx = Math.min(rects[a].right, rects[b].right)
                        - Math.max(rects[a].left, rects[b].left);
                      const dy = Math.min(rects[a].bottom, rects[b].bottom)
                        - Math.max(rects[a].top, rects[b].top);
                      if (dx > 1 && dy > 1) collisions.push([a, b]);
                    }
                  }
                  return {
                    width: document.documentElement.scrollWidth,
                    nav: nodes.map(node => ({
                      name: node.textContent.trim(),
                      available: node.clientWidth,
                      required: node.scrollWidth,
                      left: node.getBoundingClientRect().left,
                      right: node.getBoundingClientRect().right
                    })),
                    collisions
                  };
                }''')
                assert state['width'] <= width + 1, (width, large, 'overflow', state)
                assert len(state['nav']) == 6, (width, large, 'missing links')
                assert not state['collisions'], (width, large, 'nav overlap', state)
                for link in state['nav']:
                    assert link['required'] <= link['available'] + 1, (
                        width, large, 'clipped label', link)
                    assert link['left'] >= -1 and link['right'] <= width + 1, (
                        width, large, 'off-screen label', link)
                checks += 1
                page.close()

            for fragment in (
                'brief-workspace', 'brief-examples', 'brief-example-meeting',
                'brief-blank',
                'brief-next-check', 'how-it-works',
            ):
                page = render(320, True)
                if fragment == 'brief-example-meeting':
                    page.locator('#brief-walkthrough summary').click()
                jump = page.locator('.entry-jumps a[href="#' + fragment + '"]')
                if not jump.count():
                    jump = page.locator('a[href="#' + fragment + '"]')
                assert jump.count(), ('missing fragment link', fragment)
                jump.first.focus()
                page.keyboard.press('Enter')
                state = page.evaluate('''id => ({
                  hash: location.hash,
                  headerBottom: document.querySelector('.site-header').getBoundingClientRect().bottom,
                  targetTop: document.getElementById(id).getBoundingClientRect().top,
                })''', fragment)
                assert state['hash'] == '#' + fragment, (fragment, state)
                assert state['targetTop'] >= state['headerBottom'] - 1, (
                    fragment, 'heading hidden by sticky header', state)
                fragments += 1
                page.close()
            assert context.cookies() == []
            script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
            live_context = browser.new_context(
                java_script_enabled=True, reduced_motion='reduce')
            live_context.route('**/*', lambda route: route.abort())
            try:
                for width in (320, 390, 620):
                    page = live_context.new_page()
                    page.set_viewport_size({'width': width, 'height': 900})
                    page.set_content(html, wait_until='domcontentloaded')
                    for css in styles:
                        append_style(page, css)
                    append_style(page, LARGE_TEXT)
                    page.add_script_tag(content=script)
                    assert page.locator('#brief-editor').is_visible(), width
                    for field in ('goal', 'materials', 'output', 'review'):
                        page.locator('#brief-' + field).fill(
                            'A fictional example requiring independent checks.')
                    page.locator('#brief-build').click()
                    assert page.locator('#brief-result').is_visible(), width
                    assert page.locator('#brief-preview .brief-preview-part').count() == 6, width
                    assert 'WORKING INSTRUCTIONS' in page.locator('#brief-text').input_value()
                    assert page.evaluate('document.documentElement.scrollWidth') <= width + 1, (
                        width, 'assembled brief overflows')
                    # At 200% text, the next step must not be buried after a
                    # sixteen-row readonly textarea. Navigation is in-page:
                    # the completed brief remains available until departure.
                    next_link = page.locator('#brief-result-next a[href="#brief-next-check"]')
                    assert next_link.is_visible(), width
                    assert page.locator('#brief-result-next').bounding_box()['y'] < (
                        page.locator('#brief-text').bounding_box()['y']), width
                    saved = page.locator('#brief-text').input_value()
                    next_link.focus()
                    page.keyboard.press('Enter')
                    assert page.evaluate('location.hash') == '#brief-next-check', width
                    headerBottom, targetTop = page.evaluate('''() => [
                        document.querySelector('.site-header').getBoundingClientRect().bottom,
                        document.getElementById('brief-next-check').getBoundingClientRect().top,
                    ]''')
                    assert targetTop >= headerBottom - 1, (width, 'check hidden by header',
                                                           headerBottom, targetTop)
                    assert page.locator('#brief-text').input_value() == saved, width
                    assert page.locator('#brief-result').is_visible(), width
                    assert page.evaluate('document.documentElement.scrollWidth') <= width + 1, (
                        width, 'handoff overflows')
                    # A very large reader font can scroll the standalone
                    # selection cue out of view. The visible fallback panel
                    # must itself explain that selection is not a copy.
                    page.go_back()
                    page.locator('#brief-select').click()
                    panel = page.locator('#brief-export-alternatives')
                    assert panel.is_visible(), width
                    title = panel.locator('#brief-export-alternatives-title').inner_text()
                    assert 'Selected, not copied.' in title and 'Ctrl+C' in title, width
                    assert 'Cmd+C' in title and 'touch Copy' in title, width
                    assert page.locator('#brief-text').evaluate(
                        'el => el.selectionStart === 0 && el.selectionEnd === el.value.length'
                    ), width
                    assert page.locator('#brief-text').input_value() == saved, width
                    assert page.evaluate('document.documentElement.scrollWidth') <= width + 1, (
                        width, 'manual selection overflows')
                    interactive += 1
                    page.close()
                assert live_context.cookies() == []
            finally:
                live_context.close()
        finally:
            context.close()
            browser.close()
    print(json.dumps({
        'status': 'pass', 'navigation_and_width_checks': checks,
        'enlarged_keyboard_fragment_arrivals': fragments,
        'assembled_large_text_preview_checks': interactive,
        'method': 'offline Chromium, local CSS and builder JS; no remote requests',
    }))


if __name__ == '__main__':
    main()
