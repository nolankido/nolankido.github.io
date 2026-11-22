# PBG-10: A checkable difference between flush completion and winning equity

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Sprint:** Poker Book Growth, Turn 10 of 25  
**Primary URL:** https://nolankido.com/poker/poker-math-reference/#clean-outs-turn-check  
**Supporting URL:** https://nolankido.com/poker/pot-odds-workshop/  
**Status:** Website source and compiled HTML committed; targeted public exercise content retrieved. Independently runnable verifier executed locally. Full repository and browser suites are not yet executed.

## Why this particular instructional improvement

The existing math reference already distinguishes pot odds, pure-bluff thresholds, minimum defense frequency, pot-limit raise sizes, stack-to-pot ratio, and outs. Its central weakness for a beginner was the lack of a single **exact, full-card showdown example** where a draw completion *is not* a winning out and the resulting difference actually changes the sign of expected value.

This is not a request for more keyword variants or a new overlapping poker page. The PBG-06 ownership ledger already makes `/poker/poker-math-reference/` the focused answer for pot-odds questions and `/poker/pot-odds-workshop/` the extended review route.

The public [PokerStars outs guidance](https://www.pokerstars.com/poker/learn/lesson/calculating-outs/) explains how visible cards and outs change draw probabilities. The [PokerStars pot-odds guide](https://www.pokerstars.com/poker/learn/lesson/pot-odds/) distinguishes the price paid to call from the chance of winning and notes that future bets may matter. [GTO Wizard's equity-realization discussion](https://blog.gtowizard.com/equity-realization/) likewise emphasizes the difference between raw equity and a decision with future action. None of these pages certifies this site's own invented cards as a real or solver-approved hand.

## New exercise and exact result

The original, no-wager `#clean-outs-turn-check` aside on the existing Poker Math Reference page asks a reader to work out the following fictional face-up turn model:

| Item | Value |
| --- | --- |
| Hero cards | A♥ J♥ |
| Opponent cards, known for this model only | 7♦ Q♣ |
| Turn board | K♥ 7♥ 7♣ 2♦ |
| Pot before opponent bets | 60 chips |
| Opponent bet | Their remaining 20 chips, all-in |
| Incremental call | 20 chips |
| Future betting | None because opponent is all-in |
| Fees, side pots, ties, payout adjustment | Omitted from the model |

Known physical cards: 2 Hero + 2 opponent + 4 board = **8**. Unseen river cards = **52 minus 8 = 44**. This is different from the typical 46 unseen cards when only Hero's cards and the four-card turn board are known.

**Nine heart rivers complete a flush:** 2♥, 3♥, 4♥, 5♥, 6♥, 8♥, 9♥, 10♥ and Q♥.

**Two heart completions are dirty:** 2♥ and Q♥ give the opponent a full house (sevens full of twos or sevens full of queens), beating Hero's ace-high flush. The **seven actual winning rivers** are 3♥, 4♥, 5♥, 6♥, 8♥, 9♥ and 10♥. All other 37 possible rivers lose; there are no ties.

| Distinct calculation | Exact expression | Result |
| --- | --- | --- |
| Flush-completion rate | 9/44 | 20.45% |
| Actual showdown-winning rate vs *these revealed cards* | 7/44 | 15.91% |
| Final eligible pot after a call | 60 + 20 + 20 | 100 chips |
| Break-even call equity | 20/100 | 20.00% |
| Correct call EV relative to folding | (7 × 80 − 37 × 20) / 44 | **−45/11 ≈ −4.09 chips** |
| Incorrect EV if all nine hearts were called clean | (9 × 80 − 35 × 20) / 44 | **+5/11 ≈ +0.45 chips** |

Counting nine heart completions as nine *wins* changes the sign of the resulting EV estimate. It is not a small rounding issue. The lesson is that an outs count must match the actual showdown-winning event, and the known-card denominator must match the assumed information set.

**Scope:** This is a face-up, fictional teaching model, not information available to a normal live opponent, a solved equilibrium action, evidence about an unknown player's range, or advice to fold in a real cash or tournament game. For a normal unknown villain, an actual range and betting frequencies are required. If future betting is possible, a single flop call does not buy two cards for free. Tournament prize equity is separate from this chip-value calculation.

## Actual committed improvements

1. Replaced a general outs paragraph in `_source/poker/poker-math-reference.html` and `poker/poker-math-reference/index.html` with one `<aside id="clean-outs-turn-check">` and its native `<details id="clean-outs-turn-answer">` teaching example. The block carries fixed, nonpersonal `data-hero`, `data-villain`, `data-board`, `data-pot-before-bet` and `data-opponent-bet` attributes so its math can be checked.
2. Created [the free study worksheet](../../downloads/holdem-clean-outs-turn-study.md) at `/downloads/holdem-clean-outs-turn-study.md`. It includes original prompts, every heart card, the two full-house runouts, exact EV, the false-positive raw-out comparison, and future-betting/payout caveats.
3. Created [the standard-library offline verifier](../../downloads/holdem-clean-outs-turn-verify.py) at `/downloads/holdem-clean-outs-turn-verify.py`. It enumerates all 44 legal rivers; compares the best five of seven for each player with a genuine five-card hand-ranking evaluator; validates exact fractions, draws and winners; and emits JSON with `--json`. It performs no network requests, account access, wager, output file writes or solver calculations.
4. Replaced one paragraph in the existing `/poker/pot-odds-workshop/` source and generated HTML to explain 47 unknown cards in a flop-only information set versus 44 in this fully face-up turn example, with a direct link to `#clean-outs-turn-check`. Its Omaha wrap link remains present.
5. Registered both new downloadable files in `_scripts/check_live.py` to make them exact-byte read-only site-health targets.
6. Added `_tests/test_pbg10_clean_outs_turn.py` with **15** focused offline methods. It validates page source/public parity, fixture data, independent river enumeration, seven actual winning cards, two dirty hearts, exact fractional EV and its erroneous sign reversal, negative tampering cases, preserved original math and book links, available public downloads, supporting workshop route and existing reader-time tier.
7. Registered the standalone verifier and test module in `_scripts/local_release_checks.py`. No GitHub Actions, paid service or new analytics events were installed.

### Concise restructuring rather than content inflation

To keep the math reference useful as a quick lookup, I tightened its explanatory introduction and condensed tangential PLO, Omaha hi-lo and stud link blurbs. The original references, 148,995 Omaha four-card combinations, 3-of-40 hi-lo example, C(7,5) = 21 stud subset calculation, existing three native viewer-question exercises, exact math table, and single optional link to the beginner book remain.

The current source rough visible-text estimate is **1,101 words**, within the existing **five-minute** reading bucket at 225 words/minute; there was no need to alter sitewide generated reader metadata. The related Pot Odds Workshop retains its original six-minute label and the two source/public copies were changed together.

No new canonical page, heading duplication, editor-freshness date claim, Amazon direct link, sales testimonial, affiliate redirect or paywall was created.

## Verification done, precisely

- The actual downloaded verifier source was run as Python in a local execution environment. It returned `status: pass`, 44 unknown rivers, nine heart completions, seven wins, 37 losses, no ties, dirty hearts `2h` and `Qh`, exact equity `7/44`, call price `1/5`, true chip EV `-45/11` and incorrect raw-heart EV `5/11`. Tampering with the known opponent cards or bet amount caused its audit to fail. Wheel and royal-flush scoring smoke checks also passed.
- The SHA of the independently executed Python verifier file is the **exact same Git blob SHA** as the committed `downloads/holdem-clean-outs-turn-verify.py` file after the final audit-binding correction. This establishes that the script actually executed matches the committed source bytes.
- Authenticated GitHub readback passed **26** targeted static assertions over the original math reference and generated page, study sheet, verifier, existing math and book links, three legacy question classes, download registry, new tests, manual runner and original canonical.
- Live read-only public extraction of `/poker/poker-math-reference/#clean-outs-turn-check` confirmed the newly published section, the two full-house explanations, exact 7/44 versus 9/44 result, 20/100 price, negative chip EV and both download links.
- The live Markdown worksheet was retrievable as readable text and its answer key included **7 wins, 37 losses and no ties**. The public .py download link appeared in the live page, but generic page-extraction tools did **not** independently retrieve the .py file bytes as a document. Its direct HTTP download behavior therefore remains a browser acceptance item, despite correct committed bytes and registration. Do not claim a complete public .py download byte match from an extraction failure.

**Not executed here:** the full `test_pbg10_clean_outs_turn.py` test module against a complete cloned checkout, `_scripts/build.py --check`, existing sitewide Python/HTML5/internal-link suites, exact-byte production publication comparison, or narrow-screen and keyboard accessibility testing in a real browser. Local repository clone could not resolve github.com. Those gates are distinct from the successfully executed standalone verifier.

## Manual release checks

From a complete checkout:

```powershell
py -3 downloads/holdem-clean-outs-turn-verify.py --json
py -3 -m unittest discover -s _tests -p test_pbg10_clean_outs_turn.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
```

Also verify that both `/downloads/holdem-clean-outs-turn-study.md` and `/downloads/holdem-clean-outs-turn-verify.py` download through a normal browser and open in a text editor, and that the native answer reveal can be opened by keyboard at 320px without horizontal scrolling.

## Sprint status and next work

The previously frozen 11-page acquisition cohort still has **9 of 11** selected poker learning pages linking directly to the first-party book page. This turn strengthens a preexisting, search-intent-aligned educational page, rather than adding another blanket book link.

Actual Search Console impressions, click-throughs, AI citations, Umami events and KDP book orders are still **unmeasured**, not zero. The model does not establish an improvement in visitor satisfaction, rankings or book sales.

**Next Turn, PBG-11:** Audit the beginner practice/checkpoint progression and the first-session cost guide, using current source and live content. Prefer another substantive checkable learner outcome and the minimum useful navigational connection, without duplicating the math reference or promoting the book at the expense of the free learning resources. Consider authenticated Google Search Console page/query data if connected and date-qualified.
