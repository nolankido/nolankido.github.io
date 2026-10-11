# Reading and return paths

Baseline: f48997916922601e53c193e388025144cc052cdc
Date: 2026-10-11

## Reader need

The personal introduction and cross-interest discovery already exist. This pass
supports staying with an essay, keeping an attributable reading copy, and returning
for future writing. No new identity, article, or primary navigation category.

## Implementation

`/follow/` explains the combined writing feed and all three existing section feeds.
`/writing.xml` is a deterministic union of the generated Notes, Living Well and
Poker feed records, not a new article catalog or a web crawl. Stable canonical
GUIDs, publication dates, titles and summaries remain intact. Source feed metadata
is carried with each item. Duplicate canonical entries are collapsed only when
records agree; conflicts, hidden entries, proposed experiments and invalid dates
fail the build. Future guide source data must be updated before publishing it.

No feed has been silently repointed. All existing subscriptions continue to work.
The new combined feed is advertised first for discovery; the existing Notes and
section alternates remain. The footer now says Follow writing instead of an
unexplained RSS link to only one collection. Writing and the contact card link to
Follow. The page explains potential duplicate subscriptions and archive entries.

Original Notes essays reuse the existing heading parser for a native expandable
outline of existing h2 fragment links. It operates on the body before continuation
cards and disclosures are added. It does not invent IDs or change source text.

`assets/reading.css` loads only on Notes essays and Follow. The print view hides
outlines, recommendations and navigation; it retains attribution, publication
information, the AI-assistance disclosure, source URLs and a canonical origin link.
A native Keep or share disclosure explains browser print and the permanent link.
No new client script, clipboard permission, external service, subscriber collection,
tracking, account, photograph, credential or firsthand claim is introduced.

## Preserved boundaries

All existing article sources, publication dates, feeds, directory source data,
personal identity, About, biography, contact/privacy, base design, social cards,
analytics settings, vCard and QR payload remain unchanged. The contact card's
introductory paragraph is shortened and links to published interests and writing.
Rendered shared-shell snapshots advance solely for feed discovery and the footer.

## Validation

Validate feed union and history independently; test malformed/duplicate sources
and privacy boundaries. Check keyboard/no-JavaScript outline and return journeys,
readable feed addresses, reflow and print rendering. Confirm all existing suites
and committed output before merge. Verify deployment and live feed bytes separately.
Do not claim an external reader subscription or printer has been tested unless it
actually has. Automated accessibility testing is not certification.

References: https://www.rssboard.org/rss-specification
https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Media_queries/Printing

## Release-verification reliability

The previous main run 38166080483 completed all test stages but reached its
15-minute cancellation boundary before its final live-byte step. Keep every
existing test and give the checks job 20 minutes. Move the unchanged read-only
public verifier into its own ten-minute main-only job, so browser-test duration
cannot prevent verification. It still compares exact bytes against the checkout,
retries pending targets, and checks main before and after the run. The full
pre-release test suite remains required before a manual merge. No continue-on-error,
permissions expansion, deployment change, or skipped test was introduced.
