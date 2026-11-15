# Poker authority sprint: Turn 09, river decisions in three-bet pots

Date: November 14, 2026

## Editorial result

Prepared a new, source-owned, original long-form guide at
[`/poker/three-bet-pot-river-decisions/`](https://nolankido.com/poker/three-bet-pot-river-decisions/).
It closes the explicit three-bet preflop, flop and turn lesson sequence
without reusing the simpler beginner river lesson as duplicate content.
This is a locally generated release candidate; live availability must
be verified after the change is merged and the website deploys.

The worked example carries forward the same fictional six-handed cash
game: 100 BB stacks, 0.5/1 BB blinds, cutoff open to 2.5 BB, button
three-bet to 10 BB and cutoff call. The flop begins with 21.5 BB and
90 BB behind; a 5 BB c-bet and call builds a 31.5 BB turn pot with
85 BB behind. From there, the guide treats a 12 BB turn bet-and-call
and a 24 BB turn bet-and-call as **independent histories**.

It adds:

- Two distinct five-card river boards with accessible playing-card
  labels. A♣ 7♦ 2♠ K♠ 3♦ gives A♥ K♥ two pair; 9♠ 8♠ 7♦ 6♠ 2♦
  leaves the same hole cards ace-high. An explicit alternative T♠ river
  illustrates a board straight and four board spades without mixing
  these outcomes into the 2♦ analysis.
- Called-turn pot and stack ledgers: **55.5 BB / 73 BB behind**, river
  SPR approximately **1.32**; and **79.5 BB / 61 BB behind**, river
  SPR approximately **0.77**.
- A river check-back comparison and an illustrative 24 BB bet after the
  55.5 BB branch, with a 103.5 BB post-call pot, 49 BB behind, and
  **23.19%** no-tie call-price threshold.
- A conditional value-bet hypothesis with A♥ K♥ on the ace-high board,
  and a separate bluff hypothesis on the connected board. Neither
  asserts that the bet is preferable to checking.
- Two **pure zero-equity, zero-check-value bluff thresholds** that
  are explicitly not assigned to the actual A♥ K♥ holding: **30.19%**
  folds for 24 into 55.5, and **43.42%** for 61 into 79.5. These
  are contrasted with the caller's **23.19%** and **30.27%** direct-
  showdown price thresholds, respectively.
- A separate cutoff river lead of 18 BB into 55.5 BB, generating a
  91.5 BB called pot and **19.67%** price. A hypothetical two-holding
  betting range gives **+4.875 BB** for a call with an invented 25%
  bluff proportion, versus **-8.85 BB** with an invented 10% bluff
  proportion. Neither proportion is presented as solver output or
  an observed population statistic.
- A full 61 BB river all-in after the larger turn branch. If called,
  the final pot is 201.5 BB including both folded blind contributions,
  with no chips left for either continuing player. Uncalled wagers are
  explicitly returned on a fold rather than double-counted as profit.
- An independent river check-raise to 60 BB total over a 24 BB bet,
  with a 36 BB incremental call, 175.5 BB final pot, 13 BB behind,
  and **20.51%** simplified call-price threshold. The guide explains
  why a smaller price percentage does not certify a call against a
  different raising range.
- Seven hidden-answer, keyboard-operable self-checks; a river hand-
  review memo; source-provenance and gambling-assistance limitations.

The educational citations are primary PokerStars Learn materials on
pot odds, value betting, bet sizing and Texas hold'em rules, plus
GTO Wizard's custom-solution documentation. Sources are credited for
mechanics and concepts, **not** for solving the invented boards.

## Site integration

- One canonical guide in `_source/pages.json`, one search-description
  record in `_source/poker/library.json`, and `Strategy & math` as its
  single primary topic with secondary `Learn poker` and `Cash games`
  navigation.
- Contextual prose inlinks from the preceding three-bet turn guide,
  the beginner turn-and-river guide, pot-odds workshop, betting-purpose
  guide and range-combination workshop.
- Outgoing links to the exact preceding lesson, board reading, range
  counting, pot odds, Decision Lab, free learning and a correction route.
- Deterministic generated public article, Poker Library, Finder,
  topic hubs, Poker and combined RSS, sitemap and related-page output.
- No new client-side feature, external dependency, GitHub Action,
  scheduled job, tracking service or paid endpoint.

## Locally measured navigation

These are source-derived guide-to-guide link counts, not search data,
ranking forecasts, confirmed live deployments or user-behavior evidence.

| Measure | Turn 08 | Turn 09 |
| --- | ---: | ---: |
| Original Poker guides | 65 | 66 |
| Distinct guide-to-guide prose links | 346 | 358 |
| Guides with at most one incoming prose link | 0 | 0 |
| Guides unreachable from Poker entry routes | 0 | 0 |

The generated coverage inventory has been refreshed for 66 guides,
146 catalogued outside sources, 10 topic hubs and 13 curated resource
collections. No new external resource was added to the central catalogue.

## Local validation

- `python _scripts/build.py`: **244 generated files**, 29 changed
  outputs when the new source was first incorporated.
- `python _scripts/build.py --check`: **244 files**, zero differences
  after the local generation.
- `python _scripts/poker_coverage_matrix.py --write`: refreshed the
  reproducible 66-guide coverage matrix.
- `python _scripts/poker_link_graph.py`: **358** guide prose links,
  zero weak-inlink guides, zero unreachable guides.
- `python _scripts/check_internal_links.py`: **15,101 internal links**
  across **220 HTML pages**, zero issues.
- `python _scripts/check_search.py`: **215 sitemap URLs**, zero errors.
- `python _tests/check_html5.py`: **220 pages**, zero failures.
- `python _tests/test_poker_three_bet_river.py`: **nine tests passed**.
  These independently count card combinations and seven-card showdown
  comparisons; exact fractions test all pot, stack, call-price, bluff
  and raise-to claims; discovery and contextual links are checked.
- The preceding three-bet turn, flop and geometry tests plus Poker
  Library and topic tests: **42 additional tests passed**, or **51**
  focused tests in total including Turn 09.

The focused Playwright browser script `_tests/poker_three_bet_river_browser.py`
was added to exercise 320, 390, 768 and 1440 pixel reading widths,
keyboard reveal questions, link arrivals and a no-JavaScript version.
**It did not run successfully in this environment:** Playwright's
managed Chromium executable was missing and the available system
Chromium could not create its required socket under local execution
permissions. Browser layout and axe outcomes are therefore not claimed.

The broader historical release checklist was also attempted. Several
older tests fail because they hard-code counts or search-result orders
from earlier site revisions. For example, a Stand Off companion test
expects **95** Poker entries in site-wide Find, whereas the current
`main` already has **100** before this new article and Turn 09 raises
that count to **101**. That stale assertion cannot pass simply by
repairing the river guide. These failures are not reported as a
successful full release-suite run.

One unrelated, previously existing generated-file drift in
`technology/ai-website-visibility/index.html` is left out of this
turn's staged scope. It is not a new poker feature and should not be
silently included in the commit merely because the main builder
refreshed it.

## Suggested Turn 10

Move to the next high-priority distinct question in the editorial
backlog: **3 to 5 BB tournament decisions with explicit antes and
action legality**. Audit the existing short-stack and push/fold guides
first; specify a nine-handed event, who posted the blinds and big-blind
ante, effective stacks before and after forced bets, an unopened-pot
action point and an over-raise/rejam case. Count the available dead
money and costs exactly, separate chip-EV from tournament-payout or
bounty objectives, and never substitute an unstated solver chart for
a worked decision. Give the new guide contextual inlinks and its own
focused tests. Reserve 6 to 10 BB and satellite-specific strategy for
separate follow-up turns rather than compressing them into one article.
