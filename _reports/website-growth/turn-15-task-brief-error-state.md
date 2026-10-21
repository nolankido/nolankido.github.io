# Turn 15: clear an obsolete Task Brief field description

Status: candidate; full hosted release qualification and deployment are separate.
Published predecessor: `82c0a82df9969c2255e3c3ebbaacf290faeef78e`.

## Reproduced reader-facing problem

Assemble an empty brief, then enter a nonblank purpose. The existing input handler hides the warning and removes `aria-invalid`, but leaves its text in the element referenced by `aria-describedby`. An explicitly referenced hidden element still contributes to the accessible description.

An offline Chromium 144 AX-tree inspection using the exact published script blob `1495745ef9d68036c51ef275b0f226c1dc1ea5ba` returned the following description after typing a fictional purpose:

> Name one useful outcome and who it is for. Maximum 600 characters. Add a short answer to this required field.

The field had a value, its visible error was hidden, and `aria-invalid` was absent. This is a reproducible application-state inconsistency, not a finding attributed to a participant or a measured screen-reader user session. The study in #123 remains unconducted.

## Minimal repair and preserved behavior

One line clears the edited field's error text before hiding it. The generated page changes only its task-brief script content-version token. The corrected AX description contains the existing help text without the obsolete warning. Untouched invalid fields retain their own warnings; a later Assemble still validates blank, whitespace-only and oversized values.

No validation rule, character limit, required-field rule, template text, assembled output, example, worksheet, publication date, correction link, copy/download behavior, storage or network behavior changes. The previously released public-page feedback handoff remains intact. This is not a whole-site accessibility certification.

## Evidence and qualification

Local before/after inspection used the browser's accessibility tree and a matching accessible-description assertion, with network access blocked. The published script exposes the stale warning; the candidate does not. The existing offline Task Brief suite passes 19 functional checks, 15 layouts and 15 text-spacing checks, plus six newly added error-description transitions. It performs no HTTP journeys or axe scan in that local mode. Hosted runs remain required for those existing checks.

Eight focused unit contracts cover the exact one-line script delta, sole generated cache-token delta, unchanged assembly/validation, the complete 714-path production inventory, byte/string predecessor restoration, unknown mutation detection and corrupt history refusal. The new whole-file-hash adapter runs before the existing feedback predecessor. Two older test modules explicitly inspect their historical version before testing the old contract; none of their frozen hashes or baseline records were rewritten.

The exact current source was transferred through an isolated read-only maintenance export, bound to commit `82c0a82d` and tree `01a2456802afc4594015d57f0319406c2564fa26`. ZIP SHA256: `36a27a7313e9c95854e8e65c96fd394b101fc2c6bc47a3e922a2d0d64d25a046`. The maintenance export/preparation workflows and transport files must remain outside the candidate tree.

Require the complete final-head Site checks, all five browser groups, aggregate gate and completed code review before merge. After merge, verify the released tree, Pages deployment and actual public responses. No real message, private brief, participant record, search metric or indexing claim is part of this change.

References checked October 21, 2026:
- https://www.w3.org/TR/accname-1.1/ , sections 4.2 and 4.3: referenced hidden descriptions remain meaningful.
- https://playwright.dev/python/docs/api/class-locatorassertions#locator-assertions-to-have-accessible-description : computed-description assertions.
