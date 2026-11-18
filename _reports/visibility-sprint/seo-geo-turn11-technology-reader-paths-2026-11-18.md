# SEO/GEO Turn 11: Technology reader paths and canonical audit

- **Date:** November 18, 2026
- **Site:** https://nolankido.com/
- **Sprint:** Turn 11 of 25
- **Status:** Implemented in source and validated against the locally built site; live indexing and audience behavior not measured.

## Decision

The existing Technology collection has substantial public evidence, but visitors previously encountered several lists of projects and generic entry points without a concise answer to *which page handles my specific question?* This turn improves information architecture and contextual next actions. It does not invent an additional case study, create another canonical URL, or claim measurable SEO growth.

The [19-route intent matrix](seo-geo-turn11-technology-intent-matrix-2026-11-18.csv) inventories every Technology URL, including the collection hub, 16 manifest-backed guides and cases, and two manually maintained case studies. Each record identifies the primary question, bounded answer, distinct artifact, evidence type, next action, and two or three selected contextual destinations. These are editorial intent hypotheses, not observed Google or Bing queries.

## Eight reader tasks

| Task | Principal reader question | Where to go | Key evidence boundary |
| --- | --- | --- | --- |
| Deciding | Should AI be involved at all? | [Six-question AI task choice](../../technology/should-i-use-ai/) | Fictional decisions do not certify suitability for another situation. |
| Briefing | How do I define and check a delegated task? | [AI task brief](../../technology/task-brief/) and [public-notes example](../../technology/organize-public-notes/) | A saved brief cannot authorize a real-world action. |
| Checking | What independently supports this AI claim? | [Answer checks](../../technology/check-ai-answers/), [summary checks](../../technology/check-ai-summary/), [website-repair case](../../technology/checking-ai-website-changes/) | A passing checker is only evidence for its tested scope. |
| Measuring | Did the workflow help, or improve website visibility? | [Time calculator](../../technology/ai-time-savings/), [pilot](../../technology/ai-workflow-pilot/), [visibility method](../../technology/ai-website-visibility/) | Synthetic trials and release checks are not measured productivity or ranking gains. |
| Local execution | What can run on my computer, and what was measured? | [Windows laptop guide](../../technology/local-ai-gaming-laptop/) and [Ubuntu test record](../../technology/local-ai-test-record/) | The real historical CPU-runner measurement is not a verified laptop benchmark. |
| Writing and continuity | How do I preserve source constraints in a manuscript or note? | [Preflight case](../../technology/ai-book-continuity-checker/) and [weekly-reset case](../../technology/ai-weekly-reset/) | Source-linked editing may contain false flags; the weekly note was not tested on a person. |
| Practical operations | How do customer-review drafts remain accountable? | [Review Reply Writer](../../technology/local-ai-review-replies/) and [independent reply audit](../../technology/review-reply-evidence-audit/) | Archived fictional review examples do not prove production accuracy or client outcomes. |
| Project demonstrations | What do these AI-assisted prototypes actually do? | [RightsReceipt](../../technology/rightsreceipt-ai-licensing/), [Dinner on Time](../../technology/dinner-on-time/), [poker-video evidence gate](../../technology/ai-poker-video-evidence/) | Payment is simulated; meal planning is simulated; a proposed caption still needs a video review. |

The hub now shows these eight task questions after the existing first three pathways. This preserves the first-screen project, checking, and measuring choices while giving every flagship case a direct route. Selected case pages gained only missing, task-relevant neighboring links. The Technology landing page remains a hub, not a duplicate of the article bodies.

## Ownership and metadata

- **Main manifest:** `_source/pages.json` retains 17 Technology paths, including `/technology/`. Page bodies continue to come from the existing `_source/technology/` files and the main build.
- **Independent cases:** `/technology/local-ai-gaming-laptop/` still uses `_scripts/build_local_laptop_case.py`; `/technology/review-reply-evidence-audit/` still uses `_scripts/build_reply_audit_case.py`. Neither was moved into the main manifest. Each standalone builder's `--check` passed.
- **Find:** Both manual cases and all other Technology routes still have one Find result each.
- **Feed:** The Technology RSS retains 16 article records, including the two manual cases, with original publication dates. The hub and two browser tools are not mislabeled as new articles.
- **Modification dates:** Only the substantively revised Technology, Projects, and Resources hubs advanced to November 18. Publication dates of all 16 published guides and cases, including the two manual cases, remain unchanged. Small contextual links do not impersonate a new article publication.
- **URLs:** No new or redirected Technology URL; all 19 self-canonicals preserved.

## Reproducible local release checks

Run from the repository root on Python 3.10 or newer:

```bash
python _scripts/build.py --check
python _scripts/audit_technology_cluster.py
python -m unittest _tests.test_turn11_technology_cluster _tests.test_turn09_ai_reader_paths _tests.test_turn10_website_repair_case _tests.test_standalone_reader_arrivals -v
python _scripts/check_search.py
python _tests/check_html5.py
python _scripts/check_internal_links.py
```

Results captured November 18, 2026, from the local built tree:

| Check | Verified result |
| --- | --- |
| Build consistency | 253 generated outputs checked, zero drift |
| Technology intent and discovery | 19 routes, eight tasks, zero audit issues |
| Sitemap and canonical matching | All 224 sitemap URLs self-canonical, no duplicate canonical targets |
| Find | 211 result routes scanned; each of 19 Technology destinations present exactly once |
| Practical AI RSS | 18 feed items total, 16 Technology case/guide items, no wrong tool-as-article registration |
| Test selection | 24 tests passed, including six new Turn 11 tests and both independent builder checks |
| Static search | 224 sitemap pages, 224 unique titles, 224 unique descriptions; pass |
| HTML5 parser | 229 pages checked; pass |
| Internal links | 231 HTML pages, 16,162 occurrences, zero unresolved targets |

The audit script reads only committed site files and the explicit CSV. It asserts a distinct primary question for every row, two or three contextual links present in the actual article body, complete eight-task hub coverage, Find and sitemap membership, feed publication-date ownership, and self-canonical consistency for every indexed sitemap page. It does not contact crawlers or inspect private analytics.

## Remaining verification and next turn

This is a static and editorial quality milestone, not a claim of improved clicks, indexing, impressions, AI assistant citations, reader satisfaction, or conversion. A 320-pixel interactive mobile browser inspection and measured user navigation remain unverified in this environment. Historical full-suite fixture failures unrelated to these files were not rerun here. The public site should be checked after merge for deployment and expected live HTML, without treating a successful HTTP response as search-engine indexing.

**Next planned improvement:** Turn 12, the evidence-bounded ten-big-blind tournament-bubble learning destination, using real public hand records and explicit solver and ICM limits. No unpublished cards, results or ranges should be filled in to complete it.
