# SEO/GEO Turn 62: close a real HTML5 release-inventory gap

**Review date:** November 20, 2026 (Pacific/Honolulu)
**Starting `main`:** `f3c82e4fa30d04fe62306c59bb7b626a55a9b428` (merged Turn 61, PR #435)
**Canonical resource:** https://nolankido.com/poker/10bb/
**Risk class:** Release validation. No visitor-facing copy, date, schema, stylesheet, article, canonical URL or sitemap change.

## Why this improvement is needed

Turn 61 identified that the full local release suite was not executable from a complete checkout in the connector/container environment. This turn inspected the *actual* Python release inventory to find a narrower, provable gap rather than writing another generic release checklist.

The current sitemap has 230 URLs. The standalone **10 Big Blind Tournament Playbook** has a separately maintained public file `poker/10bb/index.html` and is correctly registered by `_scripts/tenbb_companion.py` for sitemap inclusion and by `_scripts/check_live.py` for exact-byte production checks. Its math/provenance tests already exist in `_tests/test_turn52_10bb_playbook.py`.

However, before Turn 62, `_tests/check_html5.py` `publication_paths()` included all 225 manifest pages, six other standalone manual HTML pages, two author book pages and the book catalog, **but omitted the 10 BB Playbook**. The historical release test explicitly assumed `len(pages) + 9` HTML5 targets. A malformed closing tag on the standalone 10 BB page could therefore escape the HTML5 release inventory even though the page was in the sitemap and download/live inventory.

This is a confirmed **test coverage defect**, not evidence that the currently published 10 BB page itself is malformed.

## Concrete code correction

1. **`_tests/check_html5.py`:** Call the existing `tenbb_companion.record(root)` fail-closed publication validator, reject a duplicate canonical route, and include its exact `tenbb_companion.OUTPUT` in `publication_paths()`. No second registry or content authoring was added.
2. **`_tests/test_turn34_release_integrity.py`:** Update the static HTML5 page inventory assertion from `len(manifest) + 9` to `len(manifest) + 10` and explicitly parse the 10 BB page as part of the existing regression.
3. **`_tests/test_turn62_html5_tenbb.py`:** Add a focused contract verifying complete inventory, independent route equality with canonical HTML in the production target registry, the public page's HTML5 parsing, negative detection of an extra closing tag, rejection of duplicate 10 BB routes, and registration in the local release runner.
4. **`_scripts/local_release_checks.py`:** Run the new focused test during the default local checklist, followed by the existing full HTML5 checker. No remote CI or schedule.
5. **`AGENTS.md`:** Correct the stale standalone count and document the actual ten standalone pages covered by HTML5 checking.

**Expected new complete HTML5 scope:** 225 manifest-backed pages (including the five intentional noindex utility pages) + ten independent HTML pages = **235 HTML documents**. This is a source-inventory expectation, **not** a claim that 235 validators ran or that all 235 URLs are indexable.

## Evidence observed in this turn

- Repository `main` was pinned to `f3c82e4fa30d04fe62306c59bb7b626a55a9b428` before the fix.
- Read-only full recursive Git tree was retrieved, not truncated. No repository-authored GitHub Actions workflows were added.
- Prechange `_tests/check_html5.py` lacked any `tenbb_companion` import or registration, while `_scripts/check_live.py` did contain it. Historical test code expected only nine extra HTML documents.
- Prechange public `poker/10bb/index.html` is a single manually authored HTML document with one `<main>` and one `</main>`, and the existing Turn 52 evidence check preserves its route. A separate source-level lexical scan found balanced and correctly nested tracked block tags on the 10 BB public file (including main, article, section, table and div). This narrow check does not replace an HTML5 parser.
- A bounded separate Git-tree link-target audit examined **22 selected public HTML pages** (Home, About, Technology, AI portfolio, three book pages, Poker, 10 BB, three current poker study pages, Contact, a video companion, website-repair case, Start Here, Resources, Projects, Poker Library, two topic indexes and Bio). It processed **1,992 internal-anchor references**, checked target-path presence in the committed Git tree, and checked same-document hash IDs. No missing target or same-document fragment was found in this sample. This static regex check does **not** cover cross-document fragment IDs, runtime navigation, actual HTTP status or all site pages; `_scripts/check_internal_links.py` is the authoritative full offline check.

## Verification status and limitations

**Source-level inspection:** The problem and correct registry target were confirmed against the real connector-fetched code; postchange branch static tests review paths, identifiers, duplicate protection and no-workflow rules.

**Local executable tests:** **Not run in this session**. The execution container still fails DNS resolution of `github.com`, `raw.githubusercontent.com` and `nolankido.com`, so it cannot clone a complete checkout or perform repository-relative HTML5 and full release checks. `html5lib` is also not installed in that container. Do not interpret this as a passing HTML5 parse, a successful production byte comparison, or a known site failure.

From a full local checkout of the merged commit with `requirements-test.txt` installed, execute:

```powershell
py -3 -m unittest discover -s _tests -p test_turn62_html5_tenbb.py -v
py -3 -m unittest discover -s _tests -p test_turn34_release_integrity.py -v
py -3 -m unittest discover -s _tests -p test_turn52_10bb_playbook.py -v
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/build.py --check
py -3 _scripts/build_books.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope priority --attempts 2 --interval 2
```

The exact-byte live test must only be labeled passed if it independently returns a successful byte comparison. Any network or DNS failure is inconclusive, never a declared HTTP 404.

## Exit and next handoff

**Completed by this code turn:** Close the known 10 BB HTML5 registration omission in the repository and add regression guards. This is a concrete improvement to future release coverage, not a traffic or ranking experiment.

**Still open:** Full Python, HTML5, complete link, Playwright, network byte verification and authenticated Search Console/AI citation measurements. The next turn should run the full release gate from a network-capable checkout, fix any actual errors found, and only then call the wider release qualified. No new paid service or GitHub Actions should be enabled.

**Source references:** [Turn 61 scorecard](seo-geo-turn61-release-and-evidence-scorecard-2026-11-20.md), `_tests/check_html5.py`, `_scripts/tenbb_companion.py`, `_scripts/check_live.py`, `_tests/test_turn34_release_integrity.py`, `_tests/test_turn52_10bb_playbook.py`, `_reports/search-audit.json`.
