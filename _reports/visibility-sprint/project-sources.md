# Public project case sources

Prepared for the website visibility sprint. This record documents the sources used for the two new articles, rather than a new test of either application. Only public project material was read. No private customer records, manuscripts, credentials, operator feedback, or unpublished project outcomes were added.

## Source snapshots

| Project | Public repository | Commit inspected |
| --- | --- | --- |
| Review Reply Writer | https://github.com/nolankido/reviewReplyWriter | `1c5e0487c331d5202410c9f342557d9355951c3a` |
| Preflight / canonkeeper | https://github.com/nolankido/canonKeeper | `947e9c3d7dbc9bfa719579ca1e697d4479567684` |

Both commits were the public default-branch heads returned by shallow public clones during this work. Article evidence links use those commits so a later repository update does not silently change the cited source. The public repository and hosted-example links remain convenient current entry points.

## Review Reply Writer

Article: `_source/technology/local-ai-review-replies.html`

### Primary records inspected

- `README.md`: application purpose, Python requirement, local setup, template and model modes, saved-text approval, manual posting, current evidence limits.
- `web/app.js`: exact fictional Duplicate billing example. The article's quotation matches this source.
- `web/index.html`: actual control labels and saved-text review/approval explanation.
- `docs/OWNER_FIRST_WORKFLOW.md`: source and policy beside the editor, reapproval after editing, workflow evidence and explicit runtime limits.
- `docs/REVIEW_EVIDENCE_PASS.md`: material detail handling, exact source excerpts, interpretation limits, retained fixture evidence.
- `docs/LOCAL_SETUP.md`: launcher commands, Python 3.10+, separate Gemma setup, explicit model verification and privacy scope.
- `examples/evaluation/live-smoke-2026-10-13.json`: the actual rejected `should have addressed` candidate and accepted `extended wait` retry.
- `examples/evaluation/live-quality-smoke-2026-10-13.json`: the later retained three-case actual-model run.
- `docs/QUALITY_RESULTS.md` and `docs/REPLY_QUALITY_RESULTS.md`: interpretation of those historical results and why they are not current-source model or human-quality evidence.
- `examples/evaluation/source-evidence-template-2026-10-14.json`: retained template evidence, explicitly separate from model output.
- Public DEV article: https://dev.to/kidon/the-model-writes-the-review-reply-the-owner-keeps-the-promises-57a2 . Read through web retrieval, including the October 13 Hawaii historical-demo date and 68-second description.
- Public demonstration destination: https://share.descript.com/view/n1ZTnZpfNyB . The accessible page identifies a historical Gemma demo. Web extraction returns the JavaScript shell, so playback was not independently reverified for this website article. The article's description is attributed to the published project record.

### Deliberate boundaries

- The duplicate-billing review is fictional, not customer correspondence.
- The historical model records are not renamed as current validation, and no model acceptance percentage is inferred from three examples.
- No actual owner assessment, adoption, revenue, comparative time saving, or approval of the article's wording is claimed.
- No screenshot was invented. No committed project screenshots were present in the inspected repository; the article links to the existing historical demonstration and uses a readable source example.
- The setup command is the documented launcher, not a claim that installation was executed in this sprint.
- No current Gemma inference, operator trial, model download, public post, or review-platform action was performed.

## Preflight / canonkeeper

Article: `_source/technology/ai-book-continuity-checker.html`

### Primary records inspected

- `README.md`: project identity, sample entry points, extraction/comparison/judgment stages, source snapshot's recorded Holmes findings, public-demo and sandbox boundaries.
- `docs/ENGINE.md`: documented engine and provider choices. The article links here for details rather than reproducing prices or current model availability.
- `src/canonkeeper/preflight/samples/sherlock-holmes-report.html`: saved public report with wound and landlady findings.
- `src/canonkeeper/preflight/samples/sherlock-holmes-reviews.json`: two stored wrong-call explanations: Holmes's disguise and Mrs. Barclay's maiden name.
- `evals/results/holmes-seed0-2026-10-27/README.md`: seeded protocol, changes to matching rules, missing bible required for regenerating the per-stage table, and benchmark-quality limitations.
- `evals/results/holmes-seed0-2026-10-27/result.raw.md`: original same-run score, 7 true positives, 4 false positives, 13 false negatives; precision 0.64, recall 0.35.
- `evals/results/holmes-seed0-2026-10-27/result.md`: rescored output, 8 true positives, 2 false positives, 12 false negatives; precision 0.80, recall 0.40. One other finding is counted as neither a hit nor a false positive. Eight recorded misses are attributed to extraction and four to judgment.
- `LICENSE`: MIT license, copyright 2026 Nolan Kido.

### Actual image provenance

| Local website asset | Original source at pinned commit | Dimensions | SHA-256 |
| --- | --- | --- | --- |
| `assets/projects/preflight-holmes-report.png` | `docs/img/report.png` | 1200 x 1349 | `cee1a9bd2ff1cc2140c440660f0314763bf33fd0b56bfca9258d050fd882bb28` |

The image was visually inspected with the image viewer and copied byte for byte. It shows an archived report and its then-visible counters. The caption identifies the screenshot as archived and explains that its $0.15 figure covers judging rather than the full extraction-and-judging cost. The article does not equate the screenshot's counters with current correctness.

The public `docs/gallery/01-report.png` and `docs/img/bible-by-book.png` were also inspected. The gallery graphic was not selected because its promotional text says the tool finds every contradiction, which the retained benchmark does not support. The by-book screenshot was not selected because its visible birthplace row contains an extraction interpretation that requires additional context.

The original MIT notice is retained at `assets/projects/preflight-LICENSE.txt`.

### Deliberate boundaries

- The Holmes sample is an actual recorded audit of public-domain books. The benchmark is a separate run over text containing planted changes.
- The original and rescored benchmark rows describe the same output. They are not represented as a model improvement or a paired before-and-after experiment.
- The article acknowledges ambiguous plants, source-fact mistakes, missed detections, and incorrect findings.
- No current hosting availability, paying customers, comprehensive accuracy, author time saving, live purchase, or new local-model result is claimed.
- Hosted demo links are provided to existing public examples. No private manuscript, checkout, payment, model audit, or author trial was submitted.

## New website files

- `_source/technology/local-ai-review-replies.html`
- `_source/technology/ai-book-continuity-checker.html`
- `assets/projects/preflight-holmes-report.png`
- `assets/projects/preflight-LICENSE.txt`
- `_reports/visibility-sprint/project-sources.md`

## Source-level checks

- Review Reply Writer source: 916 rendered-text words, six unique section IDs, all local jump anchors resolve, no em dashes.
- Preflight source: 942 rendered-text words, six unique section IDs, all local jump anchors resolve, no em dashes.
- Exact fictional review wording checked against the pinned JavaScript example.
- Benchmark numbers checked against both pinned result files.
- Image hash matches the original public file.
- Both complete source fragments parsed with `lxml.html.HTMLParser(recover=False)` without parser errors.
- Every pinned GitHub file link in the articles was checked against its inspected local source tree and required to use the stated commit.
- No build, commit, push, model run, or checkout action was performed by the article authoring task. Manifest, shared CSS, generated output, browser QA, and release verification belong to the integrating task.

## Integration notes

Both sources follow the existing `section folio-row`, `section-meta`, and `section-content prose` structure. They use `entry-jumps`, `evidence-facts`, `evidence-note`, and `editorial-note`. Preflight uses the existing responsive `work-preview` figure pattern from `assets/practical-discovery.css` and a `project-table-scroll` region around its small results table; the integrating task should provide the applicable responsive table styling.

Suggested manifest metadata, with publication dates assigned explicitly by the integrating task:

```json
[
  {
    "id": "local-ai-review-replies",
    "section": "technology",
    "path": "/technology/local-ai-review-replies/",
    "title": "Using local AI to draft customer review replies.",
    "seo_title": "Local AI Review Replies: Gemma Project Case | Nolan Kido",
    "description": "Inspect Nolan Kido's Review Reply Writer: local Gemma drafts, customer-source checks, owner approval, and a documented model failure with its retained evidence.",
    "kicker": "Technology / Public project case",
    "source": "technology/local-ai-review-replies.html",
    "evidence_article": true
  },
  {
    "id": "ai-book-continuity-checker",
    "section": "technology",
    "path": "/technology/ai-book-continuity-checker/",
    "title": "Checking a book series for continuity errors with AI.",
    "seo_title": "AI Book Continuity Checker: Preflight Case | Nolan Kido",
    "description": "Explore Nolan Kido's Preflight continuity checker through a Sherlock Holmes audit, source passages, real project screenshots, and a benchmark with its misses visible.",
    "kicker": "Technology / Public project case",
    "source": "technology/ai-book-continuity-checker.html",
    "evidence_article": true
  }
]
```
