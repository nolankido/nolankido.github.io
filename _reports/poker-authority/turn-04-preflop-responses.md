# Poker authority sprint: Turn 04, facing preflop raises

Date: November 14, 2026

## Published contribution

Added an original, approximately 2,300-source-word educational guide at
[`/poker/facing-preflop-raises/`](https://nolankido.com/poker/facing-preflop-raises/).
It fills the previously identified gap between a beginning starting-hand
lesson and chart literacy: reconstructing a decision after an open-raise or
three-bet, with the actual players, prices and remaining stacks included.

The guide contains:

- A terminology and legality table distinguishing open-raises, three-bets,
  four-bets, calls, limps and the action-reopening exception.
- A six-handed fictional cutoff-open/button-response exercise with three
  choices, explicit dead blinds, a conditional 8 BB three-bet/call branch,
  and resulting pot and SPR.
- A second six-handed fictional button-open/big-blind-three-bet exercise
  with a counted call, illustrative 22 BB four-bet, exact minimum full
  four-bet of 15.5 BB, and separate resulting SPRs.
- A matched 100 BB versus 25 BB stack comparison, four answer-reveal
  questions and a six-part private after-play study record.
- Visible official rules/tool-documentation links and a clear distinction
  between constructed examples, model assumptions, and genuine strategy
  solutions. No fabricated solver frequencies or real-hand claims.

## Navigation and visibility

- The canonical URL is in the static sitemap, Poker RSS, sitewide writing
  feed, Poker Library, Poker Finder and Writing archive.
- The `Strategy & math` topic is its primary hub; `Learn poker` and `Cash
  games` offer secondary routes. Both primary and secondary placements
  are deliberate, not duplicate guide content.
- Three relevant existing guides link to its substantive sections from
  their prose: `starting-hand-decisions`, `reading-preflop-charts` and
  `range-combinations`.
- The new guide links forward to nine existing guides in measured prose
  edges, including chart-reading, range counting, mathematics, tournament
  considerations and the short-stack reference.

## Deterministic graph and tests

The read-only `_scripts/poker_link_graph.py` measurement on the reviewed
local public build changed as follows:

| Measure | Turn 03 | Turn 04 |
| --- | ---: | ---: |
| Library guides | 60 | 61 |
| Unique guide-to-guide prose edges | 284 | 296 |
| Guides with zero or one incoming guide prose link | 0 | 0 |
| Unreachable guides from Poker navigation | 0 | 0 |

The following were run locally with no GitHub Actions, browser or remote
search-ranking assumptions:

- `python _scripts/build.py` and `--check`: regenerated 239 files,
  deterministic output with 0 remaining changes.
- `python -m unittest discover -s _tests -p 'test_poker_facing_raises.py' -v`:
  5 tests passed, including independent Fraction arithmetic for both
  examples and at least three existing prose inlinks.
- `test_poker_library.py`: 7 tests passed.
- `test_poker_topics.py`: 14 tests passed.
- `test_poker_coverage_matrix.py`: 3 tests passed.
- `_scripts/check_internal_links.py`: 14,636 local links across 215 public
  HTML pages, no issues.
- `_scripts/check_search.py`: 210 sitemap URLs, no reported errors.
- `_tests/check_html5.py`: 215 HTML pages validated, no failures.
- The authored source, report and unit-test diffs passed `git diff --check`.
  The newly generated HTML inherits a blank, space-indented template line
  shared by existing site pages; its entire content is rebuilt byte-for-byte
  by the deterministic builder.

These results verify build wiring, static search hygiene and stated arithmetic.
They do not prove that a search engine indexed the page, that an AI assistant
cites it, that the strategies are optimal, or that all live room conditions
are covered. A full historical suite and browser interaction tests were not
part of this focused turn.

## Suggested Turn 05

Extend the preflop decision sequence into a practical blind-defense guide:
compare facing a button open from the small and big blinds, separate posted
chips from new investment, add a clearly counted squeeze-over-a-call case,
and show how multiway callers alter the pot and the available actions. Keep
the new article connected to the starting-hand, preflop-response and
range-counting routes. Do not invent solved defense frequencies.
