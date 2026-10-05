/* Contact behavior is independent of the visual design. No secrets or message logging. */
(() => {
  'use strict';
  const form = document.getElementById('contact-form');
  if (!form) return;
  const fields = document.getElementById('contact-fields');
  const button = document.getElementById('contact-submit');
  const error = document.getElementById('form-error');
  const success = document.getElementById('form-success');
  const challenge = document.getElementById('contact-challenge');
  const verification = document.getElementById('verification-status');
  const retry = document.getElementById('verification-retry');
  const originalLabel = button.textContent;
  let token = '';
  let tokenTime = 0;
  let widget = null;
  let busy = false;
  let complete = false;
  let loadAttempt = 0;

  function verificationMessage(message, canRetry = false) {
    verification.textContent = message;
    retry.hidden = !canRetry;
  }
  function showError(message) {
    error.textContent = message;
    error.hidden = false;
    error.focus();
  }
  function clearError() {
    error.hidden = true;
    error.textContent = '';
  }
  function setBusy(value) {
    busy = value;
    button.disabled = value;
    fields.disabled = value;
    form.setAttribute('aria-busy', String(value));
    button.textContent = value ? 'Sending…' : originalLabel;
  }
  function invalidate(message) {
    token = '';
    tokenTime = 0;
    verificationMessage(message, true);
  }
  function mountChallenge() {
    if (complete || widget !== null) return;
    try {
      widget = window.turnstile.render(challenge, {
        sitekey: challenge.dataset.sitekey,
        action: 'contact',
        theme: 'light',
        size: challenge.clientWidth < 300 ? 'compact' : 'flexible',
        appearance: 'interaction-only',
        'response-field': false,
        'refresh-expired': 'auto',
        'refresh-timeout': 'auto',
        callback(value) {
          token = value;
          tokenTime = performance.now();
          verificationMessage('Anti-spam check complete.');
        },
        'error-callback'() {
          invalidate('The anti-spam check could not finish. Retry verification or check your connection.');
          return true;
        },
        'expired-callback'() {
          invalidate('Verification expired. A fresh check is needed before sending.');
        },
        'timeout-callback'() {
          invalidate('The anti-spam check timed out. Please retry verification.');
        },
        'unsupported-callback'() {
          invalidate('This browser could not complete verification. Try an updated browser.');
        }
      });
    } catch (_) {
      widget = null;
      invalidate('The anti-spam check could not load. Please retry verification.');
    }
  }
  function loadChallenge() {
    if (complete || busy) return;
    verificationMessage('Loading the anti-spam check…');
    if (window.turnstile && typeof window.turnstile.render === 'function') {
      mountChallenge();
      return;
    }
    const attempt = ++loadAttempt;
    const old = document.getElementById('nk-turnstile-loader');
    if (old) old.remove();
    const script = document.createElement('script');
    script.id = 'nk-turnstile-loader';
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
    script.async = true;
    const timer = window.setTimeout(() => {
      if (attempt === loadAttempt && !window.turnstile) {
        invalidate('Verification is taking too long to load. Retry it without leaving this page.');
      }
    }, 15000);
    script.onload = () => {
      window.clearTimeout(timer);
      if (attempt === loadAttempt) mountChallenge();
    };
    script.onerror = () => {
      window.clearTimeout(timer);
      if (attempt === loadAttempt) invalidate('The anti-spam check could not load. Check your connection or content blocker, then retry.');
    };
    document.head.appendChild(script);
  }
  function resetChallenge() {
    token = '';
    tokenTime = 0;
    if (complete) return;
    verificationMessage('Completing a fresh anti-spam check…', true);
    try {
      if (widget !== null && window.turnstile) window.turnstile.reset(widget);
      else loadChallenge();
    } catch (_) {
      invalidate('Please retry verification. Your message is still in the form.');
    }
  }
  retry.addEventListener('click', () => {
    if (busy || complete) return;
    if (widget === null) loadChallenge();
    else resetChallenge();
  });
  form.addEventListener('input', event => {
    if (typeof event.target.setCustomValidity === 'function') event.target.setCustomValidity('');
  });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy || complete) return;
    clearError();
    for (const name of ['name', 'email', 'message']) {
      const input = form.elements.namedItem(name);
      input.setCustomValidity(input.value.trim() ? '' : 'Please complete this field.');
    }
    if (!form.reportValidity()) return;
    if (form.elements.namedItem('_honeypot').checked) {
      showError('The form could not be submitted. Please reload the page and try again.');
      return;
    }
    // Keep Send usable on this return path. The receiving service validates the token.
    if (!token || performance.now() - tokenTime >= 270000) {
      if (token) resetChallenge();
      showError('Please let the anti-spam check finish, then select Send message again. Use Retry verification if it cannot finish.');
      return;
    }
    const value = name => form.elements.namedItem(name).value.trim();
    const payload = {
      name: value('name'), email: value('email'), reason: value('reason'),
      context: value('context'), message: value('message'),
      'cf-turnstile-response': token,
      _email: {from: 'Nolan Kido Website', subject: '[NK Contact] New website message', template: {title: true, footer: true}}
    };
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 15000);
    setBusy(true);
    try {
      const response = await fetch(form.action, {
        method: 'POST', credentials: 'omit',
        headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
        body: JSON.stringify(payload), signal: controller.signal
      });
      if (!response.ok) {
        const failure = new Error('Submission rejected');
        failure.status = response.status;
        throw failure;
      }
      complete = true;
      form.reset();
      form.hidden = true;
      success.hidden = false;
      success.focus();
      if (widget !== null && window.turnstile) {
        try { window.turnstile.remove(widget); } catch (_) { /* Submission already accepted. */ }
      }
      token = '';
    } catch (failure) {
      if (failure.name === 'AbortError' || !failure.status) {
        showError('We could not confirm whether the message was accepted. Your text is still here. Check your connection before retrying; another attempt could send a duplicate.');
      } else if (failure.status === 429) {
        showError('The service is receiving too many requests. Keep this page open and try again later. Your message is still here.');
      } else {
        showError('The message was not accepted. Please complete a fresh verification check and try again. Your message is still here.');
      }
      // A token can be consumed even when a request fails. Never automatically repost.
      token = '';
    } finally {
      window.clearTimeout(timer);
      setBusy(false);
      if (!complete) resetChallenge();
    }
  });
  // Prevent a misleading no-JavaScript submission, but use native field validation once active.
  form.noValidate = true;
  fields.disabled = false;
  loadChallenge();
})();
