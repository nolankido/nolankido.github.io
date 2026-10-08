/* Local progressive search. No network, query URLs, analytics events or storage. */
(() => {
  'use strict';
  const controls = document.getElementById('finder-controls');
  const grid = document.getElementById('finder-results');
  const input = document.getElementById('finder-search');
  const kind = document.getElementById('finder-kind');
  const free = document.getElementById('finder-free');
  const reset = document.getElementById('finder-reset');
  const more = document.getElementById('finder-more');
  const count = document.getElementById('finder-count');
  const empty = document.getElementById('finder-empty');
  const heading = document.getElementById('finder-results-heading');
  if (![controls, grid, input, kind, free, reset, more, count, empty, heading].every(Boolean)) return;
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
    el, index, text: normalize(el.dataset.search || ''), body: normalize(Array.from(el.querySelectorAll('[data-finder-passage]')).map(p => p.dataset.heading + ' ' + p.textContent).join(' ')), title: normalize(el.querySelector('h3').textContent),
    passages: Array.from(el.querySelectorAll('[data-finder-passage]')),
    url: el.querySelector('h3 a').getAttribute('href')
  }));
  if (!cards.length) return;
  const shelf = document.getElementById('finder-shelf');
  const shelfList = document.getElementById('finder-shelf-list');
  const shelfCount = document.getElementById('finder-shelf-count');
  const shelfDownload = document.getElementById('finder-shelf-download');
  const chosen = new Set();
  let exportURL;
  function renderShelf() {
    if (!shelf || !shelfList || !shelfCount || !shelfDownload) return;
    shelfList.replaceChildren();
    const lines = ['# My poker study list', '', 'Public links selected on Nolan Kido Poker. This is a snapshot, not a new source review.', ''];
    for (const card of cards) {
      const button = card.el.querySelector('.finder-save');
      if (button) { button.setAttribute('aria-pressed', String(chosen.has(card.el.dataset.id))); button.textContent = chosen.has(card.el.dataset.id) ? 'Remove from study list' : 'Add to study list'; }
      if (!chosen.has(card.el.dataset.id)) continue;
      const sourceLink = card.el.querySelector('h3 a');
      const li = document.createElement('li'), link = document.createElement('a');
      link.textContent = sourceLink.textContent; link.setAttribute('href', card.url); li.appendChild(link); shelfList.appendChild(li);
      const url = card.url.startsWith('/') ? 'https://nolankido.com' + card.url : card.url;
      lines.push('## ' + sourceLink.textContent, '', url, '');
      for (const para of Array.from(card.el.children).filter(el => el.tagName === 'P' && !el.classList.contains('finder-excerpt') && !el.classList.contains('finder-jump'))) lines.push(para.textContent, '');
    }
    shelfCount.textContent = chosen.size + ' of 12 places used. This list clears when the page reloads; download it to keep it.';
    if (exportURL) URL.revokeObjectURL(exportURL);
    shelfDownload.hidden = !chosen.size;
    if (chosen.size) {
      exportURL = URL.createObjectURL(new Blob([lines.join('\n')], {type: 'text/markdown;charset=utf-8'}));
      shelfDownload.href = exportURL;
    } else shelfDownload.removeAttribute('href');
  }
  if (shelf && shelfList && shelfCount && shelfDownload) {
    shelf.hidden = false;
    cards.forEach(card => {
      const button = card.el.querySelector('.finder-save');
      if (!button) return;
      button.hidden = false;
      button.addEventListener('click', () => {
        const id = card.el.dataset.id;
        if (chosen.has(id)) chosen.delete(id);
        else if (chosen.size < 12) chosen.add(id);
        else {shelfCount.textContent = 'The list has 12 items. Remove one before adding another.'; return;}
        renderShelf();
      });
    });
    document.getElementById('finder-shelf-clear').addEventListener('click', () => {chosen.clear(); renderShelf();});
    renderShelf();
  }
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
      && (!free.checked || card.el.dataset.free === 'true')
      && groups.every(group => group.some(term => includes(card.text + ' ' + card.body, term))));
    const score = card => groups.reduce((total, group) => total + (group.some(term => includes(card.title, term)) ? 20 : group.some(term => includes(card.text, term)) ? 5 : 1), 0)
      + (query.length && card.title === query.join(' ') ? 50 : 0);
    matches.sort((a, b) => score(b) - score(a) || a.index - b.index);
    for (const card of cards) {
      const excerpt = card.el.querySelector('.finder-excerpt');
      const jump = card.el.querySelector('.finder-jump');
      if (!excerpt || !jump) continue;
      const selected = card.passages.map(p => ({p, score: groups.reduce((n, g) => n + (g.some(t => includes(normalize(p.textContent + ' ' + p.dataset.heading), t)) ? 1 : 0), 0)}))
        .sort((a, b) => b.score - a.score)[0];
      const found = groups.length && selected && selected.score > 0;
      excerpt.hidden = !found; jump.hidden = !found;
      if (found) {
        const text = selected.p.textContent.replace(/\s+/g, ' ').trim();
        const hit = text.split(/(?<=[.!?])\s+/)
          .map(sentence => ({sentence, score: groups.reduce((n, group) => n + (group.some(term => includes(normalize(sentence), term)) ? 1 : 0), 0)}))
          .sort((a, b) => b.score - a.score)[0].sentence || text;
        excerpt.textContent = 'In this guide: ' + hit.slice(0, 320) + (hit.length > 320 ? '…' : '');
        const link = jump.querySelector('a');
        link.setAttribute('href', card.url + (selected.p.dataset.anchor ? '#' + selected.p.dataset.anchor : ''));
        link.textContent = 'Read: ' + selected.p.dataset.heading;
      }
    }
    // Reorder real nodes only; neither queries nor source text are parsed as HTML.
    for (const card of matches) grid.appendChild(card.el);
    if (resetPage) limit = 12;
    render();
  }
  function clear() {
    input.value = ''; kind.value = 'all'; free.checked = false;
    update(); input.focus();
  }
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(update, 120); });
  input.addEventListener('keydown', event => {
    if (event.key === 'Enter') { event.preventDefault(); update(); heading.focus(); }
    if (event.key === 'Escape') { event.preventDefault(); clear(); }
  });
  kind.addEventListener('change', update); free.addEventListener('change', update);
  reset.addEventListener('click', clear);
  more.addEventListener('click', () => {
    const firstNew = matches[limit]; limit += 12; render();
    if (firstNew) firstNew.el.focus();
  });
  controls.querySelectorAll('[data-finder-example]').forEach(button => button.addEventListener('click', () => {
    input.value = button.dataset.finderExample; kind.value = 'all'; free.checked = false;
    update(); heading.focus();
  }));
  window.addEventListener('beforeprint', () => { printing = true; update(false); });
  window.addEventListener('afterprint', () => { printing = false; render(); });
  update(); controls.hidden = false; grid.classList.add('finder-enhanced');
})();
