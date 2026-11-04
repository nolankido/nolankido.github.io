# Sprint 50, Turn 23: Technology metadata freshness

Review date: 2026-11-04  
Status: Merged in [pull request #179](https://github.com/nolankido/nolankido.github.io/pull/179)  
Implementation commit: `667601806f8f179eaafd6d7d6401f498127e81c2`  
Prior main: `7ee90e508112f98bfa66c8c55d2bba3d2dc0ccea`

## Why this was the next useful change

The Technology page had gained public poker-vlog evidence QA and a deterministic, offline structured-claim checker on November 4. Its search summary still mentioned only the older local review, book continuity, and cooking-planner examples. Its structured `dateModified` field and Technology sitemap `lastmod` still said November 3. These mismatches made the page's public search presentation lag behind the actual content.

The revision fixes the specific contradiction without claiming a search-ranking effect.

## Reviewed public description

> Explore Nolan Kido's practical AI work: small-business review checks, poker-vlog evidence QA, book continuity, and repeatable tools. AI Works Human Decides.

The description is 156 characters. It names the site owner, core public projects, and the established principle without claiming that an AI reviewed actual private poker footage.

## Changes

1. `_source/pages.json`: update only the Technology entry's description and reviewed date to November 4.
2. `_scripts/practical_path.py`: align its explicit Technology description override with the manifest, preventing the next generator run from restoring outdated wording.
3. `technology/index.html`: update HTML description, Open Graph and Twitter snippets, JSON-LD description, and `dateModified`; leave the body, canonical URL, title, and page cards unchanged.
4. `find/index.html`: update the browser-local Technology listing snippet without changing search behavior.
5. `sitemap.xml`: advance only `https://nolankido.com/technology/` to `2026-11-04`, leaving every other URL and date untouched.
6. `_tests/test_turn23_technology_metadata.py`: add focused checks for source-to-generator consistency, metadata surfaces, all other sitemap dates, committed generated outputs, and exact historical predecessor blobs.
7. `_tests/turn23_technology_metadata_history.py` and earlier test-only adapters: retain SHA-gated Turn 14, 17, 21 and 22 snapshots. Unknown mutations still pass through untouched.

## Verification and limits

- Confirmed the merged pull request contains exactly 13 files: five production files, one new regression test, one new historical helper, and six earlier test-only compatibility updates.
- Confirmed the five production files and two new test files on the review branch matched the intended replacement content byte for byte.
- Python syntax parsing passed for all eight new or edited Python test and history files.
- Static checks confirmed one Technology sitemap date change, one JSON-LD description, three escaped page-description copies, and one Find listing description.
- The full filesystem-backed generator and unittest suite **could not be executed** in the current read-only runtime. The new regression tests are committed for the next environment with a checked-out repository.
- The first live requests immediately after merging returned the prior description. A later uncached live fetch confirmed the new Technology page description and the updated browser-local Find listing. These public HTML surfaces have propagated.
- GitHub main independently confirms the intended November 4 Technology sitemap date in the committed XML file. The external page-extraction service renders sitemap URLs as links and did not expose the live XML dates, so direct verification of the deployed `lastmod` is still outstanding.
- No GitHub Actions, cron jobs, paid API calls, accounts, private analytics, invented poker facts, or changes to unrelated pages were introduced.

## Follow-up

The live Technology description and Find summary are confirmed. Independently check the deployed JSON-LD `dateModified` and raw sitemap `lastmod` when a raw-response verifier is available. Then consider further substantive evidence-backed content improvements and actual Search Console measurements if the connected property becomes available.

This turn corrects consistency and relevance of metadata. It does not establish new rankings, traffic, citations in AI answers, or viewer retention.
