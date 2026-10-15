/* Local filtering of the already-rendered public index. No query transport. */
(() => {
  'use strict';
  const stops = new Set(['a', 'an', 'the', 'and', 'of', 'to', 'for', 'in', 'on', 'with', 'how', 'do', 'i', 'my', 'is', 'can', 'what']);
  const normalize = value => String(value).normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
  const words = value => normalize(value).split(/\s+/).filter(Boolean);
  const stem = value => value.length > 5 && value.endsWith('ies') ? value.slice(0, -3) + 'y' : value.length > 4 && value.endsWith('s') && !value.endsWith('ss') ? value.slice(0, -1) : value;
  const terms = value => [...new Set(words(String(value).slice(0, 180)).filter(t => !stops.has(t)).map(stem))];
  const matches = (word, term) => word === term || (term.length >= 3 && word.startsWith(term));
  // Use only the canonical local destination already present in each result.
  // No decoding, query string, fragment, external address or guessed synonym.
  const addressWords = record => typeof record.path === 'string' && /^\/(?:[a-z0-9-]+\/)+$/.test(record.path) ? words(record.path).map(stem) : [];
  // Reuse the exact public browser/search title, without inventing keywords.
  const searchTitleWords = record => typeof record.searchTitle === 'string' ? words(record.searchTitle).map(stem) : [];
  function matchingSections(record, query) {
    const needles = terms(query);
    if (!needles.length) return [];
    const base = [...words(record.title + ' ' + record.description + ' ' + record.subjects).map(stem), ...searchTitleWords(record), ...addressWords(record)];
    return (record.sections || []).map((section, order) => {
      const heading = words(section[1]).map(stem);
      const hits = needles.filter(term => heading.some(word => matches(word, term))).length;
      const found = hits > 0 && needles.every(term => [...base, ...heading].some(word => matches(word, term)));
      return {section, order, hits, found};
    }).filter(row => row.found).sort((a, b) => b.hits - a.hits || a.order - b.order).slice(0, 3).map(row => row.section);
  }
  function score(record, query) {
    const needles = terms(query);
    if (!normalize(query)) return String(query).trim() ? -1 : 0;
    if (!needles.length) return -1;
    const title = words(record.title).map(stem);
    const all = [...title, ...words(record.description + ' ' + record.subjects).map(stem)];
    const baseMatch = needles.every(term => all.some(word => matches(word, term)));
    const addressMatch = needles.every(term => [...all, ...addressWords(record)].some(word => matches(word, term)));
    const searchTitleMatch = !addressMatch && needles.every(term => [...all, ...searchTitleWords(record), ...addressWords(record)].some(word => matches(word, term)));
    if (!baseMatch && !searchTitleMatch && !addressMatch && !matchingSections(record, query).length) return -1;
    return (baseMatch ? 1000 : searchTitleMatch ? 750 : addressMatch ? 500 : 0) + needles.filter(term => title.some(word => matches(word, term))).length * 10 + (normalize(record.title).includes(normalize(query)) ? 25 : 0);
  }
  function decodeSections(data) {
    if (!data || ![2, 3, 4].includes(data.version) || !data.pages || typeof data.pages !== 'object' || Array.isArray(data.pages)) return {};
    if (data.version === 4 && (!Array.isArray(data.labels) || data.labels.some(label => typeof label !== 'string' || !label.trim()))) return {};
    const result = Object.create(null);
    const entries = [];
    if (data.version === 2) entries.push(...Object.entries(data.pages));
    else for (const [group, pages] of Object.entries(data.pages)) {
      if (!/^[a-z0-9-]*$/.test(group) || !pages || typeof pages !== 'object' || Array.isArray(pages)) continue;
      for (const [suffix, flat] of Object.entries(pages)) {
        if (!/^(?:[a-z0-9-]+\/)*$/.test(suffix) || (!group && suffix)) continue;
        entries.push([group ? '/' + group + '/' + suffix : '/', flat]);
      }
    }
    for (const [path, flat] of entries) {
      if (!/^\/(?:[a-z0-9-]+\/)*$/.test(path) || !Array.isArray(flat) || flat.length % 2) continue;
      const rows = [];
      for (let i = 0; i < flat.length; i += 2) {
        const value = flat[i + 1];
        const label = data.version === 4 && Number.isInteger(value) && value >= 0 ? data.labels[value] : value;
        if (typeof flat[i] !== 'string' || !/^[A-Za-z0-9_-]+$/.test(flat[i]) || typeof label !== 'string' || !label.trim()) continue;
        rows.push([flat[i], label]);
      }
      result[path] = rows;
    }
    return result;
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = { normalize, terms, score, matchingSections, decodeSections };
  if (typeof document === 'undefined') return;
  const controls = document.getElementById('find-controls');
  if (!controls) return;
  const query = document.getElementById('find-query');
  const interest = document.getElementById('find-interest');
  const kind = document.getElementById('find-kind');
  const status = document.getElementById('find-status');
  const heading = document.getElementById('find-results');
  const empty = document.getElementById('find-empty');
  let sectionIndex = {};
  try {
    const data = document.getElementById('find-section-data');
    const parsed = data ? JSON.parse(data.textContent) : {};
    sectionIndex = decodeSections(parsed);
  } catch (_) { /* The original title and summary search remains available. */ }
  function sectionsFor(node) {
    const path = node.querySelector('h3 a').getAttribute('href');
    const rows = sectionIndex[path];
    return Array.isArray(rows) ? rows.filter(row => Array.isArray(row) && row.length === 2 &&
      typeof row[0] === 'string' && /^[A-Za-z0-9_-]+$/.test(row[0]) && typeof row[1] === 'string' && row[1].trim()) : [];
  }
  const groups = [...document.querySelectorAll('.find-group')].map(group => ({
    node: group, list: group.querySelector('.find-items'), count: group.querySelector('.find-group-count'),
    items: [...group.querySelectorAll('.find-item')].map((node, order) => ({
      node, order, path: node.querySelector('h3 a').getAttribute('href'), title: node.querySelector('h3').textContent,
      searchTitle: node.dataset.searchTitle || '',
      description: node.querySelector('.find-description').textContent,
      subjects: node.querySelector('.find-subjects').textContent,
      interests: node.dataset.interests.split(' '), kind: node.dataset.kind, sections: sectionsFor(node)
    }))
  }));
  const total = groups.reduce((n, group) => n + group.items.length, 0);
  let timer;
  function showSections(item, query, visible) {
    if (!item.sections.length) return;
    if (!item.sectionMatches) {
      item.sectionMatches = document.createElement('div');
      item.sectionMatches.className = 'find-section-matches';
      item.node.append(item.sectionMatches);
    }
    const target = item.sectionMatches;
    const sections = visible ? matchingSections(item, query) : [];
    target.replaceChildren();
    target.hidden = !sections.length;
    if (!sections.length) return;
    const label = document.createElement('p');
    label.textContent = sections.length === 1 ? 'Matching section' : 'Matching sections';
    const list = document.createElement('ul');
    const path = item.node.querySelector('h3 a').getAttribute('href');
    for (const [anchor, title] of sections) {
      const row = document.createElement('li');
      const link = document.createElement('a');
      link.setAttribute('href', path + '#' + anchor);
      link.textContent = title;
      row.append(link); list.append(row);
    }
    target.append(label, list);
  }
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
        showSections(item, value, show);
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
  function submit() {
    filter(); heading.focus({preventScroll:true});
    heading.scrollIntoView({block:'center',behavior:'instant'});
  }
  query.addEventListener('input', event => { clearTimeout(timer); if (!event.isComposing) timer = setTimeout(filter, 140); });
  query.addEventListener('compositionstart', () => clearTimeout(timer));
  query.addEventListener('compositionend', filter);
  query.addEventListener('search', filter);
  query.addEventListener('keydown', event => {
    if (event.key === 'Enter' && !event.isComposing && event.keyCode !== 229) { event.preventDefault(); submit(); }
  });
  interest.addEventListener('change', filter);
  kind.addEventListener('change', filter);
  document.getElementById('find-submit').addEventListener('click', submit);
  document.getElementById('find-reset').addEventListener('click', () => reset(true));
  // Do not restore a previous visitor query when returning through browser history.
  window.addEventListener('pagehide', () => reset(false));
  window.addEventListener('pageshow', event => { if (event.persisted) reset(false); });
  reset(false);
  controls.hidden = false;
})();
