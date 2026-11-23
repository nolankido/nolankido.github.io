# SEO/GEO Turn 105: three-way side-pot ICM and explicit optional study time

Date: November 23, 2026, Pacific/Honolulu.
Base main: 2e4edb46152886ed0fea767166b9e62042a960ea.
Existing canonical guide: /poker/tournament-equity/.

## Reader-facing improvement

Add an original, approximately 1,600-word after-play workbook and an offline standard-library verifier, reachable from the existing tournament-equity guide's Side-pot worksheet link. Reuse the three-way contribution structure from the earlier bounty guide but use ordinary $70/$30/$0 finishing prizes without bounties.

Three players X/H/Y start with 4/14/9 BB. X shoves 4, H calls 4, Y shoves 9, and H faces a final additional 5 BB call. On a fold, H keeps 10 BB, Y receives a 5 BB unmatched refund and X/Y alone contest the 12 BB main. On a call, H retains 5 BB and contests the 12 BB main plus the 10 BB side against Y. All 27 BB are conserved.

Use one explicitly stipulated joint strict-ranking distribution: H > Y > X with probability 1/10; X > H > Y with 3/10; X > Y > H with 3/5. Other orders are assigned zero for this teaching example. The toy event awards Y second and X third if both bust together, because Y started with the larger stack. No real event rule or range is inferred.

Main-pot win probability is 1/10 and side-pot win probability is 2/5; the events are related, not independent. Incremental chip EV is 12/10 + 10(2/5) - 5 = 1/5 BB. Fold and call expected ordinary prize equities are $11312/297 and $5366/153 respectively. The difference is -$15226/5049, approximately -$3.02. Winner-only prize equity would instead be chip-proportional, yielding +$20/27 in the same counterfactual. The worksheet explains each fold/call branch, conditional finish-order arithmetic, six self-check questions and an answer key.

## Publishing correction

Earlier Turns 103 and 104 introduced optional advanced disclosures whose full text was counted by the original 225 words/minute estimate even though the generated reading labels remained at their previous values. Preserve the educational content rather than remove it. Explicitly label both disclosures as extra reading time, and introduce data-reading-optional="true" on their native details elements. The estimator now excludes only details deliberately marked with that value, while continuing to count ordinary practice answers. It preserves the 225-word ceiling and the prior script/style exclusion. The library visibly documents the new convention, including separate downloads. Nested details and non-details/false markers are regression-tested.

The reader estimator lives in _scripts/poker_read_time.py and is imported by the original poker_library module, which retains its PlainText and minutes names. The three affected authored guides' direct core-text checks give 1573, 3110 and 3189 words, consistent with their existing 7-, 14- and 15-minute labels. The new worksheet link keeps the tournament-equity navigation word count neutral. No new indexed page, sitemap entry, Finder artifact, tracking, paid service or GitHub Actions is introduced. Ordinary disclosure text is not stripped from the web pages.

## Actual validation

Thirteen standalone unittest methods executed and passed in the local fixture. Eight check the exact multiway settlement/ICM program and workbook, including every strict three-player rank order, both actions, independent closed-form ICM values, invalid inputs, regular/-O/-OO output parity and rejection of a deliberately wrong prize expectation. Five test the reading-time implementation, its word boundary, ordinary answer inclusion, optional details exclusion, nested disclosure handling and marker scope.

All four new files match the exact locally tested Git blobs:
- downloads/poker-multiway-icm-verify.py: d7dadac9ee7e06366730f45ef0ddcb64b3ff87e8
- downloads/poker-multiway-icm-workbook.md: ebbd67ce917288b0bc92a23e040ce822983adfed
- _scripts/poker_read_time.py: 6cda8a99f59bfe0743b468337e60a735dc79e90a
- _tests/test_turn105_multiway_icm_workbook.py: 2f3bd73b80190ed45ab9d147ccdad533559f9b08

Both download assets are registered with the existing public exact-byte inventory. The manual release runner includes the new regression module. Prior Turn 103/104 test patterns are updated for the explicit optional attribute. The earlier Turn 104 example was independently observed live before this work.

Four site-integration methods, the full deterministic builder, search snapshot, browser suite and exact deployment receipts remain unexecuted because the local environment lacks a complete checkout. Static source calculations and GitHub readback do not establish a full site build pass or an SEO outcome.

## Complete-checkout release gates

    py -3 -m unittest discover -s _tests -p test_turn105_multiway_icm_workbook.py -v
    py -3 -m unittest discover -s _tests -p test_turn103_satellite_tie_branch.py -v
    py -3 -m unittest discover -s _tests -p test_turn104_mystery_bounty_inventory.py -v
    py -3 _scripts/build.py --check
    py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
    py -3 _scripts/local_release_checks.py --full --browser
    py -3 _scripts/check_live.py --only /poker/tournament-equity/ --only /downloads/poker-multiway-icm-workbook.md --only /downloads/poker-multiway-icm-verify.py --attempts 8 --interval 15

These are fictional mathematical study materials, not at-table advice, observed opponent probabilities, real-world payout assurances or evidence of increased search traffic.
