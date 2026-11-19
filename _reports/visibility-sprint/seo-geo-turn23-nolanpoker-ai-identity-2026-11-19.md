# SEO/GEO/AEO visibility sprint, Turn 23 of 25

**Date:** November 19, 2026 (Honolulu)

**Scope:** A source-bounded identity bridge between Nolan Kido, the NolanPoker channel, and one documented AI-assisted editorial exercise.

**Primary answer:** https://nolankido.com/about/#nolanpoker-ai-link

## Observed gap

The site already used the stable `https://nolankido.com/about/#nolan-kido` Person identifier, a verified public-work `sameAs` set, named author links, an introductory identity answer, an independently source-linked poker profile, and the original AI/poker editing case. Their relationship was scattered across several pages. Searchers asking whether NolanPoker is the same Nolan Kido who writes about practical AI did not have a concise, bounded answer with a stepwise path to the different evidence types.

## Published change set

1. `_source/about.html` adds a direct first-person answer at `#nolanpoker-ai-link`. Three ordered evidence steps lead from channel and independently listed finishes, through archived first-person Portland Meadows hand accounts, to an AI-assisted draft and offline checker. It explains what none of those records verify.
2. `_source/poker/home.html` adds a descriptive link from the existing NolanPoker video/profile route to the About answer.
3. `_source/technology/ai-poker-video-evidence.html` links back to the same answer near the case introduction. The page's three proposed captions, source JSON, fact gate, original publication date and current-video disclaimer are preserved.
4. `_source/pages.json` records genuine November 19 changes to About, Poker hub and the AI/poker article, while keeping that article's November 4 publication date. Its description now names Nolan Kido and NolanPoker alongside the narrow check.
5. `assets/about-reader.css` gives the new native heading fragment an outline on arrival, inheriting existing mobile scroll offsets and touch-target rules. No script is added.
6. README and AGENTS document the public route, source boundaries and local verification requirements. The deterministic builder refreshes the affected static outputs, including local Find entries, feeds and sitemap. No new public article URL, schema type, remote service or feed is created.

## Claim-to-evidence chain

| Public statement | Evidence | Boundary |
| --- | --- | --- |
| Nolan Kido publishes the first-person channel NolanPoker | Author's own About and `/poker/nolan-kido/` profile, plus the existing public YouTube channel link | First-person account of channel identity, not independent auditing of each video |
| Nolan has independently listed tournament results | Source links on `/poker/nolan-kido/` to WSOP and tournament result pages | Results and gross cashes do not verify every hand, net profit or creator accreditation |
| Nolan documented two Portland Meadows hand recollections | `/poker/episodes/portland-meadows-ep1/#hand-64o-record` and `#hand-77-record` | Archived narration, not a full checked transcript of the current video or solver finding |
| A poker/AI editorial case proposed three captions | `/technology/ai-poker-video-evidence/#poker-ai-draft`, public scene-claims JSON and offline `poker-vlog-fact-gate.py` | An editorial proposal and narrow rules test, not proof any AI caption appeared in the released video or human authorization |

The answer is a discovery and attribution improvement, **not** evidence of higher Google ranking, AI citation frequency, search referrals, product adoption, poker performance, or measured revenue.

## Local verification

- `python _scripts/build.py`: 253 files built, 8 generated outputs changed from baseline.
- `python _scripts/build.py --check`: 253 checked, 0 drift.
- `python _scripts/check_search.py`: 224 manifest pages, 225 sitemap URLs, 0 errors.
- `python _tests/check_html5.py`: 230 pages parsed, 0 failures (using local `html5lib==1.1`).
- `python _scripts/check_internal_links.py`: 232 HTML pages and 16,320 internal links, 0 issues.
- `test_turn23_nolanpoker_ai_identity_bridge.py`: 5 tests pass, including link/datetime/identity, visible native target and negative claim mutations.
- `test_turn20_identity_answer.py`: 4 tests pass, with legitimate latest About modification date.
- `test_turn35_ai_poker_case.py`: 12 tests pass, using the original archived commit for its source snapshots, plus a current-manifest-aware check for later editorial changes.
- `test_turn126_article_method_links.py`: 4 tests pass, allowing genuine later modifications but rejecting date backdating or sitemap divergence.
- `test_turn36_about_reader.py`: 8 tests pass with the expanded section navigation and stable Person ID.
- `test_turn135_about_hobby_navigation.py`: 5 tests pass with the new visible native anchor.
- `git diff --check`: no whitespace errors.

The broad default `_scripts/local_release_checks.py` was also attempted. It **did not pass** because older, separate regression fixtures still expect earlier dates, older homepage links and original UI structure elsewhere in the site. Examples include old assumptions in `test_turn48_visibility_demo.py`, `test_turn136_home_ai_arrivals.py`, and `test_turn158_keyboard_focus.py`. Those historical failures are not counted as passing tests or attributed to a demonstrated production defect from this change. The directly affected About navigation and AI/poker article tests were updated and rerun successfully. The full historical suite and browser suites are **not** claimed to pass.

A focused headless Chromium arrival check was attempted but could not launch because the execution environment rejected Chromium's local process socket with `Operation not permitted`. It is recorded as **unverified**, not a passing browser run. The new native anchor, visible target outline, viewport offset, HTML5 and local link destinations have static regression coverage.

## Release boundary and next action

No GitHub Actions, paid API, cron job, third-party login, private production record, new Person identity, `FAQPage` schema or current-video analysis was added. The affected public files must be byte-compared with the tested outputs after merging.

**Suggested Turn 24:** Strengthen source-to-topic pathways for nonbranded readers who arrive on poker or practical AI guides, while preserving one canonical author identity and measuring actual referral or citation outcomes only when observed data are available.
