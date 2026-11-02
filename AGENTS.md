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

The first public episode uses the source file `_source/poker/portland-meadows-ep1.html` and the independently compiled `/poker/episodes/portland-meadows-ep1/index.html`. Build it locally using `python _scripts/build_poker_episode.py`, then check it with `--check`. The source-validated `_scripts/poker_episode.py` registry allows the Poker hub to advertise the video only when the exact source and canonical Article page exist, and links to the public YouTube video without an iframe. The existing sitemap and on-site Find index include only this verified manual video route. Chapter timestamps reflect the public version 7 edit map and must be reviewed if the video changes. Do not publish unverified scenes, payouts, opponent identities, videos or private drafts. Keep the four-way deal's actual reported $2,900 payment distinct from the $5,100 advertised top prize. Preserve manual page ownership until the main generator has a reviewed migration path. Never use GitHub Actions for release tests.

## Editorial and privacy standards

- No fabricated achievements, professional credentials, current residence claims, or performance figures.
- Cite independent public sources for poker tournament results, distinguishing gross cashes from net profit.
- Do not expose private analytics, unpublished footage or documents, personal addresses, financial plans, or other private material.
- Preserve published URLs, article dates, factual provenance, identity `@id`, internal links, and established visitor pathways.
- Never use em dashes in published copy.
- Do not incur paid API charges or use new automation services without explicit permission.

The active 50-hour visibility sprint document lives in the owner's private ChatGPT Library, not this public repository. Keep private plans and authenticated analytics out of source control.
