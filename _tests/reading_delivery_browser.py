"""Sharing behavior, ordinary HTTP fallbacks, and a controlled font-delay comparison.

--offline renders checked-out HTML in memory when local HTTP is unavailable.
Offline mode does not test requests, origin storage, or font-delay timing. Font-delay results are a laboratory dependency check, never real
user Core Web Vitals. No messages or real OS sharing/clipboard writes occur.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit, unquote
import argparse, base64, faulthandler, json, mimetypes, os, re, sys
from playwright.sync_api import sync_playwright, expect
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build, font_delivery
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--offline', action='store_true')
args = parser.parse_args()
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
server = None
if not args.offline:
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
base = 'https://nolankido.com' if args.offline else 'http://127.0.0.1:' + str(server.server_port)
origin = 'https://nolankido.com'
report = {'offline': args.offline, 'layouts': 0, 'text_spacing': 0, 'copy_checks': 0,
          'share_checks': 0, 'fallbacks': 0, 'privacy_checks': 0, 'print_checks': 0, 'axe': [], 'font_delay': [], 'font_face_parity': False}
errors = []
paths = ['/technology/check-ai-summary/', '/notes/keep-the-judgment/', '/poker/pot-odds-workshop/',
         '/living-well/find-the-document-you-need/', '/technology/task-brief/', '/technology/ai-time-savings/']
output = Path(os.environ.get('SCREENSHOT_DIR', '/mnt/data/reading-delivery-previews')); output.mkdir(parents=True, exist_ok=True)
font_record = json.loads((ROOT / font_delivery.PROVENANCE).read_text())
font_css = (ROOT / font_delivery.SOURCE).read_text()


def reference(document):
    document = re.sub(r'<link rel="stylesheet" href="/assets/site-fonts[.]css\?v=[a-f0-9]+">',
                      '<link rel="stylesheet" href="' + font_record['url'].replace('&', '&amp;') + '">', document)
    return document


def setup(context, requests, *, old=False, hold_fonts=False, held=None, block_share=False):
    def route(r):
        requests.append(r.request.url)
        u = urlsplit(r.request.url)
        if u.hostname == 'fonts.googleapis.com':
            if hold_fonts: held.append(r)
            else: r.fulfill(status=200, content_type='text/css', body=font_css)
        elif u.hostname == 'fonts.gstatic.com':
            if hold_fonts: held.append(r)
            else: r.abort()
        elif block_share and u.path == '/assets/page-sharing.js': r.abort()
        elif u.hostname == urlsplit(base).hostname:
            if args.offline or (old and r.request.resource_type == 'document'):
                path = unquote(u.path).lstrip('/')
                if u.path.endswith('/'): path += 'index.html'
                target = (ROOT / path).resolve()
                if not target.is_relative_to(ROOT) or not target.is_file():
                    r.fulfill(status=404, body='Not found'); return
                raw = target.read_bytes()
                if old and target.suffix == '.html': raw = reference(raw.decode()).encode()
                r.fulfill(status=200, content_type=mimetypes.guess_type(path)[0] or 'application/octet-stream', body=raw)
            else: r.continue_()
        else: r.abort()
    context.route('**/*', route)


def stub_source(mode='success', clipboard='success'):
    return """(() => {
      window.sharedPages = []; window.copiedPages = [];
      const mode = MODE, clip = CLIP;
      Object.defineProperty(navigator, 'clipboard', {configurable:true, value: clip === 'missing' ? undefined : {
        writeText: async text => { if (clip === 'denied') throw new Error('Denied'); window.copiedPages.push(text); }
      }});
      Object.defineProperty(navigator, 'canShare', {configurable:true, value: () => mode !== 'unsupported'});
      Object.defineProperty(navigator, 'share', {configurable:true, value: mode === 'missing' ? undefined : async data => {
        if (mode === 'cancel') throw new DOMException('Canceled', 'AbortError');
        if (mode === 'denied') throw new DOMException('Denied', 'NotAllowedError');
        if (mode === 'pending') { window.sharedPages.push(data); await new Promise(resolve => window.finishSharing = resolve); return; }
        window.sharedPages.push(data);
      }});
    })();""".replace('MODE', json.dumps(mode)).replace('CLIP', json.dumps(clipboard))


def stub(context, mode='success', clipboard='success'):
    context.add_init_script(stub_source(mode, clipboard))


def render(page, path, *, mode='success', clipboard='success', execute=True):
    if not args.offline:
        page.goto(base + path)
        return
    from browser import html_for
    clean = urlsplit(path).path
    text = html_for(clean)
    # Do not execute provider or site scripts implicitly in an opaque origin.
    # CSS comes from the exact generated page's local stylesheet references.
    text = re.sub(r'<script\b[^>]*src="[^"]+"[^>]*>.*?</script>', '', text, flags=re.S)
    page.set_content(text)
    if execute:
        page.evaluate(stub_source(mode, clipboard))
        if clean.endswith('/task-brief/'):
            page.add_script_tag(content=(ROOT/'assets/task-brief.js').read_text())
        page.add_script_tag(content=(ROOT/'assets/page-sharing.js').read_text())


def open_panel(page):
    panel = page.locator('details.page-share, details.note-keep')
    expect(panel).to_have_count(1)
    panel.locator('summary').focus(); page.keyboard.press('Enter')
    expect(panel).to_have_attribute('open', '')
    return panel

faulthandler.dump_traceback_later(240, exit=True)
try:
 with sync_playwright() as pw:
    options = {'headless': True}
    if os.environ.get('CHROMIUM_PATH'): options['executable_path'] = os.environ['CHROMIUM_PATH']
    browser = pw.chromium.launch(**options)
    # Keyboard copy and native-share payload exclude query strings, hashes and entered data.
    context = browser.new_context(); requests = []; setup(context, requests); stub(context)
    page = context.new_page(); page.on('pageerror', lambda e: errors.append(str(e))); page.set_default_timeout(10000)
    for path in paths:
        print('Sharing page:', path, flush=True)
        render(page, path + '?test-private=not-real#example')
        if path.endswith('/task-brief/'): page.locator('#brief-goal').fill('Synthetic private input, never shared')
        if path.endswith('/ai-time-savings/'):
            # Leave native input values untouched; URL taint is tested on both tools.
            expect(page.locator('h1')).to_be_visible()
        panel = open_panel(page); page.wait_for_timeout(100)
        before = len(requests)
        panel.locator('[data-copy-page]').focus(); page.keyboard.press('Enter')
        expect(panel.locator('.page-share-status')).to_have_text('Page link copied.')
        assert page.evaluate('window.copiedPages') == [origin + path]
        panel.locator('[data-share-page]').click()
        expect(panel.locator('.page-share-status')).to_have_text('Sharing dialog completed.')
        assert page.evaluate('window.sharedPages') == [{'title': page.title(), 'url': origin + path}]
        assert len(requests) == before
        if not args.offline:
            assert page.evaluate('localStorage.length + sessionStorage.length') == 0
            assert context.cookies() == []
        report['copy_checks'] += 1; report['share_checks'] += 1; report['privacy_checks'] += 1
        for width in [320, 390, 768, 1440]:
            page.set_viewport_size({'width': width, 'height': 950})
            assert page.evaluate('document.documentElement.scrollWidth') <= width, (path, width)
            for button in panel.locator('button').all(): assert button.bounding_box()['height'] >= 44
            report['layouts'] += 1
            style = page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
            assert page.evaluate('document.documentElement.scrollWidth') <= width, ('text spacing', path, width)
            report['text_spacing'] += 1; style.evaluate('(el)=>el.remove()')
            if width in [390, 1440] and path in paths[:2]:
                panel.scroll_into_view_if_needed()
                page.screenshot(path=str(output / (path.strip('/').replace('/', '-') + '-' + str(width) + '.png')))
        if os.environ.get('AXE_PATH'):
            page.set_viewport_size({'width':390,'height':950})
            page.add_script_tag(path=os.environ['AXE_PATH'])
            audit = page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>v.id),incomplete:r.incomplete.map(v=>v.id)}}")
            assert not audit['violations'], (path, audit)
            report['axe'].append({'path':path, **audit})
        page.emulate_media(media='print')
        expect(panel.locator('[data-copy-page]')).to_be_hidden()
        visible_origin = page.locator('.note-print-origin' if '/notes/' in path else '.page-share-print-origin')
        expect(visible_origin).to_be_visible(); expect(visible_origin).to_contain_text(origin + path)
        report['print_checks'] += 1; page.emulate_media(media='screen')
    context.close()
    # Device and permission fallbacks do not claim to have copied or shared.
    for mode, clip in [('success','missing'),('success','denied'),('missing','success'),('unsupported','success'),('cancel','success'),('denied','success'),('pending','success')]:
        c = browser.new_context(); req=[]; setup(c,req); stub(c,mode,clip); p=c.new_page(); p.set_default_timeout(10000)
        render(p,paths[0],mode=mode,clipboard=clip); panel=open_panel(p)
        if clip != 'success':
            panel.locator('[data-copy-page]').click()
            expect(panel.locator('.page-share-status')).to_contain_text('Automatic copying is unavailable')
            assert p.evaluate('window.getSelection().toString()') == origin+paths[0]
            expect(panel.locator('.page-share-address')).to_be_focused()
        elif mode in ['missing','unsupported']: expect(panel.locator('[data-share-page]')).to_be_hidden()
        elif mode == 'pending':
            panel.locator('[data-share-page]').click()
            expect(panel.locator('[data-copy-page]')).to_be_disabled()
            p.evaluate("document.querySelector('[data-share-page]').dispatchEvent(new Event('click'))")
            assert len(p.evaluate('window.sharedPages')) == 1
            p.evaluate('window.finishSharing()'); expect(panel.locator('[data-copy-page]')).to_be_enabled()
        else:
            panel.locator('[data-share-page]').click()
            expected = 'Sharing canceled' if mode == 'cancel' else 'Sharing is unavailable'
            expect(panel.locator('.page-share-status')).to_contain_text(expected)
            expect(panel.locator('[data-share-page]')).to_be_enabled()
        report['fallbacks'] += 1; c.close()
    # Native disclosures, public URLs and existing downloads survive script failure.
    for mode in ['disabled','blocked']:
        c=browser.new_context(java_script_enabled=mode!='disabled');req=[];setup(c,req,block_share=True)
        p=c.new_page()
        for path in paths[:4]:
            render(p,path,execute=False);panel=open_panel(p)
            expect(panel.locator('[data-copy-page]')).to_be_hidden(); expect(panel.locator('[data-share-page]')).to_be_hidden()
            expect(panel.locator('.page-share-address a, .note-origin a')).to_have_attribute('href',origin+path)
            report['fallbacks'] += 1
        c.close()
    if not args.offline:
        # Isolate the removed dependency. All font bytes are held, not downloaded.
        for old in [True, False]:
            c=browser.new_context();req=[];held=[];setup(c,req,old=old,hold_fonts=True,held=held)
            p=c.new_page();p.goto(base+'/',wait_until='commit');p.wait_for_timeout(900)
            before = p.evaluate("performance.getEntriesByName('first-contentful-paint').map(x=>x.startTime)")
            api_requests = sum(urlsplit(u).hostname=='fonts.googleapis.com' for u in req)
            if old:
                assert not before, ('reference unexpectedly painted before held CSS', before)
                assert api_requests == 1
                api = [r for r in held if urlsplit(r.request.url).hostname=='fonts.googleapis.com']
                assert len(api)==1;held.remove(api[0]);api[0].fulfill(status=200,content_type='text/css',body=font_css)
                p.wait_for_function("performance.getEntriesByName('first-contentful-paint').length > 0",timeout=5000)
            else:
                p.wait_for_function("performance.getEntriesByName('first-contentful-paint').length > 0",timeout=5000)
                assert api_requests == 0
            after=p.evaluate("performance.getEntriesByName('first-contentful-paint').map(x=>x.startTime)")
            report['font_delay'].append({'mode':'reference_external_css' if old else 'local_css','held_font_requests':len(held),
                                        'font_api_requests':api_requests,'painted_before_api_release':bool(before),'first_contentful_paint_ms':after[0]})
            for r in held:r.abort()
            c.close()
        descriptors=[]
        for old in [True,False]:
            c=browser.new_context();req=[];setup(c,req,old=old);p=c.new_page();p.goto(base+'/')
            descriptors.append(p.evaluate('Array.from(document.fonts).map(f=>[f.family,f.style,f.weight,f.display,f.unicodeRange]).sort()'))
            c.close()
        assert descriptors[0] == descriptors[1] and len(descriptors[0]) == 38
        report['font_face_parity']=True
    assert not errors, errors
    browser.close(); report['status']='pass'
    (output/'reading-delivery-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
finally:
    if server:server.shutdown();server.server_close()
    faulthandler.cancel_dump_traceback_later()
