# SEO/GEO Turn 115: isolated deterministic release rebuild

November 24, 2026. Parent: 7d2fddae0b6b4ddfd4f3e7d692cebac536e192a4.

The release preparation command checks generated output before writing its audit. That is correct for a committed release but cannot repair build drift introduced during connector-only editing. The new _scripts/rebuild_release_candidate.py creates a detached local Git worktree at the exact committed HEAD in a new directory outside the current checkout. It regenerates the book and site outputs using the actual existing builders, then invokes prepare_local_release.py --apply, which retains the actual passing audit only after full validation. On failure the worktree is retained for diagnosis. Uncommitted edits are excluded, and the existing working tree is not edited. No fetch, push, commit, merge, deployment, GitHub Actions or paid service is added.

Actual local tests: 7 test methods passed using real local Git worktrees and synthetic build/release subprocesses, both with ordinary Python and -OO (14 executions). Tested blob hashes: helper c050839a436f2010d10dbf712b7c5176621d07d7 and test 3549a5fc9f3f97d8941dbc73bdb201e79a513e15. The test exercises success and detached revision identity, dirty checkout preservation, builder failure, release failure, existing destination, nested destination, missing parent and wrong root. These are not real full-site build results.

Reconciled two older current identity regressions (Turns 20 and 23) with the actual manifest and sitemap. Preserve their evidence and original publication date, require revision dates no earlier than the original reviewed dates, and check current structured/article and sitemap revision consistency rather than requiring all future changes to keep the November 19 date. 17 connector structural and exact-edit checks passed before committing these changes.

From a complete local checkout of the intended draft branch, with test dependencies installed, choose a new sibling directory:
    python _scripts/rebuild_release_candidate.py --worktree ../nolankido-release-candidate

Inspect the candidate's status and actual generated changes. The command does not modify the original branch or automatically commit anything. Review and commit validated output before merge. If the original generated files already match, the earlier prepare_local_release.py --apply remains suitable.

GitHub DNS remains unavailable in the current execution container (git ls-remote returned Could not resolve host: github.com). The actual full-site build, search-audit snapshot regeneration, all current and archival tests, browser checks and live exact-byte release verification remain outstanding. Do not claim production or ranking/citation gains. Keep the PR draft until real checks pass.
