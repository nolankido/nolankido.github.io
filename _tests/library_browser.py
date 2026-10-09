"""Real local HTTP checks for local-only search, keyboard reading and blocked scripts."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import os
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def copyfile(self,source,outputfile):
        try:super().copyfile(source,outputfile)
        except (BrokenPipeError,ConnectionResetError):pass

def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    try:
        with sync_playwright() as pw:
            options={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):options['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**options)
            context=browser.new_context();errors=[];requests=[]
            context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:requests.append((r.method,r.url)))
            page.goto(origin+'/poker/library/')
            expect(page.locator('#library-controls')).to_be_visible()
            total=page.locator('#library-grid article').count()
            assert total>=22
            baseline=len(requests);url=page.url
            search=page.locator('#library-search')
            search.fill('ICM');expect(page.locator('#library-grid [data-library-card]:visible')).not_to_have_count(0)
            expect(page.locator('#library-grid a[href="/poker/tournament-equity/"]')).to_be_visible()
            page.locator('[data-filter="poker-world"]').click()
            expect(page.locator('#library-empty')).to_be_visible()
            expect(page.locator('[data-filter="poker-world"]')).to_have_attribute('aria-pressed','true')
            page.locator('#library-reset').click();expect(search).to_be_focused()
            expect(page.locator('#library-grid [data-library-card]:visible')).to_have_count(total)
            for query in ['side-pots','  SIDE   POTS  ','side pots']:
                search.fill(query);expect(page.locator('#library-grid a[href="/poker/betting-and-pots/"]')).to_be_visible()
            search.fill('<img src=x onerror=alert(1)>');expect(page.locator('#library-empty')).to_be_visible()
            assert page.locator('#poker-library img').count()==0
            search.fill('zzzz-no-match');expect(page.locator('#library-empty')).to_be_visible()
            page.locator('#library-reset').click()
            page.locator('[data-filter="poker-world"]').focus();page.keyboard.press('Space')
            expect(page.locator('#library-grid [data-library-card]:visible')).to_have_count(page.locator('#library-grid [data-topics~="poker-world"]').count())
            expect(page.locator('#library-grid a[href="/poker/hand-to-vlog/"]')).to_be_visible()
            page.locator('#library-reset').click()
            assert page.url==url
            assert len(requests)==baseline,requests[baseline:]
            assert page.evaluate('localStorage.length===0 && sessionStorage.length===0')
            assert context.cookies()==[]
            checks=0
            for width in [320,390,768,1440]:
                page.set_viewport_size({'width':width,'height':1000})
                for route in ['/poker/','/poker/library/','/poker/decision-lab/']:
                    page.goto(origin+route)
                    expect(page.locator('h1')).to_be_visible()
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(route,width)
                    if route.endswith('/decision-lab/'):
                        for panel in page.locator('details.lab-answer').all():
                            assert panel.get_attribute('open') is None
                            panel.locator('summary').focus();page.keyboard.press('Enter')
                            expect(panel.locator('div').first).to_be_visible()
                        spacing=page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),('expanded',width)
                        spacing.evaluate('(el)=>el.remove()')
                    checks+=1
            # Both disabled JavaScript and a failed library script leave every guide accessible.
            for nojs in [True,False]:
                fallback=browser.new_context(java_script_enabled=not nojs)
                fallback.route('**/*',lambda r:r.abort() if 'poker-library.js' in r.request.url or urlsplit(r.request.url).hostname!='127.0.0.1' else r.continue_())
                p=fallback.new_page();p.goto(origin+'/poker/library/')
                expect(p.locator('#library-controls')).to_be_hidden()
                expect(p.locator('#library-grid [data-library-card]:visible')).to_have_count(total)
                p.locator('#library-grid a[href="/poker/decision-lab/"]').click()
                panel=p.locator('details.lab-answer').first
                panel.locator('summary').click();expect(panel.locator('div')).to_be_visible()
                fallback.close()
            if os.environ.get('AXE_PATH'):
                for route in ['/poker/library/','/poker/decision-lab/']:
                    page.goto(origin+route);page.add_script_tag(path=os.environ['AXE_PATH'])
                    if route.endswith('/library/'):
                        page.locator('#library-search').fill('no-matching-guide');expect(page.locator('#library-empty')).to_be_visible()
                    result=page.evaluate('async()=>await axe.run(document.querySelector("main"))')
                    assert not result['violations'],[(v['id'],v['help']) for v in result['violations']]
            assert not errors,errors
            context.close();browser.close()
        print(f'PASS: {total} searchable guides; topic/search intersections; empty/reset/XSS checks; no requests, storage, cookies or URL changes from filtering; {checks} reader viewports; five keyboard disclosures; blocked-script/no-JavaScript fallbacks.')
    finally:server.shutdown();server.server_close()

if __name__=='__main__':
    main()
    from resources_browser import main as check_resources
    check_resources()
