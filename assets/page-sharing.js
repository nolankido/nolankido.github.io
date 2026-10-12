/* Explicit public-link actions only. No inputs, URLs from location, or tracking. */
(() => {
  'use strict';
  const controls = document.querySelector('.page-share-controls');
  if (!controls) return;
  const panel = controls.closest('details');
  const link = panel?.querySelector('.page-share-address a, .note-origin a');
  const status = panel?.querySelector('.page-share-status');
  const canonical = document.querySelector('link[rel="canonical"]');
  if (!link || !status || !canonical || link.href !== canonical.href) return;
  let url;
  try { url = new URL(canonical.href); } catch (_) { return; }
  if (url.origin !== 'https://nolankido.com' || url.search || url.hash) return;
  const address = url.href;
  const copy = controls.querySelector('[data-copy-page]');
  const share = controls.querySelector('[data-share-page]');
  if (!copy || !share) return;
  let busy = false;
  function selectLink(message) {
    const target = link.parentElement;
    target.setAttribute('tabindex', '-1');
    target.focus();
    try {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(link);
      selection.removeAllRanges();
      selection.addRange(range);
    } catch (_) { /* The ordinary visible link is always available. */ }
    status.textContent = message + ' The permanent link is below; copy it with your browser or save it in your notes.';
  }
  async function run(action) {
    if (busy) return;
    busy = true;
    copy.disabled = share.disabled = true;
    status.textContent = '';
    try { await action(); }
    finally { busy = false; copy.disabled = share.disabled = false; }
  }
  copy.hidden = false;
  copy.addEventListener('click', () => run(async () => {
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(address);
      status.textContent = 'Page link copied.';
    } catch (_) { selectLink('Automatic copying is unavailable.'); }
  }));
  const data = {title: document.title, url: address};
  try {
    share.hidden = !(typeof navigator.share === 'function' &&
      (typeof navigator.canShare !== 'function' || navigator.canShare(data)));
  } catch (_) { share.hidden = true; }
  share.addEventListener('click', () => run(async () => {
    try {
      await navigator.share(data);
      status.textContent = 'Sharing request accepted by your device.';
    } catch (error) {
      if (error?.name === 'AbortError') status.textContent = 'Sharing canceled. You can still copy the page link.';
      else selectLink('Sharing is unavailable on this device.');
    }
  }));
})();
