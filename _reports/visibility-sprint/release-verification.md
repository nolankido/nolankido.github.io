# Visibility sprint: preparation and publication checks

Prepared October 27, 2026, Honolulu, before merge. This record covers the local release candidate. Final hosted check, merge, and production-delivery receipts belong in the associated visibility-sprint pull request and GitHub Actions run; this preparation record alone does not establish publication.

## Publication receipts added October 28, 2026

The original preparation record below is retained. Publication has since been verified:

| Release | Required gate | Published commit | Public-response check |
| --- | --- | --- | --- |
| [PR150: project cases and visibility](https://github.com/nolankido/nolankido.github.io/pull/150) | [Site checks #564](https://github.com/nolankido/nolankido.github.io/actions/runs/40648149617), 1,163 unit tests and all five browser groups passed | `116359834b8b48dbd1526c68392d89f9dd7bf1a0` | [494/494 exact responses](https://github.com/nolankido/nolankido.github.io/actions/runs/40664532327/job/122735579913) |
| [PR151: contextual guide links](https://github.com/nolankido/nolankido.github.io/pull/151) | [Site checks #566](https://github.com/nolankido/nolankido.github.io/actions/runs/40666298208), 1,172 unit tests and all five browser groups passed | `1f315095cef741bd1afe6fe3bcba8b11216b0d0e` | [494/494 exact responses](https://github.com/nolankido/nolankido.github.io/actions/runs/40671626565/job/122759561157) |

For each release, the published tree matched the tested tree, GitHub Pages deployment passed, and the public-response job emitted the exact published `LIVE_VERIFIED_COMMIT`. These receipts establish publication of the reviewed implementation. Indexing, rankings, traffic, and AI citations remain unmeasured.

## Completed local checks

- Deterministic build: 229 generated files checked with zero drift.
- HTML5 validation: all 200 HTML pages pass, including the validator's defect-detection self-test.
- Static search validation: 195 sitemap URLs, 110 articles, unique titles and descriptions across 200 HTML pages, and no reported errors. Five intentionally excluded pages retain their existing noindex treatment.
- JavaScript syntax: all 18 existing asset scripts pass `node --check`.
- Independent HTML reproduction: the retained invalid example is detected and the corrected example parses cleanly.
- Visual/browser review: homepage, Technology, Creative, and six new cases pass at 1440px and 390px. All six new cases retain identical main text and source-link counts with JavaScript disabled.
- New page interaction review: four evidence tables scroll inside their mobile containers using the keyboard. Checked section links land below the sticky header with and without scripts. No broken local images, page exceptions, local HTTP errors, or document-width overflow were found. Analytics was intentionally blocked in local browser checks.
- Current practical-path browser contract: original workflow and worksheet behavior remains covered after following the hub to the extracted weekly-reset article. All 13 retained hub fragment links work with and without scripts, for 26 tested legacy journeys. Source disclosures, source-check links, text spacing, decisions, and downloaded workbook bytes pass.
- Current search browser contract: 180 eligible pages have exact, unique coverage in the no-script index, including all six new articles. Section keyboard journeys, URL filters, text spacing, and missing/malformed data fallbacks pass.
- Current article archive browser contract: exact, unique coverage of all 110 articles at four widths with scripts enabled and disabled, including all six new cases. Eight layouts, eight text-spacing views, 32 native disclosure openings, and 20 keyboard journeys pass.
- Source review: selected notes-output rows match the actual retained response; the downloadable record contains the original instruction and complete unchanged input/output. Project statements use the pinned sources in `project-sources.md`.
- Sharing previews: six new 1200 by 630 title cards use the existing generator and design. Every full title fits, catalog and presentation validation pass, and all previous catalog records and assets are preserved. Rebuilding the six article heads leaves their tested body bytes identical.
- Browser regressions were repaired in content and CSS with the original test expectations retained. Creative Work again appears for the real “family story” query, and the complete site-find browser suite passes. Project cards now reduce columns as text grows and wrap long heading words; the exact failing homepage test passes. The complete Technology hub fits 320, 390, 768, and 1440px at 200% text with local/fallback fonts and native disclosures closed/open, covering 16 states. Additional page-scoped wrapping rules preserve normal-size geometry in eight comparisons.
- Source whitespace checks pass, and no additional em dashes were introduced. The six new generated HTML pages retain two whitespace-only lines from the existing template; their HTML validation and deterministic output checks pass.

These local browser runs used Chromium. Their purpose was to check the actual generated pages and revised journeys. They do not establish behavior in every browser, external video playback, or production delivery. The complete hosted browser matrix also includes the site's existing accessibility checks; those remain a required release gate.

## Release gates

The full unit suite and all five hosted browser groups must pass on the final candidate before merge. No historical golden JSON is replaced. A new exact, hash-bound predecessor capsule restores only the reviewed sprint files and additions when older release contracts are evaluated. Unrecognized mutations remain visible.

The build workflow fetches only the fixed published parent commit, `2aae4923318c0028d98266d78f6e4aabea295387`, so independent parent-byte checks work in a shallow Actions checkout. This does not change a branch reference.

After merge, the deployed tree must match the tested tree. The existing public-response verifier covers every page plus the new CSS, both project images, attribution license, and both downloadable records. It compares successful response bytes to the checked-out release and retains the existing expected-404 checks.

## Outcome limits

Passing implementation checks means the site is prepared to expose the new material consistently. It does not mean a search engine has indexed the pages, an AI assistant has cited them, or visibility has increased. Search/citation/referral measurements remain pending as recorded in `baseline.json` and the sprint README.
