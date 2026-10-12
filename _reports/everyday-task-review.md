# Everyday tasks: search visibility and public presentation

Baseline: `f2557e06531927468c9194c5b72ca7b769c5ef25` (PR #42).
Review scope: the existing Technology entry point, seven Living Well worked guides,
their original templates, and the worksheet directory. This is a follow-on release,
not a claim that the previous work increased search traffic.

## Assessment

The site already has a recognizable person-first introduction, linked authorship,
canonical URLs, breadcrumbs, working tools, and a documented implementation case.
Another generic article collection or new claim of expertise would add little to
that foundation. The useful next step is to connect the practical-AI positioning
to recognizable tasks that a reader can actually finish.

The seven existing Technology for Real Life worked guides already describe their
inputs, a simple non-AI route, a concrete outcome, a stopping point, and a plain-text
starter. Before this change, that starter could be selected on the page, but it
was not available as a normal file download. Technology linked to the series in
broad terms instead of exposing the seven tasks individually. Search titles were
based on the original editorial wording, which was less explicit about the task
and the available worksheet.

The chosen change is to make the existing work more useful and easier to find,
not to duplicate it under new URLs. The intended public impression is practical,
careful judgment: help with an ordinary task, retain the person's decisions, and
use AI only when it earns its place. This is a qualitative editorial judgment,
not a measured change in how visitors perceive Nolan.

## Implemented scope

1. Technology's existing `#technology-path` becomes a seven-task menu. Each card
   names a task, describes one boundary, and repeats the original guide's stated
   outcome. Existing tool previews, the recorded case, and primary navigation remain.
2. Eight existing routes receive more descriptive search titles and descriptions:
   the series overview and seven guides. The worksheet hub's description also
   changes to reflect its expanded download menu. No URL, H1, publication date,
   original guide body, or evidence label changes.
3. Seven standalone `.txt` downloads are generated from the original
   `utility.starter` strings. No headers, invented results, or alternative versions
   are added. The original visible preview and the downloadable UTF-8 bytes match.
4. Each guide exposes the worksheet near its outcome summary and beside the full
   preview. The worksheet directory adds a task-sheet menu while preserving the
   original five reflection worksheets. Task guides link back to the task menu and
   the worksheet directory.
5. The same bounded metadata reaches the existing internal-search and related-card
   presentation through the public manifest. All five RSS files remain byte-stable.
   No duplicate articles, artificial new publication dates, or feeds are added.
6. A small scoped stylesheet supports mobile and desktop task cards. There is no
   new runtime JavaScript, account system, form, analytics event, or network service.

## Search-intent hypotheses, not keyword-volume findings

| Existing guide | Reader task made explicit |
| --- | --- |
| scattered-notes-to-next-step | Organize notes into action items |
| shared-plan-people-can-use | Make a shared plan with decisions, owners, and dates |
| find-the-document-you-need | Find and organize the original document |
| rough-idea-to-small-creation | Turn rough notes into a draft using a creative brief |
| make-digital-reading-easier | Use reader view, text size, and read-aloud support |
| reflection-with-your-judgment-intact | Reflect using bounded questions, with optional AI |
| did-the-tool-actually-help | Evaluate effort, quality, upkeep, and tradeoffs |

These are derived from the pages' actual content. No search-volume estimate,
competition score, current ranking, or traffic upside was available or invented.
Google can rewrite search-result titles and snippets; the supplied metadata is
not a promise of how the result will appear.

## Implementation and maintenance

- `_source/everyday-tasks.json`: selection, task labels, and metadata overrides.
- `_scripts/everyday_tasks.py`: strict validation and escaped native cards.
- `_scripts/living_well_utility.py`: one source for preview and download bytes.
- `_scripts/living_well.py`: directory integration and generated exports.
- `_scripts/build.py`: manifest-level presentation overrides and scoped stylesheet.
- `_scripts/check_live.py`: verifies the seven download responses and new stylesheet.
- `_tests/test_everyday_tasks.py`: nine focused tests with independent preservation
  contracts for 138 baseline files and the complete public-page identity inventory.
- `_tests/everyday_tasks_browser.py`: native journeys/downloads with scripts enabled
  and disabled, reflow, text spacing, print content, and optional axe scans.

Two older snapshots of rendered presentation were updated for intentional
Technology/reader-card changes. Original content and feeds are pinned separately;
no content preservation assertion or browser suite was removed.

## Validation before submitting the release

The local complete unit/content run passed 375 tests. The 190 generated outputs
match source. HTML5 parsing and the search audit pass on all 168 HTML pages. There
remain 163 indexable sitemap URLs, 87 Article records, 166 breadcrumb pages, and
five noindex pages. All five original feed files match the baseline byte for byte.

A separate traversal of the actual rendered anchor graph, excluding noindex
pages as intermediate nodes, reaches all 163 indexable pages from Home. Depth
counts are 1 / 19 / 94 / 49 at depths 0 / 1 / 2 / 3. Each of the seven task guides
is reachable in at most two links; the existing homepage review guide remains at
one. This is crawlable navigation, not proof of Google indexing.

Offline browser checks passed 72 layouts and 72 text-spacing checks with scripts
enabled and disabled. Desktop/mobile screenshots were inspected. The offline
mode cannot establish native HTTP journeys, download behavior, or axe results.
The pull request must pass all 24 browser suites before merge, and the published
release must pass its separate 254-target live-response check. Consult the merged
PR's final receipt for those outcomes; the numbers here are the expected coverage,
not a pre-emptive claim that the remote or deployed checks have passed.

## Measurement and boundaries

GSC Wizard was queried again. `nolankido.com` was absent from the connected
properties, so no authenticated query, page, indexing, or Core Web Vitals report
was obtained. No unrelated property's figures were used. No DNS, Search Console,
registrar, hosting, contact, analytics, or account settings were changed.

To measure the release later, first establish access to the correct Search Console
property, inspect the existing canonical URLs, and record query/page impressions
and clicks across comparable windows. Separate the person's name searches from
queries about a specific task. At low volume, individual daily movements will not
be adequate evidence of an effect. The release does not establish a ranking gain.

Original guide examples remain illustrative. No private project details, personal
results, biography expansion, credentials, profile links, or portrait were added.
Downloaded blank sheets contain no user answers. Completed worksheets are handled
wherever the reader chooses to keep them. Existing sitewide privacy disclosures
continue to apply to ordinary page visits.

## Primary search guidance reviewed

- Google: descriptive, concise title links grounded in the page content.
  https://developers.google.com/search/docs/appearance/title-link
- Google: crawlable anchors and meaningful internal-link context.
  https://developers.google.com/search/docs/crawling-indexing/links-crawlable
- Google: helpful, people-first content and useful original value.
  https://developers.google.com/search/docs/fundamentals/creating-helpful-content

These sources motivate the design choices. They do not guarantee ranking gains
from this release or establish a special ranking benefit for text downloads.
