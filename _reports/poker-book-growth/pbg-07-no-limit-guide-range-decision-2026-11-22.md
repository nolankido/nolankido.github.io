# PBG-07: Make the comprehensive no-limit Hold'em guide teach a real decision boundary

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Sprint:** Poker Book Growth, Turn 07 of 25  
**Existing canonical:** https://nolankido.com/poker/no-limit-holdem-guide/  
**Book:** https://nolankido.com/books/how-to-play-no-limit-texas-holdem/  
**Release:** Source and generated HTML committed; read-only public page extraction confirmed the new exercise and related routes. A full repository build, Python test run and browser QA remain outstanding.

## Reader problem and editorial finding

The existing long-form no-limit Hold'em guide is already substantive, with rules, a complete chip-accounted hand, rankings, range concepts, outs, pot odds, expected value, betting, stacks, tournaments, limits and hand review. It already explains a $30 river bet into a $60 pot: a $30 call makes the final pot $120 and requires 25% equity before rake and under the no-future-bet, no-tie assumptions.

The gap was **not** another definition of pot odds. Readers need to understand why a correct 25% price can support a call against one range and a fold against another, without pretending to know the opponent's actual bluff frequencies. This integrates the guide's earlier work on ranges, price and outcomes. It also offers a falsifiable alternative to blanket advice like "call when you could be facing a bluff."

Current independent instructional reference checks support the call-price calculation and the conceptual bluff-catcher distinction:
- https://www.pokerstars.com/poker/learn/lesson/pot-odds/
- https://blog.gtowizard.com/mathematical-misconceptions-in-poker/
- https://lp.gtowizard.com/glossary/pot-odds/

These outside references are conceptual checks, not an independent validation of the actual fictional betting weights in this article or a solver verdict.

## Changes in the existing guide

1. **First-screen decision route:** Expanded the original "Choose a useful way to learn" table by one row, "Practice a starting-hand choice", pointing to eight existing changed-input exercises at `/poker/starting-hand-decisions/`. The six-stage course and other original paths remain in their original positions. This supports PBG-06's distinct primary ownership of the starting-hand question.
2. **River bluff-catcher example:** Replaced a largely abstract discussion of weighted bluff probability in the existing worked-review section with a more economical explanation of betting-range weights and one accessible native `<details>` / `<summary>` challenge, `#guide-check-bluff-mix`. The reader attempts the task before opening the explanation.
3. **Fictional two-range comparison:** Two separate heads-up opponents make the same $30 river bet into $60. Hero has a bluff-catcher that beats all bluffs and loses to all value hands, with no ties, fees or side pots. Betting-case weights, not actual card combinations or observed opponents:
   - 2 bluff weights, 10 value weights: win share `2/12 = 16.67%`; `EV(call) = (2/12 × $90) - (10/12 × $30) = -$10` relative to folding.
   - 3 bluff weights, 9 value weights: `3/12 = 25%`; call is exactly break-even.
   - 4 bluff weights, 8 value weights: win share `4/12 = 33.33%`; `EV(call) = (4/12 × $90) - (8/12 × $30) = +$10` relative to folding.
   - Both opponents offer the same 25% break-even price. The different hypothetical betting ranges, not a change in call-cost arithmetic, change the result.
4. **Practice handoff:** The answer links to the real `/poker/turn-and-river-decisions/#catching-a-bluff` section for a distinct follow-up exercise. Its target fragment was inspected in the existing published specialist guide.

The example is a thought experiment, not an actual opponent's twelve combinations, a hand history, coaching verdict, promise of profit, or table-ready decision tool. An estimate for an actual river line still requires available cards, earlier actions, possible blockers, betting frequencies and the conditions of the game. Readers can examine the actual original math and its assumptions without a purchase.

## Source and release scope

Changed exactly two synchronized locations:
- `_source/poker/no-limit-holdem-guide.html`
- `poker/no-limit-holdem-guide/index.html`

Added one regression file and registered it in the existing local release runner:
- `_tests/test_pbg07_no_limit_guide.py` (12 offline test methods)
- `_scripts/local_release_checks.py`

The added material changed the source length by approximately 128 words after copy editing. The original `49 min read` label remains consistent with the existing 225-words-per-minute editorial reading-time estimator. No new H2/H3 or canonical URL was added, so the current article outline and its URL/fragment contract remain intact.

The prior article publication and last-reviewed metadata remain recorded as October 14 and November 20, 2026. They were **not advanced solely for a bounded within-section exercise** that did not entail a comprehensive source re-review. The dated sprint report provides the truthful November 22 addition record instead of implying all existing linked rule sources were rechecked today. Future substantive full-guide revisions should update the page metadata and rebuild the derived site outputs together.

No Amazon link was added directly to this free article. Its existing single unfragmented link to the first-party book page, the separate site-original sample link and free worksheet remain unchanged. No source material from the book was represented as an excerpt, and no new paid service, promotional interstitial, visitor-tracking event or GitHub Actions workflow was introduced.

## QA and actual evidence

**Committed readback:** 23 targeted source-level assertions passed after the final edit, including source/public exercise parity, full 25% threshold arithmetic, both EV cases and the exact zero boundary, fictional assumptions, the free specialized destinations, unchanged book links, one unique exercise ID, unmodified heading counts and a 49-minute estimated reading time. The targeted source/public paragraphs were compared as exact strings after the edits.

**Read-only public check:** The served canonical guide contained the updated "Two fictional opponents" question, displayed both `-$10` and `+$10` results, linked the starting-hand specialist and turn/river bluff-catching specialist, and retained the first-party book link. This is actual public content visibility, not proof of an exact complete HTML byte match or user engagement.

**Regression module authored:** Twelve local tests exercise source/public parity, fraction-exact bluff-mix calculations at 2/12, 3/12 and 4/12, mutation controls for a wrong payoff or fraction, fictional-range provenance, free specialist route and fragment, preserved original practice, unchanged book identity, heading outline, reading-time label, runner registration and no GitHub Actions.

**Unexecuted acceptance gates:** The full local Python tests, `build.py --check`, full HTML5 and internal-link scanners, and Playwright reflow/keyboard tests were not executed against a complete matching checkout. Source checks do not replace these gates. Public search clicks, AI assistant citations, attributed Amazon visits, Umami events, and KDP orders remain **unmeasured**.

## Manual verification in a complete local checkout

```powershell
py -3 -m unittest discover -s _tests -p test_pbg07_no_limit_guide.py -v
py -3 -m unittest discover -s _tests -p test_turn49_topic_book_paths.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
```

In the browser, verify the original "Choose your route" table still works at 320px and desktop; opening the new native reveal requires no script; the question remains understandable if styles fail; and both specialist links land on the intended sections. If the full build shows any generated drift, rebuild using the existing local script and compare carefully before release.

## Next turn: PBG-08

Improve the existing focused beginner reference cluster, beginning with the highest-impact **rules, hand rankings and action sequence** page gap rather than adding another overlapping "ultimate poker guide." Use real mistakes observed in existing site content, a checkable teaching task and a clearly scoped canonical answer. Preserve the PBG-06 primary route ownership and avoid expanding the standalone author-book page into a duplicate free rules encyclopedia.

Keep the 9-of-11 link coverage from PBG-04 as a separate source-only discovery measure. This improvement does not establish a rise in web impressions, rankings, clicks, reader satisfaction or book sales.
