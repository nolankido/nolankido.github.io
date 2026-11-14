# Resources hub: discovery paths to original downloadable kits

Prepared: November 14, 2026
Canonical hub: https://nolankido.com/resources/

## Decision

Several new original resources were buried in separate publication pages. The site's Resources hub still led with earlier AI task-brief, time, weekly-reset and poker links. A visitor looking for the recently published workflow pilot, AI citation method, incremental game study, or wine-tasting notes had to know which section to browse.

This change adds an explicit "Hands-on kits" route in the top resource navigation and four concise, evidence-bounded entries in the existing resource collection.

## Four kits

1. **AI workflow pilot:** completed workflow evaluation guide, blank CSV, fictional six-case CSV and offline standard-library Python auditor. The example is synthetic and does not prove a measured customer result.
2. **AI answer citation panel:** no-cost manual prompt guide, blank CSV, fictional 16-trial CSV, offline Python verifier and monthly worksheet. An assistant answer must be observed and its clickable link manually checked; no actual site rankings or citations are claimed.
3. **Incremental game design:** playable teaching game, upgrade payback comparison and two blank playtest or balancing worksheets. The calculations are not evidence of player retention or a commercial game's success.
4. **Wine tasting:** a source-based observational method and a blank, private-use tasting-note sheet. No professional wine credential or real tasting session is claimed.

All new destinations were verified as existing repository files before the update. No private projects, client data, real Search Console exports or personalized logs were added.

## Release choices

- Reused the existing `/resources/` URL, page title, search description and CollectionPage structured data rather than making a competing thin index.
- Added a visible native anchor and four semantic article cards inside the existing resource section. The new heading uses h3, so no new section-search h2 index entry is required.
- Updated `_source/pages.json`, the generated page's `dateModified`, and the sitemap's `lastmod` to the actual revision date, 2026-11-14.
- Added six focused offline regressions to `_tests/test_resources_hands_on_kits.py`, referenced by the manual release gate. No GitHub Actions or other scheduled deployment tooling was introduced.

## Verification scope

A read-only pre-publication audit checked **18 assertions**, all passing: source/rendered block parity, one navigation anchor, one section target, four article cards, ten downloadable links and five guide destinations, existing headings, local-only new links, evidence limitations, retained canonical URL, consistent modified date in manifest/schema/sitemap, no added em dash, and registration in the manual release suite.

The full deterministic generator and full 89+ group release suite were **not run in this environment** because there is no complete local repository checkout. The six regression tests are committed for future full local execution. A merged GitHub tree and production availability must be checked separately before claiming the deployed site was verified.

## Outcomes not established

This is an information architecture and reader-utility release. More internal links may help discovery, but no Google indexing increase, search ranking improvement, AI answer citation, visitor conversion, or time savings was measured.
