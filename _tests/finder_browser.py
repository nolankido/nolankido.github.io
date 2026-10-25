"""Read-only local browser verification: search, accessibility, print and fallbacks."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import os
import re
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ('find','poker-math-reference','reading-preflop-charts','poker-rules-and-fair-play')
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
    def copyfile(self, source, out):
        try: super().copyfile(source, out)
        except (BrokenPipeError, ConnectionResetError): pass

# Exercise the real Blob/download path while replacing only the browser APIs
# whose failure modes need deterministic coverage. No OS clipboard is written.
SHELF_HOOKS = r"""(() => {
  const nativeBlob = window.Blob;
  const nativeCreate = URL.createObjectURL.bind(URL);
  const nativeRevoke = URL.revokeObjectURL.bind(URL);
  const state = window.__studyTest = {created: [], revoked: [], types: [], writes: [], failure: '', pending: []};
  const create = blob => {
    if (state.failure === 'url-throws') throw new Error('Test object URL failure');
    const url = nativeCreate(blob);
    state.created.push(url); state.types.push(blob.type); return url;
  };
  URL.revokeObjectURL = url => { state.revoked.push(url); nativeRevoke(url); };
  state.setFailure = failure => {
    state.failure = failure;
    window.Blob = failure === 'blob-missing' ? undefined : failure === 'blob-throws'
      ? function () { throw new Error('Test Blob failure'); } : nativeBlob;
    URL.createObjectURL = failure === 'url-missing' ? undefined : create;
  };
  state.setClipboard = mode => {
    Object.defineProperty(navigator, 'clipboard', {configurable: true, value: mode === 'missing' ? undefined : {
      writeText: text => {
        state.writes.push(text);
        if (mode === 'reject') return Promise.reject(new Error('Test clipboard rejection'));
        if (mode === 'pending') return new Promise((resolve, reject) => state.pending.push({resolve, reject}));
        return Promise.resolve();
      }
    }});
  };
  state.setFailure(''); state.setClipboard('success');
})();"""


def shelf_page(browser, origin, errors, width=1280):
    context = browser.new_context(accept_downloads=True, viewport={'width': width, 'height': 900})
    context.route('**/*', lambda r: r.continue_() if urlsplit(r.request.url).hostname == '127.0.0.1' else r.abort())
    context.add_init_script(SHELF_HOOKS)
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    requests = []
    page.on('request', lambda request: requests.append((request.method, request.url)))
    response = page.goto(origin + '/poker/find/')
    assert response and response.status == 200
    expect(page.locator('#finder-controls')).to_be_visible()
    page.wait_for_load_state('networkidle')
    return context, page, requests


def shelf_record(page, identifier):
    """Expected export facts come from the public card, never the export code."""
    return page.locator(f'[data-finder-card][data-id="{identifier}"]').evaluate("""card => ({
      id: card.dataset.id, title: card.querySelector('h3 a').textContent,
      url: card.querySelector('h3 a').getAttribute('href'),
      paragraphs: Array.from(card.querySelectorAll(':scope > p:not(.finder-excerpt):not(.finder-jump)'), p => ({
        text: p.textContent,
        links: Array.from(p.querySelectorAll('a[href]'), a => ({text: a.textContent, href: a.getAttribute('href')}))
      }))
    })""")


def add_shelf_card(page, identifier, query=None):
    record = shelf_record(page, identifier)
    search = page.locator('#finder-search')
    search.fill(query or record['title'])
    search.press('Enter')
    button = page.locator(f'[data-finder-card][data-id="{identifier}"] .finder-save')
    expect(button).to_be_visible()
    button.click()
    expect(button).to_have_attribute('aria-pressed', 'true')
    expect(button).to_be_focused()
    return record


def shelf_ids(page):
    return page.locator('.finder-shelf-remove').evaluate_all('buttons => buttons.map(button => button.dataset.finderRemove)')


def public_url(url):
    return 'https://nolankido.com' + url if url.startswith('/') else url


def assert_shelf_export(page, records, download=True):
    """The native file and selectable text contain only selected public facts."""
    content = page.locator('#finder-shelf-text').input_value()
    if download:
        with page.expect_download() as pending:
            page.locator('#finder-shelf-download').click()
        item = pending.value
        assert item.suggested_filename == 'poker-study-list.md'
        assert item.failure() is None
        assert Path(item.path()).read_text(encoding='utf-8') == content
    lines = ['# My poker study list', '', 'Public links selected on Nolan Kido Poker. This is a snapshot, not a new source review.', '']
    for identifier in shelf_ids(page):
        record = records[identifier]
        lines.extend(['## ' + record['title'], '', public_url(record['url']), ''])
        for paragraph in record['paragraphs']:
            lines.extend([paragraph['text'], ''])
            for link in paragraph['links']:
                assert f'[{link["text"]}]({public_url(link["href"])})' in content
    # Strip link markup only, preserving every paragraph and its original text.
    # This catches missing cautions, invented claims, passages and extra entries.
    plain = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'\1', content)
    assert plain == '\n'.join(lines), (plain, '\n'.join(lines))
    assert 'In this guide:' not in content
    assert 'Read matching section' not in content
    assert 'Searchable article text, without exercise answers' not in content
    return content


def assert_manual_copy(page, content):
    preview = page.locator('#finder-shelf-preview')
    text = page.locator('#finder-shelf-text')
    expect(preview).to_have_attribute('open', '')
    expect(text).to_be_visible()
    expect(text).to_have_value(content)
    expect(text).to_have_attribute('readonly', '')
    expect(text).to_be_focused()
    assert text.evaluate('field => field.selectionStart === 0 && field.selectionEnd === field.value.length')
    expect(page.get_by_label('Your complete study list in Markdown', exact=True)).to_have_count(1)
    expect(page.locator('#finder-shelf-status')).to_contain_text('Copy')


def assert_shelf_private(context, page, requests, before, url):
    assert requests == before, ('Study-list action generated a request', requests[len(before):])
    assert page.url == url
    assert context.cookies() == []
    assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')


def study_copy_focus_browser(browser, origin, errors):
    """A current copy failure explains recovery without taking moved focus."""
    context, page, requests = shelf_page(browser, origin, errors, 320)
    try:
        initial_requests, initial_url = list(requests), page.url
        record = add_shelf_card(page, 'poker-reading-preflop-charts', 'pre-flop')
        content = assert_shelf_export(page, {record['id']: record})
        page.evaluate('__studyTest.setClipboard("pending")')
        page.locator('#finder-shelf-copy').click()
        assert page.evaluate('__studyTest.writes') == [content]
        search = page.locator('#finder-search')
        search.fill('PLO8')
        expect(search).to_be_focused()
        page.evaluate("async () => { __studyTest.pending.shift().reject(new Error('Late test rejection')); await Promise.resolve(); }")
        expect(search).to_be_focused()
        expect(page.locator('#finder-shelf-status')).to_contain_text('Copying is unavailable')
        expect(page.locator('#finder-shelf-preview')).to_have_attribute('open', '')
        expect(page.locator('#finder-shelf-text')).to_be_visible()
        expect(page.locator('#finder-shelf-text')).to_have_value(content)
        expect(page.locator('[data-id="external-omaha-eight-rules"]')).to_be_visible()
        expect(search).to_be_focused()
        assert_shelf_private(context, page, requests, initial_requests, initial_url)
    finally:
        context.close()


def study_list_browser(browser, origin, errors, dest):
    for width in (320, 1280):
        context, page, requests = shelf_page(browser, origin, errors, width)
        try:
            initial_requests, initial_url = list(requests), page.url
            expect(page.locator('#finder-shelf')).not_to_be_visible()
            expect(page.locator('#finder-shelf-copy')).not_to_be_visible()
            assert page.evaluate('__studyTest.created.length === 0 && __studyTest.writes.length === 0')
            guide_id = 'poker-reading-preflop-charts'
            public_id = page.locator('[data-kind="resource"]').filter(has_text='Public page read').first.get_attribute('data-id')
            reviewed_id = 'external-nj-dge-information'
            assert public_id and reviewed_id and public_id != reviewed_id
            expect(page.locator(f'[data-id="{reviewed_id}"]')).to_contain_text('Public page read')
            records = {}
            for identifier, query in [(guide_id, 'pre-flop'), (public_id, None), (reviewed_id, None)]:
                records[identifier] = add_shelf_card(page, identifier, query)
            expect(page.locator('#finder-shelf-list li')).to_have_count(3)
            expect(page.locator('#finder-shelf-count')).to_contain_text('3 of 12')
            expect(page.locator('#finder-shelf-count')).to_have_attribute('role', 'status')
            expect(page.locator('#finder-shelf-status')).to_have_attribute('role', 'status')
            expect(page.locator('#finder-shelf-status')).to_have_attribute('aria-live', 'polite')
            expect(page.locator('#finder-shelf-status')).to_have_attribute('aria-atomic', 'true')
            for identifier in shelf_ids(page):
                button = page.locator(f'[data-finder-remove="{identifier}"]')
                expect(button).to_have_accessible_name('Remove ' + records[identifier]['title'] + ' from study list')
                assert button.bounding_box()['height'] >= 44
            content = assert_shelf_export(page, records)
            assert 'Before you use it:' in content
            assert content.count('Public page read') >= 2 and 'Search index only' not in content
            assert 'complain to the operator before filing' in content
            assert re.search(r'\d{4}-\d{2}-\d{2}', content)
            assert 'https://nolankido.com/poker/resources/#resource-' in content
            # Real teaching answers are not part of a catalogue-only export.
            guide_html = context.request.get(origin + '/poker/reading-preflop-charts/').text()
            answers = page.evaluate("html => Array.from(new DOMParser().parseFromString(html, 'text/html').querySelectorAll('details.viewer-question > div'), answer => answer.textContent.trim())", guide_html)
            assert len(answers) == 3 and all(answers)
            assert all(answer not in content for answer in answers)
            assert page.evaluate('__studyTest.writes.length === 0'), 'Adding/downloading must not copy automatically'
            # Preview is complete, labelled, read-only, and fits a narrow screen.
            page.locator('#finder-shelf-preview summary').click()
            expect(page.locator('#finder-shelf-text')).to_have_value(content)
            expect(page.locator('#finder-shelf-text')).to_have_attribute('readonly', '')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), ('study list', width)
            if dest:
                page.locator('#finder-shelf').screenshot(path=str(dest / f'poker-study-list-{width}.png'))
            page.emulate_media(media='print')
            expect(page.locator('#finder-shelf-list a')).to_have_count(3)
            expect(page.locator('#finder-shelf-list a').first).to_be_visible()
            for selector in ('#finder-shelf-copy', '#finder-shelf-clear', '#finder-shelf-download', '.finder-shelf-remove', '#finder-shelf-text'):
                assert page.locator(selector + ':visible').count() == 0, ('printed control', selector)
            page.emulate_media(media='screen')
            # The list stays editable when none of its result cards are visible.
            search = page.locator('#finder-search')
            private_query = 'study-export-private-marker-913'
            search.fill(private_query); search.press('Enter')
            expect(page.locator('#finder-empty')).to_be_visible()
            assert page.locator('[data-finder-card]:visible').count() == 0
            page.locator('#finder-shelf-copy').click()
            expect(page.locator('#finder-shelf-status')).to_contain_text('Study list copied')
            assert page.evaluate('__studyTest.writes') == [content]
            assert private_query not in content
            identifiers = shelf_ids(page)
            remove = page.locator(f'[data-finder-remove="{identifiers[1]}"]')
            remove.focus(); page.keyboard.press('Enter')
            expect(page.locator(f'[data-finder-remove="{identifiers[2]}"]')).to_be_focused()
            expect(page.locator(f'[data-id="{identifiers[1]}"] .finder-save')).to_have_attribute('aria-pressed', 'false')
            expect(page.locator('#finder-shelf-list li')).to_have_count(2)
            changed = assert_shelf_export(page, records)
            assert changed != content and '## ' + records[identifiers[1]]['title'] + '\n' not in changed
            last = page.locator(f'[data-finder-remove="{identifiers[2]}"]')
            last.focus(); page.keyboard.press('Enter')
            expect(page.locator(f'[data-finder-remove="{identifiers[0]}"]')).to_be_focused()
            page.keyboard.press('Enter')
            expect(page.locator('#finder-shelf')).not_to_be_visible()
            expect(search).to_be_focused()
            expect(page.locator('#finder-shelf-text')).to_have_value('')
            assert page.locator('#finder-shelf-download').get_attribute('href') is None
            assert page.evaluate('__studyTest.created.every(url => __studyTest.revoked.includes(url))')
            assert_shelf_private(context, page, requests, initial_requests, initial_url)
        finally:
            context.close()

    # The capacity boundary is announced beside the corrective action and never
    # truncates a list. Keyboard focus moves to the visible Remove control.
    context, page, requests = shelf_page(browser, origin, errors, 320)
    try:
        initial_requests, initial_url = list(requests), page.url
        cards = page.locator('[data-finder-card]:visible').all()
        records = {card.get_attribute('data-id'): shelf_record(page, card.get_attribute('data-id')) for card in cards}
        for card in cards:
            card.locator('.finder-save').click()
        expect(page.locator('#finder-shelf-list li')).to_have_count(12)
        before = assert_shelf_export(page, records)
        page.locator('#finder-more').click()
        overflow = page.locator('[data-finder-card]:visible').nth(12).locator('.finder-save')
        overflow.click()
        expect(page.locator('.finder-shelf-remove').first).to_be_focused()
        expect(overflow).to_have_attribute('aria-pressed', 'false')
        expect(page.locator('#finder-shelf-count')).to_contain_text('12 of 12')
        expect(page.locator('#finder-shelf-count')).to_contain_text('Remove an item below')
        expect(page.locator('#finder-shelf-status')).to_have_text('')
        expect(page.locator('#finder-shelf-list li')).to_have_count(12)
        expect(page.locator('#finder-shelf-text')).to_have_value(before)
        retained_url = page.locator('#finder-shelf-download').get_attribute('href')
        page.locator('.finder-shelf-remove').first.click()
        overflow.click()
        expect(overflow).to_have_attribute('aria-pressed', 'true')
        expect(page.locator('#finder-shelf-list li')).to_have_count(12)
        assert page.locator('#finder-shelf-download').get_attribute('href') != retained_url
        assert retained_url in page.evaluate('__studyTest.revoked')
        page.locator('#finder-shelf-clear').click()
        expect(page.locator('#finder-search')).to_be_focused()
        expect(page.locator('#finder-shelf')).not_to_be_visible()
        assert page.locator('[data-finder-card] .finder-save[aria-pressed="true"]').count() == 0
        assert_shelf_private(context, page, requests, initial_requests, initial_url)
    finally:
        context.close()

    for clipboard in ('missing', 'reject'):
        context, page, requests = shelf_page(browser, origin, errors, 320)
        try:
            initial_requests, initial_url = list(requests), page.url
            record = add_shelf_card(page, 'poker-reading-preflop-charts', 'pre-flop')
            content = assert_shelf_export(page, {record['id']: record})
            page.evaluate('mode => __studyTest.setClipboard(mode)', clipboard)
            page.locator('#finder-shelf-copy').click()
            assert_manual_copy(page, content)
            assert page.evaluate('__studyTest.writes') == ([] if clipboard == 'missing' else [content])
            page.add_style_tag(content='* {line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important;} p {margin-bottom:2em!important;}')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), ('manual copy spacing', clipboard)
            assert_shelf_private(context, page, requests, initial_requests, initial_url)
        finally:
            context.close()

    # Each download API can be absent or throw both before the first selection
    # and while replacing a previously working download. All failures preserve
    # search, selected entries, complete copy text and the triggering focus.
    for failure in ('blob-missing', 'blob-throws', 'url-missing', 'url-throws'):
        for replacement in (False, True):
            context, page, requests = shelf_page(browser, origin, errors, 320)
            try:
                initial_requests, initial_url = list(requests), page.url
                records = {}
                previous_url = None
                if replacement:
                    record = add_shelf_card(page, 'poker-reading-preflop-charts', 'pre-flop')
                    records[record['id']] = record
                    previous_url = page.locator('#finder-shelf-download').get_attribute('href')
                    assert previous_url.startswith('blob:')
                page.evaluate('mode => __studyTest.setFailure(mode)', failure)
                record = add_shelf_card(page, 'external-stars-tool-policy')
                records[record['id']] = record
                expect(page.locator('#finder-shelf-download')).not_to_be_visible()
                assert page.locator('#finder-shelf-download').get_attribute('href') is None
                expect(page.locator('#finder-shelf-status')).to_contain_text('download is unavailable')
                expect(page.locator('#finder-shelf-preview')).to_have_attribute('open', '')
                content = assert_shelf_export(page, records, download=False)
                if previous_url:
                    assert previous_url in page.evaluate('__studyTest.revoked')
                search = page.locator('#finder-search')
                search.fill('PLO8'); search.press('Enter')
                expect(page.locator('[data-id="external-omaha-eight-rules"]')).to_be_visible()
                expect(page.locator('#finder-shelf-text')).to_have_value(content)
                page.locator('#finder-shelf-copy').click()
                expect(page.locator('#finder-shelf-status')).to_contain_text('Study list copied')
                assert page.evaluate('__studyTest.writes') == [content]
                page.evaluate('__studyTest.setClipboard("missing")')
                page.locator('#finder-shelf-copy').click()
                assert_manual_copy(page, content)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (failure, replacement)
                page.evaluate('__studyTest.setFailure("")')
                record = add_shelf_card(page, 'term-big-blind', 'what does BB mean')
                records[record['id']] = record
                expect(page.locator('#finder-shelf-download')).to_be_visible()
                recovered = assert_shelf_export(page, records)
                assert recovered != content
                assert_shelf_private(context, page, requests, initial_requests, initial_url)
            finally:
                context.close()

    # Settling an old clipboard promise must not change a newer list or take
    # focus from the action the reader has already chosen.
    for outcome in ('resolve', 'reject'):
        for mutation in ('remove', 'clear'):
            context, page, requests = shelf_page(browser, origin, errors)
            try:
                initial_requests, initial_url = list(requests), page.url
                records = {}
                for identifier in ('poker-reading-preflop-charts', 'external-stars-tool-policy'):
                    record = add_shelf_card(page, identifier)
                    records[identifier] = record
                copied = assert_shelf_export(page, records)
                page.evaluate('__studyTest.setClipboard("pending")')
                page.locator('#finder-shelf-copy').click()
                assert page.evaluate('__studyTest.writes') == [copied]
                if mutation == 'remove':
                    page.locator('.finder-shelf-remove').first.click()
                    current = page.locator('#finder-shelf-text').input_value()
                    assert current != copied
                    focus = page.locator('.finder-shelf-remove').first
                else:
                    page.locator('#finder-shelf-clear').click()
                    current = ''
                    focus = page.locator('#finder-search')
                status = page.locator('#finder-shelf-status').text_content()
                page.evaluate("async outcome => { const pending = __studyTest.pending.shift(); pending[outcome](outcome === 'reject' ? new Error('Late test rejection') : undefined); await Promise.resolve(); }", outcome)
                expect(focus).to_be_focused()
                expect(page.locator('#finder-shelf-status')).to_have_text(status)
                expect(page.locator('#finder-shelf-text')).to_have_value(current)
                assert not page.locator('#finder-shelf-preview').evaluate('details => details.open')
                assert_shelf_private(context, page, requests, initial_requests, initial_url)
            finally:
                context.close()

    # Back/forward cache retains its working link. A real departure releases it.
    context, page, requests = shelf_page(browser, origin, errors)
    try:
        add_shelf_card(page, 'poker-reading-preflop-charts', 'pre-flop')
        url = page.locator('#finder-shelf-download').get_attribute('href')
        page.evaluate('dispatchEvent(new PageTransitionEvent("pagehide", {persisted:true}))')
        assert url not in page.evaluate('__studyTest.revoked')
        expect(page.locator('#finder-shelf-download')).to_have_attribute('href', url)
        page.evaluate('dispatchEvent(new PageTransitionEvent("pageshow", {persisted:true}))')
        expect(page.locator('#finder-shelf-download')).to_be_visible()
        page.evaluate('dispatchEvent(new PageTransitionEvent("pagehide", {persisted:false}))')
        assert page.evaluate('__studyTest.revoked') == [url]
        assert page.locator('#finder-shelf-download').get_attribute('href') is None
        page.reload()
        expect(page.locator('#finder-shelf')).not_to_be_visible()
        expect(page.locator('#finder-shelf-text')).to_have_value('')
        assert page.locator('[data-finder-card] .finder-save[aria-pressed="true"]').count() == 0
    finally:
        context.close()
    study_copy_focus_browser(browser, origin, errors)

def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    dest=Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if dest: dest.mkdir(parents=True,exist_ok=True)
    errors=[]
    with sync_playwright() as pw:
        opts={'headless':True}
        if os.environ.get('CHROMIUM_PATH'): opts['executable_path']=os.environ['CHROMIUM_PATH']
        browser=pw.chromium.launch(**opts)
        context=browser.new_context()
        context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        traffic=[];page.on('request',lambda r:traffic.append((r.method,r.url)))
        try:
            for width in (320,390,768,1280):
                page.set_viewport_size({'width':width,'height':900})
                for slug in ROUTES:
                    response=page.goto(origin+'/poker/'+slug+'/')
                    assert response and response.status==200
                    expect(page.locator('h1')).to_have_count(1)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(slug,width)
                    if slug=='find':
                        expect(page.locator('[data-finder-card]:visible')).to_have_count(12)
                        assert page.locator('#finder-search').bounding_box()['y'] < 900,('Search below first viewport',width)
                    page.add_style_tag(content='* {line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important;} p {margin-bottom:2em!important;}')
                    if not page.evaluate('document.documentElement.scrollWidth <= innerWidth'):
                        print('OVERFLOW', slug, width, page.evaluate('Array.from(document.querySelectorAll("main *")).filter(e=>e.getBoundingClientRect().right>innerWidth+1).map(e=>({tag:e.tagName,cls:e.className,id:e.id,right:e.getBoundingClientRect().right,width:e.getBoundingClientRect().width}))'), flush=True)
                        if dest: page.screenshot(path=str(dest/'poker-desk-overflow.png'),full_page=True)
                        raise AssertionError(('spacing',slug,width))
                    if dest and width in (390,1280) and slug in ('find','poker-math-reference'):
                        page.screenshot(path=str(dest/f'poker-desk-{slug}-{width}.png'),full_page=True)
            page.set_viewport_size({'width':1280,'height':900})
            page.goto(origin+'/poker/find/')
            search=page.locator('#finder-search')
            total=page.locator('[data-finder-card]').count()
            assert total > 200
            expect(page.locator('#finder-controls')).to_be_visible()
            page.wait_for_timeout(200)
            initial_traffic=list(traffic);initial_url=page.url
            # Real failed question, changed wording, spelling recovery and exact
            # short abbreviations use the same core as the declared benchmark.
            for question, target in [
                ('why did my two pair lose', '/poker/hand-rankings/'),
                ('TWO PAIRS LOST', '/poker/hand-rankings/'),
                ('pot ods', '/poker/glossary/#pot-odds'),
                ('kikcer poker', '/poker/glossary/#kicker'),
                ('first live tournment', '/poker/first-live-tournament/'),
                ('what does BB mean', '/poker/glossary/#big-blind'),
                ('what is ICM', '/poker/tournament-equity/'),
                ('prize equity', '/poker/tournament-equity/'),
                ('tournament equity', '/poker/tournament-equity/')]:
                search.fill(question);search.press('Enter')
                first=page.locator('[data-finder-card]:visible').first
                expect(first.locator('h3 a')).to_have_attribute('href',target)
                if target=='/poker/hand-rankings/':
                    expect(first.locator('.finder-jump a')).to_have_attribute('href',target+'#ties')
                    expect(first.locator('.finder-excerpt')).to_contain_text('Two pair compares the higher pair')
                if target=='/poker/tournament-equity/':
                    expect(first.locator('h3 a')).to_have_text('When more chips are not enough.')
                    expect(first.locator('.finder-excerpt')).to_be_visible()
            search.fill('two pair football');search.press('Enter')
            expect(page.locator('#finder-empty')).to_be_visible()
            page.locator('#finder-reset').click()
            # Live typing and input-method composition retain the editor. The
            # legacy 229 boundary must not submit a partial query.
            search.fill('pot odds')
            expect(search).to_be_focused()
            prior_count=page.locator('#finder-count').inner_text()
            search.evaluate("x=>{x.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true}));x.value='PLO8';x.dispatchEvent(new InputEvent('input',{bubbles:true,isComposing:true}));}")
            for flags in [{'isComposing':True,'keyCode':13},{'isComposing':False,'keyCode':229}]:
                allowed=search.evaluate("(x,flags)=>x.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true,cancelable:true,...flags}))",flags)
                assert allowed,'Composition Enter must retain its native default'
                expect(search).to_be_focused()
            page.wait_for_timeout(160)
            expect(page.locator('#finder-count')).to_have_text(prior_count)
            search.evaluate("x=>x.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true}))")
            expect(page.locator('[data-id="external-omaha-eight-rules"]')).to_be_visible()
            expect(search).to_be_focused()
            # Known glossary answer with no unrelated source-type results.
            page.locator('#finder-kind').select_option('glossary');search.fill('BB');search.press('Enter')
            expect(page.locator('[data-id="term-big-blind"]')).to_be_visible()
            assert page.locator('[data-finder-card]:visible:not([data-kind="glossary"])').count()==0
            assert page.evaluate('document.activeElement.id')=='finder-results-heading'
            assert page.locator('#finder-results-heading').evaluate('h=>h.getBoundingClientRect().top>=document.querySelector(".site-header").getBoundingClientRect().bottom+4')
            page.locator('#finder-reset').click()
            search.fill('what is ICM?');search.press('Enter')
            expect(page.locator('[data-id="poker-tournament-equity"]')).to_be_visible()
            page.locator('#finder-kind').select_option('resource');page.locator('#finder-free').check()
            assert page.locator('[data-finder-card]:visible:not([data-free="true"])').count()==0
            assert page.locator('[data-finder-card]:visible:not([data-kind="resource"])').count()==0
            page.locator('#finder-reset').click()
            search.fill('PLO8');search.press('Enter')
            expect(page.locator('[data-id="external-omaha-eight-rules"]')).to_be_visible()
            page.locator('#finder-reset').click()
            search.fill('pre-flop');search.press('Enter')
            expect(page.locator('[data-id="poker-reading-preflop-charts"]')).to_be_visible()
            # Literal hostile text must never create an element, script or request.
            search.fill('<img src=x onerror="window.finderInjected=1">');search.press('Enter')
            expect(page.locator('#finder-empty')).to_be_visible()
            assert page.evaluate('window.finderInjected === undefined')
            assert page.locator('#finder-results img').count()==0
            expect(page.locator('section[aria-labelledby="finder-support"] a').first).to_be_visible()
            search.focus();search.press('Escape')
            expect(search).to_have_value('')
            assert page.evaluate('document.activeElement.id')=='finder-search'
            expect(page.locator('[data-finder-card]:visible')).to_have_count(12)
            page.locator('#finder-more').click()
            expect(page.locator('[data-finder-card]:visible')).to_have_count(24)
            assert page.evaluate('document.activeElement.matches("[data-finder-card]")')
            # Printing expands all matches, then restores the user's page size.
            page.evaluate('dispatchEvent(new Event("beforeprint"))')
            expect(page.locator('[data-finder-card]:visible')).to_have_count(total)
            page.evaluate('dispatchEvent(new Event("afterprint"))')
            expect(page.locator('[data-finder-card]:visible')).to_have_count(24)
            page.locator('[data-finder-example="fair play"]').click()
            expect(page.locator('[data-id="poker-poker-rules-and-fair-play"]')).to_be_visible()
            assert traffic==initial_traffic,('Search generated traffic',traffic[len(initial_traffic):])
            assert page.url==initial_url
            assert context.cookies()==[]
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
            # Every original source appears in the unfiltered search and leads to its listing.
            page.locator('#finder-reset').click()
            search.fill('PokerStars third party');search.press('Enter')
            expect(page.locator('[data-id="external-stars-tool-policy"]')).to_be_visible()
            page.locator('[data-id="external-stars-tool-policy"] a[href^="/poker/resources/#"]').click()
            expect(page.locator('#resource-stars-tool-policy')).to_be_visible()
            # All nine new answer panels work with keyboard-only disclosure.
            for slug in ROUTES[1:]:
                page.goto(origin+'/poker/'+slug+'/')
                expect(page.locator('details.viewer-question')).to_have_count(3)
                for panel in page.locator('details.viewer-question').all():
                    expect(panel.locator('div')).not_to_be_visible()
                    panel.locator('summary').focus();page.keyboard.press('Enter')
                    expect(panel.locator('div')).to_be_visible()
                    page.keyboard.press('Enter');expect(panel.locator('div')).not_to_be_visible()
            response=context.request.get(origin+'/downloads/poker-math-reference.md')
            assert response.ok and response.body()==(ROOT/'downloads/poker-math-reference.md').read_bytes()
            study_list_browser(browser, origin, errors, dest)
            for mode in ('no-js','blocked-script'):
                offline=browser.new_context(java_script_enabled=mode!='no-js')
                offline.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
                if mode=='blocked-script':offline.route('**/poker-finder.js*',lambda r:r.abort())
                p=offline.new_page();p.goto(origin+'/poker/find/')
                expect(p.locator('#finder-controls')).not_to_be_visible()
                expect(p.locator('[data-finder-card]:visible')).to_have_count(total)
                expect(p.locator('#finder-more')).not_to_be_visible()
                expect(p.locator('#finder-shelf')).not_to_be_visible()
                assert p.locator('.finder-save:visible, .finder-shelf-remove:visible, #finder-shelf-copy:visible, #finder-shelf-download:visible').count()==0
                offline.close()
            if os.environ.get('AXE_PATH'):
                for slug in ROUTES:
                    page.goto(origin+'/poker/'+slug+'/')
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    results=page.evaluate('async () => await axe.run(document, {runOnly: {type:"tag",values:["wcag2a","wcag2aa","wcag21a","wcag21aa"]}})')
                    assert not results['violations'],(slug,results['violations'])
            assert not errors,errors
        finally:
            browser.close();server.shutdown();server.server_close()
    print(f'PASS: {total} finder entries; four routes at four widths; nine keyboard answers; synonyms, type/free filters, zero results, XSS text, pagination, print restoration, no search traffic/storage/URL writes, no-JS and blocked-script fallbacks, exact downloads; study-list export provenance, filtered removal and focus, 12-item limit, clipboard success/fallback/races, eight Blob/URL failure paths, object URL cleanup and reload reset.')
if __name__=='__main__':main()
