/* Editorial decision rules. No model, score, network, or storage. */
(() => {
  'use strict';
  const OPTIONS = Object.freeze({
    goal: ['clear', 'unclear'], inputs: ['allowed', 'restricted', 'unknown'],
    stakes: ['low', 'high'], review: ['ready', 'missing'],
    simpler: ['yes', 'no', 'unknown'], scope: ['draft', 'action']
  });
  function decide(answers) {
    if (!answers || typeof answers !== 'object' || Array.isArray(answers) ||
        Object.keys(answers).length !== Object.keys(OPTIONS).length ||
        Object.entries(OPTIONS).some(([key, values]) =>
          !Object.hasOwn(answers, key) || !values.includes(answers[key]))) {
      throw new TypeError('Choose one valid answer for each question.');
    }
    const reasons = [];
    if (answers.inputs !== 'allowed') reasons.push('Do not put these inputs in the proposed tool until permission and the tool rules are resolved.');
    if (answers.stakes === 'high') reasons.push('The consequences are outside this everyday-task guide. Keep the decision with the appropriate person and arrange qualified review.');
    if (answers.review !== 'ready') reasons.push('Arrange a specific independent check before relying on an output. Another answer from the same system is not enough.');
    if (answers.goal !== 'clear') reasons.push('Name a useful finished result and what would make it unacceptable.');
    if (answers.simpler === 'yes') reasons.push('An adequate simpler method is already available. Start there.');
    if (answers.simpler === 'unknown') reasons.push('Try the ordinary method first so there is a real comparison.');
    if (answers.scope === 'action') reasons.push('Keep sending, spending, deleting, publishing and commitments outside this trial. A person must decide about any external action separately.');
    let result;
    if (answers.inputs !== 'allowed' || answers.stakes === 'high') {
      result = {kind: 'pause', title: 'Pause before using AI for this task.',
        next: 'Resolve the input or consequence boundary first. Do not treat the other answers as permission to proceed.',
        route: '#choice-method', label: 'Read the boundaries and decision order'};
    } else if (answers.review !== 'ready' || answers.goal !== 'clear') {
      result = {kind: 'prepare', title: 'Prepare the task before delegating.',
        next: 'Define the result and arrange its independent check. Revisit this guide after those conditions are in place.',
        route: '/technology/task-brief/', label: 'Use the task brief to define the missing pieces'};
    } else if (answers.simpler !== 'no') {
      result = {kind: 'simpler', title: answers.simpler === 'yes' ? 'Start with the simpler method.' : 'Compare with the ordinary method first.',
        next: 'Try the simpler approach on the same task. Count preparation, checking and repairs before deciding whether another method is worth trying.',
        route: '/technology/ai-time-savings/', label: 'Compare the whole workflow, not just drafting time'};
    } else if (answers.scope !== 'draft') {
      result = {kind: 'prepare', title: 'Keep actions out of this trial.',
        next: 'Reduce the task to one reviewable draft or set of suggestions. Decide separately who may take any action and under what permission.',
        route: '/technology/task-brief/', label: 'Write the draft-only boundary into a task brief'};
    } else {
      result = {kind: 'trial', title: 'Try one small, reversible draft.',
        next: 'Keep the original, request one bounded output, and check it before using it. Stop if checking or repairs make the method more work than it is worth.',
        route: '/technology/task-brief/', label: 'Build a brief for the bounded trial'};
      reasons.push('Your answers leave no unresolved condition in this short guide. That is not a verification of the task, the inputs, or the service.');
    }
    return {...result, reasons};
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {decide};
  if (typeof document === 'undefined') return;
  const form = document.getElementById('choice-form');
  if (!form) return;
  const result = document.getElementById('choice-result');
  const error = document.getElementById('choice-error');
  const title = document.getElementById('choice-result-title');
  function clearResult() {
    result.hidden = true;
    delete result.dataset.kind;
    ['choice-result-title', 'choice-next', 'choice-reasons', 'choice-boundary', 'choice-route'].forEach(id => {
      document.getElementById(id).replaceChildren();
    });
    form.querySelectorAll('[aria-invalid]').forEach(el => el.removeAttribute('aria-invalid'));
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    clearResult();
    const answers = {};
    for (const key of Object.keys(OPTIONS)) {
      const control = form.querySelector('input[name="' + key + '"]:checked');
      if (!control) {
        error.textContent = 'Choose an answer for every question. Start with the highlighted question.';
        const first = form.querySelector('input[name="' + key + '"]');
        first.setAttribute('aria-invalid', 'true');
        first.focus();
        return;
      }
      answers[key] = control.value;
    }
    let decision;
    try { decision = decide(answers); }
    catch (_) {
      error.textContent = 'These answers could not be checked. Clear them and try again, or use the written rules below.';
      return;
    }
    error.textContent = '';
    title.textContent = decision.title;
    document.getElementById('choice-next').textContent = decision.next;
    const list = document.getElementById('choice-reasons');
    decision.reasons.forEach(reason => {
      const item = document.createElement('li'); item.textContent = reason; list.appendChild(item);
    });
    document.getElementById('choice-boundary').textContent = 'No external action is authorized by this result. Keep the final judgment and any send, publish, spend or delete decision with a person.';
    const link = document.createElement('a'); link.href = decision.route; link.textContent = decision.label;
    document.getElementById('choice-route').appendChild(link);
    result.dataset.kind = decision.kind;
    result.hidden = false;
    title.focus();
  });
  form.addEventListener('change', () => {
    const wasVisible = !result.hidden;
    clearResult();
    error.textContent = wasVisible ? 'Answers changed. Show your next step again for an updated suggestion.' : '';
  });
  form.addEventListener('reset', () => { clearResult(); error.textContent = 'Answers cleared.'; });
  window.addEventListener('pagehide', () => { form.reset(); error.textContent = ''; });
  window.addEventListener('pageshow', event => { if (event.persisted) { form.reset(); error.textContent = ''; } });
  form.hidden = false;
  document.getElementById('choice-fallback').hidden = true;
})();
