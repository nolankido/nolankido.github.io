/* Local search. Search words never leave this page or enter URLs/storage.
   Only validated topic, source type and free-access filters use URL fragments. */
(() => {
  'use strict';
  const controls = document.getElementById('finder-controls');
  const grid = document.getElementById('finder-results');
  const input = document.getElementById('finder-search');
  const kind = document.getElementById('finder-kind');
  const topic = document.getElementById('finder-topic');
  const free = document.getElementById('finder-free');
  const reset = document.getElementById('finder-reset');
  const more = document.getElementById('finder-more');
  const count = document.getElementById('finder-count');
  const empty = document.getElementById('finder-empty');
  const heading = document.getElementById('finder-results-heading');
  if (![controls, grid, input, kind, topic, free, reset, more, count, empty, heading].every(Boolean)) return;
  const normalize = value => value.normalize('NFKD').toLowerCase().replace(/[\u0300-\u036f]/g, '')
    .replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim()
    .replace(/\bpre flop\b/g, 'preflop').replace(/\bhold em\b/g, 'holdem');
  const stop = new Set('a an the what how do does is are i my in on of for to can and with when why'.split(' '));
  const aliases = {
    mtt: ['mtt', 'tournament'], sng: ['sng', 'sit and go'], plo: ['plo', 'omaha'],
    plo8: ['plo8', 'omaha hi lo', 'omaha high low', 'omaha eight'], o8: ['plo8', 'omaha hi lo', 'omaha high low'],
    holdem: ['holdem', 'hold em'], nlhe: ['nlhe', 'holdem', 'hold em'],
    bb: ['bb', 'big blind'], spr: ['spr', 'stack to pot'], icm: ['icm', 'independent chip', 'tournament equity'],
    gto: ['gto', 'game theory', 'solver'], cbet: ['cbet', 'continuation bet'],
    rta: ['rta', 'real time assistance', 'fair play'], pkos: ['pko', 'bounty'], pko: ['pko', 'bounty'],
    hu: ['hu', 'heads up'], rake: ['rake', 'game costs'], rules: ['rules', 'procedures'],
    beginner: ['beginner', 'start here', 'learn the basics'], videos: ['video', 'watch'], podcasts: ['podcast', 'audio']
  };
  const includes = (text, phrase) => (' ' + text).includes(' ' + phrase);
  const cards = Array.from(grid.querySelectorAll('[data-finder-card]')).map((el, index) => ({
    el, index, topics: new Set((el.dataset.topics || '').split(' ')),
    text: normalize(el.dataset.search || ''), title: normalize(el.querySelector('h3').textContent)
  }));
  if (!cards.length) return;
  let limit = 12;
  let matches = cards;
  let timer;
  let printing = false;
  const words = () => normalize(input.value.slice(0, 160).replace(/c[ -]bet/gi, 'cbet'))
    .split(/\s+/).filter(word => word && !stop.has(word));
  function render() {
    const visible = new Set(matches.slice(0, printing ? matches.length : limit).map(item => item.el));
    for (const card of cards) card.el.hidden = !visible.has(card.el);
    more.hidden = printing || limit >= matches.length;
    more.textContent = 'Show ' + Math.min(12, Math.max(0, matches.length - limit)) + ' more';
    empty.hidden = matches.length !== 0;
    count.textContent = 'Showing ' + visible.size + ' of ' + matches.length + ' matches. ' + cards.length + ' entries in the index.';
  }
  function update(resetPage = true) {
    clearTimeout(timer);
    const query = words();
    const groups = query.map(word => aliases[word] || [word]);
    matches = cards.filter(card => (kind.value === 'all' || card.el.dataset.kind === kind.value)
      && (topic.value === 'all' || card.topics.has(topic.value))
      && (!free.checked || card.el.dataset.free === 'true')
      && groups.every(group => group.some(term => includes(card.text, term))));
    const score = card => groups.reduce((total, group) => total + (group.some(term => includes(card.title, term)) ? 10 : 1), 0)
      + (query.length && card.title === query.join(' ') ? 50 : 0);
    matches.sort((a, b) => score(b) - score(a) || a.index - b.index);
    // Reorder real nodes only; neither queries nor source text are parsed as HTML.
    for (const card of matches) grid.appendChild(card.el);
    if (resetPage) limit = 12;
    render();
  }
  // Read only whitelisted navigation state. Never serialize search input.
  const topicValues = new Set(Array.from(topic.options, option => option.value));
  const kindValues = new Set(Array.from(kind.options, option => option.value));
  function restoreFilters() {
    const params = new URLSearchParams(window.location.hash.slice(1));
    topic.value = topicValues.has(params.get('topic')) ? params.get('topic') : 'all';
    kind.value = kindValues.has(params.get('kind')) ? params.get('kind') : 'all';
    free.checked = params.get('free') === '1';
    input.value = '';
    update();
  }
  function saveFilters() {
    const params = new URLSearchParams();
    if (topic.value !== 'all' && topicValues.has(topic.value)) params.set('topic', topic.value);
    if (kind.value !== 'all' && kindValues.has(kind.value)) params.set('kind', kind.value);
    if (free.checked) params.set('free', '1');
    const fragment = params.toString();
    const nextHash = fragment ? '#' + fragment : '';
    if (window.location.hash === nextHash) return;
    try {
      window.history.pushState(null, '', window.location.pathname + nextHash);
    } catch (_) {
      // Filtering still works in a restricted embedded browser. No fallback request.
    }
  }
  function filtersChanged() { update(); saveFilters(); }
  function clear() {
    input.value = ''; kind.value = 'all'; topic.value = 'all'; free.checked = false;
    update(); saveFilters(); input.focus();
  }
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(update, 120); });
  input.addEventListener('keydown', event => {
    if (event.key === 'Enter') { event.preventDefault(); update(); heading.focus(); }
    if (event.key === 'Escape') { event.preventDefault(); clear(); }
  });
  kind.addEventListener('change', filtersChanged); free.addEventListener('change', filtersChanged);
  topic.addEventListener('change', filtersChanged);
  window.addEventListener('popstate', restoreFilters);
  window.addEventListener('hashchange', restoreFilters);
  reset.addEventListener('click', clear);
  more.addEventListener('click', () => {
    const firstNew = matches[limit]; limit += 12; render();
    if (firstNew) firstNew.el.focus();
  });
  controls.querySelectorAll('[data-finder-example]').forEach(button => button.addEventListener('click', () => {
    input.value = button.dataset.finderExample; kind.value = 'all'; topic.value = 'all'; free.checked = false;
    update(); saveFilters(); heading.focus();
  }));
  window.addEventListener('beforeprint', () => { printing = true; update(false); });
  window.addEventListener('afterprint', () => { printing = false; render(); });
  restoreFilters(); controls.hidden = false;
})();
