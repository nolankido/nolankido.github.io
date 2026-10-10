/* Optional in-page filtering. No network, storage, account, or URL writes. */
(() => {
  'use strict';
  const controls = document.getElementById('lw-filters');
  const query = document.getElementById('lw-query');
  const collection = document.getElementById('lw-collection');
  const access = document.getElementById('lw-access');
  const clear = document.getElementById('lw-clear');
  const count = document.getElementById('lw-result-count');
  const empty = document.getElementById('lw-empty');
  const root = document.getElementById('lw-results');
  if (!controls || !query || !collection || !access || !clear || !count || !empty || !root) return;
  const normalize = value => String(value).normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/\s+/g, ' ').trim();
  const entries = Array.from(root.querySelectorAll('[data-lw-entry]')).map(node => ({
    node, collection: node.dataset.collection, access: node.dataset.access,
    text: normalize(node.textContent + ' ' + node.dataset.terms)
  }));
  if (!entries.length) return;
  const apply = () => {
    const words = normalize(query.value.slice(0, 120)).split(' ').filter(Boolean);
    let visible = 0;
    for (const entry of entries) {
      const match = (!collection.value || collection.value === entry.collection) &&
        (!access.value || access.value === entry.access) && words.every(word => entry.text.includes(word));
      entry.node.hidden = !match;
      if (match) visible += 1;
    }
    count.textContent = `Showing ${visible} of ${entries.length} resources.`;
    empty.hidden = visible !== 0;
  };
  query.addEventListener('input', apply);
  collection.addEventListener('change', apply);
  access.addEventListener('change', apply);
  clear.addEventListener('click', () => {
    query.value = ''; collection.value = ''; access.value = ''; apply(); query.focus();
  });
  // Initialize before showing controls; content remains readable if initialization fails.
  apply();
  controls.hidden = false;
})();
