"""Multiway guide: readable arithmetic, native explanations, routes and private worksheet."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import json,os
from playwright.sync_api import sync_playwright,expect
from field_guide_browser import QuietHandler,ROOT
from learning_path_browser import SPACING
from holdem_essay_browser import position
ROUTE='/poker/limped-multiway-pots/'
TITLE='Limped and multiway pots: how to think through live poker'
ARRIVALS=['/poker/','/poker/library/','/poker/topics/cash-games/','/poker/topics/strategy/','/poker/topics/tournaments/','/poker/multiway-pot-workshop/','/poker/cash-game-study/','/poker/cash-game-study-path/','/poker/first-flop-decisions/','/poker/betting-with-a-purpose/','/poker/poker-under-uncertainty/','/notes/']

def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    shots=Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if shots:shots.mkdir(parents=True,exist_ok=True)
    report={'widths':[],'arrivals':0,'axe':[]};errors=[];writes=[]
    try:
        with sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**opts)
            context=browser.new_context(reduced_motion='reduce')
            context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:writes.append(r.url) if r.method not in ['GET','HEAD'] else None)
            for width in [320,390,768,1440]:
                page.set_viewport_size({'width':width,'height':1000})
                assert page.goto(origin+ROUTE).status==200
                page.evaluate('()=>document.fonts.ready.then(()=>true)')
                expect(page.locator('h1')).to_have_text(TITLE)
                expect(page.locator('.reader-outline').first.locator('nav a')).to_have_count(11)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
                if shots and width in [390,1440]:page.screenshot(path=str(shots/f'multiway-opening-{width}.png'))
                outline=page.locator('.reader-outline').first;outline.locator('summary').press('Enter')
                outline.locator('a[href="#bluff-math"]').press('Enter');expect(page.locator('#bluff-math')).to_be_in_viewport()
                table=page.locator('main table');expect(table).to_contain_text('30.3%')
                assert table.evaluate('e=>e.getBoundingClientRect().right<=innerWidth+1 && e.getBoundingClientRect().left>=0'),('table',width)
                if shots and width in [390,1440]:
                    position(page,table);page.screenshot(path=str(shots/f'multiway-folds-{width}.png'))
                q=page.locator('#fold-check').locator('..');expect(q.locator('details > div')).not_to_be_visible()
                q.locator('summary').press('Enter');expect(q.locator('details > div')).to_contain_text('30.25%')
                outline.locator('a[href="#cash-hand"]').press('Enter');expect(page.locator('#cash-hand')).to_be_in_viewport()
                if shots and width in [390,1440]:
                    position(page,page.locator('#cash-hand'));page.screenshot(path=str(shots/f'multiway-hand-{width}.png'))
                q=page.locator('#call-check').locator('..');q.locator('summary').press('Enter');expect(q.locator('details > div')).to_contain_text('$253')
                outline.locator('a[href="#review"]').press('Enter');expect(page.locator('#review')).to_be_in_viewport()
                page.locator('main a[href="#source-icm"]').first.press('Enter');source=page.locator('#source-icm');expect(source).to_be_in_viewport()
                metrics=source.evaluate('''async e=>{await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return {top:e.getBoundingClientRect().top,header:document.querySelector('.site-header').getBoundingClientRect().bottom}}''')
                assert metrics['top']>=metrics['header'],('source anchor',width,metrics)
                page.add_style_tag(content=SPACING);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),('spacing',width)
                if os.environ.get('AXE_PATH') and width in [390,1440]:
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    bad=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
                    assert not bad,(width,bad);report['axe'].append({'width':width,'violations':bad})
                report['widths'].append(width)
            for route in ARRIVALS:
                page.goto(origin+route)
                if route.startswith('/poker/topics/'):page.locator('details.topic-guides > summary').press('Enter')
                if route=='/notes/':page.locator('#archive-poker summary').press('Enter')
                link=page.locator('main a[href^="'+ROUTE+'"]').first;expect(link).to_be_visible();link.press('Enter')
                page.wait_for_url('**'+ROUTE+'*',wait_until='load');report['arrivals']+=1
            for query in ['limped multiway','limpers','isolation']:
                page.goto(origin+'/find/');page.locator('#find-query').fill(query);page.locator('#find-query').press('Enter')
                arrival=page.locator('.find-item a[href="'+ROUTE+'"]').first;expect(arrival).to_be_visible();arrival.press('Enter');page.wait_for_url(origin+ROUTE,wait_until='load')
            page.goto(origin+'/poker/find/');page.locator('#finder-search').fill('overlimp');page.locator('#finder-search').press('Enter')
            card=page.locator('[data-id="poker-limped-multiway-pots"]');expect(card).to_be_visible();card.locator('a[href="'+ROUTE+'"]').first.press('Enter')
            page.wait_for_url(origin+ROUTE,wait_until='load')
            page.goto(origin+'/find/');page.locator('#find-query').fill('combination of folds');page.locator('#find-query').press('Enter')
            page.locator('.find-section-matches a[href="'+ROUTE+'#bluff-math"]').press('Enter')
            page.wait_for_url(origin+ROUTE+'#bluff-math',wait_until='load');expect(page.locator('#bluff-math')).to_be_in_viewport()
            download=context.request.get(origin+'/downloads/poker-multiway-review.md');assert download.status==200
            assert page.locator('.multiway-sheet').text_content()==download.text()
            page.emulate_media(media='print');expect(page.locator('#review')).to_be_visible()
            expect(page.locator('#model-check').locator('..').locator('details > div')).to_be_visible()
            assert page.locator('main form,main input,main textarea').count()==0
            assert page.evaluate('localStorage.length===0 && sessionStorage.length===0') and context.cookies()==[]
            nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':1000})
            nojs.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            static=nojs.new_page();static.goto(origin+ROUTE)
            static.locator('.reader-outline').first.locator('summary').press('Enter');static.locator('.reader-outline').first.locator('a[href="#tools"]').press('Enter')
            expect(static.locator('#tools')).to_be_in_viewport()
            static.locator('#model-check').locator('..').locator('summary').press('Enter');expect(static.locator('#model-check').locator('..').locator('details')).to_have_attribute('open','')
            expect(static.locator('.multiway-sheet')).to_contain_text('RANGE HYPOTHESES')
            assert static.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert not errors,errors;assert not writes,writes;browser.close()
    finally:server.shutdown();server.server_close()
    if shots:(shots/'multiway-browser.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
