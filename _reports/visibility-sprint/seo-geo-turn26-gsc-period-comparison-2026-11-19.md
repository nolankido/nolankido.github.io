# SEO/GEO/AEO improvement, Turn 26: reliable private Search Console comparisons

**Date:** November 19, 2026 (Pacific/Honolulu)

**Resource:** https://nolankido.com/downloads/gsc-period-compare.py

**Baseline:** The 25-turn sprint closed with verified publication but no authenticated Search Console performance export. The connected GSC Wizard service returned `payment_required` because its trial had ended. This turn does not purchase a subscription or claim observed search results.

## Concrete improvement

A new Python standard-library-only command compares two **private** JSON summaries already produced by `downloads/gsc-monthly-local-audit.py`. The existing monthly checker is unchanged. This gives the monthly scorecard a reusable, no-cost comparison step once the owner has genuine Search Console exports.

The program:
- Requires an explicit exact site property (`sc-domain:nolankido.com` or `https://nolankido.com/`), plus `--same-filters-confirmed`; the confirmation is made by the operator, not independently verified by the program.
- Rejects reversed months, future or incomplete calendar months, malformed summary dates, mismatched chart totals, invalid types and incoherent page/query export statuses.
- Compares property Web clicks and impressions only when complete daily Chart rows were validated in both underlying summaries. It refuses to substitute Pages-table sums for property totals.
- Separately labels observed exported section-click counts, visible branded query clicks and visible query/page nonbrand technology clicks. The latter can be missing even if other metrics are present.
- Leaves missing data as `null`, never zero; with a zero baseline, absolute change may be calculated but percentage change is `null`.
- Calculates calendar-day-normalized property totals for interpretation of months with different lengths.
- Prints only aggregate comparison JSON to standard output and never writes files, reads the network, or copies raw queries or page URLs into its output.

The script cannot verify the original Search Console property, UI filters, country, device, data freshness or export completeness from JSON alone. It makes no claims about Google AI Overviews, ChatGPT/Bing citations, rankings, indexing, or causal SEO lift.

## Private-use example

First generate two owner-only monthly summaries using the existing checker and true, complete Search Console exports. On Windows PowerShell, with these private files stored in Documents:

```powershell
py -3 .\downloads\gsc-period-compare.py --baseline "$env:USERPROFILE\Documents\gsc-2026-10-private.json" --followup "$env:USERPROFILE\Documents\gsc-2026-12-private.json" --property "sc-domain:nolankido.com" --same-filters-confirmed > "$env:USERPROFILE\Documents\gsc-oct-dec-private-comparison.json"
```

Run the October-to-December example only **after December ends**, its data settles and the operator verifies identical Search Console property, search type, device, country, filters and reporting completeness. October is presprint, November is a mixed transition month, and December is the first complete postsprint calendar month. A difference does not demonstrate that the sprint caused it. Keep the generated private JSON and all raw exports out of this repository and public issues.

## Verification

- Local test file: `_tests/test_gsc_period_compare.py`.
- Nine Python `unittest` regression tests passed on fictional JSON summaries, including missing chart totals, zero baselines, future months, filter confirmation, and manipulated counts.
- The tested Python file's Git blob SHA is `ce44611f64d0196d779a5f3b33679201dd31210a`; the test file's Git blob SHA is `c96d174e7d341c72b8bf0e455bff3c32e3612253`.
- This addition does not alter site metadata, canonical URLs, the static page generator, the old monthly checker or the frozen assistant prompt panels. Existing full static-site checks were not rerun because no generated page or template changes were made.
- Publication via GitHub and public file retrieval require separate confirmation after merge.

## Source guidance

Google documents the distinction between property totals and Page-table grouping, filtering differences, privacy-limited query rows and exported unavailable values: https://support.google.com/webmasters/answer/7576553 and https://support.google.com/webmasters/answer/12919797 . Reporting delays and date grouping are also documented: https://support.google.com/webmasters/answer/17010575 .
