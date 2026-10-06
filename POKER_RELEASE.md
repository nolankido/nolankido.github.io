# Personal gateway and poker section

The main page is now a stable personal introduction and destination selector. Poker is the primary destination; the existing general Notes collection is secondary. About and shared biographies use the same approved broad identity.

## Published scope

- `/poker/`: an introduction, a hand-review entry point, a private-use worksheet, and a contact path.
- `/poker/reviewing-a-hand/`: a substantive guide with a clearly fictional example and independently checkable pot bookkeeping. No optimal action, solver result, or actual tournament result is asserted.
- `/downloads/poker-hand-review.md`: an editable blank record. No visitor answers are collected.

No unreviewed footage, social profile, real hand, tournament story, results table, travel schedule, or private project has been published. Future stories need approved source material and verified media links. Do not create empty content archives or promise a release date.

## Implementation

Source remains under `_source/`; `pages.json` defines the two new routes. The primary navigation is Poker, Notes, About, Contact. Poker has a small server-rendered local navigation with a clear route back to the main site. Existing article URLs, resource paths, general RSS entries, domain settings, contact code, and the two reviewed stylesheets are preserved. New presentation rules live in `assets/hubs.css`, with content-derived cache versions.

## Verification

Run the committed-build check, dependency-free tests, mocked-contact browser tests, real-page design browser tests, and the full accessibility/reflow audit from README. Browser tests cover the gateway-to-poker-to-guide path and the exact new download bytes. The live verifier includes both poker routes, the new stylesheet, and the review sheet. No real contact submission is part of these tests.

## Editorial direction

The root page is not an activity feed. Add a destination only when it leads to useful content. Poker may grow around approved tournament stories, hand reviews, and study material. A subsite separates subjects, not privacy: all committed files in this repository are public. Keep unpublished footage, source conversations, private drafts, and completed worksheets outside this repository.
