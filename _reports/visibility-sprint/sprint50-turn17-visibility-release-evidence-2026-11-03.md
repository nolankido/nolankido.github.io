# Visibility sprint, Turn 17: Source-linked release evidence on Nolan Kido's website

**Review date:** November 3, 2026  
**Site:** https://nolankido.com/  
**Purpose:** Strengthen public credibility for Nolan Kido's practical AI implementation work by making actual site changes traceable, useful, and distinct from outcomes that have not been measured.

## The opportunity

The site already contained specific AI projects, an independently auditable local-model example and a small-business pilot guide. A reader could see the output but needed to follow separate GitHub history to learn what an AI-assisted discoverability sprint actually changed and how those changes were checked.

Turn 17 adds one plain-language release case to the Technology hub. It is not a new client story, benchmark, ranking claim or duplicated keyword landing page.

## Public content

[What did an AI-assisted website visibility sprint actually change?](https://nolankido.com/technology/#site-visibility-evidence)

Three documented interventions are explained with public evidence:

| Intervention | Exact source | Verifiable claim | Important limit |
| --- | --- | --- | --- |
| Improve access to real work | [PR #171](https://github.com/nolankido/nolankido.github.io/pull/171) | Homepage and About gained descriptive links to the local AI laptop guide, reply audit and player record | More links do not themselves prove indexing or traffic |
| Align dated signals | [PR #170](https://github.com/nolankido/nolankido.github.io/pull/170) | Four landing-page `lastmod` dates were corrected after substantive revisions | A truthful timestamp does not guarantee ranking movement |
| Add a useful operator guide | [PR #172](https://github.com/nolankido/nolankido.github.io/pull/172) | Technology gained an original small-business AI pilot guide with approval limits and review criteria | Instructional content is not a measured client deployment |

The new section also explains editable source versus generated public HTML, local destination checks, direct public retrieval after publication, the importance of a manual fallback, and what external query/page measurement would be needed before asserting discoverability gains.

It points readers to [Google's link best practices](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) and [sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) as official technical background, not third-party validation of this site's results.

## Implementation

- Edited `_source/technology/home.html` and generated `technology/index.html` with an exactly matching standalone section and a visible contextual introduction link.
- Added `_tests/test_turn17_site_visibility_evidence.py` and its SHA-gated predecessor `_tests/turn17_site_visibility_evidence_history.py`.
- Extended the test-only Turn 16 predecessor and focused test to normalize this reviewed revision, preserving prior exact-release history.
- Left the Technology canonical, metadata, Person identity, existing project cards, published URL, sitemap modification date, stable sections, other page files, navigation and third-party source links unchanged.
- No GitHub Actions, CI, scheduled jobs, paid APIs, extra analytics, confidential records, new credentials or performance claims were introduced.

## Verification

- Inspected the six-file GitHub compare; it included only the two site files and four test-only files.
- Checked byte-identical authored section in source and public output.
- Checked that removing the two targeted edits restores the exact preceding bytes of both files.
- Verified the new anchor appears once, the incoming contextual link appears once, three evidence links point to existing published pages, all three cited PR paths are correct, and original project cards and earlier guide sections remain present.
- Parsed the four revised and new Python test files successfully with the local Python AST parser; computed Git object hashes of the four changed files exactly matched GitHub's blob identifiers.
- The full local deterministic builder, automated unit test suite, HTML5 parser and browser suites were not run in the available read-only environment. No complete-suite pass is claimed.
- No Search Console ranking, indexing, click or impression result was available to attribute to this turn.

## Publication

- [Pull request #173](https://github.com/nolankido/nolankido.github.io/pull/173) was squash-merged to `main` at commit `169d0a647929eea743cb83092e0f86db65e77738`.
- Main-branch source and generated files were re-fetched and exactly matched the reviewed changes.
- Public Pages verification: The live Technology page's `#site-visibility-evidence` section was fetched after propagation. It contained the approved heading, exact PR #170/#171/#172 links, and the caveats about unmeasured search outcomes. The existing `#ai-works-human-decides` section also contained the incoming link to `#site-visibility-evidence`. This verifies the published reader pathway, not index status or a ranking change.

## Next focus

Prefer a distinct, inspectable technical or poker case with reliable source documents and reader utility. Avoid adding further broad navigation links unless a specific missing pathway is identified. Measure sustained branded and nonbranded performance when permitted primary data is available; do not infer it from deployment success.
