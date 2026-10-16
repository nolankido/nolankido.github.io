"""Private course progress: real downloads, storage consent, import and failure recovery."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from time import perf_counter
from urllib.parse import urlsplit
import copy
import json
import os
import re

from playwright.sync_api import sync_playwright, expect
from field_guide_browser import QuietHandler, ROOT
from learning_path_browser import SPACING


ROUTE = '/poker/study/'
KEY = 'nolan-kido:poker-foundations:progress:v1'
LESSONS = ('first-decisions', 'starting-hand-decisions', 'first-flop-decisions',
           'turn-and-river-decisions', 'ranges-for-beginners', 'betting-with-a-purpose')
STATES = ('not-started', 'working', 'practiced', 'revisit')
PRACTICE = dict(zip(LESSONS, ('one', 'two', 'three', 'four', 'five', 'six')))
NEXT = ('foundations', 'checkpoint') + tuple(value for lesson in LESSONS for value in ('read:' + lesson, 'practice:' + lesson))

# Retain real browser storage, Blob URLs and File reads. Only explicit failure
# cases are replaced, and all clipboard calls stay in this isolated test context.
HOOKS = r"""(() => {
  const storage = window.localStorage;
  const descriptor = Object.getOwnPropertyDescriptor(window, 'localStorage');
  const nativeGet = Storage.prototype.getItem;
  const nativeSet = Storage.prototype.setItem;
  const nativeRemove = Storage.prototype.removeItem;
  const nativeClear = Storage.prototype.clear;
  const nativeAdd = window.addEventListener;
  const nativeText = File.prototype.text;
  const nativeBlob = window.Blob;
  const nativeCreate = URL.createObjectURL.bind(URL);
  const nativeRevoke = URL.revokeObjectURL.bind(URL);
  const state = window.__progressTest = {
    storageFault: '', exportFault: '', calls: [], created: [], revoked: [], clipboard: [],
    holdStorage: false, heldStorage: [], holdReads: false, reads: [], readCount: 0, finishedReads: 0
  };
  state.get = key => nativeGet.call(storage, key);
  state.put = (key, value) => nativeSet.call(storage, key, value);
  state.remove = key => nativeRemove.call(storage, key);
  state.keys = () => Object.keys(storage);
  Object.defineProperty(window, 'localStorage', {configurable: true, get() {
    if (state.storageFault === 'access') throw new DOMException('Test storage blocked', 'SecurityError');
    return descriptor.get.call(window);
  }});
  Storage.prototype.getItem = function (key) {
    state.calls.push({op: 'get', key: String(key), local: this === storage});
    if (state.storageFault === 'get') throw new DOMException('Test read blocked', 'SecurityError');
    return nativeGet.call(this, key);
  };
  Storage.prototype.setItem = function (key, value) {
    state.calls.push({op: 'set', key: String(key), value: String(value), local: this === storage});
    if (state.storageFault === 'set') throw new DOMException('Test write blocked', 'QuotaExceededError');
    return nativeSet.call(this, key, value);
  };
  Storage.prototype.removeItem = function (key) {
    state.calls.push({op: 'remove', key: String(key), local: this === storage});
    if (state.storageFault === 'remove') throw new DOMException('Test removal blocked', 'SecurityError');
    return nativeRemove.call(this, key);
  };
  Storage.prototype.clear = function () {
    state.calls.push({op: 'clear', local: this === storage});
    return nativeClear.call(this);
  };
  window.addEventListener = function (type, listener, options) {
    if (type !== 'storage') return nativeAdd.call(this, type, listener, options);
    return nativeAdd.call(this, type, event => {
      const deliver = () => typeof listener === 'function' ? listener.call(window, event) : listener.handleEvent(event);
      if (state.holdStorage) state.heldStorage.push(deliver); else deliver();
    }, options);
  };
  state.deliverStorage = () => { for (const deliver of state.heldStorage.splice(0)) deliver(); };
  File.prototype.text = function () {
    state.readCount += 1;
    if (!state.holdReads) return nativeText.call(this).then(text => { state.finishedReads += 1; return text; });
    return new Promise((resolve, reject) => state.reads.push({file: this, resolve, reject}));
  };
  state.finishRead = async (index, reject = false) => {
    const pending = state.reads[index];
    state.finishedReads += 1;
    if (reject) pending.reject(new Error('Test file read rejected'));
    else pending.resolve(await nativeText.call(pending.file));
    await Promise.resolve();
  };
  const create = blob => {
    if (state.exportFault === 'url-throws') throw new Error('Test URL creation failed');
    const url = nativeCreate(blob); state.created.push(url); return url;
  };
  URL.revokeObjectURL = url => { state.revoked.push(url); nativeRevoke(url); };
  state.setExportFault = fault => {
    state.exportFault = fault;
    window.Blob = fault === 'blob-missing' ? undefined : fault === 'blob-throws'
      ? function () { throw new Error('Test Blob creation failed'); } : nativeBlob;
    URL.createObjectURL = fault === 'url-missing' ? undefined : create;
  };
  state.setExportFault('');
  Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {
    writeText: async text => { state.clipboard.push(text); }
  }});
})();"""


def enter(page, locator):
    locator.scroll_into_view_if_needed()
    locator.focus()
    expect(locator).to_be_focused()
    page.keyboard.press('Enter')


def watch_errors(page, errors):
    page.on('pageerror', lambda error: errors.append({'url': page.url, 'stack': error.stack}))


def local_context(browser, errors, width=1280, init='', scripting=True):
    context = browser.new_context(accept_downloads=True, java_script_enabled=scripting,
                                  viewport={'width': width, 'height': 950}, reduced_motion='reduce')
    context.route('**/*', lambda route: route.continue_() if urlsplit(route.request.url).hostname == '127.0.0.1' else route.abort())
    if scripting:
        # New blank tabs have opaque origins and no web storage. The harness is
        # only for our served pages, and must not throw before they load.
        context.add_init_script("if (location.protocol === 'http:' && location.hostname === '127.0.0.1') {\n" + HOOKS + '\n' + init + '\n}')
    page = context.new_page()
    watch_errors(page, errors)
    return context, page


def load(page, origin):
    response = page.goto(origin + ROUTE)
    assert response and response.status == 200
    page.wait_for_load_state('networkidle')
    return page


def json_text(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def reflow(page, label):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), label


def open_details(page, identifier):
    details = page.locator(identifier)
    if not details.evaluate('element => element.open'):
        enter(page, details.locator(':scope > summary'))


def progress_page(browser, origin, errors, width=1280, init=''):
    context, page = local_context(browser, errors, width, init)
    load(page, origin)
    expect(page.locator('#course-progress')).to_be_visible()
    expect(page.locator('#progress-status-' + LESSONS[0])).to_be_visible()
    return context, page


def state(page):
    value = json.loads(page.locator('#progress-export-text').input_value())
    assert set(value) == {'format', 'version', 'course', 'revision', 'next', 'lessons'}, value
    assert value['format'] == 'nolan-kido-poker-progress' and value['version'] == 1
    assert value['course'] == 'poker-foundations'
    assert re.fullmatch('[0-9a-f]{64}', value['revision'])
    assert value['next'] in NEXT
    assert set(value['lessons']) == set(LESSONS)
    assert all(mark in STATES for mark in value['lessons'].values())
    return value


def expected_url(token):
    if token == 'foundations':
        return '/poker/free-poker-learning-path/'
    if token == 'checkpoint':
        return '/poker/beginner-checkpoint/'
    kind, lesson = token.split(':', 1)
    return '/poker/' + lesson + '/#course-first-pass-title' if kind == 'read' else '/poker/beginner-checkpoint/#situation-' + PRACTICE[lesson]


def assert_state(page, expected):
    assert state(page) == expected
    for lesson in LESSONS:
        expect(page.locator('#progress-status-' + lesson)).to_have_value(expected['lessons'][lesson])
    expect(page.locator('#progress-next')).to_have_value(expected['next'])
    expect(page.locator('#progress-resume')).to_have_attribute('href', expected_url(expected['next']))


def mark(page, lesson, value):
    page.locator('#progress-status-' + lesson).select_option(value)
    expect(page.locator('#progress-status-' + lesson)).to_have_value(value)


def remember(page, enabled=True):
    open_details(page, '#progress-storage')
    box = page.locator('#progress-remember')
    if box.is_checked() != enabled:
        box.focus()
        page.keyboard.press('Space')


def stored(page):
    text = page.evaluate('key => __progressTest.get(key)', KEY)
    return json.loads(text) if text is not None else None


def reset(page):
    open_details(page, '#progress-storage')
    enter(page, page.locator('#progress-reset'))


def request_watch(page):
    requests = []
    page.on('request', lambda request: requests.append((request.method, request.url)))
    return requests, page.url


def private_actions(context, page, observed, saved=False):
    requests, url = observed
    assert requests == [], ('Progress action made a request', requests)
    assert page.url == url
    assert context.cookies() == []
    assert page.evaluate('sessionStorage.length') == 0
    calls = page.evaluate('__progressTest.calls')
    assert all(call['local'] and call.get('key') == KEY for call in calls), calls
    assert all(call['op'] != 'clear' for call in calls)
    if not saved:
        assert all(call['op'] != 'set' for call in calls), calls
        assert page.evaluate('__progressTest.keys()') == []


def export_json(page, download=True):
    open_details(page, '#progress-transfer')
    content = page.locator('#progress-export-text').input_value()
    assert content == json.dumps(state(page), ensure_ascii=False, indent=2) + '\n'
    if download:
        with page.expect_download() as pending:
            enter(page, page.locator('#progress-download'))
        item = pending.value
        assert item.suggested_filename == 'poker-foundations-progress.json'
        assert item.failure() is None
        assert Path(item.path()).read_text(encoding='utf-8') == content
    return content


def select_export(page, content):
    enter(page, page.locator('#progress-select-export'))
    text = page.locator('#progress-export-text')
    expect(text).to_be_focused()
    expect(text).to_have_value(content)
    expect(text).to_have_attribute('readonly', '')
    assert text.evaluate('field => field.selectionStart === 0 && field.selectionEnd === field.value.length')


def import_file(page, content, name='poker-progress.json', pending=False):
    open_details(page, '#progress-transfer')
    data = content.encode('utf-8') if isinstance(content, str) else content
    completed = page.evaluate('__progressTest.finishedReads')
    calls = page.evaluate('__progressTest.readCount')
    page.locator('#progress-import-file').set_input_files({'name': name, 'mimeType': 'application/json', 'buffer': data})
    if not pending and len(data) <= 8192:
        page.wait_for_function('completed => __progressTest.finishedReads > completed', arg=completed)
    if len(data) > 8192:
        assert page.evaluate('__progressTest.readCount') == calls, 'Oversized files must be rejected before reading'


def paste_import(page, content):
    open_details(page, '#progress-transfer')
    page.locator('#progress-import-text').fill(content)
    enter(page, page.locator('#progress-review-import'))


def apply_import(page):
    expect(page.locator('#progress-import-preview')).to_be_visible()
    enter(page, page.locator('#progress-apply-import'))
    expect(page.locator('#progress-import-preview')).not_to_be_visible()


def invalid_candidates(base):
    values = [('malformed', '{not JSON'), ('null', 'null'), ('array', '[]')]
    changes = [
        ('unsupported format', 'format', 'unrelated-progress'),
        ('unsupported version', 'version', 2), ('wrong version type', 'version', True),
        ('unsupported course', 'course', 'other-course'),
        ('different revision', 'revision', '0' * 64 if base['revision'] != '0' * 64 else '1' * 64),
        ('malformed revision', 'revision', '../current'),
        ('unknown next token', 'next', 'read:unknown-lesson'),
        ('arbitrary HTTPS URL', 'next', 'https://example.invalid/progress-exfiltration'),
        ('script URL', 'next', 'javascript:window.progressInjected=1'),
        ('HTML payload', 'next', '<img src="https://example.invalid/pixel" onerror="window.progressInjected=1">'),
        ('unknown property', 'notes', 'private answer should never be saved'),
        ('prototype property', '__proto__', {'polluted': True}),
        ('constructor property', 'constructor', {'prototype': {'polluted': True}}),
        ('null lesson map', 'lessons', None),
    ]
    for label, key, value in changes:
        candidate = copy.deepcopy(base); candidate[key] = value
        values.append((label, json_text(candidate)))
    for label, mutate in [
        ('unknown lesson', lambda lessons: lessons.update({'unlisted-lesson': 'working'})),
        ('missing lesson', lambda lessons: lessons.pop(LESSONS[-1])),
        ('invalid status', lambda lessons: lessons.update({LESSONS[0]: 'mastered'})),
        ('wrong status type', lambda lessons: lessons.update({LESSONS[0]: {'answer': 42}})),
        ('lesson prototype', lambda lessons: lessons.update({'__proto__': 'working'})),
    ]:
        candidate = copy.deepcopy(base); mutate(candidate['lessons'])
        values.append((label, json_text(candidate)))
    candidate = copy.deepcopy(base); del candidate['next']
    values.append(('missing property', json_text(candidate)))
    values.append(('oversized file', json_text(base) + ' ' * 8193))
    return values


def check_ui(browser, origin, errors, report, shots):
    for width in (320, 1280):
        context, page = progress_page(browser, origin, errors, width)
        try:
            observed = request_watch(page)
            baseline = state(page)
            assert all(value == 'not-started' for value in baseline['lessons'].values())
            expect(page.locator('#progress-remember')).not_to_be_checked()
            assert stored(page) is None
            assert all(call['op'] == 'get' for call in page.evaluate('__progressTest.calls'))
            assert page.locator('#course-progress select').count() == 7
            assert page.locator('#course-progress input').evaluate_all("items => items.every(item => ['checkbox', 'file'].includes(item.type))")
            assert page.locator('#course-progress textarea:not([readonly])').evaluate_all("items => items.length === 1 && items[0].id === 'progress-import-text'")
            for lesson in LESSONS:
                control = page.locator('#progress-status-' + lesson)
                assert control.locator('option').evaluate_all('items => items.map(item => item.value)') == list(STATES)
                assert page.locator(f'label[for="progress-status-{lesson}"]').count() == 1
                assert page.locator('#course-progress a[href="' + expected_url('read:' + lesson) + '"]').count() >= 1
                assert page.locator('#course-progress a[href="' + expected_url('practice:' + lesson) + '"]').count() >= 1
            assert set(page.locator('#progress-next option').evaluate_all('items => items.map(item => item.value)')) == set(NEXT)
            for identifier in ('progress-status', 'progress-storage-status', 'progress-transfer-status'):
                expect(page.locator('#' + identifier)).to_have_attribute('role', 'status')
                expect(page.locator('#' + identifier)).to_have_attribute('aria-live', 'polite')
                expect(page.locator('#' + identifier)).to_have_attribute('aria-atomic', 'true')
            # Change the first status with the actual native keyboard control.
            first = page.locator('#progress-status-' + LESSONS[0])
            first.focus(); page.keyboard.press('Home'); page.keyboard.press('ArrowDown'); page.keyboard.press('Enter')
            expect(first).to_have_value('working')
            expect(first).to_be_focused()
            for index, lesson in enumerate(LESSONS):
                mark(page, lesson, ('working', 'practiced', 'revisit')[index % 3])
            expected = copy.deepcopy(baseline)
            expected['lessons'] = {lesson: ('working', 'practiced', 'revisit')[index % 3] for index, lesson in enumerate(LESSONS)}
            expect(page.locator('#progress-revisit-list > li')).to_have_count(2)
            expect(page.locator('#progress-revisit-empty')).not_to_be_visible()
            for lesson in (LESSONS[2], LESSONS[5]):
                assert page.locator('#progress-revisit-list a[href="' + expected_url('read:' + lesson) + '"]').count() >= 1
            for token in NEXT:
                page.locator('#progress-next').select_option(token)
                expect(page.locator('#progress-resume')).to_have_attribute('href', expected_url(token))
            expected['next'] = NEXT[-1]
            assert_state(page, expected)
            content = export_json(page)
            select_export(page, content)
            assert page.evaluate('__progressTest.clipboard') == []
            reflow(page, ('progress', width))
            if shots:
                page.locator('#course-progress').screenshot(path=str(shots / f'poker-progress-{width}.png'))
            page.add_style_tag(content=SPACING)
            reflow(page, ('progress text spacing', width))
            page.emulate_media(media='print')
            expect(page.locator('#course-progress')).to_be_visible()
            expect(page.locator('#progress-summary')).to_be_visible()
            expect(page.locator('#progress-resume')).to_be_visible()
            assert page.locator('[id^="progress-print-"]:visible').count() == 6
            assert page.locator('#course-progress select:visible, #course-progress input:visible, #course-progress textarea:visible, #course-progress button:visible').count() == 0
            page.emulate_media(media='screen')
            private_actions(context, page, observed)
            assert all(call['op'] == 'get' for call in page.evaluate('__progressTest.calls'))
            page.reload()
            assert_state(page, baseline)
            assert stored(page) is None
            report['layouts'] += 1
        finally:
            context.close()


def check_imports(browser, origin, errors, report):
    context, page = progress_page(browser, origin, errors)
    try:
        observed = request_watch(page)
        baseline = state(page)
        mark(page, LESSONS[0], 'working')
        before = state(page)
        candidate = copy.deepcopy(baseline)
        candidate['lessons'][LESSONS[2]] = 'revisit'
        candidate['lessons'][LESSONS[4]] = 'practiced'
        candidate['next'] = 'practice:' + LESSONS[2]
        import_file(page, json_text(candidate))
        expect(page.locator('#progress-import-preview')).to_be_visible()
        expect(page.locator('#progress-import-lessons > li')).to_have_count(6)
        assert_state(page, before)
        assert stored(page) is None
        enter(page, page.locator('#progress-cancel-import'))
        expect(page.locator('#progress-import-preview')).not_to_be_visible()
        assert_state(page, before)
        paste_import(page, json_text(candidate))
        expect(page.locator('#progress-import-preview')).to_be_visible()
        apply_import(page)
        assert_state(page, candidate)
        expect(page.locator('#progress-remember')).not_to_be_checked()
        assert stored(page) is None
        assert json.loads(export_json(page)) == candidate
        for label, content in invalid_candidates(candidate):
            previous = state(page)
            import_file(page, content)
            expect(page.locator('#progress-import-preview')).not_to_be_visible()
            assert_state(page, previous)
            expect(page.locator('#progress-transfer-status')).not_to_have_text('')
            assert stored(page) is None
            assert page.evaluate('window.progressInjected === undefined && Object.prototype.polluted === undefined'), label
            report['rejected_imports'] += 1
        # Size uses the complete file; valid JSON plus whitespace at the limit works.
        exact = json_text(candidate).encode()
        import_file(page, exact + b' ' * (8192 - len(exact)))
        expect(page.locator('#progress-import-preview')).to_be_visible()
        enter(page, page.locator('#progress-cancel-import'))
        paste_import(page, '{"answer":"private-import-marker"}')
        expect(page.locator('#progress-import-preview')).not_to_be_visible()
        assert_state(page, candidate)
        assert 'private-import-marker' not in export_json(page)
        private_actions(context, page, observed)
        report['import_flows'] += 1
    finally:
        context.close()


def check_navigation(browser, origin, errors, report):
    context, page = progress_page(browser, origin, errors)
    try:
        mark(page, LESSONS[1], 'revisit')
        before = state(page)
        for token in NEXT:
            page.locator('#progress-next').select_option(token)
            expected = state(page)
            link = page.locator('#progress-resume')
            expect(link).to_have_attribute('target', '_blank')
            assert 'noopener' in link.get_attribute('rel').split()
            expect(link).to_have_accessible_name(re.compile('opens in a new tab'))
            with page.expect_popup() as pending:
                enter(page, link)
            destination = pending.value
            watch_errors(destination, errors)
            destination.wait_for_load_state('load')
            expect(destination).to_have_url(origin + expected_url(token))
            fragment = urlsplit(expected_url(token)).fragment
            if fragment:
                expect(destination.locator('#' + fragment)).to_be_visible()
            if token == 'read:' + LESSONS[0]:
                answer = destination.locator('#course-lesson-answer')
                enter(destination, answer.locator('summary'))
                expect(answer.locator(':scope > div')).to_be_visible()
            if token == 'practice:' + LESSONS[0]:
                panel = destination.locator('#situation-one details').first
                if panel.count():
                    enter(destination, panel.locator('summary'))
            destination.close()
            assert_state(page, expected)
            assert state(page)['lessons'] == before['lessons'], 'Reading and answer reveals must not infer marks'
            assert stored(page) is None
            assert all(call['op'] != 'set' for call in page.evaluate('__progressTest.calls'))
            report['navigation'] += 1
    finally:
        context.close()


def check_storage(browser, origin, errors, report):
    context, page = progress_page(browser, origin, errors)
    try:
        baseline = state(page)
        mark(page, LESSONS[0], 'working')
        page.locator('#progress-next').select_option('practice:' + LESSONS[0])
        expected = state(page)
        assert stored(page) is None
        remember(page)
        expect(page.locator('#progress-remember')).to_be_checked()
        assert stored(page) == expected
        page.reload()
        page.wait_for_load_state('networkidle')
        assert_state(page, expected)
        expect(page.locator('#progress-remember')).to_be_checked()
        assert all(call['op'] != 'set' for call in page.evaluate('__progressTest.calls')), 'Restore must not rewrite the record'
        observed = request_watch(page)
        mark(page, LESSONS[2], 'revisit')
        page.locator('#progress-next').select_option('checkpoint')
        expected = state(page)
        assert stored(page) == expected
        writes = len([call for call in page.evaluate('__progressTest.calls') if call['op'] == 'set'])
        import_file(page, json_text({**expected, 'answer': 'must not be saved'}))
        expect(page.locator('#progress-import-preview')).not_to_be_visible()
        assert_state(page, expected)
        assert stored(page) == expected
        expect(page.locator('#progress-remember')).to_be_checked()
        assert len([call for call in page.evaluate('__progressTest.calls') if call['op'] == 'set']) == writes
        candidate = copy.deepcopy(expected)
        candidate['lessons'][LESSONS[3]] = 'practiced'
        import_file(page, json_text(candidate))
        assert stored(page) == expected
        apply_import(page)
        expect(page.locator('#progress-remember')).to_be_checked()
        assert stored(page) == candidate
        remember(page, False)
        expect(page.locator('#progress-remember')).not_to_be_checked()
        assert stored(page) is None
        assert_state(page, candidate)
        writes = len([call for call in page.evaluate('__progressTest.calls') if call['op'] == 'set'])
        mark(page, LESSONS[5], 'working')
        assert len([call for call in page.evaluate('__progressTest.calls') if call['op'] == 'set']) == writes
        remember(page)
        page.evaluate('__progressTest.put("unrelated-browser-record", "keep this")')
        reset(page)
        assert_state(page, baseline)
        expect(page.locator('#progress-remember')).not_to_be_checked()
        assert stored(page) is None
        assert page.evaluate('__progressTest.get("unrelated-browser-record")') == 'keep this'
        private_actions(context, page, observed, saved=True)
        report['storage'] += 1
    finally:
        context.close()

    # Invalid records remain untouched until the reader chooses removal.
    for label, raw in [('malformed', '{broken'),
                       ('old schema', json_text({**baseline, 'version': 2})),
                       ('old course', json_text({**baseline, 'revision': '0' * 64}))]:
        init = '__progressTest.put(' + json.dumps(KEY) + ', ' + json.dumps(raw) + ');'
        context, page = progress_page(browser, origin, errors, init=init)
        try:
            assert_state(page, baseline)
            expect(page.locator('#progress-remember')).not_to_be_checked()
            assert page.evaluate('key => __progressTest.get(key)', KEY) == raw, label
            assert all(call['op'] != 'set' for call in page.evaluate('__progressTest.calls'))
            mark(page, LESSONS[0], 'working')
            assert page.evaluate('key => __progressTest.get(key)', KEY) == raw
            open_details(page, '#progress-storage')
            expect(page.locator('#progress-storage-status')).not_to_have_text('')
            enter(page, page.locator('#progress-forget'))
            assert stored(page) is None
            assert state(page)['lessons'][LESSONS[0]] == 'working'
            report['storage'] += 1
        finally:
            context.close()

    for fault in ('access', 'get'):
        init = '__progressTest.put(' + json.dumps(KEY) + ', ' + json.dumps(json_text(expected)) + '); __progressTest.storageFault = ' + json.dumps(fault) + ';'
        context, page = progress_page(browser, origin, errors, 320, init=init)
        try:
            observed = request_watch(page)
            assert_state(page, baseline)
            expect(page.locator('#progress-remember')).not_to_be_checked()
            assert stored(page) == expected
            mark(page, LESSONS[4], 'working')
            current = state(page)
            export_json(page)
            assert stored(page) == expected
            page.evaluate('__progressTest.storageFault = ""')
            remember(page)
            expect(page.locator('#progress-remember')).to_be_checked()
            assert stored(page) == current
            page.evaluate('fault => __progressTest.storageFault = fault', fault)
            mark(page, LESSONS[5], 'working')
            latest = state(page)
            assert stored(page) == current
            expect(page.locator('#progress-remember')).not_to_be_checked()
            page.evaluate('__progressTest.storageFault = ""')
            remember(page)
            assert stored(page) == latest
            private_actions(context, page, observed, saved=True)
            report['storage'] += 1
        finally:
            context.close()

    # Quota/write errors preserve the current marks and permit explicit recovery.
    context, page = progress_page(browser, origin, errors)
    try:
        observed = request_watch(page)
        mark(page, LESSONS[0], 'working')
        page.evaluate('__progressTest.storageFault = "set"')
        remember(page)
        expect(page.locator('#progress-remember')).not_to_be_checked()
        expect(page.locator('#progress-storage-status')).not_to_have_text('')
        assert stored(page) is None
        export_json(page)
        page.evaluate('__progressTest.storageFault = ""')
        remember(page)
        previous = state(page)
        assert stored(page) == previous
        page.evaluate('__progressTest.storageFault = "set"')
        mark(page, LESSONS[1], 'revisit')
        current = state(page)
        assert current != previous and stored(page) == previous
        expect(page.locator('#progress-remember')).not_to_be_checked()
        page.evaluate('__progressTest.storageFault = ""')
        remember(page)
        assert stored(page) == current
        private_actions(context, page, observed, saved=True)
        report['storage'] += 1
    finally:
        context.close()

    for action in ('forget', 'reset'):
        context, page = progress_page(browser, origin, errors)
        try:
            observed = request_watch(page)
            mark(page, LESSONS[0], 'practiced')
            remember(page)
            previous = state(page)
            page.evaluate('__progressTest.put("unrelated-browser-record", "keep this"); __progressTest.storageFault = "remove"')
            if action == 'forget':
                enter(page, page.locator('#progress-forget'))
                assert_state(page, previous)
            else:
                reset(page)
                assert_state(page, baseline)
            expect(page.locator('#progress-remember')).not_to_be_checked()
            assert stored(page) == previous, 'Failed removal must not be reported as deletion'
            expect(page.locator('#progress-storage-status')).to_contain_text(re.compile('remain|return|could not|unable', re.I))
            mark(page, LESSONS[1], 'working')
            current = state(page)
            assert stored(page) == previous
            page.evaluate('__progressTest.storageFault = ""')
            enter(page, page.locator('#progress-forget'))
            assert stored(page) is None
            assert_state(page, current)
            assert page.evaluate('__progressTest.get("unrelated-browser-record")') == 'keep this'
            private_actions(context, page, observed, saved=True)
            report['storage'] += 1
        finally:
            context.close()


def check_cross_tab(browser, origin, errors, report):
    # A temporary desk belongs to this tab. Another tab's saved copy must not
    # replace or reset it, whether that copy is removed by the UI or site-data
    # clearing. Observe real browser storage events after the controller runs.
    for removal in ('forget', 'clear'):
        context, page = progress_page(browser, origin, errors)
        try:
            observed = request_watch(page)
            baseline = state(page)
            for lesson, value in zip(LESSONS, ('working', 'practiced', 'revisit', 'working', 'practiced', 'revisit')):
                mark(page, lesson, value)
            page.locator('#progress-next').select_option('practice:' + LESSONS[5])
            temporary = state(page)
            exported = export_json(page, download=False)
            pasted = json_text(baseline)
            page.locator('#progress-import-text').fill(pasted)
            expect(page.locator('#progress-remember')).not_to_be_checked()
            assert stored(page) is None
            page.evaluate("""() => {
              __progressTest.storageEvents = [];
              window.addEventListener('storage', event => __progressTest.storageEvents.push({
                key: event.key, oldValue: event.oldValue, newValue: event.newValue,
                local: event.storageArea === window.localStorage
              }));
            }""")

            companion = context.new_page()
            watch_errors(companion, errors)
            load(companion, origin)
            assert_state(companion, baseline)
            mark(companion, LESSONS[0], 'revisit')
            companion.locator('#progress-next').select_option('checkpoint')
            remember(companion)
            saved = state(companion)
            assert saved != temporary and stored(companion) == saved
            page.wait_for_function('__progressTest.storageEvents.length >= 1')
            events = page.evaluate('__progressTest.storageEvents')
            assert len(events) == 1 and events[0]['local'] and events[0]['key'] == KEY, events
            assert events[0]['oldValue'] is None and json.loads(events[0]['newValue']) == saved
            assert_state(page, temporary)
            expect(page.locator('#progress-export-text')).to_have_value(exported)
            expect(page.locator('#progress-import-text')).to_have_value(pasted)
            expect(page.locator('#progress-remember')).not_to_be_checked()
            assert stored(page) == saved, 'A temporary tab must not overwrite another tab\'s saved record'
            assert all(call['op'] == 'get' for call in page.evaluate('__progressTest.calls'))

            if removal == 'forget':
                enter(companion, companion.locator('#progress-forget'))
                expect(companion.locator('#progress-remember')).not_to_be_checked()
            else:
                # This is an isolated browser context with synthetic data only.
                companion.evaluate('localStorage.clear()')
            assert stored(companion) is None
            page.wait_for_function('__progressTest.storageEvents.length >= 2')
            events = page.evaluate('__progressTest.storageEvents')
            assert len(events) == 2 and events[1]['local'] and events[1]['newValue'] is None, events
            assert events[1]['key'] == (KEY if removal == 'forget' else None), events
            assert_state(page, temporary)
            expect(page.locator('#progress-export-text')).to_have_value(exported)
            expect(page.locator('#progress-import-text')).to_have_value(pasted)
            expect(page.locator('#progress-remember')).not_to_be_checked()
            assert stored(page) is None

            mark(page, LESSONS[0], 'practiced')
            temporary['lessons'][LESSONS[0]] = 'practiced'
            assert_state(page, temporary)
            expect(page.locator('#progress-import-text')).to_have_value(pasted)
            expect(page.locator('#progress-remember')).not_to_be_checked()
            assert stored(page) is None, 'Later temporary edits must not resurrect the removed saved copy'
            assert all(call['op'] == 'get' for call in page.evaluate('__progressTest.calls'))
            private_actions(context, page, observed)
            report['cross_tab'] += 1
        finally:
            context.close()

    for held, pending_read in ((False, False), (True, False), (False, True)):
        context, page = progress_page(browser, origin, errors)
        try:
            baseline = state(page)
            mark(page, LESSONS[0], 'practiced')
            remember(page)
            companion = context.new_page()
            watch_errors(companion, errors)
            load(companion, origin)
            expect(companion.locator('#progress-remember')).to_be_checked()
            assert_state(companion, state(page))
            if held:
                page.evaluate('__progressTest.holdStorage = true')
            if pending_read:
                candidate = copy.deepcopy(state(page)); candidate['lessons'][LESSONS[4]] = 'revisit'
                page.evaluate('__progressTest.holdReads = true')
                import_file(page, json_text(candidate), pending=True)
                assert page.evaluate('__progressTest.reads.length') == 1
            reset(companion)
            assert stored(companion) is None
            if held:
                page.locator('#progress-status-' + LESSONS[1]).select_option('working')
                expect(page.locator('#progress-remember')).not_to_be_checked()
                assert_state(page, baseline)
                assert stored(page) is None, 'A stale tab must not resurrect a deleted record'
                page.evaluate('__progressTest.holdStorage = false; __progressTest.deliverStorage()')
            else:
                expect(page.locator('#progress-remember')).not_to_be_checked()
                assert_state(page, baseline)
            mark(page, LESSONS[2], 'working')
            latest = state(page)
            assert stored(page) is None
            if pending_read:
                page.evaluate('() => __progressTest.finishRead(0)')
                expect(page.locator('#progress-import-preview')).not_to_be_visible()
                assert_state(page, latest)
                assert stored(page) is None
            report['cross_tab'] += 1
        finally:
            context.close()

    context, page = progress_page(browser, origin, errors)
    try:
        baseline = state(page)
        companion = context.new_page()
        watch_errors(companion, errors)
        load(companion, origin)
        for focused in ('progress-import-preview-title', 'progress-apply-import', 'progress-cancel-import', 'progress-next'):
            mark(page, LESSONS[0], 'working')
            remember(page)
            candidate = copy.deepcopy(baseline); candidate['lessons'][LESSONS[3]] = 'revisit'
            paste_import(page, json_text(candidate))
            expect(page.locator('#progress-import-preview')).to_be_visible()
            page.locator('#' + focused).focus()
            expect(page.locator('#' + focused)).to_be_focused()
            reset(companion)
            expect(page.locator('#progress-import-preview')).not_to_be_visible()
            target = 'progress-next' if focused == 'progress-next' else 'progress-review-import'
            expect(page.locator('#' + target)).to_be_focused()
            expect(page.locator('#' + target)).to_be_visible()
            assert_state(page, baseline)
            assert stored(page) is None
        report['cross_tab'] += 1
    finally:
        context.close()


def check_read_races(browser, origin, errors, report):
    for action in ('edit', 'reset', 'saving'):
        context, page = progress_page(browser, origin, errors)
        try:
            observed = request_watch(page)
            baseline = state(page)
            mark(page, LESSONS[0], 'working')
            candidate = copy.deepcopy(baseline)
            candidate['lessons'][LESSONS[5]] = 'practiced'
            candidate['next'] = 'practice:' + LESSONS[5]
            page.evaluate('__progressTest.holdReads = true')
            import_file(page, json_text(candidate), pending=True)
            assert page.evaluate('__progressTest.reads.length') == 1
            if action == 'edit':
                mark(page, LESSONS[2], 'revisit')
            elif action == 'reset':
                reset(page)
            else:
                remember(page)
            latest = state(page)
            focus = page.evaluate('document.activeElement.id')
            page.evaluate('() => __progressTest.finishRead(0)')
            assert_state(page, latest)
            expect(page.locator('#progress-import-preview')).not_to_be_visible()
            assert page.evaluate('document.activeElement.id') == focus
            assert stored(page) == (latest if action == 'saving' else None)
            private_actions(context, page, observed, saved=action == 'saving')
            report['read_races'] += 1
        finally:
            context.close()

    for outcome in ('resolve', 'reject'):
        context, page = progress_page(browser, origin, errors)
        try:
            observed = request_watch(page)
            baseline = state(page)
            older = copy.deepcopy(baseline); older['lessons'][LESSONS[0]] = 'practiced'
            newer = copy.deepcopy(baseline); newer['lessons'][LESSONS[4]] = 'revisit'
            newer['next'] = 'read:' + LESSONS[4]
            page.evaluate('__progressTest.holdReads = true')
            import_file(page, json_text(older), pending=True)
            import_file(page, json_text(newer), name='newer-progress.json', pending=True)
            assert page.evaluate('__progressTest.reads.length') == 2
            page.evaluate('() => __progressTest.finishRead(1)')
            expect(page.locator('#progress-import-preview')).to_be_visible()
            preview = page.locator('#progress-import-preview').inner_text()
            focus = page.evaluate('document.activeElement.id')
            page.evaluate('reject => __progressTest.finishRead(0, reject)', outcome == 'reject')
            expect(page.locator('#progress-import-preview')).to_have_text(preview, use_inner_text=True)
            assert page.evaluate('document.activeElement.id') == focus
            assert_state(page, baseline)
            apply_import(page)
            assert_state(page, newer)
            assert stored(page) is None
            private_actions(context, page, observed)
            report['read_races'] += 1
        finally:
            context.close()

    context, page = progress_page(browser, origin, errors)
    try:
        observed = request_watch(page)
        baseline = state(page)
        candidate = copy.deepcopy(baseline); candidate['lessons'][LESSONS[1]] = 'practiced'
        import_file(page, json_text(candidate))
        expect(page.locator('#progress-import-preview')).to_be_visible()
        mark(page, LESSONS[0], 'working')
        latest = state(page)
        expect(page.locator('#progress-import-preview')).not_to_be_visible()
        paste_import(page, json_text(candidate))
        expect(page.locator('#progress-import-preview')).to_be_visible()
        page.locator('#progress-import-text').fill(json_text(baseline))
        expect(page.locator('#progress-import-preview')).not_to_be_visible()
        assert_state(page, latest)
        page.evaluate('__progressTest.holdReads = true')
        import_file(page, json_text(candidate), pending=True)
        page.evaluate('() => __progressTest.finishRead(0, true)')
        expect(page.locator('#progress-import-preview')).not_to_be_visible()
        expect(page.locator('#progress-transfer-status')).not_to_have_text('')
        assert_state(page, latest)
        private_actions(context, page, observed)
        report['read_races'] += 1
    finally:
        context.close()


def check_export_recovery(browser, origin, errors, report):
    for fault in ('blob-missing', 'blob-throws', 'url-missing', 'url-throws'):
        for replacement in (False, True):
            init = '' if replacement else '__progressTest.setExportFault(' + json.dumps(fault) + ');'
            context, page = progress_page(browser, origin, errors, 320, init)
            try:
                observed = request_watch(page)
                previous = page.locator('#progress-download').get_attribute('href') if replacement else None
                if replacement:
                    assert previous and previous.startswith('blob:')
                    page.evaluate('fault => __progressTest.setExportFault(fault)', fault)
                mark(page, LESSONS[0], 'working')
                expect(page.locator('#progress-download')).not_to_be_visible()
                assert page.locator('#progress-download').get_attribute('href') is None
                if previous:
                    assert previous in page.evaluate('__progressTest.revoked')
                content = export_json(page, download=False)
                select_export(page, content)
                assert page.get_by_label('Complete progress file', exact=True).count() == 1
                candidate = state(page)
                candidate['lessons'][LESSONS[3]] = 'revisit'
                paste_import(page, json_text(candidate))
                apply_import(page)
                assert_state(page, candidate)
                assert stored(page) is None
                assert page.locator('#progress-download').get_attribute('href') is None
                reflow(page, ('export recovery', fault, replacement))
                page.evaluate('__progressTest.setExportFault("")')
                mark(page, LESSONS[1], 'practiced')
                recovered = export_json(page)
                assert recovered != content
                active = page.locator('#progress-download').get_attribute('href')
                objects = page.evaluate('({created: __progressTest.created, revoked: __progressTest.revoked})')
                assert all(url == active or url in objects['revoked'] for url in objects['created'])
                private_actions(context, page, observed)
                report['export_failures'] += 1
            finally:
                context.close()


def check_fallbacks(browser, origin, errors, report):
    for mode in ('no-js', 'blocked-script'):
        context, page = local_context(browser, errors, 320, scripting=mode != 'no-js')
        if mode == 'blocked-script':
            context.route('**/poker-progress.js*', lambda route: route.abort())
        try:
            load(page, origin)
            expect(page.locator('#course-progress')).to_be_visible()
            expect(page.locator('#progress-fallback')).to_be_visible()
            expect(page.locator('#progress-resume')).to_be_visible()
            assert page.locator('#course-progress select:visible, #course-progress input:visible, #course-progress textarea:visible, #course-progress button:visible').count() == 0
            assert page.locator('#course-progress [data-progress-read]:visible').count() == 6
            assert page.locator('#course-progress [data-progress-practice]:visible').count() == 6
            for lesson in LESSONS:
                expect(page.locator('[data-progress-read="' + lesson + '"]')).to_have_attribute('href', expected_url('read:' + lesson))
                expect(page.locator('[data-progress-practice="' + lesson + '"]')).to_have_attribute('href', expected_url('practice:' + lesson))
            reflow(page, mode)
            with page.expect_popup() as pending:
                enter(page, page.locator('#progress-resume'))
            destination = pending.value
            destination.wait_for_load_state('load')
            expect(destination).to_have_url(origin + expected_url('read:' + LESSONS[0]))
            expect(destination.locator('#course-first-pass-title')).to_be_visible()
            destination.close()
            with page.expect_download() as pending:
                enter(page, page.locator('#course-progress a[download][href="/downloads/poker-beginner-study-card.txt"]'))
            assert Path(pending.value.path()).read_bytes() == (ROOT / 'downloads/poker-beginner-study-card.txt').read_bytes()
            report['fallbacks'] += 1
        finally:
            context.close()


def main():
    started = perf_counter()
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    shots = Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    errors = []
    report = {'layouts': 0, 'navigation': 0, 'import_flows': 0, 'rejected_imports': 0,
              'storage': 0, 'cross_tab': 0, 'read_races': 0, 'export_failures': 0, 'fallbacks': 0}
    try:
        with sync_playwright() as playwright:
            options = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                options['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = playwright.chromium.launch(**options)
            try:
                check_ui(browser, origin, errors, report, shots)
                check_navigation(browser, origin, errors, report)
                check_imports(browser, origin, errors, report)
                check_storage(browser, origin, errors, report)
                check_cross_tab(browser, origin, errors, report)
                check_read_races(browser, origin, errors, report)
                check_export_recovery(browser, origin, errors, report)
                check_fallbacks(browser, origin, errors, report)
                assert not errors, errors
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print('PASS: manual course progress, explicit saving/resume, native JSON download/import, strict rejection, storage failures, cross-tab clear and import races, selectable export recovery, keyboard/reflow/print/no-script, and private actions.')
    print(json.dumps({**report, 'seconds': round(perf_counter() - started, 1)}, sort_keys=True))


if __name__ == '__main__':
    main()
