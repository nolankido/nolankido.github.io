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

  if (typeof module !== 'undefined' && module.exports) module.exports = {LIMITS, calculate};
  if (typeof document === 'undefined') return;

  const form = document.getElementById('payback-form');
  const fallback = document.getElementById('payback-fallback');
  const result = document.getElementById('payback-result');
  if (!form || !fallback || !result) return;

  const fields = Object.fromEntries(Object.keys(LIMITS).map(key => [key,
    document.getElementById('payback-' + key.replace(/[A-Z]/g, letter => '-' + letter.toLowerCase()))]));
  const ids = ['feedback', 'result-title', 'no-buy', 'pencil-final', 'routine-final',
    'winner', 'breakeven', 'assumptions'];
  const parts = Object.fromEntries(ids.map(id => [id, document.getElementById('payback-' + id)]));
  const presets = [20, 60].map(taps => ({taps, button: document.getElementById('payback-preset-' + taps)}));
  if ([...Object.values(fields), ...Object.values(parts), ...presets.map(preset => preset.button)].some(element => !element)) return;

  const number = value => value.toLocaleString('en-US');

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
    result.hidden = false;
    parts.feedback.textContent = 'Comparison ready. The three possible balances are listed below.';
    parts['result-title'].focus({preventScroll: true});
    result.scrollIntoView({block: 'start', behavior: 'instant'});
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    clearErrors();
    result.hidden = true;
    const values = parse();
    if (!values) return;
    render(values, calculate(values));
  });
  form.addEventListener('reset', function () {
    clearErrors();
    result.hidden = true;
    parts.feedback.textContent = 'Example restored. Compare again to see its three balances.';
  });
  for (const preset of presets) {
    preset.button.addEventListener('click', function () {
      const values = {bank: 25, taps: preset.taps, seconds: 60, pencilCost: 10, routineCost: 25};
      for (const [key, value] of Object.entries(values)) fields[key].value = String(value);
      clearErrors();
      result.hidden = true;
      render(values, calculate(values));
    });
  }

  form.hidden = false;
  fallback.hidden = true;
}());
