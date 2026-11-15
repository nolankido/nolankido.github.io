# Poker authority sprint: Turn 12, satellite bubble seat equity

Date: November 15, 2026

## Editorial result

Created an original, source-owned lesson at
[`/poker/satellite-bubble-seat-equity/`](https://nolankido.com/poker/satellite-bubble-seat-equity/).
This document records the local release candidate; a merged GitHub PR and
successful public GET are separately required to establish live deployment.
The lesson adds a distinct satellite-seat-bubble branch to the tournament
curriculum, which previously covered ordinary payout ICM and short-stack chip
pot calculations but not an independently audited identical-seat example.

The guide deliberately avoids treating ICM, chip EV and seat qualification
as interchangeable. Its example is fictional, not a published hand or
opponent read. It supplies no game-theory solve or general shove/call range.
It gives readers exact, checkable fractions and eight native hidden-answer
questions, without login, third-party JavaScript or an at-table tool.

## Reproducible three-player fixture

- Exactly **three players remain**, with **two identical qualifying seats**
  and no third-place prize. The event stops when only two remain.
- Player A starts the hand in the small blind with **10 BB**, player B
  starts in the big blind with **10 BB**, and C has **1 BB** on the button.
  Blinds are **0.5/1 BB**, with **no ante**. C folds, A shoves to ten total,
  and B considers a call. There are no ties, bounties, fees or side pots.
- At B's decision, A has ten committed and B has one committed, so the pot
  is **11 BB**. B owes **9 BB**. Calling creates a **20 BB** pot; the live
  blind is not owed twice. The **21st BB** remains with folded C.
- B folds: A wins the big blind and finishes **11**, B finishes **9**,
  C stays **1**. B calls and wins: stacks **0/20/1**; B calls and loses:
  **20/0/1**. Every outcome conserves all 21 tournament chips.

### Independently checked ICM seat calculation

Under conventional three-player Malmuth-Harville ICM, each possible first
finisher is weighted by their starting chip share and the second finisher
by their remaining conditional share. In the post-fold 11/9/1 state:

- B first: **3/7**.
- B second via A first: **33/70**.
- B second via C first: **3/140**.
- B first or second: **129/140**, about **92.14%** of a ticket.
- A qualifies with probability **33/35**, B **129/140**, C **19/140**.
  These add to exactly **two seat units**.
- If B calls, it earns a ticket if it wins and zero if it loses. Conditional
  no-tie win probability `q` therefore produces seat value **q**.
  Matching B's fold-state value requires **q = 129/140**, about **92.14%**.
- The direct **chip** threshold for B is the incremental nine divided by
  the called pot of twenty: **45%**, not the seat threshold.
- For a wholly hypothetical **q = 60%**, calling has expected chips
  `0.6 * 20 = 12`, which is **+3 BB** versus retaining nine by folding.
  But calling drops the modelled qualification chance from **92.14%** to
  **60%**, a loss of about **32.14 percentage points**. This does not
  establish any real hand's 60% equity or prescribe a fold.

### Change only the payout structure

The guide also holds the same decision and stacks fixed while changing
the fictional awards, showing why the result is not a universal ICM
"tax":

| Payout structure | B fold value | B win value | Break-even `q` |
| --- | ---: | ---: | ---: |
| Winner only, one ticket | 9/21 seat units | 20/21 seat units | **45%** |
| $70 first, $30 second, $0 third | $627/14 | $1430/21 | **1881/2860 = 65.77%** |
| Two identical tickets | 129/140 seat units | 1 seat unit | **92.14%** |

All values come from exact rational arithmetic, with displayed decimals
rounded at the end. The $70/$30 example is fabricated for comparison,
not a real event's advertised prize ladder. The winner-only row is not
presented as a two-seat satellite. The target tournament's future
performance and a restricted ticket's cash value are not modeled.

## Reader journey and site integration

- Registered one new canonical Poker guide, library card, primary
  Tournaments assignment and secondary Strategy & math placement.
- Added seven distinct contextual inlinks from existing original Poker
  guides: tournament formats, ordinary ICM, 6-10 BB decision trees,
  10-20 BB short stacks, choosing a tournament, preflop chart reading
  and the practice room. The Study desk also links it directly as a hub.
- The new guide links out to seven distinct original guides, including
  two different ICM comparisons, tournament formats, chart assumptions,
  hand-recording and planning, to prevent a single isolated article.
- Three wide tables use the site's existing keyboard-focusable,
  horizontally scrollable short-stack stylesheet. The eight self-checks
  are native HTML disclosure elements, not an answer collection service.
- Generated Poker Library, Finder, topic routes, site search, Poker and
  combined feeds, and sitemap from the same source/metadata registry.
- Existing article publication dates and URLs were preserved. Only
  linked, source-owned guides gained new contextual prose.

## Measured local content coverage

These are **repository graph metrics**, not search engine impressions,
referral clicks, new indexed pages or a forecast of rankings.

| Measure | Turn 11 | Turn 12 |
| --- | ---: | ---: |
| Original Poker guides | 68 | **69** |
| Distinct guide-to-guide prose links | 387 | **401** |
| Guides with at most one inbound guide link | 0 | **0** |
| Guides unreachable from Poker entrypoints | 0 | **0** |
| New lesson's distinct guide inlinks | Not present | **7** |
| New lesson's distinct guide outlinks | Not present | **7** |

The source inventory still has 146 catalogued third-party resource records,
ten topic hubs and 13 resource collections. Their previous review dates do
not imply a fresh external-link audit in this turn.

## Sources and editorial boundaries

Public provider documentation checked November 15, 2026:

- [GTO Wizard, comprehensive satellite guide](https://blog.gtowizard.com/satellite-guide/)
  for equal-seat multi-winner, winner-only and milestone distinctions and
  why shoving and calling branches need separate treatment.
- [GTO Wizard, payout structures and ICM](https://blog.gtowizard.com/how-payout-structures-impact-icm/)
  for the general effect of changing the number and size of prizes.
- [HoldemResources, ICM equity calculator](https://www.holdemresources.net/icmcalculator)
  as the official provider reference for stack-to-prize modeling.
- [Poker Tournament Directors Association, 2026 Rules](https://www.pokertda.com/view-poker-tda-rules/)
  as a rules reference only, not an organizer's specific satellite terms.

No source supplied a solution to this article's invented 10/10/1 hand.
Standard ICM does not directly include future blinds, position, player
skill, range reads, chip-target seats, tie payouts or other tournament
rules. The user is instructed to check the actual event's prize conditions
and run any model after play under its live-assistance restrictions.

## Local QA and known limits

- `python _scripts/build.py`: **247 generated files**; deterministic
  `--check`: **zero changes**.
- `python _scripts/check_internal_links.py`: **15,403 links** in
  **223 HTML pages**, zero issues.
- `python _scripts/check_search.py`: **218 sitemap URLs**, unique
  metadata, zero errors.
- `python _tests/check_html5.py` with the existing local test environment:
  **223 HTML pages passed**.
- **56 focused unit tests passed** across the new 11-test exact ICM
  suite and the earlier short-stack, Poker library, topic and graph tests.
  The new suite independently sums all three-player finishing orders
  with `fractions.Fraction` and asserts the alternative payout thresholds.
- New Playwright browser check covers 320, 390, 768 and 1440 px viewports,
  keyboard-only answer reveals, ten linked arrivals and a JavaScript-off
  exercise. The test **could not launch Chromium** in this environment
  because of the process sandbox's singleton socket restriction. A
  responsive visual pass is **not** claimed.
- Full local release checklist: **81 of 92 groups passed**, the same
  eleven inherited legacy groups reported for Turn 11. The failures
  concern archived Stand Off navigation counts, unrelated Technology
  case and acronym expectations, plus existing standalone Player/Find
  data-size and index contracts. The new satellite arithmetic suite,
  registered search surface, links and HTML all passed their targeted
  tests. The full suite is **not** represented as passing.
- An unrelated, pre-existing generated change in
  `technology/ai-website-visibility/index.html` is **not part of this
  turn** and must not be staged or published by this branch.

No GitHub Actions, cron, paid APIs, new analytics collection, private
tournament records, personal financials or unpublished video material
were introduced.

## Suggested Turn 13

Build a distinct **bounty / progressive knockout tournament equity**
workshop contrasting fixed elimination awards, progressive bounty
allocation and ordinary chip EV. Use a tiny, explicitly fictional
cash-and-bounty ledger with eligibility and side-pot caveats, not a
fabricated PKO solver range. Integrate it with the tournament-formats,
tournament-equity and short-stack lessons and add independent arithmetic
tests plus contextual navigation. Preserve any existing articles' dates.
