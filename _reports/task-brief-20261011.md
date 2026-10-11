# Practical AI task-brief utility

Baseline: eeff3118e0a57255fcebbc64a48b2a4545c306b2
Purpose: give the Technology entry point something usable, not another general essay.

## Reader experience

`/technology/task-brief/` is a deterministic template builder. Four required fields
cover purpose, material, deliverable and review; a fifth holds optional boundaries.
It does not call an AI system, judge safety, enforce permissions or claim results.
Three illustrative presets cover writing, a shared plan and learning. The preset
text is readable in native disclosures and is the data used by their load buttons.
Replacing existing entries or clearing them requires explicit confirmation.
Editing invalidates an earlier output, preventing accidental export of stale text.

Visitors can copy or save the assembled brief. Clipboard failure selects the
visible text for manual copying. A plain-text blank template is also provided,
with an identical on-page preview and readable examples without JavaScript.
Technology, Resources and Start here link to the tool; metadata search includes it
once at its Technology home. No new homepage section or primary navigation item.

## Privacy and scope

The script makes no network request, storage write, query-string change, clipboard
read, analytics event or AI call. Entries clear on page exit and restored-page
navigation. User-requested clipboard copies and saved files remain on the device.
The page warns about browser/extension handling and the separate policies of any
service where a visitor later pastes the brief. Use placeholders; this is not an
appropriate place to enter confidential records. Existing pageview analytics is
unchanged, not described as disabled. Drafting instructions are not a security
boundary and cannot force another tool to respect permissions or truthfulness.

The script and stylesheet load only on the utility route. All pre-existing article
bodies, feeds, identities, biographies, section-source catalogs, contact/privacy,
analytics configuration, hosting, social images and original CSS remain fixed.
The new reference page is in the sitemap but is not added to the article feeds.
Only affected reviewed visual snapshots and the two script allowlists advance.

## Checks and maintenance

Unit tests validate deterministic output, required fields, every length boundary,
literal hostile text, source/download equality, unique IDs, defined CSS tokens,
route/asset scope, unchanged protected content, and no forbidden network/storage
or HTML-injection sink. Browser checks exercise all presets, validation/focus,
copy success and denied fallback, exact text download, edit invalidation,
confirmation/cancel, clearing, page restoration, reflow and expanded text spacing.
Disabled/blocked JavaScript retains the complete examples and blank template.
Full URL journeys and automated accessibility run in CI before merge; local tests
may use --offline when HTTP browser navigation is unavailable. No real third-party
AI request, visitor contact submission or confidential sample is involved.

References checked for implementation:
https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/writeText
https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API

Edit static fields, examples and the blank template deliberately. The JavaScript
assembler has a pure exported function for independent Node tests. Keep the
readable fallback and file exactly aligned. Run build.py, the complete unit suite,
and task_brief_browser.py, then all existing browser suites. Inspect screenshots
before merge and verify exact production bytes after deployment.
