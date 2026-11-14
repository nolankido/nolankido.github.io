/* Exact calculations and form interactions, without browser packages. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const script = path.resolve(__dirname, '../assets/incremental-upgrade-payback.js');
const {calculate, LIMITS, formatScenario} = require(script);
const example = {bank:25, taps:20, seconds:60, pencilCost:10, routineCost:25};
const first = calculate(example);
assert.equal(first.noBuy, 45);
assert.equal(first.pencil, 55);
assert.equal(first.routine, 80);
assert.deepEqual(first.leaders, ['Buy daily routine']);
assert.equal(first.routineMinusPencil, 25);
assert.equal(first.routineThresholdSeconds, 35);
assert.equal(first.pencilPaybackTaps, 10);
assert.equal(first.routinePaybackSeconds, 25);
const firstRecord = formatScenario(example, first);
assert.match(firstRecord, /Starting available sparks \(B\): 25/);
assert.match(firstRecord, /Planned taps after purchase \(N\): 20/);
assert.match(firstRecord, /Visible, unpaused seconds \(T\): 60/);
assert.match(firstRecord, /\| Buy one sharper pencil \| B - C \+ 2 x N \| 55 sparks \|/);
assert.match(firstRecord, /\| Buy one daily routine \| B - R \+ N \+ T \| 80 sparks \|/);
assert.match(firstRecord, /Highest-balance path\(s\): Buy daily routine/);
assert.match(firstRecord, /Routine minus pencil: 25 sparks/);
assert.match(firstRecord, /T = N \+ R - C = 35 seconds/);
assert.match(firstRecord, /not an observation of a player/);
assert.equal(firstRecord, formatScenario(example, first));

const fastTaps = calculate({...example, taps:60});
assert.deepEqual([fastTaps.noBuy, fastTaps.pencil, fastTaps.routine], [85, 135, 120]);
assert.deepEqual(fastTaps.leaders, ['Buy sharper pencil']);
assert.equal(fastTaps.routineMinusPencil, -15);

const tie = calculate({...example, seconds:35});
assert.equal(tie.pencil, tie.routine);
assert.deepEqual(tie.leaders, ['Buy sharper pencil', 'Buy daily routine']);
assert.match(formatScenario({...example, seconds:35}, tie), /The upgrades tie/);

const none = calculate({...example, bank:5});
assert.equal(none.noBuy, 25);
assert.equal(none.pencil, null);
assert.equal(none.routine, null);
assert.deepEqual(none.leaders, ['Buy nothing']);
const unavailableRecord = formatScenario({...example, bank:5}, none);
assert.match(unavailableRecord, /Unavailable: not affordable at start/);
assert.match(unavailableRecord, /not comparable because at least one purchase is unaffordable/);
assert.match(unavailableRecord, /tie threshold: not applicable/);
assert.doesNotMatch(unavailableRecord, /Routine minus pencil: -?\d+/);
const pencilOnly = calculate({...example, bank:10});
assert.equal(pencilOnly.routine, null);
assert.equal(pencilOnly.pencil, 40);
assert.deepEqual(pencilOnly.leaders, ['Buy sharper pencil']);
assert.deepEqual(calculate({...example, taps:0, seconds:0}).leaders, ['Buy nothing']);
const negativeTie = {...example, taps:1, seconds:0, pencilCost:20, routineCost:1};
assert.match(formatScenario(negativeTie, calculate(negativeTie)),
  /A nonnegative duration cannot reach that tie/);

for (const bad of [
  {...example, bank:-1}, {...example, taps:1001}, {...example, seconds:601},
  {...example, pencilCost:0}, {...example, routineCost:1000001},
  {...example, taps:2.5}, {...example, bank:NaN}
]) assert.throws(() => calculate(bad), RangeError);
assert.deepEqual(LIMITS.seconds, [0, 600]);

for (let n = 0; n <= 120; n += 10) {
  for (let seconds = 0; seconds <= 120; seconds += 20) {
    const v = {...example, taps:n, seconds};
    const outcome = calculate(v);
    assert.equal(outcome.routineMinusPencil, v.pencilCost - v.routineCost + seconds - n);
    assert.equal(outcome.noBuy, v.bank + n);
  }
}

class Element {
  constructor() { this.hidden = false; this.textContent = ''; this.events = {}; this.attributes = {}; this.value = ''; }
  addEventListener(event, fn) { this.events[event] = fn; }
  setAttribute(name, value) { this.attributes[name] = value; }
  removeAttribute(name) { delete this.attributes[name]; if (name === 'href') this.href = ''; }
  focus(options) { this.focused = true; this.focusOptions = options; }
  scrollIntoView(options) { this.scrollOptions = options; }
  emit(event, payload) { this.events[event]?.(payload); }
}
const allIds = ['form', 'fallback', 'result', 'bank', 'taps', 'seconds', 'pencil-cost',
  'routine-cost', 'feedback', 'result-title', 'no-buy', 'pencil-final',
  'routine-final', 'winner', 'breakeven', 'assumptions', 'report', 'download',
  'preset-20', 'preset-60'];
const elements = new Map(allIds.map(id => ['payback-' + id, new Element()]));
const get = id => elements.get('payback-' + id);
get('form').hidden = true;
get('result').hidden = true;
get('download').hidden = true;
for (const [id, value] of [['bank','25'],['taps','20'],['seconds','60'],
  ['pencil-cost','10'],['routine-cost','25']]) get(id).value = value;
const document = {getElementById: id => elements.get(id) || null};
const blobUrls = new Map();
const revoked = [];
const fakeUrl = {
  createObjectURL(blob) { const url = 'blob:mock-' + (blobUrls.size + 1); blobUrls.set(url, blob); return url; },
  revokeObjectURL(url) { revoked.push(url); }
};
vm.runInNewContext(fs.readFileSync(script, 'utf8'), {document, Blob, URL:fakeUrl});
assert.equal(get('form').hidden, false);
assert.equal(get('fallback').hidden, true);

let prevented = false;
get('form').emit('submit', {preventDefault: () => {prevented = true;}});
assert.equal(prevented, true);
assert.equal(get('result').hidden, false);
assert.equal(get('no-buy').textContent, '45');
assert.equal(get('pencil-final').textContent, '55');
assert.equal(get('routine-final').textContent, '80');
assert.match(get('winner').textContent, /Buy daily routine/);
assert.equal(get('result-title').focused, true);
assert.equal(get('result-title').focusOptions.preventScroll, true);
assert.equal(get('result').scrollOptions.block, 'start');
assert.equal(get('result').scrollOptions.behavior, 'instant');
assert.equal(get('download').hidden, false);
assert.equal(get('download').href, 'blob:mock-1');
assert.equal(blobUrls.get(get('download').href).type, 'text/markdown;charset=utf-8');
assert.equal(blobUrls.get(get('download').href).size, Buffer.byteLength(firstRecord));
assert.equal(get('report').value, firstRecord);

get('preset-60').emit('click');
assert.deepEqual(revoked, ['blob:mock-1']);
assert.equal(get('taps').value, '60');
assert.equal(get('routine-final').textContent, '120');
assert.equal(get('pencil-final').textContent, '135');
assert.match(get('winner').textContent, /Buy sharper pencil/);
assert.equal(get('result').hidden, false);
assert.match(get('report').value, /Planned taps after purchase \(N\): 60/);
assert.equal(get('download').hidden, false);

get('preset-20').emit('click');
assert.equal(get('taps').value, '20');
assert.equal(get('pencil-final').textContent, '55');
assert.equal(get('routine-final').textContent, '80');
assert.match(get('winner').textContent, /Buy daily routine/);
get('taps').value = '55';
get('form').emit('input');
assert.equal(get('result').hidden, true);
assert.equal(get('download').hidden, true);
assert.equal(get('download').href, '');
assert.equal(get('report').value, '');
assert.match(get('feedback').textContent, /Inputs changed/);

get('taps').value = '60';
get('form').emit('submit', {preventDefault:()=>{}});
assert.equal(get('pencil-final').textContent, '135');
assert.equal(get('routine-final').textContent, '120');
assert.match(get('winner').textContent, /Buy sharper pencil/);

get('bank').value = '5';
get('form').emit('submit', {preventDefault:()=>{}});
assert.equal(get('pencil-final').textContent, 'Not affordable at start');
assert.equal(get('routine-final').textContent, 'Not affordable at start');
assert.match(get('breakeven').textContent, /unavailable/);
assert.match(get('breakeven').textContent, /if purchased now/);
assert.doesNotMatch(get('breakeven').textContent, /overtakes pencil/);

get('seconds').value = '601';
get('form').emit('submit', {preventDefault:()=>{}});
assert.equal(get('result').hidden, true);
assert.equal(get('seconds').attributes['aria-invalid'], 'true');
assert.equal(get('seconds').focused, true);
assert.match(get('feedback').textContent, /whole number/);
assert.equal(get('download').hidden, true);
assert.equal(get('report').value, '');

get('preset-20').emit('click');
assert.equal(get('bank').value, '25');
assert.equal(get('seconds').value, '60');
assert.equal(get('pencil-cost').value, '10');
assert.equal(get('routine-cost').value, '25');
assert.equal(get('seconds').attributes['aria-invalid'], undefined);
assert.equal(get('result').hidden, false);
assert.equal(get('routine-final').textContent, '80');

get('taps').value = '1';
get('seconds').value = '0';
get('pencil-cost').value = '20';
get('routine-cost').value = '1';
get('form').emit('submit', {preventDefault:()=>{}});
assert.match(get('breakeven').textContent, /every nonnegative duration/);
assert.match(get('winner').textContent, /Buy nothing/);

get('form').emit('reset');
assert.equal(get('result').hidden, true);
assert.equal(get('download').hidden, true);
assert.equal(get('report').value, '');
assert.equal(get('seconds').attributes['aria-invalid'], undefined);
assert.match(get('feedback').textContent, /Example restored/);
assert.ok(revoked.length >= 5);

// A browser with no Blob URL download support still reveals a copyable record.
const fallbackElements = new Map(allIds.map(id => ['payback-' + id, new Element()]));
fallbackElements.get('payback-form').hidden = true;
fallbackElements.get('payback-result').hidden = true;
fallbackElements.get('payback-download').hidden = true;
for (const [id, value] of [['bank','25'],['taps','20'],['seconds','60'],
  ['pencil-cost','10'],['routine-cost','25']]) fallbackElements.get('payback-' + id).value = value;
vm.runInNewContext(fs.readFileSync(script, 'utf8'), {
  document: {getElementById: id => fallbackElements.get(id) || null}
});
fallbackElements.get('payback-form').emit('submit', {preventDefault:()=>{}});
assert.equal(fallbackElements.get('payback-result').hidden, false);
assert.equal(fallbackElements.get('payback-download').hidden, true);
assert.equal(fallbackElements.get('payback-report').value, firstRecord);
console.log('Incremental upgrade math and browser form interactions: PASS');
