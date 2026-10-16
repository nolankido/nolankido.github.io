/* Optional Study Desk notes. No visits, answers, names or hand histories are recorded. */
(() => {
  'use strict';

  const recordKeys = ['format', 'version', 'course', 'revision', 'next', 'lessons'];
  const plainObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);
  const exactKeys = (value, keys) => plainObject(value) && Object.keys(value).length === keys.length
    && keys.every(key => Object.prototype.hasOwnProperty.call(value, key));
  function utf8Length(text) {
    let bytes = 0;
    for (const character of text) {
      const code = character.codePointAt(0);
      bytes += code < 0x80 ? 1 : code < 0x800 ? 2 : code < 0x10000 ? 3 : 4;
    }
    return bytes;
  }
  function blankRecord(config) {
    return {format: config.format, version: config.version, course: config.course, revision: config.revision,
      next: config.defaultNext, lessons: Object.fromEntries(config.lessons.map(lesson => [lesson.id, 'not-started']))};
  }
  const serializeRecord = value => JSON.stringify(value, null, 2) + '\n';
  function parseRecord(text, config) {
    if (typeof text !== 'string' || utf8Length(text) > config.maxBytes) throw new Error('The progress file is too large. Choose a file of 8 KB or less.');
    let value;
    try { value = JSON.parse(text); } catch (_) { throw new Error('This is not a readable progress file. Copy the complete exported text or choose a progress file.'); }
    if (!exactKeys(value, recordKeys) || value.format !== config.format || value.course !== config.course
      || value.version !== config.version) throw new Error('This progress format is not supported by this page.');
    if (value.revision !== config.revision) throw new Error('This record belongs to different course material and cannot be restored to this version.');
    const lessonIds = config.lessons.map(lesson => lesson.id);
    const states = new Set(config.states.map(state => state.id));
    if (!exactKeys(value.lessons, lessonIds) || !lessonIds.every(id => states.has(value.lessons[id]))
      || !config.destinations.some(destination => destination.id === value.next)) throw new Error('The record contains an unknown lesson, note or next task.');
    const result = blankRecord(config);
    result.next = value.next;
    for (const id of lessonIds) result.lessons[id] = value.lessons[id];
    return result;
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {utf8Length, blankRecord, serializeRecord, parseRecord};
  if (typeof document === 'undefined') return;

  const root = document.getElementById('course-progress');
  const configElement = document.getElementById('poker-progress-data');
  if (!root || !configElement) return;
  let config;
  try {
    config = JSON.parse(configElement.textContent);
    if (config.format !== 'nolan-kido-poker-progress' || config.version !== 1 || config.course !== 'poker-foundations'
      || !/^[a-f0-9]{64}$/.test(config.revision) || config.storageKey !== 'nolan-kido:poker-foundations:progress:v1'
      || config.maxBytes !== 8192 || config.lessons.length !== 6 || config.destinations.length !== 14
      || new Set(config.lessons.map(lesson => lesson.id)).size !== 6
      || new Set(config.destinations.map(item => item.id)).size !== 14
      || !Array.isArray(config.states) || config.states.map(item => item.id).join(',') !== 'not-started,working,practiced,revisit'
      || !config.destinations.every(item => typeof item.href === 'string' && /^\/poker\/[a-z0-9-]+\/(?:#[a-z0-9-]+)?$/.test(item.href))
      || !config.destinations.some(item => item.id === config.defaultNext)) return;
  } catch (_) { return; }
  const byId = id => document.getElementById(id);
  const next = byId('progress-next'), resume = byId('progress-resume'), status = byId('progress-status');
  const summary = byId('progress-summary'), revisitList = byId('progress-revisit-list'), revisitEmpty = byId('progress-revisit-empty');
  const storageDetails = byId('progress-storage'), rememberInput = byId('progress-remember'), storageStatus = byId('progress-storage-status');
  const forget = byId('progress-forget'), reset = byId('progress-reset');
  const transfer = byId('progress-transfer'), download = byId('progress-download'), exportText = byId('progress-export-text');
  const selectExport = byId('progress-select-export'), fileInput = byId('progress-import-file'), pasteInput = byId('progress-import-text');
  const reviewPaste = byId('progress-review-import'), transferStatus = byId('progress-transfer-status');
  const preview = byId('progress-import-preview'), previewTitle = byId('progress-import-preview-title');
  const previewSummary = byId('progress-import-summary'), previewLessons = byId('progress-import-lessons'), previewSaving = byId('progress-import-saving');
  const applyImport = byId('progress-apply-import'), cancelPreview = byId('progress-cancel-import'), fallback = byId('progress-fallback');
  const fields = config.lessons.map(lesson => byId('progress-status-' + lesson.id));
  if (![next, resume, status, summary, revisitList, revisitEmpty, storageDetails, rememberInput, storageStatus, forget, reset,
    transfer, download, exportText, selectExport, fileInput, pasteInput, reviewPaste, transferStatus, preview, previewTitle,
    previewSummary, previewLessons, previewSaving, applyImport, cancelPreview, fallback, ...fields].every(Boolean)) return;
  const destinations = new Map(config.destinations.map(item => [item.id, item]));
  const labels = new Map(config.states.map(item => [item.id, item.label]));
  const key = config.storageKey;
  let state = blankRecord(config);
  let remember = false;
  let expectedRaw = null;
  let stateRevision = 0;
  let importTicket = 0;
  let readingFile = false;
  let pendingImport = null;
  let exportURL;
  let downloadAvailable = false;

  const readSaved = () => window.localStorage.getItem(key);
  function showStorage(message, open = false) {
    storageStatus.textContent = message;
    if (open) storageDetails.open = true;
    rememberInput.checked = remember;
  }
  function invalidateImport(message = '') {
    const wasPending = pendingImport !== null || readingFile;
    const focusedPreview = !preview.hidden && preview.contains(document.activeElement);
    const source = pendingImport ? pendingImport.source : reviewPaste;
    importTicket += 1;
    pendingImport = null;
    readingFile = false;
    preview.hidden = true;
    previewSummary.textContent = '';
    previewLessons.replaceChildren();
    previewSaving.textContent = '';
    if (wasPending && message) transferStatus.textContent = message;
    if (focusedPreview) {
      const target = transfer.open ? source : transfer.querySelector('summary');
      if (target) target.focus();
    }
  }
  function releaseExport() {
    download.hidden = true;
    download.removeAttribute('href');
    const previous = exportURL;
    exportURL = undefined;
    downloadAvailable = false;
    if (previous) { try { URL.revokeObjectURL(previous); } catch (_) { /* The unusable link is already removed. */ } }
  }
  function refreshExport() {
    releaseExport();
    exportText.value = serializeRecord(state);
    try {
      exportURL = URL.createObjectURL(new Blob([exportText.value], {type: 'application/json;charset=utf-8'}));
      download.href = exportURL;
      download.hidden = false;
      downloadAvailable = true;
    } catch (_) {
      releaseExport();
      transfer.open = true;
      transferStatus.textContent = 'A download is unavailable here. Select and copy the complete progress text below to keep it.';
    }
  }
  function addLink(parent, href, text) {
    const link = document.createElement('a');
    link.href = href; link.textContent = text; link.target = '_blank'; link.rel = 'noopener';
    link.setAttribute('aria-label', text + ' (opens in a new tab)');
    parent.appendChild(link);
  }
  function renderState() {
    config.lessons.forEach((lesson, index) => {
      fields[index].value = state.lessons[lesson.id];
      const printable = byId('progress-print-' + lesson.id);
      if (printable) printable.textContent = 'Your note: ' + labels.get(state.lessons[lesson.id]);
    });
    next.value = state.next;
    const destination = destinations.get(state.next);
    resume.href = destination.href;
    resume.textContent = destination.label;
    resume.setAttribute('aria-label', destination.label + ' (opens in a new tab)');
    const counts = Object.fromEntries(config.states.map(item => [item.id, 0]));
    for (const value of Object.values(state.lessons)) counts[value] += 1;
    summary.textContent = counts.working + ' working on it · ' + counts.practiced + ' practiced · ' + counts.revisit
      + ' to revisit · ' + counts['not-started'] + ' not started. These are your notes, not a score.';
    revisitList.replaceChildren();
    for (const lesson of config.lessons.filter(item => state.lessons[item.id] === 'revisit')) {
      const li = document.createElement('li');
      addLink(li, lesson.read, lesson.title);
      li.appendChild(document.createTextNode(' · '));
      addLink(li, lesson.practice, 'Practice this lesson');
      revisitList.appendChild(li);
    }
    revisitEmpty.hidden = revisitList.children.length > 0;
    rememberInput.checked = remember;
    refreshExport();
  }
  function externalChange(raw) {
    if (raw === expectedRaw) return;
    const wasRemembered = remember;
    expectedRaw = raw;
    stateRevision += 1;
    invalidateImport('Saved progress changed in another tab. Review an import again before replacing anything.');
    if (raw === null) {
      remember = false;
      if (wasRemembered) {
        state = blankRecord(config);
        pasteInput.value = '';
        fileInput.value = '';
        showStorage('The saved copy was cleared in another tab. Remember on this device is now off.', true);
        status.textContent = 'Progress was cleared in another tab. This page has been reset and will not save old marks again.';
      } else {
        showStorage('The saved copy was cleared in another tab. Your open-page marks and next task remain temporary.', true);
        status.textContent = 'Your open-page marks and next task are unchanged. Remember on this device stays off.';
      }
    } else {
      try {
        const replacement = parseRecord(raw, config);
        if (wasRemembered) {
          state = replacement;
          showStorage('The saved marks and next task were updated in another tab.');
          status.textContent = 'Progress updated in another tab. Review the current record before continuing.';
        } else {
          showStorage('A saved record changed in another tab. This page stays temporary. Reload to load the saved copy, or explicitly remember the record shown here.', true);
          status.textContent = 'Your open-page marks are unchanged. A different saved record is available in this browser.';
        }
      } catch (error) {
        remember = false;
        showStorage(error.message + ' The saved copy was not changed. Your open-page marks remain temporary.', true);
        status.textContent = 'Saved progress changed but could not be loaded. Device saving is off for this tab.';
      }
    }
    renderState();
  }
  function checkBeforeChange() {
    if (!remember) return true;
    try {
      const raw = readSaved();
      if (raw !== expectedRaw) { externalChange(raw); return false; }
    } catch (_) {
      remember = false;
      showStorage('Device saving could not be checked. Your changes will stay in this page; an earlier saved copy may remain.', true);
    }
    return true;
  }
  function saveCurrent() {
    if (!remember) return;
    const text = serializeRecord(state);
    try {
      window.localStorage.setItem(key, text);
      expectedRaw = text;
      showStorage('Your six marks and next task are saved in this browser. Changes update this copy while Remember is checked.');
    } catch (_) {
      remember = false;
      showStorage('Device saving failed. Your changes remain in this page. An earlier saved copy may still return after reload; export this record to keep it.', true);
    }
  }
  function changeRecord(change, message) {
    if (!checkBeforeChange()) return;
    stateRevision += 1;
    invalidateImport('Your record changed. Review the import again before replacing anything.');
    change();
    saveCurrent();
    renderState();
    status.textContent = message + (remember ? ' Saved on this device.' : ' Kept in this page.');
  }
  function removeSavedCopy(resetMarks) {
    remember = false;
    stateRevision += 1;
    invalidateImport();
    transferStatus.textContent = '';
    if (resetMarks) {
      state = blankRecord(config);
      pasteInput.value = '';
      fileInput.value = '';
    }
    let removed = false;
    try {
      window.localStorage.removeItem(key);
      const raw = readSaved();
      expectedRaw = raw;
      if (raw !== null) throw new Error('Removal not confirmed');
      removed = true;
    } catch (_) { /* Saving remains off even if deletion or its verification failed. */ }
    if (removed) {
      showStorage('Device saving is off and the saved copy has been removed.');
      status.textContent = resetMarks ? 'Marks reset. Choose a next task when you are ready.' : 'The saved copy is removed. Your current marks remain in this page.';
    } else {
      showStorage('Device saving is off for this tab, but removal of the saved copy could not be confirmed. It may return after reload. Use Remove saved copy to retry, or clear this site’s browser data.', true);
      status.textContent = resetMarks ? 'The open-page marks were reset. A previously saved copy may still remain.' : 'Your open-page marks remain. The saved copy may still be present.';
    }
    renderState();
  }

  fields.forEach((field, index) => field.addEventListener('change', () => {
    const lesson = config.lessons[index], value = field.value;
    if (!labels.has(value)) { renderState(); return; }
    changeRecord(() => { state.lessons[lesson.id] = value; }, lesson.title + ': ' + labels.get(value) + '.');
  }));
  next.addEventListener('change', () => {
    const value = next.value;
    if (!destinations.has(value)) { renderState(); return; }
    changeRecord(() => { state.next = value; }, 'Next task updated.');
  });
  rememberInput.addEventListener('change', () => {
    const enabling = rememberInput.checked;
    stateRevision += 1;
    invalidateImport('The saving setting changed. Review an import again before replacing anything.');
    if (!enabling) { removeSavedCopy(false); return; }
    try {
      expectedRaw = readSaved();
      const text = serializeRecord(state);
      window.localStorage.setItem(key, text);
      expectedRaw = text;
      remember = true;
      showStorage('Your six marks and next task are saved in this browser. Changes update this copy while Remember is checked.');
      status.textContent = 'Remember on this device is on. Only your marks and next task are saved.';
    } catch (_) {
      remember = false;
      showStorage('Device saving is unavailable here. Your record remains in this page. Use a progress file or copy the complete text to keep it.', true);
      status.textContent = 'Device saving was not enabled.';
    }
    rememberInput.checked = remember;
  });
  forget.addEventListener('click', () => removeSavedCopy(false));
  reset.addEventListener('click', () => { removeSavedCopy(true); next.focus(); });

  function previewRecord(record, source, ticket, revision) {
    if (ticket !== importTicket || revision !== stateRevision) return;
    pendingImport = {record, source, ticket, revision};
    previewSummary.textContent = 'Next task: ' + destinations.get(record.next).label + '.';
    previewLessons.replaceChildren();
    for (const lesson of config.lessons) {
      const item = document.createElement('li');
      item.textContent = lesson.title + ': ' + labels.get(record.lessons[lesson.id]);
      previewLessons.appendChild(item);
    }
    previewSaving.textContent = remember
      ? 'Remember on this device is currently on. Replacing also updates its saved copy.'
      : 'Remember on this device is off. Replacing keeps the imported record in this page and does not enable saving.';
    preview.hidden = false;
    transfer.open = true;
    transferStatus.textContent = 'Review the marks below before replacing your current record.';
    if (document.activeElement === source) previewTitle.focus();
  }
  function importFailure(error) {
    transfer.open = true;
    transferStatus.textContent = error.message + ' Your current record is unchanged.';
  }
  reviewPaste.addEventListener('click', () => {
    invalidateImport();
    try { previewRecord(parseRecord(pasteInput.value, config), reviewPaste, importTicket, stateRevision); }
    catch (error) { importFailure(error); }
  });
  pasteInput.addEventListener('input', () => invalidateImport('Pasted text changed. Review it again before replacing anything.'));
  fileInput.addEventListener('change', async () => {
    const file = fileInput.files && fileInput.files[0];
    if (!file) return;
    fileInput.value = '';
    invalidateImport();
    const ticket = importTicket, revision = stateRevision;
    if (file.size > config.maxBytes) { importFailure(new Error('The progress file is too large. Choose a file of 8 KB or less.')); return; }
    readingFile = true;
    transferStatus.textContent = 'Reading your progress file in this browser.';
    let text;
    try {
      if (typeof file.text !== 'function') throw new Error('This browser could not read the file. Paste its complete text instead.');
      text = await file.text();
    } catch (_) {
      if (ticket !== importTicket || revision !== stateRevision) return;
      readingFile = false;
      importFailure(new Error('The file could not be read. Try again or paste its complete text.'));
      return;
    }
    if (ticket !== importTicket || revision !== stateRevision) return;
    readingFile = false;
    try { previewRecord(parseRecord(text, config), fileInput, ticket, revision); }
    catch (error) { importFailure(error); }
  });
  applyImport.addEventListener('click', () => {
    if (!pendingImport || pendingImport.ticket !== importTicket || pendingImport.revision !== stateRevision) return;
    const imported = pendingImport.record;
    if (!checkBeforeChange()) return;
    invalidateImport();
    stateRevision += 1;
    state = imported;
    pasteInput.value = '';
    fileInput.value = '';
    saveCurrent();
    renderState();
    const outcome = remember ? 'Progress replaced and saved on this device.' : 'Progress replaced in this page. Device saving is off.';
    status.textContent = outcome;
    transferStatus.textContent = outcome + (downloadAvailable ? '' : ' A download is unavailable; select and copy the complete export text to keep it.');
    next.focus();
  });
  cancelPreview.addEventListener('click', () => {
    const source = pendingImport ? pendingImport.source : reviewPaste;
    invalidateImport();
    transferStatus.textContent = 'Import canceled. Your current record is unchanged.';
    source.focus();
  });
  selectExport.addEventListener('click', () => {
    exportText.focus(); exportText.select();
    transferStatus.textContent = 'The complete progress text is selected. Use your device’s Copy command to keep a copy.';
  });
  download.addEventListener('click', event => {
    if (!downloadAvailable || !exportURL) {
      event.preventDefault();
      transferStatus.textContent = 'A download is unavailable. Select and copy the complete progress text instead.';
      return;
    }
    transferStatus.textContent = 'Download requested. If no file appears, select and copy the complete progress text.';
  });
  window.addEventListener('storage', event => {
    if (event.key !== key && event.key !== null) return;
    try {
      if (event.storageArea && event.storageArea !== window.localStorage) return;
      externalChange(readSaved());
    } catch (_) {
      remember = false;
      stateRevision += 1;
      invalidateImport('Device saving became unavailable. Review an import again before replacing anything.');
      showStorage('Device saving could not be checked. This page will not write again unless you explicitly enable saving. Keep an exported copy of your marks.', true);
      status.textContent = 'Your current marks remain in this page. Device saving is off.';
    }
  });
  window.addEventListener('pagehide', event => {
    invalidateImport('Import review was canceled when you left this page. Choose a file or review pasted text again.');
    if (!event.persisted) releaseExport();
  });
  window.addEventListener('pageshow', event => {
    if (!event.persisted) return;
    try { externalChange(readSaved()); }
    catch (_) {
      remember = false;
      stateRevision += 1;
      invalidateImport();
      showStorage('Device saving could not be checked after returning to this page. Your open-page marks remain temporary.', true);
      status.textContent = 'Device saving is off for this tab. Keep an exported copy of your marks.';
    }
  });

  try {
    expectedRaw = readSaved();
    if (expectedRaw === null) {
      showStorage('Nothing is saved on this device by this tool. Changes stay in this page unless you enable saving or export them.');
      status.textContent = 'Choose your next task and mark only what you want to record. Device saving starts off.';
    } else {
      try {
        state = parseRecord(expectedRaw, config);
        remember = true;
        showStorage('Your saved marks and next task were restored. Changes update this copy while Remember is checked.');
        status.textContent = 'Restored your saved marks and next task from this browser.';
      } catch (error) {
        showStorage(error.message + ' The saved copy has not been changed. Remove it to start over, or review a compatible progress file.', true);
        status.textContent = 'Saved progress was not loaded. Your open-page record starts blank and device saving is off.';
      }
    }
  } catch (_) {
    showStorage('Device saving is unavailable here. Use a progress file or copy the complete text to keep your record.', true);
    status.textContent = 'Progress can be used in this page. Device saving is off.';
  }
  root.querySelectorAll('[data-progress-enhanced]').forEach(element => { element.hidden = false; });
  fallback.hidden = true;
  root.classList.add('progress-enhanced');
  renderState();
})();
