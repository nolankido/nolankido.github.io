# SEO/GEO Turn 102: finish the targeted optimized-Python poker verifier audit

Date: November 23, 2026, Pacific/Honolulu.
Base main: `bc94eb80033db7a403e1fc9e55ce2619d41a2374`.
Existing indexed guide: `/poker/plo-wrap-redraw-blockers/`.
Existing source download: `/downloads/poker-plo-wrap-enumerator.py`.

## Reproduced issues

The original PLO wrap enumerator was reproduced byte-for-byte at Git blob `efdc5d2e3f23d3428b9b9cee4e18e4201699789b`. It used 15 ordinary assertions in its fixed fixture checks. A mutation that changed the expected number of completions after blockers from 14 to 13 exited nonzero normally, but falsely printed PASS under both Python `-O` and `-OO`.

A separate direct-call defect allowed five unique cards with nonexistent suit symbols to be scored as a wheel straight flush. Calling the original `five_card_high(('Ax','2x','3x','4x','5x'))` returned `(8, 5)` instead of rejecting an invalid physical deck.

## Implemented

- Replace all 15 optimization-elidable assertions with labelled, explicit `require(condition, case)` failures.
- Reuse the existing physical-deck validator inside the five-card scoring helper, including calls from imported code. Invalid rank and suit symbols, duplicate cards and insufficient cards are rejected. Valid original inputs are unchanged.
- Preserve the original 16/45 wrap completion case, 14/41 known-blocker case, and the complete 40-river partition of 29 hero wins, 11 rival wins and zero ties. These are fixed fictional card-removal calculations, not actual hands or predictions.
- Add ten standalone wrap regressions, two cross-script audit regressions and three full-site integration tests in `_tests/test_turn102_plo_wrap_optimized.py`. Register them in the existing manual release runner.
- Update AGENTS.md with the targeted audit closure and precise evidence limits.

The revised script Git blob is `e86b7281cc7ec3faa78ea2976164366f35003912`. The exact locally executed regression module Git blob is `68f46ccefc1efc506d86e97744dd6f0b4d69da79`. Both match authenticated GitHub readback.

## Executed local tests

Twelve standalone unittest methods passed in the matching isolated fixture, in 27.448 seconds.

- Default and self-test CLI output SHA-256 match the original valid script under all three interpreter modes.
- Three intentionally wrong expectations (wheel ranking, blocker count and opponent-winning river count) fail explicitly under all three modes.
- Direct invalid card inputs fail; the nonexistent-suit case was checked under normal and both optimized interpreter modes.
- Exact card-completion sets and the 40-river partition match separately constructed deck sets.
- The PLO flush/pair high evaluator agrees with the wrap high evaluator on both players' scores across all 40 legal rivers, giving 80 score comparisons.
- No additional imports, network behavior or input prompts.

## Targeted audit closeout

All six repaired public source scripts were independently checked against the current GitHub blob hashes, parsed to confirm zero AST Assert nodes, and executed with `--self-test` under normal Python, `-O` and `-OO`. All 18 invocations succeeded, and each script's three outputs matched exactly.

| Download | Corrected Git blob |
| --- | --- |
| poker-opponent-frequency-verify.py | 5d89ae2404caad80005e71dd508ba6498fdef690 |
| poker-pot-odds-sensitivity-verify.py | 1bc54d052346e0498a075a2e0b4723925c6ce043 |
| poker-omaha-hilo-split-enumerator.py | 523239d89674ea5c71f35dacf53cd24cb13013aa |
| poker-stud8-razz-seven-card-check.py | 9c9f3386097445946c9b76a79c6e7b6848edf7b2 |
| poker-plo-flush-pair-enumerator.py | 9eaee08148b73c4cc384cf91c5b495ca39a3092c |
| poker-plo-wrap-enumerator.py | e86b7281cc7ec3faa78ea2976164366f35003912 |

The previous targeted audit's known optimization-elidable assertions are repaired. This is not a claim of exhaustive audit coverage of every Python download, of independent statistical correctness in every possible input state, or of a full-site release pass.

## Remaining release gates

Three new site-integration methods, the complete original PLO test suite, deterministic full website build, HTML5 and link audits, browser checks, search snapshot and source-to-live exact byte receipts are not executed here. The complete repository checkout is unavailable through container DNS. Do not confuse successful source-level and isolated tests with confirmed public deployment.

The existing indexed guide, canonical, sitemap, Finder, article metadata, public asset URL and local-only release model are unchanged. No GitHub Actions, scheduled process, paid dependency or tracking is introduced.

In a complete matching checkout:

```powershell
py -3 -m unittest discover -s _tests -p test_turn102_plo_wrap_optimized.py -v
py -3 -m unittest discover -s _tests -p test_poker_plo_wrap.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _scripts/check_live.py --only /downloads/poker-plo-wrap-enumerator.py --attempts 8 --interval 15
```

Next priority: complete remaining release verification and return to a substantive reader-facing improvement instead of extending this specific optimization audit without evidence of another defect.
