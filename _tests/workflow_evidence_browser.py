"""Workflow calculator and historical case: inputs, exports, fallbacks, reflow and privacy."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from pathlib import Path
from urllib.parse import urlsplit
import argparse,json,os,faulthandler
from playwright.sync_api import sync_playwright,expect
from browser import html_for
from time_export_history import before as before_export
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
report={'offline':args.offline,'functional':0,'layouts':0,'spacing':0,'downloads':0,'export_recovery_layouts':0,'export_recovery_spacing':0,'export_normal_capture_equivalence':0,'axe':[],'journeys':0,'case_source_keyboard_journeys':0,'editable_examples':0,'example_replacement_recovery':0,'example_downloads':0,'print_layouts':0,'print_report_equivalence':0,'print_requests':0,'print_fallbacks':0,'print_state_guards':0,'print_static_fallbacks':0,'print_pdf_captures':0};errors=[]
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
  # Verify the unchanged numeric totals visually against the previous handler.
  # The new decision and sensitivity region is intentionally not pixel-identical.
  probe=browser.new_context(viewport={'width':1440,'height':1000},device_scale_factor=1,reduced_motion='reduce')
  probe.route('**/*',lambda r:r.abort())
  current_script=(ROOT/'assets/workflow-time.js').read_text()
  captures=[]
  for label,script in [('before',before_export('assets/workflow-time.js',current_script)),('after',current_script)]:
   p=probe.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
   p.set_content(html_for(calc));p.add_script_tag(content=script)
   # Isolate the unchanged manual-entry result at the same document position.
   # The historical script cannot reveal the new optional picker; allowing only
   # the current script to reveal it shifts fractional layout coordinates and
   # changes rasterization. Complete visible example journeys are tested below.
   p.locator('#time-example-picker').evaluate('el=>{el.hidden=true}')
   for key,value in zip(['manual','assisted','review','count','setup','upkeep'],['30','8','7','6','60','15']):p.locator('#time-'+key).fill(value)
   p.locator('#time-calculate').click();p.evaluate('document.activeElement.blur()')
   capture=p.locator('.time-totals').screenshot();captures.append(capture)
   if os.environ.get('SCREENSHOT_DIR'):
    out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
    (out/f'time-export-normal-{label}.png').write_bytes(capture)
   p.close()
  assert captures[0]==captures[1],'The original numeric totals changed beyond export recovery'
  probe.close();report['export_normal_capture_equivalence']+=1
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
  expect(page.locator('#time-decision')).to_contain_text('MEASURE MORE')
  expect(page.locator('#time-review-budget')).to_contain_text('9.5 min')
  expect(page.locator('#time-sensitivity')).to_contain_text('3 min saved')
  report['functional']+=3
  text=page.locator('#time-report').input_value()
  page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async t=>{window.copiedTime=t;}}})")
  page.locator('#time-copy').click();expect(page.locator('#time-copy-status')).to_contain_text('Comparison copied');assert page.evaluate('window.copiedTime')==text
  page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async()=>{throw new Error('denied')}}})")
  page.locator('#time-copy').click();expect(page.locator('#time-report')).to_be_focused();expect(page.locator('#time-copy-status')).to_contain_text('Automatic copy is unavailable')
  assert page.locator('#time-report').evaluate('x=>x.selectionEnd-x.selectionStart')==len(text);report['functional']+=2
  with page.expect_download() as item:page.locator('#time-download').click()
  download=item.value;assert download.suggested_filename=='workflow-time-comparison.txt';assert Path(download.path()).read_text()==text;report['downloads']+=1
  expect(page.locator('#time-copy-status')).to_have_text('Text download requested. Keep the comparison in your own notes.')
  page.evaluate("()=>{window.nativeTimeExportURL=URL.createObjectURL;URL.createObjectURL=()=>{throw new Error('Synthetic file creation failure')};}")
  page.locator('#time-download').press('Enter')
  expect(page.locator('#time-report')).to_be_focused();expect(page.locator('#time-result')).to_be_visible()
  expect(page.locator('#time-copy-status')).to_have_text('Download unavailable. Copy the selected comparison into your own notes.')
  assert page.locator('#time-report').input_value()==text
  assert page.locator('#time-report').evaluate('x=>x.selectionEnd-x.selectionStart')==len(text)
  for recovery_width in [390,1440]:
   page.set_viewport_size({'width':recovery_width,'height':1000})
   assert page.evaluate('document.documentElement.scrollWidth')<=recovery_width
   report['export_recovery_layouts']+=1
   if os.environ.get('SCREENSHOT_DIR'):
    out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
    page.locator('#time-result').screenshot(path=str(out/f'time-export-recovery-{recovery_width}.png'))
   page.evaluate('css=>{const style=document.createElement("style");style.id="time-export-spacing";style.textContent=css;document.head.appendChild(style)}','*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}')
   assert page.evaluate('document.documentElement.scrollWidth')<=recovery_width
   report['export_recovery_spacing']+=1
   page.evaluate('document.getElementById("time-export-spacing").remove()')
  page.evaluate('()=>{URL.createObjectURL=window.nativeTimeExportURL;}');report['functional']+=1
  page.evaluate("""()=>{window.nativeTimeExportClick=HTMLAnchorElement.prototype.click;
window.nativeTimeExportRevoke=URL.revokeObjectURL;window.timeExportRevoked=[];
window.timeExportFailureURL=null;URL.createObjectURL=blob=>{const url=window.nativeTimeExportURL.call(URL,blob);window.timeExportFailureURL=url;return url};
URL.revokeObjectURL=url=>{window.timeExportRevoked.push(url);window.nativeTimeExportRevoke.call(URL,url)};
HTMLAnchorElement.prototype.click=function(){if(this.download==='workflow-time-comparison.txt')throw new Error('Synthetic download activation failure');return window.nativeTimeExportClick.call(this)};}""")
  page.locator('#time-download').press('Enter')
  expect(page.locator('#time-report')).to_be_focused();expect(page.locator('#time-result')).to_be_visible()
  expect(page.locator('#time-copy-status')).to_have_text('Download unavailable. Copy the selected comparison into your own notes.')
  assert page.locator('#time-report').input_value()==text
  assert page.locator('#time-report').evaluate('x=>x.selectionEnd-x.selectionStart')==len(text)
  expect(page.locator('a[download="workflow-time-comparison.txt"]')).to_have_count(0)
  page.wait_for_function('window.timeExportRevoked.includes(window.timeExportFailureURL)')
  page.evaluate('()=>{HTMLAnchorElement.prototype.click=window.nativeTimeExportClick;URL.revokeObjectURL=window.nativeTimeExportRevoke;URL.createObjectURL=window.nativeTimeExportURL;}');report['functional']+=1
  with page.expect_download() as item:page.locator('#time-download').click()
  assert Path(item.value.path()).read_text()==text;report['downloads']+=1
  expect(page.locator('#time-copy-status')).to_have_text('Text download requested. Keep the comparison in your own notes.')
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
  examples=[('Repeated task',['30','8','7','6','60','15'],'15 min saved in this window'),
            ('One-off task',['30','8','7','1','60','0'],'45 min extra time in this window'),
            ('Review costs more',['20','5','18','10','10','5'],'45 min extra time in this window')]
  for width in [320,390,768,1440]:
   page.set_viewport_size({'width':width,'height':1000})
   for index,(label,values,outcome) in enumerate(examples):
    render(page,calc);page.evaluate('document.fonts.ready');page.wait_for_timeout(100)
    initial_requests=len(requests);initial_url=page.url
    picker=page.locator('#time-example-picker');expect(picker).to_be_visible()
    picker.locator('button').first.focus()
    for _ in range(index):page.keyboard.press('Tab')
    expect(picker.get_by_role('button',name=label,exact=True)).to_be_focused()
    page.keyboard.press('Enter');expect(page.locator('#time-manual')).to_be_focused()
    for key,value in zip(['manual','assisted','review','count','setup','upkeep'],values):expect(page.locator('#time-'+key)).to_have_value(value)
    expect(page.locator('#time-basis')).to_have_value('estimate');expect(page.locator('#time-quality')).to_have_value('unknown')
    expect(page.locator('#time-result')).to_be_hidden();page.locator('#time-calculate').press('Enter')
    expect(page.locator('#time-result-title')).to_have_text(outcome)
    expect(page.locator('#time-example-origin')).to_contain_text('Fictional example starting point: '+label)
    assert 'Fictional example starting point: '+label in page.locator('#time-report').input_value()
    assert page.evaluate('document.documentElement.scrollWidth')<=width
    assert page.url==initial_url and len(requests)==initial_requests
    if not args.offline:assert page.evaluate('localStorage.length+sessionStorage.length')==0;assert context.cookies()==[]
    report['editable_examples']+=1
    if width==390:
     with page.expect_download() as item:page.locator('#time-download').click()
     assert Path(item.value.path()).read_text()==page.locator('#time-report').input_value();report['example_downloads']+=1
    if index==0 and os.environ.get('SCREENSHOT_DIR') and width in [390,1440]:
     out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
     picker.screenshot(path=str(out/f'time-example-picker-{width}.png'))
     page.locator('#time-result').screenshot(path=str(out/f'time-example-result-{width}.png'))
   # Cancellation preserves all entries, quality/basis selections and the exact report.
   page.locator('#time-quality').select_option('pass');page.locator('#time-basis').select_option('observed')
   page.locator('#time-calculate').click();previous=page.locator('#time-report').input_value()
   button=page.get_by_role('button',name='Repeated task',exact=True)
   button.press('Enter');expect(page.locator('#time-example-no')).to_be_focused()
   expect(page.locator('#time-example-confirm')).to_be_visible();expect(page.locator('#time-result')).to_be_visible()
   assert page.locator('#time-report').input_value()==previous
   if os.environ.get('SCREENSHOT_DIR') and width in [390,1440]:
    page.locator('#time-example-confirm').screenshot(path=str(out/f'time-example-confirm-{width}.png'))
   page.locator('#time-example-no').press('Enter');expect(button).to_be_focused()
   for key,value in zip(['manual','assisted','review','count','setup','upkeep'],examples[2][1]):expect(page.locator('#time-'+key)).to_have_value(value)
   expect(page.locator('#time-quality')).to_have_value('pass');expect(page.locator('#time-basis')).to_have_value('observed')
   assert page.locator('#time-report').input_value()==previous
   # Editing cancels a pending replacement; a stale confirmation cannot replace it.
   button.click();page.locator('#time-manual').fill('21');expect(page.locator('#time-example-confirm')).to_be_hidden()
   page.locator('#time-example-yes').dispatch_event('click');expect(page.locator('#time-manual')).to_have_value('21')
   page.locator('#time-calculate').click();expect(page.locator('#time-example-origin')).to_contain_text('Review costs more')
   button.click();page.locator('#time-example-yes').press('Enter')
   expect(page.locator('#time-manual')).to_be_focused();expect(page.locator('#time-manual')).to_have_value('30')
   expect(page.locator('#time-quality')).to_have_value('unknown');expect(page.locator('#time-basis')).to_have_value('estimate')
   expect(page.locator('#time-result')).to_be_hidden();page.locator('#time-calculate').click()
   expect(page.locator('#time-result-title')).to_have_text('15 min saved in this window')
   expect(page.locator('#time-example-origin')).to_contain_text('Repeated task')
   page.locator('#time-clear').click();page.locator('#time-clear-yes').press('Enter')
   expect(page.locator('#time-example-origin')).to_be_hidden();expect(page.locator('#time-example-origin')).to_have_text('')
   button.click();page.evaluate("window.dispatchEvent(new Event('pagehide'))")
   expect(page.locator('#time-manual')).to_have_value('');expect(page.locator('#time-example-origin')).to_have_text('')
   report['example_replacement_recovery']+=1
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
  # Printing must carry the entire canonical record, including its final model
  # limitations. A fixed-height textarea cannot provide this printed record.
  print_context=browser.new_context(accept_downloads=True,reduced_motion='reduce')
  print_requests=[]
  def print_route(r):
   print_requests.append(r.request.url)
   r.continue_() if not args.offline and urlsplit(r.request.url).hostname=='127.0.0.1' else r.abort()
  print_context.route('**/*',print_route)
  p=print_context.new_page();p.set_default_timeout(10000);p.on('pageerror',lambda e:errors.append(str(e)))
  render(p,calc);p.evaluate('document.fonts.ready');p.wait_for_timeout(100)
  print_initial_requests=len(print_requests);print_initial_url=p.url
  p.evaluate("""() => { window.timePrintRequests=0; window.print=()=>{
   window.timePrintRequests+=1;
   window.dispatchEvent(new Event('beforeprint'));
   window.dispatchEvent(new Event('afterprint'));
  }; }""")
  print_keys=['manual','assisted','review','count','setup','upkeep']
  worksheet_text=(ROOT/'downloads/workflow-time-review.txt').read_text()
  normal_values=['30','8','7','6','60','15']
  def print_probe():
   return p.evaluate("""() => ({requests:window.timePrintRequests,printType:typeof window.print,
    status:document.getElementById('time-copy-status').textContent,focused:document.activeElement.id,
    resultHidden:document.getElementById('time-result').hidden,
    reportLength:document.getElementById('time-report').value.length,
    printLength:document.getElementById('time-print-report').textContent.length})""")
  assert p.evaluate('window.timePrintRequests')==0,print_probe()
  def print_snapshot():
   return {'fields':{k:p.locator('#time-'+k).input_value() for k in print_keys},
           'basis':p.locator('#time-basis').input_value(),'quality':p.locator('#time-quality').input_value(),
           'report':p.locator('#time-report').input_value(),'print':p.locator('#time-print-report').text_content(),
           'origin':p.locator('#time-example-origin').text_content()}
  def calculate_print(values,basis='estimate',quality='unknown'):
   for key,value in zip(print_keys,values):p.locator('#time-'+key).fill(value)
   p.locator('#time-basis').select_option(basis);p.locator('#time-quality').select_option(quality)
   p.locator('#time-calculate').click();expect(p.locator('#time-result')).to_be_visible()
   snapshot=print_snapshot();assert snapshot['report'] and snapshot['print']==snapshot['report']
   expect(p.locator('#time-print-report')).to_be_hidden()
   for key,value in zip(print_keys,values):
    assert key+': '+value+(' repetitions' if key=='count' else ' minutes') in snapshot['print']
   assert snapshot['print'].startswith('WORKFLOW TIME COMPARISON\nhttps://nolankido.com/technology/ai-time-savings/\n')
   assert 'Decision: ' in snapshot['print'] and 'What if verification takes 2 more minutes per task?' in snapshot['print']
   assert snapshot['print'].endswith('This is not a financial ROI or quality score.\n')
   return snapshot
  def no_printable_result(reason,private_marker=''):
   expect(p.locator('#time-result')).to_be_hidden();expect(p.locator('#time-report')).to_have_value('')
   expect(p.locator('#time-print-report')).to_have_text('')
   count=p.evaluate('window.timePrintRequests');p.locator('#time-print').dispatch_event('click')
   assert p.evaluate('window.timePrintRequests')==count,(reason,print_probe())
   p.emulate_media(media='print')
   expect(p.locator('html')).to_have_css('background-color','rgb(255, 255, 255)')
   expect(p.locator('#time-editor')).to_be_hidden();expect(p.locator('#time-print-report')).to_be_hidden()
   expect(p.locator('input:visible, select:visible, textarea:visible, button:visible')).to_have_count(0)
   worksheet=p.locator('section[aria-labelledby="time-worksheet"] details')
   assert worksheet.get_attribute('open') is None,reason
   expect(worksheet.locator('pre')).to_be_visible();assert worksheet.locator('pre').text_content()==worksheet_text
   if private_marker:assert private_marker not in p.locator('body').inner_text(),reason
   p.emulate_media(media='screen');expect(worksheet.locator('pre')).to_be_hidden()
   assert worksheet.get_attribute('open') is None,reason
   report['print_state_guards']+=1
  no_printable_result('blank')
  p.locator('#time-manual').fill('99999.99')
  no_printable_result('uncomputed entries','99999.99');expect(p.locator('#time-manual')).to_have_value('99999.99')
  p.locator('#time-calculate').click();no_printable_result('incomplete validation','99999.99')
  print_cases=[('normal',normal_values,'estimate','unknown'),
               ('decimal-break-even',['0.3','0.1','0.1','2','0.2','0'],'estimate','pass'),
               ('maximum',['100000']*6,'observed','fail'),
               ('fictional',normal_values,'estimate','unknown')]
  for label,values,basis,quality in print_cases:
   if label in ['fictional','maximum']:
    example_label='Repeated task' if label=='fictional' else 'Review costs more'
    p.get_by_role('button',name=example_label,exact=True).click()
    expect(p.locator('#time-example-confirm')).to_be_visible();p.locator('#time-example-yes').click()
   snapshot=calculate_print(values,basis,quality)
   if label=='normal':
    assert 'Planning estimate, not a measured outcome.' in snapshot['print']
    assert 'Quality is unverified' in snapshot['print'] and '9.5 min' in snapshot['print']
    with p.expect_download() as item:p.locator('#time-download').click()
    assert Path(item.value.path()).read_text()==snapshot['print'];report['downloads']+=1
    p.locator('#time-print').focus();expect(p.locator('#time-print')).to_be_focused();p.keyboard.press('Enter')
    assert p.evaluate('window.timePrintRequests')==1,print_probe()
    expect(p.locator('#time-copy-status')).to_contain_text('Print requested.')
    assert print_snapshot()==snapshot
    p.evaluate("window.dispatchEvent(new Event('afterprint'))")
    assert print_snapshot()==snapshot;report['print_requests']+=1
    for mode in ['unavailable','throws']:
     p.evaluate("mode => { window.print=mode==='unavailable' ? undefined : ()=>{throw new Error('Printing denied');}; }",mode)
     p.locator('#time-print').click();expect(p.locator('#time-copy-status')).to_contain_text('Printing is unavailable.')
     expect(p.locator('#time-report')).to_be_focused()
     assert p.locator('#time-report').evaluate('(e)=>e.selectionEnd-e.selectionStart')==len(snapshot['report'])
     assert print_snapshot()==snapshot;report['print_fallbacks']+=1
    p.evaluate('() => { window.print=()=>{window.timePrintRequests+=1;}; }')
   elif label=='decimal-break-even':assert 'No net time saved in this window' in snapshot['print']
   elif label=='maximum':
    assert 'User-entered observations, not independently verified or a causal experiment.' in snapshot['print']
    assert 'Quality check not met' in snapshot['print'] and 'STOP OR REDESIGN' in snapshot['print']
    assert '10,000,200,000 min extra time' in snapshot['print']
    assert 'Fictional example starting point: Review costs more.' in snapshot['print']
   else:
    assert 'Fictional example starting point: Repeated task.' in snapshot['print']
    assert 'illustrative, not observed results' in snapshot['print']
   report['print_report_equivalence']+=1
   # Browser Print is covered independently of the explicit button. Returning
   # from print preview, including cancellation, must preserve the comparison.
   for width in [320,390,768,1440]:
    p.set_viewport_size({'width':width,'height':1000});p.emulate_media(media='print')
    expect(p.locator('html')).to_have_css('background-color','rgb(255, 255, 255)')
    expect(p.locator('#time-print-report')).to_be_visible()
    expect(p.locator('#main > :visible')).to_have_count(1)
    expect(p.locator('#main > :visible')).to_have_attribute('aria-labelledby','time-workspace')
    expect(p.locator('#time-result > :visible')).to_have_count(1)
    expect(p.locator('#time-result > :visible')).to_have_attribute('id','time-print-report')
    expect(p.locator('input:visible, select:visible, textarea:visible, button:visible')).to_have_count(0)
    for selector in ['#time-print-help','#time-example-picker','#time-example-confirm','#time-clear-confirm','#time-copy-status',
                     'section[aria-labelledby="time-examples"]','section[aria-labelledby="time-method"]',
                     'section[aria-labelledby="time-worksheet"]','.site-header','footer']:
     for element in p.locator(selector).all():expect(element).to_be_hidden()
    assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),(label,width)
    assert p.locator('#time-print-report').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1 && e.scrollHeight<=e.clientHeight+1'),(label,width)
    assert print_snapshot()==snapshot,(label,width)
    report['print_layouts']+=1
    p.emulate_media(media='screen')
    expect(p.locator('#time-print-report')).to_be_hidden();expect(p.locator('#time-print-help')).to_be_visible()
    expect(p.locator('#time-manual')).to_be_visible();expect(p.locator('#time-print')).to_be_visible()
    expect(p.locator('section[aria-labelledby="time-examples"]')).to_be_visible()
    assert print_snapshot()==snapshot,(label,width,'screen restored')
   if os.environ.get('SCREENSHOT_DIR') and label in ['normal','maximum']:
    out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
    p.emulate_media(media='print')
    pdf=p.pdf(path=str(out/f'workflow-time-print-{label}.pdf'),format='A4',print_background=True,
              margin={'top':'15mm','bottom':'15mm','left':'15mm','right':'15mm'})
    assert pdf.startswith(b'%PDF-');report['print_pdf_captures']+=1
    p.emulate_media(media='screen');assert print_snapshot()==snapshot
  # The printed copy shares the existing invalidation rules, including basis,
  # quality and fictional-example replacement. Stale records must not survive.
  p.locator('#time-review').fill('99999.99');no_printable_result('edited numeric entry','99999.99')
  for key,value in [('basis','observed'),('quality','pass')]:
   calculate_print(normal_values);p.locator('#time-'+key).select_option(value);no_printable_result('changed '+key)
  calculate_print(normal_values);p.locator('#time-review').fill('<script>');p.locator('#time-calculate').click()
  no_printable_result('invalid nonnumeric value','<script>')
  calculate_print(normal_values);p.locator('#time-clear').click();p.locator('#time-clear-yes').click()
  no_printable_result('cleared')
  calculate_print(normal_values);p.get_by_role('button',name='One-off task',exact=True).click()
  before_cancel=print_snapshot();p.locator('#time-example-no').click();assert print_snapshot()==before_cancel
  p.get_by_role('button',name='One-off task',exact=True).click();p.locator('#time-example-yes').click()
  no_printable_result('example replaced')
  for event in ["new Event('pagehide')","new PageTransitionEvent('pageshow',{persisted:true})"]:
   calculate_print(normal_values);p.evaluate('window.dispatchEvent('+event+')')
   for key in print_keys:expect(p.locator('#time-'+key)).to_have_value('')
   no_printable_result(event)
  assert p.evaluate('window.timePrintRequests')==1,print_probe()
  assert len(print_requests)==print_initial_requests,(print_initial_requests,print_requests)
  assert p.url==print_initial_url
  if not args.offline:assert p.evaluate('localStorage.length+sessionStorage.length')==0
  assert print_context.cookies()==[];print_context.close()
  # Exercise native evidence links with and without JavaScript. An exact URL
  # allowlist receives a local stub, so the test cannot contact GitHub or mutate it.
  evidence_urls=[
   'https://github.com/nolankido/nolankido.github.io/compare/2bf8908339e06f604cea00f0254494e17171ecf4...73782caa4697204690c679626b36427c28201234',
   'https://github.com/nolankido/nolankido.github.io/actions/runs/38196825689',
   'https://github.com/nolankido/nolankido.github.io/pull/40',
  ]
  for enabled in [True,False]:
   ctx=browser.new_context(java_script_enabled=enabled,reduced_motion='reduce')
   def evidence_route(r):
    if r.request.url in evidence_urls:r.fulfill(status=200,content_type='text/html',body='<title>Source destination</title><h1>Source destination</h1>')
    elif not args.offline and urlsplit(r.request.url).hostname=='127.0.0.1':r.continue_()
    else:r.abort()
   ctx.route('**/*',evidence_route);p=ctx.new_page();p.set_default_timeout(10000)
   for width in [390,1440]:
    p.set_viewport_size({'width':width,'height':1000});render(p,case)
    nav=p.get_by_role('navigation',name='Open the original evidence')
    expect(nav).to_be_visible();expect(nav.locator('a')).to_have_count(3)
    if os.environ.get('SCREENSHOT_DIR'):
     out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
     p.evaluate('document.fonts.ready')
     nav.screenshot(path=str(out/f'case-source-links-{width}-js-{enabled}.png'))
    for index,url in enumerate(evidence_urls):
     render(p,case);links=p.locator('#case-source-links a')
     # Start at the first source and reach the remaining destinations by Tab.
     links.first.focus()
     for _ in range(index):p.keyboard.press('Tab')
     expect(links.nth(index)).to_be_focused()
     expect(links.nth(index)).to_have_attribute('href',url)
     p.keyboard.press('Enter');expect(p).to_have_url(url)
     expect(p.get_by_role('heading',name='Source destination')).to_be_visible()
     report['case_source_keyboard_journeys']+=1
   ctx.close()
  for mode in ['disabled','blocked']:
   ctx=browser.new_context(java_script_enabled=mode!='disabled',reduced_motion='reduce')
   def fallback(r):
    if 'workflow-time.js' in r.request.url:r.abort()
    elif not args.offline and urlsplit(r.request.url).hostname=='127.0.0.1':r.continue_()
    else:r.abort()
   ctx.route('**/*',fallback);p=ctx.new_page();p.set_default_timeout(10000);render(p,calc,False)
   expect(p.locator('#time-editor')).to_be_hidden();expect(p.locator('#time-unavailable')).to_be_visible();expect(p.locator('.time-static-example')).to_have_count(3)
   expect(p.locator('#time-example-picker')).to_be_hidden()
   # The worksheet and page-sharing panel are distinct native disclosures.
   # Exercise the worksheet explicitly rather than assuming one details element.
   worksheet=p.locator('section[aria-labelledby="time-worksheet"] details')
   expect(worksheet).to_have_count(1)
   # The complete worksheet also prints while its native disclosure is closed,
   # including when JavaScript is disabled or the calculator asset is blocked.
   assert worksheet.get_attribute('open') is None
   expect(worksheet.locator('pre')).to_be_hidden();p.emulate_media(media='print')
   expect(p.locator('html')).to_have_css('background-color','rgb(255, 255, 255)')
   expect(p.locator('#time-editor')).to_be_hidden();expect(p.locator('#time-print-report')).to_be_hidden()
   expect(worksheet.locator('pre')).to_be_visible()
   assert worksheet.locator('pre').text_content()==(ROOT/'downloads/workflow-time-review.txt').read_text()
   assert worksheet.get_attribute('open') is None
   if mode=='disabled' and os.environ.get('SCREENSHOT_DIR'):
    out=Path(os.environ['SCREENSHOT_DIR']);out.mkdir(parents=True,exist_ok=True)
    pdf=p.pdf(path=str(out/'workflow-time-print-worksheet.pdf'),format='A4',print_background=True,
              margin={'top':'15mm','bottom':'15mm','left':'15mm','right':'15mm'})
    assert pdf.startswith(b'%PDF-');report['print_pdf_captures']+=1
   p.emulate_media(media='screen');expect(worksheet.locator('pre')).to_be_hidden()
   assert worksheet.get_attribute('open') is None;report['print_static_fallbacks']+=1
   worksheet.locator('summary').focus();p.keyboard.press('Enter')
   expect(worksheet).to_have_attribute('open','')
   assert worksheet.locator('pre').inner_text()==(ROOT/'downloads/workflow-time-review.txt').read_text()
   for width in [320,390,768,1440]:
    p.set_viewport_size({'width':width,'height':950});assert p.evaluate('document.documentElement.scrollWidth')<=width;report['layouts']+=1
   ctx.close();report['functional']+=1
  assert not errors,errors;browser.close()
 print('WORKFLOW_EVIDENCE_REPORT='+json.dumps(report))
finally:
 if server:server.shutdown();server.server_close()
 faulthandler.cancel_dump_traceback_later()
