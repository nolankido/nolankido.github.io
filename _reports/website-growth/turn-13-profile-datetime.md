# Turn 13: accurate ProfilePage dates

Status: candidate; Google recrawl and report validation are separate from software qualification.

Reference release: `3d58eef8d5d878885bfbcfe67b6565a17cd9defb`.

## Reproduced defect and narrow correction

The committed About page declares `ProfilePage` with `dateModified: 2026-10-17`. Google's ProfilePage documentation defines this optional property as DateTime. The site's editorial catalog stores a calendar day, not a verified clock time. Do not append invented midnight, use the build time, or change the biography just to create a newer date.

The search decorator now omits date-only `dateModified` values from ProfilePage markup. It preserves independently supplied full timestamps, all other schema types, Person identity, the page's visible content, canonical URL, and the existing sitemap revision. The current site has one ProfilePage, so only `about/index.html` changes among the 222 generated outputs. Article and ordinary WebPage dates are unaffected. No new public route, visible content, script, style, tracking, indexing policy, or subscription is introduced.

The field is recommended, not required. This removes the reproduced invalid-value condition; it does not claim that Google has recrawled the page, cleared its report, granted a rich result, or improved traffic. A future accurately sourced profile timestamp may be supplied without this decorator rewriting it.

## Preservation and qualification

Twelve focused tests cover the old defect, corrected JSON-LD, exact visible/other-head preservation, input copying, real timestamp preservation, other schema dates, absent-date behavior, unchanged sitemap revision, exact production inventory, unknown mutation refusal, corrupt history and upstream date validation.

An exact-hash test-only adapter reverses only the two approved files, the decorator and the generated About page, before older release-preservation checks. It never accepts an altered file and does not refresh a published baseline. Three older inventory assertions use that approved predecessor view; all their original expected hashes remain unchanged. The new scope check protects all 714 tracked production/configuration paths against the published parent, with only the two approved deltas normalized.

Required before merge: deterministic build, HTML/search validation, complete unit suite, all five hosted browser groups, and review of the final candidate. After merge: verify Pages and public response bytes. A temporary source-export/preparation workflow must stay on helper branches and is not part of this release.

## Separate crawl-policy triage

The existing policy intentionally marks the site finders, contact card and not-found page noindex. Noindex/redirect notifications without affected URL examples do not justify removing these controls. Inspect the actual indexed/canonical URL examples separately when authenticated Search Console access is available. HTTP 200 and local crawlability are not evidence of indexing.

## References

- Google ProfilePage documentation, required and recommended properties: https://developers.google.com/search/docs/appearance/structured-data/profile-page
- Google monitoring guidance on that same page: validate code, inspect the live URL, request report validation, and allow recrawling time. None guarantees search appearance.

Human task observations and an authenticated dated performance export remain separate evidence requirements in issue #123. This markup repair does not count as a study result.
