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
    page.locator('[data-brief-example="writing"] summary').click()
    page.locator('[data-use-example="writing"]').click()
    expect(page.locator('#brief-goal')).to_be_focused()
    expect(page.locator('#brief-confirm')).to_be_hidden()
    page.locator('#brief-build').click()
    expect(page.locator('#brief-result-title')).to_be_focused()
    content=page.locator('#brief-text').input_value()
    assert content.startswith('PURPOSE\nHelp a first-time reader')
    assert 'Do not publish, send, book, buy' in content;report['functional']+=1
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
    with page.expect_download() as item:page.locator('#brief-download').click()
    download=item.value;assert download.suggested_filename=='ai-task-brief.txt'
    assert Path(download.path()).read_text()==content;report['functional']+=1
    page.locator('#brief-goal').fill('<img src=x onerror=alert(1)> & a literal task')
    expect(page.locator('#brief-result')).to_be_hidden()
    assert page.locator('#brief-text').input_value()==''
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
    for key in ['writing','planning','learning']:
        card=page.locator('[data-brief-example="'+key+'"]')
        if card.get_attribute('open') is None:card.locator('summary').click()
        card.locator('button').click()
        if page.locator('#brief-confirm').is_visible():page.locator('#brief-confirm-yes').click()
        page.locator('#brief-build').click();expect(page.locator('#brief-result')).to_be_visible()
        assert len(page.locator('#brief-text').input_value())>1000
    report['functional']+=3
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
        c=browser.new_context(java_script_enabled=mode!='disabled')
        def fallback_route(r):
            if 'task-brief.js' in r.request.url:r.abort()
            elif not args.offline and urlsplit(r.request.url).hostname=='127.0.0.1':r.continue_()
            else:r.abort()
        c.route('**/*',fallback_route)
        p=c.new_page();render(p,False)
        expect(p.locator('#brief-editor')).to_be_hidden();expect(p.locator('#brief-unavailable')).to_be_visible()
        assert p.locator('.brief-example').count()==3
        p.locator('.brief-template summary').click()
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
