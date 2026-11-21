# SEO/GEO Turn 64: prevent false zero Google AI impressions in the private scorecard

**Review date:** November 21, 2026 (Pacific/Honolulu)  
**Starting main:** `49e08e693247249e7c7cfbb58db6115f7caf6edf`, merged Turn 63, PR #437  
**Public helper:** https://nolankido.com/downloads/visibility-private-scorecard.py  
**Primary documentation:** [Google Search Console, Generative AI performance report (Search)](https://support.google.com/webmasters/answer/16984139)  
**Scope:** Strengthen factual visibility measurement, not claim new rankings or publish private account data.

## Verified problem

The existing offline `downloads/visibility-private-scorecard.py` correctly distinguished a missing source from an observed count and verified the property/date flags. **However, it accepted a Google AI Search impression value of `0` as `observed_operator_confirmed` based only on a generic `period_verified: true` attestation.** The previous unit-test fixture even treated this unqualified zero as acceptable.

Google's official documentation explicitly states that values displayed as `~` or `-` in the Generative AI performance report are exported as numeric zeros. A zero copied from such an export is therefore ambiguous, even when the property and month are correct. This is a genuine **measurement-integrity** weakness, not a claim that NolanKido.com has zero AI impressions.

The same conservative rule is now applied to the separate Google AI Discover impression input, rather than making a risky inference about its availability from a zero-valued export. Bing citation counts, standard Google Web charts and Umami referral counts remain separate, with their own source assumptions.

## Changes

1. **`downloads/visibility-private-scorecard.py`** identifies Google AI Search and Google AI Discover impression inputs separately from Web search, Bing AI and Umami. When an AI `observed` value is the numeric integer zero, intake now requires the exact private field `"display_zero_confirmed": true`. That field means the operator directly inspected the original Search Console display and saw an actual numeric `0`, not an unavailable `~` or `-` that a CSV converted to zero.
2. Missing, false, string or non-boolean zero-display confirmations fail closed. Positive Google AI counts retain the original four observed fields. An accidental zero flag on a positive entry fails closed rather than silently changing the schema.
3. The direct `make_scorecard()` helper enforces the same Google AI zero requirement, preventing programmatic callers from bypassing `read_dashboard()`. All original privacy, property/month validation, no-network and separate-series boundaries remain.
4. **`_tests/test_visibility_private_scorecard.py`** revises the old false-zero fixture, adds both report types and adversarial inputs, protects real numeric zero and positive inputs, verifies unavailable stays `null`, and ensures Bing/Umami zeros do not inherit Google-specific fields. No new test runner is required: this test module is already part of the manual `_scripts/local_release_checks.py`.
5. **`seo-geo-measurement-v1.md`** is updated to v1.1 with a source-linked practical interpretation rule for operator-owned private exports. Actual raw exports, screenshots and filled scorecards remain outside this public repository.

## Private input examples, illustrative only

The following are **fictional shapes, not observations of this site**:

```json
{
  "month": "2026-10",
  "metrics": {
    "gsc_ai_search_impressions": {
      "status": "unavailable"
    },
    "gsc_ai_discover_impressions": {
      "status": "observed",
      "value": 0,
      "property": "sc-domain:nolankido.com",
      "period_verified": true,
      "display_zero_confirmed": true
    }
  }
}
```

The second value is acceptable **only** when the operator has inspected a genuine numeric zero in the corresponding original report. When that proof is missing, `unavailable` is the correct record. A positive integer retains the previous schema and does not need the extra field. The offline program does not independently authenticate a dashboard session.

## Preflight and open gates

**Completed this turn:** reviewed the current repository code, official Search Console documentation, legacy unit cases and private measurement protocol; patched the existing public offline helper; added focused test cases; ran an isolated local Python exercise of the exact zero/positive branching to check two Google AI input types, valid/invalid zero confirmations and unaffected Bing zero handling.

**Not completed this turn:** no full repository checkout was available in the execution container because GitHub DNS resolution failed. The actual repository `unittest` suite, historical test suite, deterministic build, HTML5 parser, mobile/browser testing and status-bearing exact-byte production checks were **not run**. The isolated Python exercise is not a substitute for those checks. Publication should be verified from a full checkout with network access, and any release-test failure investigated.

After merge, the appropriate local commands are:

```powershell
py -3 -m unittest discover -s _tests -p test_visibility_private_scorecard.py -v
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /downloads/visibility-private-scorecard.py --attempts 3 --interval 5
```

No user-authored GitHub Actions, new scheduler, dashboard vendor, paid API, tracking change, private analytics export or site canonical page was introduced.

## Result and next turn

This improvement reduces the risk that a future website SEO/GEO review will misreport a blank or suppressed Google AI impressions cell as an actual zero. **It does not establish any measured NolanKido.com impressions, Google indexing, assistant citations, ranking increase, clicks, or causal effect.** December remains the first full calendar month after the November sprint; its performance values remain future until December has ended and data settle.

The next highest-priority outcome is still a full executable release pass, followed by first-party Google/Bing/Umami reports and actual query/page-based content prioritization when those private source reports are legitimately accessible. Do not infer a search-impact improvement from this code change.
