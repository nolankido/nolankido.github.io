# SEO/GEO Turn 99: protect Omaha Hi-Lo award conservation in optimized Python

**Date:** November 23, 2026, Pacific/Honolulu.  
**Base main SHA:** `4bb01e11d9950dc94d78a09795d8fe1ebc7632f9`.  
**Existing source URL:** `/downloads/poker-omaha-hilo-split-enumerator.py`.  
**Existing indexed guide:** `/poker/omaha-hilo-scoop-quarter-counterfeit/`.  
**Scope:** A verified correctness repair, not another indexable page.

## Confirmed issue

The original Omaha eight-or-better offline verifier was reconstructed in the model's local Python runtime **byte-for-byte**, matching Git blob `a627ffd72c51a039462dd6baf1fcdd768d70d55c`. The unmodified script's published quarter, scoop, no-low and counterfeit examples passed its regular and optimized CLI runs.

However, the original `awards()` used the runtime assertion `assert sum(result.values()) == pot`. The independent `verify()` function held 21 additional ordinary assertions. Python removes these assertions with `-O` or `-OO`.

Two deliberate mutations confirmed the defect:
- Change the expected ace-to-five wheel ranking from the correct (4,5) to the false (4,6).
- Subtract exactly one chip from a no-low high-only pot award.

Both mutations exited with errors in normal Python but **incorrectly printed PASS** under `-O` and `-OO`. In particular, the second mutation demonstrated that the runtime pot-conservation guarantee was ineffective under optimization, not just a final synthetic demonstration.

## Actual repair

- Replace the runtime pot assertion in `awards()` with `if sum(result.values()) != Fraction(pot): raise ArithmeticError(...)`. This runs even if `awards()` is imported and called rather than executing the CLI.
- Replace all 21 final `verify()` assertions with explicit `require(condition, case)` checks. Every case includes a human-readable failure label.
- Preserve original hand-selection rules (exactly two hole cards and three board cards), score functions, no-eight-or-better low condition, equal-eligibility single pot model, `Fraction` shares, all original printed values, public URL, imports and no-network boundaries.
- Add `_tests/test_turn99_omaha_hilo_optimized.py` with nine standalone tests and three authored site-integration checks, register in the existing local-only release runner, and document the known optimized-script backlog in `AGENTS.md`.

The published replacement Git blob is `523239d89674ea5c71f35dacf53cd24cb13013aa`, and the regression source blob is `d3aa5f7edb7b65dbbc1e973c69bee06e17841e7d`. These match exact local Python fixture files used for execution.

## Executed verification

- **Nine standalone tests passed** on the precise new script source.
- `--self-test` and the default script output both passed and stayed identical across regular Python, `-O`, and `-OO`. The original valid example outcomes remain unchanged.
- Both bad-case mutations fail with nonzero exits and clear messages in **all three interpreter modes**. Neither displays a false PASS.
- The AST includes zero `assert` nodes and exactly 21 `verify()` explicit `require` calls.
- Confirmed `awards()` conserves even odd-valued total pots, using fractions without inventing physical odd-chip rules. A 301-unit fictional quarter splits 903/4, 301/4, 0, totaling 301.
- Existing duplicate-card, incomplete-board and negative-pot rejection survived.
- No new library imports or remote requests were introduced.

**Not executed:** Three new full-site integration checks and the original complete Omaha Hi-Lo test module, deterministic site builder, HTML5, link/search validators, full browser suite and exact public source-byte GET. They require a complete checkout, currently inaccessible from the container due to GitHub DNS restrictions. The branch's unchanged canonical, existing guide links and exact public GET target were inspected through authenticated repository reads, not via a full browser release audit.

## Remaining sibling risks

The previous Turn 98 audit listed four vulnerable variant-game scripts. Turn 99 fixes precisely one. Still not optimized-safe:
`poker-plo-flush-pair-enumerator.py`, `poker-plo-wrap-enumerator.py` and `poker-stud8-razz-seven-card-check.py`. The last also holds runtime pot-conservation assertions, so it is the priority next separate fix.

## Complete-checkout acceptance

```powershell
py -3 downloads/poker-omaha-hilo-split-enumerator.py --self-test
py -3 -O downloads/poker-omaha-hilo-split-enumerator.py --self-test
py -3 -OO downloads/poker-omaha-hilo-split-enumerator.py --self-test
py -3 -m unittest discover -s _tests -p test_turn99_omaha_hilo_optimized.py -v
py -3 -m unittest discover -s _tests -p test_poker_omaha_hilo_split.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _scripts/check_live.py --only /downloads/poker-omaha-hilo-split-enumerator.py --attempts 8 --interval 15
```

No user action, additional paid service, CI workflow or ranking claim is required or implied.
