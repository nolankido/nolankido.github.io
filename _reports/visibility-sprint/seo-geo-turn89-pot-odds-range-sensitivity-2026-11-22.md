# SEO/GEO Turn 89: distinguish exact poker prices from unverified opponent assumptions

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Start of branch:** `cbb553a502596cb2c82917d5486462903c5f1fbe` (merged Turn 88).  
**Original indexed article:** `https://nolankido.com/poker/pot-odds-workshop/`.  
**New, standalone original resources:** `/downloads/poker-pot-odds-sensitivity-workbook.md` and `/downloads/poker-pot-odds-sensitivity-verify.py`.  
**Release scope:** two new downloads and two new links within an existing article's end navigation. No new canonical page.

## Substantive problem addressed

The published pot-odds workshop already correctly explained call prices, raise-to arithmetic and pure-bluff pricing. However, those exact prices can be misused as action recommendations when the opponent equity or fold frequency is a guess. Readers needed a fully reproducible way to test how the sign of a modeled decision changes as these assumptions change, and to distinguish the bettor's bluff threshold from the caller's pot-odds threshold. Adding another article repeating the old formulas would inflate surface area without resolving the teaching gap.

## Implemented reader resource

The original, approximately 1,650-word Markdown workbook has:

- A blank after-play record of the pot, actions, extra call, eligible final pot, assumed range, blockers, tie share and missing conditions.
- A **heads-up river call**: 20 BB before a 10 BB bet; P = 30, C = 10, final pot = 40 and break-even equity 1/4. Assumed 20%, 25% and 30% equities produce -2, 0 and +2 BB call EV. An illustrative 22% to 29% equity band gives **-1.2 to +1.6 BB** and correctly crosses zero.
- A **raise-to** model: initial pot 10; hero bets 4; villain raises **to 14**; P = 28, incremental call = 10, final matched pot = 38, and break-even equity 5/19. At hypothetical 25% and 30% equity, call EVs are -0.5 and +1.4 BB. No earlier contribution is charged twice.
- A **pure zero-equity bluff**: bet 6 into a pot of 10, against a fold-or-call response. The bettor needs 3/8 (37.5%) folds. At hypothetical 30%, 37.5%, 40%, 50% fold frequencies, bluff EVs are -1.2, 0, +0.4, +2 BB. The separate **caller** price is 3/11, or about 27.27% equity, not the bettor's 37.5% fold frequency.
- Four additional, independently calculated cases and a complete answer key; stop rules for nonclosing action, rake, side pots, opponent range gaps, ICM, bounty/seat objectives and at-table tools.
- Clear source and evidence boundaries. All inputs are fictional; no opponent database, solver or real measured outcomes are asserted.

The companion standard-library Python 3 script uses exact `Fraction` calculations. `--self-test` checks the three fixed models, conditional outputs and invalid-input boundaries. `--json` gives inspectable exact fraction strings. The script performs no remote requests, file reads/writes or poker solver calls. Readers can verify the original exercises without a paid service.

## Source and release integration

- Add workbook and Python links only to the existing `Continue studying` navigation of `_source/poker/pot-odds-workshop.html` and the generated `poker/pot-odds-workshop/index.html`. The two file changes must remain character-for-character identical within the nav.
- Preserve the old 2026-10-06 Article publication/modification date and all its mathematical body sections; this is navigation to a separately authored resource, not a rewrite of the canonical article.
- The private browser-local Poker Finder index parses article prose but excludes `nav`; no answers enter its 301-entry search dataset and no new sitemap URL is created.
- Register the two downloads as exact GET byte targets in `_scripts/check_live.py`.
- Add `_tests/test_turn89_pot_odds_sensitivity.py` with **11 tests**, register it in the offline release runner, and document source ownership and limitations in `AGENTS.md`.

## Executed arithmetic checks versus pending site release checks

The Python verifier was written and tested locally before committing. Its `--self-test` returned PASS. In a three-file isolated fixture containing the exact source verifier and workbook, **six independent tests ran and passed**: script execution/import boundaries, river call fractions and sensitivity, raise-to pot and cost accounting, bettor-vs-caller threshold distinction, four extra questions and negative input controls.

Authenticated GitHub reads verified that the uploaded verifier source matches this locally tested file exactly. The source/compiled HTML navigation and registered release asset paths are to be checked on the branch after all edits.

The remaining five new tests require the full checked-out site (article source and compiled HTML, full build, Finder contents, exact-byte target inventory and sitemap). The complete local site Python build, HTML5 parser, browser/mobile width and source-to-live byte comparison **have not run** in this environment. No ranking, referral, AI citation, solver win-rate or actual real-world poker benefit is measured or claimed.

## Local acceptance in a complete matching checkout

```powershell
py -3 downloads/poker-pot-odds-sensitivity-verify.py --self-test
py -3 downloads/poker-pot-odds-sensitivity-verify.py --json
py -3 -m unittest discover -s _tests -p test_turn89_pot_odds_sensitivity.py -v
py -3 -m unittest discover -s _tests -p test_workshops.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope all --only /poker/pot-odds-workshop/ --only /downloads/poker-pot-odds-sensitivity-workbook.md --only /downloads/poker-pot-odds-sensitivity-verify.py --attempts 8 --interval 15 --workers 1
```

After merging, inspect the public workbook and code links; content presence confirms publication, not source-byte identity until the matching checkout's GET verifier passes.

## Sprint decision

**Value delivered:** one original, falsifiable poker study workbook and independent, inspectable math script that turn a common vague question, "Is 25% enough?", into a source-and-assumption review. No SEO keyword stuffing, duplicate guide, speculative solver result, login, paywall, CI worker or analytics dependency.

**Next priority:** finish full site checks and source-to-live receipts, then use verified reader questions and first-party search data when available to prioritize the next new explanation. Do not present hypothetical equities or script-produced conditional EVs as evidence of real opponents.
