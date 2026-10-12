"""Native source-review exercise: no-script answers, navigation, exact downloads."""
import argparse, json, os, re, sys
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright, expect
from browser import html_for
ROOT=Path(__file__).resolve().parents[1]
ROUTE='/technology/check-ai-summary/'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--offline',action='store_true',help='Inspect in-memory layouts only; skips HTTP journeys/downloads')
args=parser.parse_args()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=None
if not args.offline:
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
 Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port) if server else ''
report={'offline':args.offline,'layouts':0,'text_spacing':0,'answer_disclosures':0,'source_journeys':0,'entry_journeys':0,'downloads':0,'axe':[]}
errors=[];writes=[]
try:
 with sync_playwright() as pw:
  opts={'headless':True}
  if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
  browser=pw.chromium.launch(**opts)
  for scripts in [True,False]:
   context=browser.new_context(java_script_enabled=scripts,accept_downloads=True,reduced_motion="reduce")
   def route(r):
    if r.request.method not in {'GET','HEAD'}:writes.append(r.request.url)
    r.continue_() if server and urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort()
   context.route('**/*',route)
   page=context.new_page();page.set_default_timeout(15000);page.on('pageerror',lambda e:errors.append(str(e)))
   def render(path):
    if args.offline:page.set_content(html_for(path))
    else:page.goto(base+path)
   for width in [320,390,768,1440]:
    page.set_viewport_size({'width':width,'height':950});render(ROUTE)
    expect(page.locator('h1')).to_be_visible()
    assert page.locator('.entry-jumps').evaluate('(el)=>getComputedStyle(el).display')=='flex'
    for link in page.locator('.entry-jumps a').all():
     assert link.bounding_box()['height']>=44
    assert page.evaluate('document.documentElement.scrollWidth')<=width
    report['layouts']+=1
    findings=page.locator('.summary-finding[id]')
    expect(findings).to_have_count(6)
    for details in findings.all():
     expect(details).not_to_have_attribute('open','')
     details.locator('summary').focus();page.keyboard.press('Enter')
     expect(details).to_have_attribute('open','');report['answer_disclosures']+=1
    page.locator('.summary-sheet summary').focus();page.keyboard.press('Enter')
    assert page.locator('.summary-sheet pre').text_content()==(ROOT/'downloads/ai-summary-review.txt').read_text()
    page.evaluate('css=>{const s=document.createElement("style");s.textContent=css;document.head.appendChild(s)}','*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
    assert page.evaluate('document.documentElement.scrollWidth')<=width
    report['text_spacing']+=1
    if scripts and width in [390,1440] and os.environ.get('SCREENSHOT_DIR'):
     out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
     page.evaluate('window.scrollTo(0,0)')
     page.screenshot(path=str(out/f'summary-review-spacing-{width}.png'),full_page=True)
    if scripts and os.environ.get('AXE_PATH') and width==390:
     page.add_script_tag(path=os.environ['AXE_PATH'])
     audit=page.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>v.id),incomplete:r.incomplete.map(v=>v.id)}}")
     assert not audit['violations'],audit
     report['axe'].append(audit)
   if not args.offline:
    render(ROUTE)
    for finding in page.locator('.summary-finding[id]').all():
     finding.locator('summary').focus();page.keyboard.press('Enter')
     for link in finding.locator('a[href^="#source-"]').all():
      target=link.get_attribute('href');link.focus();page.keyboard.press('Enter')
      expect(page).to_have_url(base+ROUTE+target)
      expect(page.locator(target)).to_be_visible();report['source_journeys']+=1
    for parent in ['/technology/','/notes/','/resources/']:
     render(parent);link=page.locator('a[href="'+ROUTE+'"]').first
     link.focus();page.keyboard.press('Enter');expect(page).to_have_url(base+ROUTE);report['entry_journeys']+=1
    for parent in [ROUTE,'/resources/']:
     render(parent)
     with page.expect_download() as info:page.locator('a[download][href="/downloads/ai-summary-review.txt"]').click()
     d=info.value;assert d.suggested_filename=='ai-summary-review.txt'
     assert Path(d.path()).read_bytes()==(ROOT/'downloads/ai-summary-review.txt').read_bytes();report['downloads']+=1
    page.goto(base+ROUTE)
    page.locator('.technology-return a[href="/technology/"]').focus();page.keyboard.press('Enter')
    expect(page).to_have_url(base+'/technology/')
   context.close()
  browser.close()
 assert not errors,errors
 assert not writes,writes
 report['status']='pass';print(json.dumps(report,indent=2))
finally:
 if server:server.shutdown();server.server_close()
