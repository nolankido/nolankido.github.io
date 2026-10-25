"""Task brief behavior, privacy, keyboard, export, failure states, and reflow.
--offline uses in-memory pages when local HTTP navigation is not available.
No live service or message submission is used in either mode.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json, os, sys, re
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
from browser import html_for
parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');args=parser.parse_args()
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=None
if not args.offline:
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port) if server else ''
path='/technology/task-brief/'
script=(ROOT/'assets/task-brief.js').read_text()
errors=[];report={'mode':'offline' if args.offline else 'http','functional':0,'layouts':0,'spacing':0,'axe':0,'url_journeys':0}
try:
 with sync_playwright() as pw:
    opts={'headless':True}
    if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
    browser=pw.chromium.launch(**opts)
    context=browser.new_context(accept_downloads=True)
    requests=[]
    def route(r):
        requests.append(r.request.url)
        if not args.offline and urlsplit(r.request.url).hostname=='127.0.0.1':r.continue_()
        else:r.abort()
    context.route('**/*',route)
    page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
    def render(p,execute=True):
        if args.offline:
            p.set_content(html_for(path))
            if execute:p.add_script_tag(content=script)
        else:p.goto(base+path)
    render(page);expect(page.locator('#brief-editor')).to_be_visible()
    page.wait_for_timeout(100)
    initial_requests=len(requests);initial_url=page.url
    page.locator('#brief-build').focus();page.keyboard.press('Enter')
    expect(page.locator('#brief-goal')).to_be_focused();expect(page.locator('#brief-goal')).to_have_attribute('aria-invalid','true')
    expect(page.locator('#brief-result')).to_be_hidden();report['functional']+=1
    # An explicitly described hidden error still contributes to the browser's
    # accessible description. Editing must clear its text, not only hide it.
    report['error_description_checks'] = 0
    for key in ['goal', 'materials', 'output', 'review']:
        field = page.locator('#brief-' + key)
        help_text = page.locator('#brief-' + key + '-help').inner_text()
        expect(field).to_have_accessible_description(help_text + ' Add a short answer to this required field.')
        field.fill('Fictional ' + key + ' for a sorting checklist.')
        expect(field).to_have_accessible_description(help_text)
        expect(page.locator('#brief-' + key + '-error')).to_have_text('')
        expect(page.locator('#brief-' + key + '-error')).to_be_hidden()
        assert field.get_attribute('aria-invalid') is None
        report['error_description_checks'] += 1
    # Clearing a prior warning does not mean an unfinished field is validated.
    # A fresh Assemble must still report whitespace-only required content.
    page.locator('#brief-review').fill('   ')
    page.locator('#brief-build').click()
    expect(page.locator('#brief-review')).to_be_focused()
    expect(page.locator('#brief-review')).to_have_attribute('aria-invalid', 'true')
    page.locator('#brief-review').fill('Compare every item with the supplied source.')
    expect(page.locator('#brief-review')).to_have_accessible_description(page.locator('#brief-review-help').inner_text())
    report['error_description_checks'] += 1
    # Programmatic length injection exercises the optional field's existing
    # validator without changing its normal native maxlength restriction.
    page.locator('#brief-limits').evaluate("node => { node.value = 'x'.repeat(601); }")
    page.locator('#brief-build').click()
    expect(page.locator('#brief-limits')).to_have_attribute('aria-invalid', 'true')
    expect(page.locator('#brief-limits')).to_have_accessible_description(
        page.locator('#brief-limits-help').inner_text() + ' Shorten this to 600 characters or fewer.')
    page.locator('#brief-limits').fill('')
    expect(page.locator('#brief-limits')).to_have_accessible_description(page.locator('#brief-limits-help').inner_text())
    expect(page.locator('#brief-limits-error')).to_have_text('')
    page.locator('#brief-build').click()
    expect(page.locator('#brief-result')).to_be_visible()
    report['error_description_checks'] += 1
    page.locator('#brief-clear').click()
    page.locator('#brief-confirm-yes').click()
    page.locator('[data-brief-example="writing"] summary').click()
    page.locator('[data-use-example="writing"]').click()
    expect(page.locator('#brief-goal')).to_be_focused()
    expect(page.locator('#brief-confirm')).to_be_hidden()
    page.locator('#brief-build').click()
    expect(page.locator('#brief-result-title')).to_be_focused()
    content=page.locator('#brief-text').input_value()
    assert content.startswith('PURPOSE\nHelp a first-time reader')
    assert 'Do not publish, send, book, buy' in content
    preview=page.locator('#brief-preview')
    expect(preview.locator('.brief-preview-part')).to_have_count(6)
    assert [h.inner_text() for h in preview.locator('h4').all()]==['PURPOSE','MATERIAL I WILL PROVIDE','DELIVERABLE AND STOPPING POINT','CHECK BEFORE USING','TASK BOUNDARIES','WORKING INSTRUCTIONS']
    assert 'Help a first-time reader' in preview.locator('.brief-preview-part').first.inner_text()
    report['functional']+=2
    # Clipboard success is explicit and writes precisely the reviewed output.
    page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText: async text => { window.copiedBrief = text; }}})")
    page.locator('#brief-copy').click();expect(page.locator('#brief-copy-status')).to_contain_text('Brief copied')
    assert page.evaluate('window.copiedBrief')==content
    # Denied/unavailable clipboard falls back to visible, selected plain text.
    page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText: async () => { throw new Error('Denied'); }}})")
    page.locator('#brief-copy').click();expect(page.locator('#brief-copy-status')).to_contain_text('Automatic copy is unavailable')
    expect(page.locator('#brief-text')).to_be_focused()
    assert page.locator('#brief-text').evaluate('(el)=>el.selectionEnd-el.selectionStart')==len(content)
    report['functional']+=2
    page.locator('#brief-select').click()
    expect(page.locator('#brief-copy-status')).to_contain_text('Complete text selected')
    expect(page.locator('#brief-text')).to_be_focused()
    assert page.locator('#brief-text').evaluate('(el)=>el.selectionEnd-el.selectionStart')==len(content)
    report['functional']+=1
    with page.expect_download() as item:page.locator('#brief-download').click()
    download=item.value;assert download.suggested_filename=='ai-task-brief.txt'
    assert Path(download.path()).read_text()==content;report['functional']+=1
    page.locator('#brief-goal').fill('<img src=x onerror=alert(1)> & a literal task')
    expect(page.locator('#brief-result')).to_be_hidden()
    assert page.locator('#brief-text').input_value()==''
    expect(page.locator('#brief-preview .brief-preview-part')).to_have_count(0)
    page.locator('#brief-build').click();assert '<img src=x' in page.locator('#brief-text').input_value()
    assert page.locator('#brief-editor img').count()==0;report['functional']+=1
    # Changing examples and clearing never discard work without an explicit second action.
    page.locator('[data-brief-example="planning"] summary').click()
    page.locator('[data-use-example="planning"]').click();expect(page.locator('#brief-confirm')).to_be_visible()
    before=page.locator('#brief-goal').input_value()
    page.locator('#brief-confirm-no').click();assert page.locator('#brief-goal').input_value()==before
    expect(page.locator('[data-use-example="planning"]')).to_be_focused()
    page.locator('[data-use-example="planning"]').click();page.locator('#brief-confirm-yes').click()
    assert 'small group' in page.locator('#brief-goal').input_value()
    page.locator('#brief-clear').click();page.locator('#brief-confirm-no').click()
    assert 'small group' in page.locator('#brief-goal').input_value()
    page.locator('#brief-clear').click();page.locator('#brief-confirm-yes').click()
    for key in ['goal','materials','output','review','limits']:
        assert page.locator('#brief-'+key).input_value()==''
    expect(page.locator('#brief-goal')).to_be_focused();report['functional']+=2
    assert len(requests)==initial_requests,(initial_requests,requests)
    assert page.url==initial_url
    if not args.offline:
        assert page.evaluate('localStorage.length+sessionStorage.length')==0
        assert context.cookies()==[]
    page.locator('#brief-goal').fill('A disposable test input')
    page.evaluate("window.dispatchEvent(new Event('pagehide'))")
    assert page.locator('#brief-goal').input_value()==''
    page.locator('#brief-goal').fill('Restored test input')
    page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))")
    assert page.locator('#brief-goal').input_value()=='';report['functional']+=1
    # All examples are readable and independently usable; no hidden preset data.
    for key in ['meeting','article','website','writing','planning','learning']:
        card=page.locator('[data-brief-example="'+key+'"]')
        if card.get_attribute('open') is None:card.locator('summary').click()
        card.locator('button').click()
        if page.locator('#brief-confirm').is_visible():page.locator('#brief-confirm-yes').click()
        page.locator('#brief-build').click();expect(page.locator('#brief-result')).to_be_visible()
        assert len(page.locator('#brief-text').input_value())>600
        expect(page.locator('#brief-preview .brief-preview-part')).to_have_count(6)
    report['functional']+=6
    # Reflow checks for blank, assembled and confirmation states.
    spacing='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}'
    screenshots=Path(os.environ.get('SCREENSHOT_DIR','/mnt/data/task-brief-previews'));screenshots.mkdir(parents=True,exist_ok=True)
    for state in ['result','confirm','blank']:
        if state=='confirm':page.locator('#brief-clear').click()
        if state=='blank':page.locator('#brief-confirm-yes').click()
        for width in [320,390,768,1024,1440]:
            page.set_viewport_size({'width':width,'height':950})
            assert page.evaluate('document.documentElement.scrollWidth')<=width,(state,width)
            report['layouts']+=1
            style=page.add_style_tag(content=spacing)
            assert page.evaluate('document.documentElement.scrollWidth')<=width,('spacing',state,width)
            report['spacing']+=1;style.evaluate('(el)=>el.remove()')
            if width in [390,1440] and state!='confirm':
                page.locator('h1').click()
                page.evaluate('window.scrollTo(0,0)');page.wait_for_timeout(100)
                page.screenshot(path=str(screenshots/f'task-brief-{state}-{width}.png'),full_page=True)
            if os.environ.get('AXE_PATH') and width==390:
                page.add_script_tag(path=os.environ['AXE_PATH'])
                scan=page.evaluate("async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})")
                assert scan['violations']==[],scan['violations'];report['axe']+=1
    # The optional walkthrough is ordinary HTML and never edits a draft.
    report['walkthrough_checks'] = 0
    page.locator('#brief-goal').fill('Keep this unsubmitted example draft.')
    for width in [320,390,768,1440]:
        page.set_viewport_size({'width':width,'height':950})
        guide=page.locator('#brief-walkthrough')
        summary=guide.locator('summary')
        # Native disclosure affordances need a usable tap area even on a
        # narrow screen; keep the built-in summary marker and keyboard action.
        for target in page.locator('.brief-example summary, .brief-template summary').all():
            bounds=target.bounding_box()
            assert bounds and bounds['height']>=44, ('small-brief-disclosure',width,bounds)
        summary.focus();page.keyboard.press('Enter')
        expect(guide.locator('ol')).to_be_visible()
        expect(guide.locator('li')).to_have_count(4)
        assert page.locator('#brief-goal').input_value()=='Keep this unsubmitted example draft.'
        assert page.evaluate('document.documentElement.scrollWidth')<=width
        style=page.add_style_tag(content=spacing)
        assert page.evaluate('document.documentElement.scrollWidth')<=width
        style.evaluate('(el)=>el.remove()')
        if width in [390,1440]:
            guide.scroll_into_view_if_needed()
            page.screenshot(path=str(screenshots/f'task-brief-walkthrough-{width}.png'),full_page=False)
        summary.focus();page.keyboard.press('Enter')
        expect(guide.locator('ol')).to_be_hidden()
        report['walkthrough_checks']+=1
    if not args.offline:
        for route_path in ['/technology/','/resources/','/start-here/']:
            page.goto(base+route_path)
            page.locator('main a[href="'+path+'"]').first.focus();page.keyboard.press('Enter')
            expect(page).to_have_url(base+path);report['url_journeys']+=1
        page.locator('#brief-goal').fill('No history storage')
        page.get_by_role('link',name='Back to Technology',exact=True).click()
        page.go_back();assert page.locator('#brief-goal').input_value()=='';report['url_journeys']+=1
    context.close()
    # Both disabled scripts and a failed asset preserve the three examples and blank text.
    for mode in ['disabled','blocked']:
        # Disable smooth-scroll animation in these no-script fallback fixtures;
        # pointer actionability must not depend on a disabled page's animation clock.
        c=browser.new_context(java_script_enabled=mode!='disabled', reduced_motion='reduce')
        def fallback_route(r):
            if 'task-brief.js' in r.request.url:r.abort()
            elif not args.offline and urlsplit(r.request.url).hostname=='127.0.0.1':r.continue_()
            else:r.abort()
        c.route('**/*',fallback_route)
        p=c.new_page();render(p,False)
        expect(p.locator('#brief-editor')).to_be_hidden();expect(p.locator('#brief-unavailable')).to_be_visible()
        assert p.locator('.brief-example').count()==6
        guide=p.locator('#brief-walkthrough')
        guide.locator('summary').focus();p.keyboard.press('Enter')
        expect(guide.locator('ol')).to_be_visible()
        expect(guide).to_contain_text('Without JavaScript:')
        expect(guide.locator('a[href="#brief-example-meeting"]')).to_have_count(1)
        expect(p.locator('#brief-example-meeting')).to_have_count(1)
        report['walkthrough_checks']+=1
        p.locator('#brief-blank .brief-template summary').click()
        assert p.locator('.brief-template pre').inner_text().strip()+'\n'==(ROOT/'downloads/ai-task-brief.txt').read_text()
        if not args.offline:
            # Build notes and the original worksheet section both offer this file.
            # Exercise both original worksheet entry points. The optional workflow
            # adds a separate workbook download, checked by its navigation suite.
            links=p.locator('a[download][href="/downloads/ai-task-brief.txt"]')
            expect(links).to_have_count(2)
            for link in links.all():
                expect(link).to_have_attribute('href','/downloads/ai-task-brief.txt')
                with p.expect_download() as d:link.click()
                assert Path(d.value.path()).read_bytes()==(ROOT/'downloads/ai-task-brief.txt').read_bytes()
        c.close();report['functional']+=1
    assert not errors,errors
    browser.close()
 print('TASK_BRIEF_REPORT='+json.dumps(report))
finally:
 if server:server.shutdown();server.server_close()
