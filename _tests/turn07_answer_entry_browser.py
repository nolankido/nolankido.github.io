"""Local-only browser checks for the AI answer-checking entry, table and offline link.

CHROMIUM_PATH may point to an installed Chromium. No external requests or forms.
"""

import json
import os
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from browser import html_for


def run():
    checks = []
    failures = []
    with sync_playwright() as playwright:
        options = {'headless': True}
        if os.environ.get('CHROMIUM_PATH'):
            options['executable_path'] = os.environ['CHROMIUM_PATH']
        browser = playwright.chromium.launch(**options)
        try:
            context = browser.new_context(accept_downloads=False, reduced_motion='reduce')
            context.route('**/*', lambda route: route.abort())
            page = context.new_page()
            page_errors = []
            page.on('pageerror', lambda error: page_errors.append(str(error)))
            page.set_content(html_for('/technology/check-ai-answers/'), wait_until='domcontentloaded')
            for width in (320, 390, 768, 1440):
                page.set_viewport_size({'width': width, 'height': 900})
                measurements = page.evaluate('''() => {
                  const panel = document.querySelector('[aria-label="Claim types, warning signs, independent checks, and unknowns"]');
                  return {pageWidth: document.documentElement.scrollWidth,
                          viewportWidth: innerWidth, panelWidth: panel.clientWidth,
                          panelContents: panel.scrollWidth,
                          rows: document.querySelectorAll('.review-evidence-map tbody tr').length,
                          download: document.querySelector('.review-quick-action a').getAttribute('href')};
                }''')
                checks.append({'viewport': width, **measurements})
                if measurements['pageWidth'] > width:
                    failures.append({'viewport': width, 'reason': 'page horizontal overflow'})
                if width == 320 and measurements['panelContents'] <= measurements['panelWidth']:
                    failures.append({'viewport': width, 'reason': 'matrix should scroll within its region'})
                if measurements['rows'] != 6:
                    failures.append({'viewport': width, 'reason': 'matrix row count'})
                if measurements['download'] != '/downloads/ai-answer-quick-check.txt':
                    failures.append({'viewport': width, 'reason': 'offline checklist link'})
            if page_errors:
                failures.append({'reason': 'uncaught script errors', 'errors': page_errors})
            page.emulate_media(media='print')
            if page.locator('.review-quick-action').evaluate('(el) => getComputedStyle(el).display') != 'none':
                failures.append({'reason': 'print includes redundant download button'})
            if page.locator('.review-evidence-map').evaluate('(el) => getComputedStyle(el).minWidth') != '0px':
                failures.append({'reason': 'print matrix retains scroll minimum width'})
        finally:
            browser.close()
    print(json.dumps({'status': 'pass' if not failures else 'fail',
                      'checks': checks, 'failures': failures}, indent=2))
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(run())
