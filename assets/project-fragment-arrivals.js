/* Keep a direct project-section arrival visible after the page settles. */
(() => {
  'use strict';
  const article = document.querySelector('.page-local-ai-review-replies');
  if (!article) return;

  let arrival = null;
  function followFragment() {
    arrival?.abort();
    arrival = null;

    const hash = location.hash;
    if (!/^#reply-[a-z-]+$/.test(hash)) return;
    const heading = document.getElementById(hash.slice(1));
    if (!heading || !article.contains(heading) ||
        !heading.matches('.section-content > h2[id]')) return;

    const pending = new AbortController();
    arrival = pending;
    const cancel = () => pending.abort();
    for (const event of ['keydown', 'pointerdown', 'wheel', 'touchstart', 'pagehide']) {
      addEventListener(event, cancel, {once: true, passive: true, signal: pending.signal});
    }

    const settle = () => document.fonts.ready.then(() => {
      if (pending.signal.aborted) return;
      const timeout = setTimeout(() => {
        if (pending.signal.aborted || location.hash !== hash) return;
        const header = document.querySelector('.site-header');
        const headerBottom = header ? Math.max(0, header.getBoundingClientRect().bottom) : 0;
        const padding = parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0;
        const desiredTop = Math.max(headerBottom + 24, padding);
        const top = heading.getBoundingClientRect().top;

        // Do not move a section that is already visible, or take keyboard focus.
        if (top < headerBottom + 12 || top > innerHeight - 48) {
          scrollTo({top: Math.max(0, scrollY + top - desiredTop), behavior: 'instant'});
        }
        cancel();
      }, 1300);
      pending.signal.addEventListener('abort', () => clearTimeout(timeout), {once: true});
    });
    if (document.readyState === 'complete') settle();
    else addEventListener('load', settle, {once: true, signal: pending.signal});
  }

  followFragment();
  addEventListener('hashchange', followFragment);
})();
