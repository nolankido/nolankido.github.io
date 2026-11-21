# SEO/GEO Turn 57: exact three-player ICM proof and payout sensitivity

Review date: November 20, 2026, Pacific/Honolulu.
Prior main commit: 9895a6cd7f61cd70b79f4d64957aa87d3e77e207.
Canonical: https://nolankido.com/poker/tournament-equity/
Model reference: https://blog.gtowizard.com/icm-basics/

## Source audit finding

The existing 10/10/10 chip-transfer example with $50/$30/$20 prizes was correct. A second exact-fraction finish-order enumeration reproduced the baseline prize value 100/3, win value 130/3, loss value 20, the 4/7 win threshold (57.14%), and the spectator's modeled value 110/3. At a hypothetical 55% win chance, hero prize expectation is 197/6, a difference of -1/2 dollar against keeping the starting state. Hero chip expectation is 11 rather than 10. This does not assign real showdown equity or poker strategy.

The meaningful gap was public reproducibility and demonstrating that the resulting risk premium belongs to the particular prize ladder, not the stack count alone.

## Fixed-input sensitivity

All three examples use identical pre-gamble stacks (10,10,10), hero-win stacks (20,0,10), hero-loss stacks (0,20,10), one original $100 prize pool, no blinds, antes, dead money, tie events, side pots or subsequent decisions.

| Payouts for first, second, third | Hero equity before | Win equity | Loss equity | Break-even win chance |
| --- | ---: | ---: | ---: | ---: |
| $50 / $30 / $20 | 100/3 | 130/3 | 20 | 4/7, about 57.14% |
| $60 / $40 / $0 | 100/3 | 160/3 | 0 | 5/8 = 62.50% |
| $100 / $0 / $0 | 100/3 | 200/3 | 0 | 1/2 = 50.00% |

At the same artificial 60% chance to win, $50/$30/$20 yields expected prize value $34.00 versus $33.333... for preserving the stack, approximately +$0.67. At $60/$40/$0, calling yields $32.00 versus $33.333..., approximately -$1.33. This sign flip comes from the prize distribution, not changed chip math or a validated opponent range.

For the original $50/$30/$20 exercise at 55% wins, all three expected prizes are (197/6, 61/2, 110/3) in hero, opponent, spectator order. Their sum is exactly $100. The uninvolved player's gain of 10/3 in modeled expectation does not cause new payout money to appear or constitute cash already received.

## Changes

1. Added one independently executed standard-library reader script at downloads/tournament-equity-three-player-verify.py. Its inputs are fixed, uses fractions.Fraction and finishing-order enumeration, explicitly checks chip/prize conservation, and produces structured JSON. It does not read files, write files, contact any API, calculate opponent ranges or advise live action.
2. Updated the original canonical tournament-equity source and compiled HTML with three scoped answer paragraphs: the #icm-reproduce download with Windows and macOS/Linux commands; #icm-conservation on the spectator/prize conservation; and #icm-prize-sensitivity for two additional payout distributions. The existing no-blind and no-future-game limitations and GTO Wizard model citation remain.
3. Preserved October 6 publication date and updated only the meaningful November 20 article revision metadata and sitemap lastmod. Synchronized the generator-computed seven-minute reading estimate in the article, Poker Library and tournament-topic guide list. No new canonical or feed publication event.
4. Registered the script with the exact-byte local live checker, added a standard-library regression suite using a second independent permutation calculation and synthetic negative controls, and registered that suite with the no-Actions local release runner. README and AGENTS record this source and evidence boundary.

## Validation and limits

The new reader script was actually executed in local Python and passed checks on all three payout structures, prize totals and invalid stack fixtures. The page's arithmetic and the added source/compiled paragraphs were also compared before committing. The new full repository regression tests, historical test suite, deterministic site build, HTML5/browser checks and post-merge live verification are separate tasks. Do not mark these passed unless they have been executed.

There is no claim about rankings, indexing, AI assistant citations, actual played poker hand equity or measured player learning.

### Full checkout verification commands

~~~powershell
py -3 downloads/tournament-equity-three-player-verify.py
py -3 -m unittest discover -s _tests -p test_turn57_icm_prize_audit.py -v
py -3 -m unittest discover -s _tests -p test_workshops.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /poker/tournament-equity/ --only /downloads/tournament-equity-three-player-verify.py --attempts 3 --interval 5
~~~

## Next improvement

Turn 58: validate a consequential decision framework against its actual action-tree and payout assumptions, not merely its use of a familiar chart or solver label.
