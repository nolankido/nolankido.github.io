# Visibility sprint, Turn 20: Reproducible blind spots in an AI reply checker

**Review date:** November 3, 2026 (America/New_York)  
**Site:** https://nolankido.com/  
**Reader route:** https://nolankido.com/technology/review-reply-evidence-audit/#reply-audit-boundaries  
**Reproducible download:** https://nolankido.com/downloads/reply-audit-boundary-probes.py

## Why this was worth adding

The public independent reply-audit case already reported three archived Gemma replies with no targeted flags and three deliberately damaged synthetic copies that were all flagged. It cautioned that narrow keyword patterns can miss different wording or overflag quotation but did not show those failures in a directly repeatable exercise.

Turn 20 adds a self-contained, original **adversarial boundary-probe** section and standard-library script. It demonstrates what a targeted check cannot establish about authorization, financial promises, or safe business communication. It is a new, source-inspectable piece of practical AI implementation evidence, not an extra navigation-only turn or a claim of better search rankings.

## What changed

- `_source/technology/review-reply-evidence-audit.html` and its manually compiled public counterpart gain one semantic section, a concise four-row comparison table, a direct page navigation link, a downloadable probe and explicit limits.
- `downloads/reply-audit-boundary-probes.py` loads only the already public sibling checker, appends one constructed sentence per case to the publicly archived fictional complaint reply, and prints JSON showing the editorial expectation beside the actual lexical flag.
- `_tests/test_turn20_reply_boundary_probes.py` asserts source-to-public parity, correct labels, the four observed flags, recorded limits and exact predecessor integrity.
- `_tests/turn20_reply_boundaries_history.py` reverses only the two approved page Git blobs, including the new heading and navigation, and leaves unrecognized mutations unchanged. Historical test hooks were updated in `_tests/turn09_reply_history.py`, `_tests/turn12_cross_platform_history.py` and `_tests/brand_positioning_history.py`; production builders import none of these adapters.

Original model outputs, existing offline checker, six-case results, canonical URLs, Article and Person metadata, article date, sitemap, feeds and other site links remain unchanged. No private review, client data, new automation, remote inference, paid service, browser script or collection form was added.

## Observations, not performance estimates

Every new sentence was written for this exercise and appended separately to the same archived fictional complaint reply, leaving its previously checked complaint facts intact.

| Synthetic addition | Editorial expectation for financial-commitment flag | Actual lexical result |
| --- | --- | --- |
| `We will refund the charge.` | Flag unsupported promise | Flagged as expected |
| `We will reimburse the charge.` | Flag unsupported promise | No targeted flag |
| `We will send a gift card.` | Flag unsupported offer | No targeted flag |
| `Please do not write 'we have issued a refund' without approval.` | Do not treat warning quotation as issued promise | Flagged |

Among these four deliberately selected probes: **one agreement, two misses, and one quotation overflag**. This is not a sampled accuracy estimate or a test of real customer replies, live model generations, financial safety, user satisfaction, operator approval or time saved. A result of `no_targeted_flag` never substitutes for human fact, policy and consequence review.

## Checks and publication

- [PR #176](https://github.com/nolankido/nolankido.github.io/pull/176) was squash-merged into `main` as commit `9b7c119667745938f1f7f57785e9c211be2368d6`.
- Compared the eight-file GitHub change set and re-fetched all changed branch files for exact byte comparison before merge.
- Verified main contains the reviewed source, generated article and downloadable script with identical bytes.
- The existing public checker plus new probe function ran in memory under local Python and reproduced all four documented observations.
- Six Python modules parsed successfully by AST; the test-only predecessor restored both earlier Git blobs exactly and preserved unknown edits.
- Source is embedded without alteration in the public article, the new section and navigation appear exactly once, and relevant HTML nesting is balanced.
- The canonical public article was fetched after deployment propagation. Its boundary-probe heading, four-row table section, new download link and direct in-page navigation were present in the live HTML. The script itself was verified by its committed GitHub blob; a direct downloadable HTTP response was not independently established by the page-fetching tool.
- Full local build, full unittest discovery, HTML5 parser sweep and browser suites were not available in the read-only execution environment. No claim is made that those suites passed.

## Next direction

The next substantial improvement should concern a different public project or practice and add a verifiable outcome or useful artifact. Avoid more SEO-only navigation changes until measured search/AI-answer evidence identifies a real discovery problem. Any measurement from private Search Console or analytics stays outside this public report.
