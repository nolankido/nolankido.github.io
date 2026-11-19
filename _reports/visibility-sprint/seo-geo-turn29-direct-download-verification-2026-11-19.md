# SEO/GEO/AEO visibility follow-on, Turn 29: directly check a published download

**Date:** November 19, 2026 (Pacific/Honolulu)

**Repository:** `nolankido/nolankido.github.io`

**Pinned comparator source:** `downloads/gsc-period-compare.py` at commit `b0a419f51096df3b7b12ee471edb09a5e2aa4312`.

**Expected SHA-256:** `805be287f6e57906e1be096a3a806e58fe1cd7eabc7484d0f311f2cbc3417da7`.

## Verified evidence before the change

Turn 26 created a no-cost, offline comparator for two private Search Console monthly JSON summaries. Turn 27 repaired the test import and registered the download in the existing live-file inventory. Turn 28 added a scoped manual public checker. The custom-domain deployment receipt remained inconclusive.

On November 19 an independent site fetch successfully identified the **November 19 sprint closeout section** at `https://nolankido.com/technology/ai-website-visibility/#site-visibility-sprint-outcome`. Therefore the website should **not** be described as globally stale merely because the earlier generic text extraction omitted the section.

A browser-like tool displayed a not-found page for the comparator, an older `.py` file, and a CSV control. Another site retrieval succeeded in reading that CSV and reported the Python files as unreachable. This contradictory evidence does not establish a trustworthy response status for the comparator. A direct `curl` from the available model container failed **before HTTP**, with `curl: (6) Could not resolve host: nolankido.com`. No claim that the custom domain returned HTTP 404 or HTTP 200 is supported by that attempt.

## Implementation

Added `downloads/gsc-download-verify.py`, a stand-alone Python standard-library diagnostic that does **not** require a local website checkout. The script makes two read-only GET requests, each limited to a fixed HTTPS URL: the public comparator on `nolankido.com` and the exact comparator in the pinned GitHub commit at `raw.githubusercontent.com`. It never runs downloaded code, posts data, collects credentials, logs private Search Console records or writes files.

The script computes SHA-256 on response bytes (maximum 256 KiB) and checks the public response against the frozen expected digest. It clearly separates:
- `site_verified`, exit 0: HTTP 200 and exact expected bytes.
- `site_does_not_match_pinned_release`, exit 1: observed non-200 response, byte mismatch or excessive response size.
- `site_status_inconclusive`, exit 2: DNS, network or unsafe-redirect error prevented a decisive public-site result.

The pinned GitHub control is **informational**, and cannot turn a failed live-site response into a passing result. Only same-origin HTTPS redirects are accepted for either request. The two URLs and expected hash are hardcoded; there is no arbitrary URL or private-input parameter.

In a complete local repository the manual, full-inventory release checker now includes the new downloadable diagnostic script as an expected HTTP 200 and byte-equal static target. The README links to the raw GitHub script as a fallback and gives a short run command.

## Exact use

On Windows, download the source from `https://raw.githubusercontent.com/nolankido/nolankido.github.io/main/downloads/gsc-download-verify.py` and inspect it. Save it as `gsc-download-verify.py`, then run this command in PowerShell from the directory where you saved it:

```powershell
py -3 .\gsc-download-verify.py
```

From a complete checkout, use:

```powershell
py -3 .\downloads\gsc-download-verify.py
```

The diagnostic prints JSON that includes the actual HTTP status when one was observed, expected hash, received hash when available, control result, and exit code. Do not upload actual private Search Console exports or responses to this public repository.

The checker is pinned to the Turn 26 comparator. If the comparator is deliberately revised later, update the expected hash and its tests with an explicit source revision; otherwise a legitimate content change will be reported as a mismatch.

## Verification and limitations

- The SHA-256 embedded in the diagnostic matched the **actual frozen comparator file** in the local Turn 28 test fixture, whose Git blob ID matched the stored `main` source.
- The checker and its tests were placed in the intended `downloads/` and `_tests/` directory structure.
- **11 of 11** offline `unittest` tests passed, including pinned SHA, matching HTTP 200, byte mismatch, observed HTTP 404, DNS failure, body cap, URL allowlist, cross-origin and HTTPS-downgrade redirects, and failure isolation from the pinned GitHub control.
- A real invocation from the model's container returned `site_status_inconclusive` with `network_unavailable` and exit code 2 because that environment could not resolve the domain. This is a limitation of the test environment, not a measured production 404.
- The full website static generator, full regression suite, and live HTTP release checker were **not** executed in this turn. The repository change affects only documentation, a new downloadable Python script, its tests and release inventory, not public HTML/templates or SEO metadata.

**Not measured:** Google Search Console clicks or impressions, AI Overview appearances, ChatGPT citations, assistant referrals or business outcomes. A download check is not a visibility study.

No GitHub Actions, scheduled checks, paid service, external dependency, new analytics tracking or credential access was introduced.
