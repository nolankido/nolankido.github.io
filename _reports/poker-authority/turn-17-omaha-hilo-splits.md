# Poker authority sprint: Turn 17, Omaha/8 high-low split-pot showdowns

Date: November 15, 2026

## Reader question and distinct scope

**When does a qualifying Omaha hi-lo low actually win chips, when does it
tie and get quartered, and can the same player make independent high and
low hands to scoop? What does an exact counterfeit river change?**

New dated, source-owned article:
[`/poker/omaha-hilo-scoop-quarter-counterfeit/`](https://nolankido.com/poker/omaha-hilo-scoop-quarter-counterfeit/).

The established [`omaha-hi-lo-workshop`](https://nolankido.com/poker/omaha-hi-lo-workshop/)
explained low qualifiers, an abstract 240-chip quarter and a specific
counterfeit; Turn 17 adds complete four-card holdings for every player,
separate five-card high and low scoring, exact rational chip distribution,
all 40 river outcomes and a standard-library offline reproducer. Turn 15
and Turn 16 continue to study **Omaha high only**, never low qualifiers.

All new cards are original fictional educational examples. One fully
eligible final pot is assumed, with no rake, fees, side pots, future betting
or venue-specific odd-chip procedures. The examples do not establish live
opponent tendencies, win rates, solver plays, EV, profits or field results.

## Rules and mathematical provenance

- [PokerStars official Omaha Hi/Lo](https://www.pokerstars.com/poker/games/omaha/high-low/)
  confirms exactly two of four private cards plus exactly three board cards
  for each separate high and low selection. Low requires five distinct ranks
  of eight or lower; aces can be low.
- [PokerStars high/low reference](https://www.pokerstars.com/help/articles/po-game-rules-m/217177/)
  confirms the ace-to-five wheel is the best low, unaffected by a straight
  or flush for low ranking.
- Neither source contains nor independently endorses the new fictional
  card fixtures, pot shares or exact river counts.

`downloads/poker-omaha-hilo-split-enumerator.py` uses only standard-library
Python 3.10+ and no network calls. Its high evaluator ranks every legal
two-private plus three-board five-card candidate, correctly recognizes
wheel straights and straight flushes, and keeps standard high rankings.
Its low evaluator separately scores five distinct ranks all at most eight
with ace counted as one, then compares descending rank tuples from high
to low. Its `awards` function allocates a single fully eligible pot using
exact `fractions.Fraction` shares so no rounding hides a tie or violates
pot conservation. It does not simulate odds or opponent strategy.

### Exact three-way quarter, 300-chip pot

- Board: `Ah Ad 2c 3d Kd`.
- A: `Ac As 4h 5h`. Best high: **four aces** using `Ac As` plus
  `Ah Ad Kd`. Best low: **5-4-3-2-A wheel** using **different private
  cards** `4h 5h` plus `Ah 2c 3d`.
- B: `4c 5c Qh Jh`. Best high: five-high straight, below quads.
  Best low: the same wheel, tying A.
- C: `Kc Ks 9h 9d`. Best high: kings full of aces, below quads.
  No qualifying low.
- High half 150 to A. Low half 150 split 75 each to A and B.
  **Total A/B/C: 225 / 75 / 0.** Each distinct physical card is used
  exactly once in the full information set.

### Scoop, 240-chip pot

- Board `Ah 2d 3c Kd Qs`; A `4h 5h Ac Ad`; B `6c 7c 9h 9d`.
- A's **best high is a five-high straight**, not trips aces, using
  `4h 5h` plus `Ah 2d 3c`. Its low is the same five-card wheel.
- B has a pair of nines for high and `7-6-3-2-A` for low.
  **A receives 240 / B receives 0.** Both high and low hands were checked.

### No qualifying low, 240-chip pot

- Board `Kc Kd Qh Jh 9s`; A `Kh Ks As 2s`; B `Ah 3c 4c 5d`.
- Zero board ranks are eight or below, so no one can select the three
  distinct low board ranks needed for a qualifying low.
- A's four kings win the **entire 240**, without creating a low half.

### Counterfeit and protection, exact exposed turn

- Turn `3c 5d 7h Kc`. A `As 2s Qd Jd`; B `Ah 4h Qh Js`.
- On the turn, A's best low is `7-5-3-2-A`, ahead of B's
  `7-5-4-3-A`, with exactly two private and three board cards each.
- On river `2h`, A **retains a valid seven-low**, but B makes the
  `5-4-3-2-A` wheel using `Ah 4h` plus `2h 3c 5d`. B also wins high
  with a five-high straight against A's pair of twos.
  **B scoops 240** in this one completely revealed showdown.
- Exactly 12 exposed cards on the turn leave 40 possible river cards.
  Comparing best low against every legal river gives **B on `2c 2d 2h`:
  3 / 40 = 7.5%**; **A on the other 37 / 40 = 92.5%**; no low ties
  and no absent low. These percentages describe **which low wins only**,
  not full-pot odds or decision EV.
- In a **different hypothetical deal**, replace A's `Qd` with `4c`.
  On river `2h`, both A and B have a wheel for low **and** a five-high
  straight for high. The total split is **120 / 120** from 240.
- The program's `--self-test` asserts each result, pot conservation and
  physical card uniqueness. Tests independently cross-check all published
  fixture high hands and both players' 40 river highs against the earlier
  Turn 15 PLO evaluator, which has a separately written high-ranking path.

## Reader access and site structure

- One new guide in public page manifest, library, **Variants** primary hub
  and **Strategy** related link; registered in native Finder, RSS and sitemap.
- Eight contextual inbound original-guide prose links from Omaha hi-lo,
  Omaha overview, PLO wrap, PLO flush, stud/lowball, math reference, range
  combinations and multiway pots; additional Study desk card.
- More than six outbound deep links with distinct learning continuations.
- Eight answer-reveal panels using native HTML `details`, three
  keyboard-focusable scroll tables, and accessible scroll hints.
- Self-contained offline Python enumerator and an unfilled Markdown review
  sheet, both registered in static download targets. No worksheet collection.
- No GitHub Actions, cron, paid services, real opponent/player private data,
  fabricated personal results or em dashes.

## Local verification

- Script: `python downloads/poker-omaha-hilo-split-enumerator.py --self-test`
  passed all fixed mathematical assertions.
- New focused tests: **13 passed**.
- Consecutive Turns 15-17, link-graph and coverage regressions:
  **39 passed**.
- Build: **252 generated outputs**, deterministic check **0 changes**.
- Search: **223 sitemap URLs**, zero reported errors; native guide
  inclusion confirmed in library, topics, feeds and Finder.
- Internal link check: **228 HTML pages, 15,914 link references,
  0 broken internal links**.
- HTML5 validator: **228 pages, zero failures**.
- Source-coverage check: **74 original guides**, **146 reviewed external
  resource records**, **10 hubs**, guide placement valid.
- Guide prose link graph: **481 unique directed guide-to-guide edges**;
  **0 unreachable** and **0 weak (at most one inbound)** guides.
- The historical local release checklist has unrelated archived
  Stand Off / Find / Technology contracts with stale baselines. Record its
  observed outcome separately; do not call the whole checklist green.

## Next useful improvement

Suggested Turn 18: a reproducible **Stud hi-lo eight-or-better versus razz**
hand-reading workshop. Distinguish seven-card subset construction from Omaha's
two-plus-three constraint, show bring-in and exposed-card information limits,
use offline exact examples, and link from the existing mixed-game material.
That would add a materially different variant before expanding yet another
Omaha subtopic. No tournament or house-rule claim without specific sources.
