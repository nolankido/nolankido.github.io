/* Original browser-local incremental game design example for nolankido.com.
   No storage, account, network request, tracking, or offline catch-up. */
(function () {
  'use strict';

  const GOAL = 150;
  const MAX_UPGRADES = 15;

  function initialState() {
    return { bank: 0, total: 0, pencil: 0, routine: 0, paused: false };
  }

  function upgradeCost(kind, owned) {
    if (!Number.isInteger(owned) || owned < 0 || owned >= MAX_UPGRADES) return null;
    if (kind === 'pencil') return Math.ceil(10 * Math.pow(1.7, owned));
    if (kind === 'routine') return 25 * Math.pow(2, owned);
    return null;
  }

  function produce(state, amount) {
    if (!Number.isSafeInteger(amount) || amount < 0) return state;
    return { ...state, bank: state.bank + amount, total: state.total + amount };
  }

  function tap(state) {
    return produce(state, 1 + state.pencil);
  }

  function tick(state, visible) {
    return state.paused || !visible ? state : produce(state, state.routine);
  }

  function buy(state, kind) {
    const price = upgradeCost(kind, state[kind]);
    if (price === null || state.bank < price) return state;
    return { ...state, bank: state.bank - price, [kind]: state[kind] + 1 };
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GOAL, MAX_UPGRADES, initialState, upgradeCost, produce, tap, tick, buy };
  }
  if (typeof document === 'undefined') return;

  const panel = document.getElementById('game-lab');
  const fallback = document.getElementById('lab-fallback');
  if (!panel || !fallback) return;

  const ids = ['bank', 'total', 'per-tap', 'per-second', 'progress', 'progress-copy',
    'tap', 'pencil', 'routine', 'pencil-count', 'routine-count', 'pause', 'reset', 'action-status'];
  const parts = Object.fromEntries(ids.map(function (id) {
    return [id, document.getElementById('lab-' + id)];
  }));
  if (Object.values(parts).some(function (element) { return !element; })) return;

  let state = initialState();
  const number = function (value) { return value.toLocaleString('en-US'); };

  function render() {
    parts.bank.textContent = number(state.bank);
    parts.total.textContent = number(state.total);
    parts['per-tap'].textContent = number(1 + state.pencil);
    parts['per-second'].textContent = number(state.routine);
    parts.progress.value = Math.min(GOAL, state.total);
    parts['progress-copy'].textContent = number(state.total) + ' total sparks produced. Goal: ' + GOAL + '.';
    parts.tap.textContent = 'Make sparks (+' + number(1 + state.pencil) + ')';
    for (const kind of ['pencil', 'routine']) {
      const cost = upgradeCost(kind, state[kind]);
      const label = kind === 'pencil' ? 'sharper pencil' : 'daily routine';
      parts[kind].textContent = cost === null ? 'Maximum ' + label + ' purchases reached' :
        'Buy ' + label + ' (' + number(cost) + ' sparks)';
      parts[kind].disabled = cost === null || state.bank < cost;
      parts[kind + '-count'].textContent = 'Purchased: ' + state[kind] + ' of ' + MAX_UPGRADES;
    }
    parts.pause.textContent = state.paused ? 'Resume passive production' : 'Pause passive production';
    parts.pause.setAttribute('aria-pressed', state.paused ? 'true' : 'false');
  }

  function announce(message, before) {
    if (before < GOAL && state.total >= GOAL) {
      parts['action-status'].textContent = 'Goal reached: ' + number(state.total) + ' sparks produced. You can keep playing or start over.';
    } else if (message) {
      parts['action-status'].textContent = message;
    }
  }

  parts.tap.addEventListener('click', function () {
    const before = state.total;
    state = tap(state);
    render();
    announce('', before);
  });
  for (const kind of ['pencil', 'routine']) {
    parts[kind].addEventListener('click', function () {
      const before = state;
      const cost = upgradeCost(kind, state[kind]);
      state = buy(state, kind);
      if (state !== before) {
        render();
        announce((kind === 'pencil' ? 'Sharper pencil' : 'Daily routine') +
          ' purchased for ' + number(cost) + ' sparks. The total produced did not decrease.', before.total);
      }
    });
  }
  parts.pause.addEventListener('click', function () {
    state = { ...state, paused: !state.paused };
    render();
    announce(state.paused ? 'Passive production paused. Taps still work.' : 'Passive production resumed.', state.total);
  });
  parts.reset.addEventListener('click', function () {
    state = initialState();
    render();
    announce('Started over at zero. No run was saved.', state.total);
    parts.tap.focus();
  });

  render();
  fallback.hidden = true;
  panel.hidden = false;
  window.setInterval(function () {
    if (document.hidden || state.paused || state.routine === 0) return;
    const before = state.total;
    state = tick(state, true);
    render();
    announce('', before);
  }, 1000);
}());
