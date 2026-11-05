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

The public Poker hub and standalone player profile now link three independently accessible YouTube uploads (Portland Meadows Deepstack, evening Stand Off, and WSOP Circuit Reserve Day 1). The first and second now have distinct source-limited written companions; the second is based on an archived v9 packet and does not verify the current YouTube cut. Reserve Day 1 does not yet have a written hand companion. Maintain separate video and companion labels, do not invent hand outcomes or timestamps, and preserve tournament listing citations and the gross-versus-net caveat. Edit the Poker hub at `_source/poker/home.html`, run the main builder, edit the player source at `_source/poker/nolan-kido-profile.html`, and rerun its standalone builder. The player's metadata, Find card and main sitemap must agree on the current reviewed title, description and modification date. Use local release checks; never add GitHub Actions.

## Turn 8 local AI gaming-laptop article

The original 3,000+ word practical guide lives at `_source/technology/local-ai-gaming-laptop.html`. Its independently compiled public URL is `/technology/local-ai-gaming-laptop/`, built with `python _scripts/build_local_laptop_case.py` and verified with `--check`. The separately owned source uses an existing Technology article shell, so do not add the page to the main manifest without a reviewed ownership migration. Run `python _scripts/build.py` to update sitemap, Find and feeds after approved source changes.

The source-validated `_scripts/local_laptop_case.py` guards the canonical, shared Person `@id`, article date, native Technology-hub link, download, and explicit benchmark caveats. `downloads/local-ai-loopback-check.py` is an original local-only test with a synthetic prompt, a dry-run, a fixed `127.0.0.1` destination, rejected redirects and cloud model aliases. It does not download models or call a paid endpoint. Never change it to use remote endpoints or handle private client data by default.

Existing October 2026 Gemma smoke results were recorded on a GitHub-hosted Ubuntu CPU runner, **not** on the MSI Crosshair gaming laptop. Do not transfer those timings to a laptop-speed claim. The article does not establish exact CPU/GPU/VRAM specs, energy use, profitability, or a current measured laptop run. Source links refer to official Ollama and LM Studio docs and pinned public project artifacts. Preserve original author privacy and do not expose system reports or internal file paths.

The page is listed once in the existing sitemap, on-page Find index, Technology RSS and combined writing RSS, with a genuine 2026-11-02 publication date. Any future edits must preserve this coherent source-to-page-to-feed chain, and all tests are local-only. **Never use GitHub Actions or another scheduled CI workflow for this project.**

## Turn 9: independent AI reply evidence audit

The public `/technology/review-reply-evidence-audit/` article is owned separately from the primary site manifest. Its editable source is `_source/technology/review-reply-evidence-audit.html`; rebuild the public HTML using `python _scripts/build_reply_audit_case.py` and verify with `--check`. `_scripts/reply_audit_case.py` ensures that source, canonical, stable Person ID, November 3, 2026 Article date, Technology link, and offline audit tool stay aligned.

`downloads/review-reply-independent-audit.py` contains only **public historical model outputs for fictional customers**, plus three **deliberately altered negative controls**. The tool is a narrow lexical checker, not a replacement for the Review Reply Writer application's actual approval process. Its offline self-test initially found 0 targeted flags in 3 archived outputs and flagged all 3 deliberately corrupted controls. These numbers are not production error rates, user endorsements, real model runs, benchmark speeds, or authorization. Never upgrade "no targeted flag" into "approved." Rerun `python downloads/review-reply-independent-audit.py --self-test` and review its conditions if changing rules or fixtures.

The article appears once in the existing sitemap, Technology RSS, combined writing feed and browser-local Find directory. Any changes to these must be generated from the verified source. Run the local release checklist, not GitHub Actions. Do not publish private reviews, business policy text, client records, usernames, credentials, current unreleased model results, or personal filesystem paths.

## Editorial and privacy standards

- No fabricated achievements, professional credentials, current residence claims, or performance figures.
- Cite independent public sources for poker tournament results, distinguishing gross cashes from net profit.
- Do not expose private analytics, unpublished footage or documents, personal addresses, financial plans, or other private material.
- Preserve published URLs, article dates, factual provenance, identity `@id`, internal links, and established visitor pathways.
- Never use em dashes in published copy.
- Do not incur paid API charges or use new automation services without explicit permission.

The active 50-hour visibility sprint document lives in the owner's private ChatGPT Library, not this public repository. Keep private plans and authenticated analytics out of source control.
