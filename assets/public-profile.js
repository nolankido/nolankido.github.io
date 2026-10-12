/* Public-text copying only. No requests, input collection, storage, or analytics. */
(() => {
  'use strict';
  const allowed = new Map([
    ['profile-short-text', 'Short biography'],
    ['profile-long-text', 'Longer biography'],
    ['profile-site-url', 'Website address']
  ]);
  const status = document.getElementById('profile-copy-status');
  if (!status) return;
  let latest = 0;
  for (const button of document.querySelectorAll('button[data-profile-copy]')) {
    const id = button.getAttribute('data-profile-copy');
    const target = document.getElementById(id);
    if (!allowed.has(id) || !target) continue;
    button.hidden = false;
    button.addEventListener('click', async () => {
      const request = ++latest;
      const text = target.textContent.trim();
      status.textContent = '';
      button.disabled = true;
      try {
        if (!navigator.clipboard || typeof navigator.clipboard.writeText !== 'function') {
          throw new Error('Clipboard unavailable');
        }
        await navigator.clipboard.writeText(text);
        if (request === latest) status.textContent = allowed.get(id) + ' copied.';
      } catch (_) {
        if (request === latest) {
          target.focus();
          const selection = window.getSelection();
          if (selection) {
            const range = document.createRange();
            range.selectNodeContents(target);
            selection.removeAllRanges();
            selection.addRange(range);
          }
          status.textContent = 'Automatic copy is unavailable. Select and copy the visible text, or use the text download.';
        }
      } finally {
        button.disabled = false;
      }
    });
  }
})();
