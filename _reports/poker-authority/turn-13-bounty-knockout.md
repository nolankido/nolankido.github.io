# Poker authority sprint: Turn 13, fixed KO and PKO bounty ledgers

Date: November 15, 2026

## Editorial result

Created an original, source-owned workshop at
[`/poker/bounty-knockout-equity/`](https://nolankido.com/poker/bounty-knockout-equity/).
This report describes the local candidate. A merged pull request and a
successful public GET are separately needed to establish deployment.

The guide adds the missing accounting layer between a poker tournament's
ordinary chip pots, fixed knockout payments, progressive 50/50 bounties
and modeled future rewards. Its examples are deliberately fictional and
fully specified. It does not claim that a bounty amount, a chip-EV
percentage or a post-hand accounting identity constitutes a solver
recommendation.

The reader can start with a single $80 eligible target, inspect two
successive PKO knockouts, walk through a three-way main and side pot,
then try eight native hidden-answer questions. It requires neither a
login nor a third-party poker calculator.

## Independent prize and chip ledgers

### One eligible $80 target

Each row is a separate hypothetical hand and event contract. The
eliminator covers the target, wins the relevant pot outright, and
knocks out the target without a tie.

| Event | Eliminator's own bounty before | Target's bounty | Immediate cash | Added to own bounty | Own bounty afterward |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed KO, with fixed $80 heads | $80 | $80 | **$80** | **$0** | **$80** |
| 50/50 PKO | $40 | $80 | **$40** | **$40** | **$80** |

The second PKO $40 is not another $40 that has been paid into the
eliminator's account. It belongs to a potentially payable later
bounty-on-head marker. The chip pot is a third quantity.

### Two successive PKO knockouts

An eliminator's own progressive bounty begins at $40. Separate eligible
targets carry $80 and $60. The first earns $40 cash and adds $40 to the
eliminator's head. The second earns $30 cash and adds $30 to that head.
The final audit totals are **$70 immediate cash**, **$70 added** and
**$110 own bounty** ($40 initial + $70 added). The $110 is not a
second cash award. These are independent realized-knockout fixtures,
not probabilities of real table action.

### Three-way legal preflop fixture

- Before blind posting, X on the button has **4 BB**, hero in the small
  blind has **14 BB**, and Y in the big blind has **9 BB**. Blinds are
  **0.5/1 BB**, no ante or rake, with no prior voluntary contributions.
- X shoves to **4 BB**; hero adds **3.5 BB** to call to four; Y adds
  **8 BB** over the live big blind to raise all-in to **9 BB**; hero
  adds **5 BB** to call to nine. Y's raise is at least a legal full
  raise over four. Hero retains **5 BB** unwagered.
- Main pot: `3 * 4 = 12 BB`, contested by X, hero and Y.
- Side pot: `2 * (9 - 4) = 10 BB`, contested by hero and Y.
- Conservation: `12 + 10 + 5 = 27 BB` across pots and hero's uncalled
  starting chips. X and Y are all-in and the hand goes to showdown.

| Hypothetical no-tie ranking | Main winner | Side winner | Final stacks X / hero / Y | Bounty outcome |
| --- | --- | --- | --- | --- |
| X best; hero second; Y worst | X | Hero | **12 / 15 / 0 BB** | Hero eliminates Y in the relevant side pot, earning Y's $60 PKO: **$30 cash** plus $30 on head. X lives and keeps X's $80 bounty. |
| Y best; hero second; X worst | Y | Y | **0 / 5 / 22 BB** | Y eliminates X. Hero earns no bounty. |
| Hero best; Y second; X worst | Hero | Hero | **0 / 27 / 0 BB** | Hero eliminates both: combined $140 PKO bounties pay **$70 cash** and add $70 to hero's head. |

All three branch outcomes add to the same 27 BB. The example's two
individual bounties are stipulated as X $80 and Y $60. Multiple
simultaneous relevant-pot winners and split-pot award rules would need
additional event-specific treatment and are not asserted here.

### Expected immediate cash, not a call solve

For a separate covered, heads-up no-tie artificial branch, stipulate a
40% chance of an eligible elimination and zero bounty upon its failure.
The **fixed $80 KO** creates `0.40 * $80 = $32` expected immediate cash.
The **50/50 PKO $80 target** creates `0.40 * $40 = $16` expected
immediate cash and an independently recorded **$16 numerical expected
increase in the displayed own bounty**. The latter is not cash received.
No post-hand payouts, risk premium, hand equity, range, future bounty
realization or total action EV is computed by this conditional example.

## Reader journey and internal link coverage

- Registered one canonical dated Poker guide and a searchable library
  record, with primary Tournaments and secondary Strategy & math topic
  placements.
- Added nine distinct editorial guide-to-guide inlinks from tournament
  formats, ordinary ICM, short stacks, satellite-seat equity, choosing
  a tournament, preflop chart interpretation, multiway pots, the pot-odds
  workshop and the practice room. The Study desk adds another direct
  hub route to the guide.
- The guide itself links to eight distinct original Poker guides. Its
  next-steps navigation points readers toward the relevant accounting
  lesson rather than repeating only generic Poker hub links.
- Four wide tables use the existing keyboard-focusable horizontal
  scrolling CSS. Eight hidden answers use native HTML `<details>`.
- The generated Library, Finder, topic pages, site search, Poker feed,
  combined writing feed and sitemap all include the new route via the
  existing builder. Older URLs and article dates were preserved.

## Measured repository content coverage

These are **static source graph measures**, not Google or Bing search
impressions, indexed-page confirmations, organic conversions, AI search
citations or predictions of ranking changes.

| Measure | Turn 12 | Turn 13 |
| --- | ---: | ---: |
| Original Poker guides | 69 | **70** |
| Distinct guide-to-guide prose links | 401 | **418** |
| Guides with at most one inbound guide link | 0 | **0** |
| Guides unreachable from Poker entrypoints | 0 | **0** |
| New lesson's distinct guide inlinks | Not present | **9** |
| New lesson's distinct guide outlinks | Not present | **8** |

Other directory records were not newly link-audited or endorsed in
this turn. No traffic measurement or webmaster ownership claim is made.

## Primary sources and editorial boundaries

Provider and rules documentation checked November 15, 2026:

- [PokerStars: knockout and progressive knockout structure](https://www.pokerstars.com/help/articles/trn-knockout/213401/)
  for the full fixed bounty and typical immediate/progressive 50/50 split.
- [PokerStars: elimination and relevant-pot bounty ownership](https://www.pokerstars.com/help/articles/trn-elimination-bounty/182700/)
  for main- and side-pot eligibility in an elimination award.
- [HoldemResources: knockout model implementation](https://www.holdemresources.net/blog/hrc-1v4-update-knockout-bounty/)
  for distinguishing realized knockout awards and modeled future bounty
  opportunities instead of treating bounty dollars as chip units.
- [GTO Wizard: knockout bounty models](https://blog.gtowizard.com/bounty-models-explained-solving-knockout-tournaments/)
  for the limits of estimating future bounty value.
- [Poker Tournament Directors Association, 2026 Rules](https://www.pokertda.com/view-poker-tda-rules/)
  for general tournament pot management, not venue-specific bounties.

None of these sources supplies a solver solution to this workshop's
constructed cases. All stacks, target amounts, hand rankings and 40%
knockout probability are original teaching assumptions. Live venue
rules can differ and must be checked before applying an award model.
The page is designed for study after play, not real-time assistance.

## Verification and release limits

- `python _scripts/build.py`: **248 generated files**; deterministic
  `--check` reported **0 changes**.
- `python _scripts/check_internal_links.py`: **15,504 links** across
  **224 generated HTML pages**, **0 issues**.
- `python _scripts/check_search.py`: **219 sitemap URLs**, **219 unique
  titles and descriptions**, **0 errors**.
- `_tests/check_html5.py`: **224 HTML files passed**.
- **68 focused tests passed**, including 12 new independent bounty
  accounting tests plus the existing satellite, short-stack, library,
  topics and graph suites. These test exact fractions, the legal
  4/9/9 BB contributions, all three alternative showdown chip totals,
  immediate cash splits, metadata and internal discovery.
- The optional Playwright script specifies 320, 390, 768 and 1440 px,
  keyboard-only answer reveals, twelve inbound arrivals and JavaScript
  disabled. It **could not launch Chromium** because this environment
  rejects the browser singleton socket with `Operation not permitted`.
  No responsive visual browser pass is claimed.
- Full local release checklist: **81 of 92 groups passed**. The same
  eleven previously known legacy groups failed, with no new category:
  Stand Off historical counts; eight unrelated Technology article,
  crosslink, acronym and table-hint expectations; the Player Find count
  contract; and the standalone Find payload-size limit. The new bounty
  suite and targeted search, HTML and link checks all passed, but the
  full legacy release checklist **did not pass**.
- An unrelated, pre-existing generated change to
  `technology/ai-website-visibility/index.html` was deliberately
  excluded from this turn's source and commit.

No GitHub Actions, cron, new paid API, analytics collector, private
tournament notes or unpublished video footage were introduced.

## Suggested Turn 14

Build a reader-auditable **tournament entry-fee, rake and prize-pool
breakdown**. Contrast total entry cost, withheld fees, money available
for ordinary finishing prizes, separately funded bounty awards and
re-entry risk with a small fictional event sheet. Link it to the
format and event-selection guides and test that all contributions
balance. Avoid promising venue profitability or publishing personal
financial records.
