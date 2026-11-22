# PBG-09: Same A♠ J♠, different button decision

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Sprint:** Poker Book Growth, Turn 09 of 25  
**Primary teaching URL:** https://nolankido.com/poker/starting-hand-decisions/#study-record  
**Supporting positioning URL:** https://nolankido.com/poker/position-and-stacks/  
**Book landing URL:** https://nolankido.com/books/how-to-play-no-limit-texas-holdem/  
**Status:** Changes committed to source and generated HTML. The live case and supporting crosslink were independently retrieved. Complete local Python, deterministic build and interactive browser suites still await execution.

## Reader problem and instructional objective

The existing beginner starting-hands guide already contained eight useful hypothetical questions on cards, position, earlier action, call prices, big-blind depth, effective stacks, future payments and a complete preflop study record. But its eighth example ended with **one raised-pot scene**, even though a central lesson of the chapter was that the same cards and position can face a very different decision when an earlier player folds rather than raises.

This turn replaces only the final Exercise 8 with a controlled **two-scene transfer comparison**, retaining all other seven questions. The goal is not to prescribe a call, fold or raise. The goal is to make a learner reconstruct what objectively changes before examining an opponent range, chart or solver: pot size, immediate call cost, who can still raise and whose stacks matter.

The core mechanics match public Hold'em explanations for blinds, preflop actions and the big blind's live bet. These are procedural concepts, not strategic recommendations:
- https://www.pokerstars.com/poker/learn/lesson/texas-holdem-rules/
- https://www.pokerstars.com/poker/games/texas-holdem/
- https://www.pokertda.com/view-poker-tda-rules/ (tournament procedures, not authority for every cash room)

## The actual changed-input exercise

Six handed no-limit cash game, blinds **1/2**, no ante and no fees. Hero is on the **button** with **A♠ J♠**, has a 150-chip starting stack (75 BB). The cutoff started with 60, small blind 200, and big blind 400. The two early players fold.

| Input or consequence | Scene A: cutoff raises to 6 | Scene B: cutoff folds |
| --- | ---: | ---: |
| Current pot before button acts | **9**, composed of cutoff 6 + SB 1 + BB 2 | **3**, composed of SB 1 + BB 2 |
| Immediate button call to match current wager | **6** | **2**, the live big blind |
| Pot immediately after button calls, before blinds respond | **15** | **5** |
| Players behind hero yet to act | Small blind and big blind | Small blind and big blind |
| Additional participant who may act again if action is reopened | Cutoff, if a blind raises | None from the cutoff, who folded |
| Hero starting depth | 75 BB | 75 BB |
| Relevant starting effective stacks | 30 BB vs cutoff; 75 BB vs either blind | 75 BB vs either blind; cutoff folded |
| Preflop action category | Facing an open-raise | Unopened pot; a new raise would be an open-raise |

**Accuracy boundaries:** These are pots at the instant described, not guaranteed final preflop pots or expected showdowns. If the button calls, the small blind and big blind can still act, and either can raise. Calling now does not guarantee a flop at that price; subsequent streets can require further betting. In Scene A, the original raiser may respond if action is reopened. A pot-price fraction calculated from a preflop call **cannot** be used as a complete all-streets equity rule without modeling future action.

The educational conclusion is conditional and testable: a chart for a button facing an unopened pot does not answer the button facing a cutoff raise, even when the exact A♠ J♠ hole cards, position, blind sizes and starting stacks remain unchanged. The only modified prior action is the cutoff's decision to raise versus fold.

## Implemented website changes

1. Replaced the existing `#study-record` Exercise 8 text and native answer panel in `_source/poker/starting-hand-decisions.html` and `poker/starting-hand-decisions/index.html`, preserving the original `id="check-record"` and `class="poker-details viewer-question"`.
2. Added seven fixed numeric `data-*` values to the same native answer element: small and big blinds, hero stack, three relevant opposing starting stacks, and cutoff raise-to total. These are public teaching inputs, not visitor data, telemetry or actual hands.
3. The answer now separately explains raised and unopened pot totals, call costs, still-to-act blinds, effective starting stacks and the unknown ranges/future actions. It links to the already existing free `/poker/facing-preflop-raises/` workshop for further changed-action study.
4. In `_source/poker/position-and-stacks.html` and matching `poker/position-and-stacks/index.html`, replaced one general statement with a contextual native link to `/poker/starting-hand-decisions/#study-record`. It contrasts a raise with a fold and makes the benefit of position an information question, not a claim that the button always wins.

The source length of Starting-Hand Decisions changed by approximately **minus 14 words** and Position and Stacks by approximately **minus 6**. The existing published labels, about **17 minutes** and **5 minutes**, remain in place. No new H2, indexed page, metadata-generated route, stylesheet, script, active tracker or GitHub Actions was added.

The guide still has **exactly eight** native `viewer-question` exercises. The established six-stage beginner-course progression, the preflop browser regression's `150 / 2 = 75 BB` teaching value, the private study template, the original free course routes and the optional first-party author-book link all remain intact. No direct Amazon link, affiliate tag or promoted event was added to either free article.

## Verification actually performed

**Authenticated GitHub main readback:** After changes, all four source/compiled HTML files were retrieved. The entire revised final-section body and the `<details>` block matched between source and published pages, the related deep link matched in both Position and Stacks copies, and the original eight question IDs and count remained intact. A **32-check** static verification pass confirmed the math, strings, canonical URLs, free study route, book link, current reading-time labels and manual-release registration.

**Independent numeric result:** With blinds 1/2 and cutoff raise 6, the raised pot is 6 + 1 + 2 = 9, button call 6, and new pot 15. Without the raise, the unopened pot is 1 + 2 = 3, button call 2, and new pot 5. Hero starts 150 / 2 = 75 BB, with 30 BB effective against the 60-chip cutoff if still in and 75 BB effective against either deeper blind. These are arithmetic facts, not strategy evaluations.

**Read-only public retrieval:** The live Starting-Hand Decisions page exposed the changed final exercise, raised 9/6/15 arithmetic, unopened 3/2/5 arithmetic, and both effective-stack comparisons. A separate public retrieval found the new contextual deep link on Position and Stacks and the existing free preflop follow-up and author-book links on the main Starting-Hand Decisions page. No real poker wager or site analytics click was generated.

### Regression coverage authored, not executed

Added `_tests/test_pbg09_button_action_contrast.py` with 12 focused offline tests for source/public parity, math computed from the fixed inputs, effective stacks, two different prior-action states, tampered arithmetic and numeric fixture negative controls, original eight native questions, deep-link destinations, book and free-course integrity, reading-time metadata, and release-check registration.

Added this test file to `_scripts/local_release_checks.py`. The runner's existing `--browser` option discovers `_tests/preflop_browser.py`; that browser test still expects the preserved `150 / 2 = 75 BB` value.

**Not executed in this session:** Full Python test suite, complete deterministic `_scripts/build.py --check`, HTML5 parser, internal link scanner, Playwright keyboard/320px visual reflow, and exact full-response byte comparison of deployed HTML. The present read-only extraction and static validations are evidence of the visible change, but not proof of these broader acceptance gates.

From a current, complete checkout:

```powershell
py -3 -m unittest discover -s _tests -p test_pbg09_button_action_contrast.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
```

For manual keyboard verification, visit the new `#study-record` link from Position and Stacks; activate Exercise 8 using Tab and Enter; check each arithmetic result without scripts; and verify the free after-play workshop. Inspect the layout at 320 CSS pixels.

## Growth and next action

This is an original beginner teaching improvement in an established route already designated by PBG-06 as the primary canonical answer for starting-hand context. It does not increase the older PBG-04 selected book-link coverage metric of **9/11**, and it does not claim actual Google/Bing demand, assistant citations, Umami clicks or KDP orders. All such outcomes remain unmeasured, not zero.

**Next, PBG-10:** Strengthen the focused free pot-odds and one-card-draw material with an independently reproducible boundary check that distinguishes a mathematical call price from clean outs, future betting and actual tournament payout effects. Avoid copying or competing with the comprehensive guide. Keep the book link contextual, not a paywall.
