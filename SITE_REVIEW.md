# Whole-site review, October 5, 2026

## Scope

Reviewed the 14-page site, shared templates, build and catalog code, required/optional fields, contact recovery behavior, all three downloads and examples, source metadata, feeds, public-data boundaries, keyboard access, narrow layouts, reader text-spacing overrides, HTML parsing, and deployment state. The approved visual system remains in `styles.css`, unchanged by this repair. Functional CSS adjustments preserve its palette, typography, margin, seal, and editorial structure.

## Reproduced baseline failures

The previous 17 structural and 12 browser tests passed, but the expanded suite recorded seven failing checks: one homepage text-spacing overflow; two checks for an undefined verification widget ID; recovery after a widget reset throws; misleading non-delivery wording on server errors; accepting a redirected success; and no recovery explanation when the contact script is blocked.

## Repairs

The form now checks initialization results, exposes time-bounded retry guidance, and recreates failed widget instances. Callbacks from discarded instances cannot change the current verification state. The compact verification widget fits narrow layouts even after resizing. A missing local script leaves a visible recovery explanation rather than a silently disabled form. Successful verification clears only a stale verification error, not an ambiguous-delivery warning.

Redirects fail closed. A server error, timeout, or network failure preserves the message and says delivery could not be confirmed; the form never retries a submission automatically. The successful state confirms service acceptance, not inbox arrival. Required fields, optional topic/context, honeypot, endpoint, public key, and privacy limits remain unchanged.

Long text can wrap when readers override spacing, and worked examples have reading padding. Content-derived cache versions for the changed local CSS and contact script prevent future updates from reusing a fixed asset version. Regression tests bind reviewed assets and exercise the failure cases directly.

## Verification and limitations

`_tests/review_browser.py` runs HTML5 parsing on every page, reflow and text-spacing checks at seven widths, axe-core checks at phone and desktop widths, and mocked contact-failure checks. The baseline `--report-only` run records defects; normal runs fail on them. The existing tests still cover required/optional fields, expiry, duplicate prevention, request failures, offline rendering, real local HTTP pages, expanded resources, and exact downloaded bytes. A separate font-enabled run checks the selected Google Fonts families.

Automated accessibility checks are not a conformance certification. Contrast checks marked inconclusive by axe require review, particularly around antialiasing, gradients, and decorative SVG text. The main text/accent/panel palette has strong contrast; the preserved dark-surface focus color has approximately 3.23:1 contrast with its background. No real contact messages are intentionally sent by the test suites. Formspark account configuration and actual inbox delivery remain unverified.

A separate public release check compares deployed bytes with the committed pages/assets. A successful build, test run, or artifact upload is not a completed deployment. The previous cancelled Pages build was restarted at the owner's request; follow the deployment result rather than assuming queued jobs will finish.

## References

- https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/
- https://developers.cloudflare.com/turnstile/troubleshooting/client-side-errors/
- https://documentation.formspark.io/examples/ajax.html
- https://www.w3.org/TR/WCAG22/#text-spacing

The public repository itself remains public. Excluding maintenance documents from Pages does not make them confidential.
