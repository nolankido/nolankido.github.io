# Poker authority sprint: Turn 07, first flop decision in a three-bet pot

Date: November 14, 2026

## Editorial contribution

Added an original, worked guide at
[`/poker/three-bet-pot-flop-decisions/`](https://nolankido.com/poker/three-bet-pot-flop-decisions/).
It continues the exact 100 BB six-handed cutoff versus button preflop
scene from Turn 06, with separate accessible card displays for a dry,
rainbow ace-high board and a connected, two-spade board.

The new guide provides:

- A verifiable 21.5 BB flop pot, 90 BB behind each player and SPR
  approximately 4.19, after cutoff opens to 2.5 BB, button three-bets
  to 10 BB, both blinds fold and cutoff calls 7.5 BB.
- Correct flop action order, explaining why cutoff acts first and why
  the button is never obliged to continuation-bet after a check.
- Two independent flop examples: A♣ 7♦ 2♠ and 9♠ 8♠ 7♦,
  showing why A♥ K♥ is a pair of aces on one and ace-high on the other.
  The text avoids unsupported assertions about exact range advantage.
- Three flop branches: check-back preserves the 21.5 BB pot and 90 BB
  stacks; 5 BB bet and call makes 31.5 BB with 85 behind (turn SPR 2.70);
  14 BB bet and call makes 49.5 BB with 76 behind (turn SPR 1.54).
- Call-price thresholds of approximately 15.87% and 28.28% **only**
  in an explicitly artificial direct-showdown, no-rake, no-tie model.
  Future betting, equity realization and opposing ranges are not assumed
  away in the actual strategy discussion.
- A legal fictional cutoff check-raise to 20 BB total over a 5 BB c-bet:
  pot 46.5 BB facing button, call 15 BB, post-call pot 61.5 BB, 70 BB
  behind each and turn SPR approximately 1.14.
- A range advantage versus nut advantage distinction, questions for
  studying specific preflop range assumptions, five answer-reveal
  self-checks, and a compact after-play hand-review checklist.

The card scenes, actions and check-raise are fictional educational
examples, not Nolan Kido's recorded play. The article links to official
PokerStars Learn and GTO Wizard educational material, with an explicit
warning that a 40 BB tournament model is not evidence for optimal
frequencies in a 100 BB cash game. No solver output was fabricated.

## Discovery and integration

- Registered the guide once in `_source/pages.json`, with canonical
  description, date, and `poker_guide` designation.
- Indexed it once in `_source/poker/library.json` and assigned its primary
  topic to `Strategy & math`, with secondary appearances in `Learn poker`
  and `Cash games` in `_source/poker/topics.json`.
- Added four contextual prose inlinks from
  `three-bet-sizing-and-pot-geometry.html`, `reading-the-board.html`,
  `ranges-and-bets.html` and `first-flop-decisions.html`.
- Used existing board card classes and answer-reveal components. Added
  no runtime JavaScript, scheduled jobs, GitHub Actions or paid services.
- Rebuilt the guide and dependent public search, library, topic pages,
  feeds, home pages and sitemap using the existing deterministic builder.

## Measured navigation growth

The graph below measures generated, on-site prose links, not observed
search rankings, crawls or visitor behavior.

| Measure | Turn 06 | Turn 07 |
| --- | ---: | ---: |
| Original guides | 63 | 64 |
| Unique guide-to-guide prose edges | 322 | 335 |
| Guides with zero or one incoming guide prose link | 0 | 0 |
| Guides unreachable from Poker navigation | 0 | 0 |

## Local verification

- `python _scripts/build.py`: 242 generated files, 23 changes on the
  initial source version. Rebuilt once more after improving card visuals.
- `python _scripts/build.py --check`: 242 generated files, 0 differences.
- `python _scripts/poker_coverage_matrix.py --write`: refreshed the
  coverage report for 64 original Poker guides.
- `python _scripts/check_internal_links.py`: 14,914 internal links across
  218 HTML pages, 0 issues.
- `python _scripts/check_search.py`: 213 sitemap URLs, 0 errors.
- `python _tests/check_html5.py`: 218 HTML pages, 0 failures.
- `python _tests/test_poker_three_bet_flop.py`: 6 tests passed, including
  exact fraction checks for pot, flop call price, raise-to versus amount
  owed, turn stacks, SPR and four substantive inlinks.
- `python _tests/test_poker_three_bet_geometry.py`: 7 passed.
- `python _tests/test_poker_library.py`: 7 passed.
- `python _tests/test_poker_topics.py`: 14 passed.

This turn did not run the full historical unit suite or browser layout
tests; it does not claim confirmed search indexing, solver verification
or search-traffic improvement. A pre-existing unrelated modification to
`technology/ai-website-visibility/index.html` was intentionally excluded
from this work and must not be staged.

## Suggested Turn 08

Continue from the flop into **the turn decision in a three-bet pot**.
Re-use the 21.5 BB starting pot and distinct check-back versus 5 BB
c-bet-and-call branches. On at least two clearly specified turn cards,
count the new pot, stack and possible second barrels. Explain how a
turn changes value and bluff candidates without fabricating solver
frequencies or confusing the immediate flop price with all-streets EV.
Include independent arithmetic tests and substantive links from the new
flop guide and the existing turn-and-river guide.
