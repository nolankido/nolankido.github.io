# Website growth, Turn 10: verifiable public introduction

Original editorial revision: October 17, 2026. Source branch release record; deployment must be checked independently.

## Reader value

The About and Biography pages explain the same three public proof paths: **Use** the existing AI Task Brief Builder, **Inspect** a documented AI-assisted website repair, and **Understand** the accompanying essay about retaining human judgment. These are different forms of evidence: a local deterministic tool, one historical release case, and a viewpoint. The descriptions make their limits visible rather than implying measured personal productivity, generalized AI reliability, awards, employment credentials, or endorsements.

The shorter and longer copyable biographies remain byte-for-byte identical to their single source in `_source/site.json`, as do their two downloadable text versions. No additional identity, photo, public career history, credentials, testimonials, personal achievements, or new relationship to outside organizations has been invented. The original Technology / Living Well / Poker / Creative Work order and About/Bio links remain. The `try-the-work` and Bio anchors and copy controls are retained.

## Bounded technical release

Six production files change: `_source/about.html`, `_source/bio.html`, `_source/pages.json`, `about/index.html`, `bio/index.html` and `sitemap.xml`. Only the actual About/Bio revision dates advance (October 17, 2026); no essay dates are republished. The profile-specific test-only implementation changes twelve paths under `_tests`: three new files and nine modified files, including exact-SHA historical adapters, independent regression tests, and updated expectations. The combined release also changes two existing discovery-guard test files and adds `_tests/test_discovery_robots_contract.py`, bringing the total reviewed `_tests` paths in this candidate to fifteen. The nine added robots contracts supplement the retained 20 discovery tests. The earlier Turn 06 report's 20-case count describes the predecessor bank, not these additional contracts.

Older golden baselines remain intact while only the reviewed About/Bio delta is reversed. The exact predecessor adapter is SHA256-guarded and returns original bytes only for six reviewed files; unrelated changes remain detectable. The adapter does not run in public browsers.

No new public route, styles, JavaScript, cookie, account, form, analytics event, external app, privacy policy or AI crawler convention. The site already publishes Person and WebPage metadata, so no speculative schema or fictitious proof is added.

## Final robots review reconciliation

The remaining true defect was failure to flag wildcard-group `Disallow: /*$`. The guard now also recognizes this end-anchored catch-all and repeated-star forms, while preserving the distinction from `/$`, which affects only the root URL. A synthetic seven-page end-to-end fixture checks that the complete guard rejects the anchored catch-all. This is a bounded site policy against wildcard catch-all Disallow rules, not a general URL-permission evaluator; Allow exceptions do not waive that policy.

A separate automated suggestion proposed ending a group after any extension directive. That change was not applied because Google's primary documentation says records other than user-agent, allow and disallow are ignored for grouping. RFC 9309 section 2.2.4 also says other records must not interfere with standard records. Regression cases now preserve header grouping across Crawl-delay, Request-rate, Sitemap and an unknown extension, and distinguish groups separated by an actual Allow or Disallow rule.

Primary references checked during qualification:
- https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec (Grouping of rules; URL matching based on path values)
- https://www.rfc-editor.org/rfc/rfc9309.html#section-2.2.4

Local evidence: both Python files compiled, all nine new focused tests passed, and running those tests against the original fetched guard produced failures in the anchored-catch-all checks. That red control confirms the tests detect the original defect. The synthetic fixtures are not actual production pages. The final complete repository suite and browser groups remain required separately on the final committed head.

## Verification and human boundary

Verify deterministic build, all existing tests, HTML5, search checks, keyboard and no-script Bio controls, mobile reflow and download/copy text parity before release. This is an editorial and engineering improvement, not a measured increase in reader trust, unique visits, search results, invitations or authority. The user must approve any later photograph, personal testimonial or credential before publication.

For a real human clarity test: show About and Bio to three unfamiliar readers and ask (1) What does Nolan make? (2) Which link would you use to verify a concrete example? (3) Do you infer a credential or measured claim not actually present? Record actual responses privately; do not publish an invented survey.
