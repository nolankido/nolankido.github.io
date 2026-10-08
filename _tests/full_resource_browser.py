"""Reader tasks for full-text search, portable lists and scoped study calculations."""
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
import os
from playwright.sync_api import sync_playwright, expect
from finder_browser import Quiet, ROOT

ROUTES=('find','omaha-hi-lo-workshop','stud-and-lowball-workshop','multiway-pot-workshop','poker-media-study','poker-access-and-protection','study-calculators','resource-quality')
def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    dest=Path(os.environ['SCREENSHOT_DIR']) if os.environ.get('SCREENSHOT_DIR') else None
    if dest:dest.mkdir(parents=True,exist_ok=True)
    errors=[]
    try:
      with sync_playwright() as pw:
        options={'headless':True}
        if os.environ.get('CHROMIUM_PATH'):options['executable_path']=os.environ['CHROMIUM_PATH']
        browser=pw.chromium.launch(**options)
        context=browser.new_context(accept_downloads=True)
        context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        traffic=[];page.on('request',lambda r:traffic.append(r.url))
        for width in (320,390,768,1280):
            page.set_viewport_size({'width':width,'height':900})
            for slug in ROUTES:
                response=page.goto(origin+'/poker/'+slug+'/');assert response.status==200
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(slug,width)
                if dest and width in (390,1280) and slug in ('study-calculators','resource-quality'):
                    page.screenshot(path=str(dest/f'poker-full-{slug}-{width}.png'),full_page=True)
                page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),('spacing',slug,width)
        page.set_viewport_size({'width':1280,'height':900});page.goto(origin+'/poker/find/')
        original_url=page.url;initial=len(traffic)
        # A real unanchored h2 remains searchable, but must not promise a jump.
        page.locator('#finder-search').fill('references limits')
        page.locator('#finder-search').press('Enter')
        unanchored=page.locator('[data-id="poker-pot-odds-workshop"]')
        # This generic query can put the guide on a later native results page.
        for _ in range(30):
            if unanchored.is_visible() or not page.locator('#finder-more').is_visible():break
            page.locator('#finder-more').click()
        expect(unanchored).to_be_visible()
        expect(unanchored.locator('.finder-excerpt')).to_be_visible()
        expect(unanchored.locator('.finder-jump')).to_be_hidden()
        assert unanchored.locator('.finder-jump a').get_attribute('href') is None
        page.locator('#finder-reset').click()
        page.locator('#finder-topic').select_option('cash-games')
        assert page.url==original_url+'#topic=cash-games'
        search=page.locator('#finder-search');search.fill('conditional probabilities');search.press('Enter')
        card=page.locator('[data-id="poker-multiway-pot-workshop"]');expect(card).to_be_visible()
        expect(card.locator('.finder-jump a')).to_have_attribute('href','/poker/multiway-pot-workshop/#joint-folds')
        expect(card.locator('.finder-excerpt')).to_contain_text('conditional probabilities')
        card.locator('.finder-save').click();expect(card.locator('.finder-save')).to_have_attribute('aria-pressed','true')
        page.locator('#finder-reset').click();page.locator('#finder-kind').select_option('resource')
        search.fill('Internet gaming');search.press('Enter')
        page.locator('[data-id="external-nj-dge-information"] .finder-save').click()
        search.fill('PRIVATE_SEARCH_TOKEN');search.press('Enter')
        expect(page.locator('#finder-empty')).to_be_visible()
        expect(page.locator('#finder-shelf-count')).to_contain_text('2 of 12')
        with page.expect_download() as pending:page.locator('#finder-shelf-download').click()
        download=pending.value;assert download.suggested_filename=='poker-study-list.md'
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'study.md';download.save_as(path);content=path.read_text()
            assert 'PRIVATE_SEARCH_TOKEN' not in content
            assert 'conditional probabilities' not in content
            assert '403' in content and 'Search index only' in content
            assert 'https://nolankido.com/poker/multiway-pot-workshop/' in content
        assert len(traffic)==initial
        assert page.url==original_url+'#kind=resource'
        assert 'PRIVATE_SEARCH_TOKEN' not in page.url
        assert page.evaluate('localStorage.length===0 && sessionStorage.length===0')
        page.locator('#finder-shelf-clear').click();page.locator('#finder-reset').click()
        for button in page.locator('[data-finder-card]:visible .finder-save').all():button.click()
        expect(page.locator('#finder-shelf-count')).to_contain_text('12 of 12')
        page.locator('#finder-more').click();page.locator('[data-finder-card]:visible .finder-save').nth(12).click()
        expect(page.locator('#finder-shelf-count')).to_contain_text('Remove one')
        assert page.locator('#finder-shelf-list li').count()==12
        page.reload();expect(page.locator('#finder-shelf-count')).to_contain_text('0 of 12')
        page.goto(origin+'/poker/study-calculators/');initial=len(traffic);tool_url=page.url
        for mode,needle in [('call','30.00%'),('bluff','42.86%'),('potlimit','390')]:
            panel=page.locator('[data-study-tool="'+mode+'"]');panel.locator('[data-tool-run]').click()
            expect(panel.locator('[data-tool-output]')).to_contain_text(needle)
        panel=page.locator('[data-study-tool="potlimit"]')
        for committed,total in [('0','100'),('10','110')]:
            for field,value in zip(panel.locator('input').all(),['100','0',committed]):field.fill(value)
            panel.locator('[data-tool-run]').click()
            expect(panel.locator('[data-tool-output]')).to_contain_text('Maximum new chips to put in: 100.')
            expect(panel.locator('[data-tool-output]')).to_contain_text('including existing chips: '+total+'.')
        for mode in ['call','bluff']:
            other=page.locator('[data-study-tool="'+mode+'"]')
            other.locator('input').nth(1).fill('0');other.locator('[data-tool-run]').click()
            expect(other.locator('[data-tool-output]')).to_contain_text('Check the inputs')
        for field,value in zip(panel.locator('input').all(),['500','70','80']):field.fill(value)
        panel.locator('input').last.press('Enter');expect(panel.locator('[data-tool-output]')).to_contain_text('720')
        panel.locator('input').first.fill('<img>');panel.locator('[data-tool-run]').click()
        expect(panel.locator('[data-tool-output]')).to_contain_text('Check the inputs')
        assert panel.locator('img').count()==0
        panel.locator('[data-tool-clear]').click();expect(panel.locator('input').first).to_have_value('210')
        assert len(traffic)==initial and page.url==tool_url
        assert page.evaluate('localStorage.length===0 && sessionStorage.length===0') and context.cookies()==[]
        for slug in ROUTES[1:6]:
            page.goto(origin+'/poker/'+slug+'/')
            for question in page.locator('details.viewer-question').all():
                expect(question.locator('div')).to_be_hidden()
                question.locator('summary').focus();page.keyboard.press('Enter');expect(question.locator('div')).to_be_visible()
                page.keyboard.press('Enter');expect(question.locator('div')).to_be_hidden()
        if os.environ.get('AXE_PATH'):
            axe=Path(os.environ['AXE_PATH']).read_text()
            for slug in ROUTES:
                page.goto(origin+'/poker/'+slug+'/');page.add_script_tag(content=axe)
                result=page.evaluate('async()=>await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa"]}})')
                assert not result['violations'],(slug,result['violations'])
        offline=browser.new_context(java_script_enabled=False)
        offline.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
        static=offline.new_page();static.goto(origin+'/poker/find/')
        expect(static.locator('#finder-controls')).to_be_hidden();expect(static.locator('#finder-shelf')).to_be_hidden()
        details=static.locator('[data-id="poker-multiway-pot-workshop"] details.finder-text')
        details.locator('summary').click();expect(details).to_contain_text('conditional probabilities')
        static.goto(origin+'/poker/study-calculators/');expect(static.locator('[data-tool-controls]:visible')).to_have_count(0)
        expect(static.locator('[data-tool-output]')).to_have_count(3)
        static.emulate_media(media='print');expect(static.locator('[data-tool-output]:visible')).to_have_count(3)
        assert not errors,errors
        browser.close()
    finally:server.shutdown();server.server_close()
    print('PASS: full-text section retrieval, bounded portable study lists, query-free export, calculator arithmetic/validation, 15 keyboard answers, eight routes at four widths, no-JS and privacy boundaries.')
if __name__=='__main__':main()
