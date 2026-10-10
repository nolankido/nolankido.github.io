# Technology for Real Life: recovered release verification

Reviewed October 10, 2026.

Base public release: `66c507d5149b81ee666eb48f2bd2f3a94e7fbb01`.
Verified source/output commit: `29797ac6fb127cad80abd920efd3c8ad4dd16477`.
Successful recovery run: `38046353238`.
Artifact: `living-well-completion-checks`, ID `11667820832`.
Artifact SHA-256: `08cff36bc76d7fecfdd079bd43b5ebc37ff5bf8256ca9b87e44740c0a59718de`.

## Executed checks

- The original eleven-file completion payload, allowed paths, and source hashes were checked before application and after patching. The subsequent browser regression and section-CSS correction were checked against separately reviewed hashes. Other sections and global configuration remained outside the change scope.
- Deterministic build: 160 generated outputs checked, zero differences.
- Full unit discovery: 259 reported test executions in 115.404 seconds, all passing.
- Living Well browser checks: all 61 pages at 320, 390, 620, 768, 1024 and 1440 CSS pixels, including expanded text spacing.
- The seven practical templates were checked against their source text, with and without JavaScript. Native disclosures, keyboard outlines, reader routes, resource links, all five original exact-byte worksheet downloads and print visibility passed.
- The no-JavaScript resource-index-to-collection pointer route was repeated three times with normal actionability checks. All three passed. No forced click, JavaScript-enabled substitute, skipped assertion or disabled test was used.
- The dedicated report contains zero configured axe-core violations, JavaScript errors, failed local responses and write requests. External services were blocked during those browser checks.
- The retained whole-site review covered 147 page records, 1,029 viewport checks and 294 axe checks with no failures. Its manual color-contrast review notes remain in the report; automated scans do not certify all browsers, assistive technologies or contrast cases.

Local checks independently passed 259 tests and 168 isolated rendering/reflow checks over fourteen affected routes at six widths. Local HTTP browsing was administratively blocked, so the isolated rendering was not presented as navigation testing. Actual navigation was tested by the successful runner-based suite.

## What was recovered and corrected

The interrupted PR contained unpublished content, not a successful public release. Its earlier browser runs failed around a no-JavaScript resource detail interaction. Adding only a load-state wait did not resolve the problem. The final changes synchronize with the destination document, preserve the actual native pointer interaction, and use immediate anchor scrolling in the Living Well stylesheet rather than long smooth-scroll motion. The repeated route and full suite then passed. The shared stylesheet and other site sections retain their original behavior.

The eight new readings now have the actual October 10 publication date. Seven worked guides include a visible result, required starting material, simplest route, completion check and static plain-text starter. A prominent homepage route and a dedicated guide collection connect the resource library to concrete tasks. The publishing guide documents the evidence and permission needed for future articles and videos; it does not invent a completed demonstration or firsthand account.

## Preservation and limits

Living Well has 61 pages: 31 published readings and three explicitly proposed experiments, alongside its supporting and resource pages. The 66-resource catalog and five original worksheet downloads are unchanged. The canonical hash of the prior 26 reading records remains `79d2ae896b9ac0cdaf5ae2d585b5022107a6477c051a4a83bac5fd0a511ce0bb`.

The global homepage, main navigation, contact service, privacy, analytics, original design assets, Poker content and other site sections are unchanged. No new visitor JavaScript, forms, accounts, trackers, embeds or collection of private answers is added. The only style adjustment is immediate anchor navigation within Living Well.

Official Apple, Google, Joplin and NIST source information was reviewed with narrowly stated roles. App installation, model execution, account-sharing workflows, media playback, clinical outcomes and third-party security were not tested or implied. Examples remain fictional, arithmetic remains illustrative, and no personal stories, practices, favorites or measured benefits are fabricated.

The temporary recovery workflow and both transfer fragments are removed in the clean review commit. Permanent workflow permissions and all retained release gates remain unchanged. Full clean-PR checks are required before merge. GitHub Pages deployment and the existing exact public-byte verification remain separate post-merge checks; a branch verification is not described as a live release.
