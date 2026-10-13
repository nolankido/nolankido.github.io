/* Independent fake DOM failure injection. No browser or public requests. */
const fs = require('fs');
const vm = require('vm');
const path = require('path');

function exercise(phase) {
  const nodes = new Map(), created = [], revoked = [], timers = [], attached = [], downloads = [];
  function element(id) {
    if (!nodes.has(id)) nodes.set(id, {
      hidden: id === 'time-result', value: '', textContent: '', handlers: {},
      addEventListener(name, handler) { this.handlers[name] = handler; },
      setAttribute() {}, removeAttribute() {},
      focus() { this.focused = true; },
      select() { this.selectionStart = 0; this.selectionEnd = this.value.length; }
    });
    return nodes.get(id);
  }
  const document = {
    getElementById: element,
    body: {appendChild(link) {
      if (phase === 'append') throw Error('Synthetic append failure');
      attached.push(link);
    }},
    createElement(tag) {
      if (tag !== 'a') throw Error('Unexpected element');
      if (phase === 'element') throw Error('Synthetic element failure');
      return {
        click() {
          if (phase === 'click') throw Error('Synthetic activation failure');
          if (phase === 'stale') {
            element('time-review').value = '10';
            element('time-review').handlers.input();
          }
          downloads.push({filename: this.download, href: this.href, hidden: this.hidden});
        },
        remove() { const index = attached.indexOf(this); if (index >= 0) attached.splice(index, 1); }
      };
    }
  };
  const context = {
    window: {addEventListener() {}}, document, navigator: {},
    Blob: class {constructor(parts) {
      if (phase === 'blob') throw Error('Synthetic Blob failure');
      this.text = parts.join('');
    }},
    URL: {
      createObjectURL(blob) {
        if (phase === 'create') throw Error('Synthetic object URL failure');
        const url = 'blob:synthetic-' + created.length;
        created.push({url, text: blob.text}); return url;
      },
      revokeObjectURL(url) { revoked.push(url); }
    },
    setTimeout(fn, delay) { timers.push({fn, delay}); }
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../assets/workflow-time.js'), 'utf8'), context);
  const values = {manual:'30', assisted:'8', review:'7', count:'6', setup:'60', upkeep:'15'};
  for (const [key, value] of Object.entries(values)) element('time-' + key).value = value;
  element('time-quality').value = 'unknown'; element('time-basis').value = 'estimate';
  element('time-calculate').handlers.click();
  const original = element('time-report').value;
  if (phase === 'hidden') element('time-result').hidden = true;
  if (phase === 'empty') element('time-report').value = '';
  let uncaught = null;
  try { element('time-download').handlers.click(); } catch (error) { uncaught = error.message; }
  for (const timer of timers) timer.fn();
  const report = element('time-report');
  return {
    phase, uncaught, original, value: report.value,
    focused: Boolean(report.focused), selectionStart: report.selectionStart ?? null,
    selectionEnd: report.selectionEnd ?? null, hidden: element('time-result').hidden,
    feedback: element('time-copy-status').textContent,
    created, revoked, timerDelays: timers.map(t => t.delay), attached: attached.length, downloads,
    inputs: Object.fromEntries(Object.keys(values).map(key => [key, element('time-' + key).value]))
  };
}

process.stdout.write(JSON.stringify(['ok','blob','create','element','append','click','stale','hidden','empty'].map(exercise)));
