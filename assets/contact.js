/* Contact behavior: recoverable verification, explicit acceptance, no message persistence. */
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
  const initialization = document.getElementById('contact-initialization');
  if (![fields, button, error, success, challenge, verification, retry].every(Boolean)) return;
  if (typeof window.fetch !== 'function' || typeof window.AbortController !== 'function') {
    if (initialization) initialization.textContent = 'This browser cannot securely send this form. Please try an updated browser.';
    return;
  }
  const originalLabel = button.textContent;
  let token = '';
  let tokenTime = 0;
  let widget = null;
  let widgetEpoch = 0;
  let busy = false;
  let complete = false;
  let loadAttempt = 0;
  let loadTimer = null;
  let verificationTimer = null;
  let verificationError = false;

  function verificationMessage(message, canRetry = false) {
    verification.textContent = message;
    retry.hidden = !canRetry;
  }
  function showError(message, isVerification = false) {
    verificationError = isVerification;
    error.textContent = message;
    error.hidden = false;
    error.focus();
  }
  function clearError() {
    verificationError = false;
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
  function clearVerificationTimer() {
    window.clearTimeout(verificationTimer);
    verificationTimer = null;
  }
  function watchVerification() {
    clearVerificationTimer();
    verificationTimer = window.setTimeout(() => {
      if (!complete && !token) verificationMessage('Verification is taking longer than expected. Complete any visible check or retry without leaving this page.', true);
    }, 15000);
  }
  function invalidate(message) {
    if (complete) return;
    token = '';
    tokenTime = 0;
    clearVerificationTimer();
    verificationMessage(message, true);
  }
  function discardWidget() {
    const previous = widget;
    widget = null;
    widgetEpoch += 1;
    token = '';
    tokenTime = 0;
    clearVerificationTimer();
    if (previous !== null && window.turnstile && typeof window.turnstile.remove === 'function') {
      try { window.turnstile.remove(previous); } catch (_) { /* A broken instance must not block a new one. */ }
    }
    challenge.replaceChildren();
  }
  function mountChallenge() {
    if (complete || widget !== null) return;
    const epoch = ++widgetEpoch;
    const current = () => !complete && epoch === widgetEpoch;
    try {
      const id = window.turnstile.render(challenge, {
        sitekey: challenge.dataset.sitekey,
        action: 'contact',
        theme: 'light',
        // Compact fits phone widths even after rotating or resizing an existing widget.
        size: 'compact',
        appearance: 'interaction-only',
        'response-field': false,
        'refresh-expired': 'auto',
        'refresh-timeout': 'auto',
        callback(value) {
          if (!current()) return;
          if (typeof value !== 'string' || !value.trim() || value.length > 2048) {
            invalidate('Verification did not return a usable result. Please retry verification.');
            return;
          }
          token = value;
          tokenTime = performance.now();
          clearVerificationTimer();
          verificationMessage('Anti-spam check complete.');
          if (verificationError) clearError();
        },
        'error-callback'() {
          if (current()) invalidate('The anti-spam check could not finish. Retry verification or check your connection.');
          return true;
        },
        'expired-callback'() {
          if (current()) invalidate('Verification expired. A fresh check is needed before sending.');
        },
        'timeout-callback'() {
          if (current()) invalidate('The anti-spam check timed out. Please retry verification.');
        },
        'unsupported-callback'() {
          if (current()) invalidate('This browser could not complete verification. Try an updated browser.');
        }
      });
      if (typeof id !== 'string' || !id) throw new Error('Widget initialization failed');
      widget = id;
      if (!token) watchVerification();
    } catch (_) {
      discardWidget();
      invalidate('The anti-spam check could not initialize. Please retry verification.');
    }
  }
  function loadChallenge() {
    if (complete || busy) return;
    verificationMessage('Loading the anti-spam check…');
    const attempt = ++loadAttempt;
    window.clearTimeout(loadTimer);
    loadTimer = window.setTimeout(() => {
      if (attempt === loadAttempt && widget === null && !complete) {
        invalidate('Verification is taking too long to load. Retry it without leaving this page.');
      }
    }, 15000);
    const start = () => {
      if (attempt !== loadAttempt || complete) return;
      window.clearTimeout(loadTimer);
      mountChallenge();
    };
    const ready = () => {
      if (attempt !== loadAttempt || complete) return;
      try {
        if (window.turnstile && typeof window.turnstile.ready === 'function') window.turnstile.ready(start);
        else start();
      } catch (_) {
        window.clearTimeout(loadTimer);
        invalidate('Verification could not start. Please retry verification.');
      }
    };
    if (window.turnstile && typeof window.turnstile.render === 'function') {
      ready();
      return;
    }
    const old = document.getElementById('nk-turnstile-loader');
    if (old) old.remove();
    const script = document.createElement('script');
    script.id = 'nk-turnstile-loader';
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
    script.async = true;
    script.onload = ready;
    script.onerror = () => {
      if (attempt !== loadAttempt || complete) return;
      window.clearTimeout(loadTimer);
      invalidate('The anti-spam check could not load. Check your connection or content blocker, then retry.');
    };
    document.head.appendChild(script);
  }
  function resetChallenge() {
    token = '';
    tokenTime = 0;
    if (complete) return;
    verificationMessage('Completing a fresh anti-spam check…', true);
    try {
      if (widget !== null && window.turnstile && typeof window.turnstile.reset === 'function') {
        window.turnstile.reset(widget);
        if (!token) watchVerification();
      } else {
        discardWidget();
        loadChallenge();
      }
    } catch (_) {
      discardWidget();
      loadChallenge();
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
      showError('The form could not be submitted. Copy your message before reloading the page.');
      return;
    }
    if (!token || performance.now() - tokenTime >= 270000) {
      if (token) resetChallenge();
      showError('Please let the anti-spam check finish, then select Send message again. Use Retry verification if it cannot finish.', true);
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
        method: 'POST', credentials: 'omit', redirect: 'error',
        headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
        body: JSON.stringify(payload), signal: controller.signal
      });
      if (response.redirected || response.type === 'opaqueredirect') throw new Error('Unconfirmed redirect');
      if (!response.ok) {
        const failure = new Error('Submission not confirmed');
        failure.status = response.status;
        throw failure;
      }
      complete = true;
      window.clearTimeout(loadTimer);
      discardWidget();
      form.reset();
      form.hidden = true;
      success.hidden = false;
      success.focus();
    } catch (failure) {
      if (failure.name === 'AbortError' || !failure.status || failure.status >= 500 || failure.status === 408) {
        showError('We could not confirm whether the message was accepted. Your text is still here. Check your connection before retrying; another attempt could send a duplicate.');
      } else if (failure.status === 429) {
        showError('The service is receiving too many requests. Keep this page open and try again later. Your message is still here.');
      } else {
        showError('The message was not accepted. Please complete a fresh verification check and try again. Your message is still here.');
      }
      token = '';
    } finally {
      window.clearTimeout(timer);
      setBusy(false);
      if (!complete) resetChallenge();
    }
  });
  form.noValidate = true;
  fields.disabled = false;
  if (initialization) initialization.hidden = true;
  loadChallenge();
})();
