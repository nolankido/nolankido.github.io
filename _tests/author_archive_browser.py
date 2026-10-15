"""Native archive expansion, keyboard discovery, reflow and scoped accessibility."""
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
import author_archive

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port)
report={'layouts':0,'text_spacing':0,'groups':0,'journeys':0,'axe':[]}
errors=[];writes=[]

def keyboard_state(page, target, case):
    """Capture the public route and focus even when JavaScript is disabled."""
    count=target.count()
    return dict(case, url=page.url, target_count=count,
                target_visible=target.is_visible() if count==1 else False,
                target_box=target.bounding_box(timeout=1000) if count==1 else None,
                state=page.evaluate('''() => ({
        ready: document.readyState,
        focus: {tag: document.activeElement?.tagName, id: document.activeElement?.id,
                href: document.activeElement?.getAttribute('href')},
        groups: Array.from(document.querySelectorAll('.archive-group'),
                           node => ({id: node.id, open: node.open}))
    })'''))

def keyboard_follow(page, link, destination, case):
    """Assert readiness, send a real key, and require the exact loaded URL.

    Locator.press does not wait for visibility. In particular, an anchor in a
    just-opened details element must be visible and focused before Enter.
    No click, scripted navigation, retry, or longer timeout substitutes for it.
    """
    case=dict(case, destination=destination)
    print('ARCHIVE_JOURNEY '+json.dumps(case),flush=True)
    try:
        expect(link).to_be_visible()
        expect(link).to_have_attribute('href',destination)
        link.focus()
        expect(link).to_be_focused()
        print('ARCHIVE_READY '+json.dumps(keyboard_state(page,link,case)),flush=True)
        page.keyboard.press('Enter')
        page.wait_for_url(base+destination,wait_until='load')
        expect(page).to_have_url(base+destination)
        expect(page.locator('h1')).to_be_visible()
    except Exception:
        # Keep the original failure and include enough evidence to distinguish
        # a disclosure/focus problem from wrong navigation or an unloaded page.
        try:
            detail=keyboard_state(page,link,case)
            print('ARCHIVE_FAILURE '+json.dumps(detail),flush=True)
            if os.environ.get('SCREENSHOT_DIR'):
                out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                stem=f'author-archive-failure-{case["scripts"]}-{case["width"]}-{case["group"]}'
                (out/(stem+'.json')).write_text(json.dumps(detail,indent=2)+'\n')
                page.screenshot(path=str(out/(stem+'.png')))
        except Exception as diagnostic_error:
            print('ARCHIVE_DIAGNOSTIC_ERROR '+str(diagnostic_error),flush=True)
        raise
    report['journeys']+=1

try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        for scripts in [True,False]:
            ctx=browser.new_context(java_script_enabled=scripts,reduced_motion='reduce')
            ctx.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            ctx.on('request',lambda r:writes.append(r.url) if r.method not in {'GET','HEAD'} else None)
            page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            for width in [320,390,768,1440]:
                page.set_viewport_size({'width':width,'height':950})
                page.goto(base+'/notes/')
                expect(page.locator('.archive-list li')).to_have_count(100)
                for group in page.locator('.archive-group').all():
                    expect(group).not_to_have_attribute('open','')
                    group.locator('summary').press('Enter')
                    expect(group).to_have_attribute('open','')
                    expect(group.locator('.archive-list')).to_be_visible()
                    report['groups']+=1
                assert page.evaluate('document.documentElement.scrollWidth')<=width
                report['layouts']+=1
                page.evaluate('css=>{const s=document.createElement("style");s.textContent=css;document.head.appendChild(s)}','*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
                assert page.evaluate('document.documentElement.scrollWidth')<=width
                report['text_spacing']+=1
                if scripts and width in [390,1440] and os.environ.get('SCREENSHOT_DIR'):
                    out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                    page.locator('#all-writing').screenshot(path=str(out/f'author-archive-{width}.png'))
                if scripts and width==390 and os.environ.get('AXE_PATH'):
                    page.add_script_tag(path=os.environ['AXE_PATH'])
                    audit=page.evaluate("async()=>{const r=await axe.run(document.querySelector('#all-writing'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>v.id),incomplete:r.incomplete.map(v=>v.id)}}")
                    assert not audit['violations'],audit
                    report['axe'].append(audit)
            # Exercise both narrow and wide reader journeys in each input mode.
            for width in [390,1440]:
                page.set_viewport_size({'width':width,'height':950})
                case={'scripts':scripts,'width':width,'group':'about'}
                page.goto(base+'/about/')
                link=page.locator('a[href="/notes/#all-writing"]')
                keyboard_follow(page,link,'/notes/#all-writing',case)
                for group_id,target,destination in [
                    ('practical-ai','ai-answer-review','/technology/check-ai-answers/'),
                    ('living-well','living-well-notebook-or-ai','/living-well/notebook-or-ai/'),
                    ('poker','poker-holdem-basics','/poker/holdem-basics/'),
                    ('general-essays','generous-explanations','/notes/generous-explanations/')]:
                    page.goto(base+'/notes/#all-writing')
                    group=page.locator('#archive-'+group_id)
                    print('ARCHIVE_DISCLOSURE '+json.dumps(keyboard_state(
                        page,group.locator('summary'),dict(case,group=group_id))),flush=True)
                    expect(group).not_to_have_attribute('open','')
                    summary=group.locator('summary')
                    expect(summary).to_be_visible()
                    summary.focus();expect(summary).to_be_focused()
                    page.keyboard.press('Enter')
                    expect(group).to_have_attribute('open','')
                    expect(group.locator('.archive-list')).to_be_visible()
                    link=group.locator('[data-archive-id="'+target+'"] a')
                    keyboard_follow(page,link,destination,dict(case,group=group_id))
            ctx.close()
        browser.close()
    assert not errors,errors
    assert not writes,writes
    report['status']='pass';print(json.dumps(report,indent=2))
finally:
    server.shutdown();server.server_close()
