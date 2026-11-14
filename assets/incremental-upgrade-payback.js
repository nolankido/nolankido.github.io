/* Transparent first-purchase comparison for a browser-local teaching guide.
   No model, storage, tracking, network request, or changing game state. */
(function () {
  'use strict';

  const LIMITS = Object.freeze({
    bank: [0, 1000000], taps: [0, 1000], seconds: [0, 600],
    pencilCost: [1, 1000000], routineCost: [1, 1000000]
  });
  const LABELS = Object.freeze({
    bank: 'starting sparks', taps: 'planned taps', seconds: 'visible seconds',
    pencilCost: 'pencil cost', routineCost: 'routine cost'
  });

  function calculate(values) {
    for (const [key, range] of Object.entries(LIMITS)) {
      const value = values[key];
      if (!Number.isSafeInteger(value) || value < range[0] || value > range[1]) {
        throw new RangeError('Invalid ' + LABELS[key] + ': use a whole number from ' + range[0] + ' to ' + range[1] + '.');
      }
    }

    const {bank, taps, seconds, pencilCost, routineCost} = values;
    const noBuy = bank + taps;
    const pencil = bank >= pencilCost ? bank - pencilCost + 2 * taps : null;
    const routine = bank >= routineCost ? bank - routineCost + taps + seconds : null;
    const available = [
      {name: 'Buy nothing', value: noBuy},
      ...(pencil === null ? [] : [{name: 'Buy sharper pencil', value: pencil}]),
      ...(routine === null ? [] : [{name: 'Buy daily routine', value: routine}])
    ];
    const highest = Math.max(...available.map(option => option.value));
    const leaders = available.filter(option => option.value === highest).map(option => option.name);

    return {
      noBuy, pencil, routine, leaders, highest,
      pencilPaybackTaps: pencilCost,
      routinePaybackSeconds: routineCost,
      routineMinusPencil: pencil === null || routine === null ? null : routine - pencil,
      routineThresholdSeconds: taps + routineCost - pencilCost
    };
  }

  function formatScenario(values, comparison) {
    const {bank, taps, seconds, pencilCost, routineCost} = values;
    const balance = value => value === null ? 'Unavailable: not affordable at start' : value + ' sparks';
    const bothAffordable = comparison.routineMinusPencil !== null;
    const comparisonNote = bothAffordable
      ? 'Routine minus pencil: ' + comparison.routineMinusPencil + ' sparks. ' +
        (comparison.routineMinusPencil === 0 ? 'The upgrades tie.' :
          comparison.routineMinusPencil > 0 ? 'Routine finishes ahead of pencil.' : 'Pencil finishes ahead of routine.')
      : 'Routine versus pencil: not comparable because at least one purchase is unaffordable at the start.';
    const thresholdNote = bothAffordable
      ? 'Their algebraic tie occurs at T = N + R - C = ' + comparison.routineThresholdSeconds + ' seconds. ' +
        (comparison.routineThresholdSeconds < 0
          ? 'A nonnegative duration cannot reach that tie; routine is ahead for every feasible duration.'
          : 'Routine finishes ahead when T exceeds that value; pencil finishes ahead when T is below it.')
      : 'Pencil versus routine tie threshold: not applicable to these unaffordable purchase paths.';

    return [
      '# Incremental upgrade payback: hypothetical comparison',
      '',
      'Guide and model: https://nolankido.com/creative/incremental-upgrade-payback/',
      '',
      'This is a synthetic calculation, not an observation of a player or a recommendation to change a game.',
      '',
      '## Inputs',
      '',
      '- Starting available sparks (B): ' + bank,
      '- Planned taps after purchase (N): ' + taps,
      '- Visible, unpaused seconds (T): ' + seconds,
      '- Sharper pencil cost (C): ' + pencilCost,
      '- Daily routine cost (R): ' + routineCost,
      '',
      '## Final balances after the same planned actions',
      '',
      '| Path | Formula | Calculated final balance |',
      '| --- | --- | --- |',
      '| Buy nothing | B + N | ' + balance(comparison.noBuy) + ' |',
      '| Buy one sharper pencil | B - C + 2 x N | ' + balance(comparison.pencil) + ' |',
      '| Buy one daily routine | B - R + N + T | ' + balance(comparison.routine) + ' |',
      '',
      '- Highest available final balance: ' + comparison.highest + ' sparks.',
      '- Highest-balance path(s): ' + comparison.leaders.join(' and ') + '.',
      '- ' + comparisonNote,
      '- ' + thresholdNote,
      '- Conditional pencil payback against buying nothing: ' + comparison.pencilPaybackTaps + ' extra taps, if affordable and purchased now.',
      '- Conditional routine payback against buying nothing: ' + comparison.routinePaybackSeconds + ' active seconds, if affordable and purchased now.',
      '',
      '## Scope and questions',
      '',
      '- Each path starts with the same B and uses the same N and T. At most one purchase is made immediately, if affordable.',
      '- The pencil adds 1 extra spark per tap. The routine adds 1 spark per active second.',
      '- No later purchases, price increases, compounding, background progress, offline earnings, or changing tap rates are modeled.',
      '- Payback excludes time spent earning the starting purchase price. A larger balance does not measure fun, retention, or player preference.',
      '- What behavior or design assumption should be tested before changing a rule?',
      '',
      'Generated locally in your browser. The website does not receive or store these inputs.'
    ].join('\n') + '\n';
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = {LIMITS, calculate, formatScenario};
  if (typeof document === 'undefined') return;

  const form = document.getElementById('payback-form');
  const fallback = document.getElementById('payback-fallback');
  const result = document.getElementById('payback-result');
  if (!form || !fallback || !result) return;

  const fields = Object.fromEntries(Object.keys(LIMITS).map(key => [key,
    document.getElementById('payback-' + key.replace(/[A-Z]/g, letter => '-' + letter.toLowerCase()))]));
  const ids = ['feedback', 'result-title', 'no-buy', 'pencil-final', 'routine-final',
    'winner', 'breakeven', 'assumptions', 'report'];
  const parts = Object.fromEntries(ids.map(id => [id, document.getElementById('payback-' + id)]));
  const downloadLink = document.getElementById('payback-download');
  const presets = [20, 60].map(taps => ({taps, button: document.getElementById('payback-preset-' + taps)}));
  if ([...Object.values(fields), ...Object.values(parts), downloadLink,
    ...presets.map(preset => preset.button)].some(element => !element)) return;

  const number = value => value.toLocaleString('en-US');
  let downloadUrl = null;

  function clearResult() {
    result.hidden = true;
    parts.report.value = '';
    downloadLink.hidden = true;
    downloadLink.removeAttribute('href');
    if (downloadUrl !== null) {
      URL.revokeObjectURL(downloadUrl);
      downloadUrl = null;
    }
  }

  function clearErrors() {
    for (const input of Object.values(fields)) input.removeAttribute('aria-invalid');
  }

  function parse() {
    const values = {};
    for (const [key, bounds] of Object.entries(LIMITS)) {
      const input = fields[key];
      const raw = input.value.trim();
      const parsed = Number(raw);
      if (!/^\d+$/.test(raw) || !Number.isSafeInteger(parsed) || parsed < bounds[0] || parsed > bounds[1]) {
        input.setAttribute('aria-invalid', 'true');
        parts.feedback.textContent = 'Check ' + LABELS[key] + ': enter a whole number from ' + number(bounds[0]) + ' to ' + number(bounds[1]) + '.';
        input.focus();
        return null;
      }
      values[key] = parsed;
    }
    return values;
  }

  function render(values, comparison) {
    parts['no-buy'].textContent = number(comparison.noBuy);
    parts['pencil-final'].textContent = comparison.pencil === null ? 'Not affordable at start' : number(comparison.pencil);
    parts['routine-final'].textContent = comparison.routine === null ? 'Not affordable at start' : number(comparison.routine);
    const names = comparison.leaders.join(' and ');
    parts.winner.textContent = 'Highest calculated final balance: ' + names + ' (' + number(comparison.highest) + ' sparks).' +
      (comparison.leaders.length > 1 ? ' These paths tie.' : ' This is a balance comparison, not a player-preference verdict.');
    let difference;
    if (comparison.routineMinusPencil === null) {
      difference = 'Direct pencil-versus-routine comparison is unavailable because at least one upgrade cannot be purchased from this starting balance.';
    } else if (comparison.routineMinusPencil === 0) {
      difference = 'The two upgrade paths tie for this plan.';
    } else {
      difference = (comparison.routineMinusPencil > 0 ? 'Routine ends ' : 'Pencil ends ') +
        number(Math.abs(comparison.routineMinusPencil)) + ' sparks ahead of the other purchase.';
    }
    const threshold = comparison.routineMinusPencil === null ? '' : comparison.routineThresholdSeconds < 0
      ? ' At these prices and planned taps, routine finishes ahead at every nonnegative duration.'
      : ' Routine overtakes pencil when visible seconds exceed ' + number(comparison.routineThresholdSeconds) +
        ' for the same planned taps and these prices.';
    parts.breakeven.textContent = 'Conditional payback against buying nothing, if purchased now: ' + number(comparison.pencilPaybackTaps) +
      ' additional taps for the pencil; ' + number(comparison.routinePaybackSeconds) +
      ' active seconds for the routine. ' + difference + threshold;
    parts.assumptions.textContent = 'Starting balance ' + number(values.bank) + '; ' + number(values.taps) +
      ' taps; ' + number(values.seconds) + ' visible seconds; pencil cost ' + number(values.pencilCost) +
      '; routine cost ' + number(values.routineCost) + '. Only one purchase happens at the start, with no other upgrades.';
    parts.report.value = formatScenario(values, comparison);
    if (typeof Blob === 'function' && typeof URL !== 'undefined' && typeof URL.createObjectURL === 'function') {
      try {
        downloadUrl = URL.createObjectURL(new Blob([parts.report.value], {type: 'text/markdown;charset=utf-8'}));
        downloadLink.href = downloadUrl;
        downloadLink.hidden = false;
      } catch (_error) {
        downloadLink.hidden = true;
      }
    }
    result.hidden = false;
    parts.feedback.textContent = 'Comparison ready. The three possible balances are listed below.';
    parts['result-title'].focus({preventScroll: true});
    result.scrollIntoView({block: 'start', behavior: 'instant'});
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    clearErrors();
    clearResult();
    const values = parse();
    if (!values) return;
    render(values, calculate(values));
  });
  form.addEventListener('input', function () {
    if (!result.hidden) {
      clearResult();
      parts.feedback.textContent = 'Inputs changed. Compare again to update the result and its downloadable record.';
    }
  });
  form.addEventListener('reset', function () {
    clearErrors();
    clearResult();
    parts.feedback.textContent = 'Example restored. Compare again to see its three balances.';
  });
  for (const preset of presets) {
    preset.button.addEventListener('click', function () {
      const values = {bank: 25, taps: preset.taps, seconds: 60, pencilCost: 10, routineCost: 25};
      for (const [key, value] of Object.entries(values)) fields[key].value = String(value);
      clearErrors();
      clearResult();
      render(values, calculate(values));
    });
  }

  form.hidden = false;
  fallback.hidden = true;
}());
