# Repository rules for autonomous changes

This public repository builds and publishes `https://nolankido.com/`.

## Owner's permanent restriction: no GitHub Actions

**Do not create, restore, enable, dispatch, rely on, or use GitHub Actions workflows for this project.** Do not add any `.github/workflows/*.yml` or `.yaml` file. Do not introduce another CI/CD service, cron job, scheduled bot, or paid API without specific owner approval.

The former `.github/workflows/site-checks.yml` was removed intentionally on November 1, 2026. This removal is an owner instruction, not an accidental deletion. Do not bring it back for convenient automated testing or to satisfy archived historical tests.

GitHub Pages may independently run GitHub-managed deployment jobs even when there are no repository-authored workflows. These must **not** be treated as permission to run or add site test workflows. Do not promise that zero GitHub-managed deployment jobs can occur while the site remains on GitHub Pages. A total prohibition on GitHub-managed deployment requires a separately authorized hosting migration.

## How to verify instead

1. Edit `_source/` files, then generate their committed public outputs on a local machine with `python _scripts/build.py` (Python 3.10+).
2. Verify deterministic output with `python _scripts/build.py --check`.
3. Run `python _scripts/check_search.py --verify-snapshot _reports/search-audit.json` and `python _tests/check_html5.py` locally. This flags stale committed SEO reports in addition to real site defects. Install `requirements-test.txt` only in a local environment when needed.
   If the report legitimately changes after a content release, regenerate it with `python _scripts/check_search.py --json _reports/search-audit.json`, review the committed diff and rerun `--verify-snapshot`. Never hand-edit its counts.
4. For full verification, run `python -m unittest discover -s _tests -p 'test_*.py' -v` and browser suites locally with the installed Playwright dependencies. Use direct public GETs to verify deployed URLs and expected source bytes.
5. Report test scope precisely. Do not claim that the full suite or browsers passed unless they actually ran. Never reenable GitHub Actions as a shortcut.

For a single-release download receipt, use `python _scripts/check_live.py --only /downloads/gsc-period-compare.py --attempts 3 --interval 5` from a complete checked-out repository. The route must be present in the explicit public inventory. The default with no `--only` still tests all targets. `URLError`/DNS failures are inconclusive; do not call them 404s or proven deployment failures. Successful exact bytes prove serving, not search visibility.

For a bounded production smoke check after a release, use `python _tests/diagnose_live_crawl.py --scope priority --attempts 2 --interval 2` from a complete checkout with network access. This includes both author book pages, the Books catalog, the 10 BB companion, the two book worksheets, and the Search Console Python downloads. The structured report distinguishes `status=pass` (exit 0, exact expected bytes), `status=fail` (exit 1, at least one observed HTTP or byte mismatch), and `status=inconclusive` (exit 2, only unresolved DNS/network/transport errors). A separate diagnostic GET cannot convert a failed exact-byte check into success. Never interpret a general content-fetching tool's `target_unreachable` result as HTTP 404 without a status-bearing HTTP observation.

### Complete local release coverage

Install `requirements-test.txt` in a local virtual environment, then run `python _scripts/local_release_checks.py`. The default checklist includes the two Portland Meadows companion builders, the Reserve Day 1 companion builder, the search audit, and HTML5 parsing of all manifest pages plus ten independently registered standalone HTML pages: six non-book manual pages, two author book pages, the Books catalog and the 10 BB Playbook. `--full` additionally runs the historical unit suite; `--browser` additionally runs the local browser scripts. A failed standalone build must fail the checklist.

The local HTML5 release check also parses every complete HTML document under `/downloads/` registered in `_scripts/check_live.py` for exact-byte public GET checks. The current four resources are two poker hand-review practice HTML documents and two NolanPoker after-play video QA tools. They remain `noindex` and are not canonical sitemap pages. A new registered HTML download must be parsable or the release check fails. Run `_tests/test_turn63_public_html_downloads.py` and `_tests/check_html5.py` locally. No remote CI or new scheduled process.

`_scripts/search_entrypoints.py` must preserve the later of a page's actual content revision and its search-copy revision. An older search-description record must not backdate a later content change in structured data or the sitemap. Do not advance dates merely because a build ran.

Regenerate page outlines and reading estimates after source edits. The standalone Episode 1 command example uses the existing `poker-details` wrapper so command text wraps on narrow screens without changing copied commands. Test standalone reading routes at 320 pixels as well as desktop widths. HTML validity and a passing local browser check do not independently verify the current YouTube audio or footage.

`assets/standalone-section-arrivals.css` belongs only to the standalone player profile and independent reply audit. After changing it, run both `python _scripts/build_player_profile.py` and `python _scripts/build_reply_audit_case.py` to refresh their content-versioned links, then run the main build check. Do not add it to their shared hub/article shells. Preserve the existing heading IDs, `#main` skip targets and profile `#creator-introduction` bookmark. `_tests/standalone_reader_arrivals_browser.py` checks native arrivals with ordinary/enlarged text and committed/fallback fonts; a CSS-only change must not advance content dates.

## Turn 44 RightsReceipt source-to-software-test route

The existing canonical `/technology/rightsreceipt-ai-licensing/` now has an early `#rightsreceipt-software-proof` reader link directly to the **pinned** public local judge console, application-handler smoke, local learned-model diagnostic and original blank `downloads/rightsreceipt-local-software-acceptance.md` worksheet. The worksheet maps observed source files, runnable local commands, required success fields, a deliberately visible wrong model territory suggestion, and the human and payment gates still missing. It does not complete a genuinely paid PayPal Sandbox invoice, create a legal license, prove ownership, or run any unreviewed code on the reader's behalf. Keep the November 13 article publication date, Article canonical, seven-section reader outline and eight-minute estimate. The source repository at commit `646182a95faf6ab5448f10927ded1650ff38bdf5` is a historical sanitized public snapshot; do not silently substitute later private commits or imply a new independent Node test run. The site publishes a portable acceptance *method*, not real human approvals or real-world results. Run `_tests/test_turn44_rightsreceipt_software_proof.py`, the original `_tests/test_rightsreceipt_public_case.py`, build, HTML5 and internal-link checks, then verify deployed files. No GitHub Actions, recurring jobs, paid services or private credentials.

## Turn 46 source-backed AI reliability and stop rules

The existing canonical `/technology/check-ai-answers/` now includes one early `#review-stop-rules` H3 decision matrix, accessible from the `/technology/` Checking task group, and a standalone public owner-private worksheet at `downloads/ai-stop-rules-field-guide.md`. The matrix uses four *different* published cases: the October 11 historical HTML5 parser error after 347 earlier tests; the October 2026 archived fictional-review model response and separate four constructed checker blind-spot probes; the real local synthetic RightsReceipt model diagnostic alongside simulated payment responses; and the AI-assisted NolanPoker caption proposals whose current export has not been verified. Keep each source type, recorded failure, and external human/provider approval separate. PROCEED IN SCOPE, REVISE AND RECHECK, HOLD and STOP USING AI FOR THIS TASK are human decision categories, not automated verdicts. A green checker never authorizes a business promise, a license, a payment or a video graphic. Keep total human preparation, checks, corrections, setup and upkeep visible; the six-case paired review-reply productivity trial is not completed.

This is a substantive comparison update. The guide retains `date=2026-10-12`, moves `updated` to **2026-11-20** with a truthful revised Article and sitemap date, and its displayed reading estimate advances from **22 to 24 minutes**. Keep the 9 original H2 method/record sections and six original fictional example disclosures. Do not add FAQPage or special GEO markup, a duplicate canonical, new tracking, unapproved model calls, confidential reviews or GitHub Actions. The existing historical November 19 poker claim and November 18 Google search advice remain attributed to their own original checks. Run `_tests/test_turn46_ai_stop_rules.py`, plus Turn 21 and Turn 24 regression modules, the deterministic build, search snapshot, HTML5 and local links. `_scripts/check_live.py` registers the new field guide as a fixed read-only public byte target. New source content and generated public HTML must agree, including the revision label, Article modification date, reading estimate and sitemap `lastmod`. Live publication and search performance require separate observation.

## Turn 45 small-business review reply decision lab

The existing canonical `/technology/local-ai-review-replies/` now exposes `#reply-operator-decision` within its existing `#reply-owner-gate` section. Its already published private-use `downloads/review-reply-owner-approval-checklist.md` has an expanded operator decision table, explicit owner-only authorization boundaries and a reproducible **fictional** counterexample using the existing standard-library `downloads/reply-audit-boundary-probes.py --self-test`. That probe's four constructed additions produce one agreement, two missed monetary offers and one quotation false alarm against the independent narrow public screen; they are NOT model outputs or an estimated error rate. The October 13 Gemma case timings are model-stage observations only, the October 29 run produced 29 template drafts and one block with zero model calls and zero owner assessments, and the frozen six-case paired time study is a plan with zero completed pairs. Never merge those cohorts into a performance metric. Human decisions are HOLD for unsupported reimbursement or gifts, REVISE for omitted source details, REVIEW IN CONTEXT for a quotation and APPROVE only for the exact independently checked, owner-authorized saved text, manually posted if appropriate. Keep private reviews and owner policies out of GitHub. Existing article original `date=2026-10-27` and `updated=2026-11-18` stay unchanged because this article edit adds a contextual demonstration and direct offline-probe route to an earlier published owner-gate section, not a restated historical model evaluation; the linked checklist is revised separately. Its original 13 H2 anchors, single checklist link within the gate, local source parity and 14-minute reader estimate must remain. Register both public audit scripts and the checklist as exact-byte GET targets. Run `_tests/test_turn45_reply_owner_decision_lab.py`, `_tests/test_turn17_review_reply_owner_gate.py` and other relevant offline checks, then the normal local build, metadata, HTML5 and internal-link checks. No AI service, customer platform, cron or GitHub Actions may be invoked.

## Turn 45 project-to-evidence paths

The canonical `/projects/` and `/ai-in-real-life/` hubs now link readers directly into `/technology/rightsreceipt-ai-licensing/#rightsreceipt-software-proof` and to the already published `/downloads/rightsreceipt-local-software-acceptance.md` worksheet. Change only the relevant RightsReceipt section in each source and generated hub page; do not create duplicate RightsReceipt articles, present speculative keyword volume as demand, or claim simulated PayPal events were real payments. The `Projects` hub retains `updated=2026-11-18` and the `AI in Real Life` hub retains `updated=2026-11-20`, because this turn is a bounded contextual link improvement, not a newly published article or material project rerun. The RightsReceipt evidence article remains published November 13. All three canonicals, sitemap entries and section IDs remain. Run `_tests/test_turn45_project_proof_navigation.py` and the existing `_tests/test_turn44_rightsreceipt_software_proof.py`, build, search snapshot, HTML5 and internal link checks from a complete checkout. Post-merge live retrieval and exact-byte verification are separate. No GitHub Actions, paid APIs, new tracker or private data.

## Standalone poker player profile

The public `/poker/nolan-kido/` page has its own deterministic local builder because the main site's generated manifest does not yet have a personal-player-profile type. Edit `_source/poker/nolan-kido-profile.html`, then run `python _scripts/build_player_profile.py` and `python _scripts/build_player_profile.py --check`. The generated page deliberately lacks the main generator marker so the main build will not overwrite it. Both Poker and About have native links to it. `_scripts/player_sitemap.py` registers this one source-verified, manually built URL in the **existing main sitemap** and in read-only live-byte targets. Run `python _scripts/build.py` after any profile URL, canonical or review-date change to update the sitemap. The on-site Find page additionally includes this manually built public profile through the bounded `_scripts/player_find.py` adapter. Its source-verified title, description and canonical route are searchable locally under the **Player profiles** filter. The main manifest continues to own the other entries, and this addition does not add a new remote search service or index personal records outside the public page. Run `python _scripts/local_release_checks.py` to verify both the Find projection and sitemap without GitHub Actions. Keep documented tournament citations and the gross-versus-net caveat. Do not add the page to the main manifest without migrating its build ownership and search verification together.

## Public poker video companions

The first public episode uses the source file `_source/poker/portland-meadows-ep1.html` and the independently compiled `/poker/episodes/portland-meadows-ep1/index.html`. Build it locally using `python _scripts/build_poker_episode.py`, then check it with `--check`. The source-validated `_scripts/poker_episode.py` registry allows the Poker hub to advertise the video only when the exact source and canonical Article page exist, and links to the public YouTube video without an iframe. The existing sitemap and on-site Find index include only this verified manual video route. The newer public Episode 1 cut replaced an earlier private version 7 upload. Old chapter offsets were removed in Turn 10 and must not be restored until checked against the current video. Do not publish unverified scenes, payouts, opponent identities, videos or private drafts. Keep the four-way deal's actual reported $2,900 payment distinct from the $5,100 advertised top prize. Preserve manual page ownership until the main generator has a reviewed migration path. Never use GitHub Actions for release tests.

## Turn 60: repair an incomplete Bayesian range-update expression without invented opponent evidence

The canonical /poker/poker-under-uncertainty/ research essay had an explicit "The range-update process can be represented as:" sentence immediately followed by prose, with the promised expression missing. The existing section already modeled class priors value/draw/bluff as (3/10, 9/20, 1/4) and invented action likelihoods (4/5, 3/5, 1/5). Two new paragraphs at #bayes-range-update-formula and #bayes-range-update-check now show the card-filtered class-prior-times-likelihood normalized over feasible hands, and reproduce masses (0.24,0.27,0.05), denominator 0.56 and exact shares 3/7, 27/56 and 5/56. Known cards K eliminate blocked combinations before betting likelihoods are applied. These are fictional weights, not observed player tendencies, copied solver recommendations or a licensed live-play aid. Reuse the published evidence in downloads/poker-under-uncertainty-evidence.json and the existing offline reproduction script.

Keep all 190 native MathML formula elements, all tables/images, the 50-minute reading estimate, the original October 14 2026 publication and the existing canonical. Only the substantive November 20 2026 modification, Article metadata and sitemap lastmod change. The historic uncertainty predecessor test should project out this subsequently revised current article when assessing the predecessor inventory; retain its mutation, evidence, 190-formula and evaluator safeguards. The new standard-library test_turn60_bayes_update.py recomputes the prior/likelihood/posterior from the actual evidence fixture and checks source/output passages, blockers, publication and negative controls. No new PDF, page, external tool, GitHub Action, scheduled monitoring or claimed ranking gain.

## Turn 59: reconcile individual net cash to the actual hypothetical payout ladder

The existing canonical /poker/tournament-entry-prize-pool-ledger/ had a real internal inconsistency: its $39,600 fictional ten-place ladder has a minimum $1,000 tenth-place cash, but its later individual net example used $950 in that same invented event. The two net calculations were individually accurate for the wrong cash amount. The updated page anchors its real fictional tenth-place $1,000 award to the two-entry and one-entry personal cases: $1,000 less two $400 entries and $60 costs is +$140, while one entry and those costs leaves +$540. No payout after two entries and $60 costs remains -$860. The eighth original reveal question now tests the mistaken +$540 versus +$140 comparison, retaining all eight reveal panels and three original tables. All other entry/bounty/guarantee and fee calculations remain untouched.

The source and compiled guide each have a single ledger-personal-cash-check anchor, linked from the payout-table text. The new independent regression at _tests/test_turn59_payout_consistency.py extracts all ten actual placement awards from the guide, checks their total and lowest prize and rejects personal cash not in the same fictional payout schedule, incorrect gross-to-net math and a stale practice answer. The older test_poker_tournament_entry_pool.py was corrected, not disabled. Preserve the original November 15 2026 publication and old historical Turn 14 report, with the material correction dated November 20 2026 in the canonical page and sitemap. The blank personal worksheet remains unchanged; the page still takes approximately 12 minutes to read. Do not introduce CI, GitHub Actions, cron jobs, paid APIs or invented real-world event outcomes. Run the local generator, legacy unit tests and browser/HTML5 checks separately before claiming a full verified release.

## Turn 58: actor-specific eight BB shove and conditional event scope

The existing /poker/six-to-ten-bb-tournament-decisions/#bridge-ev is a fictional nine-handed BBA branch tree, not an action-complete solver, real opponent model or completed tournament-prize model. New paragraphs at #bridge-ev-break-even, #bridge-ev-two-prices and #bridge-ev-action-gate distinguish the CO's zero-fold shove break-even conditional win probability 16/35 (45.71%) from the covering BB's additional-call price 2/5 (40%). Other exact roots: f = 2/7 (28.57% joint all-folds) if q is 40%, and q = 97/245 (39.59% BB-only called wins) if f is 30%. The f=30%, q=40% scenario gains only 0.05 BB; at f=28%, q=40% it loses 0.02 BB. f is the joint all-fold event across BTN, SB and BB. In the nonfold branch BTN/SB fold and BB alone calls. These hypothetical conditional inputs cannot rank a smaller two-BB open, a limp, a BTN/SB call, a multiway pot, or a payout-sensitive decision.

The fixed-input Python reproduction at downloads/eight-bb-shove-branch-verify.py uses exact fractions, no files, no network and no opponent ranges. The new _tests/test_turn58_shove_branch.py verifies script output with independent branch events, source/public text parity, publication dates, reading times and negative controls. Maintain source and compiled page parity. Preserve the original November 15, 2026 publication date, the distinct November 18 bubble ICM addition and the November 20 substantive revision date; its editorial estimate is now 24 minutes in the canonical page, Poker Library, tournament topic and strategy topic. Retain all nine reveal panels, the four tables and the source-limited Portland Meadows hand caveats. Historic Turn 12 and Turn 55 date assertions were adjusted to the real new revision without eliminating their safeguards. Register the script with the exact-byte public inventory; run full local generator, HTML5/internal links and browser checks separately, with no GitHub Actions, cron, paid solvers, or fabricated search/AI metrics.

## Turn 57: public exact three-player ICM proof and payout sensitivity

The existing /poker/tournament-equity/ is a fictional 10/10/10 chip-transfer example with no blinds, antes, ties or genuine hand/range. Its new download at downloads/tournament-equity-three-player-verify.py uses only standard-library exact fractions and enumerates finish orders. The three distinct $100 prize ladders have required win probabilities 4/7 (50/30/20), 5/8 (60/40/0), and 1/2 (100/0/0). At a hypothetical 55% win probability under the original ladder, the hero gains one chip in expectation but loses half a dollar of modeled prize equity; the uninvolved player gains 10/3 modeled prize dollars without receiving actual cash at the hand. These are not poker solver outputs or real hand advice.

Keep October 6 2026 as original article date, November 20 2026 as latest revision, one canonical article, source-generated HTML parity and the seven-minute reading estimate on the article plus Poker Library and tournament-topic listings. The reader script is registered in the exact-byte live inventory. The new offline test is _tests/test_turn57_icm_prize_audit.py. Do not introduce GitHub Actions, paid services, account data, an at-table assistant or fabricated SEO/GEO performance. Run the local deterministic builder, historical workshop test, source snapshot and HTML checks separately before claiming a fully validated release.

## Turn 56: citation-backed short all-in reopening arithmetic

The existing `/poker/poker-rules-and-fair-play/` owns the authority comparison and now has `#reopening-per-player`, sourced to the official 2026 Poker TDA Rule 49 illustration. Fictional postflop action: A bets 100, B all-in 125, C calls 125, D all-in 200, E calls 200. Neither short increase of 25 or 75 is a full 100 raise, but together they total 100: A faces a full raise relative to A's original 100 and may raise to at least 300. After A only calls 200, C last acted at 125 and faces 75 more, so C cannot re-raise. Never apply one table-wide reopen boolean without tracking player action history. Preserve the venue-adopted rules, limits and floor-ruling caveat, the original October 8 publication, the new November 20 Article revision, and the distinct October 16 rules-directory source recheck. The older betting primer has only a native link to this named answer, and keeps its original publication/review date. Test with `_tests/test_turn56_tda_reopening.py` and the site release checks. No private hands, at-table strategy tool, new canonical route, GitHub Actions, paid API or fabricated search-results claim.

## Turn 55: after-watch hand evidence and separate free practice

The existing six-card Poker gallery retains all public YouTube IDs, exact titles and original source-bound video links. Only the three cards with written companions now provide clearer actions: the Deepstack card links a distinct `/poker/six-to-ten-bb-tournament-decisions/#bridge-practice` nine-question fictional workshop; the Stand Off card links directly to `/poker/episodes/portland-meadows-standoff/#standoff-second-decision` for the original second-decision question; Reserve Day 1 now links to `/poker/episodes/reserve-day-1/#reserve-questions` as well as its original main/side-pot discussion. The two existing `#nolanpoker-hand-study` shortcuts and four-case study bridge remain in place. Existing other videos still have no fabricated companions or hand details.

Inside the existing source-bounded companion answer areas, Deepstack links onward to the fictional nine-question 6–10 BB workshop and the `#study-loop` independent stack-record exercise; Stand Off's current `#icm-call` link is explicitly identified as a separate fictional model, not a solved A-K choice; Reserve's three hand-review questions now lead to the different-stacks `/poker/side-pot-lab/#all-in-action` fictional main/side/refund exercise. Preserve source-to-output paragraph parity for the three manually built companion pages, the canonical original/updated dates, and after-play versus at-table boundaries. No new media, upload, solver, paid API, analytics, external scripts, or GitHub Actions. Run `test_turn55_video_to_practice.py`, source-generators for three companions, `build.py --check`, `check_search.py --verify-snapshot`, HTML5 and internal link tests. Static checks and passing source files are not proof of the newly deployed site until read-only public checks confirm it.

## Turn 54 NolanPoker public listing and companion navigation integrity

The six curated NolanPoker gallery titles and exact watch-page video IDs were rechecked from public YouTube watch-page metadata on November 20 (Hawaii). They match `_source/poker/nolanpoker-video-thumbnails.json`, whose original November 13 oEmbed title/channel/image review and November 18 Reserve update are retained as historical provenance. The current pass **did not independently recheck channel byline, local thumbnail bytes, frames or audio**, and does not certify any current-video chapter offsets. The downloadable `downloads/nolanpoker-video-title-link-audit-2026-11-20.json` enumerates the six exact title/URL pairs, three published companions and scope of timestamp evidence. The public Poker hub exposes it inside its existing evidence section at `#nolanpoker-current-title-check`, preserving all six video cards and their existing order. No new video or duplicate site page.

The Deepstack companion's secondary-video paragraph previously used an outdated seven-BB Reserve packaging label and incorrectly suggested Stand Off and Reserve had no source-bounded written companions. It now uses the verified video titles and direct paths to both existing companions. Preserve the archived-current-cut distinction, original publication and modification dates, established source/public paragraph parity and human video-approval unknowns. Run `test_turn54_nolanpoker_listing_accuracy.py`, `test_turn40_poker_videos.py`, `test_turn150_nolanpoker_thumbnails.py`, the relevant video companion build checks and the normal local release checks. Do not reactivate GitHub Actions or claim traffic improvement from link accuracy.

## Turn 53 real published written-companion change

The canonical `/technology/ai-poker-video-evidence/` now shows one genuine *written* before-and-after: GitHub parent `788e3f44e09d0fc5a93a38bec138867fca492637` had no `#episode-current-transcript` in the Portland Meadows public companion; commit `4f3449cd40cf5b165b756d2c4c2fce9aa3827c67` added viewer-visible transcript starting points. The current public companion HTML was independently fetched and the section was present. That source-to-site release is NOT a verified change to the current video cut. AI-generated captions remain site-only proposals, not proven overlays. The public transcript record reports that audio and frames could not be inspected, and the public scene proposal still has `current_public_cut_timestamps_checked: false`, `current_public_cut_graphics_checked: false`, `human_release_approval: false`. The expanded evidence ledger Section M retains these distinctions. Keep the AI article's original 2026-11-04 publication and 2026-11-20 revision date, six H2 topics, correct ten-minute reading estimate, single canonical and Person identity. `_tests/test_turn53_poker_published_revision.py` protects the before/after and video gate. Run source build, search snapshot, HTML5, internal links and post-release HTTP check separately. Do not invent video verification, SEO outcomes, paid tools, CI workflows or new personal data.

### Turn 43 published content-production receipt

The published AI/poker editorial case at `/technology/ai-poker-video-evidence/` now shows `#poker-ai-publication-status` before the evidence sections. Its downloadable `downloads/nolanpoker-content-production-receipt.md` gives a five-stage, source-linked publishing account. **The written companion and AI-assisted editorial article are published. The three AI-proposed captions are published in the article as draft examples only.** Do not claim they appear in the current video or that video graphics, timestamps, privacy permissions or human caption approval are verified. The associated structured JSON deliberately retains `human_release_approval: false` and `current_public_cut_graphics_checked: false`. Keep the original November 2 companion and November 4 article publication dates, the latest meaningful article modification date, all six existing headings, the nine-minute reading estimate, and the one canonical article route. Do not create a duplicate article, add invented net profit or solver results, or rerun historical tests in prose. Use `_tests/test_turn43_published_content_receipt.py`, `_tests/test_turn35_ai_poker_case.py`, the deterministic builder, HTML5 and local link checks. `_scripts/check_live.py` registers the receipt as an exact-byte public target. Do not add GitHub Actions, background checks, or paid APIs.

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

## Turn 40 predeclared frozen assistant-answer audit

The frozen 25-prompt panel and original Turn 19 script remain in place. To prevent an assistant or browsing mode from being substituted after an unfavorable answer, first copy `downloads/ai-answer-sprint-25-roster-blank.csv` to an owner-private folder and write the exact planned `assistant,mode` combinations before testing. For every completed trial, separately record the **exact text actually submitted in the assistant interface** in a private copy of `downloads/ai-answer-sprint-25-submitted-prompts-blank.csv`; do not copy expected text from the frozen prompt file as a substitute for inspecting the submitted query. The existing private observation log retains original headers and statuses. Use `downloads/ai-answer-sprint-25-audit.py --roster <private-roster.csv> --submitted-prompts <private-submitted-prompts.csv>` along with the existing required month, mode count, frozen prompts, and observations flags. Strict mode demands both evidence files. The new code rejects wrong modes, incomplete evidence, and even minor changes to frozen question wording. A real but altered question is an **excluded pilot**, not a completed frozen-panel trial. A third-party text response without a genuine clickable site citation is not an on-site citation. The checker can verify copied text against the frozen file, not authenticate a screenshot or an assistant's actual UI. Store individual answers, assistant URLs, any screenshots, prompt evidence, date/time, and saved audits only outside this public repository; never commit private measurement logs, insert them into PR comments, or infer a citation rate from an incomplete panel. Run `_tests/test_turn40_frozen_observation_integrity.py` and `_tests/test_turn19_frozen_answer_panel.py`. Do not alter the panel SHA-256, add GitHub Actions, paid APIs or background queries.

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

## Turn 52: standalone 10 BB course and exact prize-equity audit

The manually authored `poker/10bb/index.html` is a distinct, **already public** one-hour NolanPoker video-study companion, not a manifest-generated Poker guide. It now includes a single `#icm-reproduce` exercise backed by `downloads/ten-bb-playbook-icm-verify.py`, a standard-library, no-network, exact-fraction three-player ICM enumeration. Keep the original November 19 publication date and the November 20 substantive modification date; the 45%, 50%, 55% and 60% examples are invented probability inputs, not observed ranges. The three-player classic-ICM threshold is `63/107` (58.88%) under $100/$60/$40 prizes and post-action stacks 9/21/5, 20/10/5, 0/30/5. This is a different model from the four-player 56.40% bubble example elsewhere on the site. Do not claim a solver verdict, a result from live footage, a measured win rate, at-table assistance or a new paid API.

`_scripts/tenbb_companion.py` now verifies the existing canonical/Article identity, original date, revision date and the downloadable audit before adding exactly one `/poker/10bb/` URL to the generated XML sitemap. `_scripts/check_search.py` adds this approved manual entry to expected indexed canonicals, and the committed JSON snapshot must stay generated and current. `_scripts/check_live.py` registers both the canonical standalone page and the Python audit as read-only exact-byte GET targets. The existing manifest still owns all other Poker guides. No new runtime server, schema gimmick, GitHub Actions, automatic cron or tracking is authorized. Run `test_turn52_10bb_playbook.py`, existing short-stack/ICM tests, `build.py --check`, `check_search.py --verify-snapshot`, HTML5 and internal links; verify live HTTP separately and do not confuse successful code merge with indexing.

## Turn 65 on-site 10 BB Playbook discoverability

The published standalone `/poker/10bb/` page is now a native result in the noindex `/find/` site directory. Edit its source-of-truth `poker/10bb/index.html` and keep `_scripts/tenbb_companion.py` registration current; `_scripts/player_find.py` derives the local search result title and description from the verified public HTML and Article metadata, with the original November 19 publication date. Do not fabricate extra keywords or a new indexed duplicate page. `_scripts/search_sections.py` projects only its eight visible named H2 sections, not hidden answers or the H3 practice prompts. The Poker Find group has 113 cards at this release and the section index includes `poker/10bb/`. Regenerate `find/index.html` from the main deterministic builder after edits, then run `test_turn65_tenbb_find.py`, `test_player_find.py`, `test_search_sections.py`, `build.py --check`, HTML5, local link checks and a separate public retrieval. The 230-URL sitemap and original 10 BB Article dates are not changed by this navigation-only update. No new API, tracking, scheduled tool, or GitHub Actions.

## Turn 66 contextual Poker routes into the 10 BB Playbook

The existing Poker hub `_source/poker/home.html` and six-to-ten-blind guide `_source/poker/six-to-ten-bb-tournament-decisions.html` now link directly to two distinct sections of the published standalone Playbook. The hub sends short-stack readers to `/poker/10bb/#practice-title` for six independently answered practice questions. The six-to-ten guide sends readers to `/poker/10bb/#icm-title` for a **different** three-player prize model; its own four-player bubble case retains distinct assumptions and results. The two links are contextual educational handoffs, not a solver-backed starting range, a source-verified live hand, or a search-ranking claim.

Edit the two source files, regenerate their public HTML together, and preserve existing canonical paths, original dates, sitemap counts and unrelated guidance. Because this is a narrow navigation improvement, keep the material revision dates at November 20 until a further substantive page change. `_tests/test_turn66_tenbb_reader_paths.py` checks source/public paragraph parity, unique and valid anchors, model distinctions, unchanged 24-minute reading estimate, and rebuild parity. The older `test_turn152_short_stack_route.py` now validates the complete reader link sequence, rather than wrongly assuming a three-link-only navigation and an obsolete November 16 date. Run both local test modules, `build.py --check`, `check_search.py --verify-snapshot`, HTML5 and link checks, plus a separate live GET after deployment. No new GitHub Actions, paid API, tracking or private user data.

## Turn 70: keep historical SEO closeouts separate from current site inventory

The published `/technology/ai-website-visibility/` article retains a **November 19, 25-turn** SEO/GEO/AEO closeout. Its 224-to-225 sitemap inventory and verified release details describe that period, not the whole site as of November 21. Do not rewrite the old table, recast the 25-turn number as the latest sprint count, or imply observed indexing, clicks, rankings or assistant citations. A separately marked November 21 paragraph now reports the independently retrieved **230-URL live sitemap** and three reachable learning paths, linking to the source-backed Turn 69 correction. This is publication/discovery evidence only, not evidence of search performance.

Edit `_source/technology/ai-website-visibility.html` first, then regenerate its public HTML from the deterministic builder. The dated paragraph must appear once in the source and in the published body with exactly the same accessible native links. Preserve the original Article publication date **November 3, 2026**, while moving the substantive modification, JSON-LD, and single sitemap `lastmod` for this canonical route to November 21. The site remains at 230 sitemap URLs, with no new landing page or tracking. The existing 25-turn historical source and frozen citation panel must remain unaltered. The short update does not add an H2 or change the reviewed reading estimate of about 17 minutes.

Run `test_turn70_visibility_case_current_status.py` and the original `test_turn25_visibility_closeout.py` under the manual local release suite, plus `build.py --check`, `check_search.py --verify-snapshot`, HTML5, internal links, and separate status-bearing production checks. No user-authored GitHub Actions, cron, subscription, speculative measurement or fabricated claim of reader conversion.

## Turn 69: source-check case learning paths

The existing `/technology/check-ai-summary/` fictional summary-review guide and `/technology/organize-public-notes/` recorded eight-note case now point to different **verified public sections** of the already published `/technology/ai-weekly-reset/` recorded editing example. The summary guide links to `#notes-case-sources` for original public inputs and checked rewrite; the notes case links to `#notes-case-checks` for claim-level checks. In both locations, a source-backed editorial example is a *different class of evidence* from an observed household calendar, a client deployment, or a measured time saving.

Keep the original summary's six fictional findings and repairs and the original eight-note case's retained response and offline reproduction untouched. The new paragraphs are simple contextual links, not extra AI model calls or new landing pages. The source and generated public HTML must contain the same paragraph exactly once, and the two target IDs must each exist exactly once. Both article original dates remain October 12 and October 27, respectively. The November 21 source changes now appear in the manifest's `updated` fields, Article JSON-LD and single sitemap `lastmod` entries; the sitemap still contains 230 canonical URLs. The AI weekly-reset target is unchanged.

Run `_tests/test_turn69_ai_source_case_links.py`, `test_turn29_source_notes_audit.py`, `test_summary_review.py`, `build.py --check`, `check_search.py --verify-snapshot`, HTML5 parsing, offline links and the manual release suite. In the new summary guide source check, confirm the visible reading estimate against the generator before declaring final parity. Do not reenable GitHub Actions, paid services, automation or conversion tracking, and do not claim measured search impact.

## Turn 68: direct practical AI workflow pilot reader route

The existing canonical `/technology/ai-workflow-pilot/#pilot-protocol` is now linked from two visitor starting points: a short question-driven paragraph after the **three unchanged Home practical-choice cards** in `_source/home.html`, and a separate small-business paragraph immediately after the **four unchanged Start Here task choices** in `_source/start-here.html`. Keep those two original choice/card counts, the Home hero's three distinct native actions, the six links under Home's optional disclosure, and both pages' accessible headings and keyboard order. Use source files and the normal deterministic builder; do not insert the same link through a separate generated-content source.

The pilot article already contains an independently runnable six-case **fictional** worksheet and offline calculator. New linked copy says the numbers are not measured business savings; no client outcome, conversion or AI productivity improvement is inferred. The source guide, its originally published date, and the site's existing privacy-focused analytics configuration remain unchanged. The Home and Start Here published files, their JSON-LD modification dates, source manifest updates and exactly two `sitemap.xml` lastmod entries now say November 21, 2026. Maintain the current 230 canonical sitemap URLs. No extra indexable keyword page, tracking parameter, external call, paid API, cron or GitHub Actions.

Run `_tests/test_turn68_workflow_pilot_discovery.py`, the original Turn 50 hero and homepage practical-choice tests, Start Here navigation/browser tests, the deterministic builder, search audit snapshot, local links, HTML5 and status-bearing production checks when a full checkout is available. Static checks alone do not establish reader completion, Google search ranking or assistant citations.

## Turn 67: written 10 BB Playbook and unverified video status

The canonical `/poker/10bb/` is an independently usable **written** study guide with a published November 19, 2026 date and a substantive November 21 correction. It retains the original six checks, fictional decision fixtures, exact-fraction ICM audit and six answered exercises. A specific public NolanPoker course-video URL was **not verified**, so the old one-hour video promise, unlinked 00:00 through 1:00:02 chapter timing and "Video 58:58" labels must not be restored as public facts. The page now states the video evidence limit, links only to the public channel, and offers eight native links to its own valid lesson headings. A later independently verified public video may receive its own source-checked watch link and chapter synchronization, but cannot be inferred from a working edit.

Its `<title>`, public metadata, Article `headline` and the native `/find/` result now identify a **written Poker study guide**, not a known uploaded companion. `_scripts/player_find.py` validates the exact public metadata and returns a `guide` record; the existing Find section JSON uses the revised `#chapter-map-title` heading, and all eight H2 section routes still resolve. The playbook's original Article `datePublished` remains November 19 while the visible revision, `dateModified` and sitemap `lastmod` move together to November 21. The sitemap still has 230 canonical URLs, and the noindex Find utility remains separate.

Run `_tests/test_turn67_playbook_standalone.py` with the updated Turn 52, 65, 66 regression tests, `build.py --check`, `check_search.py --verify-snapshot`, `_tests/check_html5.py`, `check_internal_links.py`, and actual status-bearing live verification. No new hosted checker, GitHub Actions, paid API or analytics instrumentation. Do not treat code review or text extraction as proof that a browser or final video playback passed.

## Turn 50 first-screen identity and direct evidence

The Home hero's single `nav.link-row.identity-actions` contains three native task links in this order: the actual recorded website repair `/technology/checking-ai-website-changes/`, the browser-local free task-brief utility `/technology/task-brief/`, and the unchanged `#home-proof-title` cross-domain evidence anchor. The prior six-way menu duplicated the site's global navigation and consumed more room at narrow widths. Keep the existing global subject menu (including Poker), the separately tested mobile `#selected-reading-title` shortcut, all underlying case pages and distinct evidence categories.

The About introduction has one native `nav.link-row.about-first-proof` immediately after the intro and before `#who-is-nolan-kido`. It goes to the same recorded website repair and `/projects/#projects-checks`. These are source-backed navigation routes, not new testimonials, client success measurements, current job credentials, or evidence of ranking increases. The long About evidence and existing `about-jump-nav` retain their IDs and order. Reuse existing `.button`, `.text-link`, and `.link-row` responsive/keyboard styles. Do not add scripts, duplicate schema or GitHub Actions. Run `_tests/test_turn50_first_screen_identity.py`, current-source build/search/HTML5/internal-link checks and live mobile/keyboard checks where available; static inspection is not a full usability test.

## Turn 49 follow-up: catalog choice-to-practice consolidation

Concurrent work merged Turn 49's **topical guide-to-book sample and reciprocal guide links** first. The later, smaller refinement has been based on that merged `main`, rather than cherry-picking older versions of those five article files or weakening its `_tests/test_turn49_topic_book_paths.py` test. In the existing canonical `/books/` catalog, each of the two comparison cards retains exactly one book-root title link and one topical free guide but now jumps to the shared `#books-catalog-free-learning` section. The Free exercises section contains exactly one link to each book's original website sample `#ai-book-first-exercise` or `#poker-book-first-exercise` and exactly one matching downloadable free worksheet. Do not promote the same worksheet twice by repeating it inside the comparison card. These materials are original site-only exercises, not verified retail excerpts. The Home books section retains a single Books catalog link and one root link per author book; a duplicate overview link into Creative Work was removed and replaced with the truthful retail/excerpt scope. About, Creative Work, and Bio remain unchanged because biography and public evidence references serve distinct functions.

The separate previous Turn 49 work remains authoritative for the three topical articles and reciprocal book links. Preserve the single root link and single sample deep-link in each guide; the intended source and generated page paragraphs should match. Both existing standalone Book work identities, author Person IDs, sitemap dates, retailer-unknown ledger, title canonical paths and original worksheets remain unchanged. Run both `_tests/test_turn49_topic_book_paths.py` and `_tests/test_turn49_book_catalog_handoff.py`, the standalone book build/check tests, full site builder, HTML5, search audit and internal links when a complete checkout is available. No GitHub Actions, paid APIs, traffic claims or new indexable book page.

## Turn 49 topic-to-book navigation

The free `/technology/ai-workflow-pilot/`, `/poker/no-limit-holdem-guide/` and `/poker/poker-books-and-courses/` articles have a single unfragmented author book link, one direct original website-example link and the existing free worksheet. Keep the poker books comparison clearly first-person, not an independent review. The book pages link back to `#pilot-protocol` and `#choose-your-route` in the free canonical guides. No genuine book excerpts or retail offers are verified. Home, About, Bio, Creative and Books catalog were audited but not changed in Turn 49. Keep current Book Person IDs, publication metadata and canonical URLs, and avoid duplicate promotional blocks. Run `test_turn49_topic_book_paths.py` with the full local build/search/HTML5/link/browser checks. Do not reactivate GitHub Actions.

## Turn 48 reader-first book pages and mobile/keyboard boundaries

The existing two standalone author book pages at `/books/one-workflow-at-a-time/` and `/books/how-to-play-no-limit-texas-holdem/` now include one named `nav.shell.book-reader-jumps` after the page hero with four native destinations: who the book serves, the original teaching example, free practice, and the existing edition-evidence section. Each page also has one `details.book-sample-answer` with a native `summary`, a site-original fictional practice question, and an answer that distinguishes arithmetic from missing evidence. These are **independent website exercises**, NOT book chapter excerpts or examples asserted to match the final owned retail edition. Do not claim an excerpt, purchase availability, customer/sales result or poker profit without verification.

The new `assets/book-reader-journey.css` is scoped to the two book page body classes and loaded using `?v=20261120`. It enforces 44px link/summary targets, wraps on narrow screens (including 320px), preserves `:focus-visible` cues and forced-color contrast, and makes native answer text printable. Do not add inline styles, JavaScript dependencies, focus traps, horizontal page scrolling, a fifth Book schema entry, or duplicate `href="/books/"` links. Source and rendered standalone files must remain **byte-identical**. The original Book JSON-LD `Person` link, the November 20 modification date and both verified/unverified edition distinctions remain unchanged. No invented official book cover, ASIN, ISBN or retailer URL.

Run `_tests/test_turn48_book_reader_journeys.py` and `_tests/test_book_pages.py`, including the `_scripts/build_books.py --check` standalone copy test and the rest of the manual release checks. For actual mobile visual acceptance, check **320px**, 375px and desktop layouts, tab order (skip, page navigation, practice summary, worksheet), the native summary opening with Enter/Space, no horizontal overflow, and destination fragments that remain readable. Source/CSS checks are not the same as a rendered browser test, so report which were actually run. No GitHub Actions or background automation.

## Turn 47 verified book-work versus retailer-edition boundaries

The canonical /books/ catalog and two standalone author book pages now expose `/downloads/nolan-kido-book-edition-verification.md` and `/downloads/nolan-kido-book-edition-evidence.json`. The public JSON contains exactly **two author-described works with three separately unverified format slots each** (Kindle eBook, paperback, hardcover). All retailer-specific ASIN, print ISBN-13, full listing title, byline, product URL, publisher/imprint, publication date, cover URL and evidence date values are deliberately `null`. "Not independently verified" means **unknown**, not "unpublished", "out of stock" or "not sold". Do not insert a guessed Amazon `/dp/` URL, ISBN, ASIN, Kindle Unlimited status, publisher name, price or official cover from unrelated search hits, private KDP screenshots, another pen name, or a first-party book description. The KDP primary publisher directions at `https://kdp.amazon.com/en_US/help/topic/GPYDJ3SECAVVPNVG` explain to find the exact `View on Amazon` URL on the author's Bookshelf, then independently compare each publicly served listing's title, author, format, identifiers and cover. KDP says eBook ISBNs are optional but print ISBNs required. A public Amazon listing may take time to show in ordinary search; non-discovery is not proof of nonpublication.

The original three book-related canonical pages already had modification dates of **2026-11-20**, so this same-day evidence improvement does not invent a new retail release or change the global `_scripts/book_pages.py` date; source and generated HTML stay byte-identical. Add retail identifiers only after reviewing an exact public product page. The regression `_tests/test_turn47_book_edition_evidence.py` deliberately fails closed on fabricated retailer details in the current unverified JSON baseline. Future verified publication records require a source-backed review of that policy and tests. The six-format ledger does not access an owner's private KDP account, and the publisher's public Help pages are **instructions**, not evidence of these books' product statuses. Run `_scripts/build_books.py --check`, `test_turn47_book_edition_evidence.py`, `test_book_pages.py`, full local builder, HTML5, SEO and live-byte tests. Do not add GitHub Actions, cron, paid APIs or private email correspondence.

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

## Book subject metadata and contextual guide links

Both standalone book pages use existing 1200-by-630 topic graphics from
`assets/social/` for social sharing. These are **not official cover art**;
keep the exact image URL and honest alternative text aligned. The
`WebPage.about` Book identifier must match its `mainEntity.Book.@id`,
while `Book.author` continues to point to the shared Nolan Kido Person
identifier. The `Book.mainEntityOfPage` links back to the canonical
WebPage. Do not add unsupported retail edition, pricing or sales claims.

The AI workflow pilot guide, poker books and courses guide, and
long-form no-limit Hold'em guide provide contextual outbound links
to the two book pages and publicly free worksheets. Preserve original
article publication dates and only advance actual modification dates,
together with XML sitemap lastmod and generated Article metadata.
Run the standalone book test and full local build checks. No GitHub
Actions or scheduled background jobs.

## Author biography and book entity relationship

The public `/bio/` page identifies the two nonfiction book works with
first-party descriptions, author-provided companion resources, and a
specific source limitation: retail editions and ASINs remain unverified.
Do not convert an author book description into independent proof of
publication date, format, retailer availability, ratings or sales.

The separate `_source/person-schema.jsonld` identity graph now includes
two abstract `Book` work nodes that repeat only the identities, author
and descriptions from the exact standalone book pages. Regenerate its
public mirror at `assets/nolan-kido-identity.jsonld` using the existing
main builder. Preserve the pre-existing WebSite, Person and scholarly
article nodes, with the same Person `@id`. Do not embed the larger
standalone graph in Home, About, Bio or Poker pages merely to solicit
a rich result. Book actions require a separate Google provider feed
and do not follow from a personal author site's `Book` JSON-LD.

When modifying `/bio/`, update its manifest metadata, rendered file,
existing Find result and sitemap lastmod consistently. Run the related
book and identity tests along with the local release checks.

## Search audit and local release verification for standalone books

Standalone book publication is now a required release check, not an optional
out-of-band page. The site search audit must register the two exact canonical
`Book` pages before comparing the existing XML sitemap. The HTML5 inventory
must parse both public book pages, and `_scripts/check_live.py` must compare
exact served bytes for both HTML routes, both original companion Markdown
worksheets, and their two existing subject-image cards.

The local release runner now checks `_scripts/build_books.py --check`
and the standalone `test_book_pages.py` contracts without CI. Preserve the
minimum temporary-site semantics: when both source and public page for a book
are absent, it is not an approved publication; if only one is present,
the audit must fail closed. Never add GitHub Actions.

The search-audit report is a static source inventory, not actual ranking,
indexing or traffic measurement. Do not infer that the
snapshot's old page count is the current sitemap. Regenerate the audit
using `python _scripts/check_search.py --json _reports/search-audit.json`
on a complete local checkout and check all reported errors before describing
it as a passing current run. Book metadata still must not invent seller,
edition, datePublished, ISBN, rating, sale or official cover claims.

## Current SEO audit inventory and provenance, November 20, 2026

The formerly committed search-audit snapshot described only 200 pages and
was no longer representative of the published 228-URL sitemap. This
release reconciles the canonical inventory: 225 manifest-backed pages,
five excluded utility routes within those pages, six other published
standalone pages, and two separately published books. Its current
`_reports/search-audit.json` values are reconstructed from the published
manifests, checked-in HTML metadata and the sitemap. The complete Python
release suite could not be executed inside the GitHub connector session.

Do not portray a rebuilt source snapshot as independently confirmed
Google Search Console indexing, search ranking, traffic or citations
by ChatGPT or other assistants. On a local checkout, run
`python _scripts/check_search.py --json _reports/search-audit.json`
and compare the newly generated report to the committed snapshot,
then run `python _scripts/local_release_checks.py`. Investigate
every discrepancy rather than lowering assertions or omitting books.
No GitHub Actions, alternative cron jobs or paid service required.

## Books catalog source and approval boundary

The first-party author catalog at `/books/` is a static,
source-backed CollectionPage with an ItemList referencing the exact two
existing Book work IDs. Its owner files are
`_source/books/index.html` and `books/index.html`.
The standalone book builder copies and checks this source alongside
both individual Book pages. The registry `_scripts/book_pages.py`
validates the catalog's canonical URL, shared Person identity, exact
two-book membership, indexability, source parity, and native links
from Home, About, Bio and Creative before approving it for the
sitemap and Find directory.

The new catalog is one more independently owned public page, not a
third Book and not an additional title with unverified retail metadata.
The expected static source inventory is now 229 canonical sitemap
URLs: 225 manifest-backed pages including five noindex utilities,
six other standalone pages, two Book pages, and one catalog page.
The HTML5 inventory includes nine standalone pages. Source-only
book descriptions and free worksheets remain clearly distinguished
from confirmed publisher or Amazon/KDP edition information.

Keep the catalog and two Book pages bidirectionally connected. For
a publication update, update the exact HTML source and output copies,
then regenerate `find/index.html` and `sitemap.xml` from the
main builder and rerun the non-CI local checks. Never add scheduled
web jobs, GitHub Actions, paid APIs, unverified publication details
or manufactured search-ranking claims.

## Editorial and privacy standards

- No fabricated achievements, professional credentials, current residence claims, or performance figures.
- Cite independent public sources for poker tournament results, distinguishing gross cashes from net profit.
- Do not expose private analytics, unpublished footage or documents, personal addresses, financial plans, or other private material.
- Preserve published URLs, article dates, factual provenance, identity `@id`, internal links, and established visitor pathways.
- Never use em dashes in published copy.
- Do not incur paid API charges or use new automation services without explicit permission.

The active 50-hour visibility sprint document lives in the owner's private ChatGPT Library, not this public repository. Keep private plans and authenticated analytics out of source control.

## Turn 71 first-visit evidence route and offline mobile checks

The existing `/start-here/` projects section includes one link to the
source-checked historical website repair at
`/technology/checking-ai-website-changes/`. Edit the owner source
`_source/start-here.html` and regenerate `start-here/index.html` together.
The link is evidence of one independently detected markup defect and a
reusable release checklist, not proof of faster AI work, search gains,
client outcomes or a newly executed parser run. Preserve the existing
2026-11-21 modification date, canonical route and project list.

Run `_tests/test_turn71_start_here_release_navigation.py` for direct
source/public consistency, evidence availability and negative controls.
The new manual browser suite
`_tests/visibility_core_journeys_browser.py` tests Home, Start Here,
Technology, Books and Poker 10 BB at 320, 390, 768 and 1440 CSS pixels,
including 200 percent text at narrow widths, with scripts and network
disabled. Its stylesheet loader includes `/styles.css` and `/assets/`
stylesheets at their original positions relative to inline CSS.
It cannot establish real-user task completion, live deployment, search
rankings, Web Vitals or mobile touch behavior. The new test must actually
run with a local Chromium before its checks may be marked passed.
Use `python _scripts/local_release_checks.py --full --browser` from a
complete checkout; no user-authored GitHub Actions, cron or paid service.

## Turn 72 three-journey live-verification and worksheet boundary

The existing manually authored `/poker/10bb/` written guide has two public
teaching downloads: `downloads/ten-bb-playbook-icm-verify.py` and
`downloads/ten-bb-tournament-checklist.md`. Treat both as required
release assets. `_scripts/tenbb_companion.py` must reject a missing
worksheet file or removed worksheet link; `_scripts/check_live.py`
must register both for status-bearing exact-byte comparison.

The priority `_tests/diagnose_live_crawl.py` now includes Start Here,
the original source-checked AI repair, the dated site-visibility case,
the free AI pilot, and the actual three reader-journey downloads.
This diagnostic classifies unreachable network/DNS paths as inconclusive,
not false HTTP 404s. Only an exact-byte GET against the matching checkout
can certify a public release.

`_tests/visibility_three_reader_journeys_browser.py` tests keyboard
activation at 320, 390 and 1440 CSS pixels, with JavaScript both enabled
and disabled. It follows Home or Start Here to real AI repair evidence,
the Books catalog to an author book worksheet, and the Poker hub to
the standalone 10 BB worksheet. A local 127.0.0.1 server serves actual
checked-in HTML, CSS and downloads; all other browser hosts are blocked.
A local successful download or DOM route is not live deployment proof.
Run it with installed Playwright/Chromium where loopback HTTP is permitted.
An execution environment that blocks loopback navigation is **not run**
or **inconclusive**, never a passing local browser result.

Run `_tests/test_turn72_reader_release_coverage.py`,
`_tests/test_turn38_live_evidence.py`, `_tests/test_turn52_10bb_playbook.py`,
the main builder, search snapshot, HTML5 and internal-link checks.
The existing manual release runner discovers the new browser script
only with `--browser`. After merge, run status-bearing priority
diagnostics with matching source bytes from a full checkout.
No GitHub Actions, paid verification provider, new tracking or cron.

## Turn 73 source-pinned public release receipts

`_tests/diagnose_live_crawl.py` now records which registered URLs actually
passed the existing status-bearing exact-byte `check_live.check()` verifier.
Each `verified_routes` entry is added only after a successful public GET
comparison, with the expected HTTP status, SHA-256 of the matching checked-out
source bytes, attempt number, and the verifier's success message.
An expected 404 negative-control document may legitimately have a successful
receipt if its exact release error-body is returned. `observed_failure_routes`
and `inconclusive_routes` remain separate; never describe DNS failures,
text extraction, merged GitHub commits, or a source SHA alone as a verified
public-byte match.

Use bounded `--only` selections for a recent release, e.g.:

`python _tests/diagnose_live_crawl.py --scope priority --only /start-here/ --only /poker/10bb/ --only /downloads/ten-bb-tournament-checklist.md`

Only existing registered priority routes may be selected in priority mode.
Duplicates and unknown routes must fail closed. The full default priority
inventory remains intact. The dated proof of a live page's **content**
retrievability is distinct from this checker, because a content extractor
does not provide status-bearing, original-response bytes.

Run `_tests/test_turn73_live_byte_receipts.py` for synthetic pass, expected
404, retries, mixed failures and false-positive safeguards. The existing
`_scripts/local_release_checks.py` runs it locally; no GitHub Actions,
scheduled service or additional subscription is authorized.

## Turn 74 canonical route integrity for exact-byte release checks

The read-only `check_live.check()` verifier must not accept matching bytes
from a different URL path. The existing `SameOriginRedirect` allows
safe same-origin redirects, but `check()` now verifies that
`response.geturl()` has the original HTTPS origin and registered route.
A query-only rewrite such as stripping `?release-check` is permitted
when the route path remains unchanged. A redirect to another page, an
`index.html` alias, a changed host or a changed scheme fails as an observed
HTTP release mismatch even when the response body has the expected bytes.

Expected 404 negative-control routes are checked against their original
requested path with the same rule. Keep the HTTP status and byte checks
separate. The new message begins `HTTP ` so the existing
`_tests/diagnose_live_crawl.py` classifies it as a confirmed mismatch
rather than a transport error. DNS, TLS and blocked environments still
remain inconclusive, never assumed HTTP 404.

Run `_tests/test_turn74_final_route_guard.py` for local mock-response
positive and negative controls and the prior Turn 38/73 release tests.
Nine independently run isolated checks demonstrated the guard behavior
on November 21, 2026, but that is not a full checkout test or a public
live-byte receipt. Use `python _scripts/local_release_checks.py --full
--browser` from a complete checkout with installed dependencies,
then the priority exact-byte diagnostic from a network-capable
environment. No GitHub Actions, cron, paid services or new tracking.

## Turn 75 case-to-checklist reader handoff

The documented AI website repair article at
`/technology/checking-ai-website-changes/` must keep the original pinned
pre-repair and repaired source links, its October 11 original publication
date, its November 18 substantive modification date and its single
documented release fact record. The original free Markdown runbook at
`/downloads/website-check-offline-runbook.md` is now linked immediately
after the early evidence note and before the reader jump navigation,
rather than only near the end of the long case.

Edit `_source/technology/checking-ai-website-changes.html` and generated
`technology/checking-ai-website-changes/index.html` together. This turn
moves an existing paragraph, with no new H2 or factual assertion, and
deliberately leaves the same reading estimate and article dates intact.
Keep the runbook link once in this case, with its existing `download`
attribute, and leave the pinned historical proof note byte-identical.
Run `test_turn75_early_case_checklist.py`, the Turn 42 repair-proof tests,
build/check, HTML5, internal links and applicable local browser suites.
Do not mark mobile browser or source-to-live byte checks passed until
executed from a complete local checkout. No new GitHub Actions or
paid search service.

## Turn 76: keep historical 10 BB Find fixtures aligned with required assets

Turn 72 made the free `downloads/ten-bb-tournament-checklist.md` worksheet a
required publication dependency alongside `poker/10bb/index.html` and
`downloads/ten-bb-playbook-icm-verify.py`. The historical temporary-site
test in `_tests/test_turn65_tenbb_find.py` had continued to copy only the
page and Python checker before asserting successful registration. That
assertion contradicts the current release validator.

The test fixture now copies all three published assets before expecting
`player_find.tenbb_entry(root)` to succeed, and explicitly checks that
removing the worksheet after successful registration fails closed.
Do not weaken `tenbb_companion.record()` just to satisfy old fixtures.
Historical recorded Turn 65 results remain unchanged; this test is a
current-contract correction, not a retroactive rewrite of that release.

The isolated `tenbb_companion.py` module, copied byte-for-byte from GitHub
blob `1dacc7d910a140cf8194965270f545b1ee0c1e69`, was tested against
four constructed temporary-file states (all behaved as expected). That is
not a full `unittest`, site build, browser or production GET pass.
Run the already-registered `test_turn65_tenbb_find.py` together with
`test_turn72_reader_release_coverage.py`, deterministic build, HTML5,
internal links and the optional manual browser suite from a complete
checkout before claiming release-wide verification. No Actions or paid tools.

## Turn 77: do not treat an orphaned public worksheet as an absent Playbook

All three 10 BB Playbook assets are required together: the manually
published `/poker/10bb/` HTML page, the exact-fraction Python ICM checker,
and the free `downloads/ten-bb-tournament-checklist.md` worksheet.
`_scripts/player_find.py` previously returned `None` when the page and
checker were missing, even if the worksheet was present. This silently
treated a partial manual release as an unpublished resource in the
site's local Find discovery. The `tenbb_entry` presence guard now checks
all three required assets. An entirely absent publication still returns
`None`; any nonempty but incomplete asset set must go through
`tenbb_companion.record(root)` and fail closed.

`_tests/test_turn65_tenbb_find.py` exercises the worksheet-only case
and ensures it becomes genuinely absent again when the orphaned worksheet
is deleted. Keep the preceding Turn 76 three-file fixture correction and
the original Find card count/metadata constraints. Run that existing
test module, Turn 72 release coverage, source builder, HTML5 and manual
browser checks from a complete checkout. The standalone five-case
presence-predicate smoke is not a full repository unittest or live GET.
No new canonical pages, altered publication dates, GitHub Actions,
automations, paid services or measured discovery claims.
