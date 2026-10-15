/* Private, optional practice. Native explanations remain when this is blocked. */
(() => {
  'use strict';
  const root = document.querySelector('[data-course-hand]');
  if (!root) return;
  const scenes = [...root.querySelectorAll('[data-course-scene]')];
  const progress = root.querySelector('[data-course-progress]');
  const back = root.querySelector('[data-course-back]');
  const next = root.querySelector('[data-course-next]');
  const finish = root.querySelector('[data-course-finish]');
  if (scenes.length !== 6 || !progress || !back || !next || !finish || scenes.some(scene => {
    const inputs = [...scene.querySelectorAll('input[type="radio"]')];
    return inputs.length !== 3 || !inputs.some(input => input.value === scene.dataset.answer) ||
      !scene.querySelector('[data-course-solution]') || !scene.querySelector('[data-course-status]') ||
      !scene.querySelector('[data-course-check]') || !scene.querySelector('[data-course-retry]');
  })) return;
  let current = 0;
  const answered = scenes.map(() => false);
  const reveal = (scene, focus) => {
    if (focus) scene.querySelector('h3').focus({preventScroll: true});
    const header = document.querySelector('.site-header');
    const clearance = header ? header.getBoundingClientRect().height + 20 : 20;
    scrollTo({top: scrollY + scene.getBoundingClientRect().top - clearance, behavior: 'instant'});
  };
  root.classList.add('course-enhanced');
  root.querySelectorAll('[data-course-enhanced], input[type="radio"]').forEach(el => { el.hidden = false; });
  const show = (index, focus) => {
    current = index;
    scenes.forEach((scene, i) => { scene.hidden = i !== current; });
    progress.textContent = 'Scene ' + (current + 1) + ' of ' + scenes.length + '. Explain your reason before checking.';
    back.disabled = current === 0;
    next.disabled = !answered[current];
    next.hidden = current === scenes.length - 1;
    finish.hidden = current !== scenes.length - 1 || !answered[current];
    if (focus) reveal(scenes[current], true);
  };
  const clear = (scene, index, resetInputs) => {
    answered[index] = false;
    const solution = scene.querySelector('[data-course-solution]');
    solution.open = false;
    solution.hidden = true;
    scene.querySelector('[data-course-status]').textContent = '';
    if (resetInputs) scene.querySelectorAll('input').forEach(input => { input.checked = false; });
    show(current, false);
  };
  scenes.forEach((scene, index) => {
    const solution = scene.querySelector('[data-course-solution]');
    const status = scene.querySelector('[data-course-status]');
    solution.hidden = true;
    scene.querySelectorAll('input').forEach(input => input.addEventListener('change', () => clear(scene, index, false)));
    scene.querySelector('[data-course-check]').addEventListener('click', () => {
      const selected = scene.querySelector('input:checked');
      if (!selected) {
        status.textContent = 'Choose one answer first. You can also use the lessons below.';
        return;
      }
      const correct = selected.value === scene.dataset.answer;
      status.textContent = correct ? 'That matches the explanation. Say why, then continue when you are ready.' : 'Compare your reason with the explanation below. You can retry or continue.';
      scene.querySelectorAll('[data-choice-note]').forEach(note => { note.hidden = note.dataset.choiceNote !== selected.value; });
      solution.hidden = false;
      solution.open = true;
      answered[index] = true;
      show(current, false);
    });
    scene.querySelector('[data-course-retry]').addEventListener('click', () => {
      clear(scene, index, true);
      scene.querySelector('input').focus();
    });
  });
  back.addEventListener('click', () => { if (current > 0) show(current - 1, true); });
  next.addEventListener('click', () => { if (answered[current] && current + 1 < scenes.length) show(current + 1, true); });
  const followFragment = () => {
    const index = scenes.findIndex(scene => '#' + scene.id === location.hash);
    if (index >= 0) {
      show(index, false);
      requestAnimationFrame(() => reveal(scenes[index], false));
    }
  };
  show(0, false);
  followFragment();
  addEventListener('hashchange', followFragment);
})();
