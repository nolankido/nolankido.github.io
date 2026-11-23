# SEO/GEO Turn 97: prevent false success from optimized Python self-tests

**Date:** November 22, 2026, Pacific/Honolulu  
**Base:** `a785bf8d81ab36e63b404833e0976ad547e6a6ed` (merged Turn 96)  
**Existing code route:** `/downloads/poker-opponent-frequency-verify.py`  
**Unchanged source context:** `/poker/poker-under-uncertainty/#frequencies`  
**Scope:** Fix the release verifier itself, not another study page.

## Reproduced defect

The already published, fixed-case Python script was reconstructed in the local container **byte-for-byte**, with original Git blob SHA `1e9bff30a40c0481ecf182692adb2400c162ab2a`, confirmed by `git hash-object`. Python 3.13.5 ran the script's normal `--self-test` and `--json` successfully.

The old `self_test()` contained **27 ordinary `assert` statements**. Python `-O` and `-OO` remove these assertions. To test whether this affected correctness rather than just style, the local source was deliberately changed to require the false Wilson interval `[10.5%, NOT-REAL%]` instead of the true fixed-case expected values. Results:

| Executable and manipulated source | Exit | What happened |
| --- | ---: | --- |
| Normal Python, corrupted expected value | 1 | Check failed, as it should |
| `python -O`, same corrupted expected value | 0 | **False PASS** |
| Normal Python, unmodified source | 0 | Existing correct fixed checks pass |

A test mode that falsely reports PASS on a changed expected answer cannot be treated as a reliable offline release gate.

## Implemented bounded fix

Replace the 27 optimization-elidable assertions in `self_test()` with explicit `require(condition, expression)` calls. The new helper raises an `AssertionError` when a fixed condition fails and names the failed expression. All original calculation inputs, arithmetic results, report structure, CLI flags, invalid count handling and standalone privacy characteristics remain unchanged.

The new file has authenticated Git blob SHA `5d89ae2404caad80005e71dd508ba6498fdef690`. GitHub returned that **exact SHA** for the revised script, which matches the locally executed replacement bytes. No third-party libraries, new network access, extra file IO or new command arguments were added.

Add `_tests/test_turn97_optimized_frequency_self_test.py` with seven standalone and three full-site integration tests. Its authenticated Git blob SHA `002609e6a58160ca66bb14b5e5aaa99fe0845764` matches the local test source that was executed. Register it in the established manual `_scripts/local_release_checks.py`, leaving older Turn 95/96 test registrations intact, and update `AGENTS.md`.

## Executed validation

Local Python 3.13.5 on the **exact new script bytes**:

- The ordinary Python, `-O` and `-OO` `--self-test` modes each exit 0 and report the original PASS.
- Both optimized JSON modes exactly match the original regular JSON report, preserving the existing Wilson, Beta and Simpson's paradox cases.
- Two intentionally incorrect expected-value mutations, one Wilson and one pooled Simpson value, each terminate with a nonzero exit and a named failure under **all three Python modes**. No false PASS is emitted.
- The AST contains no `ast.Assert` nodes. The 27 fixed-example checks invoke the fail-closed helper even under optimization.
- Existing invalid-count rejection, bounded standard-library imports and no automatic remote requests are retained.
- **Seven standalone unittest methods passed** against the exact local script and test fixture.

**Not executed:** Three new full-site integration methods, full deterministic site build, full prior Turn 95 and Turn 96 test suites, HTML5 parser, full browser test suite, search snapshot, internal-link audit, and public exact-byte GET receipt. The complete repository remains unavailable to this container because `github.com` cannot be resolved. The previous public fetcher returned an inconclusive `target_unreachable` for the Python resource, not a verified 404 response.

## Full local acceptance in a matching checkout

```powershell
py -3 downloads/poker-opponent-frequency-verify.py --self-test
py -3 -O downloads/poker-opponent-frequency-verify.py --self-test
py -3 -OO downloads/poker-opponent-frequency-verify.py --self-test
py -3 downloads/poker-opponent-frequency-verify.py --json
py -3 -m unittest discover -s _tests -p test_turn95_poker_opponent_frequency.py -v
py -3 -m unittest discover -s _tests -p test_turn96_position_mix_reversal.py -v
py -3 -m unittest discover -s _tests -p test_turn97_optimized_frequency_self_test.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope all --only /downloads/poker-opponent-frequency-verify.py --only /poker/poker-under-uncertainty/ --attempts 8 --interval 15 --workers 1
```

## Next priority

Confirm this corrected verifier is deployed, obtain an authenticated live byte receipt, and run all integrated release checks. Prioritize actual reader-facing errors or genuinely new teaching requirements afterward. Do not claim ranking, AI citation, player performance, population statistics or growth from this correctness fix.
