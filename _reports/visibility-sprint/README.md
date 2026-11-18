# Visibility sprint: public work and evidence

> **SEO/GEO Turn 06, November 17, 2026:** [Homepage and Technology reader-path improvement](seo-geo-turn06-homepage-technology-paths-2026-11-17.md) gives the main homepage AI action a direct route to the Technology introduction. The first three Technology choices now lead to public projects, an evidence-checking guide, and a whole-workflow time calculator. The former task-brief and source-backed identity-correction links remain visible just below the choices. Targeted build, search, link, HTML5 and first-screen contract checks passed. This is navigation and task discovery work, not evidence of better rankings or AI citations. Next: Turn 07, one genuinely differentiated answer-first article based on the audited question map.

> **SEO/GEO Turn 05, November 17, 2026:** [Thirty-page evidence and discoverability audit](seo-geo-turn05-30-page-quality-audit-2026-11-17.md) and [machine-readable 30-page disposition matrix](seo-geo-turn05-30-page-audit-matrix-2026-11-17.csv) cover all 12 Turn 04 priority routes plus representative AI, Poker, Creative and Living Well pages. All 30 public GETs returned HTTP 200 with self-canonicals, unique nonempty titles/descriptions, one H1, valid JSON-LD syntax, viewport/language and no omitted image alt attributes. One duplicate H1/first-H2 heading in the six-to-ten-BB guide is a minor confirmed copy issue. Dispositions: 18 keep, five deepen, one correct, six leave untouched, no redirects or deletion. GSC Wizard on-page and top-page tools returned `INVALID_ARGUMENT`, so clicks, impressions, rankings and actual AI citations remain unmeasured. Next: Turn 06, evidence-focused reader paths from the homepage and Technology hub.

> **SEO/GEO Turn 04, November 17, 2026:** [Prioritized twelve-question opportunity map](seo-geo-turn04-query-opportunity-map-2026-11-17.md) and [frozen 25-prompt assistant panel](assistant-answer-panel-v1-2026-11-17.csv) now cover practical AI, tournament poker, beginner poker, first-party identity and creator evidence. All 22 distinct candidate destinations occur in the 224-URL public sitemap. The panel freezes 20 nonbranded and five branded questions with strict actual-URL citation scoring. First-party GSC, Bing query and AI-citation metrics were unavailable, so the ranked gaps are editorial hypotheses pending Turn 05's thirty-page audit.

> **SEO/GEO Turn 03, November 17, 2026:** [Bing and ChatGPT Search discovery audit](seo-geo-turn03-bing-ai-discovery-2026-11-17.md) confirms public robots allowance for Bingbot and OAI-SearchBot, a reachable matching IndexNow proof file, and ordinary desktop/mobile HTML access. The existing offline discovery guard now tests search-bot access separately from GPTBot training preference; 11 focused robots tests and 18 IndexNow tests passed. Actual Bing indexing, AI citations and crawler-IP reachability are unverified because authenticated tools were unavailable. No IndexNow notification or crawler-preference change was made.

> **SEO/GEO Turn 02, November 17, 2026:** [Public indexability and canonical eligibility audit](seo-geo-turn02-public-indexability-audit-2026-11-17.md) reviewed 224 sitemap URLs and five intentional noindex utilities. All 229 live checks and the full internal-link/JSON-LD syntax scan passed, with no confirmed critical public defect. The [manual live audit script](../../_scripts/live_indexability_audit.py) is now reproducible without scheduled jobs. Google/Bing indexed status remains unverified because authenticated inspection access is unavailable; these counts must not be reported as zero.

> **New SEO/GEO baseline, November 17, 2026:** [Turn 01 public live audit](seo-geo-turn01-public-baseline-2026-11-17.md) verifies the current 224-URL sitemap and a 224-page HTTP/metadata scan. The 189-URL October baseline below and the older 200-URL static `search-audit.json` receipt are historical, not current indexation counts. Private GSC, Bing and Umami performance measures remain unverified.

Prepared October 27, 2026, Honolulu. Baseline commit: `2aae4923318c0028d98266d78f6e4aabea295387`.

The goal is greater visibility for Nolan Kido's practical use of AI alongside Technology, Living Well, Poker, and Creative Work. This sprint gives existing public projects permanent, source-supported pages and connects them to the site. Publication is an implementation milestone. It does not establish indexing, ranking, AI citations, traffic growth, or usefulness for a reader.

## Scope and status

The core implementation was published in [PR150](https://github.com/nolankido/nolankido.github.io/pull/150), followed by six contextual links from four existing Living Well guides in [PR151](https://github.com/nolankido/nolankido.github.io/pull/151). Both published trees passed the required checks and exact public-response verification. The table records what was implemented and what still needs evidence or measurement.

| Turn | Planned improvement | Disposition in this sprint |
| --- | --- | --- |
| 1 | Establish a visibility baseline and inclusion checks | Public crawl and repository baseline retained in `baseline.json`. Private search, citation, and referral metrics remain unavailable. |
| 2 | Connect the public identity | Home/About Person records use the verified GitHub and DEV profiles. About includes visible matching links. |
| 3 | Publish Review Reply Writer | New permanent case with pinned source links and the limits of historical Gemma evidence. |
| 4 | Publish Preflight | New permanent case with a real archived report, benchmark results, review limits, and source links. |
| 5 | Feature inspectable projects on the homepage | Three project cards added while retaining the original reader choices and four subject areas. |
| 6 | Connect practical questions to useful pages | Hubs and cases linked; a candidate question-to-page map is retained in `query-map.md`. These are editorial hypotheses, not measured search demand. |
| 7 | Publish Dinner on Time | New case and public video link distinguish AI-assisted development from the deterministic simulation's runtime. |
| 8 | Simplify the Technology hub and separate the weekly case | Projects and task choices lead the hub. The existing weekly-reset case has its own page; previous hub fragment IDs remain available. |
| 9 | Make tasks, artifacts, evidence, and limits easy to identify | Applied to new project cases and the hub introductions. |
| 10 | Publish a real notes-organization example | Actual preparation notes, instruction, unchanged output, and source mapping retained, with a full downloadable record. |
| 11 | Document a personal local-AI workflow | Partial: a real historical hosted Ubuntu CPU test record is published. It is explicitly not a personal laptop run. |
| 12 | Compare local and hosted AI on a matched task | Pending a matched input, configurations, outputs, review rubric, and observed results. Different historical workloads cannot support this comparison. |
| 13 | Show actual AI failure and review examples | The answer-checking guide links documented review-reply, continuity, and HTML-checking examples. |
| 14 | Add an empirical time-calculator example | Partial: the calculator explains the available model processing timings and the missing whole-task/manual baseline. No fabricated time-saving preset was added. |
| 15 | Show finished creative work | Creative Work now leads with two existing poker comics and the archived Preflight report, with links to the full comic set and Dinner on Time. |
| 16 | Publish an authentic poker account | Pending an approved firsthand account or recording. Existing guides and comics remain available. |
| 17 | Publish a completed Living Well field note | Pending actual observation and a publishable record. No hypothetical trial is presented as completed. |
| 18 | Publish a useful real travel artifact | Pending an approved plan and source inputs. |
| 19 | Reinforce public profile connections | Website connections implemented. External profile wording prepared in `profile-link-updates.md`; it has not been posted to another service. |
| 20 | Choose the next work from observed performance | Pending a meaningful observation window and access to search/citation/referral data. |

## Published follow-ups

- October 28, 2026: PR150 published six source-supported cases and the related identity, hub, archive, feed, search, sitemap, image, and preview improvements. Its full release gate passed 1,163 unit tests and all five browser groups. The [public-response check](https://github.com/nolankido/nolankido.github.io/actions/runs/40664532327/job/122735579913) verified 494 of 494 targets for commit `116359834b8b48dbd1526c68392d89f9dd7bf1a0`.
- October 28, 2026: PR151 connected notes organization, small creative work, tool evaluation, and personal productivity guidance to the published cases. Its full release gate passed 1,172 unit tests and all five browser groups. The [public-response check](https://github.com/nolankido/nolankido.github.io/actions/runs/40671626565/job/122759561157) verified 494 of 494 targets for commit `1f315095cef741bd1afe6fe3bcba8b11216b0d0e`.

These are implementation receipts, not search-performance results. The current discovery follow-up is described in `discovery-follow-up.md`; its pull request will retain the final tested and published commit receipts.

## Measurement handoff

The existing public site had 189 sitemap URLs. All 189 returned HTTP 200 in the audit, with unique titles/descriptions and self-canonical URLs. This is a crawl baseline, not proof that any engine indexed those pages. Search Console performance data was unavailable during this audit, so its missing metrics are stored as null rather than zero.

When the native dashboards or an export are available, record the same date range, property, country, and device scope for each comparison:

- Google Search Console: page and query impressions, clicks, average position, and indexed/canonical status for the new URLs. Separate name searches from practical-task searches.
- Google Search Console's [Generative AI performance report](https://support.google.com/webmasters/answer/16984139), when present: record AI Overview and AI Mode impressions by page over the same period, country, and device scope. An absent report can reflect insufficient impressions; it is not a verified zero. Keep unavailable values distinct from zero, including exports that replace unavailable display values with zeros.
- Bing Webmaster Tools: indexed/crawled URLs, search performance, and any available AI citation reporting, preserving the provider's definition and reporting window.
- Existing Umami dashboard: landing pages and identifiable AI referral sources. Direct/unknown visits cannot safely be attributed to AI assistants.
- Repeated manual answer checks: record the exact prompt, provider, date, locale, account/personalization state, cited URLs, and answer. These are samples, not a population-level visibility score.

Candidate prompts include “Nolan Kido practical AI projects,” “using local AI to draft customer review replies,” “checking AI replies before sending them,” “AI manuscript continuity checker with source passages,” “AI-assisted cooking planner prototype,” and “turn scattered notes into an action list without inventing tasks.” Do not turn an observed absence into proof of universal exclusion.

Review newly published URL discovery first. Make performance-led editorial decisions only after enough impressions and a comparable observation period exist. Keep the publication date and any later substantive revision date distinct.

## Evidence boundaries

- The Review Reply Writer model records are historical and do not validate the quality of a different current source revision.
- The Preflight sample includes false positives and missed issues. Its archived cost counter is not a complete project-cost measure.
- Dinner on Time is a deterministic experience simulation made with AI assistance. The video is not evidence of a physical household cooking trial or a live Alexa integration.
- The notes example records actual work in this preparation session and a subsequent AI-assisted source check. It has no independent human rating or measured time saving.
- Historical hosted-runner model timings do not establish performance on Nolan's personal laptop, whole-task time saved, or a fair local-versus-hosted comparison.
- No personal poker event, household experiment, or travel experience has been invented to fill a content slot.

See `project-sources.md` for the pinned public sources and `release-verification.md` for release checks when available.
