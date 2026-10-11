# Cross-interest site discovery

Date: 2026-10-11
Baseline: c898d68d73e4868ef082f153c87d7386fdfc6db3

## Reader problem and scope

The site has curated introductions and specialized resource finders, but readers
still needed to guess a collection to locate a topic. `/find/` is one entry point
across the four established interests. It is a discovery feature, not a new
identity, article factory, project portfolio or external provider directory.

The Search shortcut is available on every page beside Writing and Start here.
The six-link primary navigation is unchanged. Writing, Resources, Start here and
the missing-page recovery now offer a direct search route.

## Content model

`_scripts/site_find.py` derives titles, summaries, dates and page types from the
published manifest. `_source/discovery.json` supplies only the six original notes'
interest labels and a small set of deliberate cross-interest associations. It
does not copy article text or provider records. A family-story guide can match
both Creative Work and Living Well while appearing only once.

The index covers essays, guides, and subject collections/reference pages. It
excludes noindex pages, proposed experiments, administrative/identity pages and
the specialized search interfaces. About and the outside-resource finders are
linked separately. It searches page titles, summaries and interest labels, not
full article text or outside websites; this limit is visible on the page.

Static grouped links are complete before JavaScript runs. The optional script
filters and orders those same links in place. Short tokens such as AI match words,
not arbitrary letters inside unrelated words; longer words allow prefixes and a
small plural normalization. All meaningful search words must match. Results are
grouped by their canonical home collection, with stronger title matches first.

## Privacy and accessibility

There is no search form action, query-string forwarding, remote index request,
search logging, query analytics, browser-storage API or third-party search service.
The script changes only existing DOM nodes. It does not use innerHTML to render
queries. Controls have native labels, a bounded search input, a polite count
announcement, an explicit results jump and a keyboard-operable reset. Query input
is cleared on page exit and on a restored browser page. Browser behavior outside
the site's code is not promised or controlled.

When JavaScript is disabled or the search script is blocked, the controls remain
hidden and native details/links still work. Zero results explain how to recover
and link to Start here and Resources. Shared utility navigation wraps at narrow
widths; the finder stylesheet and script load only on `/find/`.

## Preserved boundaries

The personal introduction, identity configuration, biographies, original article
bodies, publication dates, all three feeds, both large subject source collections,
contact/privacy controls, analytics settings, social cards and hosting settings
are unchanged. The shared shell and its deliberate snapshot hashes advance only
for the Search shortcut and small-screen spacing. Script allowlists are extended
only for the new local asset on the new page. Existing guardrails remain in place.

## Verification and maintenance

Run the generated-output check and complete unit suite. The focused unit tests
exercise canonical coverage, exclusions, overlapping interests, escaped metadata,
configuration failures, matching behavior and absence of query transport/storage.
`_tests/site_find_browser.py` tests real local URL navigation in CI, blocked and
disabled scripts, query/filter/reset behavior, zero results, actual keyboard
journeys, and no additional requests while filtering. It checks five widths in
three states, with normal and expanded text spacing. With AXE_PATH it runs three
additional accessibility scans. `--offline` deliberately omits URL navigation
and runs in-memory rendering/interaction for restricted local environments.

Review Search desktop/mobile screenshots. Check the public page and exact asset
bytes after deployment. Temporary preparation files must not reach the release
tree. Search interface tests do not replace a complete accessibility audit or
claim support for every browser.

Implementation references: https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html
and https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/search
