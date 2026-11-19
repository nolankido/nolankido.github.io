# SEO/GEO/AEO Turn 27: comparator test portability and release coverage

**Date:** November 19, 2026 (Pacific/Honolulu)

**Scope:** A focused reliability repair after [Turn 26](seo-geo-turn26-gsc-period-comparison-2026-11-19.md). No new search-performance observations, schema, canonical URL, article or tracking mechanism.

## Verified problem and fix

The previous release correctly merged `downloads/gsc-period-compare.py`, but its test `_tests/test_gsc_period_compare.py` resolved the script using `Path(__file__).with_name("gsc-period-compare.py")`. That works when the two files are temporarily placed in one directory, as in the prior isolated test workspace, but fails with `FileNotFoundError` in the committed repository where tests live under `_tests/` and downloads live under `downloads/`.

The failure was reproduced using the actual two files in that repository-shaped local layout, with `python -m unittest discover -s _tests -p 'test_gsc_period_compare.py' -v`: 1 failed test-module import, zero tests executed. The corrected import uses `ROOT = Path(__file__).resolve().parents[1]` and `MODULE = ROOT / "downloads" / "gsc-period-compare.py"`. The same command then ran all **9** existing comparator regression tests successfully, with no application-code changes.

The prior release also omitted the new download from the explicit public target list in `_scripts/check_live.py`. Registering `downloads/gsc-period-compare.py` makes the existing read-only `targets()` routine expect HTTP 200 and the exact committed bytes. A new four-test suite checks file presence, AST registration exactly once, repo-root import consistency, and the command-line help interface.

## Public retrieval observations and limits

The main homepage and a pre-existing CSV download were successfully retrieved from `nolankido.com` on November 19. The raw GitHub URL for the new Python script was also retrieved successfully. The page-reading service returned `target_unreachable` for both the new Python download and an older `.py` download, so this result cannot by itself establish whether the custom domain serves the new script with HTTP 200, returns a download instead of readable text, or has a genuine error. Do not report these as proven 404s or as successful live-byte comparisons.

The repository README now provides a raw GitHub fallback for retrieving the source. The existing authoritative Python release checker can give a decisive status and body-byte result when run in a network-enabled environment. **No production status has yet been asserted from that check during this turn.**

## Regression scope

The new file `_tests/test_turn27_gsc_distribution.py` tests:
- The comparator exists and compiles at `downloads/gsc-period-compare.py`.
- The existing `check_live.targets()` source registers its download exactly once for HTTP 200 and byte-for-byte checking.
- The existing nine comparator tests import from the repository root rather than from beside themselves.
- The command-line help works when invoked with the repository as the current directory.

In a repository-shaped local fixture after applying the exact intended edits: **13/13 focused tests passed**, including all nine Turn 26 comparator tests and four Turn 27 distribution tests. The local fixture contained the real comparator and existing comparator test, plus the updated release-inventory registration fragment, not a complete checkout of the repository. The full-site build, browser checks, whole historical test suite and live-byte verifier were **not** run and are not represented as passing. The unchanged comparator is still standard-library-only and offline.

## Safety and next step

No GitHub Actions, paid service, remote collection, cron, search tracking code or personal performance export was added. The new release-check inventory is a read-only manual test, not an automated deployment trigger. For a definitive custom-domain check, run `python _scripts/check_live.py` from a complete working checkout in a network-enabled environment, or specifically fetch `https://nolankido.com/downloads/gsc-period-compare.py` as bytes and compare with `downloads/gsc-period-compare.py`. Do not conflate an extraction tool's failure on a Python download with a server HTTP response.

This repair improves trustworthiness of the site's measurement tooling, but it does not establish increased Google clicks, rankings, AI citations or referrals.
