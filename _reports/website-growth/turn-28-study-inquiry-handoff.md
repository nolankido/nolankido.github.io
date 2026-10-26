# Turn 28: carry explicit study interest into the existing Contact form

Prepared October 26, 2026, Pacific/Honolulu. Parent release: `7c8185b2660453e797f18dec2f3862aa1521f298`, completed Turn 27.

## Problem and scope

Turn 27 published a voluntary research-interest invitation under `/start-here/`. It linked to the existing contact form, but visitors had to remember and manually type the fixed words "Website usability study" in their message to distinguish research inquiries from ordinary correspondence.

This is an observable additional instruction and manual classification step, **not evidence that any visitors were confused, abandoned the form, or agreed to participate**. The pending NK-UTILITY-01 study (#123) still has no human observations. The existing contact page already carries name, email and message fields, optional context and topic fields, Cloudflare Turnstile, and Formspark delivery with the published privacy notice.

## Improvement

The authored Start Here link now targets `/contact/#study-inquiry`. On Contact, the script recognizes **only that exact fixed fragment**, checks that the optional context and required message remain blank, then places **Website usability study** in the existing optional context input. This topic can be changed or removed. The required message remains empty; no personal details, past tool entries or form values are moved into it. Nothing is sent before explicit form validation, anti-spam verification and the existing Send message action.

A notice appears near the fields only in the eligible anchored state. It says an inquiry is not research consent, enrolment, or recording approval, and explains that notes, withdrawal and deletion arrangements must be discussed separately before any session. It warns against sharing worksheets or sensitive data. Normal Contact, all six anchored corrections, malformed fragment strings, and existing-draft restoration remain untouched.

When JavaScript is unavailable, Start Here still explains the fixed topic, Contact still displays its original anti-spam requirement, and no auto-filled data or submission is implied.

## Files and security boundary

Exactly five production paths change: Start Here source and generated page, Contact source and generated page, and `assets/contact.js`. There are no new fields, destinations, transport requests, cookies, storage, analytics, forms, accounts, JavaScript dependencies, provider contracts, paid services or GitHub workflows. The generated Contact script cache token tracks the new exact asset bytes.

## Verification

- A test-only SHA256-gated predecessor restores only the five exact published parent files, validates the original hashes, and leaves unknown edits visible. It is chained ahead of earlier study-interest and correction-history adapters without rewriting baselines.
- Static source/output tests protect the new authored fragment, editable fields, privacy wording and unchanged form control inventory.
- The existing full-browser contact fixture gains cases for the exact anchor, malformed fragment refusal, draft restoration, keyboard edits at four widths, no auto-send, and controlled explicit mock submissions with the user's final edited context.
- The Start Here browser journey checks both JavaScript modes at 320/390/768/1440px. In script-enabled mode the context is prefilled and the message blank; disabled mode leaves the context blank and form disabled.

The complete hosted build, 194-page HTML/search checks, all five browser groups, automated review, merge, Pages deployment and independent public-file verification are release gates. Passing tests will **not** mean any participant was recruited or observed, and the user-study issue must remain open.
