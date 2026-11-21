# SEO/GEO Turn 54: NolanPoker public video link, title and companion accuracy

**Date:** November 20, 2026 (Pacific/Honolulu)
**Starting GitHub main:** `c1e8560f268838bbda3c3ec481c6a7925453c8e4`
**Scope:** six curated featured NolanPoker video IDs, three existing written companions and current-video timestamp evidence boundaries.

## Public facts actually checked

A read-only current YouTube watch-page metadata fetch returned the canonical ID and public title for each of the six curated Poker hub video links. Each title matched the existing, older on-site locally stored six-video title record. This independent check was about the public **listing**, not actual media playback, authorship verification or video edits.

| ID | Public watch-page title checked November 20 | Companion route |
| --- | --- | --- |
| `-Wm1i70Z3Bs` | I Went for $1.50 Hot Dogs... Then Entered a $120 Poker Tournament | No verified written companion on this site |
| `qABaiIcvvpU` | I Had 6.5 Big Blinds... Then Won a Trophy | `/poker/episodes/portland-meadows-ep1/` |
| `I75GOBVXij4` | I Had A-K With 10 Big Blinds. Then TWO Players Shoved. | `/poker/episodes/portland-meadows-standoff/` |
| `bxpaM_1mWPE` | I Won Yesterday. Today I Had One Bullet. \| Portland Meadows Poker | No verified written companion on this site |
| `HE7VDvO9gDU` | I Busted... Then Flipped Into a Final Table \| Portland Meadows | No verified written companion on this site |
| `edNSD5BjIV8` | My Ace-King Reshove in a 3-Way All-In \| WSOP Circuit | `/poker/episodes/reserve-day-1/` |

All three companion URLs were also publicly retrievable when checked. The site retains its *separate* historical oEmbed metadata and local-JPEG checks from November 13 and 18. **No current title changed** during this audit, so no thumbnail replacement or speculative title overwrite was warranted.

The previously published Deepstack companion contains viewer-visible transcript starting positions for its current video. They are not verified current-cut frame boundaries. The Stand Off companion still depends on archived v9 and Reserve Day 1 on archived v8 notes. The newer Portland Meadows uploads and South Point have no source-verified current-cut hand companion on this site.

## Confirmed content problem and fix

The Deepstack Episode 1's secondary-video paragraph still called the Reserve upload "WSOP Circuit Reserve Day 1: 7 BB and an A-K pot" instead of using its current public A-K 3-way video title. More significantly, the paragraph said the two linked uploads were "not source-checked written companions", when the repository and public site now *do* provide source-bounded Stand Off and Reserve written companions.

Corrected this exact paragraph in both `_source/poker/portland-meadows-ep1.html` and `poker/episodes/portland-meadows-ep1/index.html`. It now uses the verified exact public video titles, links directly to both verified **existing** written companions, and carefully distinguishes those articles from independently verified current-cut video hands or chapter times. No event result or new footage was invented.

The Poker hub source and generated page now have a short dated audit link in the original `#nolanpoker-video-notes` section, at `#nolanpoker-current-title-check`. A versioned JSON file `downloads/nolanpoker-video-title-link-audit-2026-11-20.json` records the six titles, IDs, actual watch-page titles, three companion routes, timestamp evidence class and explicitly unsupported audiovisual or thumbnail re-verification claims. The new public download is covered by the exact-byte GET inventory.

## Preserved boundaries

All six original gallery cards, images, source oEmbed dates, main Poker/Player and video page canonical URLs, original publication/modification dates, sitemap, site feeds, author identity and book links were preserved. The later source pages retain their archived/current-cut limitations and the Deepstack's five transcript markers still require a human audio/frame review. The public title alone does not verify any hand, poker payout, player status or video chapter time.

New `_tests/test_turn54_nolanpoker_listing_accuracy.py` protects the six-row title/ID agreement, gallery reference link and provenance boundaries, companion canonical destinations, one outdated crosslink correction, source-output matching snippets, inventory publication and no CI workflows. The test is registered in the manual local release suite. The README and AGENTS release notes distinguish historical oEmbed+thumbnails from the new watch-page title check.

## Verification and limits

Source and committed HTML were checked before the commit for unique exact edits, all six title/ID matches, three correct companion links and legacy source limits. New Python regressions, full deterministic build, HTML5 and browser QA were **not run** in the model container because cloning from GitHub cannot resolve DNS here. A GitHub PR merge confirms committed sources only; a fresh post-merge public response check must verify that the updated note and corrected companion paragraph are being served. This release makes no measured claim about indexing, search traffic, AI citations, viewer retention or YouTube playback reliability.

### Full-checkout verification

```powershell
py -3 -m unittest discover -s _tests -p test_turn54_nolanpoker_listing_accuracy.py -v
py -3 -m unittest discover -s _tests -p test_turn40_poker_videos.py -v
py -3 -m unittest discover -s _tests -p test_turn150_nolanpoker_thumbnails.py -v
py -3 _scripts/build_poker_episode.py --check
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /poker/ --only /poker/episodes/portland-meadows-ep1/ --only /downloads/nolanpoker-video-title-link-audit-2026-11-20.json --attempts 3 --interval 5
```

## Next

**Turn 55:** Follow a real reader from the Poker hub to a current video or source-checked written companion and back to a relevant free study exercise. Remove any redundant or ambiguous choice without breaking the maintained source and video verification boundaries.
