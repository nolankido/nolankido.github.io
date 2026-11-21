# SEO/GEO Turn 58: cutoff 8 BB shove versus BB call and omitted actions

**Review date:** November 20, 2026 (Pacific/Honolulu)
**Starting main:** ce2be3d54a8adb08433a5223819d796b06f432f0
**Canonical:** https://nolankido.com/poker/six-to-ten-bb-tournament-decisions/#bridge-ev
**Public offline calculation:** https://nolankido.com/downloads/eight-bb-shove-branch-verify.py

## Substantive audit finding

The existing first-in eight-big-blind cutoff shove equation was correct, including the single big-blind ante, the no-tie constraints and the +0.05 BB worked case. The consequential omission was its decision-role boundary. The BB's 40% incremental call price, published elsewhere in the same article, was not explicitly distinguished from the cutoff's 45.71% zero-fold break-even showdown chance. These belong to different actors, with different already-posted chips. Neither number is a preflop range or an ICM verdict.

The +0.05 BB example had no exact break-even margin displayed, so a reader might treat its positive sign as robust to small changes in hypothetical frequencies. The article also needed to state explicitly that this EV only compares a shove with folding in the given two-terminal tree. It does not price legal smaller openings, calls by the other seats or later streets.

## Frozen fictional pot and branches

Nine seats dealt in. Blinds are 0.5/1 BB; BB fully pays a separate dead 1 BB ante. All earlier players fold to the unposted cutoff with 8 BB. The artificial model contains two mutually exclusive outcomes: all remaining seats (BTN, SB and BB) fold, or BTN and SB fold and the covering BB alone calls. There are no ties, other callers, rake, bounties, ICM, future bets, deal, or real opponent range.

Initial pot: 0.5 + 1 live BB + 1 dead BBA = **2.5 BB**. CO shoves **8 BB**. The BB adds **7 BB** beyond its live blind, not an extra 8. Contested pot is 2.5 + 8 + 7 = **17.5 BB**. When called, CO wins **+9.5 BB net** from its pre-hand stack on a win, or loses **8 BB** on defeat. When all fold, CO gains **+2.5 BB** net.

Let **f** denote the **joint** chance that all remaining seats fold, not a separate BB-only observed folding frequency. Let **q** denote CO's conditional chance of winning in the BB-only call branch, not the unconditional chance a particular hole-card class beats a random hand.

The chip-EV difference between shoving and folding before investing is:

**EV = 2.5f + (1 - f) × [9.5q - 8(1 - q)]**

## Independently computed thresholds

| Question | Exact fraction | Percentage |
| --- | ---: | ---: |
| BB's additional-call chip price | 7/17.5 = 2/5 | 40.00% |
| CO's showdown win rate if always called | 8/17.5 = 16/35 | 45.71% |
| CO's required joint-fold chance if q = 40% | 2/7 | 28.57% |
| CO's required called-win chance if f = 30% | 97/245 | 39.59% |
| CO's required joint-fold chance if q = 30% | 11/21 | 52.38% |

Exact example checks:
- f = 30%, q = 40%: **+1/20 = +0.05 BB**.
- f = 28%, q = 40%: **-1/50 = -0.02 BB**.
- f = 30%, q = 30%: **-47/40 = -1.175 BB**.
- f = 2/7, q = 40%: exactly break even.
- f = 30%, q = 97/245: exactly break even.
- The zero-showdown-equity requirement remains 16/21 (76.19%) folds with one BBA, versus 16/19 (84.21%) without ante.

These numbers are exact **given the specified branches and chosen hypothetical rates**. They say nothing by themselves about the best action in a real tournament.

## External rule and model context

The [Poker TDA 2026 rules](https://www.pokertda.com/view-poker-tda-rules/) support checking legal actions and the full raise increment but do not prescribe a successful shove frequency. [GTO Wizard's custom solution setup](https://help.gtowizard.com/how-to-build-custom-solutions/) confirms that game format, blinds, antes, bet sizes, permitted limps and cold-calls, positions and objective define the game tree. Its documentation cannot be treated as a solver answer for this invented spot. [HoldemResources free Nash ICM calculator](https://www.holdemresources.net/nashicm) expressly solves a restricted push-or-fold game, not all legal small opens, three-way calls or flop continuations.

A positive shove EV compared with folding does **not** prove that shoving beats a 2 BB open or limp. Those alternatives can face folds, calls and raises, and may reach flops. Moreover f and q derive jointly from opponents' response ranges. Changing either one while holding the other fixed is a sensitivity experiment, not evidence that real opponents behave independently.

## Actual changes

1. Under the existing #bridge-ev, added three paragraphs: #bridge-ev-break-even with exact sign-change thresholds; #bridge-ev-two-prices comparing the BB and cutoff's distinct thresholds; and #bridge-ev-action-gate explicitly naming missing calls and small openings, with a link to a runnable checker. The original nine questions, four public tables, bubble ICM scenario and first-person Portland Meadows evidence limitations remain intact.
2. Added downloads/eight-bb-shove-branch-verify.py. It uses only the Python standard library and exact rational arithmetic, takes no user input, makes no network calls, reads or writes no files and produces machine-readable JSON. Locally executed and compared to independently computed exact fractions.
3. Preserved the November 15 publication and historical November 18 bubble ICM update; marked the substantive November 20 revision in Article metadata, visible editorial note, manifest and sitemap. The source-derived reading estimate is now 24 minutes across the canonical guide, Poker Library, Tournaments topic and Strategy topic.
4. Registered the new public download with exact-byte GET inventory. Added _tests/test_turn58_shove_branch.py for independent outcome arithmetic, threshold comparisons, public source parity, future action boundaries, negative controls and dates. Updated the older Turn 12 and Turn 55 test assertions to preserve their purpose under the new revision. Registered the focused suite in the manual local runner. README and AGENTS document the boundaries.

## Verification boundaries

The new calculation script was executed in Python and its exact threshold JSON output was checked. The source and compiled HTML changes had unique anchors and equal published paragraph text before merge. The complete site generator, full historical unit suite, HTML5, browser keyboard/mobile and network post-deployment source-byte checks are separate gates. Do not claim they passed without executing them.

No results were claimed about search ranking, generative AI citations, viewer retention or actual poker profitability.

### Full-checkout commands

~~~powershell
py -3 downloads/eight-bb-shove-branch-verify.py
py -3 -m unittest discover -s _tests -p test_turn58_shove_branch.py -v
py -3 -m unittest discover -s _tests -p test_poker_six_to_ten_bb.py -v
py -3 -m unittest discover -s _tests -p test_turn12_ten_bb_bubble.py -v
py -3 -m unittest discover -s _tests -p test_turn55_video_to_practice.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /poker/six-to-ten-bb-tournament-decisions/ --only /downloads/eight-bb-shove-branch-verify.py --attempts 3 --interval 5
~~~

## Next improvement

Turn 59: inspect a different consequential tournament guide where the displayed numeric answer could be confused with a different prize or legal-action objective. Prefer one verified correction and new negative tests over another overlapping content hub.
