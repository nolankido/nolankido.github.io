# Poker authority sprint: Turn 06, three-bet sizing and pot geometry

Date: November 14, 2026

## Editorial contribution

Added an original, approximately 2,850-source-word educational guide at
[`/poker/three-bet-sizing-and-pot-geometry/`](https://nolankido.com/poker/three-bet-sizing-and-pot-geometry/).
It moves the prior preflop lessons from identifying the legal action to
counting what a particular three-bet size changes, including later calls,
position, four-bets and remaining stack depth.

The guide provides:

- A raise-to-total versus new-chips distinction, including the ordinary
  minimum three-bet to 4 BB following a full open from 1 to 2.5 BB.
- One fictional six-handed cash hand with a cutoff open to 2.5 BB and
  button three-bets to 8, 10 or 12 BB. If the blinds fold and cutoff
  calls, the respective flop pots are 17.5, 21.5 and 25.5 BB, with
  checkable 100 BB starting-stack SPRs of about 5.26, 4.19 and 3.45.
- A single-raised versus three-bet pot comparison using the same
  starting seats and stacks: 6.5 BB and SPR 15 when the button flats,
  against 21.5 BB and SPR 4.19 when the button three-bets to 10 and
  cutoff calls. Both branches require the blinds to fold.
- A same-total comparison of the button and small blind three-betting
  a cutoff open to 10 BB: different new contributions, dead blind
  accounting, flop pots of 21.5 versus 21 BB, and postflop order.
- A legal fictional cutoff four-bet to 24 BB, after a button three-bet
  to 10: minimum ordinary full four-bet to 17.5, pot 35.5 before
  button responds, 49.5 after button calls, and flop SPR about 1.54.
- A 40 BB starting-stack contrast that keeps the 21.5 BB flop pot
  but leaves 30 BB behind, for SPR about 1.40.
- An explicitly unrealistic 71.4% break-even all-fold model, with
  no claim about actual opponent folds or future hand EV; five answer
  reveals; and an after-play study record.

Every action and hand is fictional. No verified solver size, opponent
tendency, proprietary range or strategy frequency has been asserted.
Primary official educational references and their limits are visible in
the article: 2026 Poker TDA, GTO Wizard documentation and PokerStars Learn.

## Site integration and contextual links

- Registered canonical article, description and publication date in
  `_source/pages.json`, with a unique Poker Library record and index terms.
- Assigned the single primary `Strategy & math` topic and deliberate
  secondary placements in `Learn poker` and `Cash games`.
- Added four contextual guide-to-guide prose links from
  `facing-preflop-raises.html`, `blind-defense.html`,
  `poker-math-reference.html`, and `reading-preflop-charts.html`.
- Regenerated article HTML, Poker Library and Finder, topic hubs,
  sitewide writing index, Poker and writing feeds, sitemap and other
  dependent static pages with the existing local builder.
- Added focused arithmetic, indexing, editorial scope and inbound-link
  tests in `_tests/test_poker_three_bet_geometry.py`.
- Added no GitHub Actions, scheduled jobs, paid services, or runtime code.

## Measured navigation growth

The read-only link graph measures only locally generated article prose
and route reachability, not crawler behavior or search performance.

| Measure | Turn 05 | Turn 06 |
| --- | ---: | ---: |
| Original guides | 62 | 63 |
| Unique guide-to-guide prose edges | 309 | 322 |
| Guides with zero or one incoming guide prose link | 0 | 0 |
| Guides unreachable from Poker navigation | 0 | 0 |

## Verification performed locally

- `python _scripts/build.py`: 241 generated files, 23 changes.
- `python _scripts/build.py --check`: 241 files, zero differences.
- `python _scripts/poker_coverage_matrix.py --write`: refreshed the
  coverage report for 63 original guides.
- `python _scripts/check_internal_links.py`: 14,822 internal links
  across 217 HTML pages, zero issues.
- `python _scripts/check_search.py`: 212 sitemap URLs, zero errors.
- `python _tests/check_html5.py`: all 217 HTML pages valid.
- `test_poker_three_bet_geometry.py`: 7 tests passed, with independent
  fraction arithmetic for sizes, dead blinds, minimum full raises,
  four-bets, SPR and the simplified fold threshold.
- `test_poker_blind_defense.py`: 7 tests passed.
- `test_poker_facing_raises.py`: 5 tests passed.
- `test_poker_library.py`: 7 tests passed.
- `test_poker_topics.py`: 14 tests passed.
- `test_poker_link_graph.py`: 3 tests passed.
- `test_poker_coverage_matrix.py`: 3 tests passed.
- `test_poker_topic_journeys.py`: 3 tests passed.

No full historical suite, interactive browser test, search-indexing
confirmation or solver calculation is claimed. A pre-existing unrelated
modification to `technology/ai-website-visibility/index.html` was not
part of this turn and must not be staged.

## Suggested Turn 07

Extend the sequence to a **first-flop decision in a three-bet pot**.
Use two board textures and the same fully counted 100 BB preflop setup;
contrast checking, small continuation bets, larger bets and responses
without inventing solver frequencies. Distinguish range advantage from
made-hand strength, include an independently checked postflop pot ledger,
and connect the article to `three-bet-sizing-and-pot-geometry`,
`reading-the-board`, `ranges-and-bets`, and the existing flop material.
