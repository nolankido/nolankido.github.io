# SEO and GEO Measurement Protocol

Version 1.0 | October 29, 2026 | Site: https://nolankido.com/

## Purpose and ownership

Measure whether the site is becoming easier to discover by people searching for practical AI in everyday life and small-business work, and whether assistants correctly associate Nolan Kido with **AI Works Human Decides**. Track Poker and Living Well separately so success in those areas cannot be mistaken for growth in practical-AI discovery.

This is a public *methodology*. Store actual Search Console, Umami, referrer, private query, contact, or AI-response records in an owner-controlled private document or spreadsheet, **not in this public repository**. A report under `_reports/` is still public on GitHub.

Do not install a second tracker, add a paid API, initiate GitHub Actions, or change privacy/tracking settings just to collect more data.

## The four primary monthly measures

| Metric | Source | Definition | What it tells us |
| --- | --- | --- | --- |
| Practical-AI search clicks | Google Search Console, Search results, Web, Pages | Sum clicks for canonical pages whose URL starts `https://nolankido.com/technology/`. Keep the total by page; do not claim it is unique sitewide searchers. | Whether people reach practical-AI work from Google Search |
| Google generative-AI appearances | Search Console, **Generative AI performance (Search)** | Property-level impressions for AI Overviews and AI Mode in the complete calendar month. Record whether the report is available. | How often Google showed a site URL in its generative answers |
| Assistant-referred pageviews | Umami Cloud, referrers | Pageviews attributed to versioned, known assistant referrer domains (listed below); same month. Record any unavailable source breakdown as missing. | Known assistant traffic that reaches the site |
| Nonbrand assistant citation rate | Fixed, reproducible prompt panel | Number of completed unbranded prompt-engine trials that link to an actual `nolankido.com` URL divided by completed eligible trials. Record numerator and denominator. | Sampled visibility in assistants other than Google's GSC report |

These are **four separate series**, not a single invented "GEO score." Search Console AI impressions, Umami referrals, and sampled citations measure different populations. Never add them.

## Supporting measures

| Metric | Source / definition | Frequency |
| --- | --- | --- |
| Total Web search clicks and impressions | Search Console Search results property-level chart, Web. Do not replace with a sum of page rows. | Monthly |
| Visible nonbranded practical-AI clicks | Search Console Query + Page export, `/technology/` pages, excluding identifiable name/domain/tagline queries. Query privacy exclusions mean this is a **visible-query lower bound**, not an exact all-search nonbrand count. | Monthly |
| Person-name and tagline discovery | Search Console visible queries containing Nolan Kido, Nolan Y. Kido, nolankido, or the full phrase AI Works Human Decides. Keep person-name and phrase as two categories. | Monthly |
| Other sections | Web search clicks by `/poker/`, `/living-well/`, `/creative/`, and an Other bucket. | Monthly |
| Google generative-AI top pages | Top pages by impressions in the Search generative-AI report, preserving its page-level aggregation. | Monthly |
| Discover generative-AI appearances | Separate Search Console **Generative AI performance (Discover)** total if shown. Never add to the Search figure or call it Web traffic. | Monthly |
| Branded answer accuracy | Fixed brand prompts below. Accurate association requires both Nolan Kido and practical AI / human judgment, with the tagline verified when asked. | Monthly |
| Technical discoverability | Current static search audit, sitemap URL count, representative Search Console indexing inspections, Search Console inclusion setting, and newly broken canonical URLs. | Quarterly and after major releases |
| Valuable actions | Genuine contact inquiries, collaborations, links or relevant citations confirmed by their own records. The installed pageview-only Umami configuration does not measure completions. | Monthly when present |

Keep `unknown`, blank, or `not_available` distinct from a measured zero.

## Monthly collection, 15-minute target once access exists

**When:** On the fifth day of each month, review the **entire previous calendar month**, using the same Google Search Console property `sc-domain:nolankido.com` if verified there. Google Search Console reporting can lag; treat provisional late-month numbers as provisional and recheck. Compare with the previous complete month and, once available, the same month a year earlier. Save the raw date range and export date for every source.

1. **Google Search Console, Search results:** Choose the last complete calendar month, search type Web. Record the chart's clicks and impressions. Export Pages and visible Queries. Record practical-AI page clicks, visible brand queries and visible nonbrand practical-AI queries. Keep all raw rows in private storage.
2. **Google Search Console, Generative AI performance (Search):** Export monthly property impressions and the top five Pages. If absent, record `report_unavailable` plus whether Search generative-AI inclusion is enabled. The report can be absent when the site has not received enough impressions. The report offers impressions, not a separate click total or the exact assistant prompts. Record Discover separately when present.
3. **Umami Cloud:** Check the same month for all pageviews, referrer-domain breakdown, and practical-AI landing pages. Sum pageviews attributed to known assistant domains only when the report supports that breakdown. Mark `ingestion_unverified` until the private dashboard confirms data collection.
4. **Prompt panel:** Run the same questions with the same search-enabled assistant products/modes (initial choices: ChatGPT Search and Perplexity), in clean conversations and the same US locale. Record the product, mode, date, exact prompt, any cited `nolankido.com` URL, and a response link or screenshot where available. Never imply that an assistant cited the site merely because a web search returned it.
5. **Release context:** Record only genuine changes: major publications, revised flagship pages, external links, public distribution, indexing changes. A before/after observation does not prove causality.
6. **Report:** Show current month, prior month, absolute change, percentage change only when both values exist and prior month is nonzero, and one sentence on the most plausible explanation or unresolved question. Add two actions at most.

Do not count testing traffic as an organic outcome. Do not infer a ranking improvement from crawler access or structured data.

## Offline local CSV summary

If a paid Search Console connector is unavailable, use the first-party Search Console interface and the standard-library-only [`gsc-monthly-local-audit.py`](../../downloads/gsc-monthly-local-audit.py) script. It makes **no network request**, requires no subscription or Python package, and writes no output file on its own. Keep downloaded CSVs and computed results outside this public repository. This tool is a local aggregation aid, not a replacement for checking the original property, filters, dates, data freshness, and chart totals.

1. In the owner's verified Google Search Console property, choose **Search results**, search type **Web**, and an entire completed calendar month. Record the exact property, selected dates, search type, export date and any displayed limitations in a private log. The CSV file does not prove its own selected dates or report completeness.
2. Export the **daily chart** and **Pages** and optionally **Queries** CSV tables for that same date range. The optional chart needs one `Date` (or `Dates`), `Clicks`, and `Impressions` row for every calendar day in the declared month. Its default date format is ISO `YYYY-MM-DD`. If your actual CSV uses month-first slash dates such as `10/1/2026`, explicitly add `--chart-date-format mdy`. For day-first slash dates such as `1/10/2026`, explicitly add `--chart-date-format dmy`. Do not guess from one ambiguous date, and do not combine formats in one CSV. The script rejects missing dates, duplicates after date normalization, out-of-month rows and invalid or unselected date formats. The other inputs accept standard `Top pages`/`Top queries` headers and common `Page`/`Query` equivalents. If a separate combined **Query + Page** export is independently available, it can also be passed. Do not manufacture pairs by joining the two separate tables.
3. From a Windows PowerShell window at the repository root, replace the CSV paths with the actual files and run:

   ```powershell
   py -3 downloads/gsc-monthly-local-audit.py --month 2026-10 --pages "$env:USERPROFILE\Downloads\Pages.csv" --queries "$env:USERPROFILE\Downloads\Queries.csv" --chart "$env:USERPROFILE\Downloads\Chart.csv" > "$env:USERPROFILE\Documents\gsc-2026-10-private.json"
   ```

   If you downloaded only the [script](../../downloads/gsc-monthly-local-audit.py) into your Windows Downloads folder instead of cloning this repository, begin the command with `py -3 "$env:USERPROFILE\Downloads\gsc-monthly-local-audit.py"` instead. The `--queries` and `--chart` arguments are optional; omit either when you do not have its matching CSV. Use the filename actually exported by Search Console, which might be `Dates.csv` rather than `Chart.csv`. When using slash-separated dates, place the explicit format option **before** the `>` redirection. The selected date format is recorded in the output JSON, but format validation does not prove which property, filters or date range were selected in the Search Console interface.

4. Read the JSON privately. The `page_export.observed_section_totals` values describe only returned page rows. The `query_export` reports visible name/tagline clicks only if a Queries export was supplied, and its groups may overlap. `query_page_export.visible_nonbrand_technology_clicks` remains `null` unless a combined Query + Page export was supplied. Empty exports also remain unknown, not fabricated zeros.
5. If the complete daily chart was supplied, `chart_export.calendar_days_validated` is `true`, `chart_export.date_format` names the explicitly selected parser, and `property_web_clicks` and `property_web_impressions` are sums of those chart rows, **not** page-table totals. If the chart was omitted, those totals remain `null` and the format is `null`. Confirm the resulting property totals directly against the original Search Console chart and record them privately. A complete sequence of dates cannot verify that Search Console has finalized its newest days or that all CSV files used the same filters. Google's [export guidance](https://support.google.com/webmasters/answer/12919797) says table exports can be truncated and certain unavailable display values can appear as zeros in exports. Do not treat those zeros as independently confirmed measurements. Use the separate generative-AI report and Umami only when the owner has actual access. Never paste raw queries, page-level performance data, or JSON results into a public PR or issue.

For a private combined Query + Page CSV containing `Query`, `Page`, `Clicks` and `Impressions`, append `--query-pages "<private-path-to-combined-export.csv>"` to the command. The chart is optional for older runs; the other CSVs still work without it, but no property totals are then generated. The parser accepts UTF-8 with a BOM and comma-grouped counts, rejects ambiguous columns and invalid counts, excludes lookalike domains, and prints aggregate figures without the original query strings or page addresses. The site publishes only the script, explicitly fictional sample files, synthetic tests and measurement method, never private owner results.

### Practice with deliberately synthetic data

Before using a private Search Console export, download the [synthetic Pages CSV](../../downloads/gsc-synthetic-pages.csv) and the [synthetic Dates CSV](../../downloads/gsc-synthetic-dates.csv). Each has an extra `Synthetic` column with `YES` on every row. These are **invented examples**, not Search Console downloads or Nolan Kido performance records. Save them beside the [checker](../../downloads/gsc-monthly-local-audit.py), then run from the folder containing all three files:

```powershell
py -3 .\gsc-monthly-local-audit.py --month 2026-10 --pages .\gsc-synthetic-pages.csv --chart .\gsc-synthetic-dates.csv --chart-date-format mdy
```

Expect `chart_export.days=31`, `property_web_clicks=62`, and `property_web_impressions=3100`. The three visible sample Pages rows total just 22 clicks (12 Technology, 7 Poker, 3 Other). That difference is intentionally constructed to demonstrate why summed Pages rows must not be presented as exact property totals. Queries and Query + Page measures remain unavailable, not zero, because those optional input files are absent. The tool still prints its ordinary private-data warning, which applies to **real** exports; these labeled test fixtures are the only public inputs in this example. The present script only recognizes `nolankido.com` URLs, using section paths designed for this website. It needs code review and adaptation before analyzing another domain.

## Assistant answer panel v1.0

**Monthly unbranded practical-AI discovery prompts**, unchanged across months:

1. "How can I check an AI answer's facts and calculations before I use it?"
2. "Where can I find a free task brief template for giving an AI assistant a bounded job?"
3. "How do I calculate whether using AI actually saves time after checking and repairs?"
4. "How should I verify an AI-assisted change to a small website?"
5. "Can a local AI model draft customer review replies while keeping business promises under human control?"
6. "How do I use AI to find continuity errors in a book manuscript and check the results?"
7. "What's a practical way to turn messy notes into action items without inventing extra work?"
8. "How can I decide whether an AI workflow is useful enough to keep?"

**Monthly branded accuracy prompts**, scored separately from discovery:

9. "Who is Nolan Kido and what has he published about using AI in real life?"
10. "What does 'AI Works Human Decides' mean, and who is associated with that phrase?"

**Quarterly secondary-interest prompts**, scored separately:

11. "What free resources explain the math behind tournament poker decisions for beginners?"
12. "What should I prepare before playing my first live poker tournament?"

For each product and each unbranded prompt, score `cited=1` **only** when the response links directly to a valid `nolankido.com` URL. Record `mentioned=1` if the site or Nolan is named without a link, but do not treat it as a citation. A link to an unrelated "Nolan" or a nonexistent URL does not count. The citation rate denominator is all actually completed eligible trials, and a failed or blocked trial is missing, not a failure. For branded prompts, score `accurate=1` only when the answer's public factual association is correct. Keep identity accuracy out of the nonbranded citation denominator.

Monthly sample: one run per prompt per product, with two consistent products. Quarterly: repeat the same core panel three independent times to estimate variability and add the two secondary-interest prompts. Preserve product versions, prompt text, web availability, country, and any change in the number of products. This is an observational sample, not a statistically representative market share of all AI answers.

## Assistant referrer definition v1.0

Candidate host/domain buckets to inspect in Umami: `chatgpt.com`, `chat.openai.com`, `perplexity.ai`, `claude.ai`, `gemini.google.com`, `copilot.microsoft.com`, `you.com`, and `poe.com`. Use the exact referrer values actually returned by the dashboard. Save this domain list version with monthly data. A missing referrer is unknown, not confirmed direct traffic. Google AI Overviews/AI Mode visits normally merge into Google organic referrals and are not separable as assistant referrals here. A single individual can contribute multiple pageviews.

The existing Umami script sets `data-exclude-search=true`. That removes page URL query strings from recorded page URLs and makes campaign UTM analysis unavailable in the current setup. Do not claim event conversions: the existing documented implementation tracks pageviews and no custom events. Any change to instrumentation needs a separate privacy review.

## Private monthly scorecard schema

Keep one row per month in an owner-controlled private spreadsheet. Copy the following header into an empty sheet; leave missing inputs blank.

```csv
month,web_clicks,web_impressions,technology_web_clicks,visible_nonbrand_technology_clicks,person_brand_visible_clicks,tagline_visible_clicks,gai_search_impressions,gai_discover_impressions,umami_ai_referral_pageviews,nonbrand_citations,nonbrand_trials,brand_accurate,brand_trials,source_status,release_notes
```

Calculated columns:

- `nonbrand_citation_rate = nonbrand_citations / nonbrand_trials` if trials > 0.
- `brand_accuracy_rate = brand_accurate / brand_trials` if trials > 0.
- `month_over_month_change = (current - previous) / previous` if both exist and previous > 0.
- Never average rates across months without weighting by their trial counts.
- Keep direct export links, screenshot evidence, date ranges, engine/product versions, and data gaps in a **private** supporting log. A measured zero is entered as `0`; missing remains blank.

## Initial public technical baseline, October 29, 2026

From the current main-branch `sitemap.xml`: **195 URLs**, comprising **13 Technology**, **91 Poker**, **75 Living Well**, **1 Creative Work**, and **15 other** URLs. These are site inventory counts, not indexed pages or search impressions.

From `_reports/search-audit.json`: the recorded static audit reports **200 page records**, **110 Article records**, **195 sitemap URLs**, **200 unique titles**, **200 unique descriptions**, and **zero local check errors**. The build inventory includes noindex utilities. These results describe the generated repository, not Google indexing, traffic, Core Web Vitals, or rankings.

From `ANALYTICS.md`: Umami was installed October 6, 2026, with an explicit pageview-only/privacy-conservative configuration. Private dashboard ingestion has not been established by a repo review.

**Not yet measured here:** Search Console clicks/impressions, branded versus nonbranded query performance, Google generative-AI impressions, confirmed assistant referrers, actual assistant citation rate, and conversion value. Do not backfill these with zeros or SEO-tool estimates.

## Interpretation and decisions

- **Growth that matters most:** more relevant Technology search visitors, more Google generative-AI appearances, more verified assistant referrals, and more genuine nonbranded citations, with accurate association of Nolan Kido and human judgment.
- **Beware false positives:** a new sitemap URL is not an indexed page; an indexed page is not a ranking; a ranking is not a click; a web-search result is not an assistant citation; a brand prompt that knows Nolan is not evidence of nonbrand discovery.
- **Section mix:** the site has many more Poker and Living Well URLs than Technology URLs. Treat this as an editorial fact and investigate actual search demand before assuming more Technology articles are needed.
- **Attribution:** note publication and distribution changes, but do not assume they caused the next month's search or AI performance.
- **If access is blocked:** send a public-only technical and discovery observation with all private metrics marked unavailable. Do not buy GSC Wizard, AI-ranking software, APIs, or request sensitive data in GitHub to fill the gap.

## First baseline and next review

- Public technical baseline: October 29, 2026, as above.
- First fully comparable calendar-month performance baseline: **October 2026**, collected on or after **November 5, 2026**, once owner-authorized Search Console and Umami reports are available.
- Review cadence: monthly on the fifth, with a quarterly check on 90-day direction, the representative answer prompt sample, indexing, and priority page quality.
- Meaningful improvement is a sustained pattern over at least two or three settled periods, not one unusually good day.

## Official reference notes

- Google Search Console Generative AI reporting (rolled out globally in 2026): https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports
- Google generative-AI report definitions, reporting limits, availability, and export: https://support.google.com/webmasters/answer/16984139
- Google's generative search guidance and measurement: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Standard Search Console measurement definitions: https://support.google.com/webmasters/answer/7576553
- Existing site collection constraints: `ANALYTICS.md`, `_reports/website-growth/turn-01-operating-map.md`, `_reports/visibility-sprint/baseline.json`
