# Incremental upgrade payback: a downloadable, reproducible comparison

Prepared: November 13, 2026, Las Vegas time

## Why this turn

The published calculator gives a reader a useful result but, until now, no
convenient way to preserve the exact hypothetical inputs, calculated final
balances, affordability decisions and formulas. A blank worksheet exists,
but copying the screen manually introduces transcription errors and separates
the outputs from the assumptions that created them.

## Improvement

- After a successful comparison, offer a filled-in, deterministic Markdown
  record. The record includes all five inputs, a formula for each purchase
  path, three results with unavailable purchases clearly labeled, the
  highest-balance path, conditional payback counts, an affordable-purchase
  difference and its crossing condition when applicable.
- Place the same record in a labeled, read-only text area under a native
  expandable section. A reader can copy it if browser downloads are blocked,
  unsupported or undesirable.
- Build the file locally from a browser Blob URL with a native download link.
  The browser holds only one current Blob URL; recalculation, edits and reset
  revoke the previous URL and discard the old report.
- Any change to the form inputs invalidates the visible result immediately,
  so the reader cannot accidentally download results for earlier values.
- Keep the old blank worksheet for use without JavaScript. Explain the
  difference between the blank and filled-in versions in the guide.

## Content and privacy boundaries

- The result remains a *synthetic single-purchase arithmetic comparison*,
  not evidence of player behavior, retention or game quality. No personal
  details or timestamps enter the generated record.
- Files are downloaded only when the reader follows the native link. The
  browser-local calculation uses no account, remote request, persistent
  storage, tracking or paid service.
- Preserve the 2026-11-13 article publication date, canonical route,
  existing formulas, metadata, feeds and worksheet download URL. No private
  game details, unverified sources or author credentials were introduced.
- No GitHub Actions, other recurring jobs or paid integrations were added.

## Tests and verification

- `node _tests/incremental_upgrade_payback_smoke.cjs`: PASS. Checks exact
  record values in the 20/60-tap examples, ties, unaffordable paths,
  negative crossing thresholds, stale-result invalidation, Blob creation,
  URL revocation and read-only fallback when Blob is unavailable.
- `python -m unittest _tests.test_incremental_upgrade_payback -v`: PASS,
  5 tests, including source and generated-page consistency.
- `python _scripts/build.py --check`: PASS, 238 generated files, zero drift.
- `python _scripts/local_release_checks.py`: PASS, 89/89 local groups.
  Link audit: 14,422 internal links across 214 HTML pages, zero issues.
  Search metadata: 209 public entries and 118 Article records, zero errors.
- `_tests/incremental_upgrade_payback_browser.py` is an added optional
  offline Chromium regression that attempts actual native `.md` downloads
  at 320, 390, 768 and 1440 pixels. **It did not run here**: the bundled
  Playwright Chromium binary is missing, and the system Chromium process
  was blocked by the execution environment's socket restriction. This is
  not a passing browser test. A public-page post-deployment browser check
  and exact deployed-byte verification should be recorded separately.
