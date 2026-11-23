# SEO/GEO Turn 100: preserve Stud8 and Razz pot conservation under optimized Python

**Date:** November 23, 2026, Pacific/Honolulu.  
**Base main:** `6180056249f76e7ddee71b54bf0a584d9f209803` (merged Turn 99).  
**Published verifier route:** `/downloads/poker-stud8-razz-seven-card-check.py`.  
**Unchanged indexed guide:** `/poker/stud-hilo-razz-hand-reading/`.

## Reproducible defect and bounded fix

The previously published seven-card Stud eight-or-better and Razz Python script used 27 ordinary Python `assert` statements. Two assertions were invoked inside the imported award functions and were intended to guarantee that exact fractional payouts sum to the fully eligible pot. The other 25 verified wheel scoring, qualifying and nonqualifying lows, different Stud8/Razz winners, scoop and quarter, ties, first-to-act and exposed-card counts. Python optimization (`-O` and `-OO`) removes these checks entirely.

The original source was reconstructed in the local runtime **byte-for-byte** and verified against the authenticated GitHub Git blob `f191ea8134cfc2b6d515b59221b57695e06cc642`. All valid original examples produced identical output across ordinary, `-O` and `-OO`, confirming the fixture was runnable before editing.

The replacement:
1. In `stud8_awards()`, replace the original removable pot-conservation assertion with an unconditional `if sum(results.values()) != Fraction(pot): raise ArithmeticError('Stud8 awards do not conserve the eligible pot')`.
2. Do the same independently in `razz_awards()`, with a Razz-specific error message.
3. Replace the remaining **25** fixed-example assertions with labelled `require(condition, case)` calls; the helper explicitly raises `AssertionError`, including in optimized Python. Preserve every expected hand score and award.
4. Add `_tests/test_turn100_stud8_razz_optimized.py` with 11 standalone methods and three optional full-site integration methods. Register the module with the existing manual `_scripts/local_release_checks.py` and retain the prior original `test_poker_stud8_razz.py` file.
5. Add release limitations and the remaining optimization audit backlog to `AGENTS.md` without new GitHub Actions.

The corrected script's Git blob is **`9c9f3386097445946c9b76a79c6e7b6848edf7b2`** and the executed regression file's Git blob is **`31ac262a1b8c9aeea81e3b9ff377010895adec6f`**. Both were independently confirmed by local `git hash-object` equivalent SHA-1 calculations and authenticated GitHub write/readback.

## Executed local verification

- **11 standalone unittest methods passed** in a fixture containing the exact corrected script and test source.
- `--self-test` and the default text output were byte-for-byte identical to the original published script under normal Python, `-O` and `-OO`. Their SHA-256 output snapshots are built into the regression suite.
- An intentionally changed wheel straight-flush expected score failed with a named fixed-check error under all three execution modes.
- An intentionally subtracted chip from a Stud8 no-low high-only award failed with an explicit pot-conservation error under all three modes.
- An independently subtracted chip from a Razz winner's award similarly failed under all three modes. Both award mutations were tested through **imported function calls**, proving the safeguards are not limited to executing the CLI.
- Exact fractional totals were checked on 301, 201 and 199 chip pots; a 301-unit Stud8 quarter remains 903/4, 301/4, 0, and a 301-unit Razz wheel tie remains 301/2 each. These rational shares intentionally do not model physical odd-chip distribution.
- Existing duplicate-card, insufficient-card and negative-pot rejection remains intact, and the AST contains zero optimization-elidable `assert` statements.
- No new dependencies, network requests, real hand inputs, solver, gambling product or personal data are introduced.

**Not executed:** Three site-integrated tests in the new module and the full original `_tests/test_poker_stud8_razz.py` suite require the matching complete website checkout. The complete deterministic site builder, HTML5 audit, all-unit suite, links, search snapshot, browser tests and exact source-to-live byte receipt were **not executed** in this container. GitHub domain resolution is unavailable here. These remain release gates, not assumed successes.

## Strict change scope

The GitHub diff should contain five files only: the existing verifier, new regression test, manual release runner, AGENTS.md and this report. Do not update the original indexed Stud8/Razz article, original MathJax/HTML, source publication dates, sitemap, Poker Finder, external libraries, GitHub Actions, or other poker variants during this bounded fix. The existing public exact GET target remains registered and the original guide links to the same URL.

## Full acceptance in a complete checkout

```powershell
py -3 downloads/poker-stud8-razz-seven-card-check.py --self-test
py -3 -O downloads/poker-stud8-razz-seven-card-check.py --self-test
py -3 -OO downloads/poker-stud8-razz-seven-card-check.py --self-test
py -3 -m unittest discover -s _tests -p test_turn100_stud8_razz_optimized.py -v
py -3 -m unittest discover -s _tests -p test_poker_stud8_razz.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _scripts/check_live.py --only /downloads/poker-stud8-razz-seven-card-check.py --attempts 8 --interval 15
```

## Remaining work

The published PLO flush/pair and PLO wrap enumerators still contain ordinary checks that disappear under optimized Python. Repair them in separate turns with actual normal/`-O`/`-OO` executions and deliberate corrupted-output tests. Do not claim that any real hand, strategy, search traffic, or player outcome has been verified by these fictional arithmetic fixtures.
