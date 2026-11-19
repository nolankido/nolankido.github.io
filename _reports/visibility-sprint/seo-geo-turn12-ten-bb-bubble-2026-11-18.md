# SEO/GEO Sprint Turn 12: A ten-blind bubble decision with checkable prize math

- **Date:** November 18, 2026 (Hawaii)
- **Property:** https://nolankido.com/
- **Sprint position:** Turn 12 of 25
- **Base repository checkpoint:** `cc87b67`, Turn 11 on `main`
- **Canonical destination:** https://nolankido.com/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble
- **Status:** Implemented and locally checked. GitHub publication, live deployment, actual mobile browser rendering and search-performance outcomes require separate confirmation.

## Editorial decision

The Turn 04 opportunity map selected the **existing** `/poker/six-to-ten-bb-tournament-decisions/` canonical to answer the question, “What changes at 6 to 10 BB near the money?” The original page already contained a complete BBA chip ledger, several distinct legal action trees and a source-bounded link to Nolan's 6-4 offsuit Portland Meadows hand. Creating another generic “10 BB shove chart” page would compete with that destination and could misrepresent an unknown live-player range as a solved result.

Turn 12 therefore strengthens the existing guide with a direct bubble answer, one separate fictional four-player cash-prize ICM calculation, a printable blank study sheet, an offline exact-arithmetic script, and two natural Poker-hub arrivals. The recorded live hand remains a different, unsolved decision. The original guide publication date is retained; its modification date advances for substantive new material.

## What readers can now inspect

1. **Immediate answer:** at ten blinds the action tree and tournament objective must be specified independently. A first-in shove can win through folds; a call against an existing shove cannot. The guide links directly to the new money-bubble analysis near the top.
2. **Reproducible counterexample:** four players remain with three paid; ordinary cash prizes are $50/$30/$20/$0. In the newly reset no-ante fixture, SB/CO/BTN/hero BB begin with 40/30/20/10 BB. CO and BTN fold; SB shoves; hero already posted 1 BB and can call for 9 BB more. The covering small blind's unmatched 30 BB returns on a call.
3. **Chip and prize comparisons:** a call creates a 20 BB contested pot and needs **9/20 = 45%** showdown win chance on a closed-action chip basis. Classic ICM modeled prize values for hero are $12.286143 after folding, $21.785714 after calling and winning, and $0 after calling and losing. The resulting exact ICM threshold is `76518591/135682300`, or about **56.40%**. All branches conserve the original 100 BB. A strictly hypothetical 50% win chance clears the chip threshold but not this modeled prize threshold.
4. **Source boundaries for an actual hand:** the Portland Meadows companion reports 13 remaining and 10 paid, 8,000/15,000 blinds with a separate 15,000 BBA, and an approximately 148,000-chip SB stack. The conditional 9.87 BB division is arithmetic. Precise stack timing, all payout steps, opponent coverage, complete board/suits and the full calling range are not established. The new four-player no-ante calculation must **never** be used as a verdict for Nolan's 6-4 offsuit shove.
5. **Downloadable work:** `downloads/ten-bb-bubble-icm.py` prints the complete fixed model with exact fraction results and never calls a remote service or writes data. `downloads/ten-bb-bubble-study-sheet.md` is a printable after-play worksheet separating recorded, calculated, assumed and unknown inputs.
6. **Natural routes:** the Poker hub links to the new section from the short-stack choice and the source-limited 6-4 hand path. The guide links to the episode companion, Poker Foundations, the poker math reference, the after-play Practice Room and the separate satellite seat-equity lesson.

## Independent numeric and editorial verification

The public script computes finish probabilities by recursion over remaining players with exact Python `Fraction` arithmetic. A new independent unit test computes all **24 complete finish-order permutations** and compares every player's finish distribution and modeled prize value with the script. Checks verify chip conservation, total prize conservation, a winner-only prize model equal to chip share, 9 BB additional call, 20 BB final pot, 30 BB refund and the displayed roundings. The test requires the real-hand verdict to remain explicitly unknown.

| Check | Observed result in the prepared local tree |
| --- | --- |
| New Turn 12 tests + existing 6–10 BB unit tests | 16 tests passed: five new and eleven existing |
| Fixed ICM script | Runs with Python standard library; exact fractions and JSON result verified |
| Main source builder | 253 outputs built; subsequent `--check` found zero drift |
| Static search | 224 sitemap URLs, unique titles/descriptions, zero findings; sitemap count unchanged |
| Internal links | 231 HTML pages, 16,175 links, zero unresolved targets |
| HTML5 parser | 229 pages, zero failures |
| Existing separate page ownership | Standalone player, Portland video companions, laptop case and reply audit build checks passed during the broader release attempt |
| Browser at 320/390/768/1440 | Attempted; Chromium launch failed with local socket permission error, so the visual result is unknown |
| Default broad release checks | Attempted but not a clean pass: prior hardcoded Poker Find count, stale unrelated Resources date expectations and historical Git object requirements in a shallow clone. The run was interrupted after failures were established. These are not claimed as regressions caused by Turn 12. |

The two new downloadable files are registered with the site's existing read-only asset inventory. The preexisting no-GitHub-Actions rule remains intact. No publication time was rewritten and no page was deleted or redirected.

## Search and answer-engine limitations

The new section is intended to answer a specific searcher question and make an original computation straightforward to inspect and cite. That does not establish higher Google or Bing ranking, actual indexing, CTR, traffic, AI citation rate, reader satisfaction or any meaningful poker edge. Authenticated first-party traffic and AI-answer reports were unavailable; the Turn 04 query ranking remains a qualitative editorial hypothesis. The new page remains educational material for **after-play review only**.

## Next turn

**Turn 13:** select one newly verified public NolanPoker release that lacks a deep written companion. Check the **actual current video**, original hand record, suits, action, payouts and privacy before adding a canonical companion. Do not reuse archived timestamps or invent a solver/ICM result. If current footage cannot be verified, document the evidence gap instead of publishing a fictional firsthand account.
