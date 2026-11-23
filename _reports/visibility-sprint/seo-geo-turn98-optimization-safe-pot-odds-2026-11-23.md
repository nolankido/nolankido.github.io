# SEO/GEO Turn 98: make pot-odds verification fail closed under optimized Python

Date: November 23, 2026, Pacific/Honolulu.
Base GitHub main: `6148d492e242e751f0a310335afce02a7e4822f6`.
Existing public code route: `/downloads/poker-pot-odds-sensitivity-verify.py`.
Original indexed guide: `/poker/pot-odds-workshop/`.

## Confirmed release-integrity defect

The original published pot-odds verifier, authenticated by Git blob `36b51d423f3aa8b05b377513a9f818986d4a96a4`, used ten ordinary Python `assert` statements to verify river call pricing, raise-to arithmetic, the bluff bettor's fold threshold and the caller's distinct break-even equity.

Python drops ordinary assertions when invoked with optimization flags. A deliberately corrupted original call-price test that expected 20% rather than the correct 25% failed under normal Python, but reported **PASS** with exit 0 under **both** `python -O` and `python -OO`. This was observed in a local fixture using the exact source bytes, not inferred from syntax alone.

## Completed fix

- Replace exactly ten optimization-elidable assertions with the explicit `require(condition, explanation)` helper. It raises a named `AssertionError` regardless of Python optimization mode when a fixed assertion is false.
- Preserve the original `--self-test`, `--json` and default text modes; retain their exact fixed mathematical output, all function names, rejected impossible input values, four allowed standard-library imports, no network or file IO, and the original fixed fictional three-model scope.
- Add `_tests/test_turn98_optimized_pot_odds.py`: eight executable standalone tests and three full-site integration checks. Register it with `_scripts/local_release_checks.py` while retaining all earlier test registrations.
- Append source ownership, the actual optimization test scope and unresolved script audit backlog to `AGENTS.md`.
- Leave the indexed guide, SEO metadata, existing sitemap, Finder catalog, public download path, exact GET asset inventory, GitHub Actions restriction and other study resources unchanged.

The final corrected file has Git blob `1bc54d052346e0498a075a2e0b4723925c6ce043`. The new regression test has blob `9a121bf9e360b78afc9d4fa5b4f73ca60300a2bb`. These match the **actual locally executed** bytes.

## Actual executed checks

In an isolated Python 3 environment:

1. Original script, intentionally wrong 25% call-price answer: normal Python exits nonzero; `-O` and `-OO` falsely report PASS with exit 0.
2. Corrected exact script: normal Python, `-O` and `-OO` all run ten model checks and report PASS on the unchanged valid cases.
3. Corrupted corrected call-price expectation: all three modes fail with a named error. Corrupted corrected pure-bluff fold-threshold expectation: all three modes fail with a named error.
4. Corrected `--json` results are identical across three Python modes and retain the expected fractions 1/4, 5/19, 3/8 and 3/11.
5. All **eight new standalone regression tests passed**.
6. All **six original Turn 89 standalone arithmetic and workbook tests passed** against the corrected script. Total: **14 executed standalone tests**.

The three new full-site integration tests, complete deterministic site build, HTML5 checks, public GET exact-byte receipt, whole historical unit suite and browser suite have **not run** because a full checkout is unavailable to the local container. Do not describe these as passing.

## Unresolved sibling risk inventory

A targeted audit of published poker-related Python downloads found four more scripts containing optimizer-elidable assertions. These are recorded explicitly rather than silently repaired without source execution:

| Script | Ordinary assert statements found | Context |
| --- | ---: | --- |
| `poker-omaha-hilo-split-enumerator.py` | 22 | Fixed card examples and runtime pot conservation |
| `poker-plo-flush-pair-enumerator.py` | 16 | Fixed card/flush calculations and deck assumptions |
| `poker-plo-wrap-enumerator.py` | 15 | Fixed out/blocker and redraw examples |
| `poker-stud8-razz-seven-card-check.py` | 27 | Fixed hand examples and runtime pot conservation |

The previous Turn 97 opponent-frequency checker and the newly fixed Turn 98 pot-odds checker no longer contain these self-test asserts. The four variant scripts are not yet safe to treat as validated under `-O`. They require their own staged replacements, ordinary and optimized executions, and independent model checks.

## Matching complete checkout commands

```powershell
py -3 downloads/poker-pot-odds-sensitivity-verify.py --self-test
py -3 -O downloads/poker-pot-odds-sensitivity-verify.py --self-test
py -3 -OO downloads/poker-pot-odds-sensitivity-verify.py --self-test
py -3 downloads/poker-pot-odds-sensitivity-verify.py --json
py -3 -m unittest discover -s _tests -p test_turn89_pot_odds_sensitivity.py -v
py -3 -m unittest discover -s _tests -p test_turn98_optimized_pot_odds.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _scripts/check_live.py --only /downloads/poker-pot-odds-sensitivity-verify.py --attempts 8 --interval 15
```

## Next priority

Fix and execute the four remaining variant-game scripts one at a time, prioritizing runtime pot-conservation invariants, and complete source-to-live receipts for previously merged downloads. No search, AI traffic or player outcome measurements can be inferred from a static arithmetic correctness repair.
