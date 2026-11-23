# SEO/GEO Turn 103: split-pot outcomes on the satellite bubble

Date: November 23, 2026, Pacific/Honolulu.
Base main: `a5514b5027bbcf153666b4290564039ca3258f5f`.
Existing canonical lesson: `/poker/satellite-bubble-seat-equity/`.

## Reader need

The original three-player satellite lesson models two identical seats and a no-tie showdown. It establishes that a chip-profitable call can reduce modeled qualification probability. A further distinction matters: chip equity itself is insufficient to identify a tournament prize-equity calculation if an equal split can leave both players alive.

## Implemented

Add one optional advanced native disclosure, `#sat-tie-branch`, after the no-tie call comparison and before the payout comparison, plus one jump link labelled Include split pots. Both the source and generated page receive the identical tested disclosure, preserving the original eight practice questions, three scrollable tables, canonical, article metadata, route and source references.

The disclosure deliberately extends only the original fictional 10/10/1 BB state. A makes the small-blind all-in, B must add 9 BB, C folds. The called pot is 20 BB, and all four outcome states preserve 21 BB in total. An exactly equal split returns 10 BB to each active contestant and leaves the third player with 1 BB. Nobody qualifies immediately in that tie branch.

## Exact mathematics

| State | Stacks A/B/C | B's modeled seat equity |
| --- | --- | --- |
| Fold | 11/9/1 | 129/140 |
| Call and win | 0/20/1 | 1 |
| Call and tie | 10/10/1 | 431/462 |
| Call and lose | 20/0/1 | 0 |

In the tie state, B's third-place probability is (10/21)(1/11)+(1/21)(10/20)=31/462; the first-or-second probability is 431/462. All three remain active, so treating a tie as half a seat would be incorrect.

For conditional outright-win, tie and outright-loss probabilities w, t, l summing to one, chip equity equals w+t/2, while seat value is w+t*(431/462).

- Distribution A, 90% win/0% tie/10% loss: chip equity 90%, expected final chips 18 BB, seat equity 90%, change from folding -3/140 seat units.
- Distribution B, 85% win/10% tie/5% loss: chip equity 90%, expected final chips 18 BB, seat equity 2179/2310 or about 94.33%, change from folding +101/4620 seat units.
- With fixed 10% ties, the break-even win probability is 1913/2310 and corresponding chip equity 4057/4620. These are conditional mathematical boundaries, not an estimate for an actual hand.

## Executed checks

Five standalone exact-fraction tests passed, independently enumerating the finishing orders of active players and validating every state, both seat units, the opposite comparison with folding, the tie-aware break-even threshold and invalid probability combinations. The test file's authenticated Git blob is `49c507367d6a45ed751ec728b11804d690476c9f`, identical to the local executed bytes.

The exact disclosure passed the markup contract. Eight isolated Chromium fragment runs passed at 320, 390, 768 and 1440 pixels, with JavaScript enabled and disabled. Keyboard activation opened and closed the native disclosure, the expected content was available, and no network requests or page errors occurred. These checks used a small test stylesheet, **not the full site CSS or full-page browser test**.

The authored and published files contain the same insertions. The original no-tie exercise and article bytes are otherwise preserved. The native Finder extractor skips nav and details, so the optional answer and new jump label do not require new search snippets.

## Remaining release checks

Three site-integration tests are authored, not executed: source/generated parity with full original guide, actual Finder section equality, and full generator output plus manual runner registration. Full deterministic build, search snapshot, link and HTML5 validation, existing complete satellite browser test, and exact live byte comparison remain outstanding without a full checkout.

The disclosure has no JavaScript, personal data inputs, paid dependency, new route, tracking, or GitHub Actions. The model is a fictional teaching example and not a solver result, measured range, real tournament outcome, or general recommendation.

Run in a matching complete checkout:

```powershell
py -3 -m unittest discover -s _tests -p test_turn103_satellite_tie_branch.py -v
py -3 -m unittest discover -s _tests -p test_poker_satellite_bubble.py -v
py -3 _tests/poker_satellite_bubble_browser.py
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _scripts/check_live.py --only /poker/satellite-bubble-seat-equity/ --attempts 8 --interval 15
```

Next: verify the live supplement and use an independently checkable reader question to choose another substantive poker resource improvement.
