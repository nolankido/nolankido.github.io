# Poker Finder: keep and manage a private study list

Prepared October 16, 2026 UTC. The published predecessor is
`ff403da6eeb4afbca704e17ce3592a2977011dcd` (PR #104).

## Why this change

The next useful step after finding an explanation is keeping a small set of
sources for later study. The existing Finder allowed up to 12 selections and a
Markdown download, but a visitor had to rediscover a selected result before
removing it. Changing a query or filter could hide its only removal control.

A separate failure was reproduced from the production `renderShelf()` function:
after the first successful export, a failed replacement `URL.createObjectURL()`
left a visible download link pointing at the already revoked first object URL.
The list itself could show two entries while its download was unusable. This is
an injected browser-API failure, not an estimate of how often visitors encounter
it.

This release advances the roadmap's private study tools and accessibility work.
It does not complete saved course progress, qualified teaching review, actual
beginner observation, or human search-relevance assessment. No learner outcomes
are supplied. The observation-dependent course redesign remains pending.

## Visitor behavior

Each selected entry has its own **Remove** control with the source title in its
accessible name. It works even if the original card is hidden by the current
search. Removing an entry moves focus to the next remaining removal control,
then the preceding one when needed, or the search field after the last removal.
The 12-item limit leads back to the visible list to make room for another source.

The list offers **Download this list as Markdown**, **Copy study list**, and a
native **View or copy the complete list** disclosure. The read-only text field
contains the same complete text as the clipboard and download. It remains
usable when the clipboard or download API is unavailable. Download activation
is described as a request, not proof that the visitor saved a file.

An export retains public titles, absolute destination URLs, access information,
source descriptions, limitations, review methods and dates. External sources
also retain a usable link to their full directory listing. It excludes the
search query, matching excerpts, hidden article text and exercise answers. The
snapshot notice does not imply a new source review.

Download replacement removes obsolete links and releases old object URLs.
Failures hide the unusable download and reveal the complete text. Clearing the
list removes the export text and URL. Leaving the page releases an unneeded URL;
a browser-cached page retains its still-live URL for Back navigation.

Clipboard writing happens only after an explicit click. Revision and request
counters stop a delayed clipboard response from reporting success for a changed
list. A failed copy focuses and selects the fallback only if the Copy button
still has focus. Neither path takes focus from a visitor who has moved on.

Selections remain in the current page only. Copying and downloading are explicit
ways to keep the list. There are no accounts, new requests, browser storage,
query collection or changes to pageview analytics.

## Scope and historical evidence

Production changes are limited to `_source/poker/find.html`,
`assets/poker-finder.js`, `assets/poker-finder.css` and generated
`poker/find/index.html`. Search ranking and the 284 existing cards remain intact.
All teaching sources, resource records, dates, routes, feeds and downloads remain
unchanged.

The separate four-file adapter restores the exact predecessor before older
preservation checks. Its baseline fingerprints the existing 480 source/assets
and 221 generated outputs. Previous baselines and release deltas are not
refreshed. Unrecognized mutations are not reversed.

The original 18/30 search baseline, the 29/30 intent repair and the 30/30 title
release remain frozen and reproducible, including without parent Git objects.
The current result is written to `search-results.json` in this folder. These
are authored engineering regressions, not independent judgments from beginners.

## Reproduction

Local verification before opening the pull request passed four new release
preservation checks and all ten existing search intent/title checks. The build
checked 221 generated outputs without drift, and HTML5 and search-metadata
checks passed for all 193 HTML pages. The 284-card Finder browser suite passed
its existing journeys and the new study-list scenarios. The final added
delayed-rejection/focus check also passed separately. The full hosted release
gate remains required on the submitted commit.

Browser coverage includes actual Markdown file downloads; catalogue-context
parity; filtering and keyboard removal; the capacity boundary; absent and
throwing Blob/object URL APIs during first creation and replacement; clipboard
success, denial and delayed settlement; cleanup, print and script-free use.
Clipboard behavior is mocked without writing the operating-system clipboard.
Mobile and desktop screenshots were inspected. These checks do not certify
every browser or assistive technology.

```sh
python _scripts/build.py --check
python -m unittest discover -s _tests -p 'test_study_list_release.py' -v
python -m unittest discover -s _tests -p 'test_poker_search*.py' -v
python _reports/poker-search-intent/evaluate.py --titles-release
python _reports/poker-search-intent/evaluate.py
python _tests/finder_browser.py
```

After a deliberate production edit, rebuild, run this folder's
`capture_history.py`, then run the search evaluator with `--write` and inspect
the new delta and results. Capture rejects other production-file changes or a
changed baseline. The ordinary release gate still runs all regression and
browser groups. Deployment evidence belongs to the pull request and its exact
commit checks.
