"""Offline reading regression for the Living Well hub, not its child pages.

Check both fallback fonts and the exact committed WOFF2 fonts embedded into
in-memory styles. No server, remote requests, page scripts or storage is used.
"""

import base64
import json
import os
from pathlib import Path
import re

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
STYLES = re.compile(r'<link rel="stylesheet" href="(/assets/[^"]+)"')
LINKS = re.compile(r'<link\b[^>]*>')
SCRIPTS = re.compile(r'<script\b[^>]*\bsrc="[^"]+"[^>]*></script>')
FONT_URLS = re.compile(r'url\((/assets/fonts/[^)]+)\)')
LARGE_TEXT = (
    'html { font-size: 200% !important; }'
    '* { line-height: 1.5 !important; letter-spacing: .12em !important;'
    ' word-spacing: .16em !important; }'
)
SECTIONS = (
    'a-life-worth-attending-to', 'technology-in-ordinary-life',
    'start-where-you-are', 'three-free-starts', 'choose-a-route',
    'resource-subsections', 'five-subjects', 'a-small-invitation',
    'first-collection',  # Preserved legacy bookmark, not a heading.
)


def inline_font(match):
    data = (ROOT / match.group(1).lstrip('/')).read_bytes()
    return 'url(data:font/woff2;base64,' + base64.b64encode(data).decode('ascii') + ')'


def append_style(page, css):
    page.evaluate('''css => {
      const node = document.createElement('style');
      node.textContent = css;
      document.head.append(node);
    }''', css)


def main():
    original = (ROOT / 'living-well/index.html').read_text(encoding='utf-8')
    assets = STYLES.findall(original)
    assert sum('living-well-reader.css' in name for name in assets) == 1
    styles = []
    for name in assets:
        relative = name.split('?', 1)[0].lstrip('/')
        css = (ROOT / relative).read_text(encoding='utf-8')
        styles.append((relative, FONT_URLS.sub(inline_font, css)))
    html = SCRIPTS.sub('', LINKS.sub('', original))
    layouts, skips, fragments = 0, 0, 0
    with sync_playwright() as pw:
        launch = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'):
            launch['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**launch)
        context = browser.new_context(java_script_enabled=False, reduced_motion='reduce')
        context.route('**/*', lambda route: route.abort())

        def render(width, enlarged, site_fonts):
            page = context.new_page()
            page.set_viewport_size({'width': width, 'height': 900})
            page.set_content(html, wait_until='domcontentloaded')
            for relative, css in styles:
                if site_fonts or relative != 'assets/site-fonts.css':
                    append_style(page, css)
            if enlarged:
                append_style(page, LARGE_TEXT)
            loaded = page.evaluate('''async () => {
              await document.fonts.ready;
              return [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family);
            }''')
            if site_fonts:
                assert {'IBM Plex Mono', 'Schibsted Grotesk', 'Source Serif 4'} <= set(loaded), loaded
            return page

        def arrival(page, fragment):
            state = page.evaluate('''id => {
              const target = document.getElementById(id).getBoundingClientRect();
              return {hash: location.hash, focused: document.activeElement.id,
                top: target.top, height: target.height, viewport: innerHeight,
                header: document.querySelector('.site-header').getBoundingClientRect().bottom};
            }''', fragment)
            assert state['hash'] == '#' + fragment, (fragment, state)
            assert state['header'] - 1 <= state['top'] < state['viewport'], (
                fragment, 'target not visible below header', state)
            if fragment != 'first-collection':
                assert state['height'] > 0, (fragment, 'empty target', state)
            return state

        try:
            for site_fonts in (False, True):
                for width in (320, 390, 620, 768, 1024, 1440):
                    for enlarged in (False, True):
                        page = render(width, enlarged, site_fonts)
                        state = page.evaluate('''() => {
                          function measure(selector) {
                            const nodes = [...document.querySelectorAll(selector)];
                            const rects = nodes.map(node => node.getBoundingClientRect());
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
                            return {collisions, items: nodes.map(node => ({
                              name: node.textContent.trim(), width: node.clientWidth,
                              content: node.scrollWidth,
                              left: node.getBoundingClientRect().left,
                              right: node.getBoundingClientRect().right,
                            }))};
                          }
                          return {
                            width: document.documentElement.scrollWidth,
                            primary: measure('.nav-links li'),
                            primaryLinks: measure('.nav-links a'),
                            topic: measure('.subsite-links a'),
                            secondary: measure('.lw-secondary-links a'),
                            textOverflow: [...document.querySelectorAll('.section-meta, .section-content')]
                              .filter(x => x.scrollWidth > x.clientWidth + 1).length,
                          };
                        }''')
                        case = (width, enlarged, site_fonts)
                        assert state['width'] <= width + 1, (case, 'page overflow', state)
                        assert state['textOverflow'] == 0, (case, 'reading column overflow', state)
                        for key, count in (('primary', 6), ('primaryLinks', 6), ('topic', 4), ('secondary', 4)):
                            group = state[key]
                            assert len(group['items']) == count, (case, key, group)
                            assert not group['collisions'], (case, key, 'overlap', group)
                            for link in group['items']:
                                assert link['content'] <= link['width'] + 1, (case, key, 'clipping', link)
                                assert link['left'] >= -1 and link['right'] <= width + 1, (
                                    case, key, 'off-screen link', link)
                        layouts += 1
                        page.close()

                page = render(320, True, site_fonts)
                page.locator('.skip-link').focus()
                page.keyboard.press('Enter')
                assert arrival(page, 'main')['focused'] == 'main'
                skips += 1
                for fragment in SECTIONS:
                    page.evaluate('id => { location.hash = "#" + id; }', fragment)
                    arrival(page, fragment)
                    fragments += 1
                page.close()
            assert context.cookies() == []
        finally:
            context.close()
            browser.close()
    print(json.dumps({
        'status': 'pass', 'responsive_layout_checks': layouts,
        'keyboard_skip_checks': skips, 'section_deep_link_arrivals': fragments,
        'font_modes': ['fallback', 'committed WOFF2 fonts'],
        'method': 'offline Chromium, local assets, scripts disabled, no remote requests',
    }))


if __name__ == '__main__':
    main()
