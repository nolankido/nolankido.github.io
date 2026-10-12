"""Independent rule table, unchanged history, discovery, privacy and icon formats."""
from copy import deepcopy
from hashlib import sha256
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
import json,re,struct,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,ai_task_choice,check_live
from test_site import Page
ID='ai-task-choice'
PATH='/technology/should-i-use-ai/'
OPTIONS={'goal':['clear','unclear'],'inputs':['allowed','restricted','unknown'],'stakes':['low','high'],
         'review':['ready','missing'],'simpler':['yes','no','unknown'],'scope':['draft','action']}
ADDITION=re.compile(r'<!-- AI task choice: start -->\n.*?<!-- AI task choice: end -->\n',re.S)

def signature(el):
    return [el.tag,[list(a) for a in sorted(el.attrib.items())],(el.text or '').strip(),[signature(c) for c in el]]

def original_source(path,raw):
    if path in {'_source/technology/home.html','_source/resources.html'}:
        return ADDITION.sub('',raw.decode()).encode()
    if path=='_source/layout.html':
        return raw.decode().replace('  <link rel="icon" href="/favicon.png" type="image/png" sizes="96x96">\n','').replace('  <link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">\n','').encode()
    if path=='_source/pages.json':
        return (json.dumps([p for p in json.loads(raw) if p['id']!=ID],indent=2,ensure_ascii=False)+'\n').encode()
    return raw

class TaskChoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=build.public_pages(); cls.outputs=build.build_outputs()
        cls.html=cls.outputs[build.output_path(PATH)]
        cls.baseline=json.loads((ROOT/'_tests/ai-task-choice-baseline.json').read_text())
    def decisions(self,inputs):
        code="const {decide}=require('./assets/ai-task-choice.js');const fs=require('fs');console.log(JSON.stringify(JSON.parse(fs.readFileSync(0,'utf8')).map(x=>{try{return decide(x)}catch(e){return {error:e.name}}})));"
        return json.loads(subprocess.run(['node','-e',code],cwd=ROOT,input=json.dumps(inputs),capture_output=True,text=True,check=True).stdout)
    def test_all_144_combinations_follow_independent_precedence(self):
        inputs=[dict(zip(OPTIONS,values)) for values in product(*OPTIONS.values())]
        self.assertEqual(len(inputs),144)
        for values,result in zip(inputs,self.decisions(inputs)):
            if values['inputs']!='allowed' or values['stakes']=='high':expected='pause'
            elif values['goal']=='unclear' or values['review']=='missing':expected='prepare'
            elif values['simpler']!='no':expected='simpler'
            elif values['scope']=='action':expected='prepare'
            else:expected='trial'
            self.assertEqual(result['kind'],expected,values)
            self.assertTrue(result['reasons']);self.assertTrue(result['next'])
            self.assertIn(result['route'],{'#choice-method','/technology/task-brief/','/technology/ai-time-savings/'})
    def test_all_unresolved_conditions_remain_visible(self):
        value={'goal':'unclear','inputs':'restricted','stakes':'high','review':'missing','simpler':'unknown','scope':'action'}
        result=self.decisions([value])[0]
        self.assertEqual(result['kind'],'pause');self.assertEqual(len(result['reasons']),6)
        text=' '.join(result['reasons'])
        for term in ['permission','qualified review','independent','finished result','ordinary method','external action']:self.assertIn(term,text)
    def test_unknown_missing_extra_and_malformed_answers_fail_closed(self):
        valid=dict(zip(OPTIONS,['clear','allowed','low','ready','no','draft']))
        invalid=[None,[],{},'yes',{**valid,'extra':'bad'}]
        for k in OPTIONS:
            x=valid.copy();del x[k];invalid.append(x)
            invalid.append({**valid,k:'<script>'})
        self.assertTrue(all(x=={'error':'TypeError'} for x in self.decisions(invalid)))
    def test_every_original_source_asset_and_download_is_preserved(self):
        for path,expected in self.baseline['files'].items():
            raw=original_source(path,(ROOT/path).read_bytes())
            self.assertEqual(sha256(raw).hexdigest(),expected,path)
    def test_original_page_identity_dates_and_feed_records_are_preserved(self):
        now=json.loads((ROOT/'_source/pages.json').read_text())
        self.assertEqual([p for p in now if p['id']!=ID],self.baseline['manifest'])
        for path,old in self.baseline['feeds'].items():
            channel=ET.fromstring((ROOT/path).read_text()).find('channel')
            items={i.findtext('guid'):signature(i) for i in channel.findall('item')}
            allowed='https://nolankido.com'+PATH
            self.assertEqual({k:v for k,v in items.items() if k!=allowed},old['items'],path)
            self.assertEqual([signature(e) for e in channel if e.tag!='item'],old['channel'],path)
    def test_167_original_rendered_bodies_preserved_with_only_marked_additions(self):
        # Writing and search gain a new record; all other previous page bodies
        # remain exact after removing the two explicitly marked hub additions.
        self.assertEqual(len(self.baseline['bodies']),167)
        for path,expected in self.baseline['bodies'].items():
            body=re.search(r'<body\b[^>]*>(.*?)</body>',self.outputs[Path(path)],re.S)[1]
            self.assertEqual(sha256(ADDITION.sub('',body).encode()).hexdigest(),expected,path)
    def test_historical_adapter_reverses_only_reviewed_additions(self):
        import choice_history
        for path,expected in self.baseline['all_bodies'].items():
            restored=choice_history.before(path,self.outputs[Path(path)])
            body=re.search(r'<body\b[^>]*>(.*?)</body>',restored,re.S)[1]
            self.assertEqual(sha256(body.encode()).hexdigest(),expected,path)
        self.assertEqual(sha256((ROOT/'favicon.svg').read_bytes()).hexdigest(),self.baseline['icon'])

    def test_native_questions_match_rule_domains_without_free_text(self):
        tags=Page(self.html)
        inputs=tags.tags('input');self.assertEqual(len(inputs),14)
        self.assertTrue(all(i.get('type')=='radio' and 'required' in i for i in inputs))
        for key,values in OPTIONS.items():self.assertEqual([i['value'] for i in inputs if i['name']==key],values)
        self.assertNotIn('<textarea',self.html);self.assertNotIn('type="file"',self.html)
        self.assertIn('id="choice-form" hidden',self.html)
    def test_form_labels_are_escaped_and_configuration_cannot_change_rule_domains(self):
        cfg=json.loads((ROOT/'_source/ai-task-choice.json').read_text())
        with TemporaryDirectory() as temp:
            root=Path(temp);(root/'_source').mkdir();p=root/'_source/ai-task-choice.json'
            copy=deepcopy(cfg);copy[0]['title']='<b>unsafe</b>';p.write_text(json.dumps(copy))
            self.assertIn('&lt;b&gt;unsafe&lt;/b&gt;',ai_task_choice.questions(root))
            copy[0]['options'][0][0]='javascript:bad';p.write_text(json.dumps(copy))
            with self.assertRaises(ValueError):ai_task_choice.questions(root)
    def test_worksheet_exact_preview_and_honest_limits(self):
        from html import unescape
        preview=re.search(r'<details class="choice-sheet">.*?<pre>(.*?)</pre>',self.html,re.S)[1]
        self.assertEqual(unescape(preview),(ROOT/ai_task_choice.SHEET).read_text())
        self.assertEqual(self.html.count('class="choice-example"'),4)
        for phrase in ['No AI runs here','not a validated assessment','Fictional','not a NIST assessment','cannot supply another person']:self.assertIn(phrase,self.html)
    def test_discovery_authorship_feeds_and_canonical(self):
        for path in ['technology/index.html','resources/index.html','notes/index.html','find/index.html']:
            self.assertIn(PATH,self.outputs[Path(path)],path)
        metadata=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',self.html,re.S)[1])
        self.assertEqual(metadata['@type'],'Article');self.assertEqual(metadata['author']['name'],'Nolan Kido')
        self.assertEqual(metadata['datePublished'],'2026-10-12')
        self.assertIn('href="https://nolankido.com'+PATH+'"',self.html)
        for path in ['technology/feed.xml','writing.xml']:
            items=ET.fromstring((ROOT/path).read_text()).findall('./channel/item')
            self.assertEqual(sum(i.findtext('link')=='https://nolankido.com'+PATH for i in items),1)
    def test_no_network_storage_input_capture_or_html_injection(self):
        script=(ROOT/'assets/ai-task-choice.js').read_text()
        for forbidden in ['fetch(', 'XMLHttpRequest','localStorage','sessionStorage','sendBeacon','innerHTML','document.cookie','location.search']:
            self.assertNotIn(forbidden,script)
        self.assertIn("addEventListener('change'",script);self.assertIn("addEventListener('pagehide'",script)
    def test_raster_icon_dimensions_crawlable_link_and_live_inventory(self):
        for path,size in [('favicon.png',96),('apple-touch-icon.png',180)]:
            raw=(ROOT/path).read_bytes()
            self.assertEqual(raw[:8],b'\x89PNG\r\n\x1a\n');self.assertEqual(struct.unpack('>II',raw[16:24]),(size,size));self.assertLess(len(raw),10000)
            for p in self.pages:self.assertIn('href="/'+path+'"',self.outputs[build.output_path(p['path'])])
        targets=check_live.targets()
        for path in [PATH,'/favicon.png','/apple-touch-icon.png','/assets/ai-task-choice.js','/assets/ai-task-choice.css','/downloads/should-i-use-ai.txt']:
            self.assertEqual(targets[path][0],200)

if __name__=='__main__':unittest.main(verbosity=2)
