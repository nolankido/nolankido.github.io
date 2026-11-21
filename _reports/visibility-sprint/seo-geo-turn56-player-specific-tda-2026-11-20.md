# SEO/GEO Turn 56: player-specific TDA Rule 49 reopening rights

**Review date:** November 20, 2026 (Pacific/Honolulu)  
**Base GitHub main:** `fa9600133c53f86fd6c839f5bcc0fe829933d17f`  
**Canonical answer:** https://nolankido.com/poker/poker-rules-and-fair-play/#reopening-per-player  
**Primary authority:** [Poker Tournament Directors Association, 2026 Rules Version 1.1 (September 21), Rule 49 and its illustration addendum](https://www.pokertda.com/view-poker-tda-rules/)

## What the authority check found

The existing site's rule reference accurately warned that a single short all-in usually does not reopen action to a player who already acted. But it did not show the **player-specific cumulative short-all-in case**. A reader could mistakenly infer that a short raise disables all prior players' raise rights. The official 2026 TDA Rule 49 and its illustration addendum explicitly distinguish the amount each player faces since acting and the cumulative effect of two short all-ins.

Using the original illustrative no-limit postflop sequence, A bets 100, B goes all-in to 125, C calls 125, D goes all-in to 200 and E calls 200. None of the two all-in increments is a full 100 raise by itself:

| Test | Independent calculation | Consequence |
| --- | --- | --- |
| B's short all-in increase | 125 - 100 = 25 | Below full 100 |
| D's short all-in increase | 200 - 125 = 75 | Below full 100 |
| Amount A faces after last betting | 200 - 100 = 100 | Full increase, so A may raise |
| Minimum raise-to total for A | 200 + 100 = 300 | A's legal minimum if A raises |
| Amount C faces if A only calls | 200 - 125 = 75 | Not a full 100, so C cannot re-raise |

The difference is **action history**, not different current wagers. House rules and floor decisions govern live rulings, and this example is not a solver strategy, at-table aid or new interpretation of a live hand.

## Actual improvement

1. Add one visible `#reopening-per-player` explanation and one native answer-reveal question to the existing `_source/poker/poker-rules-and-fair-play.html` and its committed generated HTML. No new H2/topic article, new schema, script or duplicate landing page.
2. Add one source-to-published contextual link from `/poker/betting-and-pots/#raise-to` to the named example. The old betting guide's original date and reviewed-source caveat remain intact.
3. Update only the rules article's meaningful revision date in `_source/pages.json`, compiled Article metadata, on-page revision note and `sitemap.xml` to November 20. Preserve original October 8 publication and original October 16 directory-source review.
4. Add a local standard-library `_tests/test_turn56_tda_reopening.py` checking independent arithmetic, correct source attribution, unique fragments, related intro navigation, original/new revision dates, and negative mutation cases. Register it in the no-Actions local release runner and document the provenance.

## Evidence limits and verification

A public primary-source query verified official TDA 2026 v1.1 Rule 49 and the illustration; the existing live rules page and prior Turn 55 video-to-practice release were accessible. GitHub preflight checked paired source/generated text changes, the legal amounts, unique route, original publication and changed revision dates.

A full checkout could not be cloned in the current execution environment because outbound GitHub DNS resolution failed. Therefore the complete deterministic generator, historical unit suite, HTML5 parser, Poker Finder derived index, Playwright mobile/keyboard test, and post-merge exact-byte serving must be **separately checked**, not described as passed. The local change does not prove rankings, traffic, citations, learning outcomes or correctness in a venue with different rules.

### Full-checkout verification

```powershell
py -3 -m unittest discover -s _tests -p test_turn56_tda_reopening.py -v
py -3 -m unittest discover -s _tests -p test_rules_reference.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /poker/poker-rules-and-fair-play/ --only /poker/betting-and-pots/ --only /sitemap.xml --attempts 3 --interval 5
```

## Next

Turn 57: source-check another consequential poker mathematical or factual claim, prioritizing a reproducible mismatch over additional SEO pages.
