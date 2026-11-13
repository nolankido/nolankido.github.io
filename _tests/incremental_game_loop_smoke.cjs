/* Deterministic model and mocked-browser interaction checks. No dependencies. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const script = path.resolve(__dirname, '../assets/incremental-game-loop.js');
const game = require(script);
assert.equal(game.GOAL, 150);
assert.equal(game.MAX_UPGRADES, 15);
assert.deepEqual([0, 1, 2].map(n => game.upgradeCost('pencil', n)), [10, 17, 29]);
assert.deepEqual([0, 1, 2].map(n => game.upgradeCost('routine', n)), [25, 50, 100]);
assert.equal(game.upgradeCost('pencil', 15), null);
assert.equal(game.upgradeCost('routine', -1), null);
assert.equal(game.upgradeCost('invented', 0), null);

let state = game.initialState();
for (let i = 0; i < 10; i++) state = game.tap(state);
assert.equal(state.bank, 10);
assert.equal(state.total, 10);
assert.equal(game.buy(state, 'routine'), state, 'Cannot buy an unaffordable upgrade');
state = game.buy(state, 'pencil');
assert.deepEqual(state, {bank:0, total:10, pencil:1, routine:0, paused:false});
for (let i = 0; i < 13; i++) state = game.tap(state);
assert.equal(state.bank, 26);
assert.equal(state.total, 36);
state = game.buy(state, 'routine');
assert.deepEqual(state, {bank:1, total:36, pencil:1, routine:1, paused:false});
assert.equal(game.tick(state, false), state, 'Hidden page does not advance');
assert.deepEqual(game.tick({...state, paused:true}, true), {...state, paused:true});
state = game.tick(state, true);
assert.equal(state.bank, 2);
assert.equal(state.total, 37);
assert.equal(game.buy({...state, bank:999999, pencil:15}, 'pencil').pencil, 15);

class Element {
  constructor() { this.hidden = false; this.disabled = false; this.textContent = ''; this.attributes = {}; this.events = {}; }
  addEventListener(type, callback) { this.events[type] = callback; }
  setAttribute(name, value) { this.attributes[name] = value; }
  focus() { this.focused = true; }
  click() { if (!this.disabled) this.events.click?.(); }
}
const elements = new Map();
for (const name of ['game-lab', 'lab-fallback', 'lab-bank', 'lab-total', 'lab-per-tap',
  'lab-per-second', 'lab-progress', 'lab-progress-copy', 'lab-tap', 'lab-pencil',
  'lab-routine', 'lab-pencil-count', 'lab-routine-count', 'lab-pause', 'lab-reset',
  'lab-action-status']) elements.set(name, new Element());
elements.get('game-lab').hidden = true;
const document = { hidden: false, getElementById: id => elements.get(id) || null };
let callback;
const window = {setInterval: (fn, interval) => {
  assert.equal(interval, 1000);
  callback = fn;
}};
vm.runInNewContext(fs.readFileSync(script, 'utf8'), {document, window});
const el = id => elements.get(id);
assert.equal(el('game-lab').hidden, false);
assert.equal(el('lab-fallback').hidden, true);
assert.equal(el('lab-pencil').disabled, true);
for (let i = 0; i < 10; i++) el('lab-tap').click();
assert.equal(el('lab-bank').textContent, '10');
assert.equal(el('lab-pencil').disabled, false);
el('lab-pencil').click();
assert.equal(el('lab-bank').textContent, '0');
assert.equal(el('lab-per-tap').textContent, '2');
for (let i = 0; i < 13; i++) el('lab-tap').click();
assert.equal(el('lab-total').textContent, '36');
el('lab-routine').click();
assert.equal(el('lab-bank').textContent, '1');
assert.equal(el('lab-per-second').textContent, '1');
document.hidden = true;
callback();
assert.equal(el('lab-total').textContent, '36');
document.hidden = false;
callback();
assert.equal(el('lab-total').textContent, '37');
el('lab-pause').click();
assert.equal(el('lab-pause').attributes['aria-pressed'], 'true');
callback();
assert.equal(el('lab-total').textContent, '37');
el('lab-tap').click();
assert.equal(el('lab-total').textContent, '39', 'Manual taps still work while paused');
el('lab-pause').click();
assert.equal(el('lab-pause').attributes['aria-pressed'], 'false');
for (let i = 0; i < 56; i++) el('lab-tap').click();
assert.ok(Number(el('lab-total').textContent) >= 150);
assert.match(el('lab-action-status').textContent, /Goal reached/);
assert.equal(el('lab-progress').value, 150);
el('lab-reset').click();
assert.equal(el('lab-total').textContent, '0');
assert.equal(el('lab-bank').textContent, '0');
assert.equal(el('lab-progress').value, 0);
assert.equal(el('lab-tap').focused, true);
console.log('Incremental game model and browser interactions: PASS');
