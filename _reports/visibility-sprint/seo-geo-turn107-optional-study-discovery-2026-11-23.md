# SEO/GEO Turn 107: discover optional poker study examples without answer spoilers

Date: November 23, 2026.
Base main: `fca2548e02f7af8c066a15996d733894a791ac37`.
Existing indexed resource: `/poker/find/`.

## Reader problem

The site's existing search extractor excludes collapsed details, so it avoids practice-answer spoilers but also omits the visible titles of advanced satellite split-pot and mystery-bounty inventory examples. Preserve that answer boundary while making these specific study topics searchable and linkable.

## Implementation

- Add the standard-library `poker_optional_summary.py` extractor. It reads only the plain visible direct summary of an explicitly marked `details[data-reading-optional="true"]`. Hidden, nested, unmarked, navigation, script, template and normal exercise disclosures stay excluded. Reject unsafe or duplicate anchors, empty or hidden summaries, malformed marked disclosures and collisions with ordinary guide-section anchors. Do not index the answer body.
- Append summary-only passages to the existing guide's extracted sections. Preserve all existing core passages and the existing 301 Finder entries.
- Clarify the two existing summary titles so they identify satellite split pots and ties, and mystery bounty draw inventory. The titles remain marked optional for the core reading-time calculation. Update authored and generated pages identically.
- Update only the two existing cards and the search scope note in the generated Finder HTML. Keep the existing stable anchors `sat-tie-branch` and `bounty-mystery-draw`. No new indexed URL, sitemap entry, new network behavior, tracking, or JavaScript dependency.
- Update the two previous regression expectations to require unchanged core excerpts plus exactly one summary-only passage. Register the new tests in the manual release runner, and add four future browser search checks to the existing browser suite.

## Executed evidence

The eight standalone Python tests passed against the exact new helper and a reconstructed copy of the updated GuideText class. The new helper and new test source match Git blobs `960df62fcbd58afb60ecf3384b5bd791706cad92` and `295e3a6940f5eaedad835c352deced73efb65be7`. The tests cover normal versus explicitly optional details, hidden/nested exclusions, title-only extraction, unsafe/malformed/duplicate anchors, whitespace and entities, hidden-container close handling, retained original core passages, and anchor collisions.

Read the full 301-card generated Finder blob and run the current normalize, includes, plan, prepare, passage and score functions (copied definitions checked against the committed JavaScript source). Four targeted queries ranked their intended existing guide first and selected its advanced-example anchor:

| Query | Selected anchor |
| --- | --- |
| satellite split pots and ties | sat-tie-branch |
| satellite chip equity different seat values | sat-tie-branch |
| mystery bounty draw inventory | bounty-mystery-draw |
| mystery bounty jackpot drawn | bounty-mystery-draw |

Repository readback confirms the summaries match between authored and generated article files, each appears exactly once as a Finder passage, each passage contains its title only, and the checked answer tokens are absent. The generated Finder content was updated by bounded replacements against its original authenticated Git blob. This is a targeted extraction and scoring check, **not** a complete Chromium run, complete site regeneration, or external ranking/traffic result.

The expanded Turn 106 ICM worksheet was independently observed live at the beginning of this turn.

## Remaining acceptance

The two full-site integration tests, original full Finder and article tests, new browser journeys, deterministic full builder, search snapshot, complete internal link checks and public deployment byte receipts remain unexecuted in a complete checkout. Run them before claiming full site release acceptance.

```powershell
py -3 -m unittest discover -s _tests -p test_turn107_optional_finder_summaries.py -v
py -3 -m unittest discover -s _tests -p test_turn103_satellite_tie_branch.py -v
py -3 -m unittest discover -s _tests -p test_turn104_mystery_bounty_inventory.py -v
py -3 _tests/finder_browser.py
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _scripts/local_release_checks.py --full --browser
```

No new indexed content count, search query collection, tracking, paid service, scheduled automation, or GitHub Actions.
