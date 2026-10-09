# Whole-Poker overview and reader-usability pass

Review date: October 8, 2026 (Hawaii)
Production baseline: 094da26e8aba530da1f7cfc496ef9dabfca8a7de
Scope: the complete 70-page Poker subsection; build integration and regression tests.

## Diagnosed and repaired

1. The shared reader outline discarded the first real section of every guide.
   It now includes all existing major-section anchors, while excluding hidden
   content, answer panels and navigation. The cash study path starts at Session 1.
2. Authored legacy breadcrumbs duplicated the shared subject breadcrumb on many
   articles. Build-time cleanup removes only this known legacy component, refuses
   removal if it contains a fragment target, and leaves the shared trail intact.
3. Utility pages lacked a meaningful active subsection destination. Every Poker
   page now has exactly one current section; calculators and sheets belong to the
   Study Desk and the directory review record belongs to External links.
4. The guide library used a different taxonomy from Topics and Search. Its filter
   controls now use the same ten subjects and explicit cross-list memberships.
   Each guide still appears once; overlapping topic counts are explained.
5. Topic pages offered only a few direct source links, with complete membership
   depending on the search script. Each now has a native, alphabetical disclosure
   of all sources, with publisher, access label and listing/review-context link.
6. The homepage repeated the entire detailed topic-card grid. It now uses a compact
   subject menu, with full cards kept on the topic map. Existing anchors and guided
   collection links remain available. Calculators have a direct shortcut.
7. The Study Desk buried task choices beneath blank downloads. Existing task routes
   now precede the download sections, with concise entry links and evergreen copy.
8. The finder displayed an empty study-list panel before any result. The list now
   appears only after a selection and clearing it returns focus to search. Scope
   explanations and alternate browsing paths follow results rather than block them.
9. Native browser search-field clearing did not trigger a finder update. It now
   updates results while preserving deliberate topic/type/free constraints.
10. Optional filter panels start collapsed on small screens, reducing the distance
    to results. Active deep-link search filters remain expanded. Native disclosures,
    desktop filters, keyboard reset and result navigation remain available.
11. Reader metadata preferred the original date to a substantive revision. It now
    labels the latest explicit revision as Updated, otherwise Published. Existing
    dates are not rewritten. Search also excludes aria-hidden source subtrees.

## Preservation and boundaries

All 47 guide-library entries, 146 resource records, source review dates, existing
article routes, glossary definitions, public downloads and worked examples are
retained. Source subjects and reviews are reused rather than copied into another
manually maintained catalogue. No outside publisher was newly certified or ranked.

The personal root gateway, Technology and Creative Work pages, original global
stylesheets, shared layout, contact, analytics, DNS and hosting are unchanged.
No new account, paid service, runtime dependency, data collection, gambling action
or user-input storage was introduced. This pass does not claim strategic accuracy
of paid products, a full external-link freshness audit, or accessibility certification.

## Local evidence

- Deterministic generated build and 218 dependency-free regression tests passed.
- JavaScript syntax checked for the revised finder and library scripts.
- Static rendering inspected at phone, tablet and desktop widths. The local browser
  environment blocks localhost HTTP navigation, so static previews are not described
  as end-to-end tests. Real HTTP navigation, no-JavaScript interaction, downloads,
  filter history and automated accessibility remain GitHub release-gate requirements.
- The reachability test covers every Poker route, with a maximum of three links
  from the Poker homepage in the generated navigation graph. This is not a measured
  user success rate and includes links inside native disclosures.
- Existing numeric-example, privacy, metadata, link and fragment tests are retained.
  Old tests that required obsolete filter names or omitted first sections now assert
  the new subject memberships and complete outlines instead.

## Release gates

The full Site checks workflow adds overview_browser without weakening existing
suites. Require exact-head success before merge, inspect CI screenshots and logs,
then check Pages deployment and the production public-response byte comparison.
The pull request records actual release outcomes; this source report alone does
not establish deployment or a new test pass.

## Remaining quality work

Observe actual readers performing common tasks before another broad redesign.
Continue the authorized weekly external-directory maintenance review. Distinguish
inconclusive provider blocks from dead links. Prioritize missing subject depth and
original poker material separately from navigation work. Keep any future profiles,
accounts or analytics expansion outside this static usability pass.
