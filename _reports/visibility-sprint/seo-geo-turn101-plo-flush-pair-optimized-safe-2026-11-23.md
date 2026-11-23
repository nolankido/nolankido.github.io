# SEO/GEO Turn 101: preserve PLO flush and paired-board checks under Python optimization

**Date:** November 23, 2026, Pacific/Honolulu.  
**Base main:** `a989121076399c52dcd17ffe6f8e541df40caa77` (merged Turn 100).  
**Existing download:** `/downloads/poker-plo-flush-pair-enumerator.py`.  
**Unchanged indexed guide:** `/poker/plo-nut-flush-paired-board/`.  
**Scope:** Reproduce and fix two optimization-dependent calculation failures, without changing the published teaching results.

## Confirmed defect

The original published PLO high-card, flush blocker and paired-board enumerator was reconstructed locally byte-for-byte and authenticated against its Git blob `45454ddd30792776c39bf30ae5962402ce89850d`.

Its imported `four_card_flush_holdings()` function performed `assert len(unseen) == 45` as its only four-card-deck-size guard, and its `verify()` function held 15 additional ordinary fixed-example assertions. Python optimization silently disables each of those statements.

I intentionally corrupted the fixed ace-blocker flush count from 25,830 to 25,831. Under ordinary Python, the original code failed; under both `-O` and `-OO`, the corrupted source printed **PASS** and returned exit 0. This was observed rather than inferred. A three-card (or five-card) input to the original counting function also escaped its assertion when optimized, allowing a count based on the wrong deck size.

## Implemented correction

- In `four_card_flush_holdings(hero)`, explicitly reject a hand containing anything other than exactly four private cards with `ValueError` before calculating. Preserve validation of duplicate and impossible physical cards through the existing `remaining()` helper.
- Replace the removable 45-unseen-card assumption with a normal conditional that raises `ArithmeticError` if the fixed three-card flop plus four-card hand does not leave exactly 45 cards.
- Replace all 15 remaining `verify()` assertions with always-executed, labelled `require(condition, case)` checks that raise `AssertionError` in normal and optimized Python.
- Preserve original command-line output, accepted model inputs, all fixed calculations, Python standard-library-only imports, existing published URL, guide, sitemap, Poker Finder and no-GitHub-Actions rule.
- Add `_tests/test_turn101_plo_flush_pair_optimized.py` with ten standalone tests and three full-site integration safeguards, register the new module in the existing local-only runner and document the audit boundary in `AGENTS.md`.

**Exact source provenance:** Revised code Git blob `9eaee08148b73c4cc384cf91c5b495ca39a3092c`. New regression source Git blob `91f8bfc20f3f8a9565d095900d45f2e973f5aa02`. Those are the exact bytes executed by local Python and committed to GitHub.

## Executed validation

**Ten standalone regression tests passed** using the original/revised Python 3.13.5 source fixture. They checked:

1. Valid `--self-test` output is byte-identical to the original published version under normal Python, `-O`, and `-OO`, using a saved SHA-256 checksum.
2. Default (without `--self-test`) output also matches the original SHA-256 in all modes, including flush counts and paired-river winners.
3. The AST contains zero `ast.Assert` statements and 15 explicit, reachable fixed-case checks.
4. Both three-card and five-card hero inputs are rejected with the same `ValueError` in all Python optimization modes.
5. Deliberately wrong ace-spade flush deal count and deliberately wrong exact paired-board river count now fail with specific messages in all modes, never reporting PASS.
6. Independent combinatorial formulae confirm 25,830 and 31,185 flush-containing four-card rival deals among 148,995 and 6,699 unblocked ace-spade-plus-spade holdings.
7. The original paired board yields 9 of 40 opponent-winning rivers with the seven blocked, 10 of 40 without that blocker, and no winning rivers for the alternate one-queen rival case.
8. Duplicate/invalid cards are rejected, with no new network API, remote script, storage or additional dependency.

Three new site-integration tests are **authored but not executed** in the isolated fixture because source/index, inventory and full site files are absent. An all-classes test invocation in this reduced fixture accordingly reported three missing-file errors; the separate standalone-only invocation passed all ten methods. The source/index linkage and exact GET inventory were independently inspected through the connected GitHub API instead.

**Not executed:** The full original `_tests/test_poker_plo_flush_pair.py`, complete deterministic site builder, HTML5, link checker, search snapshot, full browser suite and source-to-live byte comparison. The container cannot resolve GitHub to clone the complete site. Neither successful branch commit nor successful source preview is a live deployment byte receipt.

## Remaining audit backlog

The only remaining PLO variant script from the earlier optimization-assert audit is `/downloads/poker-plo-wrap-enumerator.py`, still carrying 15 ordinary assertions. Tackle that separately with preserved output, fault injection, normal and optimized execution, and independent arithmetic before asserting the overall variant tool family is optimization safe.

## Matching checkout acceptance

```powershell
py -3 downloads/poker-plo-flush-pair-enumerator.py --self-test
py -3 -O downloads/poker-plo-flush-pair-enumerator.py --self-test
py -3 -OO downloads/poker-plo-flush-pair-enumerator.py --self-test
py -3 -m unittest discover -s _tests -p test_turn101_plo_flush_pair_optimized.py -v
py -3 -m unittest discover -s _tests -p test_poker_plo_flush_pair.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _scripts/check_live.py --only /downloads/poker-plo-flush-pair-enumerator.py --attempts 8 --interval 15
```

**Publication boundary:** No new indexed articles, SEO/AI visibility or player performance improvements are claimed from this software integrity repair.
