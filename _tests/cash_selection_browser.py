"""Cash reader routes, native selection panels, downloads and accessible reflow."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.parse import urlsplit
import os
from playwright.sync_api import sync_playwright, expect
from finder_browser import ROOT, Quiet

ROUTES=('first-live-cash-game','cash-game-costs','cash-game-study-path','choosing-study-tools','resources','topics/cash-games')

def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    dest=Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if dest: dest.mkdir(parents=True,exist_ok=True)
    errors=[]
    try:
      with sync_playwright() as pw:
        opts={'headless':True}
        if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
        browser=pw.chromium.launch(**opts)
        context=browser.new_context(accept_downloads=True)
        context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        for width in (320,390,768,1280):
          page.set_viewport_size({'width':width,'height':900})
          for route in ROUTES:
            response=page.goto(origin+'/poker/'+route+'/');assert response.status==200
            expect(page.locator('h1')).to_have_count(1)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(route,width)
            page.locator('.task-shortlist,.resource-selection,.cash-sheet,.viewer-question').evaluate_all('(nodes)=>nodes.forEach(n=>n.open=true)')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),('expanded',route,width)
            if dest and width in (390,1280) and route in ('cash-game-costs','cash-game-study-path','choosing-study-tools'):
                page.screenshot(path=str(dest/f'poker-cash-{route}-{width}.png'),full_page=True)
            page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),('spacing',route,width)
        page.set_viewport_size({'width':1280,'height':900})
        page.goto(origin+'/poker/topics/cash-games/')
        page.locator('.topic-steps a[href="/poker/cash-game-study-path/"]').focus();page.keyboard.press('Enter')
        expect(page).to_have_url(origin+'/poker/cash-game-study-path/')
        page.locator('.article-body a[href="/poker/first-live-cash-game/"]').click()
        expect(page).to_have_url(origin+'/poker/first-live-cash-game/')
        page.get_by_role('link',name='Next: understand the charges',exact=True).click()
        expect(page).to_have_url(origin+'/poker/cash-game-costs/')
        expect(page.locator('table caption')).to_have_text('Same pot, different deductions')
        expect(page.locator('tbody tr')).to_have_count(3)
        page.locator('.viewer-question summary').first.focus();page.keyboard.press('Enter')
        expect(page.locator('.viewer-question').first).to_have_attribute('open','')
        expect(page.locator('.viewer-question').first).to_contain_text('7 removed, 113 awarded')
        page.goto(origin+'/poker/cash-game-study-path/')
        with page.expect_download() as pending:
            page.get_by_role('link',name='Download the cash-game study sheet',exact=True).click()
        with TemporaryDirectory() as tmp:
            target=Path(tmp)/'cash.md';pending.value.save_as(target)
            assert target.read_bytes()==(ROOT/'downloads/poker-cash-study.md').read_bytes()
        page.locator('.cash-sheet summary').click()
        expect(page.locator('.cash-sheet pre')).to_have_text((ROOT/'downloads/poker-cash-study.md').read_text())
        page.get_by_role('link',name='Next: choose a resource by its job',exact=True).click()
        expect(page).to_have_url(origin+'/poker/choosing-study-tools/#task-shortlists')
        groups=page.locator('.task-shortlist');expect(groups).to_have_count(3)
        summary=groups.nth(1).locator(':scope > summary')
        expect(summary).to_have_count(1);summary.focus();page.keyboard.press('Enter')
        expect(groups.nth(1)).to_have_attribute('open','')
        expect(groups.nth(1).locator('.selection-option')).to_have_count(2)
        expect(groups.nth(1)).to_contain_text('Free');expect(groups.nth(1)).to_contain_text('Paid')
        panel=groups.nth(1).locator('.resource-selection').first
        panel.locator('summary').click();expect(panel.locator('dl')).to_be_visible()
        page.goto(origin+'/poker/resources/#resource-pot-odds')
        item=page.locator('#resource-pot-odds .resource-selection');item.locator('summary').click()
        expect(item.locator('dt')).to_have_count(4)
        item.locator('a[href="/poker/resources/#resource-equity-realization"]').click()
        expect(page.locator('#resource-equity-realization')).to_be_visible()
        page.goto(origin+'/poker/find/')
        page.locator('#finder-kind').select_option('resource')
        page.locator('#finder-search').fill('tree-building workflow');page.locator('#finder-search').press('Enter')
        expect(page.locator('[data-id="external-pio-quick-start"]')).to_be_visible()
        page.locator('#finder-reset').click();page.locator('#finder-topic').select_option('cash-games')
        page.locator('#finder-kind').select_option('resource');page.locator('#finder-free').check()
        page.evaluate('dispatchEvent(new Event("beforeprint"))')
        visible=page.locator('[data-finder-card]:visible')
        assert visible.count()>0
        assert visible.evaluate_all('(els)=>els.every(e=>e.dataset.free==="true" && e.dataset.topics.split(" ").includes("cash-games"))')
        page.evaluate('dispatchEvent(new Event("afterprint"))')
        assert page.evaluate('localStorage.length===0 && sessionStorage.length===0')
        # Details and the complete directory remain useful without any JavaScript.
        nojs=browser.new_context(java_script_enabled=False)
        nojs.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
        p=nojs.new_page();p.goto(origin+'/poker/resources/#resource-equilab')
        p.locator('#resource-equilab .resource-selection summary').click()
        expect(p.locator('#resource-equilab .resource-selection dl')).to_be_visible()
        p.goto(origin+'/poker/choosing-study-tools/')
        p.locator('.task-shortlist').nth(1).locator(':scope > summary').click()
        expect(p.locator('.task-shortlist').nth(1).locator('.selection-option')).to_have_count(2)
        nojs.close()
        page.goto(origin+'/poker/cash-game-study-path/');page.emulate_media(media='print')
        expect(page.locator('.cash-sheet pre')).to_be_visible()
        page.emulate_media(media='screen');expect(page.locator('.cash-sheet')).not_to_have_attribute('open','')
        if os.environ.get('AXE_PATH'):
            for route in ROUTES:
                page.goto(origin+'/poker/'+route+'/')
                page.locator('.task-shortlist,.resource-selection').evaluate_all('(els)=>els.forEach(e=>e.open=true)')
                page.add_script_tag(path=os.environ['AXE_PATH'])
                result=page.evaluate('async()=>await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21a","wcag21aa"]}})')
                assert not result['violations'],(route,result['violations'])
        assert not errors,errors
        browser.close()
    finally:
        server.shutdown();server.server_close()
    print('PASS: cash-game route, 24 viewport checks plus expanded/text spacing, task-fit panels, source alternatives, search, free filters, byte-matched worksheet, no-JS and print. No real submissions.')

if __name__=='__main__':main()
