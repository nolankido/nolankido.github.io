# Poker authority sprint: Turn 15, PLO wraps, blockers and redraws

Date: November 15, 2026

## Reader question and scope

**Which physical cards complete a legal four-card Pot-Limit Omaha high straight,
and which ones still win after a known opponent's redraws?**

New source-owned public route:
[`/poker/plo-wrap-redraw-blockers/`](https://nolankido.com/poker/plo-wrap-redraw-blockers/).

The article stays distinct from the published Omaha hi-lo split-pot workshop
and stud/lowball rotation workshop. It does not import hold'em's flexible
zero-to-two hole-card hand construction into PLO. It does not describe a real
Nolan Kido hand, a proprietary solver run, an optimal action, real opponent
frequencies or verified search visibility.

## Original independently reproduced fixtures

The repository includes an offline, standard-library high-hand enumerator at
`downloads/poker-plo-wrap-enumerator.py` with a `--self-test` mode and no
network, gambling client, credentials, paid service or live-play interface.
Its five-card evaluator covers the wheel, ordinary straight, flush, full
house, four-of-a-kind and straight flush. It requires exactly two hole cards
and three board cards for each Omaha candidate.

1. **Flop wrap:** hero `Qs 9s 8h 7h`; flop `Jh Tc 4d`. Exactly **16 of 45**
   possible next cards make a legal straight. Rank decomposition: four kings,
   three queens, three nines, three eights and three sevens. Each row of the
   article names a legal two-hole plus three-board construction. Probability
   of that narrowly defined next-card event: **35.56%**. These are not all
   guaranteed winning outs.
2. **Visible rival hand:** same flop and hero, exposed opposing hand
   `Kd Qd 5c 5s`. The two removed completions are specifically `Kd` and
   `Qd`; the two fives were not straight completions. Count **14 of 41**
   remaining cards, or **34.15%**, for the same completion event. This is
   card-removal arithmetic, not the hero's showdown equity against that hand.
3. **Face-up turn redraw:** same hero and flop, turn `8c`, now hero has a
   queen-high straight from `Qs 9s` and `Jh Tc 8c`. New and distinct opposing
   hand `Ac Kc 9d 2d` has nine remaining club-flush rivers and three queen
   rivers for Broadway. `Qc` overlaps both sets, so there are exactly
   **9 + 3 - 1 = 11 opponent-winning rivers**, **29 hero-winning rivers**,
   and **zero ties**, out of **40** unseen cards. Probabilities at this
   closed-action, fully exposed snapshot are **27.5% / 72.5%**. Every river
   was evaluated for *both* players' legal Omaha best five.
4. **Illegal flush counterexample:** hero `As Kd Qc Jh`, board
   `2s 7s 9s Js 3d`. Only one hero spade exists, so a flush that needs
   one hole card and four board spades is invalid under Omaha rules.

## Official rules and editorial boundaries

Primary rules reviewed November 15, 2026:

- [PokerStars Omaha rules](https://www.pokerstars.com/poker/games/omaha/)
  describes exact two-hole and three-board construction and pot-limit play.
- [PokerStars Learn PLO rules](https://www.pokerstars.com/poker/learn/lesson/plo-rules/)
  confirms the four-card starting hand and required five-card selection.
- [WSOP Online Omaha rules](https://wsoponline.com/mi/learn-to-play-poker/omaha/rules/)
  distinguishes Omaha's hand construction and betting variants.

The three sources define rule scope. They do not verify or endorse the
fictional numerical cases. Those are original teaching computations checked
by the bundled enumerator and an independent scenario-level unit test.

## Reader, crosslink and search integration

- Registered one dated Poker guide in `_source/pages.json`, the original
  library and the Omaha/mixed-game topic. Build-generated routes cover Poker
  library, Find index, topic hubs, sitemap and feeds, without new services.
- Seven unique incoming guide-to-guide prose links from the variant overview,
  Omaha hi-lo, stud/lowball, reading the board, pot odds, math reference and
  the existing flush/redraw lab. Also linked visibly from the Study desk.
- Nine outgoing guide-to-guide prose links for legal-hand comparisons,
  ranges, pot odds, multiway play, uncertainty and tournament equity.
- Two keyboard-focusable scrolling tables and native no-JS reveal answers for
  eight questions. The bundled Markdown worksheet is blank and private-use.
- Registered both public download paths in the local static-asset inventory.

## Static source inventory, not search performance

| Measured field | After Turn 14 | After Turn 15 |
| --- | ---: | ---: |
| Original Poker guides | 71 | **72** |
| Guide-to-guide prose links | 431 | **447** |
| Guides with at most one inbound guide link | 0 | **0** |
| Guides unreachable from Poker entrypoints | 0 | **0** |
| New guide's incoming guide-to-guide prose links | Not published | **7** |

No claim about indexing, impressions, organic rankings, AI recommendations,
subscribers or reader satisfaction follows from these static counts.

## Release verification

The following scoped checks are required on the tested candidate before
publishing: `python downloads/poker-plo-wrap-enumerator.py --self-test`, the
new `_tests/test_poker_plo_wrap.py`, `python _scripts/build.py --check`,
`python _scripts/poker_coverage_matrix.py --check`, local search and internal
link checks, HTML5 parsing, and exact public GET comparisons after merge.

The nine dedicated unit tests, deterministic build for 250 outputs, poker
coverage inventory, search and internal-link checks, and HTML5 parsing for
226 pages all passed locally. The default broader historical local-release
checklist reported **81/92 groups passing**; its eleven failures concerned
older Stand Off and Find literal counts and existing Technology/website-case
contracts, not the dedicated PLO fixture assertions. Its failures remain
open and should not be presented as passing. Browser visual
QA was not verified in the local execution sandbox. An unrelated generated
Technology case HTML correction appears when the deterministic site build
runs because the committed generated page and its unchanged source disagree
on an old reading estimate and move date; it is a source-alignment repair,
not a new claim or source revision.

This report describes the candidate source tree. A GitHub main-branch merge
and matching live-file checks must be completed before stating that Turn 15
was published.

## Proposed Turn 16

Build a second practical PLO high lesson on **nut-flush blockers and paired
board redraws**, with carefully controlled showdown examples, suit-aware
enumeration, and explicit comparisons to the Turn 15 wrap. Avoid giving a
preflop starting-hand range chart without a validated format and stack model.
Continue adding only genuinely explanatory internal links, not repetitive
keyword anchors.
