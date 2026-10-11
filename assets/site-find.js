/* Local filtering of the already-rendered public index. No query transport. */
(() => {
  'use strict';
  const stops = new Set(['a', 'an', 'the', 'and', 'of', 'to', 'for', 'in', 'on', 'with', 'how', 'do', 'i', 'my', 'is', 'can', 'what']);
  const normalize = value => String(value).normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
  const words = value => normalize(value).split(/\s+/).filter(Boolean);
  const stem = value => value.length > 5 && value.endsWith('ies') ? value.slice(0, -3) + 'y' : value.length > 4 && value.endsWith('s') && !value.endsWith('ss') ? value.slice(0, -1) : value;
  const terms = value => [...new Set(words(String(value).slice(0, 180)).filter(t => !stops.has(t)).map(stem))];
  const matches = (word, term) => word === term || (term.length >= 3 && word.startsWith(term));
  function score(record, query) {
    const needles = terms(query);
    if (!normalize(query)) return String(query).trim() ? -1 : 0;
    if (!needles.length) return -1;
    const title = words(record.title).map(stem);
    const all = [...title, ...words(record.description + ' ' + record.subjects).map(stem)];
    if (!needles.every(term => all.some(word => matches(word, term)))) return -1;
    return needles.filter(term => title.some(word => matches(word, term))).length * 10 + (normalize(record.title).includes(normalize(query)) ? 25 : 0);
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = { normalize, terms, score };
  if (typeof document === 'undefined') return;
  const controls = document.getElementById('find-controls');
  if (!controls) return;
  const query = document.getElementById('find-query');
  const interest = document.getElementById('find-interest');
  const kind = document.getElementById('find-kind');
  const status = document.getElementById('find-status');
  const heading = document.getElementById('find-results');
  const empty = document.getElementById('find-empty');
  const groups = [...document.querySelectorAll('.find-group')].map(group => ({
    node: group, list: group.querySelector('.find-items'), count: group.querySelector('.find-group-count'),
    items: [...group.querySelectorAll('.find-item')].map((node, order) => ({
      node, order, title: node.querySelector('h3').textContent,
      description: node.querySelector('.find-description').textContent,
      subjects: node.querySelector('.find-subjects').textContent,
      interests: node.dataset.interests.split(' '), kind: node.dataset.kind
    }))
  }));
  const total = groups.reduce((n, group) => n + group.items.length, 0);
  let timer;
  function filter() {
    clearTimeout(timer);
    const value = query.value.slice(0, 180);
    const active = Boolean(value.trim() || interest.value || kind.value);
    let count = 0;
    for (const group of groups) {
      let visible = 0;
      const ranked = group.items.map(item => ({ item, value: score(item, value) }));
      ranked.sort((a, b) => b.value - a.value || a.item.order - b.item.order);
      for (const rankedItem of ranked) {
        const item = rankedItem.item;
        const show = rankedItem.value >= 0 && (!interest.value || item.interests.includes(interest.value)) && (!kind.value || item.kind === kind.value);
        item.node.hidden = !show;
        if (show) visible += 1;
        group.list.append(item.node);
      }
      group.node.hidden = visible === 0;
      group.node.open = active && visible > 0;
      group.count.textContent = '(' + visible + ')';
      group.count.hidden = !active;
      count += visible;
    }
    empty.hidden = count > 0;
    heading.textContent = active ? 'Search results.' : 'Browse the collections.';
    status.textContent = active ? count + (count === 1 ? ' matching page' : ' matching pages') + ' of ' + total + '. Grouped by collection, with closer title matches first.' : 'Browse ' + total + ' published pages, or narrow the index above.';
  }
  function reset(focus) {
    query.value = ''; interest.value = ''; kind.value = ''; filter();
    if (focus) query.focus();
  }
  query.addEventListener('input', event => { if (!event.isComposing) { clearTimeout(timer); timer = setTimeout(filter, 140); } });
  query.addEventListener('compositionend', filter);
  query.addEventListener('search', filter);
  query.addEventListener('keydown', event => { if (event.key === 'Enter') { event.preventDefault(); filter(); } });
  interest.addEventListener('change', filter);
  kind.addEventListener('change', filter);
  document.getElementById('find-submit').addEventListener('click', filter);
  document.getElementById('find-reset').addEventListener('click', () => reset(true));
  // Do not restore a previous visitor query when returning through browser history.
  window.addEventListener('pagehide', () => reset(false));
  window.addEventListener('pageshow', event => { if (event.persisted) reset(false); });
  reset(false);
  controls.hidden = false;
})();
