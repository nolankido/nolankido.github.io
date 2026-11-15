# Poker authority sprint: Turn 11, six to ten big blinds

Date: November 15, 2026

## Editorial result

Built an original source-owned tournament guide at
[`/poker/six-to-ten-bb-tournament-decisions/`](https://nolankido.com/poker/six-to-ten-bb-tournament-decisions/).
It is a local release candidate until the branch is merged and the
public deployment is verified. The guide bridges Turn 10's 3–5 BB
calculator-led lesson and the existing 10–20 BB short-stack guide.

Its narrower purpose is **the preflop action tree at 6, 8 and 10 BB**,
particularly why a two-blind open with a playable flop is different
from an open-shove, and why a rejam over a previous wager is not an
unopened-pot decision. It gives readers exact inputs to check before
opening a chart but does not invent solver equilibrium frequencies.

All cases are independent fictional no-limit hold'em fixtures using
nine players dealt in, 0.5/1 BB live blinds, and one fully paid 1 BB
big-blind ante, for a **2.5 BB initial pot**. Stacks are always
identified before forced posting, and callers cover the short player
where the branch requires it.

## New worked instruction

1. **Six, eight and ten BB first-in cutoff shoves.** Button and small
   blind fold, covering BB calls alone. BB owes **5, 7 or 9 BB** more,
   building pots of **13.5, 17.5 or 21.5 BB** and simplified no-tie
   chip prices of **37.04%, 40% or 41.86%**.
2. **The non-all-in 2 BB open.** At 6, 8 and 10 BB starting stacks, a
   BB call adds 1 BB, making the same **5.5 BB flop pot**; cutoff has
   **4, 6 or 8 BB** behind, giving approximately **0.73, 1.09 or
   1.45 flop SPR**, respectively. The chart's available small-raise
   branch is consequential and cannot be silently removed.
3. **Eight-BB rejam.** HJ opens 2.5 BB with 20 BB starting, CO rejams
   8 BB, and all other seats fold. HJ owes **5.5 BB** for an
   **18.5 BB** pot, a **29.73%** direct chip call price. If HJ folds,
   CO's unmatched 5.5 is returned; CO ends at **13 BB**, a net gain
   of five from its pre-hand eight.
4. **Big-blind defense against different BTN actions.** Same BTN
   8 BB and BB starting 12 BB. A 2 BB button open costs BB only 1 BB
   to call into a **5.5 BB flop pot**, with BTN six and BB nine
   behind. A button shove costs BB seven more into a **17.5 BB**
   all-in pot, with BB three behind. The former's **18.18% immediate
   price** is explicitly not a guaranteed showdown-equity threshold;
   the latter's direct no-tie price is **40%**.
5. **Small blind first in.** SB starts eight, posts half, then shoves
   to eight total against a covering BB. BB owes seven into a
   **17 BB** called pot, a **41.18%** price. On a BB fold, SB's
   unmatched seven is returned and SB wins a three-blind contested
   pot, finishing with ten. That is **+2 BB measured before posting**
   and **+2.5 BB compared with folding at the current action**.
6. **Three-player short four-bet.** CO opens two, BTN calls two,
   BB three-bets to six, CO jams eight, BTN calls to eight, and BB
   owes two. Exact pot sequence is **11.5, 17.5, 23.5 and 25.5 BB**.
   The last full raise increment was four, so a full next raise must
   reach ten; CO's eight is a legal short all-in that **does not
   reopen BB's raising option** under current TDA Rule 49 when BTN
   only calls. Any later side pot between the covering players is
   distinct from the main pot.
7. **Transparent chip-EV sensitivity.** In an artificial BB-only
   call model, an unposted eight-blind shove with 30% joint folds and
   40% conditional showdown wins gains **+0.05 BB** relative to
   folding. Changing only the win assumption to 30% yields
   **-1.175 BB**. Under the deliberately unrealistic zero-equity
   model, an ante raises the reward from 1.5 to 2.5 BB and lowers the
   required fold frequency from **84.21% to 76.19%**. These are not
   observed fold rates, solver outputs or real-hand recommendations.
8. **Nine native hidden-answer questions**, six-step after-play
   recording checklist, plain-language chart compatibility warnings,
   explicit chip-EV versus ICM/seat-equity boundaries and correction
   route.

Primary references checked November 15, 2026:
[Poker TDA 2026 Rules Version 1.1](https://www.pokertda.com/view-poker-tda-rules/)
for full raises and short all-in reopening rights;
[HoldemResources' free Nash ICM calculator](https://www.holdemresources.net/nashicm)
for its restricted push/fold action set; and
[GTO Wizard's custom solution guidance](https://help.gtowizard.com/how-to-build-custom-solutions/)
for input requirements including player count, stack depth, antes and
allowed preflop sizes. None has solved the article's invented cases,
and no paid solver, chart, private result or at-table assistance was used.

## Integration and reader accessibility

- One canonical Poker guide in `_source/pages.json`, one library
  search record and one primary Tournaments topic assignment, with a
  secondary Strategy & math placement.
- Seven substantive contextual prose inlinks: Turn 10 3–5 BB, the
  10–20 BB guide, preflop raise response, blind defense, chart reading,
  ICM and position/effective stacks. Ten prose links lead outward to
  related original lessons. The guide can be reached from Poker entry
  routes and from both adjacent depth lessons.
- Three wide comparative tables use the existing short-stack CSS in
  accessible, keyboard-focusable horizontal scroll regions with
  mobile scroll hints and print styling. No new JavaScript or paid
  asset is required; self-checks use native `<details>` markup.
- Local builder regenerated the article, Poker Library and Finder,
  Tournament and Strategy topic pages, Poker and combined RSS,
  site-wide search surfaces and sitemap. No existing public URL or
  original publication date was replaced.

## Locally measured content connectivity

These are exact counts from the generated source and local HTML, not
Google/Bing indexing or a claim about actual search referrals.

| Measure | Turn 10 | Turn 11 |
| --- | ---: | ---: |
| Original Poker guides | 67 | 68 |
| Distinct guide-to-guide prose links | 370 | 387 |
| Guides with at most one incoming prose link | 0 | 0 |
| Guides unreachable from Poker entry routes | 0 | 0 |
| New guide's prose inlinks | Not published | 7 |
| New guide's prose outlinks | Not published | 10 |

The generated source coverage matrix tracks 68 original Poker guides,
146 catalogued outside-source records, 10 topic hubs and 13 curated
resource collections. No new external catalogue entry was added; its
stored review dates do not represent a fresh live link audit.

## Verification and known limits

- `python _scripts/build.py`: **246 generated files**. Its final
  `--check` found **zero differences**.
- `python _scripts/poker_coverage_matrix.py --write`: refreshed the
  reproducible 68-guide coverage inventory.
- `python _scripts/check_internal_links.py`: **15,304 local internal
  links across 222 HTML pages, zero issues**.
- `python _scripts/check_search.py`: **217 sitemap URLs**, unique
  titles/descriptions, **zero errors**.
- `python _tests/check_html5.py` with pinned `html5lib==1.1`:
  **222 HTML pages passed**.
- **54 focused Python tests passed**, including 11 new Turn 11 tests
  that independently reconstruct pot, call, SPR, refund, short-raise
  and hypothetical-EV math with exact fractions, plus Turn 10/Turn 09,
  library, topic and link-graph regressions.
- A new Playwright script documents four responsive viewport checks,
  keyboard reveal, inlink arrivals and JavaScript-off behavior. It
  **could not run here** because system Chromium failed to create its
  process singleton socket (`Operation not permitted`). No observed
  mobile layout or browser interaction outcome is claimed.
- The broader historical local-release checklist finished with **81
  of 92 groups passing** and 11 inherited failures. Examples are an
  archived Stand Off test with a hard-coded old Poker Find count,
  unrelated Technology visibility/reader-route assertions, stale
  acronym search-order expectations and a standalone Find packed-data
  size cap. These failures remain explicit rather than being called a
  passing full suite. Historical tests required fetching archived
  repository branches into the temporary local clone; with those Git
  fixtures available, the previously affected Poker evidence and
  release-integrity groups passed.
- The main builder touched unrelated pre-existing generated drift in
  `technology/ai-website-visibility/index.html`. Leave that page out
  of this turn's staged commit; it is not a Poker change.

No GitHub Actions, remote CI configuration, scheduled bot, new tracking
service, paid API, private player history or unpublished footage was
introduced.

## Suggested Turn 12

Build a separately sourced **satellite-seat-bubble tournament equity
lesson**, carefully distinguishing chip EV, conventional payout ICM
and equal-seat satellite eligibility. Construct a small, precisely
specified fictional payout/stack model with reproducible rational
arithmetic and no fabricated solver outputs. Include a short-stack
survival versus call comparison, exercise answers, definitions,
internal links to tournament formats and ICM, and local validation.
Do not imply that any unmodeled tournament is solved, or collapse
different payout structures into one universal risk premium.
