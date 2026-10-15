/* Construct a best-five hand from a fixed educational card bank. */
(() => {
  'use strict';
  const NAMES = ['high card', 'one pair', 'two pair', 'three of a kind', 'a straight', 'a flush', 'a full house', 'four of a kind', 'a straight flush'];
  const valid = (cards, min, max) => Array.isArray(cards) && cards.length >= min && cards.length <= max && new Set(cards).size === cards.length && cards.every(c => typeof c === 'string' && /^[2-9TJQKA][shdc]$/.test(c));
  const compare = (a, b) => {
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
      const difference = (a[i] || 0) - (b[i] || 0);
      if (difference) return difference;
    }
    return 0;
  };
  const scoreFive = cards => {
    if (!valid(cards, 5, 5)) throw new TypeError('Choose five distinct standard cards');
    const ranks = cards.map(c => '23456789TJQKA'.indexOf(c[0]) + 2).sort((a, b) => b - a);
    const counts = new Map();
    ranks.forEach(rank => counts.set(rank, (counts.get(rank) || 0) + 1));
    const groups = [...counts].sort((a, b) => b[1] - a[1] || b[0] - a[0]);
    const flush = cards.every(c => c[1] === cards[0][1]);
    const straight = counts.size === 5 ? (ranks[0] - ranks[4] === 4 ? ranks[0] : ranks.join(',') === '14,5,4,3,2' ? 5 : 0) : 0;
    if (flush && straight) return [8, straight];
    if (groups[0][1] === 4) return [7, groups[0][0], groups[1][0]];
    if (groups[0][1] === 3 && groups[1][1] === 2) return [6, groups[0][0], groups[1][0]];
    if (flush) return [5, ...ranks];
    if (straight) return [4, straight];
    if (groups[0][1] === 3) return [3, ...groups.map(g => g[0])];
    if (groups[0][1] === 2 && groups[1][1] === 2) return [2, ...groups.map(g => g[0])];
    if (groups[0][1] === 2) return [1, ...groups.map(g => g[0])];
    return [0, ...ranks];
  };
  const bestFive = cards => {
    if (!valid(cards, 5, 7)) throw new TypeError('Use five to seven distinct standard cards');
    let score = [-1], selections = [];
    const choose = (from, selected) => {
      if (selected.length === 5) {
        const current = scoreFive(selected), difference = compare(current, score);
        if (difference > 0) { score = current; selections = [selected]; }
        else if (difference === 0) selections.push(selected);
        return;
      }
      for (let i = from; i <= cards.length - (5 - selected.length); i++) choose(i + 1, [...selected, cards[i]]);
    };
    choose(0, []);
    return {score, selections};
  };
  if (typeof module === 'object' && module.exports) module.exports = {scoreFive, bestFive, compare};
  if (typeof document === 'undefined') return;
  const root = document.querySelector('[data-hand-lab]');
  if (!root) return;
  const progress = root.querySelector('[data-lab-progress]'), back = root.querySelector('[data-lab-back]'), next = root.querySelector('[data-lab-next]');
  const review = root.querySelector('[data-lab-review]'), list = root.querySelector('[data-lab-review-list]'), restart = root.querySelector('[data-lab-restart]');
  const elements = [...root.querySelectorAll('[data-lab-case]')];
  if (elements.length !== 10 || !progress || !back || !next || !review || !list || !restart || elements.some(el => {
    const codes = [...el.querySelectorAll('input[data-card]')].map(input => input.dataset.card);
    const solution = (el.dataset.solution || '').split(',');
    return !valid(codes, 7, 7) || !valid(solution, 5, 5) || solution.some(c => !codes.includes(c)) || compare(scoreFive(solution), bestFive(codes).score) !== 0 ||
      ['check','clear','show','count','feedback','hint','answer','repair'].some(name => !el.querySelector('[data-lab-' + name + ']'));
  })) return;
  const items = elements.map(el => ({el, inputs: [...el.querySelectorAll('input[data-card]')], best: bestFive([...el.querySelectorAll('input[data-card]')].map(i => i.dataset.card)).score}));
  let index = 0, complete = false;
  const focusItem = el => {
    const title = el.querySelector('h3');
    title.focus({preventScroll: true});
    const header = document.querySelector('.site-header');
    scrollTo({top: scrollY + el.getBoundingClientRect().top - (header ? header.getBoundingClientRect().height : 0) - 20, behavior: 'instant'});
  };
  const update = () => {
    items.forEach(item => { item.el.hidden = complete || item !== items[index]; });
    review.hidden = !complete;
    back.disabled = !complete && index === 0;
    back.textContent = complete ? 'Return to the last hand' : 'Previous hand';
    next.hidden = complete;
    next.disabled = !items[index].checked && !items[index].help;
    next.textContent = index === items.length - 1 ? 'Review this visit' : 'Next hand';
    const visited = items.filter(item => item.attempted || item.help).length;
    progress.textContent = complete ? 'Review notes for ' + visited + ' of 10 hands from this visit.' : 'Hand ' + (index + 1) + ' of 10. These fixed examples repeat.';
  };
  const count = item => {
    const selected = item.inputs.filter(input => input.checked);
    item.el.querySelector('[data-lab-count]').textContent = selected.length + ' of 5 cards selected. You can deselect any card to replace it.';
    return selected.map(input => input.dataset.card);
  };
  const reset = () => {
    items.forEach(item => {
      Object.assign(item, {checked: false, attempted: false, revisit: false, help: false, solutionShown: false});
      item.inputs.forEach(input => { input.checked = false; });
      item.el.querySelector('[data-lab-feedback]').textContent = '';
      const answer = item.el.querySelector('[data-lab-answer]');
      answer.hidden = true; answer.open = false;
      item.el.querySelector('[data-lab-hint]').open = false;
      count(item);
    });
    list.replaceChildren(); index = 0; complete = false; update();
  };
  root.classList.add('hand-lab-enhanced');
  root.querySelectorAll('[data-lab-enhanced],input[data-card]').forEach(el => { el.hidden = false; });
  items.forEach(item => {
    const feedback = item.el.querySelector('[data-lab-feedback]'), answer = item.el.querySelector('[data-lab-answer]');
    const change = () => {
      item.checked = false; feedback.textContent = ''; answer.hidden = !item.solutionShown;
      count(item); update();
    };
    item.inputs.forEach(input => input.addEventListener('change', change));
    item.el.querySelector('[data-lab-clear]').addEventListener('click', () => {
      item.inputs.forEach(input => { input.checked = false; }); change(); item.inputs[0].focus();
    });
    item.el.querySelector('[data-lab-hint]').addEventListener('toggle', event => {
      if (event.target.open) { item.help = true; update(); }
    });
    item.el.querySelector('[data-lab-show]').addEventListener('click', () => {
      item.help = true; item.solutionShown = true; answer.hidden = false; answer.open = true;
      feedback.textContent = 'A worked solution is shown. Rebuild it and explain which cards you leave out.';
      update(); answer.querySelector('summary').focus();
    });
    item.el.querySelector('[data-lab-check]').addEventListener('click', () => {
      const selected = count(item);
      if (selected.length !== 5) { feedback.textContent = 'Choose exactly five cards first. You currently selected ' + selected.length + '.'; return; }
      const score = scoreFive(selected), matches = compare(score, item.best) === 0;
      item.checked = true; item.attempted = true; item.revisit = item.revisit || !matches;
      if (matches) {
        feedback.textContent = 'These five match the strongest available hand. Explain why the two cards you left out do not improve it.';
        answer.hidden = false; answer.open = true;
      } else if (score[0] !== item.best[0]) feedback.textContent = 'Your selection makes ' + NAMES[score[0]] + '. The strongest available category is ' + NAMES[item.best[0]] + '. Use the hint or compare one worked solution.';
      else feedback.textContent = 'The hand category matches, but the ranks or side cards are lower. Compare all five cards in order; a private card does not have to play. Use the hint if needed.';
      update();
    });
  });
  back.addEventListener('click', () => { if (complete) complete = false; else if (index > 0) index--; update(); focusItem(items[index].el); });
  next.addEventListener('click', () => {
    if (!items[index].checked && !items[index].help) return;
    if (index + 1 < items.length) { index++; update(); focusItem(items[index].el); return; }
    complete = true;
    list.replaceChildren(...items.filter(item => item.attempted || item.help).map(item => {
      const row = document.createElement('li'), title = document.createElement('strong'), note = document.createElement('span');
      title.textContent = item.el.querySelector('h3').textContent + ': ';
      note.textContent = item.revisit ? 'Revisit: a weaker selection was checked, including before a later correction. ' : item.help ? 'Revisit: a hint or worked solution was shown. ' : 'A strongest selection was checked before a question hint or solution was requested. Explain it again later. ';
      const retry = document.createElement('a'), repair = document.createElement('a');
      retry.href = '#' + item.el.id; retry.textContent = 'Build this hand again';
      repair.href = item.el.querySelector('[data-lab-repair]').getAttribute('href'); repair.textContent = 'Review the rule';
      row.append(title, note, retry, document.createTextNode(' · '), repair); return row;
    }));
    update(); focusItem(review);
  });
  restart.addEventListener('click', () => { reset(); focusItem(items[0].el); });
  const fragment = focus => {
    const target = document.getElementById(location.hash.slice(1));
    const el = target && target.closest('[data-lab-case]');
    const match = items.findIndex(item => item.el === el);
    if (match < 0) return;
    index = match; complete = false; update();
    requestAnimationFrame(() => { if (focus) focusItem(el); else {
      const header = document.querySelector('.site-header');
      scrollTo({top: scrollY + el.getBoundingClientRect().top - (header ? header.getBoundingClientRect().height : 0) - 20, behavior: 'instant'});
    } });
  };
  root.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (link && link.hash && link.hash === location.hash) fragment(true);
  });
  reset(); fragment(false);
  addEventListener('hashchange', () => fragment(true));
})();
