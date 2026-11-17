# SEO/GEO sprint Turn 01: Public crawl baseline and measurement boundary

**Date:** November 17, 2026 (America/Phoenix)  
**Canonical site:** https://nolankido.com/  
**Repository:** `nolankido/nolankido.github.io`  
**Source checkpoint audited:** `ef0d4089892287152a49c96c395886c1cd33a8cd` (the Turn 168 main commit)  
**Scope:** Read-only public production and repository observations, plus current availability of private measurement routes. No new claims about search rankings, indexation, AI citations, or reader traffic.

## Why this is a new baseline

The source file `_reports/search-audit.json` currently records 200 sitemap URLs. Its last file change was committed on November 5, 2026, at `bed0fba458d50c08a2ff5e8679e6d9541a760e74`. It is an older deterministic static-audit result, **not** evidence that the current site still has 200 URLs or that the live site failed a new build. The latest sitemap is larger.

Do not edit the older report to pretend the source audit was rerun. The existing `_scripts/check_search.py --json <path>` option can regenerate a fresh static audit when a full checkout and all builders are available. This report is an independent, dated *public live* baseline and is not equivalent to `check_search.py`.

## Exact live/source checks

| Check | November 17 result | Interpretation |
| --- | --- | --- |
| Main branch | `ef0d4089892287152a49c96c395886c1cd33a8cd` | Audited public source checkpoint; recheck before any subsequent change |
| Live sitemap HTTP | 200, `application/xml` | Sitemap endpoint responded during this audit |
| Sitemap comparison | Live bytes exactly match current `main:sitemap.xml` | This file's deployed response is in sync with audited source |
| Sitemap `loc` count | **224** | URLs advertised for discovery; not an indexed count |
| Unique sitemap locations | **224** | No duplicate `loc` values observed |
| `lastmod` elements | **224** | One present for each listed URL; dates ranged from 2026-10-05 to 2026-11-16 |
| Live `robots.txt` | HTTP 200; bytes exactly match current source | General wildcard `Allow: /` and canonical sitemap link observed |
| Headline site routes | Home, Technology, Poker, About and Poker library available to public text retrieval | Text access observed; visual/browser performance not certified |

### Sitemap URL distribution

| Section | Listed URLs |
| --- | ---: |
| Poker (`/poker/`) | 109 |
| Living Well (`/living-well/`) | 76 |
| Technology (`/technology/`) | 19 |
| Homepage, identity, notes, projects, Creative Work and other routes | 20 |
| **Total** | **224** |

### Complete sitemap URL response and on-page metadata sample

A fresh, read-only Python standard-library inspection fetched the **224 URLs from the live sitemap** with eight concurrent workers, an 18-second request timeout and a maximum 1 MB body read per URL. It parsed the returned HTML for status, final response URL, title, description, canonical link, robots meta and number of H1 elements. The purpose was to catch public delivery defects, not to imitate Googlebot or declare a page indexed.

| Public test | Observed |
| --- | ---: |
| Successful HTTP 200 responses | **224 / 224** |
| Fetch failures | **0** |
| Final URL equals sitemap URL | **224 / 224** |
| Self-canonical equals sitemap URL | **224 / 224** |
| Nonempty title tags | **224 / 224** |
| Unique titles | **224** |
| Nonempty meta descriptions | **224 / 224** |
| Unique descriptions | **224** |
| Exactly one H1 | **224 / 224** |
| Sitemap pages with `noindex` in the parsed robots meta | **0** |
| Public response or metadata exceptions in this specific scan | **0** |

The crawl is encouraging but **does not** establish Chrome rendering, screen-reader quality, structured data eligibility, actual Google/Bing indexation, CDN bot access, Core Web Vitals, user satisfaction, organic rankings or inclusion in AI answers. The intentional noindex utilities omitted from the sitemap require their own Turn 02 checks.

## Missing private performance evidence

The site already has a [public SEO/GEO measurement protocol](seo-geo-measurement-v1.md) with separate series for Google organic clicks, Google generative-AI appearances, known assistant referrers, and a fixed manual assistant citation panel. Reuse that protocol.

| Performance source | Turn 01 state | Next legitimate path |
| --- | --- | --- |
| Google Search Console, Web | **Unavailable, not zero** | Authorized property UI or owner-provided, dated exports; the existing GSC Wizard connection did not return data in this review |
| Google Generative AI performance (Search) | **Unavailable, not zero** | Property report when authenticated and available; keep Discover separate |
| Bing Webmaster Tools search / AI Performance | **Not inspected through an authenticated dashboard** | Existing verified Bing property or owner-provided report |
| Umami pageviews / assistant referrers | **Dashboard ingestion and values unverified** | Existing authorized Umami dashboard; no new tracking |
| Assistant citation panel | **Not run in Turn 01** | Freeze prompts and method in Turn 04; comparison in Turn 24 |

Prior owner project notes identified an expired GSC Wizard subscription. During this turn its account-info request returned `INVALID_ARGUMENT`, so it did not establish that current search data could be accessed. Do not infer that Search Console itself has no information, that the property is unverified, or that a new paid subscription is required for the free first-party Google interface. No renewal or new paid service was authorized.

Actual private query rows, clicks, impressions, ranking snapshots, referral records, full assistant responses and account details must remain out of this public repository and its issues/PRs. The old public audit, source content and this report contain no authenticated performance exports.

## Decision and impact

**Public technical verdict:** no confirmed P0 public sitemap or common metadata delivery error was found in this scan. The source/live sitemap mismatch hypothesized in the roadmap was **not present**: current source and live are identical. The apparent discrepancy is between a dated older audit artifact and the current site.

**Search/AI visibility verdict:** **unknown**. No current first-party performance measurements were obtained. These observations should not be converted into a ranking or citation improvement claim.

**Implementation completed:** This dated, non-private baseline documents the verified public state and disambiguates the old report. No site page, public URL, metadata, analytics configuration or release automation was changed for Turn 01.

## Turn 02 handoff

1. Re-read `AGENTS.md`, the current main SHA and this report. Avoid rerunning the full 224-page crawl unless the public site changed in a relevant way.
2. Select a representative **25-URL indexing/canonical audit sample** from homepage, About, Technology, several real AI case pages, Poker hub/course/library, actual episode companions, the player profile, a tool and a few Living Well routes.
3. Check meta robots, HTTP status, final URL, canonical, sitemap inclusion, important internal routes, any relevant structured-data errors, and known October GSC indexing/markup notices if native evidence is available.
4. Separately confirm the five intentionally excluded utility pages really retain their intended `noindex` behavior. Never add them to the sitemap merely to grow the count.
5. With authenticated GSC access, record real indexed/excluded and canonical verdicts for sample URLs. If it remains unavailable, explicitly label the coverage as public-only and continue safe diagnostics without guessing.
6. Fix only a confirmed discrepancy, then run the correct local builders and tests. Do not modify canonical URLs or publication dates based on this baseline alone.

## Verification and restrictions

- **Actually executed:** live sitemap retrieval, source/live byte comparison, live robots retrieval and comparison, GitHub history read, public HTML/text retrieval of key landing pages, and the 224-URL live Python response/metadata scan.
- **Not executed:** local `build.py --check`, `check_search.py`, HTML5 static test, full historical unittest suite, Playwright browser suites, private GSC/Bing/Umami dashboard reads, URL Inspection API, bot IP allowlist checks, or real-device responsive tests.
- **Restrictions preserved:** no GitHub Actions, CI substitutes, cron, paid API, private data, invented indexation, unverified external claims or unjustified `lastmod` changes.

**Evidence refs:** [current sitemap source](https://github.com/nolankido/nolankido.github.io/blob/main/sitemap.xml), [current robots source](https://github.com/nolankido/nolankido.github.io/blob/main/robots.txt), [prior deterministic audit](https://github.com/nolankido/nolankido.github.io/blob/main/_reports/search-audit.json), [current source audit script](https://github.com/nolankido/nolankido.github.io/blob/main/_scripts/check_search.py), and [Turn 168 source checkpoint](https://github.com/nolankido/nolankido.github.io/commit/ef0d4089892287152a49c96c395886c1cd33a8cd).
