# SEO/GEO sprint Turn 03: Bing, ChatGPT Search, and fresh-content discovery

**Date:** November 17, 2026 (Pacific/Honolulu)  
**Site:** https://nolankido.com/  
**Repository:** `nolankido/nolankido.github.io`  
**Starting main:** `9da41d068e752bb202d78172c7a4c9542144c41f` (Turn 02, PR #374)  
**Scope:** Public discovery permissions, representative HTTP access, IndexNow proof and safeguards, public documentation, and the availability of authenticated Bing AI-citation evidence. No claims of increased indexing, traffic, ranking or AI citations.

## Decision and implementation

**The inspected public controls do not reveal a blocker to Bingbot or OAI-SearchBot.** The site presently declares `User-agent: *` and `Allow: /`, serves its sitemap, and returns expected content to ordinary mobile and desktop requests. The root IndexNow key proof is published and its bytes match its filename. That does not prove actual requests from Bing or OpenAI crawler IPs are accepted by the host, that either bot has crawled the site, or that any page appears in AI answers.

Instead of changing an already permissive crawler policy, this turn adds a focused **offline search-bot regression guard** to the existing discovery checker and tests. It explicitly protects the search-discovery routes for `OAI-SearchBot` and `bingbot`, without making a claim or imposing a test expectation about `GPTBot` training preferences. The tests demonstrate that a future explicit GPTBot opt-out can coexist with OAI-SearchBot search access.

There were no new or substantively revised canonical public pages in the preceding Turn 02 PR or in the current test/report change, so this turn **did not submit a blanket IndexNow notification**. No crawler training preference, `robots.txt`, sitemap, site content, publication date, authentication setting, scheduled job or paid service was changed.

## Current crawler and control matrix

The robots column records a direct read of https://nolankido.com/robots.txt and the result of standard-library robots parsing for representative paths `/`, `/technology/check-ai-answers/` and `/poker/`. The HTTP column is deliberately restricted to **ordinary browser user agents**, not impersonated search bots. A crawler can also be denied by hosting/CDN rules or network controls not visible in `robots.txt`.

| Client / mechanism | Purpose | Public robots permission | What was observed directly | Actual engine access / citation status | Recommendation |
| --- | --- | --- | --- | --- | --- |
| `OAI-SearchBot` | ChatGPT Search discovery and potential citations | Allowed via `User-agent: *` | Robots rule parse passed; ordinary HTML GETs work | Real OAI-SearchBot IP access, crawl and citation unverified | Preserve search access; verify allowlisted crawler IP behavior only if host logs or approved settings become available |
| `bingbot` | Bing search discovery | Allowed via wildcard | Robots parse passed, sitemap returns 200 | Bing crawl/index/AI-citation verdict unavailable | Review Bing Webmaster Tools when authenticated; use its crawl and AI Performance reports |
| `Googlebot` | Google search discovery | Allowed via wildcard | Robots parse passed and 224 page eligibility verified in Turn 02 | Actual Google indexing still unverified | Resolve free first-party Search Console access separately |
| `ChatGPT-User` | User-initiated ChatGPT page fetch | Allowed via wildcard | Robots parse passed | User-triggered fetch from OpenAI IPs not independently tested | Do not confuse this with scheduled search crawling |
| `GPTBot` | Potential model-training crawl | Allowed via wildcard currently | No named GPTBot rule exists; generic robots parser permits it | Actual training ingestion not measured and not asserted | **Do not change training policy without the owner's choice.** Search and training controls are independent |
| `IndexNow` | Notify participating engines of meaningful URL changes | Not a robots user agent | Published root key file returned HTTP 200 and its 32-byte body matched the published filename | Prior accepted submissions and subsequent indexing cannot be authenticated | Use existing bounded helper only for verified changed pages, not a whole-site re-ping |

Primary references: [OpenAI publisher FAQ](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq), [ChatGPT Search crawling requirements](https://help.openai.com/en/articles/9237897-chatgpt-search), [Bing IndexNow guidance](https://blogs.bing.com/webmaster/2021/9/Access-to-Instant-Indexing-%C2%A0Bing%C2%A0URL-submission-API/), and [IndexNow protocol](https://www.indexnow.org/documentation).

## Public host checks

| Target | Desktop request | Mobile request | Canonical and observed blocking header |
| --- | --- | --- | --- |
| `/` | HTTP 200, HTML served | HTTP 200, HTML served | `https://nolankido.com/`; no `X-Robots-Tag` |
| `/technology/check-ai-answers/` | HTTP 200, HTML served | HTTP 200, HTML served | `https://nolankido.com/technology/check-ai-answers/`; no `X-Robots-Tag` |
| `/poker/` | HTTP 200, HTML served | HTTP 200, HTML served | `https://nolankido.com/poker/`; no `X-Robots-Tag` |
| `/robots.txt` | HTTP 200, text | Not separately tested | General crawler allowed; canonical sitemap declared |
| `/sitemap.xml` | HTTP 200, XML | Not separately tested | Main sitemap URL correct |
| `/fad988cb80ec4bc36cf2965cf1c64577.txt` | HTTP 200, text | Not separately tested | IndexNow proof filename and file contents match, without disclosing the full key here |

The mobile and desktop body sizes were identical within each of the three sampled pages, and canonical values matched. These requests do not originate from Bing or OpenAI's published crawler IP ranges; a passing generic GET cannot verify CDN firewall behavior for those ranges. Turn 02 established a 224-item sitemap and 224/224 self-canonical public page scan; do not reinterpret that as 224 indexed URLs.

## IndexNow setup and decision

The site already has `_scripts/submit_indexnow.py` with its key proof in source. Its code selects semantically changed canonical pages between two *exact* Git commits, validates that the current main release is deployed, checks canonical/noindex and byte consistency, and only posts when `--submit` is explicitly passed. A default run is a dry run. It distinguishes a confirmed 200 delivery response from a 202 key-validation-pending response, neither of which proves indexing.

- Public root key file: **present and matching**. The direct GET returned 200, with a 32-byte body equal to the key represented by the filename.
- Key stored in third-party GSC Wizard: **unknown**. `get_indexnow_settings` returned `INVALID_ARGUMENT`; the existence of the public proof file does not prove third-party account configuration.
- Prior IndexNow delivery receipts: **unknown**. The authenticated submission-history tool also returned `INVALID_ARGUMENT`.
- Changed canonical content since Turn 02: **none in this sprint's current documentation/test-only changes**. The script will not be invoked in submit mode just to produce a receipt.

When a later turn publishes real changes, use the existing script with audited base/head commits and review its dry-run URL list before any actual submission. Submission remains a separate, explicit action. IndexNow notifies participating engines, **not Google**; do not present it as a Google indexing request.

## Bing AI Performance and first-party measurement

Bing officially announced [AI Performance in Bing Webmaster Tools](https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/) in February 2026 and later expanded it with [intent, topic and citation-share reporting](https://blogs.bing.com/search/2026/6/New-AI-Visibility-Insights-in-Bing-Webmaster-Tools-Intents-Topics-Citation-Share-Compare/). The availability of the product does **not** mean this site has accessible, populated data.

Calls to the connected GSC Wizard's `list_bing_sites`, `get_indexnow_settings` and `list_indexnow_submissions` returned `INVALID_ARGUMENT` on this review. The plugin's Bing AI Performance tool is not currently exposed. Consequently we cannot verify:

1. Whether `nolankido.com` is a verified Bing Webmaster Tools property and whether its sitemap is submitted and fetched.
2. Actual Bing pages crawled, pages indexed, crawl errors, link counts or URL submission quota.
3. Site-level AI citations, cited pages, sampled grounding queries, Topics/Intents or Citation Share.
4. Whether OpenAI's OAI-SearchBot is allowed by external CDN/firewall rules or has actually crawled or cited any page.

Keep all these values **unknown, never zero**. Do not renew a paid connector or change third-party access settings without the owner's permission. If free direct Bing Webmaster Tools access becomes available, inspect its sitemap, Crawl Information and AI Performance dashboard, then record the exact date range, cited URLs and queries privately.

## Small public retrieval sample, not an AI answer test

A manual public web-search retrieval for targeted Nolan Kido, practical-AI and poker queries surfaced real pages such as [Technology](https://nolankido.com/technology/), [Notes](https://nolankido.com/notes/), [Poker Math](https://nolankido.com/poker/poker-math/) and [Start Here](https://nolankido.com/start-here/). This is evidence that those pages can be retrieved from a public search interface. It is **not** a Bing-index count, a measured ChatGPT Search citation, an assistant-answer benchmark, a ranking trend or a representative population sample. No isolated, repeatable assistant-answer experiment was performed in this turn.

## New local regression coverage

- `_tests/check_discovery.py`: new `blocked_search_entrypoints` check for `OAI-SearchBot` and `bingbot` at `/`, `/technology/check-ai-answers/`, and `/poker/`, incorporated into the existing offline discovery check. It uses `urllib.robotparser` as a bounded local policy approximation; it cannot assert actual CDN or bot-IP access.
- `_tests/test_discovery_robots_contract.py`: verifies current public robots source permits these search entry points, that an explicit `GPTBot` training opt-out can coexist with both search bots allowed, and that an intentional OAI search block is detected.
- **11/11** focused robots contract tests passed locally. **18/18** existing IndexNow helper tests passed in an isolated local fixture with mocked HTTP. No real IndexNow requests were sent.

**Validation boundary:** these focused tests, live public GETs, and read-only source inspection were performed. Full deterministic builds, HTML validation and browser test suites were not run because a complete site checkout was not present in the local working directory. No GitHub Actions or scheduled substitute was used.

## Turn 03 acceptance and next turn

**Public crawler/control matrix and manual discovery readiness: complete.** No confirmed public robots or key-file defect justified a site-content or crawler-preference change. Local regression coverage was added to protect the main AI-search and Bing entry paths. Authenticated Bing indexing and Bing AI Performance remain an explicit evidence gap.

**Next: Turn 04**, the search-query-to-page and assistant-question opportunity map. Keep observed query/citation records separate from unmeasured editorial hypotheses, using the existing public query map and private metrics only when accessible.
