# SEO/GEO Turn 70: separate the original visibility milestone from the current live inventory

**Date:** November 21, 2026 (Pacific/Honolulu)  
**Starting `main`:** `decb9d947717cffad9629a0cd81353ed5cea459d` (merged Turn 69, PR #443)  
**Existing canonical article:** https://nolankido.com/technology/ai-website-visibility/  
**Scope:** Update the public evidence and status of an existing site case study, without creating another landing page or claiming search growth.

## Fresh public evidence

A read-only live retrieval on November 21 confirmed that **both** contextual links added in Turn 69 are now on the public site:

- `/technology/check-ai-summary/` links to `/technology/ai-weekly-reset/#notes-case-sources`.
- `/technology/organize-public-notes/` links to `/technology/ai-weekly-reset/#notes-case-checks`.

The linked recorded editing case resolves with its self-canonical. A separate fresh public retrieval of `https://nolankido.com/sitemap.xml` returned **230 distinct links**, matching the committed 230-URL sitemap inventory. These are **content-level access observations**. Text extraction is not an exact-byte status-bearing GET receipt, full mobile-browser test, evidence of indexing, or a verified Search Console performance gain.

The local container still cannot resolve `github.com`, `api.github.com` or `nolankido.com` and lacks a complete repository checkout and `html5lib`. Full executable release testing remains unavailable here.

## Confirmed reader-facing issue

The site's source-backed [AI website visibility case](../../technology/ai-website-visibility/index.html) still led with a **November 19, 2026** readout titled *Did 25 SEO, GEO and AEO improvement turns make this site more visible?*. Its detailed table reports **224 URLs** at the November 17 baseline and **225 URLs** after Turn 24, with a specific 16-of-16 published-file release check. Those facts are historical and remain important.

But by November 21 the public sitemap had **230 URLs**, and later source-checked publication turns were already live. Without a distinct, later update, readers could mistake the old inventory for a present-day site count and could not see whether the subsequent work had any publication evidence. Rewriting the old table's numbers to 230 would corrupt the original benchmark, so the correct editorial action is a **dated addendum**.

## Change completed

1. In `_source/technology/ai-website-visibility.html` and generated `technology/ai-website-visibility/index.html`, insert one plain, labeled paragraph immediately after the original 25-turn short answer, before the historical supporting evidence. It clearly says that the 224-to-225 comparison belongs to **November 19**, not today's inventory.
2. Give the independently verified **230-URL** current sitemap and examples of live content: the [written 10 BB Poker study guide](../../poker/10bb/index.html), the [free AI workflow pilot](../../technology/ai-workflow-pilot/index.html) linked from Home and Start Here, and the [recorded AI source check](../../technology/ai-weekly-reset/index.html) reached from related guides. Link to the [merged Turn 69 PR](https://github.com/nolankido/nolankido.github.io/pull/443) as a public evidence record.
3. Explicitly state that these checks cannot establish indexing, Google impressions, actual visits or AI citations. None of the historical 25-turn table, frozen question panel, primary claims or data-gap boundaries was edited.
4. Record the **November 21** substantive article revision in `_source/pages.json`, the actual Article `dateModified` and `article:modified_time` in the generated page, and one `sitemap.xml` `lastmod`. The **November 3 original publication date** and unique canonical URL are unchanged. The sitemap still contains exactly 230 URLs.
5. Keep the change below the existing major heading, with **no new H2, schema class or route**. A 57-word bounded update leaves the guide's existing *about 17 minutes* source-derived reading estimate unchanged.
6. Add `_tests/test_turn70_visibility_case_current_status.py` with eight zero-network test methods: source/public paragraph identity, old evidence preservation, target routes and anchor, Article identity/dates, reading-size constraint, deterministic builder parity, false-claim/stale-inventory negative controls, and repository workflow safety. Register this test with `_scripts/local_release_checks.py`. Update `AGENTS.md` source ownership instructions.

## Evidence reviewed this turn

| Signal | Confirmed state | What it does not prove |
| --- | --- | --- |
| Live sitemap | 230 unique URLs | Actual Google/Bing indexing or rankings |
| November 19 historical evidence | 224 and 225 preserved unchanged | Current site inventory |
| New dated follow-up | One source and one matching public paragraph | Visitor engagement |
| Cross-page references | Links point to existing canonical guides and exact public fragments | Users completed those journeys |
| Original article | Published Nov 3; newly modified Nov 21 | New article or new age for the original |
| Find and homepage metadata | No new page, menu or title change | New organic query demand |
| Search / AI metrics | Authenticated counts unavailable | Zero impressions, zero citations or search impact |
| Automation | No new GitHub Actions, cron, paid tool or tracking | Complete CI/test coverage |

### Manual release gates

**Static source checks completed:** 230 distinct sitemap routes, self-canonical and updated Article dates, unique dated addendum, matching source/published addendum, existing 25-turn facts and two missing-measurement entries preserved, valid recorded links, and unchanged 17-minute displayed reading estimate.

**Not completed:** full repository Python unit suite, builder `--check`, HTML5 parser, browser/mobile navigation, whole-site internal link audit or raw live HTTP byte parity. Static checks are not substitutes.

From a complete checkout, run:

```powershell
py -3 -m unittest discover -s _tests -p test_turn70_visibility_case_current_status.py -v
py -3 -m unittest discover -s _tests -p test_turn25_visibility_closeout.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _scripts/check_live.py --only /technology/ai-website-visibility/ --only /sitemap.xml --attempts 3 --interval 5
```

Confirm the new dated paragraph is publicly served before asserting Turn 70 deployed. Do not treat GitHub merge or a cached text extraction as exact-byte verification.

## Next substantive gate

The evidence page now distinguishes the initial 25-turn closeout from the November 21 publication state. Additional SEO/GEO work should be driven by **owner-authorized Search Console and Bing query/page exports, Google AI Search/Discover dashboard status, and actual task-completion observations**, if those sources become available. Missing metrics must remain unavailable, never silently represented as zero or replaced with speculative rankings.

If another release is made, avoid automatically extending this page for every PR. Update it only when a new observation changes a real reader decision or a reportable outcome. The original 25-turn baseline must stay immutable.

**Source ledger:** [Turn 61 release scorecard](seo-geo-turn61-release-and-evidence-scorecard-2026-11-20.md), [Turn 69 crosslinks](seo-geo-turn69-ai-source-check-case-2026-11-21.md), `_source/technology/ai-website-visibility.html`, `_source/pages.json`, and `sitemap.xml`.
