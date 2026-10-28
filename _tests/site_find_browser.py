"""Real-page discovery checks. Use --offline for in-memory interaction/layout only.

Default CI mode tests actual local URLs and keyboard journeys. Both modes block
all external traffic. Search terms must cause no additional network request.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import os
import sys
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,site_find
OFFLINE='--offline' in sys.argv
if OFFLINE:
    from browser import html_for
items=site_find.entries(ROOT,build.public_pages())
title_queries=[('pot odds calculator','/poker/study-calculators/'),
               ('Texas Holdem rules','/poker/holdem-basics/'),
               ('AI assisted reflection prompts','/living-well/reflection-with-your-judgment-intact/')]
cross_interest_queries=[
    ('creative','book continuity','/technology/ai-book-continuity-checker/'),
    ('living-well','cooking planner','/technology/dinner-on-time/'),
    ('living-well','weekly reset','/technology/ai-weekly-reset/'),
    ('living-well','organize notes','/technology/organize-public-notes/'),
    ('technology','personal productivity','/living-well/ai-and-personal-productivity/'),
]
server=None
if not OFFLINE:
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port) if server else 'about:blank'
errors=[]
def load(page,script=True):
    if OFFLINE:
        page.set_content(html_for('/find/'))
        if script:page.add_script_tag(content=(ROOT/'assets/site-find.js').read_text())
    else:
        assert page.goto(base+'/find/').status==200

def set_query(page,text):
    page.locator('#find-query').fill(text)
    page.locator('#find-query').press('Enter')
    expect(page.locator('#find-results')).to_be_focused()

try:
    with sync_playwright() as p:
        opts={'headless':True}
        if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
        browser=p.chromium.launch(**opts)
        context=browser.new_context()
        context.route('**/*',lambda r:r.continue_() if not OFFLINE and urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        load(page);expect(page.locator('#find-controls')).to_be_visible()
        assert page.locator('.find-item').count()==len(items)
        requests=[];page.on('request',lambda r:requests.append(r.url))
        before=page.url
        # Live typing and input-method composition must retain the editor.
        query=page.locator('#find-query')
        query.fill('family story')
        expect(page.locator('.find-item:visible h3 a[href="/living-well/preserve-family-story/"]')).to_be_visible()
        expect(query).to_be_focused()
        original_status=page.locator('#find-status').inner_text()
        query.evaluate("x=>{x.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true}));x.value='pot odds';x.dispatchEvent(new InputEvent('input',{bubbles:true,isComposing:true}));}")
        for flags in [{'isComposing':True,'keyCode':13},{'isComposing':False,'keyCode':229}]:
            allowed=query.evaluate("(x,flags)=>x.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true,cancelable:true,...flags}))",flags)
            assert allowed,'Composition Enter must retain its native default'
            expect(query).to_be_focused()
        page.wait_for_timeout(200)
        expect(page.locator('#find-status')).to_have_text(original_status)
        query.evaluate("x=>x.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true}))")
        expect(page.locator('.find-item:visible h3 a[href="/poker/pot-odds-workshop/"]')).to_be_visible()
        expect(query).to_be_focused()
        # Explicit button submission should offer the same keyboard handoff.
        for activation in ['click','Enter','Space']:
            query.fill('family story')
            button=page.locator('#find-submit')
            if activation=='click':button.click()
            else:button.press(activation)
            expect(page.locator('#find-results')).to_be_focused()
            page.keyboard.press('Tab')
            expect(page.locator('.find-group:not([hidden]) summary').first).to_be_focused()
            page.keyboard.press('Tab')
            expect(page.locator('.find-item:visible h3 a').first).to_be_focused()
        for field,value in [('find-interest','creative'),('find-kind','guide')]:
            control=page.locator('#'+field);control.focus();control.select_option(value)
            expect(control).to_be_focused()
        page.locator('#find-reset').click()
        for query,destination in [('family story','/living-well/preserve-family-story/'),('how do I review a hand','/poker/reviewing-a-hand/'),('AI','/notes/keep-the-judgment/')]+title_queries:
            set_query(page,query)
            expect(page.locator('.find-item:not([hidden]) a[href="'+destination+'"]')).to_be_visible()
        page.locator('#find-interest').select_option('creative')
        page.locator('#find-kind').select_option('guide')
        set_query(page,'family story')
        expect(page.locator('.find-item:visible')).to_have_count(1)
        expect(page.locator('.find-item:visible h3 a')).to_have_attribute('href','/living-well/preserve-family-story/')
        for interest,query,destination in cross_interest_queries:
            page.locator('#find-reset').click()
            page.locator('#find-interest').select_option(interest)
            set_query(page,query)
            link=page.locator('.find-item h3 a[href="'+destination+'"]')
            expect(link).to_have_count(1)
            expect(link).to_be_visible()
            page.locator('#find-interest').select_option('poker')
            expect(link).to_be_hidden()
        for query in ['zznotarealpage','???','the and','<img src=x onerror=alert(1)>']:
            set_query(page,query);expect(page.locator('#find-empty')).to_be_visible()
            expect(page.locator('.find-item:visible')).to_have_count(0)
        expect(page.locator('.find-item img')).to_have_count(0)
        page.locator('#find-reset').click()
        expect(page.locator('#find-query')).to_be_focused()
        expect(page.locator('#find-query')).to_have_value('')
        expect(page.locator('#find-interest')).to_have_value('')
        expect(page.locator('#find-kind')).to_have_value('')
        assert page.locator('.find-item:not([hidden])').count()==len(items)
        assert page.url==before
        assert not requests,requests
        assert context.cookies()==[]
        if not OFFLINE:
            assert page.evaluate('localStorage.length + sessionStorage.length')==0
        for width in [320,390,768,1024,1440]:
            page.set_viewport_size({'width':width,'height':900})
            for query in ['', 'family story', 'zznoresults']:
                set_query(page,query)
                expect(page.locator('#find-results')).to_be_in_viewport()
                assert page.locator('#find-results').evaluate('h=>h.getBoundingClientRect().top>=document.querySelector(".site-header").getBoundingClientRect().bottom+4'),'Focused results must clear the sticky header'
                assert page.evaluate('document.documentElement.scrollWidth')<=width,(width,query)
                if os.environ.get('SCREENSHOT_DIR') and width in [390,1440]:
                    out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                    name='browse' if not query else 'family' if query=='family story' else 'empty'
                    if query:page.screenshot(path=str(out/f'find-submitted-{name}-{width}.png'))
                    page.screenshot(path=str(out/f'find-{name}-{width}.png'),full_page=True)
                spacing=page.add_style_tag(content='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                set_query(page,query)
                assert page.locator('#find-results').evaluate('h=>h.getBoundingClientRect().top>=document.querySelector(".site-header").getBoundingClientRect().bottom+4'),'Expanded-text results must clear the sticky header'
                assert page.evaluate('document.documentElement.scrollWidth')<=width,('text-spacing',width,query)
                spacing.evaluate('(el)=>el.remove()')
        # Context-specific type and interest filters work without a query.
        page.locator('#find-reset').click();page.locator('#find-kind').select_option('essay')
        assert page.locator('.find-item:visible').count()==sum(e['kind']=='essay' for e in items)
        for node in page.locator('.find-item:visible').all(): assert node.get_attribute('data-kind')=='essay'
        page.locator('#find-reset').click();page.locator('#find-interest').select_option('technology')
        assert page.locator('.find-item:visible').count()==sum('technology' in e['interests'] for e in items)
        page.locator('#find-reset').click()
        if os.environ.get('AXE_PATH'):
            page.add_script_tag(path=os.environ['AXE_PATH'])
            for query in ['', 'family story', 'zznoresults']:
                set_query(page,query)
                result=page.evaluate('''async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}''')
                assert not result,('axe',query,result)
        if not OFFLINE:
            set_query(page,'family story')
            page.locator('a[href="#find-results"]').focus();page.keyboard.press('Enter')
            expect(page.locator('#find-results')).to_be_focused()
            expect(page.locator('.find-item:visible h3 a[href="/creative/"]')).to_be_visible()
            link=page.locator('.find-item:visible h3 a[href="/living-well/preserve-family-story/"]')
            expect(link).to_be_visible();link.focus();page.keyboard.press('Enter')
            expect(page).to_have_url(base+'/living-well/preserve-family-story/')
            page.locator('.utility-find').focus();page.keyboard.press('Enter')
            expect(page).to_have_url(base+'/find/')
            expect(page.locator('#find-query')).to_have_value('')
            page.goto(base+'/404.html');page.locator('main a[href="/find/"]').click()
            expect(page).to_have_url(base+'/find/')
            # Public descriptive titles must lead to the actual page by keyboard.
            for width in [390,1440]:
                page.set_viewport_size({'width':width,'height':900})
                for query,destination in title_queries:
                    set_query(page,query)
                    expect(page.locator('#find-results')).to_be_in_viewport()
                    assert page.locator('#find-results').evaluate('h=>h.getBoundingClientRect().top>=document.querySelector(".site-header").getBoundingClientRect().bottom+4'),'Descriptive-title results must clear the sticky header'
                    link=page.locator('.find-item:visible h3 a[href="'+destination+'"]')
                    expect(link).to_be_visible()
                    record=next(p for p in build.public_pages() if p['path']==destination)
                    expect(link).to_have_text(record['title'])
                    assert page.evaluate('document.documentElement.scrollWidth')<=width
                    if os.environ.get('SCREENSHOT_DIR') and query=='pot odds calculator':
                        out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                        page.screenshot(path=str(out/f'find-public-title-{width}.png'))
                    link.focus();page.keyboard.press('Enter')
                    expect(page).to_have_url(base+destination)
                    expect(page).to_have_title(record['seo_title'])
                    expect(page.locator('h1')).to_have_text(record['title'])
                    page.go_back();expect(page.locator('#find-query')).to_have_value('')
                    assert page.locator('.find-item:not([hidden])').count()==len(items)
                for interest,query,destination in cross_interest_queries:
                    page.locator('#find-interest').select_option(interest)
                    set_query(page,query)
                    link=page.locator('.find-item:visible h3 a[href="'+destination+'"]')
                    expect(link).to_be_visible()
                    link.focus();page.keyboard.press('Enter')
                    expect(page).to_have_url(base+destination)
                    record=next(p for p in build.public_pages() if p['path']==destination)
                    expect(page.locator('h1')).to_have_text(record['title'])
                    page.go_back()
                    expect(page.locator('#find-query')).to_have_value('')
                    expect(page.locator('#find-interest')).to_have_value('')
        context.close()
        # No-JavaScript and blocked-script visitors have a usable native index.
        for disabled in [True,False]:
            context=browser.new_context(java_script_enabled=not disabled)
            context.route('**/*',lambda r:r.continue_() if not OFFLINE and urlsplit(r.request.url).hostname=='127.0.0.1' and 'site-find.js' not in r.request.url else r.abort())
            page=context.new_page();load(page,script=False)
            expect(page.locator('#find-controls')).to_be_hidden()
            assert page.locator('.find-item').count()==len(items)
            for group in page.locator('.find-group').all():
                group.locator('summary').focus();page.keyboard.press('Enter')
                expect(group.locator('h3 a').first).to_be_visible()
            for interest,query,destination in cross_interest_queries:
                link=page.locator('.find-item h3 a[href="'+destination+'"]')
                expect(link).to_have_count(1)
                expect(link).to_be_visible()
            if not OFFLINE:
                page.locator('.find-item a[href="/notes/keep-the-judgment/"]').focus();page.keyboard.press('Enter')
                expect(page).to_have_url(base+'/notes/keep-the-judgment/')
            context.close()
        browser.close()
    assert not errors,errors
    print('PASS site discovery: explicit search focus, composition and boundary Enter defaults, live-filter focus, queries, 5 project cross-interest filters and unrelated-subject exclusion, escaping, reset, no query transport, 15 layouts + 15 text-spacing checks, disabled/blocked script fallback'+(' (in-memory; URL navigation not run)' if OFFLINE else ', keyboard URL navigation and 404 recovery, 6 descriptive-title and 10 project cross-interest keyboard arrivals with private-query history resets'))
finally:
    if server:server.shutdown()
