# PBG-08: An original straight-on-the-board comparison

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Sprint:** Poker Book Growth, Turn 08 of 25  
**Existing primary canonical:** https://nolankido.com/poker/hand-rankings/  
**Existing related rules page:** https://nolankido.com/poker/holdem-basics/  
**Status:** Source/generated page changes committed and targeted live public section verified. Full repository build, Python tests and browser accessibility run still pending.

## Reader problem

The Hand Rankings guide already displays ten familiar hand labels and four visually rendered fictional showdowns, including a board that produces the same two-pair value for both players. One remaining beginner misconception is that a made straight among the five community cards must automatically produce a split pot. That is **not always true**: in Texas Hold'em, a hole card may replace a board card to create a stronger five-card straight. Conversely, two different physical jacks can make equally ranked straights and require a tie.

The official [PokerStars Texas Hold'em rule explanation](https://www.pokerstars.com/poker/learn/lesson/texas-holdem-rules/) confirms that the best five may use zero, one or two hole cards. This is the rule supporting the site-original exercise, not a copied or verified retail book excerpt. The lesson is about showdown comparison, not betting strategy or a live poker hand.

## New two-part, no-wager teaching example

A single native `<aside class="viewer-example" id="board-straight-check">` appears directly after the guide's kicker/tie rules, before the original four showdowns. The question uses one board and two versions of Player B:

| Case | Board | Player A | Player B | Correct result |
| --- | --- | --- | --- | --- |
| Initial | 6♠ 7♥ 8♦ 9♣ 10♠ | J♦ 2♣ | A♣ K♦ | **A wins** with 7-8-9-10-J, a jack-high straight; B plays the ten-high straight on the board |
| Changed opponent hole card | same board | J♦ 2♣ | J♣ K♦ | **Tie**: both players can make a jack-high straight; suits do not decide a winner |

Both are legal, nine-distinct-card, 52-card Hold'em teaching situations. Neither hand is a flush or better. The initial example also clarifies why B's ace and king do not automatically extend the board's 6-7-8-9-10 sequence. The second example changes one rank and deliberately tests whether the reader can distinguish a ranked tie from the different physical five-card combinations.

The answer is in one keyboard-native `<details class="poker-details" id="board-straight-answer">` with a visible `<summary>`. No account, wager, embedded video, JavaScript or tracking event is required. The card codes are retained as fixed `data-board`, `data-a`, `data-b` and `data-b-variant` attributes for reproducible independent testing, not interpreted as real opponent holdings.

## Existing lessons and structure preserved

1. The Hand Rankings guide now provides an explicit `Straight board check` jump in its existing native section navigation, linking directly to `#board-straight-check`.
2. Simplified overlapping kicker/tie prose and corrected a small terminology defect: **four cards of one suit**, not "four matching suits," constitute a potential flush draw rather than a completed flush.
3. Retained all **10** card-ranked visual examples and **four** original independently audited showdowns. The new native exercise is not a fifth `viewer-matchup` case and does not add a `viewer-question` class, maintaining the existing hard-coded viewer-fixture count.
4. Reduced repetition in the final practice instructions while keeping the free card-building route, paused-hand follow-along route and private study-card download.
5. In the separate Hold'em Basics lesson, replaced the generic in-body hand-ranking link with a direct link to `/poker/hand-rankings/#board-straight-check`. Its general Hand Rankings navigation link at the end is still present. The complete fictional hand and chip accounting remain untouched.

These are focused study improvements. The comprehensive no-limit Hold'em guide remains the authoritative long-form integrated reference. The book's first-party page, Amazon ASIN and Umami events were not altered.

## Committed files

- `_source/poker/hand-rankings.html` plus generated `poker/hand-rankings/index.html`
- `_source/poker/holdem-basics.html` plus generated `poker/holdem-basics/index.html`
- New `_tests/test_pbg08_straight_board_hand_rankings.py` with **12** offline regression methods
- Updated `_scripts/local_release_checks.py`, registering the new tests and explicitly including the existing independent `test_viewer_guides.py` evaluator

No new indexed page, schema, stylesheet, JavaScript tracker or GitHub Actions workflow was added. The new topic is a section within the established, most-specific Hand Rankings canonical page rather than a competing "poker hand rankings" page.

### Reading-time and historical-date integrity

The source HTML's rough visible-text estimate changed from about **1,113 to 1,066 words** on Hand Rankings, while retaining and improving the reader tasks. It stays in the existing **5-minute** editorial reading bucket. Hold'em Basics changed from roughly **893 to 895 words**, remaining in its existing **4-minute** bucket.

Because this was a bounded within-article lesson update rather than a complete recheck of all rule references, the historical publication and update dates remain as before. This dated sprint artifact records the actual November 22 addition. Do not advance all date metadata and build derivatives merely to imply source freshness.

## Quality and independent verification

- After the final code revision, authenticated GitHub source readback passed **28 targeted static checks**: new aside/answer IDs, source/public exact new-block parity, one navigation fragment, two correct showdown outcomes, unique physical cards, absence of a flush, ten original ranking examples, four old visual showdowns and answer panels, preserved free learning routes, current canonical registration, and existing reading-time ranges.
- Independently evaluated the suit/rank fixture: Player A's seven cards yield highest straight 11; original Player B's yield highest straight 10; the J♣ variant yields highest straight 11. The first is an A win and the alternate is a tie. No physical card repeats among board + both players in either case.
- Public read-only retrieval returned the public **Hand Rankings** and **Hold'em Basics** pages with the new deep-link URL available. A separate targeted `#board-straight-check` extraction returned the full published two-part question, `First: A wins`, and `After B receives J♣: tie`, showing that this actual section is live.
- These observations establish meaningful link and text visibility; they are **not** an exact whole-page response-byte match and do not prove Google indexing, assistant citations, reader satisfaction or any book purchase.

### Tests written but not executed

The 12 new tests check the independent straight-high rules, unique cards, changed-opponent tie, source/public block equality, mutation negatives for incorrect answers and duplicate cards, navigation anchors, the existing four visual outcomes and ten hand-ranking samples, original free study routes, cross-link in the shorter rule guide, and unchanged minute estimates.

These tests are now part of the existing **manual** release checks along with the prior `test_viewer_guides.py` evaluator. The complete repository Python tests, deterministic `build.py --check`, HTML5 and internal link suites, and a real 320px keyboard/browser exercise were **not executed** in this chat. The website's repository cannot be cloned into the container in this session. Do not label those gates as passed.

In a current full checkout, run:

```powershell
py -3 -m unittest discover -s _tests -p test_pbg08_straight_board_hand_rankings.py -v
py -3 -m unittest discover -s _tests -p test_viewer_guides.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
```

Verify on a narrow mobile browser that the new "Straight board check" jump remains within the usable navigation; tabbing to the `details` summary and pressing Enter reveals the answer; the 10 rank samples and 4 visual showdowns remain readable; and the Hold'em Basics deep link lands at the visible exercise.

## Growth sprint status and next action

The original PBG-02/PBG-04 selected acquisition sample remains **9 of 11** poker study pages with direct book links. This turn improves the relevance and original explanatory depth of an existing page, not its count of outbound Amazon events.

Actual first-party Google/Bing query metrics, Umami click receipts, AI citations, KDP orders and causal growth remain **unknown**, not zero.

**PBG-09:** examine the existing **starting-hands and positional decision** path for the next concrete accuracy or instructional gap. Prefer a changed-input, no-wager teaching case with an independently checkable answer, then keep the beginning-of-study route to the book contextual rather than promotional. Avoid inventing charts, universal ranges or solver endorsements.
