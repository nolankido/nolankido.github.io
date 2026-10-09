"""Full-Poker navigation regressions using real HTTP, not screenshot fixtures."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import os
import sys
from playwright.sync_api import sync_playwright, expect
from finder_browser import Quiet, ROOT
sys.path.insert(0,str(ROOT/'_scripts'))
import build

def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    errors=[]
    screenshots=Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if screenshots:screenshots.mkdir(parents=True,exist_ok=True)
    try:
      with sync_playwright() as pw:
        opts={'headless':True}
        if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
        browser=pw.chromium.launch(**opts)
        context=browser.new_context()
        context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        topics=build.poker_topics.load(ROOT,build.public_pages(),build.poker_library.load(ROOT,build.public_pages()),build.poker_resources.load(ROOT))
        page.goto(origin+'/poker/library/')
        for t in topics:
            page.locator('[data-filter="'+t['id']+'"]').click()
            visible=page.locator('#library-grid [data-library-card]:visible')
            expected={'/poker/'+s+'/' for s in t['primary_guides']+t['related_guides']}
            assert set(visible.locator('h3 a').evaluate_all('(els)=>els.map(e=>e.getAttribute("href"))'))==expected,t['id']
        page.locator('#library-search').focus();page.keyboard.press('Escape')
        expect(page.locator('#library-search')).to_be_focused()
        page.locator('#library-search').fill('ICM');page.keyboard.press('Enter')
        expect(page.locator('#library-count')).to_be_focused()
        page.goto(origin+'/poker/cash-game-study-path/')
        expect(page.locator('nav[aria-label="Breadcrumb"]')).to_have_count(1)
        expect(page.locator('.viewer-breadcrumb')).to_have_count(0)
        page.locator('.reader-outline > summary').click()
        page.locator('.reader-outline a[href="#session-one"]').click()
        expect(page).to_have_url(origin+'/poker/cash-game-study-path/#session-one')
        expect(page.locator('#session-one')).to_be_in_viewport()
        page.goto(origin+'/poker/find/')
        expect(page.locator('#finder-shelf')).to_be_hidden()
        page.locator('#finder-kind').select_option('resource')
        page.locator('#finder-search').fill('unlikely-private-search');page.locator('#finder-search').press('Enter')
        expect(page.locator('#finder-empty')).to_be_visible()
        current=page.url
        page.locator('#finder-search').evaluate('(el)=>{el.value="";el.dispatchEvent(new Event("search"));}')
        expect(page.locator('#finder-empty')).to_be_hidden()
        expect(page.locator('#finder-kind')).to_have_value('resource');assert page.url==current
        page.locator('[data-finder-card]:visible .finder-save').first.click()
        expect(page.locator('#finder-shelf')).to_be_visible()
        page.locator('#finder-shelf-clear').click()
        expect(page.locator('#finder-shelf')).to_be_hidden()
        expect(page.locator('#finder-search')).to_be_focused()
        assert page.evaluate('localStorage.length===0 && sessionStorage.length===0')
        # Default mobile search is compact, but filters remain native and
        # deep-linked constraints are expanded rather than silently concealed.
        page.set_viewport_size({'width':390,'height':900})
        page.goto(origin+'/poker/find/')
        expect(page.locator('#finder-options')).not_to_have_attribute('open','')
        page.locator('#finder-options > summary').focus();page.keyboard.press('Enter')
        page.locator('#finder-kind').select_option('resource')
        page.locator('#finder-free').check()
        expect(page.locator('[data-finder-card]:visible:not([data-free="true"])')).to_have_count(0)
        page.goto(origin+'/poker/find/#topic=cash-games&kind=resource&free=1')
        expect(page.locator('#finder-options')).to_have_attribute('open','')
        expect(page.locator('#finder-topic')).to_have_value('cash-games')
        page.goto(origin+'/poker/library/')
        expect(page.locator('#library-options')).not_to_have_attribute('open','')
        page.locator('#library-options > summary').click()
        page.locator('[data-filter="cash-games"]').click()
        expect(page.locator('#library-grid a[href="/poker/cash-game-study-path/"]')).to_be_visible()
        page.locator('#library-search').focus();page.keyboard.press('Escape')
        expect(page.locator('[data-library-card]:visible')).to_have_count(47)
        page.set_viewport_size({'width':1280,'height':900})
        # All sources on every topic are now native, useful links without JS.
        nojs=browser.new_context(java_script_enabled=False)
        nojs.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
        for t in topics:
            p=nojs.new_page();p.goto(origin+'/poker/topics/'+t['id']+'/')
            summary=p.locator('.topic-all-sources > summary');summary.focus();p.keyboard.press('Enter')
            expect(p.locator('.topic-all-sources ul')).to_be_visible()
            expect(p.locator('.topic-all-sources a[rel="external"]')).to_have_count(len(t['resources']))
            p.close()
        nojs.close()
        routes=('/poker/','/poker/library/','/poker/study/','/poker/find/','/poker/topics/cash-games/','/poker/cash-game-study-path/')
        for width in (320,390,768,1280):
            page.set_viewport_size({'width':width,'height':900})
            for route in routes:
                page.goto(origin+route)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(route,width)
                if screenshots and width in (390,1280):
                    page.screenshot(path=str(screenshots/f'poker-overview-{route.strip("/").replace("/","-")}-{width}.png'),full_page=True)
                page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),('spacing',route,width)
        if os.environ.get('AXE_PATH'):
            for route in routes:
                page.goto(origin+route);page.add_script_tag(path=os.environ['AXE_PATH'])
                result=page.evaluate('async()=>await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21a","wcag21aa"]}})')
                assert not result['violations'],(route,result['violations'])
        assert not errors,errors
        browser.close()
    finally:server.shutdown();server.server_close()
    print('PASS: ten shared library subjects; native first-section jumps; one breadcrumb; empty shelf, clear/search keyboard recovery; ten complete no-JS source lists; 24 viewport and text-spacing checks; no storage or query transport.')
if __name__=='__main__':main()
