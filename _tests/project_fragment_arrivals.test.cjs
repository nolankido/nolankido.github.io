/* Turn 142: simulate the browser's fragment arrival and input-cancellation timing. */
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const script = fs.readFileSync(path.join(__dirname, '..', 'assets', 'project-fragment-arrivals.js'), 'utf8');

async function arrival({page = 'page-ai-book-continuity-checker', hash = '#continuity-example', top = 82, ready = 'complete'} = {}) {
  const handlers = new Map();
  const frames = new Map();
  const timers = new Map();
  const scrolls = [];
  const article = {contains: element => element === heading};
  const heading = {
    absoluteTop: 400 + top,
    matches: selector => selector === '.section-content > h2[id]',
    getBoundingClientRect: () => ({top: heading.absoluteTop - context.scrollY}),
  };
  const document = {
    readyState: ready,
    fonts: {ready: Promise.resolve()},
    documentElement: {},
    querySelector: selector => selector === `.${page}` ? article
      : selector === '.site-header' ? {getBoundingClientRect: () => ({bottom: 149})} : null,
    getElementById: id => id === hash.slice(1) ? heading : null,
  };
  let nextId = 0;
  const context = {
    document,
    location: {hash},
    innerHeight: 780,
    scrollY: 400,
    AbortController,
    getComputedStyle: () => ({scrollPaddingTop: '160px'}),
    addEventListener(name, callback, options = {}) {
      const callbacks = handlers.get(name) || [];
      callbacks.push({callback, options});
      handlers.set(name, callbacks);
    },
    requestAnimationFrame(callback) { const id = ++nextId; frames.set(id, callback); return id; },
    cancelAnimationFrame(id) { frames.delete(id); },
    setTimeout(callback, delay) {
      assert.ok([240, 1300].includes(delay));
      const id = ++nextId;
      timers.set(id, {callback, delay});
      return id;
    },
    clearTimeout(id) { timers.delete(id); },
    scrollTo({top: requested, behavior}) {
      assert.equal(behavior, 'instant');
      context.scrollY = requested;
      scrolls.push(requested);
    },
  };
  vm.runInNewContext(script, context, {timeout: 1000});
  // Let the script's document.fonts.ready handler schedule its three passes.
  await Promise.resolve();
  return {
    context, heading, scrolls, frames, timers,
    runEarly() { for (const [id, cb] of [...frames]) { frames.delete(id); cb(); } },
    runPostArrival() {
      for (const [id, entry] of [...timers]) {
        if (entry.delay === 240) { timers.delete(id); entry.callback(); }
      }
    },
    runLate() {
      for (const [id, entry] of [...timers]) {
        if (entry.delay === 1300) { timers.delete(id); entry.callback(); }
      }
    },
    dispatch(name) {
      for (const {callback, options} of handlers.get(name) || []) {
        if (!options.signal?.aborted) callback();
      }
    },
    get headingTop() { return heading.absoluteTop - context.scrollY; },
  };
}

test('hidden headings on all three project pages are revealed on the early frame', async () => {
  for (const [page, hash] of [
    ['page-local-ai-review-replies', '#reply-example'],
    ['page-ai-book-continuity-checker', '#continuity-example'],
    ['page-dinner-on-time', '#dinner-demo'],
  ]) {
    const view = await arrival({page, hash});
    assert.equal(view.frames.size, 1);
    assert.equal(view.timers.size, 2);
    view.runEarly();
    assert.equal(view.headingTop, 173, page);
    assert.equal(view.scrolls.length, 1, page);
    view.runPostArrival();
    view.runLate();
    assert.equal(view.scrolls.length, 1, page);
    assert.equal(view.frames.size + view.timers.size, 0);
  }
});

test('a native fragment restoration after the first frame is corrected promptly', async () => {
  const view = await arrival();
  view.runEarly();
  // Simulate the browser restoring its own fragment position after this frame.
  view.context.scrollY += 91;
  assert.equal(view.headingTop, 82);
  view.runPostArrival();
  assert.equal(view.headingTop, 173);
  view.runLate();
  assert.equal(view.scrolls.length, 2);
});

test('late layout shift is corrected without another user-triggered scroll', async () => {
  const view = await arrival();
  view.runEarly();
  view.runPostArrival();
  view.heading.absoluteTop -= 70;
  assert.equal(view.headingTop, 103);
  view.runLate();
  assert.equal(view.headingTop, 173);
  assert.equal(view.scrolls.length, 2);
});

test('a visible heading is not moved by any pass', async () => {
  const view = await arrival({top: 190});
  view.runEarly();
  view.runPostArrival();
  view.runLate();
  assert.deepEqual(view.scrolls, []);
  assert.equal(view.headingTop, 190);
});

test('reader input cancels all corrections before the first frame', async () => {
  for (const event of ['keydown', 'pointerdown', 'wheel', 'touchstart', 'pagehide']) {
    const view = await arrival();
    view.dispatch(event);
    assert.equal(view.frames.size + view.timers.size, 0, event);
    view.runEarly();
    view.runPostArrival();
    view.runLate();
    assert.deepEqual(view.scrolls, [], event);
  }
});

test('reader input after first correction prevents late re-scrolling', async () => {
  const view = await arrival();
  view.runEarly();
  view.heading.absoluteTop -= 70;
  view.dispatch('wheel');
  view.runPostArrival();
  view.runLate();
  assert.equal(view.scrolls.length, 1);
  assert.equal(view.headingTop, 103);
});

test('unknown fragments and pages never schedule a scroll', async () => {
  for (const options of [
    {hash: '#private-information'},
    {hash: '#dinner-demo'},
    {page: 'page-other', hash: '#continuity-example'},
  ]) {
    const view = await arrival(options);
    assert.equal(view.frames.size + view.timers.size, 0);
    assert.deepEqual(view.scrolls, []);
  }
});
