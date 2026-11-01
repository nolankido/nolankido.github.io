# Visibility sprint: Player profile in internal Find

**Date:** November 1, 2026
**Repository:** [nolankido/nolankido.github.io](https://github.com/nolankido/nolankido.github.io)
**Change:** Include the already public, independently verified player profile in the site's on-page Find index.
**Status:** Merged to main November 1, 2026. Direct public HTTP release-byte verification remains unconfirmed.
**Owner constraint:** Never use, restore, dispatch, or rely on GitHub Actions for this website.

## Scope and motivation

The canonical `/poker/nolan-kido/` player page and its independently sourced tournament results were published to the repository, and an exact page reference was added to the main sitemap. However, `/find/` was still a strict projection of the ordinary page manifest, which does not own this manually built profile. A local search for Nolan Kido or his WSOP results could therefore omit the person page even though it existed.

This pass adds **one** search result without making the primary manifest or sitemap own the profile twice.

## Changes

- `_scripts/player_find.py`: derive a search record only after `player_sitemap.record(root)` validates the existing published profile, its original source, canonical URL, structured identity, and native links. Parse the public H1, `title` and description from that HTML; require the title and description to agree with the visible Schema.org record. Do not inspect private files or live queries.
- `_scripts/build.py`: render the original manifest search entries plus this exact one validated public result. The ordinary `site_find.entries()` contract and main manifest remain unchanged.
- `_scripts/site_find.py`: recognize a new, accurate `profile` type with the visible label **Player profile**.
- `_source/find.html` and generated `find/index.html`: add an explicit **Player profiles** type filter and a native link under Poker. Preserve the existing browser-side filtering, labels, result grouping and privacy statements.
- `_tests/test_player_find.py`: check one result, source provenance, title and summary, four unchanged groups, filter compatibility, real Node search matches and negative metadata-tampering cases.
- `_tests/player_find_turn_history.py` and `_tests/test_player_find_turn_history.py`: exact Git-blob predecessor guards for six reviewed existing file changes, with unknown mutations passed through. No frozen older snapshot was rewritten.
- `_scripts/local_release_checks.py`: add the Find contract to the local release checker. `AGENTS.md` documents that the profile is now included in Find without changing its manual builder ownership.
- Adapt older test-only discovery assertions to first see their reviewed predecessor bytes. Also retire a stale historical test that expected the forbidden GitHub Actions workflow to exist, replacing it with an explicit absence/owner-policy check.

## Checked repository results

A direct read of the committed review branch confirms:

| Check | Observed result |
| --- | --- |
| Find search cards | **181** |
| Poker collection cards | **93**, up from 92 |
| Player-profile URL in results | **Exactly one** |
| Type filter | `profile` present; visible label **Player profiles** |
| Card title | **Nolan Kido: Tournament Poker Player** |
| Source summary | Original reviewed public profile description; not invented keywords |
| Core group layout | Technology 16, Living Well 69, Poker 93, Creative Work 3 |
| Existing search-section data | Preserved. The new profile is searchable by title, description and URL words. Its section headings are not separately indexed in this pass. |
| Historical predecessor checks | Exact reversal independently confirmed for six existing changed files, with pinned Git blob IDs. |
| GitHub Actions | No workflow was created, run, or restored. |

The full Python and browser suites were **not run** in the current sandbox because it cannot clone the GitHub repository or directly fetch the live site. Static repository checks and reversible changes are not substitutes for those suites. The reviewed page is committed to the repository, but a successful direct public HTTP GET and exact live-byte check are still **unconfirmed**.

## Search relevance and privacy

The on-page Find result uses the same static, browser-local filter as existing site entries. No external search provider, API call, cookies, query persistence, location data, new credentials, personal financial disclosure, ranking claims, or extra markup for invented achievements is introduced. A search result in this site's own Find page is not evidence of Google indexing or AI assistant citations.

## Next improvements

When a local full-site test environment is available, run `python _scripts/local_release_checks.py --full --browser`, resolve any remaining historical test expectations and verify `/find/`, `/poker/nolan-kido/` and `/sitemap.xml` by exact read-only public responses. After that, prioritize only factual, approved poker episode companions, not speculative result pages.

## Release receipt, November 1

- [PR #161](https://github.com/nolankido/nolankido.github.io/pull/161) squash-merged to `main` at `a86763f659ddcca81437f34ed78bca8644b631eb`.
- A fresh read of `main` confirms **181** Find result cards across Technology 16, Living Well 69, Poker 93 and Creative Work 3, and exactly one `/poker/nolan-kido/` entry with a visible **Player profiles** filter.
- The previously merged primary sitemap still contains **196** unique URLs and exactly one player-profile URL. The main builder now includes the player Find adapter, and the local release script includes the focused Find test. The owner prohibition on GitHub Actions is unchanged.
- All six modified existing files were independently reversed to exact ancestor Git blob bytes during review; no historical snapshots were rewritten. These are structural/repository checks, **not** executed full Python/browser suites.
- Public web retrieval remained unsuccessful or returned older search-crawl snapshots, so this turn does **not** assert current live bytes, search-engine indexing, ranking gains, or new AI citation traffic.
