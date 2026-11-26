# SEO/GEO Turn 112: fail-closed local release preparation

November 24, 2026. Parent: f585bee3e5ab295f9f0e2a30101a464e456dd4b0.

The consolidated draft still has a stale generated search audit snapshot. A complete checkout was not available because GitHub DNS/download access failed in the local container. The new helper _scripts/prepare_local_release.py calls the existing builders and HTML5 checker, generates the actual SEO report into a temporary directory, independently rechecks its snapshot parity, and only with --apply promotes the passing report and invokes the existing full local regression/browser runner. On a failing release check the original report is restored when it is safe to do so. Concurrent edits are not intentionally overwritten. No automatic merge, deployment, network action or GitHub Actions workflow is added.

Actual local evidence: all 15 test methods in test_turn112_prepare_local_release.py passed in normal Python and again under -OO (30 executions). These are isolated fixtures including subprocess success/failure orchestration, not executions of the full website audit. The exact third book page was reconstructed byte-for-byte and verified against Git blob bfda8721d2c1b54b44c58129bf94ac77696b2aa4. The installed vendored HTML5 parser returned zero errors. Browser smoke navigation was blocked by administrator policy, so no browser pass is asserted. The tested script and test blob hashes are 858d8d8b77eb91b328c9f863eeb5cd99fc2b8008 and 588010320cca80743ef2c73f493438e522e4dad4.

On a complete isolated checkout of this branch, with its test dependencies installed:

python _scripts/prepare_local_release.py --apply

Review any failed check and fix the underlying files. If successful, inspect the generated audit diff and commit it before reviewing and merging the draft. The default without --apply is read-only and returns 2 for verified report drift. A default return of 0 means report parity, not full release validation.

The existing audit snapshot is intentionally unchanged. The full deterministic build, real SEO audit, full browser/regression suite and production publication remain pending. No change to live SEO performance or measured AI citations is asserted.
