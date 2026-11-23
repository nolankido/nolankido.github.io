# SEO/GEO Turn 90: Make poker price sensitivity explorable without a Python installation

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Starting main:** `81df201eafda40c4ec37b4f8991809539b25563f` (merged Turn 89)  
**Existing canonical article:** https://nolankido.com/poker/pot-odds-workshop/  
**New noindex study tool:** https://nolankido.com/downloads/poker-pot-odds-sensitivity-lab.html

## Verified preceding release

Fresh public HTML scoped to the existing Pot Odds Workshop's `Continue studying` navigation exposed the prior Turn 89 Markdown workbook and Python verifier links. The previously ambiguous general content extraction of navigation was not itself proof that a link was missing. Both prior resources remain in the repository and keep their original names and fixed-input mathematical scope. A `target_unreachable` response from one general-purpose Python-file fetch is not a status-bearing HTTP 404 and remains inconclusive unless a direct status-bearing GET confirms otherwise.

## Reader problem solved

The original 1,648-word Turn 89 workbook is substantial, but readers without Python installation need a fast, accessible way to explore the central lesson: a mathematically correct pot price may produce different *conditional* chip outcomes when a hypothetical range estimate varies. Another canonical article or an unbounded real-hand calculator would duplicate the guide or invite claims unsupported by actual opponent evidence.

This turn adds one **fixed-scenario local interactive lab**, with no real-hand inputs, accounts, backend, AI API, paid solver, stored state or external assets. It is a teaching visualization of the existing original workbook, not a new measured player result.

## Delivered behavior

1. **River call sensitivity:** fixed 20 BB pot before 10 BB bet; P = 30, C = 10, final F = 40. Two separately labeled range sliders let the reader set illustrative equity lower/upper assumptions from 0% to 100%, default 22%-29%. The output calculates -1.20 to +1.60 BB using EV = equity × 40 - 10, notes the 25% threshold and the 0.4 BB change per equity percentage point. It sorts reversed bounds with an explicit message and says whether the interval is above, below, includes or crosses the threshold.
2. **Raise-to arithmetic:** fixed starting pot 10, hero bet 4, villain raises to 14. P = 28, C = 10, F = 38, threshold 5/19. An assumed-equity slider starts at 25% (-0.50 BB) and shows +1.40 BB at 30%. It never charges the hero's earlier 4 BB a second time.
3. **Zero-equity river bluff:** fixed 6 BB bet into 10 BB, fold-or-call opponent, zero checking and called showdown value. A fold-frequency slider starts at 40% (+0.40 BB), changes to 30% (-1.20 BB), and distinguishes the bettor's 37.5% required folds from the caller's 3/11 required equity.
4. **No JavaScript:** all four sliders are disabled until the script initializes. A visible no-JavaScript notice explains that fixed assumptions and original example formulas remain readable. Native input labels, keyboard, skip link, semantic main, live results and responsive typography remain available.
5. **Privacy and crawl control:** a standalone document with `noindex, follow`, strong inline Content Security Policy and no `fetch`, form, external JS, cookies, localStorage, analytics, model requests or network calls. Links are ordinary internal documentation links. The tool does not appear as a new indexed Article or local Finder record.

## Integration and regression coverage

- Source file: `_source/poker/pot-odds-sensitivity-lab.html`.
- Published file: `downloads/poker-pot-odds-sensitivity-lab.html`. These are byte-identical copies and must remain so.
- Existing `_source/poker/pot-odds-workshop.html` and generated `poker/pot-odds-workshop/index.html`: one new native `Continue studying` link, with all other original workshop markup unchanged. No article or sitemap metadata change.
- `_scripts/check_live.py`: register the standalone HTML exact-byte public GET target.
- `_tests/test_turn63_public_html_downloads.py`: extend the strict public HTML download inventory from four resources to five, retaining noindex, HTML5 and exact-byte safeguards.
- `_tests/test_turn90_offline_sensitivity_lab.py`: ten standard-library tests for source parity, input labels, accessibility, CSP, exact fictional math, original workshop navigation, sitemap/search exclusions, negative controls and manual-runner registration.
- `_tests/pot_odds_sensitivity_browser.py`: separate local browser suite, auto-discovered by existing `_scripts/local_release_checks.py --browser`.
- `AGENTS.md`: preserve the owner restriction on no GitHub Actions, no scheduled bots and no remote testing dependency.

## Actually executed

A local Chromium process rendered the final HTML using `page.set_content` at **320, 390, 768 and 1280 CSS pixels**. Each width showed:

- Default 22%-29% river interval with -1.20 to +1.60 BB.
- Reversed bounds 35% and 15%, correctly sorted to 15%-35% with -4.00 to +4.00 BB.
- Raise slider 25% to 30%, yielding +1.40 BB.
- Bluff fold slider 40% to 30%, yielding -1.20 BB.
- No horizontal overflow, no JavaScript page errors and zero outbound requests.

A separate no-JavaScript browser context kept the sliders inactive, displayed the fallback guidance, and retained the default model summary.

Those checks ran against the exact local HTML subsequently submitted as the GitHub source/public HTML. They demonstrate the tested document's functionality, not the complete website build or public serving. The repository's full Python unit suite, HTML5 parser, internal link checker, 301-entry Finder parity, local release runner and source-to-public byte comparison have not been run from a complete checkout because the container cannot resolve the public GitHub host.

## Remaining independent release acceptance

```powershell
py -3 -m unittest discover -s _tests -p test_turn90_offline_sensitivity_lab.py -v
py -3 -m unittest discover -s _tests -p test_turn63_public_html_downloads.py -v
py -3 -m unittest discover -s _tests -p test_turn89_pot_odds_sensitivity.py -v
py -3 _tests/pot_odds_sensitivity_browser.py
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope all --only /poker/pot-odds-workshop/ --only /downloads/poker-pot-odds-sensitivity-lab.html --only /downloads/poker-pot-odds-sensitivity-workbook.md --only /downloads/poker-pot-odds-sensitivity-verify.py --attempts 8 --interval 15 --workers 1
```

**Next meaningful priority:** Verify deployment and exact serving of the HTML page, inspect browser behavior on the real URL at 320px with keyboard, then use first-party search/reader data when available to select the next substantive educational addition. Do not report an SEO ranking, GEO citation, poker profitability or solver-validation gain on the basis of this release.
