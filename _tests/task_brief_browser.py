"""Task brief behavior, privacy, keyboard, export, failure states, and reflow.
--offline uses in-memory pages when local HTTP navigation is not available.
No live service or message submission is used in either mode.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from time import monotonic
from urllib.parse import urlsplit
import json, os, sys, re
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
from browser import html_for
from field_guide_browser import wait_for_fonts
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
errors=[];report={'mode':'offline' if args.offline else 'http','functional':0,'layouts':0,'spacing':0,'axe':0,'url_journeys':0,
                 'print_layouts':0,'print_requests':0,'print_fallbacks':0,'print_state_guards':0,
                 'print_static_fallbacks':0,'print_pdf_captures':0}
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
    # Browser Print and the explicit Print brief action use the same existing
    # preview. An isolated context keeps these state transitions independent of
    # the screen, clipboard and navigation journeys above.
    print_context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    print_network_requests=[]
    def print_route(r):
        print_network_requests.append(r.request.url)
        if not args.offline and urlsplit(r.request.url).hostname=='127.0.0.1':r.continue_()
        else:r.abort()
    print_context.route('**/*',print_route)
    p=print_context.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
    render(p);p.evaluate('document.fonts.ready')
    # The browser can request its favicon after load/font readiness. Finish
    # that startup activity before enforcing the unchanged zero-request print
    # boundary; do not discard a later request from the assertion below.
    if not args.offline:p.wait_for_load_state('networkidle')
    print_initial_requests=len(print_network_requests);print_initial_url=p.url
    # Return undefined when installing the stub: Playwright otherwise invokes a
    # function returned by an assignment expression, creating a phantom request.
    p.evaluate("() => { window.briefPrintRequests=0; window.print=()=>{window.briefPrintRequests+=1; window.dispatchEvent(new Event('beforeprint')); window.dispatchEvent(new Event('afterprint'));}; }")
    field_limits={'goal':600,'materials':800,'output':600,'review':800,'limits':600}
    headings=['PURPOSE','MATERIAL I WILL PROVIDE','DELIVERABLE AND STOPPING POINT','CHECK BEFORE USING','TASK BOUNDARIES','WORKING INSTRUCTIONS']
    blank_template=(ROOT/'downloads/ai-task-brief.txt').read_text()

    def print_probe():
        return p.evaluate("""() => ({
            requests: window.briefPrintRequests,
            printType: typeof window.print,
            status: document.getElementById('brief-copy-status').textContent,
            focused: document.activeElement && document.activeElement.id,
            resultHidden: document.getElementById('brief-result').hidden,
            outputLength: document.getElementById('brief-text').value.length
        })""")

    assert p.evaluate('window.briefPrintRequests')==0,print_probe()

    def print_snapshot():
        return {
            'fields':{key:p.locator('#brief-'+key).input_value() for key in field_limits},
            'text':p.locator('#brief-text').input_value(),
            'sections':p.locator('#brief-preview .brief-preview-part').evaluate_all(
                "parts=>parts.map(part=>({heading:part.querySelector('h4').textContent,content:part.querySelector('p').textContent}))"),
        }

    def assemble_print_values(values):
        for key,value in values.items():p.locator('#brief-'+key).fill(value)
        p.locator('#brief-build').click()
        expect(p.locator('#brief-result')).to_be_visible()
        snapshot=print_snapshot()
        assert [part['heading'] for part in snapshot['sections']]==headings
        assert '\n\n'.join(part['heading']+'\n'+part['content'] for part in snapshot['sections'])+'\n'==snapshot['text']
        assert p.locator('#brief-preview img, #brief-preview script').count()==0
        return snapshot

    def assert_no_printable_result(reason,private_marker=''):
        expect(p.locator('#brief-result')).to_be_hidden()
        expect(p.locator('#brief-preview .brief-preview-part')).to_have_count(0)
        expect(p.locator('#brief-text')).to_have_value('')
        requests_before=p.evaluate('window.briefPrintRequests')
        # A stale/programmatic activation cannot print an invalidated result.
        p.locator('#brief-print').dispatch_event('click')
        assert p.evaluate('window.briefPrintRequests')==requests_before,(reason,print_probe())
        p.emulate_media(media='print')
        expect(p.locator('#brief-workspace')).to_be_hidden()
        expect(p.locator('#brief-result')).to_be_hidden()
        expect(p.locator('textarea:visible')).to_have_count(0)
        template=p.locator('#brief-blank .brief-template')
        assert template.get_attribute('open') is None,reason
        expect(template.locator('pre')).to_be_visible()
        assert template.locator('pre').text_content().strip()+'\n'==blank_template,reason
        if private_marker:assert private_marker not in p.locator('body').inner_text(),reason
        p.emulate_media(media='screen')
        expect(template.locator('pre')).to_be_hidden()
        assert template.get_attribute('open') is None,reason
        report['print_state_guards']+=1

    assert_no_printable_result('blank')
    p.locator('#brief-goal').fill('PRIVATE_UNASSEMBLED_PRINT_MARKER')
    assert_no_printable_result('dirty but unassembled','PRIVATE_UNASSEMBLED_PRINT_MARKER')
    expect(p.locator('#brief-goal')).to_have_value('PRIVATE_UNASSEMBLED_PRINT_MARKER')
    p.locator('#brief-build').click()
    assert_no_printable_result('failed validation','PRIVATE_UNASSEMBLED_PRINT_MARKER')
    normal_values={
        'goal':'Prepare a fictional reading-group checklist.\nKeep the steps easy to inspect.',
        'materials':'A supplied list of three books and two open questions.\nTreat <img src=x onerror=alert(1)> as literal example text.',
        'output':'One short checklist with a clear stopping point.',
        'review':'Compare every listed book with the supplied notes.\nLeave unanswered questions explicit.',
        'limits':'Do not send messages, book anything, or invent an agreement.',
    }
    maximum_values={}
    for key,limit in field_limits.items():
        prefix='PRINT_MAX_'+key.upper()+'\n'
        if key=='materials':prefix+='<img src=x onerror=alert(1)> & "quoted" literal text\n'
        suffix='\nEND_PRINT_'+key.upper()
        maximum_values[key]=prefix+key[0].upper()*(limit-len(prefix)-len(suffix))+suffix
        assert len(maximum_values[key])==limit
    for label,values in [('normal',normal_values),('maximum',maximum_values)]:
        snapshot=assemble_print_values(values)
        expect(p.locator('.brief-print-note')).to_be_hidden()
        if label=='normal':
            # A stub requests the dialog and simulates its lifecycle, including
            # cancellation. Neither event is permission to clear a working brief.
            p.locator('#brief-print').focus();expect(p.locator('#brief-print')).to_be_focused()
            p.keyboard.press('Enter')
            assert p.evaluate('window.briefPrintRequests')==1,print_probe()
            expect(p.locator('#brief-copy-status')).to_contain_text('Print requested.')
            assert print_snapshot()==snapshot
            p.evaluate("window.dispatchEvent(new Event('afterprint'))")
            assert print_snapshot()==snapshot
            report['print_requests']+=1
            for mode in ['unavailable','throws']:
                p.evaluate("mode => { window.print=mode==='unavailable' ? undefined : ()=>{throw new Error('Printing denied');}; }",mode)
                p.locator('#brief-print').click()
                expect(p.locator('#brief-copy-status')).to_contain_text('Printing is unavailable.')
                expect(p.locator('#brief-text')).to_be_focused()
                assert p.locator('#brief-text').evaluate('(el)=>el.selectionEnd-el.selectionStart')==len(snapshot['text'])
                assert print_snapshot()==snapshot
                report['print_fallbacks']+=1
            p.evaluate('() => { window.print=()=>{window.briefPrintRequests+=1;}; }')
        # Emulating print without pressing the button also covers browser Print.
        for width in [320,390,768,1440]:
            p.set_viewport_size({'width':width,'height':1000});p.emulate_media(media='print')
            expect(p.locator('html')).to_have_css('background-color','rgb(255, 255, 255)')
            expect(p.locator('#brief-workspace')).to_be_visible()
            expect(p.locator('#main > :visible')).to_have_count(1)
            expect(p.locator('#main > :visible')).to_have_attribute('id','brief-workspace')
            expect(p.locator('#brief-result-title')).to_be_visible()
            expect(p.locator('.brief-print-note')).to_be_visible()
            expect(p.locator('#brief-preview .brief-preview-part:visible')).to_have_count(6)
            expect(p.locator('input:visible, textarea:visible, button:visible')).to_have_count(0)
            for selector in ['#brief-text','#brief-examples','#brief-blank','#brief-text-help','#brief-status','#brief-confirm','.site-header','footer']:
                for element in p.locator(selector).all():expect(element).to_be_hidden()
            assert print_snapshot()==snapshot,(label,width)
            assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),(label,width)
            assert p.locator('#brief-preview h4, #brief-preview p').evaluate_all(
                'elements=>elements.every(el=>el.scrollWidth<=el.clientWidth+1 && el.scrollHeight<=el.clientHeight+1)'),(label,width)
            assert [heading.inner_text() for heading in p.locator('#brief-preview h4:visible').all()]==headings
            report['print_layouts']+=1
            p.emulate_media(media='screen')
            expect(p.locator('.brief-print-note')).to_be_hidden()
            expect(p.locator('#brief-goal')).to_be_visible()
            expect(p.locator('#brief-print')).to_be_visible()
            expect(p.locator('#brief-examples')).to_be_visible()
            assert print_snapshot()==snapshot,(label,width,'screen restored')
        if os.environ.get('SCREENSHOT_DIR'):
            p.emulate_media(media='print')
            pdf=p.pdf(path=str(screenshots/f'task-brief-print-{label}.pdf'),format='A4',print_background=True,
                      margin={'top':'15mm','bottom':'15mm','left':'15mm','right':'15mm'})
            assert pdf.startswith(b'%PDF-')
            report['print_pdf_captures']+=1
            p.emulate_media(media='screen')
            assert print_snapshot()==snapshot,(label,'PDF capture changed draft')
    p.locator('#brief-goal').fill('PRIVATE_EDITED_PRINT_MARKER')
    assert_no_printable_result('edited','PRIVATE_EDITED_PRINT_MARKER')
    p.locator('#brief-build').click()
    p.locator('#brief-clear').click();p.locator('#brief-confirm-yes').click()
    assert_no_printable_result('cleared')
    for event in ["new Event('pagehide')","new PageTransitionEvent('pageshow',{persisted:true})"]:
        assemble_print_values(normal_values)
        p.evaluate('window.dispatchEvent('+event+')')
        for key in field_limits:expect(p.locator('#brief-'+key)).to_have_value('')
        assert_no_printable_result(event)
    assert p.evaluate('window.briefPrintRequests')==1,print_probe()
    assert len(print_network_requests)==print_initial_requests,(print_initial_requests,print_network_requests)
    assert p.url==print_initial_url
    if not args.offline:assert p.evaluate('localStorage.length+sessionStorage.length')==0
    assert print_context.cookies()==[]
    print_context.close()
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
        # A closed blank-template disclosure is printable even when the script
        # cannot run. Returning to screen preserves its original closed state.
        template=p.locator('#brief-blank .brief-template')
        assert template.get_attribute('open') is None
        expect(template.locator('pre')).to_be_hidden()
        p.emulate_media(media='print')
        expect(p.locator('html')).to_have_css('background-color','rgb(255, 255, 255)')
        expect(p.locator('#brief-workspace')).to_be_hidden()
        expect(p.locator('#brief-print')).to_be_hidden()
        expect(template.locator('pre')).to_be_visible()
        assert template.locator('pre').text_content().strip()+'\n'==(ROOT/'downloads/ai-task-brief.txt').read_text()
        p.emulate_media(media='screen')
        expect(template.locator('pre')).to_be_hidden()
        assert template.get_attribute('open') is None
        report['print_static_fallbacks']+=1
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
    # A brief is deliberately ephemeral. The new native handoff must preserve
    # it during same-page reading, let the reader keep an exact copy, and reach
    # a usable independent check before the documented page-exit clearing.
    # These are real HTTP journeys; the offline mode cannot qualify navigation.
    report.update(answer_handoff_journeys=0,answer_handoff_saved_briefs=0,
                  answer_handoff_blank_downloads=0,answer_handoff_same_page=0,
                  answer_handoff_return_clears=0,answer_handoff_method_choices=0,
                  answer_handoff_records=0,answer_handoff_spacing=0,
                  answer_handoff_print_layouts=0,answer_handoff_cold_arrivals=0,
                  answer_handoff_delayed_font_arrivals=0,
                  answer_handoff_scripted_delayed_arrivals=0,
                  answer_handoff_cancelled_arrivals=0)
    if not args.offline:
        field_keys=['goal','materials','output','review','limits']
        answer_path='/technology/check-ai-answers/'

        def handoff_enter(p,target):
            # Keyboard activation follows an observable, usable focus target.
            # Position the source control as a reader can before focusing it;
            # never scroll a link's destination to manufacture an arrival.
            expect(target).to_be_visible()
            target.scroll_into_view_if_needed()
            target.focus()
            expect(target).to_be_focused()
            expect(target).to_be_in_viewport()
            p.keyboard.press('Enter')

        def readable_native_target(p,selector,label):
            # Wait for the actual destination fonts, without scrolling the
            # target into place or supplying different production styles.
            # A matching URL alone does not mean the new document has loaded.
            p.wait_for_load_state('load')
            wait_for_fonts(p)
            target=p.locator(selector)
            # Observe native smooth scrolling until it has actually stopped.
            # Driver polling also works when page scripts are disabled.
            deadline=monotonic()+5
            previous=None;stable_since=None
            while True:
                position=target.evaluate('el => ({y:scrollY,top:el.getBoundingClientRect().top})')
                now=monotonic()
                if previous==position:
                    if stable_since is not None and now-stable_since>=0.3:break
                else:stable_since=now;previous=position
                assert now<deadline,('native scroll did not settle',label,position)
                p.wait_for_timeout(50)
            expect(target).to_be_in_viewport(ratio=1)
            bounds=target.evaluate("""el => {
                const r=el.getBoundingClientRect();
                const header=document.querySelector('.site-header');
                const sticky=header && ['fixed','sticky'].includes(getComputedStyle(header).position);
                return {top:r.top,bottom:r.bottom,height:innerHeight,
                        headerBottom:sticky?Math.max(0,header.getBoundingClientRect().bottom):0};
            }""")
            assert bounds['top']>=bounds['headerBottom']-1,(label,bounds)
            assert bounds['bottom']<=bounds['height']+1,(label,bounds)

        def brief_font_mode(p,javascript):
            fonts=p.evaluate('''() => ({disabled:matchMedia('(scripting: none)').matches,
                body:['--sans','--serif','--mono'].map(name=>getComputedStyle(document.body).getPropertyValue(name)),
                root:['--sans','--serif','--mono'].map(name=>getComputedStyle(document.documentElement).getPropertyValue(name)),
                requests:performance.getEntriesByType('resource').filter(item=>item.name.includes('.woff')).map(item=>item.name)
            })''')
            assert fonts['disabled']==(not javascript),fonts
            if javascript:assert fonts['body']==fonts['root'],fonts
            else:
                assert all(body!=root for body,root in zip(fonts['body'],fonts['root'])),fonts
                assert fonts['requests']==[],fonts

        # Both the public section bookmark and the indexed heading must work
        # on a fresh arrival, with normal native motion and the shipped fonts.
        for javascript in [True,False]:
            for width in [320,390,768,1440]:
                for fragment in ['brief-next-check','brief-next-check-title']:
                    c=browser.new_context(java_script_enabled=javascript,
                                          viewport={'width':width,'height':1000})
                    c.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
                    p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
                    label={'width':width,'javascript':javascript,'fragment':fragment}
                    try:
                        response=p.goto(base+path+'#'+fragment)
                        assert response and response.status==200,label
                        expect(p).to_have_url(base+path+'#'+fragment)
                        readable_native_target(p,'#brief-next-check-title',label)
                        brief_font_mode(p,javascript)
                        assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),label
                        assert p.evaluate('localStorage.length+sessionStorage.length')==0,label
                        assert c.cookies()==[],label
                        if not javascript and width==320 and fragment=='brief-next-check-title':
                            p.screenshot(path=str(screenshots/'task-brief-cold-native-320.png'))
                        report['answer_handoff_cold_arrivals']+=1
                    except Exception:
                        p.screenshot(path=str(screenshots/f'task-brief-cold-failure-{width}-{javascript}-{fragment}.png'))
                        raise
                    finally:c.close()

        # Reproduce the specific no-script font race by holding the actual font
        # definitions until DOMContentLoaded. No CSS or scroll correction is
        # substituted by the driver, and the browser keeps normal motion.
        c=browser.new_context(java_script_enabled=False,viewport={'width':320,'height':1000})
        c.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
        held=[];c.route('**/site-fonts.css*',lambda r:held.append(r))
        p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
        try:
            response=p.goto(base+path+'#brief-next-check-title',wait_until='domcontentloaded')
            assert response and response.status==200
            assert held,'The delayed-font fixture did not intercept the actual font stylesheet'
            c.unroute('**/site-fonts.css*')
            for request in held:request.continue_()
            readable_native_target(p,'#brief-next-check-title',{'width':320,'javascript':False,'fonts':'delayed'})
            brief_font_mode(p,False)
            expect(p).to_have_url(base+path+'#brief-next-check-title')
            p.screenshot(path=str(screenshots/'task-brief-delayed-native-320.png'))
            report['answer_handoff_delayed_font_arrivals']+=1
        finally:c.close()

        # The production arrival repair may adjust an untouched initial
        # bookmark once. Real reader input, scrolling or another destination
        # must cancel that pending adjustment while fonts are still delayed.
        for mode in ['arrival','typing','wheel','navigation']:
            c=browser.new_context(viewport={'width':320,'height':1000})
            c.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            held=[];c.route('**/*.woff2*',lambda r:held.append(r))
            c.add_init_script('''(() => {
                const original=window.scrollTo;
                window.briefArrivalCalls=[];
                window.scrollTo=function(...args){window.briefArrivalCalls.push(args);return original.apply(window,args);};
                window.briefWheelEvents=0;
                addEventListener('wheel',()=>{window.briefWheelEvents+=1;},{passive:true});
            })();''')
            p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
            try:
                response=p.goto(base+path+'#brief-next-check',wait_until='domcontentloaded')
                assert response and response.status==200,mode
                expect(p.locator('#brief-editor')).to_be_visible()
                assert held,('No real font was held',mode)
                focus_before=p.evaluate('document.activeElement.id')
                if mode=='typing':
                    field=p.locator('#brief-goal')
                    field.scroll_into_view_if_needed();field.focus()
                    p.keyboard.type('Keep this typed check private.')
                    expect(field).to_have_value('Keep this typed check private.')
                elif mode=='wheel':
                    p.mouse.wheel(0,300)
                    p.wait_for_function('window.briefWheelEvents>0')
                elif mode=='navigation':
                    handoff_enter(p,p.locator('.entry-jumps a[href="#brief-blank"]'))
                    expect(p).to_have_url(base+path+'#brief-blank')
                c.unroute('**/*.woff2*')
                for request in held:request.continue_()
                p.wait_for_load_state('load');wait_for_fonts(p)
                p.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
                if mode=='arrival':
                    readable_native_target(p,'#brief-next-check-title',{'fonts':'delayed','mode':mode})
                    assert len(p.evaluate('window.briefArrivalCalls'))==1
                    assert p.evaluate('document.activeElement.id')==focus_before
                    p.screenshot(path=str(screenshots/'task-brief-scripted-delayed-320.png'))
                    report['answer_handoff_scripted_delayed_arrivals']+=1
                else:
                    assert p.evaluate('window.briefArrivalCalls')==[],mode
                    if mode=='typing':
                        expect(p.locator('#brief-goal')).to_be_focused()
                        expect(p.locator('#brief-goal')).to_have_value('Keep this typed check private.')
                        expect(p.locator('#brief-result')).to_be_hidden()
                    if mode=='navigation':expect(p).to_have_url(base+path+'#brief-blank')
                    report['answer_handoff_cancelled_arrivals']+=1
            except Exception:
                p.screenshot(path=str(screenshots/f'task-brief-delayed-{mode}-failure.png'))
                raise
            finally:c.close()

        for javascript in [True,False]:
            for width in [320,390,768,1440]:
                c=browser.new_context(java_script_enabled=javascript,accept_downloads=True,
                                      viewport={'width':width,'height':1000},
                                      reduced_motion='no-preference' if javascript else 'reduce')
                journey_requests=[]
                def handoff_route(r):
                    journey_requests.append((r.request.method,r.request.url))
                    if urlsplit(r.request.url).hostname=='127.0.0.1':r.continue_()
                    else:r.abort()
                c.route('**/*',handoff_route)
                p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
                label={'width':width,'javascript':javascript}
                try:
                    response=p.goto(base+path)
                    assert response and response.status==200,label
                    wait_for_fonts(p)
                    if javascript:
                        handoff_enter(p,p.locator('#brief-example-meeting summary'))
                        handoff_enter(p,p.locator('[data-use-example="meeting"]'))
                        goal=p.locator('#brief-goal').input_value()+' HANDOFF_TEST_ONLY'
                        p.locator('#brief-goal').fill(goal)
                        handoff_enter(p,p.locator('#brief-build'))
                        expect(p.locator('#brief-result')).to_be_visible()
                        fields={key:p.locator('#brief-'+key).input_value() for key in field_keys}
                        saved_content=p.locator('#brief-text').input_value().encode('utf-8')
                        with p.expect_download() as download:
                            handoff_enter(p,p.locator('#brief-download'))
                        same_page=p.locator('#brief-result-next a[href="#brief-next-check"]')
                        report['answer_handoff_saved_briefs']+=1
                    else:
                        expect(p.locator('#brief-editor')).to_be_hidden()
                        expect(p.locator('#brief-unavailable')).to_be_visible()
                        saved_content=(ROOT/'downloads/ai-task-brief.txt').read_bytes()
                        with p.expect_download() as download:
                            handoff_enter(p,p.locator('#brief-blank a[download]'))
                        same_page=p.locator('.entry-jumps a[href="#brief-next-check"]')
                        report['answer_handoff_blank_downloads']+=1
                    assert download.value.suggested_filename=='ai-task-brief.txt',label
                    saved_file=Path(download.value.path())
                    assert saved_file.read_bytes()==saved_content,label
                    handoff_enter(p,same_page)
                    expect(p).to_have_url(base+path+'#brief-next-check')
                    readable_native_target(p,'#brief-next-check-title',label)
                    handoff=p.locator('#brief-next-check')
                    expect(handoff.locator('ol > li')).to_have_count(3)
                    expect(handoff).to_contain_text('This builder clears its entries when you leave.')
                    expect(handoff).to_contain_text('Add the chosen check to your saved copy')
                    if javascript:
                        assert {key:p.locator('#brief-'+key).input_value() for key in field_keys}==fields,label
                        assert p.locator('#brief-text').input_value().encode('utf-8')==saved_content,label
                        report['answer_handoff_same_page']+=1
                    assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),label
                    if javascript and width in [390,1440]:
                        handoff.screenshot(path=str(screenshots/f'task-brief-next-check-{width}.png'))
                    # The no-script browser does not emit the stylesheet load
                    # event awaited by add_style_tag. Use the same driver-only
                    # insertion as the existing weekly-reset spacing checks.
                    style=p.evaluate_handle(
                        'css => { const el=document.createElement("style"); el.textContent=css; document.head.append(el); return el; }',
                        spacing)
                    assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),('handoff spacing',label)
                    style.evaluate('(el)=>el.remove()')
                    report['answer_handoff_spacing']+=1
                    p.emulate_media(media='print')
                    if javascript:
                        expect(handoff).to_be_hidden()
                        expect(p.locator('#brief-result-next')).to_be_hidden()
                        expect(p.locator('#brief-preview .brief-preview-part:visible')).to_have_count(6)
                    else:
                        expect(handoff).to_be_visible()
                        expect(p.locator('#brief-next-check-title')).to_be_visible()
                        expect(p.locator('#brief-blank .brief-template pre')).to_be_visible()
                    assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),('handoff print',label)
                    p.emulate_media(media='screen')
                    report['answer_handoff_print_layouts']+=1
                    handoff_enter(p,handoff.locator('a[href="'+answer_path+'"]'))
                    expect(p).to_have_url(base+answer_path)
                    readable_native_target(p,'#main h1',label)
                    expect(p.locator('.review-picker a')).to_have_count(6)
                    handoff_enter(p,p.locator('.review-picker a[href="#review-summary"]'))
                    expect(p).to_have_url(base+answer_path+'#review-summary')
                    readable_native_target(p,'#review-summary',label)
                    report['answer_handoff_method_choices']+=1
                    p.go_back();expect(p).to_have_url(base+answer_path)
                    # Keep the guide's context first, then follow its existing
                    # native link to the completed record in the loaded page.
                    handoff_enter(p,p.locator('a[href="#review-completed-record"]'))
                    expect(p).to_have_url(base+answer_path+'#review-completed-record')
                    readable_native_target(p,'#review-completed-title',label)
                    expect(p.locator('#review-completed-record')).to_be_visible()
                    report['answer_handoff_records']+=1
                    p.go_back();expect(p).to_have_url(base+answer_path)
                    p.go_back();expect(p).to_have_url(base+path+'#brief-next-check')
                    if javascript:
                        for key in field_keys:expect(p.locator('#brief-'+key)).to_have_value('')
                        expect(p.locator('#brief-result')).to_be_hidden()
                        expect(p.locator('#brief-text')).to_have_value('')
                        report['answer_handoff_return_clears']+=1
                    assert saved_file.read_bytes()==saved_content,('saved file after leaving',label)
                    assert p.evaluate('localStorage.length+sessionStorage.length')==0,label
                    assert c.cookies()==[],label
                    assert all(method=='GET' and 'HANDOFF_TEST_ONLY' not in url
                               for method,url in journey_requests),(label,journey_requests)
                    report['answer_handoff_journeys']+=1
                except Exception:
                    p.screenshot(path=str(screenshots/f'task-brief-handoff-failure-{width}-{javascript}.png'),full_page=True)
                    arrival=p.evaluate('''() => ({scrollY,fonts:document.fonts.status,
                        readyState:document.readyState,
                        headings:Object.fromEntries(['brief-next-check-title','review-start','review-summary','review-record','review-completed-title'].map(id=>{
                            const el=document.getElementById(id); return [id,el?el.getBoundingClientRect().toJSON():null];
                        })),
                        header:document.querySelector('.site-header')?.getBoundingClientRect().toJSON()
                    })''')
                    (screenshots/'task-brief-handoff-failure.json').write_text(
                        json.dumps({'case':label,'url':p.url,'arrival':arrival,
                                    'requests':journey_requests,'report':report},indent=2)+'\n')
                    raise
                finally:c.close()
    assert not errors,errors
    browser.close()
 print('TASK_BRIEF_REPORT='+json.dumps(report))
finally:
 if server:server.shutdown();server.server_close()
