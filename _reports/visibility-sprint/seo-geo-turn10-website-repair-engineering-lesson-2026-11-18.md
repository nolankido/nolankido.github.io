# SEO/GEO Turn 10: turn an archived HTML5 repair into a source-verifiable engineering lesson

**Prepared:** November 18, 2026
**Base:** main after Turn 09, merged in pull request 381
**Purpose:** Strengthen an existing recorded case, not create another unsupported AI success story.

## Why this turn

The original sprint's Turn 10 calls for a reproducible engineering account of an AI-assisted website repair: the specific defect, the check that caught it, and why other passing tests did not settle HTML correctness. The site already had a detailed October 11 case and a reduced checker. This turn makes its public source evidence independently inspectable, upgrades the checker to require the **specific historical HTML5 error class**, and makes its method reusable on one local built page.

It does not claim a real AI productivity advantage, a complete historical release replay, higher search rankings, indexing, or additional AI citations.

## Directly checked historical source

I fetched the two pinned public versions of \`_source/technology/task-brief.html\` from the GitHub repository on November 18:

| Pre-repair source | Repaired source |
| --- | --- |
| [Commit 2bf8908](https://github.com/nolankido/nolankido.github.io/blob/2bf8908339e06f604cea00f0254494e17171ecf4/_source/technology/task-brief.html) | [Commit 73782ca](https://github.com/nolankido/nolankido.github.io/blob/73782caa4697204690c679626b36427c28201234/_source/technology/task-brief.html) |
| Blob \`5d82e36b892d8bb31c325c1afa9ded90cd233712\` | Blob \`33dc068bb75bcaf2ac21ec29dfed5d62b4bccf09\` |
| Final line \`</div></div></section>\` | Final line \`</div></section>\` |

The [actual repair comparison](https://github.com/nolankido/nolankido.github.io/compare/2bf8908339e06f604cea00f0254494e17171ecf4...73782caa4697204690c679626b36427c28201234) contains this one-tag removal from source and generated HTML, along with other changes. The pre-repair commit is a pinned state, **not** necessarily the commit that first introduced the error.

The earlier 347 passing tests, subsequent 21 browser suites and 235 matching public GET targets come from the existing archived release evidence, now separated explicitly from the direct source verification. I did not rerun those historical suites or retrieve a new production measurement. The compact [public evidence ledger](../../downloads/website-check-evidence.json) now records the pinned source path, both file blob hashes, exact final lines and the provenance boundary.

## Public changes

1. The existing [website-repair case](https://nolankido.com/technology/checking-ai-website-changes/#case-source-diff) gains a separately labeled exact source comparison and links to both public file revisions. Its original description, recorded run claims and publication date remain intact.
2. The revised [offline Python reproduction](../../downloads/website-check-reproduction.py) now treats only an \`end-tag-too-early\` error on \`div\` as success for its negative control. It still requires the corrected fixture to have zero errors. Its output is structured JSON.
3. The same script adds \`--file path/to/built/index.html\` to check any one local UTF-8 HTML file with the HTML5 parser. It reads the named file, makes no external requests and writes no files. Exit 0 means no parser errors; exit 1 means parser errors; exit 2 means the file was unreadable. It does not claim to test browser behavior.
4. A downloadable [offline release runbook](../../downloads/website-check-offline-runbook.md) gives a portable negative-control procedure, this site's source/build/search/HTML/link commands, a gate-versus-limitation table, and a blank private review record.
5. The Technology hub now offers a contextual deep link to the source repair. The new runbook is registered as a public download in \`_scripts/check_live.py\`.
6. Five new local tests verify the error code, positive/negative local-file behavior, unreadable-file exit, evidence ledger consistency, article source/build anchors and public download registration.

No old GitHub Actions workflow was restored. All checks in this turn are local.

## Verification

| Check | Result | Scope |
| --- | --- | --- |
| Script, embedded negative control | PASS | Detects \`end-tag-too-early\` / \`div\`, accepts corrected fixture |
| Script, built case HTML | PASS | One actual generated page, no HTML5 parser errors |
| Turn 10 regression tests | 5 passed | Exact negative control, file mode, ledger, page and downloads |
| Main site deterministic build | 253 generated files checked, 0 changes | Local generated outputs, not live site |
| Public internal links | 231 HTML pages, 16,125 occurrences, 0 issues | Registered local targets, not HTTP responses |
| Search metadata | 224 sitemap URLs, no errors | Local descriptions/canonicals, not indexing |
| HTML5 suite | 229 checked pages, no failures | Parser validity, not accessibility or function |

The final checked output includes the contextual Technology-hub link, the exact-source section and the portable download. The source/HTML rebuild required three generated-page changes across the two edits; the subsequent deterministic check reported zero remaining changes.

## Boundaries and outstanding checks

- This exercise was a **source-verification and publication-quality improvement**, not a new measured AI experiment.
- The reduced fixture is intentionally tiny and reproduces the same parser error class, not the entire historical site or CI environment.
- The original historical tests, browser suites and deployed byte comparisons were not rerun in this turn.
- The comprehensive legacy unit suite contains unrelated stale fixtures and Git-history assumptions reported in Turn 09, so the focused five-test pass does not certify that full suite.
- No 320-pixel browser visual audit or new production GET comparison has yet been completed. The public live page should be checked after deployment.
- No Google indexing, ranking, click-through or assistant-citation result was measured.

**Handoff:** Follow the saved 25-turn roadmap for the next sprint priority. Maintain the no-GitHub-Actions restriction and the source-ledger separation between verified code, archived outcomes and unknown search performance.
