# Turn 12: retain unresolved accessibility evidence

Status: candidate, not a claim that the website has passed a full accessibility audit.

Published predecessor: `60f50b8f77ead395b3591d8f51626703c97e6ce5`.
Study reference: issue #123, NK-UTILITY-01. There are still no recorded human task observations or fresh authenticated traffic figures.

## Reproduced gap

The released `weekly-reset-browser.json` reports functional status `pass`, two automated accessibility scans, no violations, and an incomplete `color-contrast` rule at 1440 pixels. The Python wrapper retained only width and rule ID. It discarded the affected node selectors, check IDs and related selectors, so the artifact alone could not identify the manual review target.

This is an evidence-reporting problem, not proof that page colors fail. Keep the functional status separate from accessibility coverage. A missing optional axe engine must be `not_run`, not an empty list interpreted as approval. A scan exception must remain `scan_failed` even if other checks succeeded earlier.

## Narrow change

Only `_tests` and this report change. The shared standard-library helper projects both incomplete findings and violations onto an explicit allowlist. It retains the configured route, viewport width, script mode, exact scan scope, rule IDs, node selector paths and related check targets. Nested frame/shadow selectors are preserved without mutating the source result. HTML, element text, arbitrary check data, free-form messages and remote URLs are not copied. Selectors are diagnostic data and may themselves contain identifiers; these fixtures must never use confidential participant input.

The Weekly Reset wrapper now writes a separate `accessibility_status`: `not_run`, `scan_failed`, `violations_found`, `manual_review_required`, or `no_automated_findings`. None is a conformance certificate. Incomplete rules stay pending and do not become passes merely because no automated violation was raised. Functional failures still fail the browser job; their partial diagnostic JSON is saved before re-raising.

No existing layout, keyboard, script-disabled, download, print, privacy or error assertion is removed. Axe still scans only `.lw-quick-start` in this helper at 390 and 1440 pixels with JavaScript enabled; this work does not expand that scan into a full-page claim. The rest of the existing browser suite is unchanged.

## Preliminary diagnostic, not acceptance

The exact Pages artifact for the predecessor was retrieved and its ZIP digest verified against GitHub: `afcdaba0ab7f16fd4f4d867166d8e61bf47d34c61fa5ddf935d840ed1c096e0b`. An offline rendering of the six flagship resources plus Start Here, Resources and Find found no low-contrast candidates among their visible DOM text under a simple ancestor-background calculation. The renderer inlined the artifact's styles and fonts in memory and blocked network requests. This approximation does not handle every overlap, clipping, pseudo-element or painted background and does not resolve the axe incomplete item. No live navigation or human task outcome is inferred from it.

The connected browser and authenticated analytics remain unavailable in this session. Local HTTP browser navigation is blocked by administrator policy. No paid automation or new subscription was purchased. Existing hosted browser checks must supply final integration evidence.

## Qualification and next step

Twenty-one synthetic helper tests cover result scope, selectors, related nodes, immutability, redaction boundaries, no-scan state, unresolved state, violation precedence and malformed-result rejection. Run them with:

```text
python -m unittest discover -s _tests -p 'test_accessibility_evidence.py' -v
```

Before merge: run the complete unchanged Site checks workflow, confirm all five browser groups, inspect the richer final-head Weekly Reset artifact, and resolve any code-review finding. All production files, published baseline records and existing workflows must remain byte-identical to the predecessor. This is test-only work, not a new public feature.

After the artifact identifies the exact unresolved element, assess that element with its actual colors and background at the recorded state. Only a demonstrated problem should trigger a design change. Continue the separately consented visitor study and obtain an authenticated search export when available; do not replace those evidence classes with this diagnostic.

Reference: W3C, Understanding WCAG 2.2 SC 1.4.3, https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html . Use specified foreground/background values, applicable 4.5:1 or 3:1 thresholds, and do not round a sub-threshold ratio up to a pass.

## Failure-path review correction

Review identified that the newly saved failure report would still contain raw axe violation objects even though incomplete items were redacted. Both arrays now use the same explicit projection before they can reach JSON or stdout. The helper keeps rule IDs, impacts, selector paths and check IDs for failed findings while excluding their HTML, free-form messages and data. Five added synthetic tests cover failure redaction, immutability, empty failures, malformed node refusal and mixed unresolved/failed results. A violation still fails the browser job. The correction does not claim that a violation was observed on the actual website.
