"""Offline browser smoke for core NolanKido visitor journeys at narrow widths.

Reads committed public pages and every same-origin stylesheet they reference.
No login, external fonts, network requests, private analytics or GitHub Actions.
This is a LOCAL acceptance test, not real-user Web Vitals or deployment evidence.
"""
from html.parser import HTMLParser
from pathlib import Path
import json
import os
import re
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ('/', '/start-here/', '/technology/', '/books/', '/poker/free-poker-learning-path/', '/poker/10bb/')
WIDTHS = (320, 390, 768, 1440)
LARGE_TEXT = ('html{font-size:200%!important}'
              '*{line-height:1.5!important;letter-spacing:.12em!important;'
              'word-spacing:.16em!important}')


class LocalStyles(HTMLParser):
    """Read actual local stylesheet URLs, including /styles.css, in order."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.paths = []

    def handle_starttag(self, tag, attrs):
        if tag != 'link':
            return
        values = dict(attrs)
        if 'stylesheet' not in (values.get('rel') or '').lower().split():
            return
        href = values.get('href') or ''
        parts = urlsplit(href)
        if parts.scheme or parts.netloc or not parts.path.startswith('/'):
            return
        if parts.path == '/styles.css' or parts.path.startswith('/assets/'):
            path = ROOT / parts.path.lstrip('/')
            assert path.is_file(), f'missing local CSS referenced by page: {path}'
            self.paths.append(path)


def page_file(route):
    return ROOT / route.lstrip('/') / 'index.html'


def load(route):
    html = page_file(route).read_text(encoding='utf-8')
    parser = LocalStyles()
    parser.feed(html)
    assert parser.paths, (route, 'no local stylesheets discovered')
    # Insert each local stylesheet at the original <link> position. This keeps
    # cascade order relative to page-specific inline <style> rules.
    inlined = [0]

    def replace_link(match):
        tag = match.group(0)
        rel = re.search(r'\brel="([^"]+)"', tag, flags=re.I)
        href = re.search(r'\bhref="([^"]+)"', tag, flags=re.I)
        if not rel or 'stylesheet' not in rel.group(1).lower().split() or not href:
            return ''
        url = urlsplit(href.group(1))
        if url.scheme or url.netloc or not url.path.startswith('/'):
            return ''
        if url.path == '/styles.css' or url.path.startswith('/assets/'):
            path = ROOT / url.path.lstrip('/')
            assert path.is_file(), ('missing local stylesheet', route, path)
            inlined[0] += 1
            return '<style>\n' + path.read_text(encoding='utf-8') + '\n</style>'
        return ''

    html = re.sub(r'<link\b[^>]*>', replace_link, html, flags=re.I)
    assert inlined[0] == len(parser.paths), (route, 'CSS coverage mismatch')
    html = re.sub(r'<script\b[^>]*>.*?</script\s*>', '', html, flags=re.I | re.S)
    return html


def inspect(page, route, width, enlarged):
    state = page.evaluate('''() => {
      const nav = [...document.querySelectorAll('.nav-links li')];
      const boxes = nav.map(item => item.getBoundingClientRect());
      const overlaps = [];
      for (let i=0;i<boxes.length;i++) for (let j=i+1;j<boxes.length;j++) {
        const dx=Math.min(boxes[i].right,boxes[j].right)-Math.max(boxes[i].left,boxes[j].left);
        const dy=Math.min(boxes[i].bottom,boxes[j].bottom)-Math.max(boxes[i].top,boxes[j].top);
        if (dx>1 && dy>1) overlaps.push([i,j]);
      }
      return {
        viewport: innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
        nav: nav.map(item => ({label:item.textContent.trim(),
          left:item.getBoundingClientRect().left,
          right:item.getBoundingClientRect().right,
          available:item.clientWidth,
          required:item.scrollWidth})),
        overlaps,
        main: !!document.querySelector('main#main'),
        skip: !!document.querySelector('a.skip-link[href="#main"]'),
      };
    }''')
    assert state['main'] and state['skip'], (route, width, enlarged, 'main/skip absent')
    assert state['viewport'] == width, (route, width, enlarged, state)
    assert state['scrollWidth'] <= width + 1, (route, width, enlarged, 'document overflow', state)
    assert len(state['nav']) == 6 and not state['overlaps'], (
        route, width, enlarged, 'primary links overlap or disappear', state)
    for link in state['nav']:
        assert link['left'] >= -1 and link['right'] <= width + 1, (
            route, width, enlarged, 'primary link off screen', link)
        assert link['required'] <= link['available'] + 1, (
            route, width, enlarged, 'primary link clipped', link)
    return state


def check_reader_paths():
    source = (ROOT / '_source/start-here.html').read_text(encoding='utf-8')
    published = page_file('/start-here/').read_text(encoding='utf-8')
    home = page_file('/').read_text(encoding='utf-8')
    case = page_file('/technology/checking-ai-website-changes/').read_text(encoding='utf-8')
    books = page_file('/books/').read_text(encoding='utf-8')
    playbook = page_file('/poker/10bb/').read_text(encoding='utf-8')
    beginner = page_file('/poker/free-poker-learning-path/').read_text(encoding='utf-8')
    assert 'href="/poker/10bb/#six-checks"' in beginner, 'beginner course missing optional tournament study handoff'
    assert 'id="six-checks"' in playbook, 'advanced study handoff has no real section'
    proof_url = '/technology/checking-ai-website-changes/'
    workbook_url = '/downloads/website-check-offline-runbook.md'
    for html in (source, published, home):
        assert f'href="{proof_url}"' in html, 'recorded AI release not discoverable'
    assert f'href="{workbook_url}"' in case, 'missing release checklist'
    assert (ROOT / workbook_url.lstrip('/')).is_file(), 'unpublished release checklist'
    for href in ('/books/one-workflow-at-a-time/',
                 '/books/how-to-play-no-limit-texas-holdem/'):
        assert f'href="{href}"' in books, ('missing book route', href)
    for href in ('/downloads/ten-bb-tournament-checklist.md',
                 '/downloads/ten-bb-playbook-icm-verify.py'):
        assert f'href="{href}"' in playbook, ('missing playbook download', href)
        assert (ROOT / href.lstrip('/')).is_file(), ('missing playbook file', href)


def main():
    check_reader_paths()
    checks = 0
    with sync_playwright() as pw:
        launch = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'):
            launch['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = pw.chromium.launch(**launch)
        context = browser.new_context(java_script_enabled=False)
        context.route('**/*', lambda route: route.abort())
        page = context.new_page()
        try:
            for route in ROUTES:
                html = load(route)
                for width in WIDTHS:
                    for enlarged in ((False, True) if width in (320, 390) else (False,)):
                        page.set_viewport_size({'width': width, 'height': 900})
                        page.set_content(html, wait_until='domcontentloaded')
                        if enlarged:
                            page.add_style_tag(content=LARGE_TEXT)
                        inspect(page, route, width, enlarged)
                        checks += 1
            assert context.cookies() == [], 'unexpected browser state'
        finally:
            context.close()
            browser.close()
    print(json.dumps({'status': 'pass', 'routes': list(ROUTES),
                      'viewport_checks': checks,
                      'method': 'offline Chromium with true local styles, scripts and network disabled'}))


if __name__ == '__main__':
    main()
