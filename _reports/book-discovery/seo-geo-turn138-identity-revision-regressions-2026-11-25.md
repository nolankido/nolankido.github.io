# SEO/GEO Turn 138: reconcile identity release-date regressions

Date: 2026-11-25. Base candidate: 2e7237e847a742fed4793e5611f6475753e8d968.

The reviewed current source manifest and committed sitemap agree exactly on these dates: Home and About 2026-11-24 (the three-title bibliography revision), Technology 2026-11-20, Keep the Judgment 2026-11-06 (original publication 2026-10-11). Six older regression modules still used superseded date expectations. Updated their exact date assertions, preserving all other identity, navigation, accessibility, source, output and negative controls. The earlier dated evidence is not rewritten. Dates remain exact, not lower bounds or dynamic comparisons that would permit arbitrary freshness changes.

Verified before committing: each of the four routes has exactly one matching manifest record and one matching sitemap record; all 17 guarded text substitutions matched exactly once. No public content, canonical, generated files, historical ledger, date, workflow or dependency changes. This is a targeted repository inspection and edit, not an executed Python suite. Full local checkout/build, search snapshot, HTML5, full unit and browser validation remain mandatory. Direct checkout was blocked by DNS. Do not merge or assert public release without the existing gate and exact live receipts.
