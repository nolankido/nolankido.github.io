/* Exercise public input events with a deterministic timer and focus model. */
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const nodes = {}, timers = new Map(), events = {}, result = {};
let active = null, serial = 0;
for (const id of ['find-controls','find-query','find-interest','find-kind','find-status','find-results','find-empty','find-submit','find-reset']) {
  nodes[id] = {value:'',hidden:false,textContent:'',events:{},
    addEventListener(type, handler) { this.events[type] = handler; },
    focus() { active = id; },
    fire(type, data = {}) { this.events[type]?.(data); }};
}
const context = {document:{getElementById:id=>nodes[id],querySelectorAll:()=>[]},
  window:{addEventListener:(type,handler)=>events[type]=handler},
  setTimeout:handler=>{timers.set(++serial,handler);return serial;},
  clearTimeout:id=>timers.delete(id)};
let script = fs.readFileSync(path.join(root,'assets/site-find.js'),'utf8');
if (process.argv[2] === 'baseline') {
  const baseline = JSON.parse(fs.readFileSync(path.join(__dirname,'find-submission-baseline.json'),'utf8'));
  script = script.replace(baseline.new_handler,baseline.old_handler);
}
vm.runInNewContext(script,context);
const query = nodes['find-query'];
query.focus();query.value='family story';query.fire('input',{isComposing:false});
result.typing = {active,pending:timers.size};
const status = nodes['find-status'].textContent;
query.fire('compositionstart');
result.compositionStart = {active,pending:timers.size};
query.fire('input',{isComposing:true});
for (const [name,extra] of [['composing',{isComposing:true,keyCode:13}],['boundary',{isComposing:false,keyCode:229}]]) {
  let prevented = false;
  query.fire('keydown',{key:'Enter',...extra,preventDefault(){prevented=true;}});
  result[name] = {active,prevented,pending:timers.size,statusUnchanged:nodes['find-status'].textContent===status};
}
query.fire('compositionend');
result.compositionEnd = {active,pending:timers.size,heading:nodes['find-results'].textContent};
let prevented = false;
query.fire('keydown',{key:'Enter',isComposing:false,keyCode:13,preventDefault(){prevented=true;}});
result.enter = {active,prevented};
nodes['find-submit'].focus();nodes['find-submit'].fire('click');result.button = {active};
for (const id of ['find-interest','find-kind']) {
  nodes[id].focus();nodes[id].fire('change');result[id] = {active};
}
query.focus();query.fire('input',{isComposing:false});
for (const callback of [...timers.values()])callback();
result.live = {active,pending:timers.size};
nodes['find-reset'].fire('click');result.reset = {active,value:query.value,heading:nodes['find-results'].textContent};
query.value='temporary query';query.fire('input',{isComposing:false});events.pagehide();
result.leave = {value:query.value,pending:timers.size};
process.stdout.write(JSON.stringify(result));
