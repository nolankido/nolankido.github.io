# Turn 26: complete the printable practical-AI exercises

Prepared October 26, 2026 (Pacific/Honolulu). This is a bounded engineering improvement, independent of the still-unconducted visitor study in issue #123.

## Reproduced gap

The AI Summary Review page keeps six claim-level findings, an optional comparison prompt and the exact blank checklist in eight closed native details. Its page-specific stylesheet had no print rules. The 'Should I Use AI?' task guide kept its private blank decision worksheet in another closed details. Its print stylesheet only tried to make a child pre visible, leaving Chromium's details-content computed visibility hidden.

A focused Chromium print-media fixture confirmed that with a closed details element, the screen and print content-visibility is hidden until print CSS explicitly sets details-content to visible. This is a page-print defect, not evidence of incorrect source-checking guidance or human success.

## Repair

- Both page-scoped stylesheets reveal native details-content only while printing. On-screen disclosures continue to start closed with the existing keyboard interaction.
- Preserve all six finding headings and optional prompt, and render both complete downloaded blank templates as wrapping, paginated text on a white paper background.
- Hide only screen-specific jump/download actions from print. Printed headings have no disclosure marker.
- Update the two generated pages' CSS content hashes. No source article prose, JavaScript, worksheet download, feed, sitemap, metadata, form, storage, tracking, external request or analytics changes.

## Tests

- summary_review_browser.py checks all eight initially closed panels in print, exact checklist content, screen state restoration and overflow at 320/390/768/1440px with JavaScript enabled and disabled. Creates one A4 PDF smoke specimen.
- ai_task_choice_browser.py tests print visibility and exact worksheet text at the same four widths, with separate blocked-script and JavaScript-disabled fallbacks, plus an A4 PDF specimen.
- test_practical_ai_print.py checks exact original downloadable worksheet text, six answers, CSS scoping, content-addressed cache references, immutable full-file predecessors, idempotence and unknown-file/corrupt-record refusal.
- practical_ai_print_history.py preserves the exact four predecessor files from release 17794dbd423e80215a7c17f50e6606785e8064ba. The existing test-only history chains call this before their older baselines without refreshing those historical digests.

## Evidence boundary

Full hosted build, browser suite, review, merge, Pages deployment and independent live-file verification remain separate release gates. Do not claim them until passed. The study in issue #123 has zero observed participants. No new search-traffic or conversion measurements were available or invented, and no API subscription was purchased.
