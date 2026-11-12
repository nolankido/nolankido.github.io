/* Keep a direct project-section arrival visible after the page settles. */
(() => {
  'use strict';
  const cases = [
    {article: document.querySelector('.page-local-ai-review-replies'), fragment: /^#reply-[a-z-]+$/},
    {article: document.querySelector('.page-ai-book-continuity-checker'), fragment: /^#continuity-[a-z-]+$/},
    {article: document.querySelector('.page-dinner-on-time'), fragment: /^#dinner-[a-z-]+$/},
  ];
  const active = cases.find(({article}) => article);
  if (!active) return;

  let arrival = null;
  function followFragment() {
    arrival?.abort();
    arrival = null;

    const hash = location.hash;
    if (!active.fragment.test(hash)) return;
    const heading = document.getElementById(hash.slice(1));
    if (!heading || !active.article.contains(heading) ||
        !heading.matches('.section-content > h2[id]')) return;

    const pending = new AbortController();
    arrival = pending;
    const cancel = () => pending.abort();
    for (const event of ['keydown', 'pointerdown', 'wheel', 'touchstart', 'pagehide']) {
      addEventListener(event, cancel, {once: true, passive: true, signal: pending.signal});
    }

    const settle = () => document.fonts.ready.then(() => {
      if (pending.signal.aborted) return;
      const correct = () => {
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
      };

      // Correct a hidden arrival on the next frame, then recheck late shifts.
      const earlyFrame = requestAnimationFrame(correct);
      const timeout = setTimeout(() => {
        correct();
        cancel();
      }, 1300);
      pending.signal.addEventListener('abort', () => {
        cancelAnimationFrame(earlyFrame);
        clearTimeout(timeout);
      }, {once: true});
    });
    if (document.readyState === 'complete') settle();
    else addEventListener('load', settle, {once: true, signal: pending.signal});
  }

  followFragment();
  addEventListener('hashchange', followFragment);
})();
