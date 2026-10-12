"""Workflow calculator and historical case: inputs, exports, fallbacks, reflow and privacy."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from pathlib import Path
from urllib.parse import urlsplit
import argparse,json,os,faulthandler
from playwright.sync_api import sync_playwright,expect
from browser import html_for
parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=None
if not args.offline:
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
 Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port) if server else ''
calc='/technology/ai-time-savings/';case='/technology/checking-ai-website-changes/'
report={'offline':args.offline,'functional':0,'layouts':0,'spacing':0,'downloads':0,'axe':[],'journeys':0};errors=[]
faulthandler.dump_traceback_later(300,exit=True)
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,**({'executable_path':os.environ['CHROMIUM_PATH']} if os.environ.get('CHROMIUM_PATH') else {}))
  context=browser.new_context(accept_downloads=True,reduced_motion="reduce");requests=[]
  def route(r):
   requests.append(r.request.url)
   r.continue_() if not args.offline and urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort()
  context.route('**/*',route)
  page=context.new_page();page.set_default_timeout(10000);page.set_default_navigation_timeout(15000)
  page.on('pageerror',lambda e:errors.append(str(e)))
  def render(p,path,execute=True):
   if args.offline:
    p.set_content(html_for(path))
    if path==calc and execute:p.add_script_tag(content=(ROOT/'assets/workflow-time.js').read_text())
   else:p.goto(base+path)
  def fill(values):
   for k,v in zip(['manual','assisted','review','count','setup','upkeep'],values):page.locator('#time-'+k).fill(v)
  render(page,calc);expect(page.locator('#time-editor')).to_be_visible()
  page.wait_for_timeout(100);initial=len(requests);initial_url=page.url
  page.locator('#time-calculate').focus();page.keyboard.press('Enter');expect(page.locator('#time-manual')).to_be_focused();expect(page.locator('#time-result')).to_be_hidden();report['functional']+=1
  fill(['30','8','7','6','60','15']);page.locator('#time-calculate').click()
  expect(page.locator('#time-result-title')).to_have_text('15 min saved in this window');expect(page.locator('#time-result-title')).to_be_focused()
  expect(page.locator('#time-threshold')).to_contain_text('repetition 5; strictly positive time savings start at repetition 6')
  expect(page.locator('#time-quality-note')).to_contain_text('Quality is unverified');report['functional']+=1
  text=page.locator('#time-report').input_value()
  page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async t=>{window.copiedTime=t;}}})")
  page.locator('#time-copy').click();expect(page.locator('#time-copy-status')).to_contain_text('Comparison copied');assert page.evaluate('window.copiedTime')==text
  page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async()=>{throw new Error('denied')}}})")
  page.locator('#time-copy').click();expect(page.locator('#time-report')).to_be_focused();expect(page.locator('#time-copy-status')).to_contain_text('Automatic copy is unavailable')
  assert page.locator('#time-report').evaluate('x=>x.selectionEnd-x.selectionStart')==len(text);report['functional']+=2
  with page.expect_download() as item:page.locator('#time-download').click()
  download=item.value;assert download.suggested_filename=='workflow-time-comparison.txt';assert Path(download.path()).read_text()==text;report['downloads']+=1
  page.locator('#time-review').fill('10');expect(page.locator('#time-result')).to_be_hidden();assert page.locator('#time-report').input_value()==''
  page.locator('#time-calculate').click();expect(page.locator('#time-result-title')).to_have_text('3 min extra time in this window');report['functional']+=1
  page.locator('#time-review').fill('<script>');page.locator('#time-calculate').click();expect(page.locator('#time-review')).to_be_focused();expect(page.locator('#time-result')).to_be_hidden();report['functional']+=1
  fill(['0.3','0.1','0.1','2','0.2','0']);page.locator('#time-calculate').click();expect(page.locator('#time-result-title')).to_have_text('No net time saved in this window');report['functional']+=1
  fill(['30','8','7','6','60','15']);page.locator('#time-quality').select_option('fail');page.locator('#time-basis').select_option('observed');page.locator('#time-calculate').click()
  expect(page.locator('#time-quality-note')).to_contain_text('Quality check not met');expect(page.locator('#time-basis-note')).to_contain_text('not independently verified');report['functional']+=1
  page.locator('#time-clear').click();expect(page.locator('#time-clear-confirm')).to_be_visible();page.locator('#time-clear-no').click();expect(page.locator('#time-manual')).to_have_value('30')
  page.locator('#time-clear').click();page.locator('#time-clear-yes').click();expect(page.locator('#time-manual')).to_have_value('');expect(page.locator('#time-result')).to_be_hidden();report['functional']+=1
  assert len(requests)==initial,(initial,requests);assert page.url==initial_url
  if not args.offline:assert page.evaluate('localStorage.length+sessionStorage.length')==0;assert context.cookies()==[]
  page.locator('#time-manual').fill('1');page.evaluate("window.dispatchEvent(new Event('pagehide'))");expect(page.locator('#time-manual')).to_have_value('');report['functional']+=1
  page.locator('#time-manual').fill('1');page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))");expect(page.locator('#time-manual')).to_have_value('');report['functional']+=1
  spacing='*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}'
  for path in [calc,case]:
   for width in [320,390,768,1440]:
    render(page,path);page.set_viewport_size({'width':width,'height':1000})
    if path==calc:fill(['30','8','7','6','60','15']);page.locator('#time-calculate').click()
    expect(page.locator('h1')).to_be_visible();assert page.evaluate('document.documentElement.scrollWidth')<=width,(path,width);report['layouts']+=1
    if os.environ.get('SCREENSHOT_DIR') and width in [390,1440]:
     out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
     page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(out/(path.strip('/').replace('/','-')+'-'+str(width)+'.png')),full_page=True)
    if os.environ.get('AXE_PATH'):
     page.add_script_tag(path=os.environ['AXE_PATH']);scan=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)})),incomplete:r.incomplete.map(v=>v.id)}}")
     assert not scan['violations'],(path,width,scan);report['axe'].append({'path':path,'width':width,**scan})
    page.locator('details').evaluate_all('(els)=>els.forEach(e=>e.open=true)')
    page.evaluate('s=>{const e=document.createElement("style");e.textContent=s;document.head.appendChild(e)}',spacing)
    assert page.evaluate('document.documentElement.scrollWidth')<=width,('spacing',path,width);report['spacing']+=1
  if not args.offline:
   for parent in ['/technology/','/resources/','/about/']:
    for path in [calc,case]:
     page.goto(base+parent);page.locator('main a[href="'+path+'"]').first.focus();page.keyboard.press('Enter');expect(page).to_have_url(base+path);report['journeys']+=1
   for path in [calc,case]:
    page.goto(base+path)
    for link in page.locator('main a[download]').all():
     href=link.get_attribute('href')
     # Open disclosure when its download is inside a closed detail.
     link.evaluate('(a)=>{const d=a.closest("details");if(d)d.open=true;}')
     with page.expect_download() as item:link.click()
     assert Path(item.value.path()).read_bytes()==(ROOT/href.lstrip('/')).read_bytes();report['downloads']+=1
  context.close()
  for mode in ['disabled','blocked']:
   ctx=browser.new_context(java_script_enabled=mode!='disabled',reduced_motion='reduce')
   def fallback(r):
    if 'workflow-time.js' in r.request.url:r.abort()
    elif not args.offline and urlsplit(r.request.url).hostname=='127.0.0.1':r.continue_()
    else:r.abort()
   ctx.route('**/*',fallback);p=ctx.new_page();p.set_default_timeout(10000);render(p,calc,False)
   expect(p.locator('#time-editor')).to_be_hidden();expect(p.locator('#time-unavailable')).to_be_visible();expect(p.locator('.time-static-example')).to_have_count(3)
   p.locator('details summary').focus();p.keyboard.press('Enter');assert p.locator('details pre').inner_text()==(ROOT/'downloads/workflow-time-review.txt').read_text()
   for width in [320,390,768,1440]:
    p.set_viewport_size({'width':width,'height':950});assert p.evaluate('document.documentElement.scrollWidth')<=width;report['layouts']+=1
   ctx.close();report['functional']+=1
  assert not errors,errors;browser.close()
 print('WORKFLOW_EVIDENCE_REPORT='+json.dumps(report))
finally:
 if server:server.shutdown();server.server_close()
 faulthandler.cancel_dump_traceback_later()
