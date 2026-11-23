# SEO/GEO Turn 92: private, copyable fixed-scenario study record in the Pot Odds Lab

**Date:** November 22, 2026 (Pacific/Honolulu)  
**GitHub base:** `bace38e4e0edcaececdccbf78fb0b57d2f669b70` (merged Turn 91)  
**Existing browser tool:** `https://nolankido.com/downloads/poker-pot-odds-sensitivity-lab.html`  
**Indexed parent:** `https://nolankido.com/poker/pot-odds-workshop/`

## Reader problem and bounded solution

The public, original Turn 91 boundary drill was verified live at the start of this turn: its `#boundary-drill` section and bluff slider `step=0.5` both served on the public site. The tool allowed local exploration of a fictional call, raise and pure bluff but had no direct way to carry forward the exact assumptions used in an experiment. Readers who remembered an EV figure without its price and assumed opponent percentage could easily mistake conditional arithmetic for supported strategy.

Extend **the existing offline HTML only** with `#study-record-panel`, a five-section private study record in a native labelled `<textarea readonly>`. Its default static text includes all fixed costs and pots, the four slider defaults, the correct three conditional EV outputs, missing opponent evidence, and the fictional model restrictions. When the original `render()` executes, it reconstructs the complete record from the current four slider values, preserving the user's raw lower/upper ordering while displaying the properly sorted interval. The existing boundary preset buttons call that same function, so the record also reflects preset changes. No extra math model, real hand collection, or new indexed article is introduced.

Add one disabled-until-JavaScript `type=button` control, **Select full record to copy**. On a user click it focuses the read-only textarea and selects all text. The user then chooses their operating system's ordinary Copy action. No automatic clipboard access or claim that the note was saved is made. With JavaScript off, the static record remains readable and the action button stays disabled. The existing printing experience still includes the three displayed model results, while the select button is hidden.

This is an after-play, three-fictional-model exercise. It is not a real range estimate, actual solver output, tournament payout analysis, verified equity range, or claim of improved player outcomes.

## Actual code changes

1. Edit `_source/poker/pot-odds-sensitivity-lab.html` and `downloads/poker-pot-odds-sensitivity-lab.html` byte-for-byte identically. A new note section and read-only textarea reflect one browser-local function, and CSS handles narrow layouts, focus, text wrapping, and print.
2. Update the previous Turn 90 source HTML test to require the original four slider labels **plus one** read-only note label, without permitting new range inputs.
3. Update the previous Turn 91 threshold test to distinguish the unchanged four preset buttons from the separate one-click Select button. Preserve preset disabled state, CSP, noindex and exact arithmetic.
4. Extend `_tests/pot_odds_sensitivity_browser.py` with actual record-update, copy-select, keyboard, print, mobile and no-JS assertions. The existing runner still runs browser tests only on explicit `--browser`.
5. Add `_tests/test_turn92_private_study_record.py` with **eleven checks**, eight standalone and three site integration; register it in `_scripts/local_release_checks.py`.
6. Append source ownership and evidence policy to `AGENTS.md`. Do not add a new public URL, canonicals, sitemap entry, dependency, external service or GitHub Actions.

## Executed verification, with scope

A local Chromium/Playwright smoke ran the **exact** new HTML at 320, 390, 768 and 1280 pixel widths. Each passed initial note consistency, reversed lower/upper bounds, original preset interactions, raising-equity updates, exact 37.5% bluff threshold and ArrowRight to 38%, native full-text selection after an explicit click, absence of horizontal overflow, print hiding the select button, and **zero external requests / zero script errors**. In a separate no-JavaScript browser context, controls remained disabled and the original fictional note was readable.

The **eight standalone unit tests** ran and passed in an isolated exact-source/output fixture with the candidate HTML. They include original chip arithmetic verified with `Fraction`, required static disclosures, unique/read-only/labelled note controls, no automatic clipboard or storage path, render source wiring and deliberate privacy/fact mutation rejection. **The remaining three integration checks have been authored but have not run**, because a matching complete checkout is unavailable to the local runtime.

An authenticated GitHub write response recorded `86529a8849610e23ef45a516f3db2666b1282168` as the exact Git blob SHA of **both** authored source and public HTML, matching the tested local file. The regression test file was also read back with Git blob SHA `cb07b85a15ce8d748edb583a70c3e2086ddda103`, matching the locally executed test source. Neither source parity nor local browser passes assert public exact-byte deployment or search growth.

## Still pending in a complete checkout

```powershell
py -3 -m unittest discover -s _tests -p test_turn90_offline_sensitivity_lab.py -v
py -3 -m unittest discover -s _tests -p test_turn91_threshold_boundary_drill.py -v
py -3 -m unittest discover -s _tests -p test_turn92_private_study_record.py -v
py -3 _tests/pot_odds_sensitivity_browser.py
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope all --only /downloads/poker-pot-odds-sensitivity-lab.html --only /poker/pot-odds-workshop/ --attempts 8 --interval 15 --workers 1
```

A fresh public-site check after merge must verify `#study-record-panel` and the select control appear. This is *presence verification*, not an authenticated source-byte equality receipt. Do not invent first-party search impressions, rankings, AI citations, solver-backed ranges or performance from this work.

## Next priority

Complete the integrated release checks and live exact-byte receipt before adding more interactive features. Then select a new teaching improvement from real reader questions or first-party search measurements, prioritizing reader comprehension and genuine evidence over another layer of navigation.
