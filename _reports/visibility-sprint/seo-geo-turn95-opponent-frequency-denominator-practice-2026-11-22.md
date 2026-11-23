# SEO/GEO Turn 95: original opponent-frequency denominator practice

Date: November 22, 2026, Pacific/Honolulu.
Base main: 43c13e5d541ffb3520ed56cf61779350f5132a58 (merged Turn 94).
Existing indexable guide: /poker/poker-under-uncertainty/#frequencies.
New standalone resources: /downloads/poker-opponent-frequency-evidence-workbook.md and /downloads/poker-opponent-frequency-verify.py.

## Reader need

The previous pot-odds lab now has a live reset button. Further interface controls have limited return compared with improving the educational accessibility of the site's existing comprehensive Poker Under Uncertainty research. That guide already explains that opponent statistics need eligible opportunity denominators, Wilson uncertainty and Bayesian model assumptions. It lacks a separate beginner-oriented self-check workbook.

## Implemented

1. Write an original approximately 1,400-word workbook covering a fictional 3-bet sample, a denominator trap, seven practice questions, two interval conventions, two explicit prior choices, a second flop continuation-bet denominator trap, a blank evidence ledger and fully explained solutions. It is intended for permitted after-play study, not real-time decisions.
2. Create a Python standard-library-only fixed-case verifier with --self-test and --json modes and invalid-count rejection. It uses Fractions, the Wilson score formula, NormalDist's fixed 97.5th normal percentile, and finite binomial-tail integration of integer Beta parameters. No real-hand inputs, remote services, storage, solver, external dependencies or player records.
3. Insert precisely one two-link navigation panel after the guide's existing 3/12 Wilson example in both original source and published HTML. Preserve article prose, canonical, original metadata dates, existing 301-entry native Finder and sitemap. Poker Finder excludes navigation markup from searchable text.
4. Register both files as exact-byte public GET targets in the original local release checker.
5. Add eleven offline and site-integrated regression tests, register them in the existing manual-only release runner, and document source/release limits in AGENTS.md. Do not add GitHub Actions or new scheduled monitoring.

## Independent arithmetic cross-check

- 3 / 12 eligible three-bet chances = 25.0% observed, whereas 3 / 50 dealt hands = 6.0% of all hands, not the conditional reraise frequency.
- A two-sided 95% Wilson score interval for 3 / 12 is about 8.9% to 53.2%. For 8 / 40 it is about 10.5% to 34.8%. With 0 / 12, the Wilson upper limit is about 24.2%.
- The entirely illustrative Beta(6,24) prior plus three successes and nine failures produces Beta(9,33), mean 21.43%, and equal-tailed credible interval about 10.6% to 34.9%.
- Choosing an alternative Beta(1,1) prior produces Beta(4,10), mean 28.57%. These are deliberately different assumptions, not contradictory player observations.
- The separate invented continuation-bet statistic is 7 / 8 eligible opportunities = 87.5%, not 7 / 30 total flops = 23.3%.

These values were independently recalculated using local Python math. They demonstrate the stated statistical model only, not any actual opponent tendency or population rate.

## Verification scope

The complete site checkout is unavailable in the local container because github.com DNS resolution fails. The new Python verifier and all eleven new regression tests are authored, but they have NOT been executed here. Before merging, review exact navigational source/output parity, report the GitHub compare file list, and preserve all pre-existing article prose. After merging, use a fresh public read to check that both new resources appear live. Public-content presence is not an exact-byte source-to-live receipt.

## Full local acceptance in a matching repository checkout

    py -3 downloads/poker-opponent-frequency-verify.py --self-test
    py -3 downloads/poker-opponent-frequency-verify.py --json
    py -3 -m unittest discover -s _tests -p test_turn95_poker_opponent_frequency.py -v
    py -3 _scripts/build.py --check
    py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
    py -3 _tests/check_html5.py
    py -3 _scripts/check_internal_links.py
    py -3 _scripts/local_release_checks.py --full --browser
    py -3 _tests/diagnose_live_crawl.py --scope all --only /poker/poker-under-uncertainty/ --only /downloads/poker-opponent-frequency-evidence-workbook.md --only /downloads/poker-opponent-frequency-verify.py --attempts 8 --interval 15 --workers 1

Next priority: Confirm deployment, execute full-script and site-integrated checks, and pursue genuinely distinct source-verifiable teaching materials guided by reader questions. Do not claim search rankings, visits, solver-derived strategy or measured outcomes without evidence.
