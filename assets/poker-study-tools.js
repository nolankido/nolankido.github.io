/* Study-only arithmetic. No network, storage, hand histories or action recommendations. */
(() => {
  'use strict';
  function amount(raw) {
    const text = String(raw).trim();
    if (!/^\d{1,9}(?:\.\d{1,2})?$/.test(text)) throw new Error('Use a non-negative number with at most two decimal places, without commas.');
    const value = Number(text);
    if (!Number.isFinite(value)) throw new Error('Enter a finite amount.');
    return value;
  }
  function calculate(mode, first, second, committed = '0') {
    const a = amount(first), b = amount(second), w = amount(committed);
    if (a <= 0 || b <= 0) throw new Error('The pot and call or risk must both be greater than zero.');
    if (mode === 'call') return {percent: 100 * b / (a + b), finalPot: a + b};
    if (mode === 'bluff') return {percent: 100 * b / (a + b), reward: a, risk: b};
    if (mode === 'potlimit') {
      if (w > a) throw new Error('Your existing contribution cannot exceed the current pot.');
      return {afterCall: a + b, extra: a + 2 * b, total: w + a + 2 * b};
    }
    throw new Error('Unknown calculation.');
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {amount, calculate};
  if (typeof document === 'undefined') return;
  const panels = Array.from(document.querySelectorAll('[data-study-tool]'));
  const format = n => n.toLocaleString('en-US', {maximumFractionDigits: 2});
  for (const panel of panels) {
    const controls = panel.querySelector('[data-tool-controls]');
    const output = panel.querySelector('[data-tool-output]');
    const fields = Array.from(panel.querySelectorAll('input'));
    const run = panel.querySelector('[data-tool-run]');
    const clear = panel.querySelector('[data-tool-clear]');
    if (!controls || !output || fields.length < 2 || !run || !clear) continue;
    function update() {
      fields.forEach(field => field.removeAttribute('aria-invalid'));
      try {
        const result = calculate(panel.dataset.studyTool, ...fields.map(f => f.value));
        const mode = panel.dataset.studyTool;
        output.textContent = mode === 'call'
          ? 'Final pot after calling: ' + format(result.finalPot) + '. Break-even pot-share equity: ' + result.percent.toFixed(2) + '%. Calculation: call / (current pot + call). This is not an estimated win probability.'
          : mode === 'bluff'
            ? 'Break-even fold rate: ' + result.percent.toFixed(2) + '%. Calculation: risk / (pot before betting + risk). Assumes zero equity when called and no further betting.'
            : 'Pot after the call: ' + format(result.afterCall) + '. Maximum new chips to put in: ' + format(result.extra) + '. Total wager for this street, including existing chips: ' + format(result.total) + '. Stack limits and whether raising is reopened are not checked.';
      } catch (error) {
        for (const field of fields) {
          try { amount(field.value); } catch (_) { field.setAttribute('aria-invalid', 'true'); }
        }
        output.textContent = 'Check the inputs: ' + error.message;
      }
    }
    run.addEventListener('click', update);
    fields.forEach(field => field.addEventListener('keydown', event => {
      if (event.key === 'Enter') { event.preventDefault(); update(); }
    }));
    clear.addEventListener('click', () => {
      fields.forEach(field => {field.value = field.defaultValue; field.removeAttribute('aria-invalid');});
      output.textContent = 'Example values restored. Choose Calculate to check them.';
      fields[0].focus();
    });
    controls.hidden = false;
  }
})();
