"""Offline crawlability guard. Checks site outputs, not search-engine indexing."""
from pathlib import Path
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
import json, re
ROOT=Path(__file__).resolve().parents[1]
ROUTES=('/technology/task-brief/','/technology/check-ai-answers/','/technology/ai-time-savings/','/living-well/weekly-reset/','/poker/first-live-tournament/','/poker/hand-rankings/','/poker/school/')
class Parsed(HTMLParser):
    def __init__(self):
        super().__init__();self.title=False;self.title_text='';self.meta=[];self.links=[];self.h1=0;self.schemas=[];self.inside_schema=False
    def handle_starttag(self,tag,attributes):
        a=dict(attributes)
        if tag=='title':self.title=True
        if tag=='h1':self.h1+=1
        if tag=='meta':self.meta.append(a)
        if tag in ('link','a'):self.links.append(a)
        if tag=='script' and a.get('type')=='application/ld+json':self.inside_schema=True;self.schemas.append('')
    def handle_endtag(self,tag):
        if tag=='title':self.title=False
        if tag=='script':self.inside_schema=False
    def handle_data(self,value):
        if self.title:self.title_text+=value
        if self.inside_schema:self.schemas[-1]+=value
def check(root=ROOT):
    errors=[]
    robots=(root/'robots.txt').read_text()
    if 'Sitemap: https://nolankido.com/sitemap.xml' not in robots:errors.append('Missing sitemap declaration')
    if re.search(r'(?im)^\\s*Disallow:\\s*/\\s*$',robots):errors.append('Blanket robots block')
    tree=ET.fromstring((root/'sitemap.xml').read_text())
    ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    locs=[n.text for n in tree.findall('.//s:loc',ns)]
    for route in ROUTES:
        canonical='https://nolankido.com'+route
        if locs.count(canonical)!=1:errors.append(route+': sitemap entry count')
        path=root/route.strip('/')/'index.html'
        if not path.exists():errors.append(route+': missing file');continue
        page=Parsed();page.feed(path.read_text())
        if not page.title_text.strip():errors.append(route+': missing title')
        if len([m for m in page.meta if m.get('name')=='description' and m.get('content')])!=1:errors.append(route+': description')
        if page.h1!=1:errors.append(route+': h1 count')
        if [a.get('href') for a in page.links if a.get('rel')=='canonical']!=[canonical]:errors.append(route+': canonical')
        if [a.get('content') for a in page.meta if a.get('property')=='og:url']!=[canonical]:errors.append(route+': og:url')
        if any(re.search(r'\\bnoindex\\b',a.get('content',''),re.I) for a in page.meta if a.get('name') in ('robots','googlebot')):errors.append(route+': noindex')
        try: schemas=[json.loads(value) for value in page.schemas]
        except json.JSONDecodeError:errors.append(route+': invalid JSON-LD');schemas=[]
        if not any(isinstance(s,dict) and s.get('url')==canonical for s in schemas):errors.append(route+': schema URL')
    poker=Parsed();poker.feed((root/'poker/index.html').read_text())
    for route in ('/poker/hand-rankings/','/poker/school/'):
        if route not in [a.get('href') for a in poker.links]:errors.append('Poker missing link: '+route)
    if errors:raise ValueError('; '.join(errors))
    return {'result':'pass','priority_pages':len(ROUTES),'sitemap_entries':len(locs),'scope':'local generated outputs only'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
