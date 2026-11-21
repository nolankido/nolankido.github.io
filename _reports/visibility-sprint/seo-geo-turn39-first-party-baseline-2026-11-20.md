# SEO/GEO improvement Turn 39: First-party visibility baseline readiness

**Date:** November 20, 2026 (Pacific/Honolulu)  
**Site:** https://nolankido.com/  
**Starting `main`:** `90d450e95593f6ac6aaaac7d7e19aa9d7fbd1905`  
**Roadmap:** Turn 39 of the 25-turn SEO/GEO sprint, following Turns 37 and 38.

## Result: the data gap is real, not a zero-traffic finding

The task was to establish a first-party baseline for Google Web Search, Google AI appearances, Bing AI citations, and Umami assistant referrals. The accounts' actual performance reports were **not accessible in this session**, so **no observed October or November traffic or citation numbers are published or invented**.

| Metric | First-party source | Turn 39 status | Why not a count |
| --- | --- | --- | --- |
| Google Web Search clicks / impressions | Google Search Console property Web Search chart | `not_collected` | Authenticated first-party export absent |
| Practical-AI landing page clicks | GSC Web Pages export, `/technology/` scope | `not_collected` | No owner report |
| Google AI Search impressions | GSC Generative AI performance (Search) | `not_collected` | No owner report; not a ChatGPT citation count |
| Google AI Discover impressions | Separate GSC generative Discover report | `not_collected` | No owner report; never add to Web |
| Bing AI visible citations | Bing Webmaster Tools AI Performance | `not_collected` | No owner report; citations are not search clicks |
| Assistant-referred pageviews | Owner Umami Cloud referrer breakdown | `not_collected` | Client tracker exists, but dashboard ingestion and source metrics not inspected |

The configured GSC Wizard service previously returned `payment_required` / `subscription_required` in this project. No further paid tool was enabled. The read-only connected browser had no open authenticated Search Console, Bing Webmaster or Umami tab. A targeted Drive title search did not locate a confirmed current Search Console export or monthly first-party measurement. That does not prove no privately stored data exist elsewhere.

The existing private operational Google Doc mentions Search Console verification as an intended task, but supplies no usable performance counts; it is not being copied or quoted publicly.

## Release and public technical baseline remain separate

At the close of Turn 38 the repository sitemap had 229 unique canonical URL entries, with important pages and book worksheets independently retrievable. Those observations are **technical availability**, not Search Console clicks, Google indexing, Bing citations, or referral sessions.

Use **October 2026** as the presprint month, **November 2026** as the mixed transition month, and **December 2026** as the first full post-sprint month, when those full calendar windows have closed and reporting has settled. Record actual source, time window, filters and export date privately. A future before/after difference is not proof that a site change caused it.

## New implemented capability

Added `downloads/visibility-private-scorecard.py`, a standard-library-only, zero-network tool that combines strict **private aggregates**, without adding an analytics beacon or paid connector. Existing `gsc-monthly-local-audit.py` and `gsc-period-compare.py` remain the source parsers and validators for Google Web Search.

- Missing metrics produce JSON `null` with `status=not_collected`, **never 0**.
- A dashboard metric may be `unavailable` (value null) or `observed` (nonnegative integer count), but an observed count requires an **explicit confirmed month, correct site/property and verified date window**.
- Google Search impressions, Google AI Search and Discover impressions, Bing AI citations, and Umami assistant-referrer pageviews retain **different metric keys and cannot be added as one score**.
- GSC Web measures can only enter as observed values with an explicitly specified valid site property and a separate operator assertion that the original property, Web search filters and dates were checked. No local tool can verify that assertion remotely.
- Existing validated GSC summary is inspected via the strict local comparator, not by joining Pages and Queries tables or summing incomplete page rows.
- Input JSON may not contain extra keys for raw queries, page-level data or personally identifying records. Any parse error is generic and does not echo the private file path or its contents. The tool makes **no** network requests, creates **no** local files and writes only minimal aggregate JSON to stdout. The owner should redirect output to a private location **outside** GitHub.
- Added `_tests/test_visibility_private_scorecard.py` containing 10 focused offline tests for missing-versus-zero, period/property validation, unsupported data, GSC confirmation, rejection of extra fields, redacted parse errors and CLI output.
- Updated `_scripts/local_release_checks.py` to require those tests, `_scripts/check_live.py` to include the new public tool in exact-byte release targets, `.gitignore` to exclude local private analytics directories and `ANALYTICS.md` to document the boundary.

### Usage without any account connection

From a checkout, this generates an **unmeasured, nullable status** for October. Its output must stay private:

```powershell
py -3 downloads/visibility-private-scorecard.py --month 2026-10 > "$env:USERPROFILE\Documents\visibility-private-2026-10.json"
```

After owner-authorized GSC Web CSV exports have been converted by the existing monthly parser, and **after confirming filters in the original dashboard**, run:

```powershell
py -3 downloads/visibility-private-scorecard.py --month 2026-10 --gsc-summary "$env:USERPROFILE\Documents\gsc-2026-10-private.json" --gsc-property sc-domain:nolankido.com --gsc-filters-confirmed --dashboard-json "$env:USERPROFILE\Documents\dashboard-2026-10-private.json" > "$env:USERPROFILE\Documents\visibility-private-2026-10.json"
```

The dashboard JSON's only allowed structure is a `month` and `metrics` object. Its metric keys may be `gsc_ai_search_impressions`, `gsc_ai_discover_impressions`, `bing_ai_citations`, or `umami_ai_referral_pageviews`.

Each missing report may use:

```json
{"status":"unavailable"}
```

A genuinely observed count uses:

```json
{"status":"observed","value":<integer count>,"property":"<verified source property>","period_verified":true}
```

The `property` must be exactly `sc-domain:nolankido.com` or `https://nolankido.com/` for GSC, `https://nolankido.com/` or `https://nolankido.com` for Bing, and `nolankido.com` for Umami. The tool validates syntax and operator attestations, **not** the private source dashboards themselves.

## Verification and limits

- The new isolated Python source and 10 synthetic negative-control/CLI tests **passed 10/10** in the available local execution environment. It does not contain the complete website checkout or owner dashboards.
- The local no-input October run produced all nullable values as intended, with no fabricated count.
- The full repository's Python tests, HTML5 and browser suites could not run here because a direct GitHub checkout was unavailable. Their execution must not be claimed.
- The standard release verifier registers the new download's expected exact bytes, but a **successful public custom-domain response** has not been independently confirmed for this new tool.
- No first-party October or November traffic metrics have been measured. No source-export data or private scorecard results have been committed to the public repository.

## Next turn

**Turn 40:** Run the previously frozen 25-question assistant-answer panel (20 nonbranded and five branded) in a consistent protocol, record genuine clickable site citations and correct identity associations, and distinguish those manual observations from Google Search and Bing's independent dashboards. An incomplete or unavailable panel is a partially observed sample, not a zero citation rate.

## Primary methodological references

- Google Search Console export limitations: https://support.google.com/webmasters/answer/12919797
- Bing AI Performance definitions: https://www.bing.com/webmasters/help/?topicid=9f8e7d6c
- Existing measurement protocol: [seo-geo-measurement-v1.md](seo-geo-measurement-v1.md)
- Existing Google offline tools: `downloads/gsc-monthly-local-audit.py` and `downloads/gsc-period-compare.py`
- Site analytics configuration: `ANALYTICS.md`

No GitHub Actions, background task, cron, paid APIs, new trackers, personal account data, or raw performance exports were added.
