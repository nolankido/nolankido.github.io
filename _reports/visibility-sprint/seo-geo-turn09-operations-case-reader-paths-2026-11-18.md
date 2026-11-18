# SEO/GEO Turn 09: an inspectable operations exception and repaired AI reader paths

**Prepared:** November 18, 2026
**Base:** `2335a47a307d082920435c328741792a164e324d` (Turn 08)
**Status:** source and generated page changes locally checked, publication tracked through the repository change

## What this turn actually improves

The saved sprint roadmap calls for an original small-business AI workflow example with a failure, an independent check and a human decision. The previous release also proposed auditing local-AI reader paths. This turn completes a **fully fictional** exception exercise and repairs a specific source-to-download integrity failure left by Turn 08. It does not invent a real model run, client outcome, laptop benchmark or search-performance result.

### Original, reproducible case

The existing [AI workflow pilot](https://nolankido.com/technology/ai-workflow-pilot/#pilot-exception-case) now contains a fictional print-shop request:

1. A customer requests **120 printed cards** for Friday at 4 p.m., without a confirmed order.
2. Only **90 blank cards** are on hand; 60 more were requested but supplier arrival is unconfirmed.
3. A manager must authorize a pickup-time promise and the customer must agree before accepting a split delivery.
4. A **deliberately constructed, illustrative draft** wrongly confirms pickup for all 120 and offers a 90-card split without the needed authorization.
5. Independent checks reveal a **30-card current shortfall** (120 - 90), unknown additional-stock arrival, and missing approvals. The **fictional reviewer decision** is to reject the message and keep the request pending until the facts and permission are confirmed.

The case spells out its input, candidate, arithmetic, authority checks, revised internal status and final decision. There is **no actual AI generation, real shop, customer or manager decision** in this record. It is an educational counterexample, not an observed model error or customer deployment.

- [Download the exact synthetic input, flawed draft, checks and simulated decision](../../downloads/ai-operations-exception-source.json).
- [Download the reusable blank exception and authorization worksheet](../../downloads/ai-operations-exception-worksheet.md). Neither artifact requires an AI account, network call or paid service.
- A Technology-hub link opens the case at its stable heading. The existing four-stage task workflow remains intact.

### Link integrity repair and evidence path

Turn 08 placed a test protocol and blank CSV in `downloads/`, but the site's separate public-target registry did not include them. A read-only scan of the initial Turn 08 checkout found exactly two unregistered targets in the gaming-laptop article. Both files were present on disk; the defect was in the checking inventory, not proof of a live HTTP 404.

This turn registers those two files and the new operations-case downloads in `_scripts/check_live.py`. It also connects the Technology hub, historical CPU-runner case, workflow pilot and time calculator to the relevant evidence. The time calculator now explicitly describes the old Gemma measurements as **GitHub-hosted Ubuntu CPU runner timings**, not MSI gaming-laptop timings.

The accompanying [offline content-link audit](../../_scripts/audit_ai_reader_paths.py) reads built public HTML, counts unique incoming **main-content pages** for each chosen destination, and finds the shortest link route from Home and Technology. Global header links are excluded from its content-link counts. It makes no HTTP requests, does not query Search Console and cannot infer PageRank or search-engine authority.

New contextual links use ordinary HTML anchors with meaningful labels, consistent with [Google Search Central's link guidance](https://developers.google.com/search/docs/crawling-indexing/links-crawlable). Such structure makes a route easier to discover in HTML but is not proof that a search engine actually crawled or indexed it.

## Reproducible local observations

| Check | Turn 08 starting state | Turn 09 checked state |
| --- | --- | --- |
| Registered internal-link scan | 231 HTML pages, 16,108 internal-link occurrences, **2 unregistered** new downloads | 231 HTML pages, 16,120 internal-link occurrences, **0 issues** |
| Comparison protocol | One homepage route through the Technology hub, but not registered as a public target | Registered; **2 clicks from Home, 1 from Technology**, linked in the main content of **5 pages** |
| Comparison CSV | Not registered in the target inventory | Registered; **2 clicks from Technology**, linked in **2 pages** |
| New operations source and worksheet | Not yet present | Both registered, each **2 clicks from Technology** and **3 from Home** |
| AI workflow example | A synthetic time arithmetic exercise but no separate source-by-source operations decision | Source ledger, flawed counterexample, three independent checks and a simulated reject/revise decision |

The click counts are shortest routes through links in checked-in HTML, not observed human clickstream or Google crawler data. The 16,120 total includes repeated links and is not a number of unique links or backlinks. The audit shows all **nine tracked destinations** reachable from Home and Technology; every mandatory content link is present.

## Verification, including limits

- `python _scripts/build.py`: **passed**, generated current source outputs.
- `python _scripts/build.py --check`: **passed**, 253 generated files checked with no changes.
- `python _scripts/check_internal_links.py`: **passed**, 231 HTML pages and zero unresolved public targets.
- `python _scripts/audit_ai_reader_paths.py`: **passed**, all nine target routes registered and reachable.
- `python -m unittest discover -s _tests -p 'test_turn09_ai_reader_paths.py' -v`: **four tests passed**, including the synthetic quantity calculation, source labels and downloads.
- `python _scripts/check_search.py`: **passed**, 224 sitemap routes, unique title and description counts and no reported errors. This is not indexing confirmation.
- `python _tests/check_html5.py`: **passed**, 229 validated pages and no reported failures.
- `python _scripts/build_local_laptop_case.py --check`: **passed**, independently built gaming-laptop page still matches its source.
- `python downloads/local-ai-loopback-check.py --dry-run`: **passed** and correctly returned null timing, token and quality values. No model ran.
- The broader `local_release_checks.py` and historical full-unit suite were **attempted but not accepted as clean passes**. Unrelated older frozen fixtures, including an outdated Poker Finder count and Git revision/path assertions that fail in this shallow checkout, caused failures. They were interrupted after those failures were established. None is evidence of this turn passing all historical tests.
- The installed Python Playwright package has **no Chromium executable** in this environment. A 320px browser visual review was not performed.
- Authenticated GSC Wizard property listing and on-page audit both returned `INVALID_ARGUMENT`; live crawling and search metrics were not obtained through that service.

The offline case, its worksheet, the new text links and existing canonical URLs add no GitHub Actions, scheduled CI, external AI requests, credentials or private data.

## What remains unknown and what follows

Nothing in this turn measures clicks, CTR, rankings, Google indexing, AI citation, real model accuracy, client time saved, or actual laptop/hosted AI speed. No claim about those outcomes is justified.

**Turn 10 per the original sprint roadmap:** deepen the existing AI-assisted website-repair case into a reproducible engineering lesson, using verified historical commits, a minimal defective HTML fixture, the independent HTML5 check that caught it, and the correctly limited lesson about passing tests. Confirm public deployment and 320px layout checks when browser access is available.
