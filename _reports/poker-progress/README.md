# Poker Foundations: private progress on the Study Desk

Prepared October 16, 2026 UTC against published PR #105, commit
`ca0264c251f2c999a8375d9e748521fe46ef22fe`.

**Status at handoff:** implementation and focused preservation checks are
complete. The new progress browser suite passed in 78.0 seconds. The full
744-test unit run, 57-suite hosted browser gate and deployment verification
remain required. Final check and deployment receipts belong in the pull request.

## Purpose and visitor behavior

This implements the recovered roadmap's cycle 5 recommendation for private
learning progress: resume after refresh, export, import and reset without an
account. The recommendation is a product direction, not evidence of learner
outcomes. Qualified teaching review and actual beginner observation remain
separate, unfinished work.

The companion lives at `/poker/study/#course-progress`. Its six lessons come from
the canonical Poker Foundations course. Each has a manual **Not started**,
**Working on it**, **Practiced** or **Revisit** note. A next-task selector offers
the six reading destinations, their six existing checkpoint practice situations,
the course map and the complete checkpoint. A prominent link resumes that task;
a short list collects lessons marked Revisit. Reading or answering an exercise
does not change a note. These are self-reported marks, with no score or completion
claim.

Lesson and practice links open in a new tab with visible and accessible notice,
keeping a temporary desk record open. Native lesson links and the complete blank
TXT study card remain usable without JavaScript. Storage and transfer tools sit
inside native disclosures, while the next task and lesson controls remain easy
to reach.

## Saving, transfer and privacy contract

**Remember on this device** starts off. Until the visitor enables it, the tool
makes no storage writes. Enabling it saves the record and subsequent manual
changes under one key, `nolan-kido:poker-foundations:progress:v1`, in this browser
profile. Loading an existing valid saved record restores the prior opt-in without
a startup write. Anyone using that profile can see its saved marks.

**Remove saved copy** turns saving off and retains the open-page marks.
**Reset marks and stop saving** immediately clears those marks and the chosen
next task as well. Both actions touch only this tool's storage entry. Browser
data can be unavailable or cleared; a progress file provides a portable copy.

**Download progress file** exports `poker-foundations-progress.json`. A read-only
field exposes the complete same text, with an explicit select button for the
device's Copy command. File import and pasted-text import validate first, show
all six marks and the next task, then require **Replace the current record**.
Cancel leaves the current record intact. Import does not enable saving. If the
visitor already enabled saving, the preview states that replacement will update
that saved copy too.

The record has exactly six top-level fields: `format`, `version`, `course`,
`revision`, `next` and `lessons`. It uses format `nolan-kido-poker-progress`,
version `1`, course `poker-foundations`, exactly six allowlisted lesson IDs, four
status values and 14 destination tokens. Imports are limited to 8,192 UTF-8
bytes. Extra fields, unknown lessons or states, unsupported versions, different
course revisions and arbitrary destination values are rejected. The schema
contains no saving preference, names, free text, answers, hand histories,
timestamps or arbitrary URLs.

The course revision is a SHA-256 digest of canonical course, short-lesson and
final-hand data; the six lesson sources and checkpoint source; and the three
instructional renderers `poker_course.py`, `poker_lessons.py` and
`poker_final_hands.py`. A changed digest prevents silent reuse of marks against
different material. Even an operating-copy change in a renderer can require a
new record. This is conservative compatibility metadata, not a teaching review
or an automatic migration.

All imports are read within the browser. The companion adds no upload, network
request, account, progress analytics, automatic visit tracking or answer
tracking. Existing pageview analytics remain described in the revised privacy
notice. Workbook and course operating notices now distinguish optional manual
marks from exercise answers, which the site still does not receive or save.

## Recovery and accessibility

Storage access, read, write and removal failures leave the open-page record
usable. A failed autosave turns Remember off and reports that an earlier saved
copy may remain. Failed deletion is reported as unconfirmed, with a retry
control; it does not claim that browser data was removed. Corrupt or incompatible
stored records are left untouched and are not silently loaded or replaced.

Before autosaving, the controller compares the current stored value with the
value it expects. A stale tab therefore checks for clearing before writing old
marks back, even if its storage event has been held. Cross-tab clearing resets
tabs that were using the saved record and disables their saving. Tabs with
Remember off retain their independent temporary marks and next task when another
tab creates or removes a saved record. A returning browser-cached page checks
storage again and follows the same distinction. These safeguards use
localStorage events and comparisons, with no additional keys or cross-device
synchronization.

Import request and record revisions invalidate pending reads or previews after
edits, reset, saving changes, other-tab changes and page departure. Rejected or
late file reads cannot overwrite newer marks. Edited paste text requires another
review. If invalidation hides the focused preview, focus returns to its visible
source control; focus elsewhere is preserved. A canceled import no longer leaves
stale reading or review feedback after returning to the page.

Download replacement removes the old link and releases its object URL. Missing
or throwing Blob and object-URL APIs leave the complete selectable export
available. A download activation is described as a request, not proof of a saved
file. The implementation uses no clipboard API.

Controls have native labels, polite status announcements, visible focus and
44 px targets. Lesson and revisit links remain native. The layout reflows to one
column on narrow screens. Print keeps lesson links, the chosen next destination
and readable marks while hiding editing and transfer controls. Browser checks
cover these interactions, but do not certify every browser or assistive
technology.

## Bounded change and historical evidence

The production capture declares ten edited source/asset paths, three new
production files and 13 derived outputs. The blank TXT card is counted in both
the source/asset and output sets. Including the workflow edit, the union is
23 existing changed paths, plus the three new files. Tests, reports, review
packet files and history adapters are tracked separately. The exact sets are in
[capture_history.py](capture_history.py) and
[`poker-progress-change.json`](../../_tests/poker-progress-change.json).

The new generator, controller and stylesheet are scoped to the Study Desk.
Other production edits integrate the build, native return links, two page
metadata records, privacy and workbook operating notices, and live verification.
The Study Desk date also updates its existing search-entrypoints metadata override.
Derived changes include the Study Desk, privacy page, six lesson pages, course
overview, two search pages, sitemap and blank study card.

The baseline preserves fingerprints for the predecessor's 480 source/assets and
221 outputs. The adapter reconstructs that predecessor only for exact reviewed
SHA-256 matches. Unknown mutations pass through and remain visible to tests;
new files are excluded from historical views only when their bytes match the
declared hashes. Previous baselines, change records and frozen search-result
reports are not rewritten.
Old and new public metadata records are paired using the exact parent's scripts
and sources in a temporary directory, preserving their normal transformations.

The current [search-results.json](search-results.json) still has 284 entries and
30/30 declared targets in the first three results. All recorded results,
scores, section destinations and excerpts match the prior study-list release;
only the index SHA changes. The queries and relevance judgments are authored
engineering regressions, not observations of beginner search success.

Of the teaching packet's 14 scoped inputs, 13 are byte-identical to the
predecessor. The sole change is the workbook operating/privacy notice in
`poker_course.py`. Instructional examples, answers and their explanations remain
unchanged. The packet is rebound to actual material commit
`8505785a02c2565e3dd97215f8ce7dc63aa6db43`, with all 18 review slots still
**unreviewed** and the same 28 mechanical evidence cases. Packet regeneration
does not supply a human signoff. Actual beginner sessions remain pending.

## Verification and reproduction

Completed locally at this handoff: six new preservation tests; a drift-free
check of 221 generated outputs; HTML5 and search-metadata checks for 193 HTML
pages; search-result parity; and JavaScript syntax checking. The complete
744-test unit run and all 57 hosted browser suites remain release gates. The
new browser suite passed: two layouts, all 14 native destinations, 24 invalid
imports, one full import flow, nine storage scenarios, six cross-tab scenarios,
six file/preview races, eight download failures and two script-free modes.
It exercised real JSON downloads, imports and storage, plus explicit failure
injection. No page errors, extra action requests, cookies or unintended storage
writes were observed. Mobile and desktop screenshots were inspected.

The cross-tab coverage includes real removal events from both the saved-copy
control and `localStorage.clear()`. Unsaved tabs preserve all six marks, their
next task, export and pasted import text, remain temporary, and do not recreate
a removed record. Tabs using the saved record still clear as intended.

Run from the repository root with the test dependencies and Playwright Chromium
installed:

```sh
python _scripts/build.py --check
python _tests/check_html5.py
python _scripts/check_search.py
node --check assets/poker-progress.js
python -m unittest discover -s _tests -p 'test_poker_progress.py' -v
python _reports/poker-teaching-review/build_packet.py
python _reports/poker-search-intent/evaluate.py --study-list-release
python _reports/poker-search-intent/evaluate.py
python _tests/poker_progress_browser.py
python -m unittest discover -s _tests -p 'test_*.py' -v
```

The browser script starts its own local server. `CHROMIUM_PATH` can point to an
existing Chromium executable, and `SCREENSHOT_DIR` can retain previews.
`.github/workflows/site-checks.yml` defines the full 57-suite matrix and its
required aggregate `checks` result. After an intentional production edit,
rebuild, run this folder's `capture_history.py`, write the current search report
with the evaluator's `--write` flag, and inspect the bounded delta before
repeating verification. Capture rejects unexpected production changes and a
changed frozen baseline.

Record final release evidence in the pull request: exact submitted-head checks,
merge commit, successful GitHub Pages deployment, and the independent published
byte check for all 472 declared targets. Its `LIVE_VERIFIED_COMMIT` must name the
actual deployed main commit. Live verification can be reproduced after
deployment with `python _scripts/check_live.py --attempts 10 --interval 10`.
No deployment success is claimed by this preparation report.
