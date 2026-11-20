# Repository rules for autonomous changes

This public repository builds and publishes `https://nolankido.com/`.

## Owner's permanent restriction: no GitHub Actions

**Do not create, restore, enable, dispatch, rely on, or use GitHub Actions workflows for this project.** Do not add any `.github/workflows/*.yml` or `.yaml` file. Do not introduce another CI/CD service, cron job, scheduled bot, or paid API without specific owner approval.

The former `.github/workflows/site-checks.yml` was removed intentionally on November 1, 2026. This removal is an owner instruction, not an accidental deletion. Do not bring it back for convenient automated testing or to satisfy archived historical tests.

GitHub Pages may independently run GitHub-managed deployment jobs even when there are no repository-authored workflows. These must **not** be treated as permission to run or add site test workflows. Do not promise that zero GitHub-managed deployment jobs can occur while the site remains on GitHub Pages. A total prohibition on GitHub-managed deployment requires a separately authorized hosting migration.

## How to verify instead

1. Edit `_source/` files, then generate their committed public outputs on a local machine with `python _scripts/build.py` (Python 3.10+).
2. Verify deterministic output with `python _scripts/build.py --check`.
3. Run `python _scripts/check_search.py` and `python _tests/check_html5.py` locally. Install `requirements-test.txt` only in a local environment when needed.
4. For full verification, run `python -m unittest discover -s _tests -p 'test_*.py' -v` and browser suites locally with the installed Playwright dependencies. Use direct public GETs to verify deployed URLs and expected source bytes.
5. Report test scope precisely. Do not claim that the full suite or browsers passed unless they actually ran. Never reenable GitHub Actions as a shortcut.

For a single-release download receipt, use `python _scripts/check_live.py --only /downloads/gsc-period-compare.py --attempts 3 --interval 5` from a complete checked-out repository. The route must be present in the explicit public inventory. The default with no `--only` still tests all targets. `URLError`/DNS failures are inconclusive; do not call them 404s or proven deployment failures. Successful exact bytes prove serving, not search visibility.

### Complete local release coverage

Install `requirements-test.txt` in a local virtual environment, then run `python _scripts/local_release_checks.py`. The default checklist includes the two Portland Meadows companion builders, the Reserve Day 1 companion builder, the search audit, and HTML5 parsing of all manifest pages plus the six source-validated standalone pages. `--full` additionally runs the historical unit suite; `--browser` additionally runs the local browser scripts. A failed standalone build must fail the checklist.

`_scripts/search_entrypoints.py` must preserve the later of a page's actual content revision and its search-copy revision. An older search-description record must not backdate a later content change in structured data or the sitemap. Do not advance dates merely because a build ran.

Regenerate page outlines and reading estimates after source edits. The standalone Episode 1 command example uses the existing `poker-details` wrapper so command text wraps on narrow screens without changing copied commands. Test standalone reading routes at 320 pixels as well as desktop widths. HTML validity and a passing local browser check do not independently verify the current YouTube audio or footage.

`assets/standalone-section-arrivals.css` belongs only to the standalone player profile and independent reply audit. After changing it, run both `python _scripts/build_player_profile.py` and `python _scripts/build_reply_audit_case.py` to refresh their content-versioned links, then run the main build check. Do not add it to their shared hub/article shells. Preserve the existing heading IDs, `#main` skip targets and profile `#creator-introduction` bookmark. `_tests/standalone_reader_arrivals_browser.py` checks native arrivals with ordinary/enlarged text and committed/fallback fonts; a CSS-only change must not advance content dates.

## Standalone poker player profile

The public `/poker/nolan-kido/` page has its own deterministic local builder because the main site's generated manifest does not yet have a personal-player-profile type. Edit `_source/poker/nolan-kido-profile.html`, then run `python _scripts/build_player_profile.py` and `python _scripts/build_player_profile.py --check`. The generated page deliberately lacks the main generator marker so the main build will not overwrite it. Both Poker and About have native links to it. `_scripts/player_sitemap.py` registers this one source-verified, manually built URL in the **existing main sitemap** and in read-only live-byte targets. Run `python _scripts/build.py` after any profile URL, canonical or review-date change to update the sitemap. The on-site Find page additionally includes this manually built public profile through the bounded `_scripts/player_find.py` adapter. Its source-verified title, description and canonical route are searchable locally under the **Player profiles** filter. The main manifest continues to own the other entries, and this addition does not add a new remote search service or index personal records outside the public page. Run `python _scripts/local_release_checks.py` to verify both the Find projection and sitemap without GitHub Actions. Keep documented tournament citations and the gross-versus-net caveat. Do not add the page to the main manifest without migrating its build ownership and search verification together.

## Public poker video companions

The first public episode uses the source file `_source/poker/portland-meadows-ep1.html` and the independently compiled `/poker/episodes/portland-meadows-ep1/index.html`. Build it locally using `python _scripts/build_poker_episode.py`, then check it with `--check`. The source-validated `_scripts/poker_episode.py` registry allows the Poker hub to advertise the video only when the exact source and canonical Article page exist, and links to the public YouTube video without an iframe. The existing sitemap and on-site Find index include only this verified manual video route. The newer public Episode 1 cut replaced an earlier private version 7 upload. Old chapter offsets were removed in Turn 10 and must not be restored until checked against the current video. Do not publish unverified scenes, payouts, opponent identities, videos or private drafts. Keep the four-way deal's actual reported $2,900 payment distinct from the $5,100 advertised top prize. Preserve manual page ownership until the main generator has a reviewed migration path. Never use GitHub Actions for release tests.

## Second Portland Meadows companion, archived v9 source

A second manually owned written companion is published at `/poker/episodes/portland-meadows-standoff/`, with source `_source/poker/portland-meadows-standoff.html`, generator `_scripts/build_standoff_episode.py`, public HTML `poker/episodes/portland-meadows-standoff/index.html`, and registry `_scripts/poker_standoff_episode.py`. It uses the existing Episode 1 Poker shell, so run `python _scripts/build_poker_episode.py` first and then `python _scripts/build_standoff_episode.py`. The registered manual sitemap, local Find Poker collection, Poker RSS, combined writing RSS, and read-only live-byte targets must all contain the exact second route once. Use `python _scripts/build_standoff_episode.py --check`, then `python _scripts/build.py --check` and local release checks. Neither manual page belongs in the main manifest or private poker catalog.

This Stand Off narrative was constructed from an archived November 3 Episode 2 v9 script, source-verification memo and QA packet. Its current YouTube upload has not been independently compared frame by frame or listened to in this release. **Do not add v9 chapter offsets to links, unverified board runouts, opponent suits, estimated equity or a solver/ICM verdict.** Source-backed chip arithmetic, the narrated A-K versus K-K/Q-Q result, and the player's later hotel hypothesis are labeled separately. The source packet itself stays private. Both authored companions have their own publication dates; new HTML or links do not silently republish Episode 1 or reset its RSS date. Never add GitHub Actions, cron, paid APIs, or background monitoring.

## Narrated hand records and RSS

The Portland Meadows Episode 1 source has two stable firsthand decision sections, `#hand-64o-record` and `#hand-77-record`. Those records distinguish facts stated in the public video, the author's retrospective account of a read, independently checkable big-blind arithmetic, and missing inputs that prevent a verified solver or ICM conclusion. The event calendar date is not independently established from the public footage, so do not invent one. Keep the current public video URL and label old version 7 scene offsets as unverified for the newer cut. Keep private scripts, opponent names, unsupported card suits, confidential finances, and unfinished footage out of the public site.

The separately authored public Episode 1 appears once in `/poker/feed.xml` and once in `/writing.xml`. `_scripts/manual_poker_feed.py` adds that one source-validated RSS item, and `_scripts/follow.py` accepts it only when the standalone companion passes `poker_episode.record(root)`. Two hand sections do **not** create two article publication dates or separate feed items. For a local site update, run `python _scripts/build_poker_episode.py`, then `python _scripts/build.py`, then `python _scripts/local_release_checks.py`. Never use GitHub Actions, other recurring workflows, or paid external APIs.

## Turn 11 public poker-video discovery

The public Poker hub and standalone player profile link three public YouTube uploads (Portland Meadows Deepstack, evening Stand Off, and WSOP Circuit Reserve Day 1). Turn 11 had two source-limited written companions; Turn 13 added the third for Reserve. Maintain separate video and companion labels, do not invent hand outcomes or timestamps, and preserve tournament listing citations and the gross-versus-net caveat. Edit the Poker hub at `_source/poker/home.html`, run the main builder, edit the player source at `_source/poker/nolan-kido-profile.html`, and rerun its standalone builder. The player's metadata, Find card and main sitemap must agree on the current reviewed title, description and modification date. Use local release checks; never add GitHub Actions.

## Turn 13 Reserve Day 1 archived-source companion

The original first-person companion `/poker/episodes/reserve-day-1/` has an independently maintained HTML source at `_source/poker/reserve-day-1.html`. Build it with `python _scripts/build_reserve_day1_episode.py`, followed by `--check`. Its bounded registry `_scripts/poker_reserve_day1_episode.py` validates the source, Article canonical, shared Person `@id`, November 18 publication date and public-safe `downloads/reserve-day1-public-source-ledger.json`. The page is intentionally absent from the main manifest. The existing sitemap, Poker Find, global Find section search, Poker RSS, writing RSS, Poker hub, standalone player profile, read-only live checker, and HTML5 inventory register it exactly once. Build the player profile, then run `python _scripts/build.py`, its `--check`, the Reserve builder's `--check`, and the Turn 13 tests. Never add a second feed, sitemap, publishing workflow or GitHub Action.

The written hand sequence is paraphrased from private November 3 v8 script, truth-and-continuity notes and metadata, **not** from an independently inspected copy of the presently public YouTube audio or footage. Do not publish private production materials, editor paths or unverifiable chapter timestamps. The official WSOP listing establishes 527 entries and 80 paid; independently published player results establish Nolan Kido's 63rd place and $800 **gross** payout, not profit. Approximate A-K main/side-pot layers and the ~10 BB uncalled refund are arithmetic illustrations only; full suits, board, opponent ranges, effective stacks, ante ledger and solver/ICM results are unknown. Keep the article, public ledger and validation checks consistent when correcting a claim. Do not represent this archived-source narrative as certified current-cut footage.

## Turn 14 current Reserve video listing and answer path

The November 18 public YouTube oEmbed listing for video `edNSD5BjIV8` uses the title **My Ace-King Reshove in a 3-Way All-In | WSOP Circuit**, replacing the earlier seven-big-blind headline, and its public `hqdefault.jpg` thumbnail changed. The exact current locally hosted image bytes, title and check date are recorded in `_source/poker/nolanpoker-video-thumbnails.json` and `downloads/reserve-day1-public-source-ledger.json`. The old public title remains only as a dated historical value. The public Poker hub, player profile and Reserve companion must display this same current title; each preserves an ordinary link to the public video and a separate canonical link to the source-bounded hand explanation. The Poker hub also links directly to the Reserve main/side-pot answer and the educational side-pot lab.

Use `python _scripts/check_reserve_video_listing.py` for an offline, fail-closed agreement check between the public source, ledger and stored JPEG. `--live` optionally makes two read-only, no-login public YouTube metadata and thumbnail requests to detect later title/artwork drift. It is **manual only** and not a default remote release gate or scheduled service. If metadata has changed again, check and intentionally update all public elements and the dated ledger together. A current title or thumbnail proves only current packaging, **not the spoken current cut, card overlays in the actual video, chapters, showdowns, solver correctness or net profit**. On November 18 the publicly advertised auto-caption tracks returned no transcript text; do not treat this as having reviewed the actual current audio. Never add synthetic chapters or publish private production records to fill the gap.

## Turn 15 AI website visibility direct-answer case

The existing manifest-backed `/technology/ai-website-visibility/` article now begins with a direct answer about AI-assisted publication and a November 18 Reserve listing example at `#site-visibility-recent-release`. Its evidence chain distinguishes public YouTube packaging, the source-level site diff, local test scope, and read-only live-byte parity. The example points to merged PR #386, the public source ledger, offline checker and dated report. This publication evidence **does not** establish Google impressions, rankings, AI-answer citations, current-video transcript accuracy or conversions. Never turn a technical release pass into a search-performance claim. Preserve the original November 3 publication date, historical `#site-visibility-evidence` anchors, free Search Console method, AI citation sample and technology-hub fragment aliases. The case is manifest-backed, so edit `_source/technology/ai-website-visibility.html`, its record in `_source/pages.json`, and relevant `_source/technology/home.html` links, then rebuild. Run `_tests/test_turn15_ai_website_release_answer.py` and the ordinary local search, HTML5 and link checks. Do not add a duplicate URL, paid subscription, monitoring workflow or GitHub Action.

## Turn 16 Preflight continuity answer and author decision log

The manifest-backed `/technology/ai-book-continuity-checker/` page answers whether AI can find book-series continuity errors, using the pinned October 27 Sherlock Holmes audit and its revised seeded benchmark. A new `#continuity-decision` section links `downloads/book-continuity-editorial-review-log.md`, an original blank human review log with two public-domain examples. The file is explicitly registered as a public read-only target in `_scripts/check_live.py`. The Technology and Creative hubs lead to the same existing canonical page and decision anchor. Preserve the original October 27 article publication date, existing fragment IDs, historical raw/rescored scores, source links, and imperfect-benchmark caveats. The revised same-run result was 8 of 20 found, 12 missed, 2 false positives and one separate finding; eight misses occurred at extraction and four at judgment. Ambiguous planted data and source attribution errors mean these are not general accuracy rates. Do not imply the checker verifies all manuscript facts, that a local run was performed for this site turn, or that a hosted demonstration is safe for private writing. Edit `_source/technology/ai-book-continuity-checker.html`, the manifest entry and native hub links, build locally, and run `_tests/test_turn16_continuity_answer.py` plus search, HTML5 and link audits. No new paid service, GitHub Action, automated publication workflow or private manuscript upload is permitted.

## Turn 17 Review Reply Writer owner approval answer

The existing manifest-backed `/technology/local-ai-review-replies/` case now opens with a direct answer about human approval of AI-generated customer responses and adds `#reply-owner-gate`. Its downloadable blank `downloads/review-reply-owner-approval-checklist.md` separates reported customer details, the business owner's actual policy, the exact saved draft, and the person who approves or manually posts it. The file is an explicit public GET target in `_scripts/check_live.py`, and Technology and Resources link directly to the new section or checklist. Preserve the original October 27 Article publication date, existing case and evaluation fragment IDs, pinned source records and historical model receipts. The recorded October 2026 Gemma reply was for a fictional cafe, not a real client. Separate synthetic offline boundary probes showed the narrow checker missed constructed offers to reimburse a charge and send a gift card, and falsely flagged a quoted warning. These are **not** additional Gemma outputs, a current model evaluation, a representative error rate, or permission to post. The program does not auto-post; edits invalidate earlier approval. Run `python downloads/reply-audit-boundary-probes.py --self-test`, `_tests/test_turn17_review_reply_owner_gate.py`, and the usual local build, metadata, HTML5 and link checks. Never publish private customer reviews, policies, owner notes or credentials. No paid API, GitHub Action or scheduled monitoring was introduced.

## Turn 18 Review Reply Writer time break-even answer

The existing manifest-backed `/technology/ai-time-savings/` page now has a direct answer at `#reply-time-break-even` and a registered public worksheet at `downloads/review-reply-time-break-even.md`. The Technology hub, Resources and the original Review Reply Writer case link into that answer, without a new canonical article. Preserve the original October 27 AI time calculator publication date, its existing calculator IDs/formulas, Review Reply Writer publication date, and both records' established fragments. The pinned October 13, 2026 Gemma 3 4B smoke file contains only three historical Linux CPU case elapsed times of 19.536, 18.157 and 19.325 seconds for fictional reviews, **not** matched manual time, observed owner review/repair, complete workflow cost, a current laptop result, or verified human approval. A distinct teaching example deliberately assumes manual 6, preparation 2, review 3 minutes per reply, setup 20 minutes, upkeep 5 minutes and 10 replies. It yields 60 versus 75 minutes, 15 additional minutes, break-even at 25 replies and positive savings starting at 26. These numbers are invented, not a customer outcome or measured productivity gain. If review rises to 4 minutes, the fixed overhead is never recovered with the stated assumptions. Keep source observations and hypothetical arithmetic clearly labeled, and never infer that a fast model is a safe public reply. Run `_tests/test_turn18_reply_time_break_even.py`, the deterministic builder, search, HTML5, and internal-link audits after editing the example. No private records, new model inference, paid services, background jobs or GitHub Actions are part of this case.

## Turn 19 frozen AI-answer panel measurement kit

The existing manifest-backed `/technology/ai-website-visibility/` now contains `#ai-answer-sprint-panel`, an answer about auditing AI citations with an explicitly unchanged 25-question panel from November 17. Keep the eight-question monthly visibility method and its `downloads/ai-citation-panel-*` artifacts **separate** from this sprint panel: 20 exact nonbranded `NB01` to `NB20` prompts and five exact branded `BR01` to `BR05` prompts. The downloadable `downloads/ai-answer-sprint-25-prompts.csv` must remain byte-identical to `_reports/visibility-sprint/assistant-answer-panel-v1-2026-11-17.csv`; the offline `downloads/ai-answer-sprint-25-audit.py` pins that file's SHA-256 checksum and validates IDs, human-labeled outcomes, URL syntax, duplicates and incomplete trials. `downloads/ai-answer-sprint-25-blank.csv` is a header-only log. All three assets are explicit public GET targets in `_scripts/check_live.py`. The checker cannot observe assistant responses, independently prove clickable citations, obtain Search Console data, or measure rankings. It prints no raw observed links, splits branded and nonbranded rates, counts expected-page citations separately, and uses `null` for a segment without completed observations. Any real answers, screenshots, personal information or metrics belong only in an owner-private log. The site's original November 3 article publication date and all preexisting anchors must stay intact. Run `_tests/test_turn19_frozen_answer_panel.py` plus the Turn 15 visibility-page regression, build, search, HTML5 and internal-link audits. The attempted GSC Wizard connection is blocked by a lapsed paid subscription, so do not activate it or claim measured search improvement. Never add a paid service, scheduled run or GitHub Action.

## Turn 20 source-bounded Nolan Kido identity answer

The manifest-backed `/about/` ProfilePage now has a direct named answer at `#who-is-nolan-kido`. Home, Projects and Bio link to that same canonical About fragment, and existing About and biography evidence anchors remain. This section distinguishes Nolan's own archived Review Reply Writer and Preflight software records from the independently published 2012 *Journal of Accounting Research* byline and poker result listings. The primary code snapshots are pinned to commits, and the poker record separates independent results from first-person video commentary. These facts do **not** establish real client productivity, product adoption, a current employer or faculty role, net poker profit, official media status, or search ranking gains. Preserve the stable Person `@id` `https://nolankido.com/about/#nolan-kido`, verified `sameAs` profiles, `/about/` canonical, and all earlier fragment IDs. Home, About and Bio received meaningful November 18 content/link revisions; Projects already had a November 18 revision date. Run `_tests/test_turn20_identity_answer.py`, the deterministic builder, search metadata, HTML5 and internal-link audits. Never add unsupported career credentials, residences, private records, paid search tooling, GitHub Actions or automated publishing.

## Turn 21 source-to-claim check for nonbranded AI search advice

The existing manifest-backed `/technology/check-ai-answers/` now includes `#review-search-advice`, a dated, first-party Google source check of an **invented** claim about special GEO schema and guaranteed AI Overviews citations. The exercise distinguishes contradicted special-schema and guaranteed-citation assertions, Google's conditional rule for indexed and snippet-eligible pages, and the still-unobserved outcome of a specific site's appearance. Google docs are public primary sources for Google's own Search features, not proof of other assistants' behavior or NolanKido.com search performance. Preserve the original October 12 Article publication date, the six original methods and examples, the printable private checklist, all earlier fragments, and the existing canonical. The Technology hub, Resources and AI website visibility case link to the new answer fragment. Never change the frozen Turn 19 citation prompt file, create a separate near-duplicate article, claim measured rankings or AI mentions, add special AI search schema, or introduce paid APIs, GitHub Actions, scheduled jobs or private data. Run `_tests/test_turn21_ai_search_source_check.py` and the deterministic build, metadata, HTML5 and link checks after edits.

## Turn 22 poker solver chart-fit answer

The existing manifest-backed `/poker/evaluating-poker-advice/` now has a direct nonbranded answer at `#solver-fit-test` explaining why a 10 BB solver chart cannot settle a bubble call without matched action, pot, ante, stack, player and payout inputs. It reuses the already independently verified four-player, three-paid **fictional** no-ante case at `/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble` and the exact-fraction offline checker `downloads/ten-bb-bubble-icm.py`: 9 BB more to call into 20 BB final is a 45% chip-price threshold, while a standard classic-ICM model with $50/$30/$20/$0 payouts needs about 56.40% showdown win probability to match the fold's modeled prize equity. No actual hand is assigned a 50% win chance, and no solver run, validated range or result for Nolan's Portland Meadows 6-4 hand is claimed. The Poker hub, resource directory and preflop-chart reading guide link to the same canonical fragment. Preserve the original October 8 Article publication date, prior fragment IDs, all original guide methods, NolanPoker video evidence boundaries and the unchanged verified 10 BB code and worksheet. Test the new path with `_tests/test_turn22_poker_solver_fit_answer.py`, rerun `test_turn12_ten_bb_bubble.py` and static build, search, HTML5 and internal-link checks. No at-table advice tool, private hands, paid solver, new service, automation or GitHub Actions may be added.

## Turn 23 NolanPoker and practical AI author bridge

The existing canonical `/about/` ProfilePage now has a named answer at `#nolanpoker-ai-link` connecting Nolan Kido's first-person NolanPoker channel with his practical AI writing, through a three-step evidence path. The separate `/poker/nolan-kido/` profile links external results and channel accounts, the already published Portland Meadows Episode 1 companion records specific first-person hands, and `/technology/ai-poker-video-evidence/#poker-ai-draft` documents proposed captions using the public structured scene record and the offline checker. This **does not** establish a current-cut transcript, footage review, solver verdict, net profit, measured client result, AI-edited released video or official creator credential. The Poker hub and the original November 4 AI/poker article link to the new About answer, without changing the standalone player builder, any video files, the original Article publication date, the stable Person `@id`, verified `sameAs` list or the source records. The existing About-only stylesheet highlights the new native target on arrival, with no JavaScript. About, Poker hub and the AI/poker article carry genuine November 19 revision dates; the sitemap and relevant feeds follow the manifest. After changes run `_tests/test_turn23_nolanpoker_ai_identity_bridge.py`, `_tests/test_turn20_identity_answer.py`, `_tests/test_turn126_article_method_links.py`, the deterministic builder, search audit, HTML5 and internal-link checks. Historical tests that pin earlier revision dates should compare current manifest dates instead of treating every later substantive revision as a failure. Never publish private production notes, invent a source, add promotional identity schema or restore GitHub Actions.

## Turn 24 cross-topic AI answer and poker math audit

The existing canonical `/technology/check-ai-answers/` page now includes `#review-poker-solver-claim`, an answer to whether a confidently stated 10 BB tournament bubble call follows from a 45% chip-price threshold. Its AI claim is explicitly **invented**, not a captured model response, and its mathematical source is the already tested fictional four-player no-ante, no-bounty, no-deal case at `/poker/evaluating-poker-advice/#solver-fit-test`, the complete branches at `/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble`, and `downloads/ten-bb-bubble-icm.py`. Under those inputs, 9 BB to call into a final 20 BB pot gives a 45% direct chip-price threshold; classic ICM for $50/$30/$20/$0 payouts gives about 56.40% modeled showdown win probability to justify calling versus folding. Neither figure estimates a real opponent range, assigns actual cards, yields a solver verdict, or resolves Nolan's independently described Portland Meadows hand. The AI checking intro, Technology hub, solver-fit guide and poker research-reading map link to the same answer fragment, and its cited author-identity route is `/about/#nolanpoker-ai-link`. Preserve the October 12 and October 8 original Article publication dates, existing older claim-audit anchors and dated source checks, site Person `@id`, and six original review methods. The four genuinely edited page records carry November 19 modification dates. Run `_tests/test_turn24_ai_poker_claim_bridge.py`, historical Turn 21, Turn 22 and Turn 12 tests, deterministic builder, search, HTML5 and internal-link audits. Do not create a duplicate URL, at-table advice, chatbot experiment, ranking claim, special AI schema, private data, paid tooling, workflow or GitHub Action.

## Turn 25 sprint publication versus search outcomes closeout

The existing canonical `/technology/ai-website-visibility/` page now has a direct answer at `#site-visibility-sprint-outcome` distinguishing the 25-turn public release trail from still-unmeasured Google Search clicks, impressions, positions, AI feature appearances, assistant citations and referrals. The November 17 technical baseline had 224 sitemap URLs, versus 225 before the Turn 25 closeout on November 19; this is a URL-inventory change, not proof of indexing. Turn 24 had a separate receipt for 16 of 16 deployed public files matching tested source bytes. The source-linked table and 25-turn ledger at `_reports/visibility-sprint/seo-geo-turn25-closeout-2026-11-19.md` preserve those distinct evidence types. October 2026 is before the Nov 17 to 19 sprint, November is mixed, and December is the first fully post-sprint calendar month, subject to reporting lag. The original 25-question panel contains 20 nonbranded and five branded prompts but has **no validated real observation set** in this sprint; its first completed post-sprint run is a baseline, not measured lift. The existing eight-prompt monthly panel is separate. The Technology hub and Resources link to the closeout; no duplicate canonical page, panel files, scorecard service, background run or analytics collection is introduced. Preserve the original November 3 Article publication date, historical November 18 release example, all older anchors, the stable Person `@id`, and original external-source limits. Run `_tests/test_turn25_visibility_closeout.py`, the affected Turns 15 and 19 tests, Turn 126 Article date/link regression, static builder, metadata, HTML5 and internal-link checks. Never publish raw private Search Console exports, invented search gains, personal analytics, actual assistant response text, new paid APIs, authored GitHub Actions or scheduled monitors.

## Turn 8 local AI gaming-laptop article

The original 3,000+ word practical guide lives at `_source/technology/local-ai-gaming-laptop.html`. Its independently compiled public URL is `/technology/local-ai-gaming-laptop/`, built with `python _scripts/build_local_laptop_case.py` and verified with `--check`. The separately owned source uses an existing Technology article shell, so do not add the page to the main manifest without a reviewed ownership migration. Run `python _scripts/build.py` to update sitemap, Find and feeds after approved source changes.

The source-validated `_scripts/local_laptop_case.py` guards the canonical, shared Person `@id`, article date, native Technology-hub link, download, and explicit benchmark caveats. `downloads/local-ai-loopback-check.py` is an original local-only test with a synthetic prompt, a dry-run, a fixed `127.0.0.1` destination, rejected redirects and cloud model aliases. It does not download models or call a paid endpoint. Never change it to use remote endpoints or handle private client data by default.

Existing October 2026 Gemma smoke results were recorded on a GitHub-hosted Ubuntu CPU runner, **not** on the MSI Crosshair gaming laptop. Do not transfer those timings to a laptop-speed claim. The article does not establish exact CPU/GPU/VRAM specs, energy use, profitability, or a current measured laptop run. Source links refer to official Ollama and LM Studio docs and pinned public project artifacts. Preserve original author privacy and do not expose system reports or internal file paths.

The page is listed once in the existing sitemap, on-page Find index, Technology RSS and combined writing RSS, with a genuine 2026-11-02 publication date. Any future edits must preserve this coherent source-to-page-to-feed chain, and all tests are local-only. **Never use GitHub Actions or another scheduled CI workflow for this project.**

## Turn 9: independent AI reply evidence audit

The public `/technology/review-reply-evidence-audit/` article is owned separately from the primary site manifest. Its editable source is `_source/technology/review-reply-evidence-audit.html`; rebuild the public HTML using `python _scripts/build_reply_audit_case.py` and verify with `--check`. `_scripts/reply_audit_case.py` ensures that source, canonical, stable Person ID, November 3, 2026 Article date, Technology link, and offline audit tool stay aligned.

`downloads/review-reply-independent-audit.py` contains only **public historical model outputs for fictional customers**, plus three **deliberately altered negative controls**. The tool is a narrow lexical checker, not a replacement for the Review Reply Writer application's actual approval process. Its offline self-test initially found 0 targeted flags in 3 archived outputs and flagged all 3 deliberately corrupted controls. These numbers are not production error rates, user endorsements, real model runs, benchmark speeds, or authorization. Never upgrade "no targeted flag" into "approved." Rerun `python downloads/review-reply-independent-audit.py --self-test` and review its conditions if changing rules or fixtures.

The article appears once in the existing sitemap, Technology RSS, combined writing feed and browser-local Find directory. Any changes to these must be generated from the verified source. Run the local release checklist, not GitHub Actions. Do not publish private reviews, business policy text, client records, usernames, credentials, current unreleased model results, or personal filesystem paths.

## Public High Noon Deepstack organizer-schedule source

The Portland Meadows 2026 Wild West schedule independently establishes the
**scheduled** Thursday August 20 noon High Noon Deepstack event, $200 buy-in,
50,000 starting chips, 15-minute levels, 2:15 PM registration close, and
re-entry permitted. The PDF is publicly hosted by the organizer at
`https://img1.wsimg.com/blobby/go/d6503eb7-9b1f-4048-b895-1b68f9534a37/Wild%20West%20Schedule%202026.pdf`
and the source-limited parsed record is
`downloads/portland-meadows-organizer-schedule-2026.json`.
Card Player's 2026 Wild West festival schedule separately lists an August 20
$200 NLH Deep Stack event.

This **does not independently verify** Nolan's participation, actual date
played, 88 reported entries, $17,600 reported prize pool, $5,100
advertised top prize, $2,900 reported post-deal gross share, win, or
the details of any hand. The pre-existing scene proposal retains
`event_calendar_date_independently_verified: false` because the poster
is not a timestamped attendance or results record. Do not infer from
"re-entry permitted" that the player re-entered. Preserve the
companion's November 2 publication and November 20 modification dates,
the standalone manual builder and source parity, and existing RSS item
dates. See `_tests/test_portland_organizer_schedule.py` for regression
checks. No GitHub Actions, paid APIs or scheduled jobs.

### Festival-specific rules and prepared records request

The August 2026 Wild West program, page 2, allows players in a
heads-up pot to discuss/show cards and permits an under-the-gun live
straddle for twice the big blind. This is a festival-wide printed
rule, NOT proof either permission was used in Nolan's two reported
hands. Never add a straddle to chip arithmetic, infer shown cards,
or apply these rules to unrelated tournaments.

A public [confirmation request](https://nolankido.com/downloads/portland-meadows-aug20-event-results-confirmation-request.md)
has been drafted, NOT sent. The official venue's public poker room
phone 503-309-3087 and contact page may be listed, but do not invent
an event-records email address, claim an inquiry was sent, or post
unredacted financial, tax, identity or third-party participant data.
Do not promote any results or payment claims to independent facts
until an actual dated, independently inspectable event-specific
source is obtained. Preserve historical scene unknowns and keep the
November 2 publication and November 20 revision dates. No GitHub
Actions, scheduled jobs or externally dispatched messages.

## Portland Meadows August 20 result verification boundary

The standalone Episode 1 companion now publishes a bounded results-source
check at `#episode-result-source-status` and the dated,
machine-readable source receipt
`downloads/portland-meadows-result-source-audit-2026-11-20.json`.
The organizer's public tournament schedule independently establishes
the planned High Noon event. Card Player's festival listing confirms
its scheduled August 20 $200 Deep Stack, but the inspected festival
page did not supply results. The venue links to The Hendon Mob as
a results directory, and the checked search-indexed 2026 Portland
Meadows event listing displayed six January-April events with no
matching August 20 result; direct full archive access was blocked.

**Do not infer that no event occurred, or that the narrator's account
was false, from the limitations of these public sources.** The
reported 88 entries, $17,600 prize pool, $5,100 advertised top prize,
first-place finish and $2,900 gross post-deal personal payment are
still attributed to the first-person narrator. An organizer-issued
dated results sheet could verify the finish, while a venue-confirmed
deal or payout record would be needed to independently verify actual
post-deal proceeds. Do not publicly upload private payout or
participant information. No automatic monitoring or scheduled
verification is authorized. Maintain the original November 2
publication date, November 20 revision, source-to-output parity,
search heading and pre-existing RSS publication date.

## Standalone author book pages

The two public standalone pages at `/books/one-workflow-at-a-time/`
and `/books/how-to-play-no-limit-texas-holdem/` have full HTML
sources in `_source/books/` with byte-identical outputs in `books/`.
Edit the full source HTML, run `python _scripts/build_books.py`,
then `python _scripts/build_books.py --check`. The book builder
does not replace the main site generator, use GitHub Actions, or
make any external API calls.

`_scripts/book_pages.py` source-validates the pages before
registering their canonical URLs in the existing main sitemap
and the local Find directory. It requires native links from
Home and Creative, a unique canonical and matching OG URL,
the same author Person identifier, one H1, indexability and
Book JSON-LD without unsupported retailer claims. Keep those
requirements and `_tests/test_book_pages.py` in sync.
Run `python _scripts/build.py` and the documented local
release checks after any navigation or discovery change.

The owner describes the two books as newly published. Exact
retailer URLs, ASINs, ISBNs, publication dates, formats and
prices have not been independently verified in this release.
Do not add invented offers, dates, seller links, reviews,
ratings or sales evidence. Never restore GitHub Actions.

## Book reader companion exercises, November 20, 2026

Two original public worksheets have been added:
`downloads/one-workflow-ai-pilot-worksheet.md` and
`downloads/holdem-river-call-check-worksheet.md`. They are clearly
fictional instructional material, not official KDP excerpts, actual
client outcomes, real tournament hands, or verified solver outputs.
Their short examples appear on the respective source-backed book pages
and are linked from Creative Work. Do not replace these download
destinations with new names without updating all sources and tests.

The book landing pages still inherit the Creative Work sharing graphic.
Their alt text now explicitly says it is not an official book cover.
When legitimate edition artwork is available, replace both image URL
and alt text, and verify the artwork against an exact public edition.
Do not claim social cards are retail covers.

For changes, preserve byte-identical standalone source and output
HTML and run `python _scripts/build_books.py --check`,
`python -m unittest _tests.test_book_pages` and the documented
local release checks, without adding GitHub Actions.

## Editorial and privacy standards

- No fabricated achievements, professional credentials, current residence claims, or performance figures.
- Cite independent public sources for poker tournament results, distinguishing gross cashes from net profit.
- Do not expose private analytics, unpublished footage or documents, personal addresses, financial plans, or other private material.
- Preserve published URLs, article dates, factual provenance, identity `@id`, internal links, and established visitor pathways.
- Never use em dashes in published copy.
- Do not incur paid API charges or use new automation services without explicit permission.

The active 50-hour visibility sprint document lives in the owner's private ChatGPT Library, not this public repository. Keep private plans and authenticated analytics out of source control.
