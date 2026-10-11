"""Real HTTP first-step journeys, keyboard use, no-script download, reflow and axe."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import faulthandler,json,os
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port)
starts={'technology':'/technology/task-brief/','living-well':'/living-well/worksheets/#weekly-reset','poker':'/poker/study-calculators/','creative':'/creative/#creative-brief'}
errors=[];missing=[];report={'keyboard_journeys':0,'downloads':0,'layouts':0,'expanded_spacing':0,'axe_scans':0}
def route(r):
 if urlsplit(r.request.url).hostname=='127.0.0.1':r.continue_()
 else:r.abort()
# Bound unexpected driver waits and keep diagnostic output if a browser regresses.
faulthandler.dump_traceback_later(180,exit=True)
try:
 with sync_playwright() as pw:
  opts={'headless':True}
  if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
  browser=pw.chromium.launch(**opts)
  for js in [True,False]:
   print('Testing JavaScript enabled='+str(js),flush=True)
   context=browser.new_context(java_script_enabled=js,accept_downloads=True)
   context.route('**/*',route)
   page=context.new_page()
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('response',lambda r:missing.append(r.url) if r.status>=400 and urlsplit(r.url).hostname=='127.0.0.1' else None)
   for key,dest in starts.items():
    for selector,target in [('.destination-action','/'+key+'/'),('.destination-first-link',dest)]:
     page.goto(base+'/')
     link=page.locator('.destination-'+key+' '+selector)
     link.focus();page.keyboard.press('Enter');expect(page).to_have_url(base+target)
     report['keyboard_journeys']+=1
   page.goto(base+'/creative/')
   summary=page.locator('.creative-template summary')
   summary.focus();page.keyboard.press('Enter')
   expect(page.locator('.creative-template')).to_have_attribute('open','')
   assert page.locator('.creative-template pre').text_content()==(ROOT/'downloads/creative-brief.txt').read_text()
   with page.expect_download() as info:
    page.get_by_role('link',name='Download the creative brief (.txt)',exact=True).click()
   assert info.value.suggested_filename=='creative-brief.txt'
   assert Path(info.value.path()).read_bytes()==(ROOT/'downloads/creative-brief.txt').read_bytes()
   report['downloads']+=1
   page.goto(base+'/resources/')
   page.locator('a[href="/creative/#creative-brief"]').focus();page.keyboard.press('Enter')
   expect(page).to_have_url(base+'/creative/#creative-brief');report['keyboard_journeys']+=1
   print('Native journeys and exact download passed',flush=True)
   for width in [320,390,540,768,1024,1440]:
    print('Testing width='+str(width),flush=True)
    page.set_viewport_size({'width':width,'height':1000})
    for path in ['/','/creative/','/resources/']:
     page.goto(base+path);expect(page.locator('h1')).to_be_visible()
     assert page.evaluate('document.documentElement.scrollWidth')<=width,(path,width,js)
     report['layouts']+=1
     if path=='/':
      for link in page.locator('.destination a').all():
       expect(link).to_be_visible()
       assert link.bounding_box()['height']>=44,('target-size',width,link.text_content())
     if path=='/creative/':
      page.locator('.creative-template summary').click()
      expect(page.locator('.creative-template pre')).to_be_visible()
     # add_style_tag waits indefinitely for a load event with page scripts disabled.
     # A synchronous test-only DOM insertion applies the same CSS in both contexts.
     spacing=page.evaluate_handle("css=>{const el=document.createElement('style');el.textContent=css;document.head.append(el);return el}", '*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
     assert page.evaluate('document.documentElement.scrollWidth')<=width,('spacing',path,width,js)
     report['expanded_spacing']+=1;spacing.evaluate('(n)=>n.remove()')
     if js and width in [390,1440]:
      if os.environ.get('AXE_PATH'):
       page.add_script_tag(path=os.environ['AXE_PATH'])
       audit=page.evaluate("async()=>{let r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}")
       assert not audit,(path,width,audit);report['axe_scans']+=1
      if os.environ.get('SCREENSHOT_DIR'):
       out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(exist_ok=True,parents=True)
       page.evaluate("document.activeElement?.blur();window.scrollTo({top:0,left:0,behavior:'instant'})")
       page.screenshot(path=str(out/('first-steps-'+(path.strip('/') or 'home')+'-'+str(width)+'.png')),full_page=True)
    page.goto(base+'/creative/')
    for anchor in ['creative-brief','creative-practice','creative-reading']:
     jump=page.locator('.creative-jumps a[href="#'+anchor+'"]')
     jump.focus();expect(jump).to_be_focused();expect(jump).to_be_in_viewport()
     jump.click()
     target=page.locator('#'+anchor).bounding_box()
     header=page.locator('.site-header').bounding_box()
     assert target['y']>=header['y']+header['height']-1,('obscured-anchor',width,anchor,target,header)
   context.close()
  browser.close()
 assert not errors,errors
 assert not missing,missing
 print(json.dumps({'result':'pass',**report},indent=2))
finally:
 faulthandler.cancel_dump_traceback_later()
 server.shutdown();server.server_close()
