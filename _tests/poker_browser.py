"""Test populated publishing/reader paths in a disposable copy. Never publish fixtures."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.parse import urlsplit
import json
import os
import shutil
import subprocess
import sys
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_tests'))
from test_poker_content import fixture

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass


def run():
    with TemporaryDirectory() as d:
        root=Path(d)/'site'
        shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','__pycache__'))
        episode=fixture(); hand=fixture('hand','test-hand'); story=fixture('story','test-story')
        episode['related']=['test-hand']; hand['related']=['test-story']
        story['sources']=[{'label':'Review method','url':'https://nolankido.com/poker/reviewing-a-hand/#after-the-session'}]
        episode['sections'][0]['paragraphs']=['<script>window.unwanted = true</script>']
        (root/'_source/poker/catalog.json').write_text(json.dumps({'version':1,'entries':[episode,hand,story]}))
        subprocess.run([sys.executable,str(root/'_scripts/build.py')],cwd=root,check=True)
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)))
        Thread(target=server.serve_forever,daemon=True).start()
        base='http://127.0.0.1:'+str(server.server_port)
        errors=[]; media=[]; violations=[]
        paths=['/poker/','/poker/start-here/','/poker/study/','/poker/reviewing-a-hand/',
               '/poker/episodes/test-episode/','/poker/hands/test-hand/','/poker/stories/test-story/']
        try:
            with sync_playwright() as p:
                opts={'headless':True}
                if os.getenv('CHROMIUM_PATH'): opts['executable_path']=os.environ['CHROMIUM_PATH']
                browser=p.chromium.launch(**opts)
                context=browser.new_context(accept_downloads=True)
                def intercept(r):
                    host=urlsplit(r.request.url).hostname
                    if host and ('youtube' in host or 'ytimg' in host or host=='youtu.be'): media.append(r.request.url)
                    r.continue_() if host=='127.0.0.1' else r.abort()
                context.route('**/*',intercept)
                page=context.new_page(); page.on('pageerror',lambda e:errors.append(str(e)))
                for width in [320,390,768,1024,1440]:
                    page.set_viewport_size({'width':width,'height':900})
                    for route in paths:
                        response=page.goto(base+route); assert response.status==200
                        expect(page.locator('h1')).to_be_visible()
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(route,width)
                        page.locator('details').evaluate_all('(items)=>items.forEach(x=>x.open=true)')
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(route,width,'expanded')
                        if os.getenv('AXE_PATH') and width in [320,1440]:
                            page.add_script_tag(path=os.environ['AXE_PATH'])
                            result=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
                            if result: violations.append({'route':route,'width':width,'violations':result})
                        page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(route,width,'spacing')
                page.goto(base+'/poker/')
                feature=page.locator('#featured-work .reader-feature-link')
                expect(feature).to_have_attribute('href','/poker/stories/test-story/')
                assert page.locator('#featured-work').bounding_box()['y'] < page.locator('.poker-paths').bounding_box()['y']
                feature.focus(); page.keyboard.press('Enter')
                expect(page).to_have_url(base+'/poker/stories/test-story/')
                expect(page.locator('a[href="https://nolankido.com/poker/reviewing-a-hand/#after-the-session"]')).to_be_visible()
                page.goto(base+'/poker/reviewing-a-hand/#after-the-session')
                back=page.locator('[aria-labelledby="context-reading-title"] a[href="/poker/stories/test-story/"]')
                back.focus(); page.keyboard.press('Enter')
                expect(page).to_have_url(base+'/poker/stories/test-story/')
                page.goto(base+'/poker/')
                page.locator('.poker-content-grid a[href="/poker/episodes/test-episode/"]').click()
                expect(page.locator('.poker-watch a')).to_have_attribute('href','https://www.youtube.com/watch?v=abcdefghijk')
                expect(page.locator('.poker-chapters a').nth(1)).to_have_attribute('href','https://www.youtube.com/watch?v=abcdefghijk&t=150s')
                expect(page.locator('.poker-details')).not_to_have_attribute('open','')
                expect(page.get_by_text('Synthetic result, not a real result.',exact=True)).to_be_hidden()
                page.locator('.poker-details summary').focus(); page.keyboard.press('Enter')
                expect(page.get_by_text('Synthetic result, not a real result.',exact=True)).to_be_visible()
                assert page.evaluate('window.unwanted === undefined')
                page.locator('a[href="/poker/hands/test-hand/"]').click()
                expect(page.get_by_text('Illustrative hand. This did not occur in a recorded session.',exact=True)).to_be_visible()
                assert page.locator('a[href="/poker/episodes/test-episode/"]').count()==1
                page.goto(base+'/poker/study/')
                for name in ['poker-hand-review','poker-session-debrief']:
                    with page.expect_download() as info:
                        page.locator(f'a[href="/downloads/{name}.md"]').click()
                    assert Path(info.value.path()).read_bytes()==(root/'downloads'/f'{name}.md').read_bytes()
                assert not errors,errors
                assert not media,media
                assert not violations,violations
                browser.close()
            print('PASS: 35 populated-poker route/viewport checks; expanded disclosures, text-spacing, chapter URLs, real-work feature, guide return links, escaped text, keyboard spoilers, 2 exact downloads, and no video requests. Synthetic content stayed in a temporary directory. Accessibility scans enabled: '+str(bool(os.getenv('AXE_PATH'))))
        finally:
            server.shutdown();server.server_close()

if __name__=='__main__':run()
