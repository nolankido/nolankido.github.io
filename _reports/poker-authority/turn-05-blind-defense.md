# Poker authority sprint: Turn 05, blind defense and squeeze accounting

Date: November 14, 2026

## Editorial contribution

Added the original guide at
[`/poker/blind-defense/`](https://nolankido.com/poker/blind-defense/).
Its purpose is to close a practical gap in the preflop decision sequence:
the small blind and big blind do not face the same incremental price or
remaining action when a button opens, and an open plus a cold-call creates
still another decision for the blinds.

The guide includes:

- A four-situation comparison of live blind credit, the cost of continuing
  and players still able to act.
- A fictional six-handed 100 BB cash hand after a button open to 2.5 BB,
  including SB and BB calls, 9 BB three-bets, and separately accounted
  button-call branches of 19 and 18.5 BB.
- A separate blind-versus-blind example: completing to 1 BB, raising to
  3 BB, a 6 BB raised pot and a checked 97/6 stack-to-pot ratio.
- A fictional cutoff-open/button-cold-call/big-blind-squeeze exercise,
  with independently checked pot sizes of 6.5, 8, 16.5, 25 and 33.5 BB,
  plus the distinction between a 16.5 BB pot award and 5.5 BB net gain.
- A tournament big-blind ante calculation explaining that a posted
  1 BB ante raises the pot without reducing the 1.5 BB live call price.
- Four answer-reveal checks and a six-part after-play record.

All strategic examples are explicitly fictional and show possible actions,
not a recommendation to call, three-bet or squeeze a specific hand. No
solver frequencies, opponent statistics, proprietary charts or real hand
history have been asserted. Sources are visible in the guide and include
the Poker TDA, PokerStars Learn and GTO Wizard documentation.

## Publishing and internal navigation

- The canonical article appears in the Poker Library, Poker Finder,
  strategy topic hub, sitewide writing archive, Poker and writing feeds,
  and the sitemap through the existing static generator.
- `Strategy & math` is its one primary topic. `Learn poker` and `Cash
  games` are related guide routes.
- Three existing article bodies link to the guide with contextual prose:
  `facing-preflop-raises.html`, `position-and-stacks.html`, and
  `limped-multiway-pots.html`. The new guide links to ten other guides.
- All new route references use the existing page, guide and topic catalogs.
  No GitHub Actions, runtime services or paid APIs were added.

## Measured static coverage

Read-only `_scripts/poker_link_graph.py` results from deterministic public
HTML builds:

| Measure | Turn 04 | Turn 05 |
| --- | ---: | ---: |
| Original guides | 61 | 62 |
| Unique guide-to-guide prose edges | 296 | 309 |
| Guides with zero or one incoming guide prose link | 0 | 0 |
| Guides unreachable from Poker navigation | 0 | 0 |

These are locally measured content and navigation counts, not external
search rankings, traffic or indexing confirmations.

## Verification

- `python _scripts/build.py`: 240 files generated, 20 changed.
- `python _scripts/build.py --check`: 240 files checked, zero changes.
- `python _scripts/poker_coverage_matrix.py --write`: recomputed the
  coverage matrix for 62 original guides.
- `python _scripts/check_internal_links.py`: 14,728 links across 216 HTML
  pages, with zero issues.
- `python _scripts/check_search.py`: 211 sitemap URLs, no reported errors.
- `python _tests/check_html5.py`: 216 HTML pages, no failures.
- `test_poker_blind_defense.py`: seven tests passed, including independent
  rational-number arithmetic for four decision branches, disclosure,
  canonical discovery and contextual inbound links.
- `test_poker_facing_raises.py`: five regression tests passed.
- `test_poker_library.py`: seven tests passed.
- `test_poker_topics.py`: fourteen tests passed.
- `test_poker_link_graph.py`: three tests passed.
- `test_poker_coverage_matrix.py`: three tests passed.
- `test_poker_topic_journeys.py`: three tests passed.

These checks do not constitute a solver verification of strategic hand
ranges, live-room rule adjudication or a remote crawler test. A historical
full-suite run was not included in this focused turn. The pre-existing,
unrelated modification to `technology/ai-website-visibility/index.html`
was intentionally excluded from this contribution.

## Suggested Turn 06

Create a worked **three-bet sizing and pot-geometry** guide that bridges
these blind examples to four-bet decisions. Compare the same raise-to
amount in and out of position, distinguish a single-raised pot from a
three-bet pot, independently count resulting stack-to-pot ratios, and
explain why an illustrative size is not a solver result. Link the new guide
to blind defense, facing preflop raises and the existing math reference.
