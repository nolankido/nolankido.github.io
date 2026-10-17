# Poker School Turn 1: Release gate and next engineering steps

**State (October 16, 2026, Hawaii):** Implementation on draft PR #110; NOT MERGED; no production deployment. Parent release at start: `9021d4604c9427c37dc6c788753ddf9675dfc7ba`. Current branch can advance while this document remains the issue record.

## What has been implemented

- Proposed five-stage course and free/paid distinction at `/poker/school/`.
- Small optional offers from Poker homepage, the free course and the Study Desk.
- Interest request with explicitly unchecked marketing-email consent, removal path without consent, optional learning category and name, Formspark and Cloudflare Turnstile.
- Consent and manual-processing disclosures in Privacy; existing backend processes requests only when a person reviews them.
- Focused static and form contract tests, new offline Playwright cases, and an operator procedure in `_reports/poker-school-offer.md`.
- No mailing-list enrollment API, subscriber account, checkout, billing, personal tracking event, marketing promise, or real provider submission.

## Exact QA observations

1. One-off branch-generated-site workflow `39017035468` **passed** and committed new HTML, sitemap, search payloads and cache tokens to the feature branch (commit `815fa5cf76fcea957e1c66e3960db1744821e9ed`). The temporary generator has been removed.
2. Normal full site checks for commit `c6b9d1753b9cbfa53cada9cdc6a964a16e062830`: run `39017078558`, **FAILED**. Python stage ran **791 tests** and found **143 failures and 9 errors**; browser matrix was skipped. This is a release blocker, not merely a cosmetic warning.
3. Most failures are frozen predecessor/source/body/search/inventory contracts. Examples: old tests expect 472 live targets, new manifest has 473; many earlier tests compare all older pages, HTML heading indexes and output digests without an exception for an added route; unchanged version of the free course is pinned to an independent human teaching-review source hash; other tests forbid scripts outside contact. The old source/privacy/contact script bytes also changed. Some reported errors arise downstream of the teaching-review scope mismatch. **Do not refresh all baselines just to make tests pass.**
4. An additional isolated browser test was started under one temporary workflow; its outcome belongs in the GitHub Actions run receipt. Both temporary workflows have been removed from the branch and must not be restored as permanent infrastructure.

## Priority fixes before any merge

1. **Separate shared concerns.** Decide whether to move Poker School's form logic to its own page-scoped asset so existing `assets/contact.js` and `/contact/` behavior remain byte-identical. The preferred design is minimal impact on the established general contact path.
2. **Respect the teaching review lock.** Either remove the optional course CTA from the signed-off/revision-fingerprinted `_source/poker/free-poker-learning-path.html` and link from the Poker homepage instead, or generate a genuinely new reviewed source-scope packet and revalidate all affected lesson inputs. Do not silently rewrite a signed-off hash. Reviewer acceptance is still pending.
3. **Introduce an explicit additive public-route release contract.** List every intentional new source, generated target and index addition, and independently prove that **all old entries, source paragraphs, redirects, and approved assets** remain byte-for-byte or semantically unchanged where required. Old history baselines should remain reproducible, with a verified reversible adapter for the new, bounded delta. Scope edits only to the historical invariants genuinely touched.
4. **Adjust the live/search and script scope invariants narrowly.** The new route is intended to add one page, not change pre-existing search titles, anchors, or content; show that via a targeted comparison and check the new page can be crawled. Explicitly whitelist only the new form route for its page-specific script.
5. **Run independent end-to-end validation.** Unit tests, HTML validation, accessibility, browser flows for consent and removal at mobile widths and with no JavaScript, and regression tests for the old contact form. No real Formspark submissions during automated tests. Review any Code Review findings on the exact final commit.
6. **Final release gate and evidence.** `python _scripts/build.py --check`, all project unit tests, all browser groups, PR aggregate `checks` success, publish to main via reviewed merge, independent Pages deployment and published-byte verification at the exact main SHA. Remove temporary infrastructure before merge.

Do not declare the page live until step 6 completes. Keep PR #110 as **draft** with this blocker record. No visitor interest or education outcome should be claimed from synthetic tests.

## Functional and product constraints

- Product wording remains provisional. Price, date, coaching and paid lessons are undefined. Poker Foundations stays free.
- Interest emails require explicit affirmative consent. Requests to stop emails must never require opting in. Form acceptance is not list enrollment or removal.
- Keep submitted personal information out of GitHub, URLs, tracker events, browser storage and public reports.
- Course completion or a correct test answer is not demonstrated learning or profitable play; human review and genuine beginner observations are still future dependencies.
