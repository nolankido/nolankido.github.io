# SEO/GEO Turn 59: reconcile a personal cash with the actual payout ladder

Review date: November 20, 2026 (Pacific/Honolulu)
Starting main: 53e962de660df2ad1e1f3e9dcfe67cfbe70d0ad9
Canonical guide: https://nolankido.com/poker/tournament-entry-prize-pool-ledger/

## Confirmed error

The original guide specified one fictional $39,600 ten-place ordinary payout ladder, with tenth place receiving $1,000, its smallest finishing award. The guide's later section explicitly returned to the same $400 event, yet used a $950 individual finishing cash. Both gross-to-net calculations were arithmetically correct for that $950 amount, and older unit tests separately verified the $39,600 prize schedule and $950 arithmetic. But they did not require the personal prize to be one of the awards the same event actually paid. A $950 cash could not occur in that ladder.

The issue is internal consistency, not a verified problem with a real venue or WSOP prize. The prize table is a fictional teaching device and must not be misrepresented as a real tournament financial statement.

## Corrected math

Retain all ten unchanged prizes: $12,000, $8,000, $5,500, $4,000, $3,000, $2,000, $1,600, $1,300, $1,200 and $1,000. They total $39,600, consistent with 120 paid entries contributing $330 each to ordinary prizes. One attempt costs $400 total, including $70 in fees.

| Same fictional event | Gross finishing cash | Paid entry attempts | Trip costs | Modeled pre-tax cash result |
| --- | ---: | ---: | ---: | ---: |
| Tenth-place cash after two entries | $1,000 | 2 x $400 | $60 | +$140 |
| Identical cash after one entry | $1,000 | 1 x $400 | $60 | +$540 |
| No cash after two entries | $0 | 2 x $400 | $60 | -$860 |

The difference between the first two is exactly one $400 paid attempt. Unspent reserves are not expenses, a listed gross cash is not necessarily profit, and no private person's finances are inferred.

## Changes

1. Modified the existing source and compiled Poker entry/prize guide in paired paragraphs. The $39,600 payout table now directly links to one ledger-personal-cash-check paragraph which uses its actual $1,000 tenth-place award. Two-entry result is +$140; one-entry comparator is +$540; no-cash two-entry loss stays -$860.
2. Corrected the original eighth practice answer, using +$540 as the tempting incorrect result for a two-entry cash and explaining it would apply to one entry. All eight native reveal panels and three tables stay in place, and the other tournament entry/pool/guarantee/bounty cases are not altered.
3. Updated the older tournament-entry pool regression fixture from a $950 receipt to the schedule's $1,000 receipt. Added a standard-library Turn 59 regression that parses the actual HTML ten-place payout table instead of checking independently invented strings, reconciles all awards, calculates personal net cash, checks source/compiled fragment parity, the link, practice answer, and rejects mutations that reintroduce an impossible award, miscalculation or broken link.
4. Preserved original November 15, 2026 publication, added a meaningful November 20, 2026 modification date to the manifest, public Article metadata, editorial correction note and sitemap. The page remains a 12-minute guide. The prior historical Turn 14 report is an archived account of the old release and is intentionally not silently rewritten. The blank private worksheet, RSS publication date, catalog, titles, canonicals and other books and videos are unchanged.
5. Registered the new test in the repository's manual local release runner. No new canonical page, scripts, tracking, GitHub Actions, recurring monitoring or paid API is introduced.

## Verification and limitations

An independent arithmetic preflight confirmed the ten actual table awards total $39,600 and the corrected personal results +$140, +$540 and -$860. GitHub source and compiled HTML changed in matching passages, and the page retained eight answer reveals, one named anchor, the original publication date and an unchanged 12-minute reading estimate.

This repository commit alone cannot certify that the full Python suite, deterministic generator, HTML5 parser, keyboard/mobile browser or postmerge public GET passed. Those must be run before asserting full local release validation. No SEO ranking, generative-AI citation, viewer learning or poker-profit outcome is measured or claimed.

### Full checkout verification

~~~powershell
py -3 -m unittest discover -s _tests -p test_turn59_payout_consistency.py -v
py -3 -m unittest discover -s _tests -p test_poker_tournament_entry_pool.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /poker/tournament-entry-prize-pool-ledger/ --only /sitemap.xml --attempts 3 --interval 5
~~~

## Next improvement

Turn 60: inspect one more existing poker instructional exercise for contradictions between its event setup, answer key, alternate branch and public worksheet. Prefer source-supported correction rather than another overlapping guide.
