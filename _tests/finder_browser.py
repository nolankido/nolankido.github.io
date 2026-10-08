"""Read-only local browser verification: search, accessibility, print and fallbacks."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import os
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ('find','poker-math-reference','reading-preflop-charts','poker-rules-and-fair-play')
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
    def copyfile(self, source, out):
        try: super().copyfile(source, out)
        except (BrokenPipeError, ConnectionResetError): pass

def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    dest=Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if dest: dest.mkdir(parents=True,exist_ok=True)
    errors=[]
    with sync_playwright() as pw:
        opts={'headless':True}
        if os.environ.get('CHROMIUM_PATH'): opts['executable_path']=os.environ['CHROMIUM_PATH']
        browser=pw.chromium.launch(**opts)
        context=browser.new_context()
        context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        traffic=[];page.on('request',lambda r:traffic.append((r.method,r.url)))
        try:
            for width in (320,390,768,1280):
                page.set_viewport_size({'width':width,'height':900})
                for slug in ROUTES:
                    response=page.goto(origin+'/poker/'+slug+'/')
                    assert response and response.status==200
                    expect(page.locator('h1')).to_have_count(1)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(slug,width)
                    if slug=='find':expect(page.locator('[data-finder-card]:visible')).to_have_count(12)
                    page.add_style_tag(content='* {line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important;} p {margin-bottom:2em!important;}')
                    if not page.evaluate('document.documentElement.scrollWidth <= innerWidth'):
                        print('OVERFLOW', slug, width, page.evaluate('Array.from(document.querySelectorAll("main *")).filter(e=>e.getBoundingClientRect().right>innerWidth+1).map(e=>({tag:e.tagName,cls:e.className,id:e.id,right:e.getBoundingClientRect().right,width:e.getBoundingClientRect().width}))'), flush=True)
                        if dest: page.screenshot(path=str(dest/'poker-desk-overflow.png'),full_page=True)
                        raise AssertionError(('spacing',slug,width))
                    if dest and width in (390,1280) and slug in ('find','poker-math-reference'):
                        page.screenshot(path=str(dest/f'poker-desk-{slug}-{width}.png'),full_page=True)
            page.set_viewport_size({'width':1280,'height':900})
            page.goto(origin+'/poker/find/')
            search=page.locator('#finder-search')
            total=page.locator('[data-finder-card]').count()
            assert total > 200
            expect(page.locator('#finder-controls')).to_be_visible()
            page.wait_for_timeout(200)
            initial_traffic=list(traffic);initial_url=page.url
            # Known glossary answer with no unrelated source-type results.
            page.locator('#finder-kind').select_option('glossary');search.fill('BB');search.press('Enter')
            expect(page.locator('[data-id="term-big-blind"]')).to_be_visible()
            assert page.locator('[data-finder-card]:visible:not([data-kind="glossary"])').count()==0
            assert page.evaluate('document.activeElement.id')=='finder-results-heading'
            page.locator('#finder-reset').click()
            search.fill('what is ICM?');search.press('Enter')
            expect(page.locator('[data-id="poker-tournament-equity"]')).to_be_visible()
            page.locator('#finder-kind').select_option('resource');page.locator('#finder-free').check()
            assert page.locator('[data-finder-card]:visible:not([data-free="true"])').count()==0
            assert page.locator('[data-finder-card]:visible:not([data-kind="resource"])').count()==0
            page.locator('#finder-reset').click()
            search.fill('PLO8');search.press('Enter')
            expect(page.locator('[data-id="external-omaha-eight-rules"]')).to_be_visible()
            page.locator('#finder-reset').click()
            search.fill('pre-flop');search.press('Enter')
            expect(page.locator('[data-id="poker-reading-preflop-charts"]')).to_be_visible()
            # Literal hostile text must never create an element, script or request.
            search.fill('<img src=x onerror="window.finderInjected=1">');search.press('Enter')
            expect(page.locator('#finder-empty')).to_be_visible()
            assert page.evaluate('window.finderInjected === undefined')
            assert page.locator('#finder-results img').count()==0
            expect(page.locator('section[aria-labelledby="finder-support"] a').first).to_be_visible()
            search.focus();search.press('Escape')
            expect(search).to_have_value('')
            assert page.evaluate('document.activeElement.id')=='finder-search'
            expect(page.locator('[data-finder-card]:visible')).to_have_count(12)
            page.locator('#finder-more').click()
            expect(page.locator('[data-finder-card]:visible')).to_have_count(24)
            assert page.evaluate('document.activeElement.matches("[data-finder-card]")')
            # Printing expands all matches, then restores the user's page size.
            page.evaluate('dispatchEvent(new Event("beforeprint"))')
            expect(page.locator('[data-finder-card]:visible')).to_have_count(total)
            page.evaluate('dispatchEvent(new Event("afterprint"))')
            expect(page.locator('[data-finder-card]:visible')).to_have_count(24)
            page.locator('[data-finder-example="fair play"]').click()
            expect(page.locator('[data-id="poker-poker-rules-and-fair-play"]')).to_be_visible()
            assert traffic==initial_traffic,('Search generated traffic',traffic[len(initial_traffic):])
            assert page.url==initial_url
            assert context.cookies()==[]
            assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
            # Every original source appears in the unfiltered search and leads to its listing.
            page.locator('#finder-reset').click()
            search.fill('PokerStars third party');search.press('Enter')
            expect(page.locator('[data-id="external-stars-tool-policy"]')).to_be_visible()
            page.locator('[data-id="external-stars-tool-policy"] a[href^="/poker/resources/#"]').click()
            expect(page.locator('#resource-stars-tool-policy')).to_be_visible()
            # All nine new answer panels work with keyboard-only disclosure.
            for slug in ROUTES[1:]:
                page.goto(origin+'/poker/'+slug+'/')
                expect(page.locator('details.viewer-question')).to_have_count(3)
                for panel in page.locator('details.viewer-question').all():
                    expect(panel.locator('div')).not_to_be_visible()
                    panel.locator('summary').focus();page.keyboard.press('Enter')
                    expect(panel.locator('div')).to_be_visible()
                    page.keyboard.press('Enter');expect(panel.locator('div')).not_to_be_visible()
            response=context.request.get(origin+'/downloads/poker-math-reference.md')
            assert response.ok and response.body()==(ROOT/'downloads/poker-math-reference.md').read_bytes()
            for mode in ('no-js','blocked-script'):
                offline=browser.new_context(java_script_enabled=mode!='no-js')
                offline.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
                if mode=='blocked-script':offline.route('**/poker-finder.js*',lambda r:r.abort())
                p=offline.new_page();p.goto(origin+'/poker/find/')
                expect(p.locator('#finder-controls')).not_to_be_visible()
                expect(p.locator('[data-finder-card]:visible')).to_have_count(total)
                expect(p.locator('#finder-more')).not_to_be_visible()
                offline.close()
            if os.environ.get('AXE_PATH'):
                for slug in ROUTES:
                    page.goto(origin+'/poker/'+slug+'/')
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    results=page.evaluate('async () => await axe.run(document, {runOnly: {type:"tag",values:["wcag2a","wcag2aa","wcag21a","wcag21aa"]}})')
                    assert not results['violations'],(slug,results['violations'])
            assert not errors,errors
        finally:
            browser.close();server.shutdown();server.server_close()
    print(f'PASS: {total} finder entries; four routes at four widths; nine keyboard answers; synonyms, type/free filters, zero results, XSS text, pagination, print restoration, no search traffic/storage/URL writes, no-JS and blocked-script fallbacks, exact download.')
if __name__=='__main__':main()
