# Cash-game and resource-selection pass

Date: October 8, 2026
Baseline: 2a625ce3e8c98373771246a20c0d90c20134522e

## Scope
Three practical guides: first live cash session, game costs, and a five-session
cash-game study route. One blank private-use Markdown worksheet. Twenty existing
resource listings receive concise editorial task-fit notes. Three tool shortlists
separate free learning, entered-range analysis, and understanding game models.
The existing cash-game guide, topic map and Study Desk connect the new work.
Legacy tournament-only breadcrumbs in the general study-tools guide are corrected.
No new application, account, tracking event, live-play assistant or paid service.

## Source review and selection boundaries
Resource identity, access labels, publisher, destination and individual listing
review history remain in resources.json. Selection notes have a separate editorial
date and never silently promote an index-only listing to a page or product review.
All 145 prior resource records are preserved without changing their review dates.
One new primary source, PokerStars Live cash-game house rules, supports the new
procedure guide. The new total is 146 sources and 47 guide-library entries.

The twenty annotated destinations were read as public web pages for task-fit
scope: Pokerology lessons; PokerStars hold'em rules, hand rankings, SPR, rake and
tool policy; The Poker Bank strategy, implied odds and expected value; Upswing
pot odds and effective stacks; GTO Wizard combinatorics, equity realization,
multiway discussion and study documentation; SplitSuit range reading;
PokerStrategy Equilab; Flopzilla; PioSOLVER documentation; and the Crush Live Poker
video catalogue. This is not installation, paid-content access, full-video review,
accuracy certification or comparative product testing. No prices are republished.

Selection notes distinguish a call-price lesson from future-street equity
realization. They do not endorse a source's every strategic conclusion. Free
shortlists are validated against current catalogue access labels; free manuals
are explicitly separated from paid or restricted underlying software features.

## Implementation
resource-selection.json stores twenty task notes keyed by existing resource IDs.
poker_selection.py validates IDs, alternatives, concise text, editorial dates and
free-shortlist membership. Rendering escapes text and reuses canonical metadata.
Native details keep the directory compact, keyboard usable and readable without
JavaScript. The finder indexes original editorial fit notes, not third-party
article bodies. Existing portable selections, source cautions and query privacy
remain in place. Notes and worksheet exports contain no visitor answers.

## Independent examples to verify
- Fee schedule A: min(5% of pot, 6) plus 1; B: fixed 5 for qualifying pots.
  Pots 20, 80 and 200 yield A deductions 2, 5 and 7 and awards 18, 75 and 193.
  B awards 15, 75 and 195. At 120, A awards 113.
- Time charge 7 per half-hour for six intervals is 42 per player; eight players
  generate 112 per hour in aggregate. These are not actual room prices.
- Cash-out 260 minus buy-ins/top-ups 200 and 100 is -40. Wallet-paid charges 28
  make the session cash flow -68; additional transport 12 makes trip flow -80.
  Chip-paid tips and pot deductions already in cash-out are not subtracted twice.
- Pot 60 before bet 30, call 30: 120 final, 25% no-fee threshold. A fictional
  six-unit deduction yields 114 and 30/114 = 26.315789...%.
- Holding one ace leaves three pocket-ace combinations, not six.

## Release gate
Run deterministic build, all unit tests, existing browser/accessibility suites,
and cash_selection_browser. Inspect mobile/desktop rendering, disclosures,
shortlists, search and worksheet download. Require exact-head PR success before
merge, then verify Pages deployment and the live public-byte comparison.
Record executed outcomes in the pull request; this plan alone is not a pass.
