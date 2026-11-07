"""Offline enlarged-text and fragment accessibility regression for Resources.

Uses committed HTML with local styles and no remote requests, server, page
scripts, cookies or scheduled automation. Run with CHROMIUM_PATH if needed.
"""

import json
import os
from pathlib import Path
import re

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
STYLES = re.compile(r'<link rel="stylesheet" href="(/assets/[^"]+)"')
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
    original = (ROOT / 'resources/index.html').read_text(encoding='utf-8')
    styles = [
        (ROOT / name.split('?', 1)[0].lstrip('/')).read_text(encoding='utf-8')
        for name in STYLES.findall(original)
    ]
    assert any('resources-reader.css' in name for name in STYLES.findall(original))
    html = SCRIPTS.sub('', LINKS.sub('', original))
    layout_checks = 0
    keyboard_jumps = 0
    external_fragments = 0
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

        def landing(page, fragment):
            return page.evaluate('''id => ({
              hash: location.hash,
              target: document.getElementById(id).getBoundingClientRect().top,
              header: document.querySelector('.site-header').getBoundingClientRect().bottom,
            })''', fragment)

        try:
            for width in (320, 390, 620, 768, 1024, 1440):
                for large in (False, True):
                    page = render(width, large)
                    state = page.evaluate('''() => {
                      const links = [...document.querySelectorAll('.nav-links li')];
                      const rects = links.map(x => x.getBoundingClientRect());
                      const collisions = [];
                      for (let i = 0; i < rects.length; i++) {
                        for (let j = i + 1; j < rects.length; j++) {
                          const dx = Math.min(rects[i].right, rects[j].right)
                            - Math.max(rects[i].left, rects[j].left);
                          const dy = Math.min(rects[i].bottom, rects[j].bottom)
                            - Math.max(rects[i].top, rects[j].top);
                          if (dx > 1 && dy > 1) collisions.push([i, j]);
                        }
                      }
                      return {
                        pageWidth: document.documentElement.scrollWidth,
                        links: links.map(link => ({
                          name: link.textContent.trim(), width: link.clientWidth,
                          content: link.scrollWidth,
                          left: link.getBoundingClientRect().left,
                          right: link.getBoundingClientRect().right,
                        })),
                        collisions,
                        metaOverflow: [...document.querySelectorAll('.section-meta')]
                          .filter(x => x.scrollWidth > x.clientWidth + 1).length,
                      };
                    }''')
                    assert state['pageWidth'] <= width + 1, (width, large, 'overflow', state)
                    assert len(state['links']) == 6, (width, large, 'missing links')
                    assert not state['collisions'], (width, large, 'collisions', state)
                    assert state['metaOverflow'] == 0, (width, large, 'section label', state)
                    for link in state['links']:
                        assert link['content'] <= link['width'] + 1, (
                            width, large, 'clipped navigation label', link)
                        assert link['left'] >= -1 and link['right'] <= width + 1, (
                            width, large, 'off-screen navigation label', link)
                    layout_checks += 1
                    page.close()

            for fragment in (
                'resources-technology', 'resources-living-well', 'resources-poker',
                'resources-creative', 'thinking-worksheets',
            ):
                page = render(320, True)
                jump = page.locator('.entry-jumps a[href="#' + fragment + '"]')
                assert jump.count() == 1, ('missing native jump', fragment)
                jump.focus()
                page.keyboard.press('Enter')
                state = landing(page, fragment)
                assert state['hash'] == '#' + fragment, (fragment, state)
                assert state['target'] >= state['header'] - 1, (
                    fragment, 'target hidden by header', state)
                keyboard_jumps += 1
                page.close()

            # These native deep links appear in the downloadable worksheets.
            for fragment in ('decision-record', 'tool-trust-check', 'learning-loop'):
                page = render(320, True)
                page.evaluate('id => { location.hash = "#" + id; }', fragment)
                state = landing(page, fragment)
                assert state['hash'] == '#' + fragment, (fragment, state)
                assert state['target'] >= state['header'] - 1, (
                    fragment, 'deep-linked worksheet hidden by header', state)
                external_fragments += 1
                page.close()

            assert context.cookies() == []
        finally:
            context.close()
            browser.close()

    print(json.dumps({
        'status': 'pass', 'responsive_layout_checks': layout_checks,
        'keyboard_resource_jumps': keyboard_jumps,
        'external_worksheet_fragments': external_fragments,
        'method': 'offline Chromium, local CSS, scripts disabled, no remote requests',
    }))


if __name__ == '__main__':
    main()
