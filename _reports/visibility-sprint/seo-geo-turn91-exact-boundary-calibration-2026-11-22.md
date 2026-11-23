# SEO/GEO Turn 91: make poker decision boundaries exact, reachable and understandable

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Base GitHub main:** `d0751beec8ca71871e05e9c6b18943326d2cec0d` (merged Turn 90)  
**Existing URL:** `https://nolankido.com/downloads/poker-pot-odds-sensitivity-lab.html`  
**Status before this turn:** the lab was confirmed accessible on the live site and already linked from the canonical Pot Odds Workshop.

## Specific user problem

Turn 90 correctly represented fixed fictional pot and bet quantities, but the pure-bluff fold-frequency slider offered only integer percentage points while its exact break-even rate was **37.5%**. Readers could see the mathematically correct threshold in the label but could not reach it interactively. In the raise-to scenario, the exact threshold is **5/19 (about 26.3158%)**. The whole-point slider can only show the adjacent inputs, so the lab should say so explicitly rather than rounding an invalid zero-EV scenario.

## Completed improvement

Edit the existing source and output HTML as **identical files**, without creating a new indexable URL.

1. Change only the pure-bluff fold slider to `step="0.5"`. Keep the other three existing integer-step sliders and all originally published defaults.
2. Add `#boundary-drill`, a printable, fully explained three-case exercise below the current models and before the existing conclusion:
   - **River call:** At 24%, 25%, 26% equity, the conditional EV is **-0.40, 0, +0.40 BB**, respectively. One button loads the 24% to 26% assumed equity band in the original two controls.
   - **Raise to 14 BB:** At 26% equity the call EV is **-0.12 BB**, at exact **5/19** it is **0 BB**, and at 27% it is **+0.26 BB**. Two buttons load the adjacent 26% and 27% cases; the exact fraction is a separate reference and **cannot** be selected by the 1-point slider.
   - **Pure bluff:** At 37%, 37.5%, 38% folds the zero-equity bluff EV is **-0.08, 0, +0.08 BB**. The third scenario button loads exactly **37.5%** and the half-point slider can move to 38% with one ArrowRight keypress.
3. Buttons are `type="button"`, disabled until the existing inline script attaches listeners, and have `aria-controls` descriptions. When clicked, they update only local fixed-scenario ranges, call the original `render()`, and move focus to the affected slider for continued keyboard investigation.
4. The static three-case proof remains readable when scripts are disabled; preset buttons remain disabled. Printed output contains the facts and removes interactive controls.
5. Preserve all existing mathematical scenarios, source statements, CSP, noindex, four original sliders, three live result announcements, private/no-network policy, navigational destinations and old source/public metadata. No new sitemap page, search entry, tracking, requests, cookie or user hand entry.

## Executed checks

**Exact artifact provenance:** A complete local copy of Turn 90's GitHub HTML was verified to have the same Git blob SHA `5aa11f4a04667e58d8e46fa16419b9d387876bee` after removing only a redundant local trailing newline. The revised local file has Git blob SHA `cef81447a1b06732c4b54d0fc9a808cefb6fa724`. GitHub returned that **exact new blob SHA for both** `_source/poker/pot-odds-sensitivity-lab.html` and `downloads/poker-pot-odds-sensitivity-lab.html`. The tested local artifact and committed remote files are byte-identical.

**Local browser:** A Chromium/Playwright smoke script ran on the exact revised HTML at **320, 390, 768 and 1280 px**, all passing original defaults, all four presets, 37.5% exact zero and ArrowRight to 38%, updated result text, keyboard focus, no overflow, print control suppression, zero external requests and zero script errors. A separate JavaScript-disabled browser context confirmed all buttons/ranges stay disabled, the fallback appears and the static proof is readable.

**Local unit fixture:** Seven new unit tests ran and passed against source/output copies of the exact revised HTML: source parity, unchanged original scenarios, three independently computed exact Fraction boundary sets, accessible control/print semantics, and negative mutations of source safety constraints. Three further new integration tests are authored but require a full site checkout.

**Existing safeguards updated:** The Turn 90 standalone HTML safety test now permits `step=0.5` **only** for the bluff slider and preserves four controls/no-JS disabled starts. The original complete-checkout Playwright suite is extended with real preset, keyboard and no-JS assertions. The new ten-test module is registered in the manual-only local release runner.

## Full release validation still pending

The complete Python site generator, full repository test suite, integrated original Playwright suite, HTML5 audit, site search snapshot, 320px broader site audit and exact source-to-live HTTP-byte comparison have **not** run in a full checkout. The new HTML is merged only after PR review; public deployment cannot be presumed from a successful merge.

In a complete local checkout:

```powershell
py -3 -m unittest discover -s _tests -p test_turn90_offline_sensitivity_lab.py -v
py -3 -m unittest discover -s _tests -p test_turn91_threshold_boundary_drill.py -v
py -3 _tests/pot_odds_sensitivity_browser.py
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope all --only /downloads/poker-pot-odds-sensitivity-lab.html --only /poker/pot-odds-workshop/ --attempts 8 --interval 15 --workers 1
```

## Next useful improvement

Verify this revised version is publicly deployed and its exact bytes match, then prioritize a reader task with documented error patterns rather than adding more formulas to the same three fictional scenarios. Do not claim solver-backed strategy, player population tendencies, improved search positions, sales or AI assistant citations from this static exercise.
