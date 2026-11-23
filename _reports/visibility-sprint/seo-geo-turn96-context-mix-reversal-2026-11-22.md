# SEO/GEO Turn 96: make a poker opponent-frequency aggregation reversal reproducible

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Base main SHA:** `e10b9b251503a2e33652d2adbb886d90517e6a74` (merged Turn 95)  
**Existing indexed article:** `/poker/poker-under-uncertainty/#frequencies`  
**Existing free, uncatalogued resources:** `downloads/poker-opponent-frequency-evidence-workbook.md` and `downloads/poker-opponent-frequency-verify.py`.

## Prior release and choice

The prior Turn 95 guide navigation was independently observed on the live site at the start of this turn. The worksheet was accessible through that guide. A direct browser fetch of its Python download was inconclusive, so the fact that a link is published must not be confused with an executed remote Python program.

The reader can now identify a valid opportunity denominator and compare small-sample statistical bounds. A remaining conceptual failure mode is assuming that an *overall* percentage will necessarily order two people or apply to a particular position. More action counts alone do not solve a mismatch in the opportunity mix. This turn expands the existing original worksheet instead of publishing another overlapping Article or adding a new interface control.

## Exact invented example

| Conditional eligible opportunity set | Fictional A | Fictional B |
| --- | --- | --- |
| Earlier-position group | 3 / 30 = 10% | 1 / 20 = 5% |
| Later-position group | 8 / 20 = 40% | 21 / 60 = 35% |
| Pooled observed rate | 11 / 50 = 22% | 22 / 80 = 27.5% |
| Hypothetical equal 50/50 position-group weighting | (10 + 40) / 2 = 25% | (5 + 35) / 2 = 20% |

A has the greater **observed** rate within **both** groups, but B has the greater pooled rate. This is a genuine constructed Simpson's paradox: the two players faced different proportions of the groups. It is neither proof of a true difference, a causal position effect nor an estimate of actual players' response distributions.

The equal 50/50 comparison is an optional, explicitly hypothetical *standardization*, not the original pooled rate or a recommended target distribution. None of the small counts independently establishes a true future frequency.

## Changes to previously published original material

1. **Workbook:** Add the fully specified new group-mix exercise as section 6, move the blank source-evidence worksheet to section 7, and move the prior answer key to section 8. Add one eighth practice question and answer describing the reversal, the denominators, the effect of group weighting, and the limits on inference. Preserve original confidence and credible interval lessons; repair literal command code formatting in the existing answer section.
2. **Fixed Python verifier:** Add `opportunity_mix_report()` to the existing standard-library-only script. It counts earlier, later, pooled and equal-position-mix probabilities with `fractions.Fraction`, validates that the reversal genuinely occurs, includes a new `position_mix_reversal` record in the existing `--json` report and extends `--self-test` exact assertions. Keep prior report keys, CLI behavior and strict invalid-count rejection.
3. **Tests:** Add ten regression methods in `_tests/test_turn96_position_mix_reversal.py`, with seven substantive standalone methods and three full-site integration safeguards. Register the module in the existing no-Actions manual runner and record the new data boundaries in `AGENTS.md`.
4. **Scope:** Change no canonical site page, Poker Finder JSON, article metadata, sitemap record, automated deployment task, user data collection, paid service or URL. The two existing downloads keep their previous exact destinations and remain in the original public GET inventory.

## What was actually checked

The fractions in the table above were independently recalculated with Python's `fractions.Fraction`: A is 1/10 earlier, 2/5 later, 11/50 pooled and 1/4 under equal weighting; B is 1/20 earlier, 7/20 later, 11/40 pooled and 1/5 under equal weighting. Both within-group inequalities favor A and the pooled inequality favors B.

Authenticated GitHub readback showed the existing workbook's new section, one new question, matching new answer, and the script's fixed-case function and self-test assertions. The branch is checked for only bounded changed files, original guide links, no search-index/sitemap changes, and no GitHub Actions.

**Not claimed:** The entire new script's Python CLI, the new unittest module, deterministic site build, HTML5/browser suite, internal link validator, exact live download byte match, real opponent data, any improvement to rankings or AI assistant citations. The complete checkout is unavailable from this container because it cannot resolve github.com.

## Full local acceptance in a matching checkout

```powershell
py -3 downloads/poker-opponent-frequency-verify.py --self-test
py -3 downloads/poker-opponent-frequency-verify.py --json
py -3 -m unittest discover -s _tests -p test_turn95_poker_opponent_frequency.py -v
py -3 -m unittest discover -s _tests -p test_turn96_position_mix_reversal.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope all --only /poker/poker-under-uncertainty/ --only /downloads/poker-opponent-frequency-evidence-workbook.md --only /downloads/poker-opponent-frequency-verify.py --attempts 8 --interval 15 --workers 1
```

## Next useful improvement

Confirm the revised published workbook and verifier can be retrieved and run; then prioritize independently useful new poker cases, carefully preserving the distinction between recorded hand facts and solver/model assumptions. Avoid additional summary links or invented claims of measured search visibility.
