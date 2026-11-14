# Poker authority sprint: Turn 08, three-bet pot turn decisions

Date: November 14, 2026

## Editorial contribution

Published an original, approximately 3,300-source-word worked guide at
[`/poker/three-bet-pot-turn-decisions/`](https://nolankido.com/poker/three-bet-pot-turn-decisions/).
It extends the prior preflop and flop three-bet lessons into the turn,
keeping the same independently counted six-handed 100 BB cash setup.

The guide provides:

- Cutoff opening to 2.5 BB, button three-betting to 10 BB, both blinds
  folding and cutoff calling 7.5 BB. The resulting flop pot is 21.5 BB
  with 90 BB behind each and SPR approximately 4.19.
- Two distinct fictional flop-to-turn boards: A♣ 7♦ 2♠ K♠, where
  the button's A♥ K♥ becomes two pair, and 9♠ 8♠ 7♦ 6♠, where the
  same hole cards remain ace-high. Accurate accessible card graphics
  distinguish completed hands from draws and four-card sequences.
- A two-history comparison that keeps a check-back flop (21.5 BB and
  90 behind each) separate from a 5 BB flop bet-and-call (31.5 BB and
  85 behind each). Neither history is inferred from the other.
- An illustrative 8 BB delayed continuation bet into 21.5 BB or an
  independently considered 8 BB cutoff turn probe. A call in either
  separate branch gives a 37.5 BB river pot and 82 BB behind each.
  Similar arithmetic does not mean the action histories are equivalent.
- After the flop 5 BB bet-and-call, a turn check-back or a second barrel
  of 12 or 24 BB. Conditional calls create 55.5 BB or 79.5 BB river
  pots, with 73 BB or 61 BB behind, and SPR about 1.32 or 0.77.
- Immediate-showdown call price calculations of 21.62% and 30.19%
  under an explicitly artificial no-fees, no-ties, no-later-betting
  model. No actual hand equity or profitable call is implied.
- A legal fictional check-raise to 36 BB total over the 12 BB turn
  barrel. Calling costs 24 more, makes a 103.5 BB pot and leaves
  49 BB behind each, for SPR about 0.47.
- Mechanical river capacity contrast: a full-stack river bet after
  the 12 BB called branch is 131.5% of the 55.5 BB pot, versus 76.7%
  of the 79.5 BB pot after the 24 BB called branch. The latter is
  close to the 76.2%-pot turn bet, illustrating geometric growth
  without prescribing a river shove.
- Six answer-reveal exercises and an after-play record for preserving
  real action order, incremental call prices and uncertain ranges.

The source section cites primary PokerStars Learn and GTO Wizard
educational materials on continuation bets, probes, turn barrels,
hold'em mechanics and configurable solution trees. Its example
boards, ranges and actions are original and have not been solved.
No personal tournament result, opponent behavior or solver frequency
has been invented.

## Site integration

- Registered one canonical article and its publication date in
  `_source/pages.json`, one Poker Library record with search terms,
  and a single `Strategy & math` primary topic.
- Added appropriate secondary navigation placements in `Learn poker`
  and `Cash games`.
- Added contextual prose inlinks from the existing flop guide,
  `turn-and-river-decisions.html`, `ranges-and-bets.html` and
  `pot-odds-workshop.html`.
- Used existing HTML components for board cards, comparison tables,
  answer reveals, source provenance and further-study navigation.
- Generated dependent public pages, sitewide search, topic pages,
  feeds and sitemap using the existing local static builder.
- No GitHub Actions, cron, new service, paid API or runtime script.

## Measured guide navigation

This is a local internal-link count, not a claim about Google traffic,
search ranking, actual visitor outcomes or a live crawler.

| Measure | Turn 07 | Turn 08 |
| --- | ---: | ---: |
| Original Poker guides | 64 | 65 |
| Unique guide-to-guide prose links | 335 | 346 |
| Guides with at most one incoming guide prose link | 0 | 0 |
| Guides unreachable from Poker navigation | 0 | 0 |

## Verification performed locally

- `python _scripts/build.py`: 243 generated files, 23 changes.
- `python _scripts/build.py --check`: 243 files, zero differences.
- `python _scripts/poker_coverage_matrix.py --write`: refreshed the
  coverage report for 65 original Poker guides.
- `python _scripts/check_internal_links.py`: 15,006 internal links
  across 219 HTML pages, zero issues.
- `python _scripts/check_search.py`: 214 sitemap URLs, zero errors.
- `python _tests/check_html5.py`: 219 HTML pages, zero failures.
- `python _tests/test_poker_three_bet_turn.py`: eight tests passed,
  including `Fraction` arithmetic for preflop and flop histories,
  turn bet/call pots, remaining stacks, turn raise-to totals,
  delayed-bet and probe accounting, river stack-to-pot ratios,
  card availability and inbound link integration.
- `python _tests/test_poker_three_bet_flop.py`: six tests passed.
- `python _tests/test_poker_library.py`: seven tests passed.
- `python _tests/test_poker_topics.py`: fourteen tests passed.

No full historical suite, browser width audit, independently run
solver or search-indexing confirmation is claimed. The pre-existing
unrelated working change in
`technology/ai-website-visibility/index.html` was preserved and must
not be staged as part of this turn.

## Suggested Turn 09

Build a dedicated **river decision in a three-bet pot** that closes the
sequence. Carry forward the 55.5 BB and 79.5 BB river-pot branches,
use clearly identified and distinct river cards, and compare a
check-down, a river value-bet hypothesis, a bluff hypothesis and a
river bet faced by the caller. Count the pot and remaining stacks,
distinguish immediate price from unknown opponent-range equity, and
explain why no future community card arrives after a river call.
Integrate contextually with the Turn 08 and existing river lessons,
with exact tests and without unsupported solver frequencies.
