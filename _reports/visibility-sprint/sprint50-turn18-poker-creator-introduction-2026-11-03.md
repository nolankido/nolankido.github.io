# Visibility sprint, Turn 18: Source-backed poker creator introduction

**Review date:** November 3, 2026 (America/New_York)  
**Site:** https://nolankido.com/  
**Public URL:** https://nolankido.com/poker/nolan-kido/#creator-introduction  
**Purpose:** Give event organizers, tournament commentators and collaborators a short, reusable description of Nolan Kido's published poker work that can be checked against independent results and the actual publicly available videos.

## Reader problem

The existing player profile listed selected official finishes and three public YouTube videos, with appropriate warnings about gross results and independently unverified narrated hands. It did not contain an event-ready, third-person introduction that a reader could quote and quickly check.

Turn 18 adds an anchored introduction on the existing canonical player page rather than creating a thin duplicate SEO page or claiming a tournament credential.

## What is new

- An original short creator introduction that connects first-person tournament videos with a limited number of independently recorded results.
- Direct citations to [South Point Lucky 300 results at The Hendon Mob](https://pokerdb.thehendonmob.com/event.php?a=r&n=1399113), [WSOP Cherokee Event #8](https://www.wsop.com/tournaments/result/17989/) and [WSOP Thunder Valley Event #10](https://www.wsop.com/tournaments/result/18650/).
- Visible distinction between independent tournament results and Nolan's self-published video/hand accounts.
- Direct internal links to the three existing published video samples, the separate source-referenced Portland Meadows companion and the contact page.
- Clear limits: no implied endorsement or affiliation by WSOP, creator-program acceptance, professional status, Circuit ring, net profit, complete playing record or media reuse permission.

## Files

- `_source/poker/nolan-kido-profile.html`: source of the new section.
- `poker/nolan-kido/index.html`: exact deterministic published rendering.
- `_tests/test_turn18_poker_creator_intro.py`: focused source, build, provenance, legacy URL and mutation checks.
- `_tests/turn18_poker_creator_history.py`: test-only, exact Git-blob predecessor for the two public page files.
- `_tests/turn11_video_discovery_history.py`: normalize the approved Turn 18 page before older historical predecessor checks.

No generator, sitemap, Find, RSS, metadata identity, date, other public content route, GitHub Actions or scheduled service was changed.

## Verification

- The GitHub five-file comparison contained only the reviewed page files and their focused test/history adaptations.
- Computed Git blob IDs for both changed page files matched the exact GitHub connector content SHAs.
- Source text is byte-identical within the compiled page, the new anchor is unique, all HTML IDs are unique, nested structural tags balance, and each of the three existing YouTube video URLs remains present exactly once.
- Independently reproduced the **exact compiled player page** by running the actual `build_player_profile.py` `render()` function in an in-memory read-only test against the existing Poker shell and reviewed new source.
- Python AST parsing passed for the two new files and amended predecessor module.
- The new predecessor was executed in-memory: both exact approved file revisions restore to their prior reviewed SHA, repeated restoration is idempotent, and unexpected bytes pass through untouched.
- The entire repository unittest suite, browser acceptance suite and HTML5 validator were **not** run in the available read-only environment; no complete-suite pass is claimed.
- This is an editorial and source-verifiability improvement. No search ranking, impressions, clicks, index status or AI-answer mention improvement was measured.

## Publication

- [PR #174](https://github.com/nolankido/nolankido.github.io/pull/174) squash-merged to `main` at commit `371ac8b83c85b61cfcc42d33ea4e069917791dfe`.
- GitHub main source, public HTML and focused test were fetched after merge and exactly matched the reviewed versions.
- - The live canonical page was fetched after deployment propagation at `https://nolankido.com/poker/nolan-kido/` using the `#creator-introduction` selector. The approved section, all three result links and the explicit official-media-credential limitation were observed in public HTML. A cache-busting request showed the same approved section during propagation. This verifies availability of the public content, not Google indexing or improved rankings.

## Next opportunity

Review and package one additional published poker episode only after its final public upload and claim/footage continuity have been verified. Avoid treating video titles, editable draft timelines, inferred suits, or retimed cuts as independently checked hand histories. Alternatively, measure search referrals and actual citations when authorized Search Console data becomes available; do not infer growth from code publication.
