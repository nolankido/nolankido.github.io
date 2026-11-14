/* Exact calculations and form interactions, without browser packages. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const script = path.resolve(__dirname, '../assets/incremental-upgrade-payback.js');
const {calculate, LIMITS} = require(script);
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

const fastTaps = calculate({...example, taps:60});
assert.deepEqual([fastTaps.noBuy, fastTaps.pencil, fastTaps.routine], [85, 135, 120]);
assert.deepEqual(fastTaps.leaders, ['Buy sharper pencil']);
assert.equal(fastTaps.routineMinusPencil, -15);

const tie = calculate({...example, seconds:35});
assert.equal(tie.pencil, tie.routine);
assert.deepEqual(tie.leaders, ['Buy sharper pencil', 'Buy daily routine']);

const none = calculate({...example, bank:5});
assert.equal(none.noBuy, 25);
assert.equal(none.pencil, null);
assert.equal(none.routine, null);
assert.deepEqual(none.leaders, ['Buy nothing']);
const pencilOnly = calculate({...example, bank:10});
assert.equal(pencilOnly.routine, null);
assert.equal(pencilOnly.pencil, 40);
assert.deepEqual(pencilOnly.leaders, ['Buy sharper pencil']);
assert.deepEqual(calculate({...example, taps:0, seconds:0}).leaders, ['Buy nothing']);

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
  removeAttribute(name) { delete this.attributes[name]; }
  focus() { this.focused = true; }
  emit(event, payload) { this.events[event]?.(payload); }
}
const allIds = ['form', 'fallback', 'result', 'bank', 'taps', 'seconds', 'pencil-cost',
  'routine-cost', 'feedback', 'result-title', 'no-buy', 'pencil-final',
  'routine-final', 'winner', 'breakeven', 'assumptions'];
const elements = new Map(allIds.map(id => ['payback-' + id, new Element()]));
const get = id => elements.get('payback-' + id);
get('form').hidden = true;
get('result').hidden = true;
for (const [id, value] of [['bank','25'],['taps','20'],['seconds','60'],
  ['pencil-cost','10'],['routine-cost','25']]) get(id).value = value;
const document = {getElementById: id => elements.get(id) || null};
vm.runInNewContext(fs.readFileSync(script, 'utf8'), {document});
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

get('seconds').value = '601';
get('form').emit('submit', {preventDefault:()=>{}});
assert.equal(get('result').hidden, true);
assert.equal(get('seconds').attributes['aria-invalid'], 'true');
assert.equal(get('seconds').focused, true);
assert.match(get('feedback').textContent, /whole number/);

get('form').emit('reset');
assert.equal(get('result').hidden, true);
assert.equal(get('seconds').attributes['aria-invalid'], undefined);
assert.match(get('feedback').textContent, /Example restored/);
console.log('Incremental upgrade math and browser form interactions: PASS');
