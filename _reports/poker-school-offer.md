# Poker School: offer and course-interest workflow

**Status: proposal (October 16, 2026).** This document does not authorize a paid launch or claim learning outcomes.

## Target learner and product boundary
Adults new to no-limit Texas Hold'em, including people who know hand rankings but cannot reliably follow an entire hand. The goal is to follow the table, track action and chips, explain basic options and uncertainty, prepare responsibly for an in-person game, and reflect away from play. No solver training, gambling coaching, expected profits or expert credentials are implied.

**Poker Foundations remains free:** six lessons, checkpoint, practice and study tools, without email gate.

**Possible paid guided course:** short original narrated walkthroughs, connected illustrative hands, independent changed-situation attempts, corrective explanation and printable worksheets. Five provisional stages are published at /poker/school/. Course dates, price, scope, commercial terms and any coaching are undecided. There is no payment or enrollment.

Before using reviewed practice as premium teaching, the exact content requires qualified human teaching review and real beginner observation. The 72-case bank remains an AI-authored, mechanically checked draft.

## Entry points
The Poker homepage points toward the possible course after the free course introduction. An optional link from the Study Desk does not interrupt learning. The frozen Poker Foundations source is unchanged to preserve its reviewed teaching scope. The School page visibly differentiates free from possible paid content.

## Request form and privacy
The existing Formspark destination and Cloudflare Turnstile are reused. The course-interest form uses a separate, page-scoped `assets/poker-school-interest.js`. The original `assets/contact.js` stays byte-identical to the approved parent, as do the original privacy page and frozen Poker Foundations teaching source. The School page carries explicit supplemental request terms and links to the existing general privacy notice.

- Required email and action, `register` or `remove`.
- Register requires an explicit initially unchecked consent box.
- Name and a broad course-interest category are optional.
- Remove requires only an email and does not require consent or an interest category.
- All requests are sent to Formspark with the fixed intended purpose and action. There is no automatic mailing-list enrollment, removal, customer account, payment, or email automation.
- A 2xx response from Formspark reports only provider acceptance. It does not prove that an address was added, removed, or read by a person.
- Unsuccessful requests remain visible for correction and retry. No form values are stored locally or sent as Umami events or URL parameters.

### Operator procedure
1. Review Formspark requests in the existing private account. Never commit addresses, form responses or other personal data to GitHub.
2. For register, check explicit consent and record source, address and consent date in an access-controlled operator record. Prefer email reconfirmation before any marketing sends.
3. For remove, locate and suppress the address from any course-email list promptly. Do not claim removal is automatic.
4. Keep course email records purpose-limited, and resolve incomplete or ambiguous requests by direct correspondence.
5. Before migrating to an email service, implement provider-managed confirmed opt-in and unsubscribe, document data processing and retention, and test the full lifecycle without sending real test emails to visitors.

### What we can measure now
Existing Umami pageviews can give aggregate Poker School page reach without collecting form values. Request count, verified opt-in count, opt-outs and beta invitations require private Formspark/operator records. They are **not** measured automatically by Umami, and no rate or learner outcome has been reported. Do not infer opt-in conversion when numerator or denominator is missing.

## Next gates
Qualified review, then observed beginner learning, then an original narrated pilot module, then a limited paid beta with a truthful offer and explicit customer terms. Avoid a membership platform, recurring billing or expansion of unreviewed practice at this stage.

## Verification
Run the committed build check, full unit and HTML suites, and the offline mocked browser suite `python _tests/browser.py`. Confirm: consent required for register, no consent required for remove, anti-spam verification and retry, no-script readability, general contact still working, privacy links and mobile layout. Provider acceptance of a live request requires a separately authorized operator check and is not covered by offline tests.
