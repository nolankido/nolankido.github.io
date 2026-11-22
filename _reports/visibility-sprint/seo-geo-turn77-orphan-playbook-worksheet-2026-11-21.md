# SEO/GEO Turn 77: fail closed on orphaned Poker Playbook worksheets

**Date:** November 21, 2026 (Pacific/Honolulu)
**Starting main:** `80e3269a43896498210d52c90a72bd5d41534716` (Turn 76, PR #450).
**Scope:** Existing Find indexing contract, its direct negative-control test, and source ownership documentation. No changes to public content, sitemap, schema, metadata, site tracking or release prerequisites.

## Confirmed defect

The published written 10 BB Poker Playbook requires three files to be a valid manual resource: `poker/10bb/index.html`, `downloads/ten-bb-playbook-icm-verify.py` and `downloads/ten-bb-tournament-checklist.md`. This was intentionally enforced by `tenbb_companion.record()` in Turn 72 and reconciled with the old Turn 65 test fixture in Turn 76.

`_scripts/player_find.py` nevertheless used a two-file presence guard: `if not page.exists() and not checker.exists(): return None`. If the **worksheet alone** was present, this returned `None` before calling the strict three-file validator. As a result, a partial publication was silently treated as an absent guide by the Find search inventory, rather than rejected as invalid. This does not establish that such an orphan currently exists in production; the repository contains all three original files.

## Correction

1. Include the worksheet path in `player_find.tenbb_entry`'s publication-presence guard. Return `None` only when **all three** publication files are absent. Any nonempty file subset must be checked by `tenbb_companion.record()`, which still fails closed when a required file is missing or its metadata is invalid.
2. Add `test_orphan_worksheet_without_playbook_cannot_silently_disappear` to the existing `_tests/test_turn65_tenbb_find.py`. A clean temporary root remains an unpublished resource; after copying only the worksheet, `tenbb_entry` must raise; after deleting the orphan file it may return `None` again. Preserve Turn 76's prior three-file fixture correction, source metadata requirements, card counts and local Find search behaviors.
3. Document the invariant in `AGENTS.md`. No extra release runner registration is needed because the existing manual checker already executes `test_turn65_tenbb_find.py`.

## Evidence and acceptance

| Gate | Result | Qualification |
| --- | --- | --- |
| Defect in authenticated main | Confirmed | Original guard checks only HTML and Python asset |
| Corrected GitHub branch source | Written and read back | Three-asset presence predicate with strict existing `record()` validation |
| New negative-control test | Authored | Worksheet-only temporary root must raise `ValueError` |
| Isolated five-state presence logic | 5/5 expected results | Synthetic file states: empty, worksheet only, HTML+Python, complete three-file set, HTML+worksheet. Not the full repository unittest |
| Complete repository Python/build/HTML5/Playwright suite | Not run | Current container cannot resolve `github.com` for a complete checkout |
| Production exact-byte HTTP verification | Not run | No source-to-public byte receipt was created |
| Authenticated Google/Bing/AI search growth | Unavailable | No ranking, indexing, AI citation or traffic gain is inferred |

## Full-checkout commands

```powershell
py -3 -m unittest discover -s _tests -p test_turn65_tenbb_find.py -v
py -3 -m unittest discover -s _tests -p test_turn72_reader_release_coverage.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
```

Do not weaken `tenbb_companion.record()` or accept incomplete file sets merely to produce a green test. Verify that the actual generator and local Find card index remain unchanged for the correctly published three-file Playbook. An isolated presence matrix is useful but does not certify the website.

## Sprint status

**Advanced:** source-owned local Find now enforces the same complete three-asset public-resource invariant as the site's sitemap and release verification. No content or canonical URL was added, removed or modified, and the most recent committed sitemap still inventories 230 distinct URLs.

**Still open:** executable full-current-source test pass and real mobile reader validation; exact live byte parity; authenticated Search Console / Bing query-page baselines and frozen AI citation panel; measured performance and book retailer identifiers. The first complete post-sprint month, December 2026, has not happened yet.

**Next priority:** Run a complete release checklist in a network-capable checkout, correct confirmed test failures, and use verified first-party search observations to target a single substantive content improvement rather than continuing to add generic pages.
