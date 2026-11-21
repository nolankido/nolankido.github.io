# SEO/GEO Turn 52: auditable 10 BB ICM lesson and missing sitemap registration

**Review date:** November 20, 2026, Pacific/Honolulu  
**Base GitHub main:** `33b146f276503b90fd1f051a7a4df43192e0b420`  
**Roadmap:** Turn 52 of 37 to 61  
**Canonical page:** https://nolankido.com/poker/10bb/

## Opportunity confirmed before editing

The already published one-hour 10 BB video companion is independently retrievable at its canonical HTTPS route. It has a mathematically specified fictional three-player ICM model, but the prior page offered no downloaded calculation to verify the three-player prize equations or the effect of one changed probability assumption. Its 50%/55% outcomes can also be confused with the separate *four-player* bubble case elsewhere on the site.

A current-source repository audit found another concrete discoverability defect: `/poker/10bb/` was absent from `sitemap.xml`, the source-aware expected-indexed set in `_scripts/check_search.py`, and the exact-byte live release inventory. It was also absent from the normal `_source/pages.json` manifest. A public page being served does not itself prove indexing, so adding a controlled sitemap record is worthwhile without claiming an engine will index it.

## Substantive educational improvement

The current video companion retains the established three-player payout assumptions: $100/$60/$40, no ante, bounty, deal or ties, three positive starting stacks BTN/SB/BB = 5/20/10 BB before posting. Hero is BB, the button folds, SB shoves and hero owes nine BB to finish a 20 BB matched pot. State outcomes in hero/SB/BTN order: fold = 9/21/5, call-and-win = 20/10/5, call-and-lose = 0/30/5 (third-place $40 is already awarded).

An **independent exact-fraction verifier** at `downloads/ten-bb-playbook-icm-verify.py` enumerates all six possible finish orders of the two remaining three-player ICM states using Python's `fractions.Fraction`; it handles the elimination state as a fixed $40 prize. The script never imports a solver, sends requests, reads sensitive input or writes files.

| Check | Exact computation | Result |
| --- | --- | --- |
| Fold | three-player ICM | $64 |
| Call and win | three-player ICM | $1696/21 = ~$80.761905 |
| Call and lose | third-place award | $40 |
| Chip call price | 9/20 | 45% |
| Prize-equity break-even | (64 - 40) / (1696/21 - 40) | 63/107 ≈ 58.8785% |
| Extra required win probability | 63/107 - 9/20 | ≈13.8785 percentage points |

Changed-parameter exercise with those **same** stacks and prizes:

| Invented p(win) | Calling chip EV vs folding | Prize EV call | Prize EV vs folding |
| --- | --- | --- | --- |
| 45% | 0 BB | $58.34 | -$5.66 |
| 50% | +1 BB | $60.38 | -$3.62 |
| 55% | +2 BB | $62.42 | -$1.58 |
| 60% | +3 BB | $64.46 | +$0.46 |

Existing 50% main-lesson and 55% final-question answers are unchanged. The page adds 45% and 60% to reveal the boundary, with its own `#icm-reproduce` heading and download. It explicitly contrasts the distinct four-player, three-paid bubble example at `/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble`, whose threshold is about 56.40%. Neither example is an observed opponent range, solver output, video-verified hand or real tournament recommendation.

## Publication and source safeguards

`_scripts/tenbb_companion.py` validates one canonical Article identity, the pinned original November 19 date, the updated November 20 date, the new ICM anchor and its script before including the manually authored page in the generator's sitemap. The read-only live inventory now adds the fixed canonical page and checker. The search snapshot gains `manual_tenbb_pages=1` and raises `sitemap_urls` from 229 to 230, without altering the manifest-managed 225 pages or suggesting Google has indexed 230 URLs. A new `_tests/test_turn52_10bb_playbook.py` independently recalculates the same outcomes via **closed-form three-player ICM**, checks four probabilities, rejects modified source identity and missing ICM anchor, asserts sitemap parity and the exact-byte inventory, and preserves the no-GitHub-Actions rule. Registered with `_scripts/local_release_checks.py`.

The standalone page is public but not a manifest-generated guide. Do not overwrite it via `_source/poker` or add a competing canonical. No unverified retail offer, private footage, analytics disclosure, fake review, new download gate, crawler trick or scheduling service was introduced.

## Checks and limits

The standalone Python verifier was independently executed with Python 3 in an isolated working environment before this GitHub change: it printed `63/107`, `58.87850467289719` and the four expected prize results above with a zero exit code. Mathematical outputs were cross-checked separately against a direct three-player formula using rational arithmetic. Connected GitHub source preflight will verify exact unique replacement markers, page canonical/Article metadata, new code registration, and sitemap/expected-count agreement before PR creation.

The full cloned repository generator, complete unit/history suite, HTML5 and Playwright browser checks cannot be claimed as passing unless executed. A live 10 BB GET was observed through a public browser-backed fetch before this edit; post-merge deployment and exact-byte parity are separate. Google indexation, rankings, Search Console clicks/impressions, real reader behavior and AI citations are **not measured** by this turn.

### Local acceptance commands

```powershell
py -3 downloads/ten-bb-playbook-icm-verify.py
py -3 -m unittest discover -s _tests -p test_turn52_10bb_playbook.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /poker/10bb/ --only /downloads/ten-bb-playbook-icm-verify.py --only /sitemap.xml --attempts 3 --interval 5
```

## Next roadmap improvement

Turn 53: publish a source-backed AI-assisted poker-video production case with actual approved before/after artifacts. Do not present proposed graphics, unverified captions, unpublished exports or editor checklists as released-video proof.
