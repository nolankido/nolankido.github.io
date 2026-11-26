# SEO/GEO Turn 113: release regression reconciliation and ProfilePage parity

November 24, 2026. Previous draft head: d66f4bb409a424f62ebb48003aef5bb0179a9554. Implementation commit: f292772376c338da72d291fb2c9b61afd2c822a2.

The current draft included a day-only About ProfilePage dateModified even though its existing generator omits such a value. Removed that single generated JSON-LD property and kept the manifest and sitemap calendar revision of November 24. The search audit now rejects this day-only field. No credentials, author claims, reader copy, or canonical changed.

Updated 12 current regression modules: PBG-03 shared reader stylesheet; Turn 62 standalone HTML5 inventory including every registered book; Turns 52, 66, 67, 68, 69, 81, 84 and 85 current sitemap expectations; Turn 80 About revision and metadata; Turn 108 identity page date policy. Turn 52 still checks the generated audit count against the actual sitemap. Old publication dates and evidence assertions remain. The draft still contains 231 unique sitemap URLs, three standalone book pages, and the unchanged previous audit snapshot pending real regeneration.

Verification: 46 targeted precommit checks and 19 exact committed read-back checks (65 total). The read-back confirms the About HTML differs only by removal of the single optional JSON-LD property, the source revision remains in the sitemap, the CSS expectation matches the draft, and the new audit check and corrected test expectations are committed. These are structural checks, not full Python regression execution. A current git ls-remote attempt failed with "Could not resolve host: github.com". Full local deterministic build, search audit generation, regression/browser suites, historical test review and production deployment remain pending. No search ranking, crawler uptake or citation increase is asserted.

Use the previously committed manual command in an isolated complete checkout:
    python _scripts/prepare_local_release.py --apply

Keep the draft unmerged until the real release checks succeed. Do not hand-edit the audit snapshot, weaken evidence tests or introduce GitHub Actions.
