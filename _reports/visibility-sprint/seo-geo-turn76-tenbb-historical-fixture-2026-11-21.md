# SEO/GEO Turn 76: repair an actual historical-test regression from the 10 BB worksheet gate

**Date:** November 21, 2026 (Pacific/Honolulu)
**Starting main:** `0d2767003dfdc192b0c926f06bad628e98eddab3` (Turn 75, merged PR #449).
**Scope:** The existing local unit-test fixture and release instructions. No public-page, sitemap, schema, analytics or product changes.

## Verified inconsistency

Turn 72 appropriately strengthened `_scripts/tenbb_companion.py`: the standalone `/poker/10bb/` page may be registered only with its original HTML, Python ICM checker, and Markdown six-check worksheet present. `_scripts/player_find.py` reuses this exact registration before adding the page to site Find.

However, `_tests/test_turn65_tenbb_find.py` still built a temporary fixture from **only the page and checker** and asserted that `player_find.tenbb_entry(root)` successfully returned the published route. Under the Turn 72 three-file gate, `tenbb_companion.record(root)` must instead raise `ValueError('10 BB Playbook, checker or written worksheet is missing')`. The old expected-success assertion therefore contradicts the current contract and would fail when the full test module executes.

## Change completed

1. Keep the original test's absence case and page-only partial-publication rejection.
2. After copying the Python checker, explicitly assert that registration **still fails** because the required worksheet is missing.
3. Copy `downloads/ten-bb-tournament-checklist.md` into the fixture before asserting a successful `/poker/10bb/` Find entry.
4. Delete that worksheet after the success assertion and verify registration fails closed again; restore it before the existing altered-metadata rejection.
5. Document this as a current test-fixture correction in `AGENTS.md`. Preserve the original Turn 65 historical publication and testing record rather than rewriting it.

## Verification performed

| Check | Outcome | Boundary |
| --- | --- | --- |
| Main and changed source dependencies | Inspected through authenticated GitHub | Old temporary fixture lacks worksheet; registration function requires it |
| Repository module identity | Verified | Local isolated copy `tenbb_companion.py` has Git blob SHA `1dacc7d910a140cf8194965270f545b1ee0c1e69`, exactly matching connected GitHub source |
| Actual module, synthetic HTML-only fixture | Expected missing-asset rejection | Isolated module execution, not full suite |
| Actual module, synthetic HTML + Python fixture | Expected missing-worksheet rejection | Reproduces the old test's invalid acceptance expectation |
| Actual module, synthetic HTML + Python + Markdown fixture | Successfully registered canonical route | Confirms repaired fixture meets the present source contract |
| Same complete fixture with worksheet removed | Expected missing-worksheet rejection | Confirms fail-closed behavior persists |
| New current test fixture source | Reviewed | Both positive and negative worksheet assertions now present |
| Full repository unit suite, deterministic build, HTML5 and browser | **Not run** | Container still cannot resolve GitHub for complete repository checkout |
| Live HTTP bytes, Google/Bing search and AI citations | **Not run/unavailable** | No claim of ranking or indexing effect |

The isolated test used deliberately minimal synthetic HTML with the source's expected Article identity and metadata, and small stand-in checker/worksheet files. It validates the registration dependency and returns the correct result for all four file states. It does not prove full Playbook content accuracy, current public delivery or a complete test suite pass.

## Acceptance on complete checkout

```powershell
py -3 -m unittest discover -s _tests -p test_turn65_tenbb_find.py -v
py -3 -m unittest discover -s _tests -p test_turn72_reader_release_coverage.py -v
py -3 -m unittest discover -s _tests -p test_turn67_playbook_standalone.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
```

If the corrected Turn 65 fixture passes but other tests fail, investigate each failing test against the latest source contract. Do not remove the worksheet requirement or rewrite historical fixture snapshots just to achieve a passing count.

## Sprint progress

This is a **test consistency and release-readiness repair**. It removes a specific internally contradictory success assertion that would obstruct meaningful execution of the full test suite. The current source still has the original **230** distinct sitemap URLs. This turn does not increase public content count, fabricate retailer details, alter the Playbook or claim Google/Bing/AI visibility gains.

The highest-value remaining tasks are still (1) executing the current-source release suite in an environment that can access the complete checkout, (2) collecting first-party settled search and AI-discovery measurements, and (3) repairing observed mobile or performance problems rather than adding generic SEO pages. Do not create GitHub Actions or another paid subscription.
