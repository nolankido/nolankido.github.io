# SEO/GEO Turn 53: a real poker publication before-and-after with open video approval

**Date:** November 20, 2026, Pacific/Honolulu  
**Starting main:** `d9267f2fe9e39670b2a41f8eba044dc34ff98e32`  
**Canonical:** https://nolankido.com/technology/ai-poker-video-evidence/  
**Roadmap:** Turn 53 of 37 to 61

## Problem solved

The site already had a detailed AI-assisted poker-caption proposal, a dated written Episode 1 companion and a source-backed public-video transcript audit. It had no easily found example of an **actual published before/after**, as distinct from deliberately constructed fact-checker negative controls. The latest published video graphics and final export are not independently verified, so asserting a video recut would have been false.

The November 20 repository history gives one honest versioned written case:

- **Before**, [published Episode 1 page at 788e3f4](https://github.com/nolankido/nolankido.github.io/blob/788e3f44e09d0fc5a93a38bec138867fca492637/poker/episodes/portland-meadows-ep1/index.html) had no `#episode-current-transcript` section.
- **After**, [actual commit 4f3449c](https://github.com/nolankido/nolankido.github.io/commit/4f3449cd40cf5b165b756d2c4c2fce9aa3827c67) added the [source-limited transcript checkpoints](https://nolankido.com/poker/episodes/portland-meadows-ep1/#episode-current-transcript), now visible in the live page. Reported 6-4, pocket sevens and $2,900 deal-share references were linked to selected public viewer-visible transcript positions, not certifiably exact scene boundaries.
- **Open gate:** The earlier [five-entry read-only transcript observation](https://nolankido.com/downloads/portland-meadows-public-transcript-audit-2026-11-20.json) could not play and inspect current video audio or frames. No current graphics, rights or final human signoff is proven. The AI-written candidate captions remain distinct site-only editorial proposals.

## Actual Turn 53 changes

Updated only the existing AI-and-poker article, using an early native jump link and one source-linked H3 within its existing verification section. Its new content links the historical parent, the actual GitHub change, the revised written companion, the public transcript audit and the original detailed evidence ledger. It explicitly says this change is to the *written page*, not a video export.

Extended `downloads/nolanpoker-content-production-evidence-ledger.md` with the full before/after source matrix (Section M) and corrected the stale written-companion revision date from November 16 to November 20. Preserved November 2 as the original Episode 1 publication.

Updated `_source/pages.json`, the article's matching compiled JSON-LD and meta modification date, its sitemap lastmod, and the generator-computed editorial reading estimate from nine to ten minutes. Original article date **November 4** and canonical URL were not replaced. No new page, Book identity, schedule, workflow, automated crawler, video URL, transcript, image, other person's data or search-only schema was created.

New `_tests/test_turn53_poker_published_revision.py` enforces exact pinned source links, original and changed publication status, unsupported audiovisual claims, source/public snippet parity, original and modified dates, sitemap and live-byte registration, no added GitHub Actions, and negative controls. The older Turn 43 date/read-time test was aligned to the actual current 2026-11-20 updated article facts. Registered the new offline test in the manual local release checks.

## Evidence, validation and limits

- Independently fetched the two pinned historical GitHub versions and verified absence then presence of the written companion's `#episode-current-transcript` section.
- Independently fetched the current public canonical companion's transcript section, including 4:20 and 6:27 cues and $2,900.
- GitHub source preflight checked exact text replacement locations, bounded single anchor, stable six H2 topic sections, source/public inserted-section parity, and 2026-11-20 date consistency.
- The local complete Python build, full unit/history suite, HTML5 parser, browser accessibility, and post-merge public exact-byte checks are **not marked passed** unless actually executed. GitHub merging source is not itself proof of a released page or improved search performance.
- Claims of a published video, transcript-text observations, candidate captions, completed checks, and unapproved media outputs remain separate.

### Complete-checkout acceptance

```powershell
py -3 -m unittest discover -s _tests -p test_turn53_poker_published_revision.py -v
py -3 -m unittest discover -s _tests -p test_turn43_published_content_receipt.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /technology/ai-poker-video-evidence/ --only /downloads/nolanpoker-content-production-evidence-ledger.md --attempts 3 --interval 5
```

## Next
Turn 54: independently verify featured NolanPoker video IDs, current titles, episode links, and any claimed cut timestamps, repairing only proven mismatches without changing current audiovisual media or inventing approval records.
