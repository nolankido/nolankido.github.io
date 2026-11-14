# Incremental upgrade calculator: an example-first mobile interaction

Prepared: November 13, 2026, Las Vegas time

## What prompted this improvement

The previously published upgrade-payback guide passed its generated-site and
JavaScript tests. A direct browser inspection of the live page then showed a
specific usability issue at a narrow mobile width: submitting the form put
the result heading near the lower edge of the visible screen, so the result
needed additional scrolling. A 5-spark test also showed that the summary
presented conditional payback counts and a two-purchase threshold even when
neither upgrade was affordable. Those statements were mathematically
conditional but easy to misunderstand.

## Changes

- Placed a prominent in-page calculator link immediately after the first
  explanatory paragraph, so a reader seeking a tool can skip the longer
  introduction.
- Added two ready-made scenarios inside the calculator: 20 planned taps and
  60 planned taps. Each restores the same 25-spark starting bank, 60 visible
  seconds and first-purchase upgrade prices, then computes the outcome.
- After submission or a preset click, focus moves to the result heading
  without an intermediate browser scroll, and the result panel scrolls to
  the start with an offset for the sticky site navigation. The movement is
  immediate, without a forced animation.
- Clarified that upgrade payback only applies when the item can be
  purchased from the initial balance. If either upgrade is unaffordable,
  the two-upgrade crossing threshold is omitted from the dynamic message.
- If the crossing threshold is negative, the page explains that routine
  outperforms pencil for every allowed nonnegative active duration. This
  concerns only those two purchase paths, not whether either beats no buy.

## Contracts and safety

- The core arithmetic, prices, source links, publication date, canonical
  URL, worksheet and site information architecture remain unchanged.
- Native labeled integer inputs, `aria-live` feedback, invalid-field focus,
  keyboard focus outlines, and an accessible JavaScript-free reading path
  are preserved.
- The controls use no account, network fetch, persistent storage or analytics.
  No private games, player tests, design successes or SEO outcomes are claimed.
- The JavaScript smoke test exercises both one-tap examples, mobile result
  scroll behavior, inaccessible purchases, invalid inputs and recovery.
  The page contract checks that the controls and styling are present and
  that the generated script/style versions match their bytes.

## Release verification

- `node _tests/incremental_upgrade_payback_smoke.cjs`: PASS, including
  both presets, the result scroll request, reset, validation, affordability
  and negative-threshold cases.
- `python _scripts/build.py --check`: 238 generated files, zero drift.
- `python _scripts/local_release_checks.py`: **89/89 groups passed**.
- `python _scripts/check_internal_links.py` from that gate: 14,421 links
  across 214 public HTML pages, zero issues.
- `python _scripts/check_search.py` from that gate: 209 distinct public
  page metadata entries, 209 sitemap URLs and 118 Article records, no errors.
- `python _tests/check_html5.py` from that gate: all 214 HTML pages parsed.

The manual baseline browser check was performed at a 375-pixel viewport; it
was not a comprehensive device or assistive-technology study. Live deployment
bytes and any post-release visual check must be recorded in the handoff rather
than presented here as completed before publication. No GitHub Actions,
scheduled services or paid integrations were used.
