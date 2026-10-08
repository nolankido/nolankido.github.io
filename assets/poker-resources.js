/* Local progressive enhancement. No network, saved searches, URL writes or custom tracking. */
(() => {
  'use strict';
  const root = document.getElementById('poker-resources');
  if (!root) return;
  const get = id => document.getElementById(id);
  const controls = get('resource-controls');
  const input = get('resource-search');
  const reset = get('resource-reset');
  const free = get('resource-free');
  const format = get('resource-format');
  const level = get('resource-level');
  const compact = get('resource-compact');
  const print = get('resource-print');
  const active = get('resource-active');
  const count = get('resource-count');
  const empty = get('resource-empty');
  const buttons = [...root.querySelectorAll('[data-resource-filter]')];
  const groups = [...root.querySelectorAll('[data-resource-section]')];
  const cards = [...root.querySelectorAll('[data-resource-card]')];
  if (![controls, input, reset, free, format, level, compact, print, active, count, empty].every(Boolean) || !cards.length) return;
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  // Index the visible listing once instead of sending a second copy in HTML attributes.
  const records = cards.map(node => ({node, category: node.dataset.category, access: node.dataset.access,
    format: node.dataset.format, level: node.dataset.level,
    search: normalize(`${[...node.children].map(child => child.textContent).join(' ')} ${node.dataset.access} ${node.dataset.category}`)}));
  const labels = new Map(buttons.map(button => [button.dataset.resourceFilter, button.textContent.replace(/\s+\(\d+\)$/, '')]));
  let category = 'all';
  let freeOnly = false;
  let timer;
  const update = () => {
    const words = normalize(input.value).split(/\s+/).filter(Boolean);
    const available = new Map();
    let shown = 0;
    for (const record of records) {
      const eligible = (!freeOnly || record.access === 'Free') && (format.value === 'all' || record.format === format.value) &&
        (level.value === 'all' || record.level === level.value || record.level === 'All levels') && words.every(word => record.search.includes(word));
      if (eligible) available.set(record.category, (available.get(record.category) || 0) + 1);
      const match = eligible && (category === 'all' || record.category === category);
      record.node.hidden = !match;
      if (match) shown += 1;
    }
    groups.forEach(group => { group.hidden = ![...group.querySelectorAll('[data-resource-card]')].some(card => !card.hidden); });
    buttons.forEach(button => {
      const key = button.dataset.resourceFilter;
      const n = key === 'all' ? [...available.values()].reduce((a, b) => a + b, 0) : (available.get(key) || 0);
      button.setAttribute('aria-pressed', String(key === category));
      button.textContent = `${labels.get(key)} (${n})`;
    });
    free.setAttribute('aria-pressed', String(freeOnly));
    count.textContent = `${shown} of ${records.length} resources shown.`;
    active.textContent = `${labels.get(category)}. ${format.options[format.selectedIndex].text}. ${level.value === 'all' ? 'Any experience' : level.value + ' + All levels'}. ${freeOnly ? 'Free only' : 'Free, mixed and paid'}.${words.length ? ' Search: ' + input.value.trim() : ''}`;
    empty.hidden = shown !== 0;
  };
  const clear = () => {
    clearTimeout(timer); category = 'all'; freeOnly = false; input.value = ''; format.value = 'all'; level.value = 'all'; update();
  };
  const targetForHash = hash => {
    let ident;
    try { ident = decodeURIComponent(hash.slice(1)); } catch (_) { return null; }
    const node = get(ident);
    return node && root.contains(node) && (node.hasAttribute('data-resource-card') || node.hasAttribute('data-resource-section') || ident === 'directory-top') ? node : null;
  };
  const reveal = (hash, focus = false) => {
    const node = targetForHash(hash);
    if (!node) return;
    clear();
    if (focus) {
      if (!node.hasAttribute('tabindex')) node.setAttribute('tabindex', '-1');
      node.focus({preventScroll: true});
      node.scrollIntoView({block: 'start', behavior: 'auto'});
    }
  };
  const jumpToResults = () => {
    const target = groups.find(group => !group.hidden)?.querySelector('h2') || count;
    target.setAttribute('tabindex', '-1');
    target.focus({preventScroll: true});
    target.scrollIntoView({block: 'start', behavior: 'auto'});
  };
  input.addEventListener('keydown', event => {
    if (event.key === 'Enter') { event.preventDefault(); clearTimeout(timer); update(); jumpToResults(); }
  });
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(update, 100); });
  input.addEventListener('search', () => { clearTimeout(timer); update(); });
  [format, level].forEach(select => select.addEventListener('change', () => { clearTimeout(timer); update(); }));
  buttons.forEach(button => button.addEventListener('click', () => { clearTimeout(timer); category = button.dataset.resourceFilter; update(); }));
  free.addEventListener('click', () => { clearTimeout(timer); freeOnly = !freeOnly; update(); });
  reset.addEventListener('click', () => { clear(); input.focus(); });
  compact.addEventListener('click', () => {
    const enabled = compact.getAttribute('aria-pressed') !== 'true';
    compact.setAttribute('aria-pressed', String(enabled));
    root.classList.toggle('resource-compact', enabled);
  });
  print.addEventListener('click', () => window.print());
  const goals = {
    beginner: {category: 'basics', level: 'Beginner', free: true},
    tournament: {category: 'tournament-study'}, watch: {category: 'watch-listen'},
    tools: {category: 'tools'}, events: {category: 'events'}, variants: {category: 'variants'}
  };
  root.querySelectorAll('[data-resource-goal]').forEach(button => button.addEventListener('click', () => {
    const goal = goals[button.dataset.resourceGoal];
    if (!goal) return;
    clear(); category = goal.category; level.value = goal.level || 'all'; freeOnly = Boolean(goal.free); update(); jumpToResults();
  }));
  root.querySelectorAll('[data-resource-jump]').forEach(link => link.addEventListener('click', () => {
    const hash = link.getAttribute('href');
    if (!targetForHash(hash)) return;
    clear();
    // Keep native anchors and browser history, including activation of the current hash.
    requestAnimationFrame(() => reveal(hash, true));
  }));
  window.addEventListener('hashchange', () => reveal(window.location.hash, true));
  window.addEventListener('pageshow', () => {
    clearTimeout(timer); update();
    if (targetForHash(window.location.hash)) reveal(window.location.hash);
  });
  window.addEventListener('beforeprint', () => {
    clearTimeout(timer);
    groups.forEach(group => { group.hidden = false; });
    cards.forEach(card => { card.hidden = false; });
    count.textContent = `${records.length} resources available.`;
    empty.hidden = true;
  });
  window.addEventListener('afterprint', update);
  update();
  controls.hidden = false;
  print.hidden = false;
  if (targetForHash(window.location.hash)) requestAnimationFrame(() => reveal(window.location.hash, true));
})();
