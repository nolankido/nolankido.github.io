"""Offline enlarged-text navigation regression for About and Bio.

Loads committed HTML and CSS into an in-memory Chromium page. No site scripts,
images, third-party requests, persistent storage or GitHub Actions are needed.
"""

from pathlib import Path
import json
import os
import re

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
ROUTES = ('/about/', '/bio/')
STYLES = re.compile(r'<link rel="stylesheet" href="(/assets/[^\"]+)"')
LINKS = re.compile(r'<link\b[^>]*>')
EXTERNAL_SCRIPTS = re.compile(r'<script\b[^>]*\bsrc="[^"]+"[^>]*></script>')
LARGE_TEXT = (
    'html { font-size: 200% !important; }'
    '* { line-height: 1.5 !important; letter-spacing: .12em !important;'
    ' word-spacing: .16em !important; }'
)


def load_page(route):
    path = ROOT / route.lstrip('/') / 'index.html'
    html = path.read_text(encoding='utf-8')
    css = []
    for asset in STYLES.findall(html):
        relative = asset.split('?', 1)[0].lstrip('/')
        css.append((ROOT / relative).read_text(encoding='utf-8'))
    return EXTERNAL_SCRIPTS.sub('', LINKS.sub('', html)), css


def append_style(page, css):
    # Avoid waiting for a font URL or an external stylesheet to load.
    page.evaluate('''css => {
      const style = document.createElement('style');
      style.textContent = css;
      document.head.append(style);
    }''', css)


def inspect(page, route, width, enlargement):
    state = page.evaluate('''() => {
      const links = [...document.querySelectorAll('.nav-links li')];
      const boxes = links.map(link => link.getBoundingClientRect());
      const overlaps = [];
      for (let i = 0; i < boxes.length; i++) {
        for (let j = i + 1; j < boxes.length; j++) {
          const x = Math.min(boxes[i].right, boxes[j].right)
                  - Math.max(boxes[i].left, boxes[j].left);
          const y = Math.min(boxes[i].bottom, boxes[j].bottom)
                  - Math.max(boxes[i].top, boxes[j].top);
          if (x > 1 && y > 1) overlaps.push([i, j]);
        }
      }
      return {
        labels: links.map(link => ({
          name: link.textContent.trim(),
          available: link.clientWidth,
          required: link.scrollWidth,
          x: link.getBoundingClientRect().left,
          right: link.getBoundingClientRect().right,
        })), overlaps,
      };
    }''')
    assert len(state['labels']) == 6, (route, 'missing navigation', state)
    assert not state['overlaps'], (route, width, enlargement, state)
    for label in state['labels']:
        assert label['required'] <= label['available'] + 1, (
            route, width, enlargement, 'label clipped', label)
        assert label['x'] >= -1 and label['right'] <= width + 1, (
            route, width, enlargement, 'label off screen', label)


def main():
    with sync_playwright() as pw:
        launch = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'):
            launch['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**launch)
        context = browser.new_context(java_script_enabled=False)
        context.route('**/*', lambda route: route.abort())
        page = context.new_page()
        count = 0
        anchor_arrivals = 0
        try:
            for route in ROUTES:
                html, styles = load_page(route)
                for width, enlargement in [
                    (320, False), (390, False), (620, False),
                    (768, False), (1440, False),
                    (320, True), (390, True), (620, True),
                ]:
                    page.set_viewport_size({'width': width, 'height': 900})
                    page.set_content(html, wait_until='domcontentloaded')
                    for css in styles:
                        append_style(page, css)
                    if enlargement:
                        append_style(page, LARGE_TEXT)
                    inspect(page, route, width, enlargement)
                    count += 1
            page.emulate_media(reduced_motion='reduce')
            for route, link, heading in [
                ('/about/', 'a[href="#what-matters-in-the-work"]', '#what-matters-in-the-work'),
                ('/bio/', 'a[href="#long-bio-title"]', '#long-bio-title'),
            ]:
                html, styles = load_page(route)
                page.set_viewport_size({'width': 320, 'height': 900})
                page.set_content(html, wait_until='domcontentloaded')
                for css in styles:
                    append_style(page, css)
                append_style(page, LARGE_TEXT)
                page.locator(link).first.focus()
                page.keyboard.press('Enter')
                position = page.evaluate('''id => {
                  const header = document.querySelector('.site-header').getBoundingClientRect();
                  const target = document.querySelector(id).getBoundingClientRect();
                  return {headerBottom: header.bottom, targetTop: target.top,
                          hash: location.hash};
                }''', heading)
                assert position['hash'] == heading, (route, 'fragment not reached', position)
                assert position['targetTop'] >= position['headerBottom'] - 1, (
                    route, 'heading hidden by sticky header', position)
                anchor_arrivals += 1
            assert context.cookies() == []
            # In-memory about:blank pages have opaque origins, so the browser
            # correctly denies access to localStorage. Scripts are disabled.
        finally:
            context.close()
            browser.close()
    print(json.dumps({'status': 'pass', 'pages': len(ROUTES),
                      'navigation_layout_checks': count,
                      'enlarged_keyboard_fragment_arrivals': anchor_arrivals,
                      'method': 'offline Chromium, locally injected styles, scripts disabled'}))


if __name__ == '__main__':
    main()
