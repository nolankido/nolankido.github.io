# SEO/GEO Turn 67: make the 10 BB Playbook an honest standalone study guide

**Review date:** November 21, 2026 (Pacific/Honolulu)  
**Starting `main`:** `57c43cf011bbf8bfa20bd65f2ce2d3338dd7ef07`, merged Turn 66, PR #440  
**Canonical page:** https://nolankido.com/poker/10bb/  
**Focus:** Factual publication status, usable on-page navigation, public metadata and accurate source-to-lesson discovery.

## Evidence: earlier site changes were published

A fresh read-only public content retrieval on November 21 found the two **Turn 66** outbound links at their exact live locations:

- `/poker/` contained `/poker/10bb/#practice-title`.
- `/poker/six-to-ten-bb-tournament-decisions/` contained `/poker/10bb/#icm-title`.

The target Playbook also resolved with its original canonical and a public page title. This is evidence of **content-level deployment of Turn 66**, not an HTTP-status-bearing exact-byte check or independent YouTube playback verification.

A bounded additional audit inspected **76 specific distinct cross-page hash targets across 30 important existing destination files** in the current GitHub repository. All 76 were present as unique `id` attributes in their intended documents. This audit did not inspect every website link or the real browser's scroll, focus, loading or mobile layout.

## Confirmed editorial defect in the Playbook

The current `poker/10bb/index.html` was a 32,152-character indexable HTML document whose title and public metadata characterized it as a *NolanPoker Video Companion*. Its introduction asserted that the written work accompanied a one-hour tournament course. The `#chapter-map` section instructed the reader to select exact chapter times in a YouTube player, and listed **21 time stamps through 1:00:02**. Six question cards claimed separate **Video 54:54 through Video 58:58** positions. Other text described a specific ICM explanation as appearing at 44:09.

Yet the page linked only to the general `@NolanPoker` channel, **not to an independently verified public course watch URL**. A public web search this turn also did not verify a specific course upload or the synchronization of those timestamps. Absence of a verified URL does **not** establish that no video exists; it means the page cannot responsibly promise that exact video playback experience. The user's public author site should not publish a production working timeline as an independently confirmed current-video navigation.

## Actual correction

1. Retain the established canonical `https://nolankido.com/poker/10bb/`, original `datePublished=2026-11-19`, unchanged H1 and existing math and worksheet.
2. Describe the resource as a **standalone NolanPoker written study guide** across HTML title, meta description, Open Graph, Twitter, Article headline and Article description. The visible introduction states that **no video is required**. A prominent note says that a matching public course-video URL and synchronized chapter times are **not verified on this page** and links only to the creator's public channel.
3. Replace the 21 obsolete time-only chapter rows with **eight native links** to the page's published lesson and reproduction anchors: `#six-checks`, `#first-in`, `#facing-action`, `#postflop`, `#icm`, `#icm-reproduce`, `#practice`, `#sources`. Eliminate the six unverifiable question-video timestamps and the unsupported 44:09 navigation promise.
4. Keep all six substantive questions with their existing written explanations, the 45/50/55/60% ICM sensitivity examples, payout arithmetic, two distinct fictional payout models, restricted source claims, and downloadable offline `ten-bb-playbook-icm-verify.py`.
5. Revise `find/index.html` and `_scripts/player_find.py` together: the course result remains **exactly one** native Poker search card but its type is now **Guide**, not Video companion. Preserve the original November 19 published label. The compact eight-heading search index now uses the actual H2 `Choose a written lesson`.
6. Record an accurate **November 21 substantive revision** in the public metadata, visible update time, JSON-LD and the single `sitemap.xml` entry. There remain **230 sitemap URLs**; no duplicate page or publication-date reset.
7. Update existing Turn 52 math/publication tests, Turn 65 Find tests and Turn 66 route tests, and add a dedicated Turn 67 fail-closed study-guide and provenance test module to the existing manual release runner. The owner restriction against GitHub Actions, cron and paid APIs remains.

## Source-level verification completed

| Evidence check | Before | Branch after correction |
| --- | --- | --- |
| Public page classification | Video companion (unverified specific URL) | Independently usable written guide |
| Unverified chapter times | 21 chapter-map timestamps + six question-card timestamps | Zero timestamp navigation claims |
| Valid direct on-page lesson links | None in the old chapter list | Eight, all eight IDs verified unique |
| Visible original H1 and canonical | Existing | Preserved unchanged |
| Practice questions and written answer cards | Six | Six, math text and examples retained |
| Exact 3-player ICM break-even | `63/107`, ~58.88% | Unchanged |
| Published date | Nov 19 | Nov 19, unchanged |
| Modified date | Nov 20 | Nov 21, corrected in HTML, JSON-LD and sitemap |
| Native site Find result | One `episode` card | One `guide` card |
| Visible H2 sections in Find | Eight | Eight, with corrected written lesson label |
| Sitemap URLs | 230 | 230, one revised lastmod |

The original and revised GitHub files provide the change record. The body also continues to distinguish the Playbook's three-player example from the separate four-player 6 to 10 BB guide. No claim is made that the course appears on YouTube, has a verified running time, or that Google indexed the revised version.

## Release and evidence limits

The current isolated execution container cannot resolve `github.com` or `nolankido.com` to download a full checkout, and lacks `html5lib`. Therefore the **full Python builder, historical unit suite, strict HTML5 parsing, browser/keyboard tests and status-bearing exact-byte production verifier were not run**. The static source checks here established the exact changed card/heading data and preserved mathematical statements, not the complete release gate. Any failed full test requires another repair rather than a changed assertion alone.

Run locally from a complete checkout of the merged commit:

```powershell
py -3 -m unittest discover -s _tests -p test_turn67_playbook_standalone.py -v
py -3 -m unittest discover -s _tests -p test_turn52_10bb_playbook.py -v
py -3 -m unittest discover -s _tests -p test_turn65_tenbb_find.py -v
py -3 -m unittest discover -s _tests -p test_turn66_tenbb_reader_paths.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /poker/10bb/ --only /find/ --only /sitemap.xml --attempts 3 --interval 5
```

After deployment, verify via public content retrieval that the Playbook uses eight internal lesson links, correctly names the guide, reports November 21 modification and has no promised YouTube timestamps. Observe separately whether search engines or assistants ever discover it. Do not infer improved rankings, visits, subscribers or citations merely from correcting publication accuracy.

## Next improvement

Follow through on the full local release gate when a checkout-capable environment is available and fix any observed errors. Once an exact **public** NolanPoker course watch URL is verified, a separate later turn can provide a clearly labeled optional video link and re-audited chapter times, but should not restore archived draft timestamps blindly. Prioritize Search Console/Bing/Umami first-party query and page evidence before writing more redundant SEO articles.

**Source ledger:** the [prechange Playbook](https://github.com/nolankido/nolankido.github.io/blob/57c43cf011bbf8bfa20bd65f2ce2d3338dd7ef07/poker/10bb/index.html), [Turn 65 native Find release](seo-geo-turn65-tenbb-local-find-2026-11-21.md), [Turn 66 reader journeys](seo-geo-turn66-playbook-reader-paths-2026-11-21.md), and existing source-verified `_scripts/tenbb_companion.py`.
