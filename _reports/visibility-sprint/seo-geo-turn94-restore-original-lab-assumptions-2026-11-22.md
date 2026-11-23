# SEO/GEO Turn 94: restore original fictional pot-odds settings in one action

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Base branch:** main at `7ae21c0d00336c81708ab36a930302431815dc3f` (merged Turn 93)  
**Existing canonical learning article:** `/poker/pot-odds-workshop/`  
**Existing standalone noindex lab:** `/downloads/poker-pot-odds-sensitivity-lab.html`

## Reader gap and decision

Turn 93's full-length print record was confirmed live at the start of this turn, including the `#study-print` mirror and unverified-assumption warning. The browser lab supports four original probability sliders, four boundary drill presets, a copyable read-only note and a separate full-length print copy.

After changing all controls, returning to the originally published set of fictional assumptions required manually adjusting all four sliders. This is a reproducibility problem, especially when a reader wants to compare a boundary scenario against the initial example.

## Implemented on existing lab, without another article

Add **one** initially disabled `type="button"`, `#study-reset`, labelled **Restore original example settings**, beside the existing copy-selection button in `.study-actions`. The button does not submit or copy anything. When the original inline script has initialized, a direct user click:

1. Restores `#river-low`, `#river-high`, `#raise-equity` and `#bluff-fold` from their *actual HTML defaultValue*, rather than introducing duplicate or potentially stale hardcoded values.
2. Calls the existing `render()` once, restoring river EV -1.20 to +1.60 BB, raise-to call EV -0.50 BB and pure bluff EV +0.40 BB, with original assumed percentage values 22%, 29%, 25% and 40%.
3. Regenerates both the read-only private study note and the full print mirror from the same render path.
4. Moves keyboard focus to the first river slider so the next experiment can start immediately.

The two study actions wrap on narrow screens, each retaining a native button and minimum 44-pixel touch height. They are hidden in print while the full note remains printable. With JavaScript off the reset remains disabled and the static fictional content is unaffected.

No additional slider, public destination, canonical Article, index entry, sitemap record, network connection, real-hand field, live opponent estimate, persistent storage or automatic clipboard access. The offline lab remains subject to its original strict CSP and noindex.

## Changes and test coverage

- Update `_source/poker/pot-odds-sensitivity-lab.html` and `downloads/poker-pot-odds-sensitivity-lab.html` with precisely matching HTML. The tested local file and the two authenticated GitHub uploaded files have the same Git blob SHA: `cb466935dfc3f13fffa8113ef2d507b17c819c2d`.
- Amend Turn 91's static test to enforce **four** unchanged boundary presets plus **two** controlled study-action buttons.
- Amend Turn 92's static test to enforce **six** total buttons, including an initially disabled reset, and exactly four original slider inputs.
- Extend the existing Playwright browser test to restore all four baseline values, confirm the three displayed results, original copyable/print notes and keyboard focus, and confirm the reset stays disabled without JS.
- Add `_tests/test_turn94_restore_lab_baseline.py` containing **11 tests** (eight standalone and three integration), register it with `_scripts/local_release_checks.py`; update `AGENTS.md` with no-new-Actions and evidence boundaries.

## Actual executed verification

The exact HTML artifact was tested in a local Chromium browser at **320, 390, 768 and 1280 pixels**. Each viewport passed: original controls, changed/reversed equity bands, boundary presets, exact 37.5% bluff case, user selection, reset, restored outputs, identical copyable/print record, focus on first slider, print hiding both actions and inclusion of the full warning, no horizontal overflow, zero observed external requests and zero page script errors. A separate **no-JavaScript** run confirmed the reset/select/presets were disabled and the printable record remained intact.

The exact new Turn 94 Python test file, Git blob SHA `4ab3408aa2fe3c160a3857d0eb02783950de061f`, was executed in an isolated fixture together with the updated original Turn 92 and unchanged Turn 93 standalone classes. **24 standalone tests passed:** eight each from Turns 92, 93 and 94. The remaining three Turn 94 site-integrated tests were **authored but not executed**, and the full original Playwright suite and the full repository test suite were not available in this environment.

GitHub returned the matching new HTML blob SHA for both source and public HTML files. This proves commit provenance against the locally tested HTML, **not** that the live website is already serving its new bytes.

## Full acceptance in a matching complete checkout

```powershell
py -3 -m unittest discover -s _tests -p test_turn91_threshold_boundary_drill.py -v
py -3 -m unittest discover -s _tests -p test_turn92_private_study_record.py -v
py -3 -m unittest discover -s _tests -p test_turn93_full_print_record.py -v
py -3 -m unittest discover -s _tests -p test_turn94_restore_lab_baseline.py -v
py -3 _tests/pot_odds_sensitivity_browser.py
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope all --only /downloads/poker-pot-odds-sensitivity-lab.html --only /poker/pot-odds-workshop/ --attempts 8 --interval 15 --workers 1
```

A public read of `#study-reset` after merge can confirm deploy presence. Exact byte parity still requires an actual source-to-live GET comparison from a complete checkout with network access. No Search Console clicks, impressions, ranking, AI assistant citations or real player results are claimed.

## Next sprint priority

Verify the new lab release, run integrated checks and prioritize broader original reader needs using observed search questions or first-party evidence. Do not keep adding cosmetic controls to this completed three-scenario lab without a demonstrated comprehension or accessibility gap.
