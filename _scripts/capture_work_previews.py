"""Developer-only real-page capture. Does not run as part of a public page."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
from io import BytesIO
import sys,json,hashlib,os,argparse
parser=argparse.ArgumentParser(description="Capture real fictional-example outputs for the Technology work previews. Requires Playwright and Pillow; blocks all network requests.")
parser.add_argument("--baseline",required=True,help="Reviewed source commit for the existing tool implementations")
args=parser.parse_args()
if len(args.baseline)!=40 or any(c not in "0123456789abcdef" for c in args.baseline):raise ValueError("Expected a full source commit SHA")
root=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(root/'_tests'))
from browser import html_for
out=root/'assets/work';out.mkdir(parents=True,exist_ok=True)
records=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,**({'executable_path':os.environ['CHROMIUM_PATH']} if os.environ.get('CHROMIUM_PATH') else {}))
 ctx=b.new_context(viewport={'width':1440,'height':1000},device_scale_factor=1,reduced_motion='reduce')
 ctx.route('**/*',lambda r:r.abort())
 p=ctx.new_page();p.set_default_timeout(15000)
 for slug,route,script,selector in [('task-brief','/technology/task-brief/','task-brief.js','#brief-result'),('ai-time-savings','/technology/ai-time-savings/','workflow-time.js','#time-result')]:
  p.set_content(html_for(route));p.add_script_tag(content=(root/'assets'/script).read_text())
  if slug=='task-brief':
   p.locator('[data-brief-example="writing"] summary').click();p.locator('[data-use-example="writing"]').click();p.locator('#brief-build').click();inputs={'example':'writing (existing illustrative example)'}
  else:
   inputs={'manual':'30','assisted':'8','review':'7','count':'6','setup':'60','upkeep':'15'}
   for k,v in inputs.items():p.locator('#time-'+k).fill(v)
   p.locator('#time-calculate').click()
  p.evaluate('document.activeElement.blur()')
  raw=p.locator(selector).screenshot()
  img=Image.open(BytesIO(raw)).convert('RGB'); full=img.size
  img=img.crop((0,0,img.width,min(img.height,600)))
  path=out/(slug+'-preview.png'); img.save(path,optimize=True)
  records.append({'id':slug,'route':route,'selector':selector,'capture':'Rendered committed HTML with local styles and JavaScript, external requests blocked; fallback fonts. Top-of-result excerpt, no result text edited.','baseline_commit':args.baseline,'input_basis':'fictional teaching example','inputs':inputs,'src':'/'+path.relative_to(root).as_posix(),'width':img.width,'height':img.height,'full_result_size':full,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'dependencies':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in ['_source/technology/'+('task-brief.html' if slug=='task-brief' else 'ai-time-savings.html'),'assets/'+script,'assets/'+('task-brief.css' if slug=='task-brief' else 'workflow-evidence.css'),'styles.css','assets/site.css']}})
  assert img.size==(1044,600), (slug,img.size)
  assert path.stat().st_size<=160_000
  print(slug,img.size,path.stat().st_size)
 b.close()
(root/'_reports/work-preview-provenance.json').write_text(json.dumps(records,indent=2)+'\n')
