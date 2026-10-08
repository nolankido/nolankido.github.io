/* Local progressive enhancement. No network, saved searches, URL writes or custom tracking. */
(() => {
  'use strict';
  const root = document.getElementById('poker-resources');
  if (!root) return;
  const controls = document.getElementById('resource-controls');
  const input = document.getElementById('resource-search');
  const reset = document.getElementById('resource-reset');
  const free = document.getElementById('resource-free');
  const count = document.getElementById('resource-count');
  const empty = document.getElementById('resource-empty');
  const buttons = [...root.querySelectorAll('[data-resource-filter]')];
  const groups = [...root.querySelectorAll('[data-resource-section]')];
  const cards = [...root.querySelectorAll('[data-resource-card]')];
  if (!controls || !input || !reset || !free || !count || !empty || !cards.length) return;
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const records = cards.map(node => ({node, category: node.dataset.category, access: node.dataset.access,
    search: normalize(`${node.dataset.search} ${node.dataset.access} ${node.dataset.category}`)}));
  let category = 'all';
  let freeOnly = false;
  let timer;
  const update = () => {
    const words = normalize(input.value).split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const record of records) {
      const match = (category === 'all' || record.category === category) && (!freeOnly || record.access === 'Free') && words.every(word => record.search.includes(word));
      record.node.hidden = !match;
      if (match) shown += 1;
    }
    groups.forEach(group => { group.hidden = ![...group.querySelectorAll('[data-resource-card]')].some(card => !card.hidden); });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.resourceFilter === category)));
    free.setAttribute('aria-pressed', String(freeOnly));
    count.textContent = `${shown} of ${records.length} resources shown.`;
    empty.hidden = shown !== 0;
  };
  const clear = () => { clearTimeout(timer); category = 'all'; freeOnly = false; input.value = ''; update(); };
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(update, 100); });
  input.addEventListener('search', () => { clearTimeout(timer); update(); });
  buttons.forEach(button => button.addEventListener('click', () => { clearTimeout(timer); category = button.dataset.resourceFilter; update(); }));
  free.addEventListener('click', () => { clearTimeout(timer); freeOnly = !freeOnly; update(); });
  reset.addEventListener('click', () => { clear(); input.focus(); });
  root.querySelectorAll('[data-resource-jump]').forEach(link => link.addEventListener('click', clear));
  window.addEventListener('pageshow', () => { clearTimeout(timer); update(); });
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
})();
