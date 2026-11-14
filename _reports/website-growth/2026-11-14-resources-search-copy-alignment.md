# Resources hub: keep search copy aligned with the published kits

Prepared November 14, 2026.
Canonical resource page: https://nolankido.com/resources/
Previous related releases: PR #333 (new resource kit links), PR #334 (balanced responsive layout).

## Problem confirmed

The visible Resources hub now offers an AI workflow pilot, AI-answer citation audit, game-design demonstrations, and a wine-tasting worksheet. Its public title and description are controlled by `_source/search-entrypoints.json`, a separate source that still used November 6 wording about the earlier collection.

The base `_source/pages.json` described the page differently again. This did not establish a search ranking problem, but it made the public description less specific and encouraged future source and generated-output drift.

## Focused change

- Rewrite the authoritative Resources description to accurately preview the current free AI workflow and citation audit tools, playable game-design demonstrations, poker guides and editable wine-tasting worksheet.
- Align the base manifest's title and description with the actual final metadata of this page. Keep the existing generated title: `Useful Tools, Worksheets & Reading Guides | Nolan Kido`.
- Update the reviewed entrypoint metadata's modification date to November 14, the same genuine revision date already recorded in the manifest and sitemap. Do not bump an unrelated or future date.
- Update the committed `resources/index.html` text consistently across the HTML meta description, Open Graph, Twitter card, JSON-LD CollectionPage schema and the visible introductory sentence.
- Keep the canonical `/resources/` URL, CSS, four kit cards, ten downloads, page headings, and sitemap unchanged.
- Add two permanent tests in the existing local Resources regression group to require metadata agreement and visible/search/schema consistency.

## Why this copy is appropriate

Google Search Central says search result snippets are derived primarily from page content and may use a suitable meta description. Specific, human-readable descriptions help users understand what a page offers. However Google can display different excerpts, and a metadata update is not evidence of improved rankings, clicks or AI referrals.

Source: https://developers.google.com/search/docs/appearance/snippet
Title guidance: https://developers.google.com/search/docs/appearance/title-link

## Verification boundary

A targeted, read-only repository check compared the source and generated copies, identified each instance of the previous text, verified all five updated description positions, the unchanged title, canonical URL and date, and the preservation of the downloadable Resources kits. Ten focused tests are now defined in `_tests/test_resources_hands_on_kits.py`, including the two new assertions.

A complete local checkout and site-wide release run are unavailable in this workspace, so this record does **not** claim that every historical regression or full browser flow passed. Verify the GitHub merged file hashes and production response separately.

No paid services, GitHub Actions, private analytics, new tracking, claimed clients, private prototypes, or fabricated search outcomes were introduced.
