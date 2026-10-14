"""Published essay discovery, source navigation and ordinary reading at four widths."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json
import os
from playwright.sync_api import sync_playwright,expect
from field_guide_browser import QuietHandler,ROOT
from learning_path_browser import position,SPACING
ROUTE='/living-well/ai-and-personal-productivity/'
TITLE='AI and personal productivity: what actually helps'
def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    shots=Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots:shots.mkdir(parents=True,exist_ok=True)
    errors=[];report={'viewports':0,'native_outline':0,'arrivals':0,'search':0,'axe':[]}
    try:
        with sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**opts);context=browser.new_context()
            context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            for width in [320,390,768,1440]:
                page.set_viewport_size({'width':width,'height':950});assert page.goto(origin+ROUTE).status==200
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                expect(page.locator('h1')).to_have_text(TITLE)
                expect(page.locator('.lw-article h3[id^="use-"]')).to_have_count(8)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),width
                if shots and width in [390,1440]:page.screenshot(path=str(shots/f'productivity-opening-{width}.png'))
                page.locator('.lw-outline summary').focus();page.keyboard.press('Enter')
                page.locator('.lw-outline a[href="#part-3"]').focus();page.keyboard.press('Enter')
                expect(page).to_have_url(origin+ROUTE+'#part-3');expect(page.locator('#part-3')).to_be_in_viewport()
                report['native_outline']+=1
                page.locator('.lw-article a[href="#use-paperwork"]').focus();page.keyboard.press('Enter')
                expect(page).to_have_url(origin+ROUTE+'#use-paperwork');expect(page.locator('#use-paperwork')).to_be_in_viewport()
                if shots and width in [390,1440]:
                    position(page,page.locator('#use-paperwork'));page.screenshot(path=str(shots/f'productivity-example-{width}.png'))
                    position(page,page.locator('#part-5'));page.screenshot(path=str(shots/f'productivity-comparison-{width}.png'))
                page.locator('.lw-outline a[href="#sources-and-context"]').focus();page.keyboard.press('Enter')
                expect(page).to_have_url(origin+ROUTE+'#sources-and-context')
                expect(page.locator('.lw-source-notes p')).to_have_count(10)
                page.add_style_tag(content=SPACING);assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),('spacing',width)
                if os.environ.get('AXE_PATH') and width in [390,1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    bad=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
                    assert not bad,(width,bad);report['axe'].append({'width':width,'violations':bad})
                report['viewports']+=1
            for route in ['/living-well/ideas/','/living-well/topics/everyday-ai/','/living-well/technology-for-real-life/','/living-well/did-the-tool-actually-help/','/notes/']:
                page.goto(origin+route)
                if route=='/notes/':
                    page.locator('#archive-living-well summary').press('Enter')
                    expect(page.locator('#archive-living-well')).to_have_attribute('open','')
                link=page.locator('main a[href="'+ROUTE+'"]').first
                expect(link).to_be_visible();link.press('Enter')
                page.wait_for_url(origin+ROUTE,wait_until='load');expect(page).to_have_url(origin+ROUTE)
                report['arrivals']+=1
            page.goto(origin+'/find/');page.locator('#find-query').fill('personal productivity');page.locator('#find-query').press('Enter')
            link=page.locator('main a[href="'+ROUTE+'"]:visible').first;link.focus();page.keyboard.press('Enter')
            page.wait_for_url(origin+ROUTE,wait_until='load');expect(page).to_have_url(origin+ROUTE);report['search']+=1
            expect(page.locator('.lw-article a[href="/technology/check-ai-answers/"]')).to_be_visible()
            expect(page.locator('.lw-article a[href="/living-well/did-the-tool-actually-help/"]').first).to_be_visible()
            page.emulate_media(media='print');expect(page.locator('#part-5')).to_be_visible();expect(page.locator('#use-paperwork')).to_be_visible();page.emulate_media(media='screen')
            assert page.locator('main input,main form,main textarea').count()==0
            assert page.evaluate('localStorage.length===0 && sessionStorage.length===0') and context.cookies()==[]
            nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':950})
            nojs.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            static=nojs.new_page();static.goto(origin+'/living-well/ideas/')
            static.locator('main a[href="'+ROUTE+'"]').focus();static.keyboard.press('Enter');expect(static).to_have_url(origin+ROUTE)
            static.locator('.lw-outline summary').focus();static.keyboard.press('Enter')
            static.locator('.lw-outline a[href="#part-3"]').focus();static.keyboard.press('Enter')
            static.locator('.lw-article a[href="#use-paperwork"]').focus();static.keyboard.press('Enter')
            expect(static).to_have_url(origin+ROUTE+'#use-paperwork');expect(static.locator('#use-paperwork')).to_be_in_viewport()
            assert static.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert not errors,errors;browser.close()
    finally:server.shutdown();server.server_close()
    print('PASS: researched essay, eight uses, reciprocal discovery, native outline and sources, print, no-JavaScript and no new collection surface.')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
