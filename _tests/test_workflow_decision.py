"""A person's workflow decision stays explicit, current, private, and portable."""
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
import unittest

import html5lib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build

CHOICES = ['', 'keep', 'adjust', 'stop', 'observe']
FIELDS = ['time-personal-choice', 'time-personal-reason', 'time-personal-review']

# These event-driven fixtures run the production handler without network, storage,
# or a browser. Native control behavior and export downloads are covered separately
# by workflow_evidence_browser.py.
HARNESS = r"""
const vm=require('vm'),fs=require('fs');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const keys=['manual','assisted','review','count','setup','upkeep'];
const values=['30','8','7','6','60','15'];
function fixture(){
 const nodes=new Map(),events={},downloads=[],attached=[],printed=[];
 let focused='';
 for(const row of input.elements){
  const attrs={...row.attrs},handlers={};
  const node={id:attrs.id,tagName:row.tag.toUpperCase(),value:row.value||'',textContent:row.text||'',
   hidden:'hidden' in attrs,options:row.options||[],maxLength:Number(attrs.maxlength||-1),
   dataset:Object.fromEntries(Object.entries(attrs).filter(([k])=>k.startsWith('data-')).map(([k,v])=>[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase()),v])),
   handlers,addEventListener(type,fn){(handlers[type]??=[]).push(fn)},
   setAttribute(k,v){attrs[k]=String(v);if(k==='hidden')this.hidden=true},
   removeAttribute(k){delete attrs[k];if(k==='hidden')this.hidden=false},
   getAttribute(k){return attrs[k]??null},focus(){focused=this.id},scrollIntoView(){},
   select(){this.selectionStart=0;this.selectionEnd=this.value.length},
   querySelectorAll(selector){return selector==='[data-time-example]'?[...nodes.values()].filter(n=>n.dataset.timeExample):[]}
  };
  Object.defineProperty(node,'selectedOptions',{get(){return this.options.filter(o=>o.value===this.value)}});
  Object.defineProperty(node,'innerHTML',{set(){throw Error('Unexpected HTML execution sink')}});
  nodes.set(node.id,node);
 }
 const n=id=>nodes.get(id)||null;
 const root={addEventListener(type,fn){(events[type]??=[]).push(fn)},print(){printed.push(n('time-print-report').textContent)}};
 const context={window:root,navigator:{clipboard:{writeText:async()=>{}}},
  document:{getElementById:n,body:{appendChild(el){attached.push(el)}},createElement(tag){
   if(tag!=='a')throw Error('Unexpected element creation');
   return {click(){downloads.push({name:this.download,text:this.href.text})},remove(){attached.splice(attached.indexOf(this),1)}};
  }},Blob:class{constructor(parts){this.text=parts.join('')}},
  URL:{createObjectURL(blob){return blob},revokeObjectURL(){}},setTimeout(){}};
 vm.runInNewContext(input.script,context);
 const fire=(id,type='click')=>Promise.all((n(id).handlers[type]||[]).map(fn=>fn({type,target:n(id)})));
 async function edit(id,value,type='input'){n(id).value=value;await fire(id,type)}
 const snapshot=()=>({choice:n('time-personal-choice').value,reason:n('time-personal-reason').value,
  review:n('time-personal-review').value,status:n('time-personal-status').textContent,
  comparisonStatus:n('time-status').textContent,
  report:n('time-report').value,print:n('time-print-report').textContent,hidden:n('time-result').hidden,
  suggestion:n('time-decision').textContent,quality:n('time-quality-note').textContent,
  basis:n('time-basis-note').textContent,copy:n('time-copy-status').textContent,focused,
  inputs:keys.map(k=>n('time-'+k).value)});
 async function calculate(){await fire('time-calculate')}
 async function start(){for(let i=0;i<keys.length;i++)await edit('time-'+keys[i],values[i]);
  await edit('time-quality','pass','change');await edit('time-basis','observed','change');await calculate()}
 async function decide(){await edit('time-personal-choice','keep','change');
  await edit('time-personal-reason','Keep a manual review step.');await edit('time-personal-review','After three comparable attempts.')}
 return {n,context,fire,edit,snapshot,calculate,start,decide,downloads,printed,
  event(type){for(const fn of events[type]||[])fn({persisted:true})}};
}
(async()=>{
 const out={},f=fixture();await f.start();out.initial=f.snapshot();out.options={};
 for(const choice of ['', 'keep','adjust','stop','observe']){
  await f.edit('time-personal-choice',choice,'change');out.options[choice]=f.snapshot();
 }
 await f.decide();out.recorded=f.snapshot();await f.calculate();out.unchanged=f.snapshot();
 out.invalidations={};
 for(const [key,value,event] of [['manual','31','input'],['assisted','9','input'],['review','8','input'],
  ['count','7','input'],['setup','61','input'],['upkeep','16','input'],['basis','estimate','change'],['quality','fail','change']]){
  const c=fixture();await c.start();await c.decide();await c.edit('time-'+key,value,event);
  const invalid=c.snapshot();await c.calculate();const recalculated=c.snapshot();
  await c.edit('time-personal-choice','stop','change');out.invalidations[key]={invalid,recalculated,reconfirmed:c.snapshot()};
 }
 const unsafe='<img src=x onerror="window.decisionExecuted=true"> & private text';
 await f.edit('time-personal-reason',unsafe);await f.edit('time-personal-review','Review <script>nothing executes</script>');
 out.literal=f.snapshot();await f.fire('time-download');await f.fire('time-print');
 out.portable={downloads:f.downloads,printed:f.printed};out.stale=[];
 const bounded=fixture();await bounded.start();await bounded.edit('time-personal-reason','r'.repeat(1001));
 await bounded.edit('time-personal-review','v'.repeat(301));out.bounded=bounded.snapshot();
 for(const failure of [false,true]){
  const c=fixture();await c.start();await c.decide();let finish;
  c.context.navigator.clipboard.writeText=()=>new Promise((resolve,reject)=>{finish=failure?()=>reject(Error('denied')):resolve});
  const pending=c.fire('time-copy');await c.edit('time-personal-reason','Changed while copy was pending.');finish();await pending;
  out.stale.push(c.snapshot());
 }
 const clear=fixture();await clear.start();await clear.decide();const before=clear.snapshot();
 await clear.fire('time-clear');await clear.fire('time-clear-no');const cancelled=clear.snapshot();
 await clear.fire('time-clear');await clear.fire('time-clear-yes');out.clear={before,cancelled,confirmed:clear.snapshot()};
 out.lifecycle={};for(const event of ['pagehide','pageshow']){
  const c=fixture();await c.start();await c.decide();c.event(event);out.lifecycle[event]=c.snapshot();
 }
 process.stdout.write(JSON.stringify(out));
})().catch(error=>{process.stderr.write(error.stack);process.exitCode=1});
"""


def plain(node):
    return ''.join(node.itertext())


class WorkflowDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / '_source/technology/ai-time-savings.html').read_text()
        cls.outputs = build.build_outputs()
        cls.documents = {
            'source': html5lib.parseFragment(cls.source, namespaceHTMLElements=False),
            'generated': html5lib.parse(cls.outputs[Path('technology/ai-time-savings/index.html')], namespaceHTMLElements=False),
        }
        elements = []
        for el in cls.documents['source'].iter():
            if not el.get('id'):
                continue
            options = [{'value': option.get('value', ''), 'textContent': plain(option)} for option in el.findall('option')]
            value = options[0]['value'] if options else el.get('value', '')
            elements.append({'tag': el.tag, 'attrs': el.attrib, 'text': plain(el), 'value': value, 'options': options})
        run = subprocess.run(['node', '-e', HARNESS], input=json.dumps({
            'elements': elements, 'script': (ROOT / 'assets/workflow-time.js').read_text(),
        }), cwd=ROOT, capture_output=True, text=True, check=True)
        cls.cases = json.loads(run.stdout)

    def one(self, document, identifier):
        found = document.findall('.//*[@id="' + identifier + '"]')
        self.assertEqual(len(found), 1, identifier)
        return found[0]

    def test_native_optional_controls_are_inside_the_valid_result(self):
        for kind, document in self.documents.items():
            with self.subTest(document=kind):
                result = self.one(document, 'time-result')
                heading = self.one(result, 'time-personal-decision')
                self.assertEqual(heading.tag, 'h3')
                group = result.find('.//*[@aria-labelledby="time-personal-decision"]')
                self.assertIsNotNone(group)
                self.assertEqual(group.get('role'), 'group')
                choice = self.one(result, FIELDS[0])
                self.assertEqual(choice.tag, 'select')
                self.assertEqual([option.get('value') for option in choice.findall('option')], CHOICES)
                self.assertFalse(any('selected' in option.attrib for option in choice.findall('option')[1:]))
                for identifier, limit in [(FIELDS[1], '1000'), (FIELDS[2], '300')]:
                    field = self.one(result, identifier)
                    self.assertEqual(field.tag, 'textarea')
                    self.assertEqual(field.get('maxlength'), limit)
                    self.assertNotIn('required', field.attrib)
                for identifier in FIELDS:
                    self.assertNotIn('required', self.one(result, identifier).attrib)
                    self.assertIsNotNone(result.find('.//label[@for="' + identifier + '"]'))
                status = self.one(result, 'time-personal-status')
                self.assertEqual(status.get('role'), 'status')
                self.assertEqual(status.get('aria-live'), 'polite')

    def test_all_choices_are_explicit_and_independent_of_the_suggestion(self):
        self.assertEqual(self.cases['initial']['choice'], '')
        self.assertIn('Your decision: Not recorded', self.cases['initial']['report'])
        labels = {o.get('value'): plain(o) for o in self.one(self.documents['source'], FIELDS[0]).findall('option')}
        for choice, state in self.cases['options'].items():
            with self.subTest(choice=choice):
                self.assertEqual(state['choice'], choice)
                self.assertEqual(state['suggestion'], self.cases['initial']['suggestion'])
                self.assertEqual(state['quality'], self.cases['initial']['quality'])
                self.assertEqual(state['basis'], self.cases['initial']['basis'])
                self.assertIn('Suggested next step: ' + state['suggestion'], state['report'])
                self.assertIn('YOUR DECISION\n', state['report'])
                self.assertIn('Your decision: ' + (labels[choice] if choice else 'Not recorded'), state['report'])
                self.assertEqual(state['print'], state['report'])
                self.assertFalse(state['hidden'])

    def test_unchanged_recalculation_preserves_the_explicit_record(self):
        before, after = self.cases['recorded'], self.cases['unchanged']
        for key in ['choice', 'reason', 'review', 'report', 'print', 'inputs']:
            self.assertEqual(after[key], before[key], key)
        self.assertEqual(after['choice'], 'keep')

    def test_every_changed_comparison_requires_a_new_choice_but_retains_notes(self):
        for key, states in self.cases['invalidations'].items():
            with self.subTest(changed=key):
                invalid, recalculated, confirmed = (states[s] for s in ['invalid', 'recalculated', 'reconfirmed'])
                self.assertTrue(invalid['hidden'])
                self.assertEqual(invalid['report'], '')
                self.assertEqual(invalid['print'], '')
                for state in [invalid, recalculated]:
                    self.assertEqual(state['choice'], '')
                    self.assertEqual(state['reason'], 'Keep a manual review step.')
                    self.assertEqual(state['review'], 'After three comparable attempts.')
                self.assertIn('choose your decision again', invalid['comparisonStatus'])
                self.assertIn('Your notes are kept.', invalid['comparisonStatus'])
                self.assertIn('retained notes are drafts', recalculated['status'])
                self.assertIn('Choose again', recalculated['status'])
                self.assertIn('Your decision: Not recorded', recalculated['report'])
                self.assertEqual(recalculated['report'], recalculated['print'])
                self.assertEqual(confirmed['choice'], 'stop')
                self.assertEqual(confirmed['report'], confirmed['print'])
        failed = self.cases['invalidations']['quality']['reconfirmed']
        self.assertIn('Quality check not met', failed['report'])
        self.assertIn('STOP OR REDESIGN', failed['report'])

    def test_literal_notes_update_the_canonical_download_and_print_record(self):
        state = self.cases['literal']
        self.assertIn(state['reason'], state['report'])
        self.assertIn(state['review'], state['report'])
        self.assertEqual(state['print'], state['report'])
        self.assertEqual(self.cases['portable']['downloads'], [{'name': 'workflow-time-comparison.txt', 'text': state['report']}])
        self.assertEqual(self.cases['portable']['printed'], [state['report']])

    def test_programmatic_note_values_follow_the_declared_length_limits(self):
        state = self.cases['bounded']
        self.assertEqual(state['reason'], 'r' * 1000)
        self.assertEqual(state['review'], 'v' * 300)
        self.assertIn(state['reason'], state['report'])
        self.assertIn(state['review'], state['report'])
        self.assertEqual(state['print'], state['report'])

    def test_the_no_script_worksheet_is_the_unchanged_published_copy(self):
        path = ROOT / 'downloads/workflow-time-review.txt'
        raw = path.read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), '73b2dcd52e2461e74c32fb7541a981a6c4f68b6a3ed1bad28182a6177e31d613')
        worksheet = self.documents['generated'].find('.//section[@aria-labelledby="time-worksheet"]')
        self.assertEqual(plain(worksheet.find('.//pre')), raw.decode())
        self.assertIsNotNone(worksheet.find('.//a[@href="/downloads/workflow-time-review.txt"][@download]'))

    def test_pending_copy_success_and_failure_cannot_relabel_an_edited_record(self):
        for state in self.cases['stale']:
            self.assertEqual(state['reason'], 'Changed while copy was pending.')
            self.assertIn(state['reason'], state['report'])
            self.assertEqual(state['print'], state['report'])
            self.assertEqual(state['copy'], '')

    def test_clear_cancellation_preserves_and_confirmation_discards_the_record(self):
        states = self.cases['clear']
        for key in ['choice', 'reason', 'review', 'report', 'print', 'inputs']:
            self.assertEqual(states['cancelled'][key], states['before'][key], key)
        for state in [states['confirmed'], *self.cases['lifecycle'].values()]:
            for key in ['choice', 'reason', 'review', 'report', 'print']:
                self.assertEqual(state[key], '', key)
            self.assertTrue(state['hidden'])
            self.assertEqual(state['inputs'], [''] * 6)


if __name__ == '__main__':
    unittest.main()
