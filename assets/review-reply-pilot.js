/* Six-case paired pilot: local inputs only, no model, storage or network calls. */
(() => {
  'use strict';
  const IDS = Object.freeze(['RP01', 'RP02', 'RP03', 'RP04', 'RP05', 'RP06']);
  const FIELDS = Object.freeze(['manual_minutes', 'ai_preparation_minutes', 'ai_review_minutes', 'ai_repair_minutes']);
  const HEADER = Object.freeze(['case_id', ...FIELDS, 'quality_status']);
  function checkMinutes(raw, manual = false) {
    const value = typeof raw === 'string' ? raw.trim() : '';
    if (value === '') return {valid: true, missing: true, hundredths: null};
    if (!/^[0-9]+(?:\.[0-9]{1,2})?$/.test(value)) return {valid: false, missing: false, hundredths: null};
    const n = Number(value);
    if (!Number.isFinite(n) || n > 100000 || (manual && n === 0)) {
      return {valid: false, missing: false, hundredths: null};
    }
    return {valid: true, missing: false, hundredths: Math.round(n * 100)};
  }
  function quality(row) {
    const started = FIELDS.some(key => !!row[key]) || !!row.manual_quality || !!row.ai_quality || !!row.confirmed;
    if (!started) return '';
    if (!row.confirmed || !['accepted','rejected'].includes(row.manual_quality) ||
        !['accepted','rejected'].includes(row.ai_quality)) return 'unreviewed';
    return row.manual_quality === 'accepted' && row.ai_quality === 'accepted' ? 'accepted' : 'rejected';
  }
  function csv(rows) {
    const body = IDS.map(id => {
      const row = rows[id] || {};
      return [id, ...FIELDS.map(key => row[key] || ''), quality(row)].join(',');
    });
    return HEADER.join(',') + '\n' + body.join('\n') + '\n';
  }
  function summarize(rows, setupRaw, upkeepRaw) {
    let count = 0, manual = 0, assisted = 0, accepted = 0, rejected = 0;
    for (const id of IDS) {
      const row = rows[id] || {};
      const values = FIELDS.map((key,i) => checkMinutes(row[key], i === 0));
      const status = quality(row);
      if (!values.every(v => v.valid && !v.missing) || !['accepted','rejected'].includes(status)) continue;
      count++;
      accepted += Number(status === 'accepted');
      rejected += Number(status === 'rejected');
      manual += values[0].hundredths;
      assisted += values.slice(1).reduce((s,v) => s + v.hundredths, 0);
    }
    const setup = checkMinutes(setupRaw), upkeep = checkMinutes(upkeepRaw);
    if (count !== 6 || !setup.valid || setup.missing || !upkeep.valid || upkeep.missing) {
      return {ready: false, complete: count, accepted, rejected};
    }
    assisted += setup.hundredths + upkeep.hundredths;
    return {ready: true, complete: count, accepted, rejected, manual, assisted,
      difference: manual - assisted, qualityGateMet: rejected === 0};
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {IDS, FIELDS, HEADER, checkMinutes, quality, csv, summarize};
  }
  if (typeof document === 'undefined') return;
  const form = document.getElementById('rr-pilot-form');
  if (!form) return;
  const cases = Array.from(form.querySelectorAll('[data-rr-case]'));
  if (cases.length !== IDS.length || cases.some((node,i) => node.dataset.rrCase !== IDS[i])) return;
  const getField = (node,key) => node.querySelector('[data-rr-field="' + key + '"]');
  const overheadSetup = document.getElementById('rr-pilot-setup');
  const overheadUpkeep = document.getElementById('rr-pilot-upkeep');
  const status = document.getElementById('rr-pilot-status');
  const summary = document.getElementById('rr-pilot-summary');
  const command = document.getElementById('rr-pilot-command');
  const actions = document.getElementById('rr-pilot-actions');
  const exportButton = document.getElementById('rr-pilot-export');
  const resetButton = document.getElementById('rr-pilot-reset');
  if ([overheadSetup,overheadUpkeep,status,summary,command,actions,exportButton,resetButton].some(x => !x)) return;
  const relevant = [...FIELDS, 'manual_quality', 'ai_quality', 'confirmed'];
  if (cases.some(node => relevant.some(key => !getField(node,key)))) return;
  const read = () => Object.fromEntries(cases.map(node => [
    node.dataset.rrCase,
    Object.fromEntries(relevant.map(key => {
      const input = getField(node,key);
      return [key, input.type === 'checkbox' ? input.checked : input.value.trim()];
    }))
  ]));
  const fmt = value => (Math.abs(value) / 100).toFixed(2);
  function refresh() {
    const result = summarize(read(), overheadSetup.value, overheadUpkeep.value);
    if (!result.ready) {
      summary.textContent = result.complete + ' of 6 matched cases have all four time fields and human approval labels. ' +
        'No time comparison is available until all six and setup/upkeep are complete. Missing is not zero.';
    } else {
      const direction = result.difference >= 0 ? 'fewer' : 'more';
      summary.textContent = 'User-entered six-case totals: manual ' + fmt(result.manual) +
        ' minutes; assisted including setup and upkeep ' + fmt(result.assisted) + ' minutes. ' +
        fmt(result.difference) + ' minutes ' + direction + ' with AI. ' +
        result.accepted + ' accepted pairs and ' + result.rejected + ' rejected. ' +
        (result.qualityGateMet
          ? 'All paired results were marked acceptable by a human. This is a small descriptive sample with fictional inputs, not verified business savings.'
          : 'At least one pair failed quality. Do not claim a productivity improvement.');
    }
    const setup = checkMinutes(overheadSetup.value), upkeep = checkMinutes(overheadUpkeep.value);
    command.textContent = setup.valid && !setup.missing && upkeep.valid && !upkeep.missing
      ? 'py -3 ai-workflow-pilot-audit.py --input review-reply-paired-observations.csv --setup-minutes ' +
        overheadSetup.value.trim() + ' --upkeep-minutes ' + overheadUpkeep.value.trim()
      : 'Enter observed setup and upkeep minutes to prepare the offline audit command. These values are not included in the CSV.';
  }
  function invalidInput() {
    for (const node of cases) {
      for (const [i,key] of FIELDS.entries()) {
        const input = getField(node,key);
        if (!checkMinutes(input.value, i === 0).valid) {
          node.open = true; input.setAttribute('aria-invalid','true'); input.focus();
          return node.dataset.rrCase + ': enter a nonnegative number to two decimal places; manual time must be greater than zero. Leave unknown time blank.';
        }
        input.removeAttribute('aria-invalid');
      }
    }
    for (const input of [overheadSetup,overheadUpkeep]) {
      if (!checkMinutes(input.value).valid) {
        input.setAttribute('aria-invalid','true'); input.focus();
        return 'Invalid setup or upkeep time. Enter a nonnegative number to two decimals, or leave it blank.';
      }
      input.removeAttribute('aria-invalid');
    }
    return '';
  }
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('input', refresh);
  form.addEventListener('change', refresh);
  exportButton.addEventListener('click', () => {
    const error = invalidInput();
    if (error) { status.textContent = error; return; }
    const anchor = document.createElement('a');
    let url = '';
    try {
      url = URL.createObjectURL(new Blob([csv(read())], {type:'text/csv;charset=utf-8'}));
      anchor.href = url; anchor.download = 'review-reply-paired-observations.csv';
      anchor.hidden = true; form.appendChild(anchor); anchor.click();
      status.textContent = 'CSV download requested. Verify it saved. Incomplete entries remain blank or unreviewed; the offline auditor will reject them.';
    } catch (_) {
      status.textContent = 'CSV download unavailable. No file was saved. Use the static blank CSV instead.';
    } finally {
      anchor.remove();
      if (url) window.setTimeout(() => URL.revokeObjectURL(url), 2000);
    }
  });
  function clearEntries() {
    for (const node of cases) {
      for (const key of relevant) {
        const input = getField(node,key);
        if (input.type === 'checkbox') input.checked = false;
        else input.value = '';
        input.removeAttribute('aria-invalid');
      }
    }
    overheadSetup.value = ''; overheadUpkeep.value = '';
    overheadSetup.removeAttribute('aria-invalid'); overheadUpkeep.removeAttribute('aria-invalid');
    refresh();
  }
  resetButton.addEventListener('click', () => {
    if (!window.confirm('Clear all six cases and overhead minutes? Download your CSV first if you need these observations.')) return;
    clearEntries();
    status.textContent = 'All entries cleared. No observations have been saved or transmitted.';
  });
  // Browsers can restore form fields across reloads or back/forward cache.
  // Clear on page exit and arrival without writing to persistent storage.
  window.addEventListener('pagehide', clearEntries);
  window.addEventListener('pageshow', () => {
    clearEntries();
    status.textContent = 'No observations entered. This page does not retain trial values across visits.';
  });
  actions.hidden = false;
  clearEntries();
  status.textContent = 'No observations entered. No data is stored or transmitted. Export before leaving the page.';
})();
