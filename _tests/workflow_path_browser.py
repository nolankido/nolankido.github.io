"""Native journey, worksheet and reflow checks, with and without JavaScript."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from pathlib import Path
from urllib.parse import urlsplit
import json,os,sys,argparse
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import workflow_path
from browser import html_for
parser=argparse.ArgumentParser();parser.add_argument("--offline",action="store_true");args=parser.parse_args()
def render(page,route):
    if args.offline:page.set_content(html_for(route))
    else:page.goto(base+route)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port)
report={'offline':args.offline,'layouts':0,'spacing':0,'stage_journeys':0,'entrance_journeys':0,'downloads':0,'preview_checks':0,'axe':[],'errors':[]}
spacing='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}'
try:
    with sync_playwright() as pw:
        options={'headless':True}
        if os.environ.get('CHROMIUM_PATH'):options['executable_path']=os.environ['CHROMIUM_PATH']
        browser=pw.chromium.launch(**options)
        for enabled in [True,False]:
            ctx=browser.new_context(java_script_enabled=enabled,accept_downloads=True,reduced_motion='reduce')
            ctx.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort())
            page=ctx.new_page();page.set_default_timeout(10000)
            page.on('pageerror',lambda err:report['errors'].append(str(err)))
            for width in [320,390,768,1440]:
                page.set_viewport_size({'width':width,'height':1000})
                for route in ['/technology/']+[s['route'] for s in workflow_path.STEPS]:
                    render(page,route);expect(page.locator('h1')).to_be_visible()
                    assert page.evaluate('document.documentElement.scrollWidth')<=width,(route,width)
                    report['layouts']+=1
                    if route=='/technology/':
                        expect(page.locator('.workflow-stage')).to_have_count(4)
                        page.locator('#ai-workflow-workbook summary').focus();page.keyboard.press('Enter')
                        expect(page.locator('#ai-workflow-workbook details')).to_have_attribute('open','')
                        assert page.locator('#ai-workflow-workbook pre').inner_text()==(ROOT/workflow_path.SHEET).read_text()
                        report['preview_checks']+=1
                    else:
                        expect(page.locator('.workflow-route [aria-current="step"]')).to_have_count(1)
                        for link in page.locator('.workflow-route nav a').all():assert link.bounding_box()['height']>=44
                    if os.environ.get('SCREENSHOT_DIR') and enabled and width in [390,1440] and route in ['/technology/','/technology/task-brief/']:
                        out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
                        if route=='/technology/':
                            page.locator('#ai-workflow-workbook summary').click()
                            page.evaluate('document.activeElement.blur();window.scrollTo(0,0)')
                            page.screenshot(path=str(out/f'workflow-hub-{width}.png'),full_page=True)
                        else:
                            page.evaluate('document.activeElement.blur();window.scrollTo(0,0)')
                            page.screenshot(path=str(out/f'workflow-stage-{width}.png'),full_page=True)
                    page.evaluate('s=>{const e=document.createElement("style");e.textContent=s;document.head.appendChild(e)}',spacing)
                    assert page.evaluate('document.documentElement.scrollWidth')<=width,('spacing',route,width)
                    report['spacing']+=1
            page.set_viewport_size({'width':390,'height':1000})
            if not args.offline:
                for source in workflow_path.STEPS:
                    for target in workflow_path.STEPS:
                        if source==target:continue
                        render(page,source['route'])
                        page.locator('.workflow-route nav a[href="'+target['route']+'"]').focus()
                        page.keyboard.press('Enter');expect(page).to_have_url(base+target['route']);report['stage_journeys']+=1
                for source in ['/start-here/','/resources/']:
                    render(page,source)
                    page.locator('main a[href="'+workflow_path.HUB+'"]').first.focus();page.keyboard.press('Enter')
                    expect(page).to_have_url(base+workflow_path.HUB);expect(page.locator('#ai-workflow-path')).to_be_visible();report['entrance_journeys']+=1
                for source in ['/technology/','/resources/']+[s['route'] for s in workflow_path.STEPS]:
                    render(page,source)
                    with page.expect_download() as transfer:
                        page.locator('a[download][href="/'+str(workflow_path.SHEET)+'"]').first.click()
                    assert transfer.value.suggested_filename==workflow_path.SHEET.name
                    assert Path(transfer.value.path()).read_bytes()==(ROOT/workflow_path.SHEET).read_bytes();report['downloads']+=1
            if enabled and os.environ.get('AXE_PATH'):
                for source in ['/technology/','/technology/task-brief/','/technology/should-i-use-ai/']:
                    render(page,source);page.add_script_tag(path=os.environ['AXE_PATH'])
                    scan=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(x=>({id:x.id,nodes:x.nodes.map(n=>n.target)})),incomplete:r.incomplete.map(x=>x.id)}}")
                    assert not scan['violations'],(source,scan);report['axe'].append({'route':source,**scan})
            assert ctx.cookies()==[]
            if not args.offline:assert page.evaluate('localStorage.length+sessionStorage.length')==0
            ctx.close()
        assert not report['errors'],report['errors']
        browser.close()
    print('WORKFLOW_PATH_REPORT='+json.dumps(report))
finally:
    server.shutdown();server.server_close()
