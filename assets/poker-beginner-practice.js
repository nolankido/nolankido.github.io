/* Fixed educational examples. All answer state stays in this document. */
(() => {
  'use strict';
  const root = document.querySelector('[data-drill-room]');
  if (!root) return;
  const units = [...root.querySelectorAll('[data-drill-unit]')];
  const progress = root.querySelector('[data-drill-progress]');
  const back = root.querySelector('[data-drill-back]');
  const next = root.querySelector('[data-drill-next]');
  const mix = root.querySelector('[data-drill-mix]');
  const summary = root.querySelector('[data-drill-summary]');
  const review = root.querySelector('[data-drill-review-list]');
  if (units.length !== 6 || !progress || !back || !next || !mix || !summary || !review || units.some(unit => {
    const cases = [...unit.querySelectorAll('[data-drill-case]')];
    return cases.length !== 3 || !unit.querySelector('[data-drill-model]') || !unit.querySelector('[data-drill-example-button]') || cases.some(el =>
      el.querySelectorAll('input[type="radio"]').length !== 3 || !['0', '1', '2'].includes(el.dataset.answer) ||
      !el.querySelector('[data-drill-answer]') || !el.querySelector('[data-drill-status]') || !el.querySelector('[data-drill-choices]') ||
      !el.querySelector('[data-drill-check]') || !el.querySelector('[data-drill-unsure]') || !el.querySelector('[data-drill-retry]') || !el.querySelector('[data-drill-choices-button]'));
  })) return;
  const all = units.flatMap(unit => [...unit.querySelectorAll('[data-drill-case]')].map(el => ({el, unit, answered: false, revisit: false, example: false})));
  let queue = [], current = 0, mixed = false, set = -1, complete = false;
  const scrollToItem = (el, focus = true) => {
    const title = el.matches('h2,h3') ? el : el.querySelector('h2, h3');
    if (focus && title) title.focus({preventScroll: true});
    const header = document.querySelector('.site-header');
    scrollTo({top: scrollY + el.getBoundingClientRect().top - (header ? header.getBoundingClientRect().height : 0) - 20, behavior: 'instant'});
  };
  const reset = (item, history) => {
    item.answered = false;
    if (history) { item.revisit = false; item.example = !mixed; }
    item.el.querySelectorAll('input').forEach(input => { input.checked = false; });
    const answer = item.el.querySelector('[data-drill-answer]');
    answer.open = false; answer.hidden = true;
    item.el.querySelector('[data-drill-status]').textContent = '';
    item.el.querySelector('[data-drill-choices]').hidden = true;
    item.el.querySelector('[data-drill-choices-button]').hidden = false;
    item.el.querySelector('[data-drill-check]').disabled = true;
    item.el.querySelector('[data-drill-unsure]').disabled = false;
  };
  const show = focus => {
    const item = queue[current];
    all.forEach(other => { other.el.hidden = complete || other !== item; });
    units.forEach(unit => { unit.hidden = complete || unit !== item.unit; });
    summary.hidden = !complete;
    back.hidden = complete; next.hidden = complete;
    back.disabled = current === 0; next.disabled = !item.answered;
    next.textContent = current === queue.length - 1 ? 'Review this visit' : 'Next question';
    progress.textContent = complete ? 'This visit is ready to review. Choose one idea to revisit later.' :
      (mixed ? 'Mixed set ' + (set + 1) + ' of 3' : 'One-skill practice') + ': question ' + (current + 1) + ' of ' + queue.length + '.';
    root.querySelectorAll('[data-drill-skill]').forEach(link => {
      if (!mixed && link.dataset.drillSkill === item.unit.dataset.drillUnit) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    if (focus) scrollToItem(complete ? summary : item.el);
  };
  const start = (unit, index, useMixed, focus) => {
    mixed = useMixed; complete = false;
    if (mixed) {
      set = (set + 1) % 3;
      queue = [3, 0, 5, 2, 1, 4].map(i => all.filter(item => item.unit === units[i])[(set + i) % 3]);
    } else queue = all.filter(item => item.unit === unit);
    current = Math.max(0, Math.min(index, queue.length - 1));
    all.forEach(item => reset(item, true));
    units.forEach(el => {
      const model = el.querySelector('[data-drill-model]');
      model.hidden = mixed; model.open = !mixed;
      el.querySelector('[data-drill-example-button]').hidden = !mixed;
    });
    review.replaceChildren();
    show(focus);
  };
  const explain = (item, unsure) => {
    const selected = item.el.querySelector('input:checked');
    const status = item.el.querySelector('[data-drill-status]');
    if (!selected && !unsure) {
      status.textContent = 'Choose an answer, or use “I’m not sure” to see what to revisit.';
      return;
    }
    const matches = !unsure && selected.value === item.el.dataset.answer;
    item.answered = true; item.revisit = item.revisit || !matches;
    status.textContent = unsure ? 'This is an idea to revisit. Compare the explanation, then try another example.' :
      matches ? 'Your choice matches. Explain the reason in your own words before continuing.' : 'Compare your reason with the explanation. You can retry or continue.';
    item.el.querySelectorAll('[data-drill-note]').forEach(note => { note.hidden = unsure || note.dataset.drillNote !== selected.value; });
    const answer = item.el.querySelector('[data-drill-answer]');
    answer.hidden = false; answer.open = true;
    show(false);
  };
  root.classList.add('drills-enhanced');
  root.querySelectorAll('[data-drill-enhanced], input[type="radio"]').forEach(el => { el.hidden = false; });
  all.forEach(item => {
    item.el.querySelector('[data-drill-choices-button]').addEventListener('click', () => {
      item.el.querySelector('[data-drill-choices]').hidden = false;
      item.el.querySelector('[data-drill-choices-button]').hidden = true;
      item.el.querySelector('[data-drill-check]').disabled = false;
      item.el.querySelector('input').focus();
    });
    item.el.querySelectorAll('input').forEach(input => input.addEventListener('change', () => {
      item.answered = false;
      const answer = item.el.querySelector('[data-drill-answer]');
      answer.hidden = true; answer.open = false;
      item.el.querySelector('[data-drill-status]').textContent = '';
      show(false);
    }));
    item.el.querySelector('[data-drill-check]').addEventListener('click', () => explain(item, false));
    item.el.querySelector('[data-drill-unsure]').addEventListener('click', () => explain(item, true));
    item.el.querySelector('[data-drill-retry]').addEventListener('click', () => { reset(item, false); show(false); item.el.querySelector('[data-drill-choices-button]').focus(); });
  });
  units.forEach(unit => unit.querySelector('[data-drill-example-button]').addEventListener('click', () => {
    const model = unit.querySelector('[data-drill-model]');
    model.hidden = false; model.open = true;
    queue[current].example = true;
    unit.querySelector('[data-drill-example-button]').hidden = true;
    model.querySelector('summary').focus();
  }));
  back.addEventListener('click', () => { if (current > 0) { current--; show(true); } });
  next.addEventListener('click', () => {
    if (!queue[current].answered) return;
    if (current + 1 < queue.length) { current++; show(true); return; }
    complete = true;
    const rows = queue.map(item => {
      const li = document.createElement('li');
      const label = document.createElement('strong');
      label.textContent = item.el.querySelector('h3').textContent + ': ';
      const text = document.createElement('span');
      text.textContent = item.revisit ? 'Revisit after an uncertain or different answer. ' : item.example ? 'Choice matched; an example was shown. ' : 'Choice matched without an example shown. Explain it again later. ';
      const repair = document.createElement('a');
      repair.href = item.el.querySelector('[data-drill-repair]').getAttribute('href');
      repair.textContent = 'Review this idea';
      li.append(label, text, repair); return li;
    });
    review.replaceChildren(...rows);
    show(true);
  });
  mix.addEventListener('click', () => start(null, 0, true, true));
  const fragment = focus => {
    const target = document.getElementById(location.hash.slice(1));
    const unit = target && (target.matches('[data-drill-unit]') ? target : target.closest('[data-drill-unit]'));
    if (!unit || !units.includes(unit)) return false;
    const cases = all.filter(item => item.unit === unit);
    const index = Math.max(0, cases.findIndex(item => item.el === target));
    start(unit, index, false, false);
    requestAnimationFrame(() => scrollToItem(target, focus));
    return true;
  };
  root.querySelectorAll('[data-drill-skill]').forEach(link => link.addEventListener('click', () => {
    if (link.hash === location.hash) fragment(true);
  }));
  start(units[0], 0, false, false);
  fragment(false);
  addEventListener('hashchange', () => fragment(true));
})();
