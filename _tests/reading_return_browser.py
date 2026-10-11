"""Read, keep, and return journeys; --offline checks rendering without URL claims."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
import sys
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build
import poker_reading
from browser import html_for
parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');args=parser.parse_args()
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=None
if not args.offline:
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port) if server else ''
notes=[p for p in build.public_pages() if p.get('note')]
result={'offline':args.offline,'layouts':0,'spacing':0,'print':0,'outline_links':0,'url_journeys':0,'feed_downloads':0,'axe':[]}
errors=[]
try:
    with sync_playwright() as pw:
        options={'headless':True}
        if os.environ.get('CHROMIUM_PATH'):options['executable_path']=os.environ['CHROMIUM_PATH']
        browser=pw.chromium.launch(**options)
        def render(page,path):
            if args.offline:page.set_content(html_for(path))
            else:page.goto(base+path)
        for javascript in [True,False]:
            context=browser.new_context(java_script_enabled=javascript)
            context.route('**/*',lambda r:r.continue_() if not args.offline and urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            for note in notes:
                render(page,note['path'])
                summary=page.locator('.reader-outline summary');summary.focus();page.keyboard.press('Enter')
                expect(page.locator('.reader-outline')).to_have_attribute('open','')
                links=page.locator('.reader-outline a');expected=poker_reading.VisibleHeadings((ROOT/'_source'/note['source']).read_text()).headings
                assert links.count()==len(expected)
                for anchor,label in expected:
                    expect(page.locator('.reader-outline a[href="#'+anchor+'"]').first).to_be_visible()
                    if not args.offline:
                        link=page.locator('.reader-outline a[href="#'+anchor+'"]');link.focus();page.keyboard.press('Enter')
                        expect(page).to_have_url(base+note['path']+'#'+anchor)
                    result['outline_links']+=1
                page.emulate_media(media='print')
                expect(page.locator('.reader-outline')).to_be_hidden()
                expect(page.locator('.reader-next')).to_be_hidden()
                expect(page.locator('.note-keep')).to_be_hidden()
                expect(page.locator('#about-this-essay')).to_be_visible()
                expect(page.locator('.note-print-origin')).to_be_visible()
                expect(page.locator('h1')).to_be_visible()
                result['print']+=1;page.emulate_media(media='screen')
                if not args.offline:
                    page.locator('.article-navigation a[href="/follow/"]').focus();page.keyboard.press('Enter')
                    expect(page).to_have_url(base+'/follow/');result['url_journeys']+=1
            render(page,'/follow/')
            page.locator('#using-feeds summary').focus();page.keyboard.press('Enter')
            expect(page.locator('#using-feeds')).to_have_attribute('open','')
            if not args.offline:
                for route in ['/writing.xml','/feed.xml','/living-well/feed.xml','/poker/feed.xml']:
                    # Request the real same-origin feed and compare exact bytes. No external subscription.
                    response=context.request.get(base+route)
                    assert response.status==200
                    assert response.body()==(ROOT/route.lstrip('/')).read_bytes()
                    result['feed_downloads']+=1
                page.get_by_role('link',name='save the contact card',exact=True).focus();page.keyboard.press('Enter')
                expect(page).to_have_url(base+'/card/');result['url_journeys']+=1
                page.get_by_role('link',name='Follow future writing',exact=True).focus();page.keyboard.press('Enter')
                expect(page).to_have_url(base+'/follow/');result['url_journeys']+=1
            context.close()
        context=browser.new_context();context.route('**/*',lambda r:r.continue_() if not args.offline and urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
        page=context.new_page()
        for width in [320,390,768,1024,1440]:
            page.set_viewport_size({'width':width,'height':950})
            for path in ['/follow/','/card/','/notes/keep-the-judgment/']:
                render(page,path)
                for selector in ['.reader-outline','#using-feeds','.note-keep']:
                    for node in page.locator(selector).all():node.locator('summary').click()
                assert page.evaluate('document.documentElement.scrollWidth')<=width,(path,width)
                result['layouts']+=1
                if width in [390,1440] and os.environ.get('SCREENSHOT_DIR'):
                    out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                    page.evaluate("document.activeElement.blur(); window.scrollTo({top:0,behavior:'instant'})")
                    page.screenshot(path=str(out/('return-'+path.strip('/').replace('/','-')+'-'+str(width)+'.png')),full_page=True)
                if os.environ.get('AXE_PATH') and width in [390,1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    audit=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>({id:v.id,nodes:v.nodes.length})),incomplete:r.incomplete.map(v=>v.id)}}")
                    assert not audit['violations'],(path,width,audit)
                    result['axe'].append({'path':path,'width':width,**audit})
                page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                assert page.evaluate('document.documentElement.scrollWidth')<=width,('spacing',path,width)
                result['spacing']+=1
        context.close();browser.close()
    assert not errors,errors
    result['status']='pass';print(json.dumps(result,indent=2))
finally:
    if server:server.shutdown();server.server_close()
