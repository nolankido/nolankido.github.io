/* Local search. Search words never leave this page or enter URLs/storage.
   Only validated topic, source type and free-access filters use URL fragments. */
(() => {
  'use strict';
  const normalize = value => value.normalize('NFKD').toLowerCase().replace(/[\u0300-\u036f]/g, '')
    .replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim()
    .replace(/\bpre flop\b/g, 'preflop').replace(/\bhold em\b/g, 'holdem')
    .replace(/\breentry\b/g, 're entry').replace(/\b2 ?pairs?\b/g, 'two pair').replace(/\btwo pairs\b/g, 'two pair');
  const stop = new Set('a an the what how do does did is are be that i my in on of for to can and with when why who which after from mean means much more'.split(' '));
  const aliases = {
    mtt: ['mtt', 'tournament'], sng: ['sng', 'sit and go'], plo: ['plo', 'omaha'],
    plo8: ['plo8', 'omaha hi lo', 'omaha high low', 'omaha eight'], o8: ['plo8', 'omaha hi lo', 'omaha high low'],
    holdem: ['holdem', 'hold em'], nlhe: ['nlhe', 'holdem', 'hold em'],
    bb: ['bb', 'big blind'], spr: ['spr', 'stack to pot'], icm: ['icm', 'independent chip', 'tournament equity'],
    gto: ['gto', 'game theory', 'solver'], cbet: ['cbet', 'continuation bet'],
    rta: ['rta', 'real time assistance', 'fair play'], pkos: ['pko', 'bounty'], pko: ['pko', 'bounty'],
    hu: ['hu', 'heads up'], rake: ['rake', 'game costs'], rules: ['rules', 'procedures'],
    beginner: ['beginner', 'start here', 'learn the basics'], videos: ['video', 'watch'], podcasts: ['podcast', 'audio'],
    calling: ['call', 'calling'], calculate: ['calculate', 'calculation', 'calculator', 'price'],
    count: ['count', 'calculate', 'calculation'], acts: ['acts', 'act', 'action'],
    bet: ['bet', 'bets', 'betting'], pot: ['pot', 'pots'], outs: ['out', 'outs']
  };
  // Short abbreviations are whole words: BB must not match the unrelated BBA.
  const includes = (text, phrase) => (' ' + text + ' ').includes(' ' + phrase + (phrase.length <= 3 || phrase === 'free' ? ' ' : ''));
  const spellings = {tournment: 'tournament', tournamnet: 'tournament', kikcer: 'kicker', kicer: 'kicker'};
  const phrases = ['two pair', 'full house', 'big blind', 'small blind', 'pot odds', 'best five', 're entry'];
  function plan(value) {
    const text = normalize(value.slice(0, 160).replace(/c[ -]bet/gi, 'cbet'));
    const tokens = text.split(/\s+/).filter(Boolean).map(word => Object.prototype.hasOwnProperty.call(spellings, word) ? spellings[word] : word);
    if (tokens.includes('pot')) for (let i = 0; i < tokens.length; i += 1) if (tokens[i] === 'ods') tokens[i] = 'odds';
    const content = tokens.filter(word => !stop.has(word));
    const query = content.some(word => word !== 'poker') ? content.filter(word => word !== 'poker') : content;
    const comparison = query.some(word => ['pair', 'straight', 'flush', 'kicker'].includes(word)) || (query.includes('full') && query.includes('house'));
    const groups = [];
    for (let i = 0; i < query.length; i += 1) {
      const pair = query[i] + ' ' + query[i + 1];
      if (phrases.includes(pair)) { groups.push([pair]); i += 1; }
      else if (comparison && ['lose', 'lost', 'wins', 'win', 'beat', 'beats'].includes(query[i])) groups.push(['lose', 'lost', 'win', 'wins', 'beat', 'compare', 'comparison', 'rank', 'kicker']);
      else groups.push(Object.prototype.hasOwnProperty.call(aliases, query[i]) ? aliases[query[i]] : [query[i]]);
    }
    let hints = [];
    if (comparison || includes(text, 'best five')) hints = ['hand rankings', 'which hand wins', 'best five'];
    else if (includes(query.join(' '), 'pot odds') || query.includes('outs') || (query.includes('break') && query.includes('even'))) hints = ['pot odds', 'math'];
    else if (query.includes('call') || query.includes('calling')) hints = ['first poker decisions', 'bets calls', 'math'];
    else if (query.includes('acts') || query.includes('position')) hints = ['position', 'first poker decisions', 'starting hand'];
    else if (query.includes('icm')) hints = ['tournament chips', 'tournament equity', 'prize equity'];
    else if (query.includes('gto')) hints = ['study tool'];
    return {query, groups, hints, active: Boolean(value.trim())};
  }
  function prepare(card) {
    // Public search titles supplement the visible heading; they do not replace it.
    return {...card, title: normalize(card.title), searchTitle: normalize(card.searchTitle || ''),
      text: normalize(card.text + ' ' + (card.searchTitle || '')), body: normalize(card.body),
      passages: card.passages.map(p => ({...p, headingWords: normalize(p.heading), words: normalize(p.text + ' ' + p.heading)}))};
  }
  function passage(card, search) {
    if (!search.groups.length) return null;
    return card.passages.map((p, index) => {
      const hits = search.groups.filter(g => g.some(t => includes(p.words, t))).length;
      return {p, index, value: hits * 4 + search.groups.filter(g => g.some(t => includes(p.headingWords, t))).length, hits};
    }).filter(row => row.hits > 0).sort((a, b) => b.value - a.value || a.index - b.index)[0]?.p || null;
  }
  function score(card, search) {
    if (search.active && !search.groups.length) return -1;
    if (!search.groups.every(g => g.some(t => includes(card.text + ' ' + card.body, t)))) return -1;
    const focused = passage(card, search);
    const sectionScore = focused ? search.groups.filter(g => g.some(t => includes(focused.headingWords, t))).length * 8
      + (search.groups.every(g => g.some(t => includes(focused.words, t))) ? 12 : 0) : 0;
    return search.groups.reduce((n, g) => n + (g.some(t => includes(card.title, t)) ? 20 : g.some(t => includes(card.searchTitle, t)) ? 8 : g.some(t => includes(card.text, t)) ? 5 : 1), 0)
      + (search.query.length && card.title === search.query.join(' ') ? 50
        : search.query.length > 1 && (' ' + card.searchTitle + ' ').includes(' ' + search.query.join(' ') + ' ') ? 25 : 0)
      + (search.hints.some(t => includes(card.title, t)) ? 40 : search.hints.some(t => includes(card.searchTitle, t)) ? 16 : 0)
      + (card.kind === 'glossary' && search.groups.some(g => g.some(t => includes(card.title, t))) ? 12 : 0) + sectionScore;
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {normalize, prepare, plan, score, passage};
  if (typeof document === 'undefined') return;
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
  const cards = Array.from(grid.querySelectorAll('[data-finder-card]')).map((el, index) => ({
    el, index, kind: el.dataset.kind, topics: new Set((el.dataset.topics || '').split(' ')), text: el.dataset.search || '', body: Array.from(el.querySelectorAll('[data-finder-passage]')).map(p => p.dataset.heading + ' ' + p.textContent).join(' '), title: el.querySelector('h3').textContent, searchTitle: el.dataset.searchTitle || '',
    passages: Array.from(el.querySelectorAll('[data-finder-passage]')).map(p => ({heading: p.dataset.heading, anchor: p.dataset.anchor, text: p.textContent})),
    url: el.querySelector('h3 a').getAttribute('href')
  })).map(prepare);
  if (!cards.length) return;
  const shelf = document.getElementById('finder-shelf');
  const shelfList = document.getElementById('finder-shelf-list');
  const shelfCount = document.getElementById('finder-shelf-count');
  const shelfDownload = document.getElementById('finder-shelf-download');
  const shelfCopy = document.getElementById('finder-shelf-copy');
  const shelfStatus = document.getElementById('finder-shelf-status');
  const shelfPreview = document.getElementById('finder-shelf-preview');
  const shelfText = document.getElementById('finder-shelf-text');
  const chosen = new Set();
  let exportURL;
  let exportText = '';
  let shelfRevision = 0;
  let copyAttempt = 0;
  function releaseExport() {
    shelfDownload.hidden = true;
    shelfDownload.removeAttribute('href');
    const previous = exportURL;
    exportURL = undefined;
    if (previous) {
      try { URL.revokeObjectURL(previous); } catch (_) { /* The old link is already removed. */ }
    }
  }
  function revealShelfText(select = false) {
    shelfPreview.open = true;
    if (select) { shelfText.focus(); shelfText.select(); }
  }
  function renderShelf(focusIndex) {
    if (![shelf, shelfList, shelfCount, shelfDownload, shelfCopy, shelfStatus, shelfPreview, shelfText].every(Boolean)) return;
    shelfRevision += 1;
    copyAttempt += 1;
    releaseExport();
    shelfStatus.textContent = '';
    shelf.hidden = chosen.size === 0;
    shelfList.replaceChildren();
    const lines = ['# My poker study list', '', 'Public links selected on Nolan Kido Poker. This is a snapshot, not a new source review.', ''];
    for (const card of cards) {
      const button = card.el.querySelector('.finder-save');
      if (button) { button.setAttribute('aria-pressed', String(chosen.has(card.el.dataset.id))); button.textContent = chosen.has(card.el.dataset.id) ? 'Remove from study list' : 'Add to study list'; }
      if (!chosen.has(card.el.dataset.id)) continue;
      const sourceLink = card.el.querySelector('h3 a');
      const li = document.createElement('li'), link = document.createElement('a');
      link.textContent = sourceLink.textContent; link.setAttribute('href', card.url); li.appendChild(link);
      const remove = document.createElement('button'), index = shelfList.children.length;
      remove.type = 'button'; remove.className = 'finder-shelf-remove'; remove.textContent = 'Remove';
      remove.dataset.finderRemove = card.el.dataset.id;
      remove.setAttribute('aria-label', 'Remove ' + sourceLink.textContent + ' from study list');
      remove.addEventListener('click', () => { chosen.delete(card.el.dataset.id); renderShelf(index); });
      li.appendChild(remove); shelfList.appendChild(li);
      const url = card.url.startsWith('/') ? 'https://nolankido.com' + card.url : card.url;
      lines.push('## ' + sourceLink.textContent, '', url, '');
      for (const para of Array.from(card.el.children).filter(el => el.tagName === 'P' && !el.classList.contains('finder-excerpt') && !el.classList.contains('finder-jump'))) {
        const details = para.cloneNode(true);
        for (const link of details.querySelectorAll('a[href]')) {
          const href = link.getAttribute('href');
          const address = href.startsWith('/') ? 'https://nolankido.com' + href : href;
          link.textContent = '[' + link.textContent + '](' + address + ')';
        }
        lines.push(details.textContent, '');
      }
    }
    exportText = chosen.size ? lines.join('\n') : '';
    shelfText.value = exportText;
    shelfCount.textContent = chosen.size + ' of 12 places used. This list clears when the page reloads; download or copy it to keep it.';
    if (chosen.size) {
      try {
        exportURL = URL.createObjectURL(new Blob([exportText], {type: 'text/markdown;charset=utf-8'}));
        shelfDownload.href = exportURL;
        shelfDownload.hidden = false;
      } catch (_) {
        releaseExport();
        shelfStatus.textContent = 'The download is unavailable here. Copy the list or use the complete text below.';
        revealShelfText();
      }
    } else shelfPreview.open = false;
    if (Number.isInteger(focusIndex)) {
      const buttons = shelfList.querySelectorAll('.finder-shelf-remove');
      if (buttons.length) buttons[Math.min(focusIndex, buttons.length - 1)].focus();
      else input.focus();
    }
  }
  if ([shelf, shelfList, shelfCount, shelfDownload, shelfCopy, shelfStatus, shelfPreview, shelfText].every(Boolean)) {
    shelf.hidden = true;
    cards.forEach(card => {
      const button = card.el.querySelector('.finder-save');
      if (!button) return;
      button.hidden = false;
      button.addEventListener('click', () => {
        const id = card.el.dataset.id;
        if (chosen.has(id)) chosen.delete(id);
        else if (chosen.size < 12) chosen.add(id);
        else {
          copyAttempt += 1;
          shelfCount.textContent = '12 of 12 places used. Remove an item below before adding another.';
          shelfStatus.textContent = '';
          shelfList.querySelector('.finder-shelf-remove').focus();
          return;
        }
        renderShelf();
      });
    });
    shelfCopy.addEventListener('click', async () => {
      if (!chosen.size) return;
      const revision = shelfRevision, attempt = ++copyAttempt, text = exportText;
      const current = () => revision === shelfRevision && attempt === copyAttempt && chosen.size > 0;
      shelfStatus.textContent = '';
      try {
        if (typeof navigator === 'undefined' || !navigator.clipboard || typeof navigator.clipboard.writeText !== 'function') throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(text);
        if (current()) shelfStatus.textContent = 'Study list copied. Paste it into your own notes.';
      } catch (_) {
        if (!current()) return;
        shelfStatus.textContent = 'Copying is unavailable here. Use your device’s Copy command on the complete list below.';
        revealShelfText(document.activeElement === shelfCopy);
      }
    });
    shelfDownload.addEventListener('click', event => {
      copyAttempt += 1;
      if (!chosen.size || !exportURL) {
        event.preventDefault();
        if (chosen.size) {
          shelfStatus.textContent = 'The download is unavailable here. Use the complete text below.';
          revealShelfText(document.activeElement === shelfDownload);
        }
        return;
      }
      shelfStatus.textContent = 'Download requested. If no file appears, copy the list or use the complete text below.';
    });
    document.getElementById('finder-shelf-clear').addEventListener('click', () => {chosen.clear(); renderShelf(); input.focus();});
    window.addEventListener('pagehide', event => { if (!event.persisted) releaseExport(); });
    renderShelf();
  }
  let limit = 12;
  let matches = cards;
  let timer;
  let printing = false;
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
    const search = plan(input.value), groups = search.groups;
    matches = cards.filter(card => (kind.value === 'all' || card.el.dataset.kind === kind.value)
      && (topic.value === 'all' || card.topics.has(topic.value))
      && (!free.checked || card.el.dataset.free === 'true')
      ).map(card => ({card, value: score(card, search)})).filter(row => row.value >= 0)
      .sort((a, b) => b.value - a.value || a.card.index - b.card.index).map(row => row.card);
    for (const card of cards) {
      const excerpt = card.el.querySelector('.finder-excerpt');
      const jump = card.el.querySelector('.finder-jump');
      if (!excerpt || !jump) continue;
      const selected = passage(card, search);
      const found = groups.length && selected;
      excerpt.hidden = !found;
      // A matching passage without an anchor has no honest section jump.
      jump.hidden = !found || !selected.anchor;
      if (found) {
        const text = selected.text.replace(/\s+/g, ' ').trim();
        const hit = text.split(/(?<=[.!?])\s+/)
          .map(sentence => ({sentence, score: groups.reduce((n, group) => n + (group.some(term => includes(normalize(sentence), term)) ? 1 : 0), 0)}))
          .sort((a, b) => b.score - a.score)[0].sentence || text;
        excerpt.textContent = 'In this guide: ' + hit.slice(0, 320) + (hit.length > 320 ? '…' : '');
        const link = jump.querySelector('a');
        if (selected.anchor) {
          link.setAttribute('href', card.url + '#' + selected.anchor);
          link.textContent = 'Read: ' + selected.heading;
        } else {
          link.removeAttribute('href');
          link.textContent = '';
        }
      }
    }
    // Reorder real nodes only; neither queries nor source text are parsed as HTML.
    for (const card of matches) grid.appendChild(card.el);
    if (resetPage) limit = 12;
    render();
  }
  // Read only whitelisted navigation state. Never serialize search input.
  const topicValues = new Set(Array.from(topic.options, option => option.value));
  const kindValues = new Set(Array.from(kind.options, option => option.value));
  const filterPanel = document.getElementById('finder-options');
  function restoreFilters() {
    const params = new URLSearchParams(window.location.hash.slice(1));
    topic.value = topicValues.has(params.get('topic')) ? params.get('topic') : 'all';
    kind.value = kindValues.has(params.get('kind')) ? params.get('kind') : 'all';
    free.checked = params.get('free') === '1';
    if (filterPanel) filterPanel.open = window.innerWidth > 760 || topic.value !== 'all' || kind.value !== 'all' || free.checked;
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
  function submit() {
    clearTimeout(timer); update(); heading.focus({preventScroll: true});
    heading.scrollIntoView({block: 'center', behavior: 'instant'});
  }
  input.addEventListener('input', event => { clearTimeout(timer); if (!event.isComposing) timer = setTimeout(update, 120); });
  input.addEventListener('compositionstart', () => clearTimeout(timer));
  input.addEventListener('compositionend', update);
  input.addEventListener('search', () => { clearTimeout(timer); update(); });
  input.addEventListener('keydown', event => {
    if (event.isComposing || event.keyCode === 229) return;
    if (event.key === 'Enter') { event.preventDefault(); submit(); }
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
  restoreFilters(); controls.hidden = false; grid.classList.add('finder-enhanced');
})();
