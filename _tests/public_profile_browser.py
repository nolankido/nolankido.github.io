"""Public-profile reuse and core CSS parity. No real messages or clipboard writes.

HTTP mode checks real local asset requests and downloads. --offline uses the
same checked-out page bytes in memory, without claiming native HTTP coverage.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import argparse
import faulthandler
import json
import os
import re
import sys
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import core_styles
import build
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--offline',action='store_true')
args=parser.parse_args()
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=None
if not args.offline:
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port) if server else ''
site=json.loads((ROOT/'_source/site.json').read_text())
expected={'profile-short-text':site['bio_short'],'profile-long-text':site['bio_long'],'profile-site-url':site['url']+'/'}
report={'offline':args.offline,'copy_checks':0,'fallback_checks':0,'downloads':0,'layouts':0,'text_spacing':0,'parity_comparisons':0,'http_asset_checks':0,'journeys':0,'axe':[]}
errors=[]
spacing='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}'

def document(path,reference=False):
    html=(ROOT/build.output_path(path)).read_text()
    if reference:
        old='\n'.join('<link rel="stylesheet" href="/'+s+'">' for s in core_styles.SOURCES)
        html=re.sub(r'<link rel="stylesheet" href="/assets/site-core\.css\?v=[a-f0-9]+">',old,html)
    return html

def offline_html(html):
    def inline(match):
        tag=match.group();href=re.search(r'href="([^"]+)"',tag).group(1)
        url=urlsplit(href)
        return '' if url.scheme or url.netloc else '<style>'+(ROOT/url.path.lstrip('/')).read_text()+'</style>'
    return re.sub(r'<link rel="stylesheet"[^>]*>',inline,html)

def setup_route(context,requests,reference=False,block_profile=False):
    def route(r):
        requests.append(r.request.url)
        parsed=urlsplit(r.request.url)
        if block_profile and parsed.path=='/assets/public-profile.js':r.abort()
        elif not args.offline and parsed.hostname=='127.0.0.1':
            if reference and r.request.resource_type=='document':
                r.fulfill(status=200,content_type='text/html',body=document(parsed.path,True))
            else:r.continue_()
        else:r.abort()
    context.route('**/*',route)

def render(page,path,reference=False,execute=True):
    if args.offline:
        page.set_content(offline_html(document(path,reference)))
        if path=='/bio/' and execute:page.add_script_tag(content=(ROOT/'assets/public-profile.js').read_text())
    else:page.goto(base+path)

faulthandler.dump_traceback_later(300,exit=True)
try:
 with sync_playwright() as pw:
    opts={'headless':True}
    if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
    browser=pw.chromium.launch(**opts)
    context=browser.new_context(accept_downloads=True);requests=[];setup_route(context,requests)
    page=context.new_page();page.set_default_timeout(15000);page.on('pageerror',lambda e:errors.append(str(e)))
    render(page,'/bio/');page.wait_for_timeout(100)
    initial_requests=len(requests);initial_url=page.url
    for id,text in expected.items():
        page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.publicCopy=text;}}})")
        button=page.locator('[data-profile-copy="'+id+'"]');expect(button).to_be_visible()
        button.focus();page.keyboard.press('Enter')
        expect(page.locator('#profile-copy-status')).to_contain_text('copied.')
        assert page.evaluate('window.publicCopy')==text
        report['copy_checks']+=1
    for mode in ['denied','missing']:
        value="{writeText:async()=>{throw new Error('Denied')}}" if mode=='denied' else 'undefined'
        page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:"+value+"})")
        page.locator('[data-profile-copy="profile-short-text"]').click()
        expect(page.locator('#profile-copy-status')).to_contain_text('Automatic copy is unavailable')
        expect(page.locator('#profile-short-text')).to_be_focused()
        assert page.evaluate('window.getSelection().toString()')==site['bio_short']
        report['fallback_checks']+=1
    assert len(requests)==initial_requests
    assert page.url==initial_url
    if not args.offline:
        assert page.evaluate('localStorage.length+sessionStorage.length')==0
        assert context.cookies()==[]
        for name in ['short','long']:
            with page.expect_download() as info:page.locator('a[download][href="/downloads/nolan-kido-'+name+'-bio.txt"]').click()
            assert Path(info.value.path()).read_bytes()==(ROOT/'downloads'/('nolan-kido-'+name+'-bio.txt')).read_bytes()
            report['downloads']+=1
        page.locator('a[href="/technology/checking-ai-website-changes/"]').focus();page.keyboard.press('Enter')
        expect(page).to_have_url(base+'/technology/checking-ai-website-changes/');report['journeys']+=1
        page.goto(base+'/about/');page.locator('a[href="/bio/"]').focus();page.keyboard.press('Enter')
        expect(page).to_have_url(base+'/bio/');report['journeys']+=1
    for width in [320,390,768,1440]:
        page.set_viewport_size({'width':width,'height':950});render(page,'/bio/')
        page.evaluate('document.activeElement.blur(); window.scrollTo({top:0,left:0,behavior:"instant"})')
        page.wait_for_timeout(50)
        assert page.evaluate('document.documentElement.scrollWidth')<=width
        report['layouts']+=1
        style=page.add_style_tag(content=spacing)
        assert page.evaluate('document.documentElement.scrollWidth')<=width
        report['text_spacing']+=1;style.evaluate('(el)=>el.remove()')
        if width in [390,1440] and os.environ.get('SCREENSHOT_DIR'):
            out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
            page.screenshot(path=str(out/('profile-'+str(width)+'.png')),full_page=True)
        if width in [390,1440] and os.environ.get('AXE_PATH'):
            page.add_script_tag(path=os.environ['AXE_PATH'])
            result=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>v.id),incomplete:r.incomplete.map(v=>v.id)}}")
            assert not result['violations'],result
            report['axe'].append({'width':width,**result})
    page.emulate_media(media='print');expect(page.locator('[data-profile-copy]').first).to_be_hidden()
    expect(page.locator('#profile-short-text')).to_be_visible();expect(page.locator('#profile-selected-work')).to_be_visible()
    page.emulate_media(media='screen');context.close()
    for mode in ['disabled','blocked']:
        context=browser.new_context(java_script_enabled=mode!='disabled',accept_downloads=True)
        setup_route(context,[],block_profile=True)
        page=context.new_page();render(page,'/bio/',execute=False)
        for id,text in expected.items():expect(page.locator('#'+id)).to_have_text(text)
        for button in page.locator('[data-profile-copy]').all():expect(button).to_be_hidden()
        for width in [320,390,768,1440]:
            page.set_viewport_size({'width':width,'height':950})
            assert page.evaluate('document.documentElement.scrollWidth')<=width
            report['layouts']+=1
            page.evaluate('css=>{const s=document.createElement("style");s.id="spacing-check";s.textContent=css;document.head.appendChild(s)}',spacing)
            assert page.evaluate('document.documentElement.scrollWidth')<=width
            report['text_spacing']+=1
            page.evaluate('document.getElementById("spacing-check").remove()')
        if not args.offline:
            for name in ['short','long']:
                with page.expect_download() as info:page.locator('a[download][href="/downloads/nolan-kido-'+name+'-bio.txt"]').click()
                assert Path(info.value.path()).read_bytes()==(ROOT/'downloads'/('nolan-kido-'+name+'-bio.txt')).read_bytes()
                report['downloads']+=1
        report['fallback_checks']+=1;context.close()
    # Compare actual layout and computed styles with three original stylesheet
    # requests versus one bundled request, without changing source declarations.
    paths=['/','/about/','/technology/','/creative/','/poker/reviewing-a-hand/','/living-well/shared-plan-people-can-use/']
    signature="""()=>Array.from(document.body.querySelectorAll('*')).filter(el=>!['SCRIPT','STYLE'].includes(el.tagName)).map(el=>{const s=getComputedStyle(el),r=el.getBoundingClientRect();return [el.tagName,el.id,...['display','fontFamily','fontSize','fontWeight','lineHeight','color','backgroundColor','margin','padding','borderWidth','whiteSpace','gridTemplateColumns'].map(p=>s[p]),r.x,r.y,r.width,r.height]})"""
    for width in [320,768,1440]:
        for path in paths:
            snapshots=[]
            for reference in [True,False]:
                context=browser.new_context(viewport={'width':width,'height':950});req=[];setup_route(context,req,reference)
                page=context.new_page();render(page,path,reference);page.wait_for_timeout(50)
                snapshots.append(page.evaluate(signature))
                if not args.offline:
                    styles=[urlsplit(u).path for u in req if urlsplit(u).path in ['/'+p for p in core_styles.SOURCES]+['/assets/site-core.css']]
                    assert sorted(styles)==sorted(['/'+p for p in core_styles.SOURCES] if reference else ['/assets/site-core.css']),(path,reference,styles)
                    report['http_asset_checks']+=1
                context.close()
            assert snapshots[0]==snapshots[1],('Core stylesheet presentation differs',path,width)
            report['parity_comparisons']+=1
    assert not errors,errors
    browser.close()
 print('PUBLIC_PROFILE_REPORT='+json.dumps(report))
finally:
 if server:server.shutdown();server.server_close()
 faulthandler.cancel_dump_traceback_later()
