# Original incremental game lab: from private interest to public teaching material

Prepared: November 13, 2026

## Why this turn

The About page already described game development as a personal interest, but
there was no independently inspectable public game-related material to support
that interest. Public verification did not establish a released personal game
that could be described accurately in a project case. The conservative next
step is an original browser-local teaching demonstration with explicit limits.

## Published materials

- `/creative/incremental-game-loop/`: a first-minute incremental game design
  guide with a playable sparks economy, the complete price curves, an exact
  worked sequence, discussion of design tradeoffs, and a reproducible proposal
  for observing player decisions.
- `assets/incremental-game-loop.js`: deterministic pure rules with isolated
  browser controls, 15-purchase caps, pause/resume, reset, and no background
  or offline catch-up. No account, storage, tracking code, AI model call, or
  outgoing request is needed to play.
- `assets/incremental-game-loop.css`: accessible, responsive interface scoped
  to the game lab. A JavaScript-free fallback keeps the rule explanation and
  download available.
- `downloads/incremental-game-first-minute-playtest.md`: blank observation
  worksheet with consent, player words, time-stamped actions, confounders,
  and hypothesis checks separated from interpretations.

## Identity, search, and publication routes

- The article has one canonical URL, a distinct description, article-type
  Open Graph metadata, a dated `Article` structured record with a named
  author, and a `SoftwareApplication` `mainEntity` for the demo.
- The manifest makes this a `creative_article`, so future creative articles
  can use the same editorial archive path. This new published page appears
  once in the full author archive, its structured `ItemList`, site search,
  and the sitemap.
- A new route from the existing About wine-and-games section makes game
  development discoverable alongside the wine learning guide. The Creative
  hub surfaces the playable demo and a practical making route. The public
  Projects portfolio labels it as a teaching demo rather than a shipped game.
- The new page links to its public source code, blank worksheet, the Creative
  hub, About, Technology, and the evidence-separated Projects portfolio.

## Claims deliberately withheld

This release does not name any nonpublic game repository, reveal its code,
assert a commercial game launch, state that anyone has completed a playtest,
claim measured enjoyment or retention, or imply search-engine indexing or
AI answer placement. The written sample run is a reproducible arithmetic
example rather than a captured outside participant session.

## Local verification

- `python _scripts/build.py --check`: deterministic build without drift.
- `node _tests/incremental_game_loop_smoke.cjs`: pure economy calculations
  and mocked browser controls, including visibility, pause, goal, and reset.
- `_tests/test_incremental_game_loop.py`: publication, metadata, links,
  safe claims, archives, download, and live-byte target contracts.
- `_tests/test_author_archive_standalone.py`: the new creative Article is
  included in all published-article counts and both archive presentations.
- `python _scripts/check_search.py`: 208 unique public titles,
  descriptions and sitemap URLs, including 117 Article records, no errors.
- `python _scripts/check_internal_links.py`: 14,373 local links across
  213 public HTML pages, no issues.
- `python _tests/check_html5.py`: 213 HTML pages parsed, no failures.
- `python _scripts/local_release_checks.py`: **88/88 current local release
  groups passed**. No GitHub Actions were invoked.
- The headless Chromium visual check could not start in this sandbox because
  Chromium's socket creation was denied. The JavaScript state and control
  interactions were exercised with an isolated DOM mock instead. Visual
  behavior on deployed desktop and mobile browsers remains unverified.

No GitHub Actions, background cron, third-party analytics, paid API, or
private user-data collection were added.
