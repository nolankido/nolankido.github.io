# SEO/GEO Turn 106: why a correct called-state ICM calculation can still misprice a fold

Date: November 23, 2026.
Base main: `c09e245f70f09ecf8477cfb76e9038e6de9c6bb2`.
Existing worksheet: `downloads/poker-multiway-icm-workbook.md`.
Existing verifier: `downloads/poker-multiway-icm-verify.py`.

## Reader improvement

Extend the existing three-way main/side-pot workbook rather than create an overlapping indexed article. The original 4/14/9 BB, 27 BB total, 12 BB main pot, 10 BB side pot, 5 BB additional call, $70/$30/$0 payouts, and stipulated simultaneous-elimination convention remain unchanged. Two new entirely fictional ranking distributions isolate the counterfactual fold baseline.

| Strict ranking | A | B |
| --- | ---: | ---: |
| H > X > Y | 1/5 | 0 |
| H > Y > X | 0 | 1/5 |
| X > H > Y | 1/4 | 1/4 |
| X > Y > H | 11/20 | 11/20 |

Both distributions produce exactly the same called-state distribution, all-player called prize equities, 1/5 main-pot win probability, 9/20 side-pot win probability, 119/10 expected called BB and 19/10 BB gain over folding. All unlisted strict rankings have probability zero.

The only changing branch is the relative ranking of X and Y when H would win both pots. After a fold, X survives in A, but X is eliminated in B with probability 1/5. Hero retains 10 BB in both. The ICM comparison therefore changes sign.

| Hero value | A | B |
| --- | ---: | ---: |
| Fold | 11090/297 | 11534/297 |
| Call | 17638/459 | 17638/459 |
| Call minus fold | 5488/5049 | -2060/5049 |

These are conditional arithmetic illustrations, not verified real-card or range distributions, predictions, or actual hand recommendations. Do not assume the probabilities are realizable by particular cards. The workbook states explicitly that a real counterfactual may be unobservable.

## Changes

- Add the new section, complete probability and prize tables, derivation, and a reader practice question to the original worksheet.
- Reuse the original settlement and classic ICM code through a private report helper. Preserve the original fixed report fields, add the two verified ledgers under `fold_baseline_sensitivity`, and reject duplicated ranking rows. Preserve default JSON and self-test flags; no new user input or dependency.
- Add one identical "Side-pot ICM worksheet" download link to the bounty guide's authored and generated jump navigation. The original tournament-equity worksheet link was already independently observed live. The eight bounty practice questions, four tables, canonical URL, and original reading labels remain.
- Register `_tests/test_turn106_icm_fold_counterfactual.py` in the manual release runner. No new indexed route or change to search or sitemap files.

## Executed checks

Nine new standalone tests and all 13 existing Turn 105 standalone tests passed in the isolated matching fixture, for 22 total. Checks include independent closed-form ICM, all branch/expected prize conservation, unchanged original fixed report, exact called-state identity, the two fold baselines, rejection of duplicate ranking weights, and deliberate corrupted expectations failing in normal, -O and -OO modes. All three self-test invocations passed. The original read-time module remains unchanged.

The locally tested Git blobs:
- Worksheet: `b76486401d37366fbbf7a9cdef169f3d124897a8`.
- Verifier: `97d364ae308045e3045200fc0a2f1eb0d82abcf7`.
- Regression module: `0bb7191a3e22d6988d35d34f110b0d62123ddd1d`.

Authenticated repository reads confirm both guide links, retained practice and table counts, and the unchanged displayed 15-minute bounty estimate. A separate static word-count check on authored HTML excluding marked optional details yields 3192 core words after the three-word link, still 15 minutes. It also yields the existing 14-minute satellite and 7-minute tournament-equity estimates. This is a bounded static cross-check, not a complete deterministic generator or Finder audit. Finder's parser excludes navigation.

Two new site integration tests remain unexecuted in the isolated fixture. The full original website suite, deterministic builder, search snapshot, HTML and browser checks, and public exact-byte receipts remain outstanding. Run them in a complete matching checkout. The previous live guide link check does not prove either downloadable file's live bytes.

```powershell
py -3 downloads/poker-multiway-icm-verify.py --self-test
py -3 -O downloads/poker-multiway-icm-verify.py --self-test
py -3 -OO downloads/poker-multiway-icm-verify.py --self-test
py -3 -m unittest discover -s _tests -p test_turn105_multiway_icm_workbook.py -v
py -3 -m unittest discover -s _tests -p test_turn106_icm_fold_counterfactual.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _scripts/local_release_checks.py --full --browser
```

No tracking, external dependencies, paid services, new automation, or GitHub Actions were introduced.
