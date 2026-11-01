# Visibility sprint: Turn 5 follow-up, canonical player-page sitemap integration

**Date:** November 1, 2026
**Site:** https://nolankido.com/
**Review branch:** `visibility-sprint-player-sitemap-20261101`
**Status:** Proposed publication, pending final scoped review and merge.
**Owner rule:** Never restore or use GitHub Actions for this project.

## Why this change exists

The tournament-player page was created at `/poker/nolan-kido/` and linked from Poker and About in merged PR #159, but it was intentionally kept outside the main generated page manifest. The existing sitemap generator therefore omitted the profile. It was a crawlable linked page, but it had no sitemap entry or read-only live-release byte target.

This change **adds the already-written, independently sourced page to the existing canonical sitemap** without moving page ownership or inventing a duplicate page. It does not claim that Google or AI assistants have indexed, recommended, or cited the page.

## Release implementation

- `_scripts/player_sitemap.py` registers a single bounded manual URL, `https://nolankido.com/poker/nolan-kido/`, with lastmod `2026-11-01`. It validates that a nonempty editable source actually appears verbatim in the published HTML, plus one H1, one canonical, matching `og:url`, one Schema.org `WebPage` carrying the stable Nolan Kido Person `@id`, matching dateModified, no noindex, and native links from Poker and About. Partial or inconsistent publications fail closed. Reduced isolated build fixtures lacking both profile source and page may omit the separate route.
- `_scripts/build.py` calls that validator when generating the existing `sitemap.xml`. It does **not** create a second sitemap, create a new author identity, or take over the standalone profile compiler.
- `sitemap.xml` now lists **196** unique canonical URLs, up from the previous 195, including exactly one `/poker/nolan-kido/` entry with its reviewed lastmod.
- `_scripts/check_search.py` audits the manual canonical along with the core manifest. `_scripts/check_live.py` includes its complete public HTML as an expected HTTP 200 response, so independent manual live verification can detect missing pages and outdated bytes.
- `_scripts/local_release_checks.py` now invokes the dedicated regression tests locally with no paid API and no CI workflow.
- `_tests/test_player_sitemap.py` checks successful registration, unique sitemap membership, builder consistency, read-only live-target coverage, and rejections for wrong canonical, noindex, stale modified date, altered body, and missing source.
- `_tests/profile_sitemap_turn_history.py` and its test capture exact reviewed predecessor blobs and preserve older release baselines without silently hiding unknown modifications. `_tests/later_release_history.py` and `_tests/test_site.py` are scoped to account for the one new manual route.
- `AGENTS.md` documents this split ownership and the continued prohibition on GitHub Actions.

## Evidence and limitations

The profile already links independent, event-specific WSOP and The Hendon Mob results. No new event placement, ranking, prize or credential is asserted in this turn.

The new sitemap registration and its source/HTML contract were checked against the committed repository content. The sitemap insertion is an exact one-record addition and preserves all 195 previous URLs. The tests were authored for local Python execution. **The full Python/unit/browser suite cannot be claimed as run in this session**, and no GitHub Actions were used. The public site is not considered independently live-byte verified until a direct successful GET of the current release has been checked against the committed bytes.

The existing **on-site Find index is still generated from the core page manifest**, which does not yet include the manual player profile. A future bounded improvement should add the profile to that discovery surface without mislabeling it a guide or allowing the main builder to overwrite the manually compiled page. Do not falsely advertise internal search coverage before then.

## Relevant documents

- [Player profile source and release report](https://github.com/nolankido/nolankido.github.io/blob/main/_reports/visibility-sprint/sprint50-turn05-player-profile-2026-11-01.md)
- [Public player page](https://nolankido.com/poker/nolan-kido/)
- [Poker hub](https://nolankido.com/poker/)
- [Public WSOP profile](https://www.wsop.com/players/448066374/nolan-kido/)
