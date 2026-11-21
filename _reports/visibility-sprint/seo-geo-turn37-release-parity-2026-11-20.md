# SEO/GEO improvement Turn 37: Main release qualification and snapshot parity

**Date:** November 20, 2026 (Pacific/Honolulu)  
**Repository:** [nolankido/nolankido.github.io](https://github.com/nolankido/nolankido.github.io)  
**Starting \`main\` commit:** \`f2778e7f0295d289bbb070b0bd9266f260e9f5ae\`  
**Next planned turn:** 38, live URL and response-byte verification.

## Goal and actual scope

The new 25-turn roadmap calls for a complete checkout-based release qualification at Turn 37, including deterministic builds, SEO, standalone books, HTML5, full historical and browser tests. This session could read and edit the authenticated GitHub repository, but the execution container could not resolve \`github.com\` to clone a complete checkout. Therefore **the full local release suite, Python builder, HTML5 parser and Playwright browser tests were not run**. Do not present this turn as a completed end-to-end release certification.

A remote, read-only source audit was completed on the exact starting \`main\` commit, and a concrete gap in the release procedure was corrected: the default local release suite previously audited current metadata but did not compare its result with the committed \`_reports/search-audit.json\`. A stale but green historical snapshot could be left in source control.

## Remote source-level release observations

| Check | Observation | What it proves |
| --- | --- | --- |
| Git tree | 2,415 tree entries, of which 2,144 are blobs | Repository inventory on the pinned starting commit, not successful local execution |
| Main sitemap | 229 \`<loc>\` URLs, all distinct | Committed sitemap itself has no duplicate URL records |
| Sitemap path existence | 229/229 URL paths resolve to a committed published target | No missing committed HTML target on these canonical routes |
| Book source/output parity | \`/books/\` and two standalone book pages have identical Git blob SHA values to their respective \`_source/books/\` files | Exact source equality on these three pages in source control |
| Critical page source inspection | 13 representative HTML pages each have one title, one H1, one main element, a matching self-canonical, and one parseable JSON-LD script | Important metadata is coherent in committed HTML; not an HTML5 parser or browser run |
| Robots policy | Committed \`robots.txt\` advertises the primary sitemap | Presence of a crawl hint, not indexing |
| Repository-authored Actions workflows | Zero \`.github/workflows/*.yml\` or \`.yaml\` files | Permanent no-GitHub-Actions rule remains intact |
| Committed SEO report | Records 225 manifest pages, 5 noindex pages, 133 articles, 2 standalone books, 1 books hub, 229 sitemap URLs and no errors | **Historical committed snapshot**; live recomputation was not available |

The standalone player profile and video companions use distinct builder transformations, so their source and public blobs are **not expected** to be identical; they require their own recorded local builders and tests.

## Actual release-gate improvement

1. \`_scripts/check_search.py\` now has \`--verify-snapshot _reports/search-audit.json\`, which computes the current audit then compares **all** fields with the committed snapshot. Missing, invalid, obsolete, or changed fields fail the command, and the snapshot is never silently rewritten.
2. \`_scripts/local_release_checks.py\` now invokes this verification as its required SEO step and separately executes \`test_search_audit_snapshot.py\`.
3. \`_tests/test_search_audit_snapshot.py\` adds eight test cases, including negative controls for stale sitemap counts, missing/extra fields, missing files, invalid JSON, non-object JSON, plus a full current-audit comparison.
4. \`AGENTS.md\` documents the parity gate and the deliberate refresh command; do not edit audit numbers manually.

**To verify from a complete local checkout:**

\`\`\`powershell
py -3 _scripts/build_books.py --check
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 -m unittest discover -s _tests -p test_search_audit_snapshot.py -v
py -3 _tests/check_html5.py
py -3 _scripts/local_release_checks.py --full --browser
\`\`\`

If a legitimate publication changes SEO counts, first run \`py -3 _scripts/check_search.py --json _reports/search-audit.json\`, review the report diff, and then rerun the verification. **Do not refresh a failing report merely to force a green gate.**

## Test and completion matrix

| Component | Status |
| --- | --- |
| Repository inventory / sitemap path existence | Source-verified |
| Representative canonical, title, H1, main, and JSON-LD | Source-verified on 13 routes |
| Book source/output three-page identity | Source-verified by exact Git blob SHA |
| New Python source and negative control test files | Added to release path; full execution not run in this environment |
| \`build_books.py --check\`, \`build.py --check\` | Not run: full checkout unavailable |
| \`check_search.py --verify-snapshot\` and negative tests | Not run end to end: full checkout unavailable |
| HTML5 parsing / all site unit tests | Not run |
| Desktop / mobile browser tests | Not run |
| HTTP production and byte parity | Deferred to Turn 38; not inferred from GitHub |
| Google index coverage, rankings, clicks, AI citation | Not measured |

**Release disposition:** *Conditionally source-checked, not fully qualified.* No current-source broken sitemap targets, book source drift or conflicting representative canonical URLs were found in the bounded audit. The missing complete checkout tests remain outstanding. A future test failure requires investigation, not optimistic dismissal as historical fixture drift.

## Next-turn handoff

Turn 38 should do independent HTTP status, canonical and exact-byte checks on the live site: Home, About, Technology, AI portfolio, \`/books/\`, both books, \`/poker/10bb/\`, sitemap, robots and original worksheets. Include the Search Console comparator download. Use the existing fixed-target \`check_live.py\` where permitted and classify DNS/network errors as **inconclusive**, never as proof of a 404. Also rerun the new Turn 37 local snapshot gate on a complete checkout before calling the current release fully qualified.

No GitHub Actions, cron, paid APIs, traffic instrumentation, private exports or automated outreach were introduced.
