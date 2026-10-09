/* Progressive enhancement only. No requests, storage, URL changes or analytics calls. */
(() => {
  'use strict';
  const root = document.getElementById('poker-library');
  if (!root) return;
  const controls = document.getElementById('library-controls');
  const input = document.getElementById('library-search');
  const reset = document.getElementById('library-reset');
  const status = document.getElementById('library-count');
  const empty = document.getElementById('library-empty');
  const buttons = [...root.querySelectorAll('button[data-filter]')];
  const cards = [...root.querySelectorAll('[data-library-card]')];
  if (!controls || !input || !reset || !status || !empty || !buttons.length || !cards.length) return;
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const records = cards.map(node => ({node, topics: new Set((node.dataset.topics || node.dataset.topic).split(" ")), search: normalize(node.dataset.search || '')}));
  let selected = 'all';
  let timer;
  const update = () => {
    const words = normalize(input.value).split(/\s+/).filter(Boolean);
    let found = 0;
    for (const record of records) {
      const show = (selected === 'all' || record.topics.has(selected)) && words.every(word => record.search.includes(word));
      record.node.hidden = !show;
      if (show) found += 1;
    }
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === selected)));
    status.textContent = `${found} of ${records.length} guides shown.`;
    empty.hidden = found !== 0;
  };
  input.addEventListener('keydown', event => {
    if (event.key === 'Enter') { event.preventDefault(); clearTimeout(timer); update(); status.focus(); }
    if (event.key === 'Escape') { event.preventDefault(); reset.click(); }
  });
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(update, 100); });
  input.addEventListener('search', () => { clearTimeout(timer); update(); });
  buttons.forEach(button => button.addEventListener('click', () => { clearTimeout(timer); selected = button.dataset.filter; update(); }));
  reset.addEventListener('click', () => { clearTimeout(timer); input.value = ''; selected = 'all'; update(); input.focus(); });
  window.addEventListener('pageshow', () => { clearTimeout(timer); update(); });
  update();
  const options = document.getElementById('library-options');
  if (options) options.open = window.innerWidth > 760;
  controls.hidden = false;
})();
