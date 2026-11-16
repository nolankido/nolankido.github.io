# Poker authority sprint: Turn 18, seven-card Stud8 versus razz

Date: November 15, 2026

## Distinct reader question

**Why does a seven-card high-low game require five separate ranks of eight or
below to win low, while a nine-low can win the full pot in razz? Which
five of seven cards play, who acts on a visible street, and how do exposed
cards affect the actually unknown deck?**

New original dated public article:
[`/poker/stud-hilo-razz-hand-reading/`](https://nolankido.com/poker/stud-hilo-razz-hand-reading/).

This follows the Turns 15 and 16 PLO-high workshops and the Turn 17
four-card Omaha hi-lo split checker. The new focus is **seven personal
cards**, with no regular shared board. The previous stud and lowball guide
compares game families but did not enumerate a complete Stud8/razz
showdown, calculate exact pot awards for the same card sets in two
different variants, or test distinct third- and fourth-street action.

## Official rules and limits of attribution

- [PokerStars Seven Card Stud Hi/Lo rules](https://www.pokerstars.com/poker/games/stud/high-low/):
  best five of seven for conventional high and ace-to-five eight-or-better
  low; independent high/low selections; best high wins all if no low
  qualifies; lowest upcard is third-street bring-in; later streets begin
  with the strongest exposed high hand.
- [PokerStars Razz rules](https://www.pokerstars.com/poker/games/razz/):
  seven-card ace-to-five low only, no eight-or-better qualifier; high
  upcard brings in; strongest exposed low hand starts later streets;
  suits may break a bring-in rank tie but not a showdown low tie.
- [PokerStars qualifying-low reference](https://www.pokerstars.com/help/articles/po-game-rules-m/217177/):
  five unpaired cards eight or lower for Stud8, wheel as best ace-to-five
  low, and straights/flushes not penalties for this low.

These are game rules, not source documentation for any newly constructed
fictional cards or counts. All hands, upcards and card-removal scenarios
are original educational fixtures. Actual room-specific exceptions,
side pots, rake, odd-chip awards, all-in ante edge cases, community-card
substitution upon deck exhaustion, player behavior and betting EV are out
of scope. The street checker explicitly rejects ambiguous tied exposed
fourth-street hands and ace-upcard bring-in conventions instead of
claiming to adjudicate house exceptions.

## Offline verification design

`downloads/poker-stud8-razz-seven-card-check.py` is a standalone, no-network,
Python 3.10+ standard-library script. It checks uniqueness of physical
cards and enumerates all **C(7,5) = 21** five-card subsets per player.

- Conventional high is the maximum of 21 five-card rank tuples, including
  wheel straights and straight flushes.
- Stud8 low is the minimum of five-distinct-rank ace-to-five lows whose
  highest rank is eight or less. Any player with none has no qualifying low.
- Razz low is the best ace-to-five five-card hand **without** an eight
  qualifier. Unpaired lows outrank paired lows, and the evaluator also
  ranks pair, two pair, trips, full house and quads if necessary.
- Pot awards use exact `Fraction` values to conserve every chip of a
  single fully eligible fictional pot without pretending to apply a
  venue's odd-chip procedures.
- The checker reproduces unambiguous third- and fourth-street exposed
  action and a pair of six-card known-information sets.
- New focused tests cross-check every five-card high in every fixture
  against the independently implemented Turn 17 high evaluator. For
  qualifying lows, they also compare the Turn 17 low evaluator's rank
  tuple with the new Stud8/razz output.

## Fictional mathematical fixtures

### Stud8: three-way 300-chip pot with a quarter

| Player | Seven cards | Best high | Qualifying low |
| --- | --- | --- | --- |
| A | `As 2s 3s 4s 7s 5h 9d` | Ace-high spade flush from `As 2s 3s 4s 7s` | Wheel using `As 2s 3s 4s 5h` |
| B | `Ah 2d 3d 4h 5d Qh Js` | Five-high straight | Wheel ties A |
| C | `Kc Kd Ks 8c 9c Tc Jh` | Three kings | None |

A wins the 150 high half; A and B split the 150 low half at 75 each.
**Awards A/B/C: 225 / 75 / 0**. A's chosen five cards differ between
high and low. Every physical card across the 21 displayed cards is unique.

### Stud8: 200-chip scoop

- A: `Ah 2h 3h 4h 5h Qs Kd`. Best high is a wheel straight flush;
  best low is the wheel itself.
- B: `6c 7c 8d 9d Td Jh Qc`. Best high is a queen-high straight;
  only three of its seven ranks are at most eight. No qualifying low.
- **A receives all 200**. This is an intentionally unusual fictional
  teaching hand, not a probability claim.

### Same two seven-card hands, opposite 200-chip winner

- A `Kh Kd Kc Qh Qd Jc Ts`: high is kings full of queens; best razz
  five-card low includes a pair of queens.
- B `Ah 2h 3h 4c 9d Td Js`: only four ranks at most eight; no Stud8
  low qualifier. Best razz low is unpaired `9-4-3-2-A`.
- **Stud8**: neither qualifies for low, so A receives 200 with high.
- **Razz**: nine-low beats the paired low, so B receives all 200.
- This compares different hypothetical games with one fixed card set,
  not two payouts awarded in the same real hand.

### Razz wheel tie

- A `As 2c 3d 4h 5s 9h Kd` and B `Ah 2d 3c 4s 5h Tc Qc`.
- Both hold a wheel for low using different suits. No high half exists.
- From 200, **A receives 100 and B receives 100**.

### Distinct upcard and card-removal exercises

- Third street upcards: A `2c`, B `Qh`, C `Qd`, D `7s`.
  **Stud8 bring-in A** as the lowest exposed; **Razz bring-in B** as the
  highest, with hearts over diamonds breaking the queen tie.
- Separate fourth street upcards: A `2c 8d`, B `Qh 9c`, C `Qd 7c`.
  **Stud8 B acts first** with the strongest exposed high; **Razz A acts
  first** with the strongest exposed low. No hidden cards are invented.
- At a separately defined early-street information set, hero knows
  `Ah 4h 7c`, with others showing `3s 5d Kc`.
  Six distinct known cards leave **46 unknown**, including **3 threes**.
  In a different hypothetical setup replace `Kc` with `3d`: still
  **46 unknown**, now **2 threes**. These are card-removal counts, not
  showdown win rates or supposed winning outs.

## Discovery and visitor-useful connections

- Registered one guide in main page manifest, library, Variants primary
  hub and Strategy related guides, with native Finder, sitemap and feeds.
- Added nine contextual inbound prose links from stud/lowball, Omaha
  overview, Omaha hi-lo basics, Turn 17 Omaha/8, math reference, range
  combinations, multiway pots, board reading and rules/fair play.
- Added a dedicated Study desk card and more than six outbound guide links.
- Three keyboard-focusable responsive comparison tables and eight native
  answer-reveal panels, plus a blank local-only worksheet and the offline
  verification script, both in static download inventory.
- No workflow, GitHub Actions, new paid provider, scheduled bot or
  real-hand or personal-identity data added.

## Local QA scope

- Offline script `--self-test`: all assertions pass.
- 15 newly added focused tests: pass.
- Prior Turns 15-17 and link-graph and coverage regressions: checked.
- Deterministic site build: **253 generated outputs**, check returns
  **0 changes**.
- Internal links: **229 HTML pages**, **16,022 link references**,
  **0 reported broken local links**.
- Search: **224 sitemap URLs**, zero reported metadata errors.
- HTML5 validator: **229 pages**, zero failures.
- Guide graph: **75 original guides**, **499 distinct guide-prose links**,
  **0 unreachable** and **0 weak** guides.
- Source coverage matrix regenerated from manifests and checked.
- The pre-existing comprehensive local release checklist has older
  Stand Off, Technology and Find contracts with hard-coded assumptions;
  report its observed pass/fail count separately from focused checks.

## Suggested next turn

**Turn 19: Deuce-to-seven lowball and Badugi construction lab.** Razz and
Stud8 both use ace-to-five low; deuce-to-seven reverses ace handling and
counts straights/flushes as penalties, while Badugi ranks four-card
distinct-rank and distinct-suit subsets before ranks. An offline checker
and complete verified hands would fill a different game-mechanics gap.
Use official variant sources and no tournament outcome assumptions.
