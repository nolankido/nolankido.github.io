# Poker finder: use the existing public page title

Prepared October 16, 2026 UTC. This follows the search repair in PR #103 and
advances the technical portion of roadmap cycle 12. Qualified teaching review,
actual beginner observations and human relevance judgments remain pending.

## Problem and change

The dedicated ICM guide already publishes the page title **Tournament Equity
and ICM | Nolan Kido** in the shared manifest and generated HTML head. Its
visible heading is **When more chips are not enough.** The Poker finder used
the visible heading but omitted the public page title from title ranking.
For **what is ICM**, this guide ranked seventh at the parent release
`9bb91ac660de26eb91aa43b1aae2b3486a1691d6`.

All 90 on-site finder entries now receive their existing `seo_title`, falling
back to the visible title, as escaped `data-search-title` metadata. No separate
keyword list, route-specific rule, newly written answer or source review is
introduced. External resources and glossary entries retain their existing titles.

The visible heading remains the stronger ranking signal. Secondary title terms
rank above general metadata, and a contiguous multiword query in that title
receives a phrase reward. Existing subject hints can also recognize this title
at a lower weight. Giving both titles equal weight initially displaced two
declared targets; that candidate was rejected before publication. The final
weights retain every prior passing case. These weights were tuned using this
authored regression set, not a held-out learner study.

**ICM**, **what is ICM**, **tournament equity** and **prize equity** now put the
dedicated guide first. **Independent chip model** puts it in the first three;
an MIT lecture with that explicit title remains first. An unrelated required
word such as **football** still produces no matches. The existing guide heading,
article excerpts, honest section anchors and no-JavaScript browse fallback
remain available. Search terms still stay out of URLs, requests and storage.

## Evidence and limits

| Same frozen authored questions | PR #103 | This release |
| --- | --- | --- |
| Declared destination in the first three | 29/30 | 30/30 |
| Previously passing cases retained | 29 | All 29 |
| Dedicated ICM guide | Seventh | First |

The original 30 questions, targets and reasons remain unchanged in
`../poker-search-intent/queries.json`. This release's `results.json` binds the
new index and script hashes to those exact expectations. The original 18/30
baseline and 29/30 release report remain frozen and reproducible, including in
a shallow checkout by reversing only exact digest-bound release deltas.
`evaluate.py --prior-release` replays the 29/30 snapshot; its default evaluates
the current site. Current output writes to this folder, never over that snapshot.

Thirty declared target hits do not establish that all results are useful, that
commercial products are recommended, or that actual beginners succeed. The
roadmap goal of useful top-three results for 27 of 30 real, human-judged beginner
questions remains open. So do the qualified teaching review and real beginner
sessions needed before observation-dependent learning changes.

Four new unit checks cover the unchanged corpus, title provenance and card
content preservation, related wording and route independence, and exact release
preservation with mutation rejection. The real browser suite adds the three
ICM/title queries alongside its existing privacy, filters, input-method,
keyboard, print and fallback checks. This is software verification, not an
accessibility certification or measured teaching outcome.

## Production scope and reproduction

Production changes are limited to `_scripts/poker_finder.py`,
`assets/poker-finder.js` and generated `poker/find/index.html`. The only HTML
changes are 90 existing public-title attributes and the script cache token.
No page wording, dates, directory judgments, download, hosting or analytics
settings change. The fresh baseline fingerprints all 480 existing source,
script, asset and download files plus 221 generated outputs against the parent
commit. Its separate three-file adapter runs before older preservation checks;
no earlier baseline or delta is widened.

```sh
python _scripts/build.py --check
python _reports/poker-search-intent/evaluate.py --baseline
python _reports/poker-search-intent/evaluate.py --prior-release
python _reports/poker-search-intent/evaluate.py
python -m unittest discover -s _tests -p 'test_poker_search*.py' -v
python _tests/finder_browser.py
```

After a deliberate edit, rebuild, run the current evaluator with `--write`,
inspect the result and run this release's `capture_history.py`. That capture
refuses a changed baseline or any production edit outside the three listed
files. It does not refresh historical evidence.
