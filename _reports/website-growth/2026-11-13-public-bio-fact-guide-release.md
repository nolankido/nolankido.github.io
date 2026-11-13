# Public biography: sourced facts for accurate introductions

Reviewed: November 13, 2026

## Audience and discovery gap

The public `/bio/` page already provides reusable short and long introductions.
Those texts serve visitors who need a concise profile, but the page did not
offer a direct verification trail for its newest public evidence, including
the 2012 peer-reviewed accounting paper and the RightsReceipt open-source
hackathon project. The new source guide helps a reader or editor choose
appropriate sources for each claim while keeping the original reusable
biographies unchanged.

## Substantive changes

- Add an anchored public-fact guide on `/bio/`, organized by evidence type:
  independent scholarly records, a publicly submitted software project and
  code, owner-published practical tools, tournament records and first-person
  video, and personal interests.
- Link the 2012 publication's DOI and MIT manuscript record, RightsReceipt's
  public submission and source code, the site's own reproducible AI pilot,
  and the distinct first-person poker sources. State the limits of each source
  directly in the visitor-facing prose.
- Add a citation-route explanation so readers can link to the relevant
  permanent resource instead of only to the homepage.
- Link About directly to the source guide, update the biography's descriptive
  search snippet, and mark its material November 13 revision in the manifest
  and generated sitemap. No historical research publication date changes.
- Include dedicated regression tests in the existing local-only release gate.
- Improve the local release runner's failure summary to list failed group names
  after the overall count. This surfaced a redundant top-level portfolio link,
  which was corrected to use precise, existing portfolio section anchors.

## Not established

No current appointment, additional professional credential, AI model benchmark,
hackathon award, official poker creator program membership, business impact,
search ranking, indexing, AI citation, or traffic lift is inferred. The page
uses owner-published context for self-described interests and independent
records only for the public facts each record actually supports. No private
records, paid services, new tracking or GitHub Actions are involved.

## Verification

Executed on the final candidate with the preinstalled local HTML parser
dependency available through `PYTHONPATH`:

- `python _scripts/build.py`: 235 generated files, with four intended page,
  search-directory and sitemap changes before the final small link revision.
- `python _scripts/build.py --check`: 235 generated files, zero differences.
- `python _scripts/local_release_checks.py`: **86/86 groups passed**; neither
  authored GitHub Actions nor a third-party CI service was invoked.
- `python _scripts/check_search.py`: 206 public sitemap URLs, 206 distinct
  page titles and descriptions, 115 articles, and no errors.
- `python _tests/check_html5.py`: 211 pages with no failures.
- `python _scripts/check_internal_links.py`: 14,266 internal links, no issues.
- Dedicated biography and public portfolio tests: both suites pass.

Run direct public GET and exact-byte comparisons for the changed Bio, About,
Find, and sitemap routes after merge; document any incomplete hosting
propagation separately. A passing local gate cannot prove traffic or citation
improvement.
