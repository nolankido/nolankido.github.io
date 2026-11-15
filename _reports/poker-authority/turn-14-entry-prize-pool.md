# Poker authority sprint: Turn 14, entry fees, guarantees and prize pools

Date: November 15, 2026

## Reader question and distinct scope

**What happens to every dollar in a tournament entry, and what changes with
re-entries, guarantees, knockout funding and an actual finishing payout?**

The new source-owned article is
[`/poker/tournament-entry-prize-pool-ledger/`](https://nolankido.com/poker/tournament-entry-prize-pool-ledger/).
This report records a source-level release candidate. A main-branch merge and
an independent public GET are required to establish that the intended page is
live. Do not treat site build success as search indexing or a traffic result.

Unlike the earlier trip budget, the new guide reconciles **the event's total
receipts and funding obligations**. Unlike the preceding KO/PKO guide, it
reconciles **initial bounty contributions**, rather than awarding a bounty to
the winner of a particular pot. It adds a blank, private-use Markdown sheet at
`downloads/poker-tournament-prize-pool-ledger.md` and eight original hidden
answer checks. No unpublished Nolan tournament finances or actual field results
were used.

## Independent numerical audit

The amounts, counts, guarantee and payout ladder are separately stated invented
teaching fixtures, not a historical event's receipts:

1. **Regular re-entry fixture:** 100 unique first entrants, 20 paid re-entries
   by 20 eliminated entrants, for 120 total paid attempts at $400 apiece. A
   per-entry split of $330 ordinary prizes plus $70 administration yields
   $48,000 collected = $39,600 ordinary prize contributions + $8,400 fees.
   Fee denominators: $70/$400 = 17.5% of the full entry; $70/$330 ≈ 21.21%
   of the ordinary contribution.
2. **Independent guarantee variant:** If the ordinary finishing pool alone is
   contractually guaranteed at $50,000, then $50,000 − $39,600 = $10,400
   in modeled organizer overlay. Sources $48,000 + $10,400 = $58,400;
   uses $50,000 + $8,400 = $58,400. At 151 paid entries, ordinary
   contributions are $49,830, still $170 short. At 152, they are $50,160,
   reaching that particular guarantee.
3. **Un-guaranteed payout ladder:** Fictional first through tenth prizes of
   $12,000, $8,000, $5,500, $4,000, $3,000, $2,000, $1,600, $1,300,
   $1,200 and $1,000 sum to exactly $39,600. This ladder is *not* silently
   reused in the guarantee variant.
4. **Separate bounty-event fixture:** 80 paid entries at $230 ordinary prizes
   + $100 initial bounties + $70 fees equal $32,000 collected = $18,400
   ordinary prizes + $8,000 bounty funding + $5,600 fees. The initial
   bounty amount is funded once. Progressive marker transfers are not a new
   inflow of prize money.
5. **One player's private accounting illustration:** Two $400 entries cost
   $800; after another $60 in expenses, a fictional $950 gross prize gives
   $950 − $800 − $60 = +$90 before tax. Zero winnings gives −$860;
   one entry instead of two would give +$490 with that same $950 payout.
   This is not a claim about Nolan or any other real player.

## Sourcing and contract boundaries

Source review performed November 15, 2026:

- [WSOP Circuit Turning Stone October 2026 structure packet](https://assets.wsopcdn.com/wsop/70956034-40c4-4027-9c56-48a298c28cd1.pdf)
  contains $400, $330-to-prizes plus $70-to-administration entries, with fee
  terms specific to those events. The fictional 120-entry field is not from
  that packet.
- [Historic $400 WSOP Circuit progressive knockout structure](https://www.wsop.com/pdfs/structuresheets/structure_5765_24602.pdf)
  explicitly separates $230 ordinary prizes, $100 bounties and $70 fees. It
  also applies distinctive rounding and a combined-pool guarantee, so the
  new article does not import ordinary-only guarantee or generic 50/50
  award rules into that historical event.
- [PokerStars buy-in display help](https://www.pokerstars.com/help/articles/buy-in-allocation/)
  explains the displayed total versus its underlying fee split.
- [PokerStars KO help](https://www.pokerstars.com/help/articles/trn-knockout/213401/)
  distinguishes cash-prize and bounty allocations; its provider-specific
  examples are not a universal live-room fee schedule.
- [PokerStars payout structures](https://www.pokerstars.com/help/articles/trn-payout-structure/61640/)
  explains the role of an eventual payout table.

Actual guarantees can cover one or more pools or permit deductions; actual
event terms control. No tax advice, individual profit promise, solver decision,
2026 current-venue price comparison, paid API or external data collection was
introduced.

## Reader and discovery integration

- Registered one dated canonical Poker page in the site manifest and the
  original-guide library, with **Tournaments** primary and **Places to play**
  secondary topic routes.
- Added contextual guide-to-guide prose inlinks from choosing a tournament,
  tournament formats, registration/re-entry, KO/PKO accounting, ordinary ICM,
  tournament trip budget, and first-live-tournament planning.
- Added an additional Study desk path from tournament context to the
  guarantee exercise and six outgoing contextual links to older original guides.
- The article's three financial tables reuse the existing focusable,
  horizontally scrollable table pattern. Eight answer checks use native HTML
  `details`, so the questions do not require JavaScript. The Markdown worksheet
  is explicitly registered as a public static download target.
- Existing library, topic hubs, Finder, search index, feeds, about/notes
  discovery, and sitemap receive generated links without new services.

## Measured repository outcomes

Source-graph measures are not search ranking, indexing, AI citations, organic
traffic, or visitor reading results.

| Static measure | Turn 13 | Turn 14 |
| --- | ---: | ---: |
| Original Poker guides | 70 | **71** |
| Distinct guide-to-guide prose links | 418 | **431** |
| Guides with at most one inbound guide link | 0 | **0** |
| Guides unreachable from Poker entrypoints | 0 | **0** |
| New guide's inbound guide links | Not present | **7** |
| New guide's outbound guide links | Not present | **6** |

## Verification and caveats

- Deterministic local build: **249 generated files**, with `--check`
  confirming no further changes after generation.
- Coverage matrix: regenerated from all four Poker manifests and `--check`
  confirmed its match to current source.
- Internal route/fragment check: **15,603 internal links** across **225 HTML
  pages**, **0 issues**.
- Search metadata check: **220 sitemap URLs** with distinct titles and
  descriptions, **0 errors**.
- HTML5 parser: **225 pages pass** with the locally installed `html5lib`.
- New independently specified accounting and discovery suite:
  **11/11 tests passed**.
- Optional Playwright script was authored for 320, 390, 768 and 1440 pixel
  layouts, keyboard answer reveal, source link arrivals, a real Markdown GET
  and JavaScript-disabled use. The local Chromium launch failed before any
  page was rendered because the environment forbids the process-singleton
  socket (`Operation not permitted`). **No successful visual, viewport or
  browser accessibility test is claimed.**
- The generated `technology/ai-website-visibility/index.html` differs from
  its checked-in prior version in a pre-existing source-to-output discrepancy.
  It was not intentionally changed by this Poker turn and should be excluded
  from the Turn 14 commit, as it was in Turn 13.
- The repository prohibition on GitHub Actions, recurring workflows, paid
  services and private data exposure remains in force.

## Suggested Turn 15

Develop a dedicated **pot-limit Omaha wrap, redraw and blocker workshop**.
Specify exact four-card private hands and five-card boards, verify the
exactly-two-hole-card hand-construction rule and enumerate the outs without
double-counting board pairings. Link to the existing Omaha and mixed-games
foundation and to a verifiable official rule source. This continues the
high-priority variant depth work without publishing unsupported solver
frequencies or pretending this fee guide answers postflop hand decisions.
