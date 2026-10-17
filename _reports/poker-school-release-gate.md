# Poker School: release engineering and evidence boundaries

**Publication receipt:** use PR #110's exact commit, required Site checks, Pages deployment and published-byte result. This file describes the candidate and its checks; it is not a deployment or mailing-list receipt.

## What the candidate changes

The proposed course and optional interest request live at `/poker/school/`. Poker home and the Study Desk point to that page. The existing free Poker Foundations course, its teaching-review inputs, `assets/contact.js`, and the general privacy page retain the exact bytes of main commit `9021d4604c9427c37dc6c788753ddf9675dfc7ba`. The separate request script is loaded only on the School page. Its supplemental privacy text explains manual handling, explicit opt-in and removal requests.

No existing free material is paywalled. No course price, launch date, paid access, personal teaching credentials, participant results or profit claims are introduced. Qualified human teaching review and actual beginner observations remain pending.

## Historical release compatibility

Earlier versions of this PR failed the full suite because the new page was not represented in the historical replay chain. The last pre-repair candidate, `3f4db484`, had 101 failures and 5 errors across 794 unit tests. Those failed runs are historical evidence, not an instruction to waive the release gate.

`_tests/poker_school_history.py` and `_tests/poker-school-change.json` now describe a bounded, test-only view of the exact pre-School release. A file is reversed only when its entire SHA-256 matches the reviewed new bytes. The adapter verifies each replacement offset and the restored file's old hash. New files, generated pages and metadata records are removed from older views only on an exact match. Unknown or modified bytes remain visible. The deployed build never invokes this adapter.

The predecessor's source inventory, 221 generated outputs and public metadata are pinned separately. Independent tests reconstruct their hashes and compare restored Git blobs to the original 1,207-file inventory. Corrupted edits, unexpected changes, modified additions and altered new-page metadata are rejected. Existing `*-baseline.json`, `*-change.json` and historical search-result files have not been refreshed to manufacture success.

The current search audit includes 194 HTML pages. The current live-response inventory includes 475 targets, including the School page and both new assets. These are inventory checks, not traffic, engagement or learning outcomes.

## Reproducing the compatibility record

From a complete local checkout containing the pinned parent Git object:

```sh
python _reports/poker-school/capture_history.py
```

The default command is read-only. It executes the actual parent metadata/build pipeline, verifies the committed parent output, checks the candidate's declared changes, and reproduces the record. `--write` is only for preparing this unapproved candidate before its exact revision is reviewed. Never overwrite historical baselines to hide an unexpected change. A later approved release needs its own explicit compatibility step.

The one-release `_scripts/poker_school_release.py` checks the tracked path inventory and protected files. It does not replace the exact-content tests or authorize publication. Its pure algorithm and mutation tests remain in the regular suite; its frozen whole-tree inventory is intentionally not imposed on every future site revision.

## Functional and release verification

Run the ordinary committed-build, HTML, search, unit and browser checks. The existing browser suite now covers School opt-in, removal without consent, switching back to registration, missing/expired verification, provider rejection, rate limits, network failure, timeouts, duplicate submission, no-script access, enlarged text and the pinned accessibility checker. All form-service requests in these tests are intercepted and mocked.

The original contact behavior remains independently tested. Link validation still checks every internal destination and fragment; repeated target parsing is cached only within that one immutable-output test to avoid redundant work.

```sh
python _scripts/build.py --check
python _tests/check_html5.py
python _scripts/check_search.py
python -m unittest discover -s _tests -p 'test_*.py' -v
node --check assets/poker-school-interest.js
python _tests/browser.py
```

The full five-group browser matrix and aggregate `checks` job are required before merge. Verify Pages and all published-response bytes at the exact main commit afterward. Use PR comments for final run IDs so recording a receipt does not silently change the tested tree.

## Operational limits

Formspark acceptance is not verified email ownership, mailing-list enrollment, completed removal, inbox delivery or a message read by Nolan. Actual incoming requests must be processed privately under `_reports/poker-school-offer.md`. This release adds no automated mailing provider, billing, account or at-table assistance. No real test submissions or marketing emails are sent during software verification.
