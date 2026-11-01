# Visibility sprint, Turn 5: Nolan Kido's player-profile landing page

**Date:** November 1, 2026
**Scope:** Public, independently sourced tournament player profile; native linking from Poker and About.
**Branch:** `visibility-sprint-turn05-player-page-20261101`
**Status:** Merged to GitHub main November 1, 2026. Deployed URL could not be independently fetched in the current session; public live-byte verification remains open.

## What the change delivers

The new canonical page `https://nolankido.com/poker/nolan-kido/` gives a reader a concise, independently checkable account of Nolan Kido's participation in tournament poker, across no-limit hold'em and Omaha. It also explains the decision-review and poker-video project without claiming that unfinished episodes have been published.

Four selected, dated, independently listed finishes:

| Date | Event | Result | Independent evidence |
| --- | --- | --- | --- |
| 2026-06-25 | South Point Lucky 300, No-Limit Hold'em, 1,652 entries | 5th | [The Hendon Mob](https://pokerdb.thehendonmob.com/event.php?a=r&n=1399113), also [GPI](https://www.globalpokerindex.com/tournaments/2026/united-states/lucky-300-no-limit-hold-em-1590392/) |
| 2026-08-10 through 2026-08-11 | Harrah's Cherokee, WSOP Circuit #8, 8-Max PLO, 341 entries | 13th | [Official WSOP event results](https://www.wsop.com/tournaments/result/17989/) |
| 2026-09-30 through 2026-10-02 | Thunder Valley, WSOP Circuit #10 Monster Stack NLH, 638 entries | 20th | [Official WSOP event results](https://www.wsop.com/tournaments/result/18650/) |
| 2025-08-20 | Graton Casino, WSOP Circuit #9 Limit Omaha Eight-or-Better, 101 entries | 4th | [Official WSOP event results](https://www.wsop.com/tournaments/result/14147/) |

The page links to [Nolan Kido's official WSOP player profile](https://www.wsop.com/players/448066374/nolan-kido/), [GPI](https://www.globalpokerindex.com/poker-players/nolan-kido-1314580/) and [The Hendon Mob](https://pokerdb.thehendonmob.com/player.php?a=r&n=967363). The numbers above concern listed individual events, not lifetime statistics or net returns.

The page explicitly avoids claims of WSOP rings, bracelets, professional status, poker profitability, current residence, or published videos. Tournament cashes are gross event payouts and do not establish profit after reentries, travel, non-cashing entries, or staking.

## Technical implementation

- `_source/poker/nolan-kido-profile.html`: editable original player-profile content.
- `_scripts/build_player_profile.py`: independent deterministic, network-free build and `--check` mode using the existing published Poker shell, consistent site navigation and shared Person `@id`.
- `poker/nolan-kido/index.html`: new indexable public page with one H1, one breadcrumb, one canonical URL, coherent Open Graph/Twitter metadata and Schema.org `WebPage` identity linking to `/about/#nolan-kido`. Its only runtime script is the already-approved site pageview script.
- `_source/poker/home.html`, `poker/index.html`, `_source/about.html`, `about/index.html`: a single native link from each of two editorial locations, with source and output staying in sync.
- `_scripts/local_release_checks.py`: adds source equality for this standalone page to the locally run gate. `AGENTS.md` explains its ownership and the continuing absolute prohibition on repository GitHub Actions.
- Dedicated tests: `_tests/test_visibility_poker_player_page.py` and `_tests/test_profile_links_turn05_history.py`, plus exact historic predecessor adapters. Older snapshots are not rewritten.

The new page is deliberately **not** inserted into `_source/pages.json`: the main generator would own and replace it, and synchronizing the full manifest, related search indexes and sitemap needs a separate full-repository validation. The current route is crawlable through native links from Poker and About, but **is not yet included in the main sitemap or the generated site search index**. Completing that migration is the next technical task when a complete local checkout and test environment is accessible.

## Verification and limits

- The four independent event results were checked against the actual event listings on November 1, 2026.
- The committed standalone HTML was independently reassembled from the current Poker shell and editable profile body. Result: **exact text/byte equality** (13,018 UTF-8 characters in the reviewed version).
- The four existing source/generated files have **only one reviewed native-link insertion each**, verified by fetching the exact parent-commit version through GitHub and reversing the insertion.
- The new page has a unique canonical and H1, matching social and structured-data URLs, the stable Nolan Kido Person identity, the existing tracker only, and no new account, form, exposed personal details or client data collection.
- Full Python unit and browser suites have **not** been executed in the current session because the execution container lacks an authenticated or public-network checkout of the whole repository. The exact Python standalone compiler check is available for local execution via `python _scripts/local_release_checks.py`; do not mistake static comparison for an executed full suite.
- No repository GitHub Actions workflow exists, was invoked, or should be restored. GitHub Pages' platform-managed deployment is separate from this prohibition.
- No rankings, indexing status, search-console impressions, assistant citations, earnings, or viewer satisfaction gains have been measured.

## Release checklist

On merge, verify the branch content exists on main and direct HTTPS GETs for `/poker/nolan-kido/`, `/poker/` and `/about/` return the new canonical content. A GitHub merge or Pages build status is not alone proof that the public URL serves the intended bytes. Update the private sprint ledger only after those checks, and record remaining sitemap integration separately.

## November 1 merge receipt and remaining release verification

- [PR #159](https://github.com/nolankido/nolankido.github.io/pull/159) was squash-merged directly to GitHub `main` at commit `9dca4e95343abe3355f84f3903185e1bd68a80dc`.
- Read-only GitHub fetch of `main` confirmed that `poker/nolan-kido/index.html`, its deterministic compiler, and native links in `poker/index.html` and `about/index.html` are present. It also confirmed the repo's `.github/workflows` directory is absent.
- The directly assembled profile body, metadata and schema matched the 13,018-character committed page in a separate JavaScript cross-check. Nineteen static scope, identity, source and privacy assertions passed, but the Python/compiler and full browser suites were **not** executed in the current sandbox.
- The external public-page reader did **not** return a usable result for `https://nolankido.com/poker/nolan-kido/` immediately after merge. That could reflect crawler freshness or deployment and does **not** prove the page is live. Independent public HTTP status and exact bytes remain **unverified**.
- Do not publish a false assertion of live availability, indexing, search rankings or AI citations. Verify the public route in a later local/browser check. Migrate into the main generated manifest and sitemap only when the full site build can be executed and verified locally, without restoring GitHub Actions.
