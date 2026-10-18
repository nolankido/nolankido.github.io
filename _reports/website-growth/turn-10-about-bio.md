# Website growth, Turn 10: verifiable public introduction

October 17, 2026. Source branch release record; deployment must be checked independently.

## Reader value

The About and Biography pages now explain the same three public proof paths: **Use** the existing AI Task Brief Builder, **Inspect** a documented AI-assisted website repair, and **Understand** the accompanying essay about retaining human judgment. These are different forms of evidence: a local deterministic tool, one historical release case, and a viewpoint. The descriptions make their limits visible rather than implying measured personal productivity, generalized AI reliability, awards, employment credentials, or endorsements.

The shorter and longer copyable biographies remain byte-for-byte identical to their single source in `_source/site.json`, as do their two downloadable text versions. No additional identity, photo, public career history, credentials, testimonials, personal achievements, or new relationship to outside organizations has been invented. The original Technology / Living Well / Poker / Creative Work order and About/Bio links remain. The `try-the-work` and Bio anchors and copy controls are retained.

## Bounded technical release

Six production files are changed: `_source/about.html`, `_source/bio.html`, `_source/pages.json`, `about/index.html`, `bio/index.html` and `sitemap.xml`. Only the actual About/Bio revision dates advance (October 17, 2026); no essay dates are republished. The test-only implementation changes twelve paths under `_tests`: three new files and nine modified files, including exact-SHA historical adapters, independent regression tests, and updated expectations. These keep older golden baselines intact while allowing only the reviewed About/Bio delta to be reversed. The exact predecessor adapter is SHA256-guarded and returns original bytes only for six reviewed files; unrelated changes remain detectable. The adapter does not run in public browsers.

No new public route, styles, JavaScript, cookie, account, form, analytics event, external app, privacy policy or AI crawler convention. The site already publishes Person and WebPage metadata, so no speculative schema or fictitious proof is added.

## Verification and human boundary

Verify deterministic build, all existing tests, HTML5, search checks, keyboard and no-script Bio controls, mobile reflow and download/copy text parity before release. This is an editorial and engineering improvement, not a measured increase in reader trust, unique visits, search results, invitations or authority. The user must approve any later photograph, personal testimonial or credential before publication.

For a real human clarity test: show About and Bio to three unfamiliar readers and ask (1) What does Nolan make? (2) Which link would you use to verify a concrete example? (3) Do you infer a credential or measured claim not actually present? Record actual responses privately; do not publish an invented survey.
