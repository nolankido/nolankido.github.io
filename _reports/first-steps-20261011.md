# Useful first steps and Creative Work

## Purpose
Keep Nolan's personal introduction and selected writing ahead of the four
interests. Let visitors use a small piece of the site without first navigating
a subject library. Give Creative Work a practical starting point without
publishing private projects or implying a finished video portfolio.

## Changes
- Each existing home destination is a labelled article with two separate native
  links: explore the subject or take one useful first step. No nested links,
  click handlers, whole-card overlay or new subject category.
- The first steps lead to the AI task-brief tool, the private weekly-reset sheet,
  after-play poker study calculators and a new Creative planning brief.
- Creative Work now opens with the blank brief and three labelled making routes:
  a small written piece, a poker-specific video workflow, and a family story.
  Existing selected essays, URLs and section anchors are retained.
- The complete plain-text brief is the source of its escaped on-page preview.
  There is no new form, storage, JavaScript, AI request, signup or event tracking.
- Resources and the generated metadata finder expose the Creative brief.
  Nothing is added to article feeds or represented as a new personal result.
- Page-scoped CSS retains the original styles, typography tokens and navigation.
  It includes native focus states, 44-pixel minimum home link heights and wrapping
  for expanded template text.

## Preservation
The source identity, biography, approved About page, original essays, both large
subject-source collections, contact, privacy, analytics, base design, social
images, saved contact and hosting are unchanged. Existing independent hash
fixtures continue to protect these boundaries. The legacy compound homepage
digest is updated only after reviewing the intentional home/Creative/Resources
changes. The two changed generated-page hashes in the older viewer fixture are
updated as well; its other protections and newer independent fixtures stay intact.

## Release checks
Run `python _scripts/build.py --check` and the full unit/content suite.
`_tests/first_steps_browser.py` checks the actual local HTTP routes with and
without page JavaScript, native keyboard journeys, exact text downloads,
six widths, expanded text spacing and optional axe scans. The complete existing
browser suite remains in Site checks. CI saves first-step previews separately.

The release verifier includes exact public bytes for the new CSS and text file.
Build/test success alone is not a deployment claim. Confirm the final Pages
deployment and the main-commit public-byte check separately.

The initial browser harness timed out when Playwright's style-insertion helper
waited for a load event in a JavaScript-disabled context. A minimal local probe
reproduced the wait. The harness now inserts its test-only text-spacing CSS
synchronously in both contexts and has progress logs plus a bounded diagnostic
timeout. Site JavaScript stays disabled throughout the no-script checks.
The two updated pages use immediate native anchor movement, avoiding unreliable
smooth-scroll settling in the no-script paths. The browser assertions require
the destination to be inside the viewport and below the sticky header, not just
below it somewhere offscreen.

## Limits
No actual message, AI-service request, private worksheet answer, at-table poker
assistance, measured personal result or reader-conversion claim is involved.
The new sheet is a planning aid, not a permission or factual-verification system.
Automated accessibility checks are not certification. Font loading is unchanged;
local static previews use fallback fonts, while CI exercises the HTTP pages.
