"""Executed from the retained Living Well browser gate, with no external requests allowed."""
from pathlib import Path
from urllib.parse import urlsplit
import json
from playwright.sync_api import expect

def check_directory(context, nojs, base, root: Path, output: Path):
    page = context.new_page()
    requests, errors = [], []
    page.on('request', lambda request: requests.append((request.method, request.url)))
    page.on('pageerror', lambda error: errors.append(str(error)))
    try:
        page.goto(base + '/living-well/find/')
        page.wait_for_load_state('load')
        expect(page.locator('#lw-filters')).to_be_visible()
        expect(page.locator('[data-lw-entry]:visible')).to_have_count(98)
        assert page.locator('[data-lw-entry]').count() == 98
        before = list(requests)
        query = page.get_by_label('A topic, task, or resource name')
        query.fill('ÓBSIDIAN')
        expect(page.locator('[data-lw-entry]:visible')).to_have_count(1)
        expect(page.locator('#resource-obsidian')).to_be_visible()
        query.fill('  shared   notes ')
        expect(page.locator('#resource-google-keep')).to_be_visible()
        expect(page.locator('#resource-simplenote')).to_be_visible()
        page.get_by_label('Collection', exact=True).select_option('notes-documents')
        page.get_by_label('Entry access').select_option('account')
        expect(page.locator('[data-lw-entry]:visible')).to_have_count(1)
        expect(page.locator('#resource-simplenote')).to_be_visible()
        query.fill('<script>window.injected=true</script>')
        expect(page.locator('[data-lw-entry]:visible')).to_have_count(0)
        expect(page.locator('#lw-empty')).to_be_visible()
        assert page.evaluate('window.injected') is None
        page.get_by_role('button', name='Clear filters').focus()
        page.keyboard.press('Enter')
        expect(query).to_be_focused()
        expect(page.locator('[data-lw-entry]:visible')).to_have_count(98)
        expect(page.locator('#lw-empty')).not_to_be_visible()
        query.fill('backup')
        expect(page.locator('#resource-syncthing')).to_be_visible()
        page.get_by_label('Collection', exact=True).select_option('files-recovery')
        visible = page.locator('[data-lw-entry]:visible').count()
        assert visible > 0
        expect(page.locator('#lw-result-count')).to_have_text(f'Showing {visible} of 98 resources.')
        expect(page).to_have_url(base + '/living-well/find/')
        assert requests == before, 'Filtering must not generate any request'
        assert page.evaluate('localStorage.length') == 0
        assert page.evaluate('sessionStorage.length') == 0
        assert context.cookies() == []
        for width in (390, 1440):
            page.set_viewport_size({'width': width, 'height': 1000})
            page.screenshot(path=str(output / f'living-well-finder-filtered-{width}.png'), full_page=True)
        page.get_by_role('button', name='Clear filters').click()
        # One normal keyboard path from directory choice to canonical resource context.
        page.goto(base + '/living-well/free-resources/')
        page.locator('a[href="/living-well/tasks/read-and-understand/"]').focus()
        page.keyboard.press('Enter')
        expect(page.locator('h1')).to_have_text('Read, listen and understand')
        page.locator('#choice-nvda a').last.focus()
        page.keyboard.press('Enter')
        page.wait_for_url(base + '/living-well/free-resources/reading-access/#nvda', wait_until='load')
        page.locator('#nvda summary').focus()
        page.keyboard.press('Enter')
        expect(page.locator('#nvda .lw-resource-notes')).to_have_attribute('open', '')
        plain = nojs.new_page()
        try:
            plain.goto(base + '/living-well/find/')
            expect(plain.locator('#lw-filters')).not_to_be_visible()
            expect(plain.locator('[data-lw-entry]:visible')).to_have_count(98)
            # Every result remains a native link even when enhancement never runs.
            expect(plain.locator('#resource-nvda a').first).to_have_attribute('href', 'https://www.nvaccess.org/about-nvda/')
            plain.locator('#resource-nvda a').last.click()
            plain.wait_for_url(base + '/living-well/free-resources/reading-access/#nvda', wait_until='load')
            expect(plain.locator('h1')).to_have_text('Reading, listening & participation')
            plain.goto(base + '/living-well/tasks/protect-and-recover/')
            expect(plain.locator('#choice-syncthing')).to_be_visible()
        finally:
            plain.close()
        assert not errors, errors
        (output / 'living-well-directory-browser.json').write_text(json.dumps({
            'inventory': 98, 'passed': True, 'literal_query_test': True,
            'combined_filters': True, 'filter_network_requests': 0,
            'nojs_static_inventory': 98, 'errors': errors,
            'note': 'Network comparison is asserted before intentional navigation; later navigation is allowed.'
        }, indent=2) + '\n')
        print('PASS: local directory search, combined filters, clear/empty states, keyboard paths, no-JS inventory and no query transport')
    finally:
        page.close()
