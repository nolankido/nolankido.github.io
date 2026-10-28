# Turn 35: carry the task brief into an independent answer check

Prepared October 27, 2026, Pacific/Honolulu.

## Purpose

The operating map's F1 outcome is a usable task brief with an independent check.
Its specified next action is the existing AI answer-checking guide. The Task
Brief Builder already provided six examples, assembly, copy, download, print,
and a native blank template, but did not link to that guide. Its other outgoing
links address judgment, general tool trust and whether a workflow helped.

This turn follows the published ranking-practice release at commit
`427f258ad895cfc736d3d29944347ea584f04826`, tree
`f51ffdb98ccb618896e25d6d729cc7919536a92d`.

## Reader improvement

The existing Task Brief page gains one native three-step handoff:

1. Keep the assembled brief, or a privately completed blank template, before
   leaving. Confirm the download saved or copy its complete text into a note.
2. Choose a relevant independent check in the existing answer-checking guide
   and add it to the saved brief under CHECK BEFORE USING.
3. Apply the check when an answer arrives, then use the guide's existing review
   record to retain the evidence, unresolved points and the decision to use,
   revise or pause the result.

An opening jump and a link beside the assembled result reach the handoff on the
same page. Readers can inspect it before taking the outbound link. The warning
that leaving clears the builder's entries precedes that outbound link. Editing
the saved copy is explicit. Choosing a check is not evidence that a later answer
passed it, and the builder still runs no AI.

## Bounded implementation

The five production paths are `_source/technology/task-brief.html`,
`_source/pages.json`, `technology/task-brief/index.html`, `find/index.html` and
`sitemap.xml`. The Task Brief record's existing updated date advances from
October 21 to October 27. No publication date or new metadata field is invented.

All six examples, original fields, fixed working instructions, controls,
downloads and existing destinations are preserved. The answer-checking guide
is unchanged. There is no new runtime script, stylesheet, account, storage,
tracking, form, model request or public route. The existing pagehide and
persisted-pageshow clearing behavior remains intact.

## Review and release qualification

Independent editorial review found no must-fix issue in the source: the saved
copy and later answer are distinguished, the save-first instruction is adjacent
to the handoff, and the short section reuses the existing checking method.

The Task Brief browser suite is extended to check the actual saved-brief journey,
same-page draft retention, native guide arrival, the original clearing behavior,
script-free access to the unchanged blank file, keyboard use, narrow layouts,
text spacing and print scope. Original checks remain in place.

A test-only predecessor boundary binds the five complete files to the genuine
published parent. It checks exact current bytes, reverse spans and complete
restored parent hashes, and leaves unknown changes visible. Earlier historical
hashes, records and counts remain unchanged; current discovery is checked
separately.

The complete hosted unit suite, all five browser groups and the aggregate check
must pass on the final candidate before merge. The merged tree must match the
tested tree, then Pages and the exact published-response check must identify the
merged release. Final receipts belong in the PR. This preparation record alone
does not establish that those gates passed.

Actual reader comprehension, successful use of a resulting answer, time savings
and traffic changes remain unmeasured. This turn supplies a usable next step,
not an observed outcome.
