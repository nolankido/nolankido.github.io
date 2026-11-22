# SEO/GEO Turn 81: make the 10 BB ICM companion a reproducible independent study worksheet

**Date:** November 21, 2026 (Pacific/Honolulu)
**Starting main:** `5d163677d691725f3e4b39b60d67a61653774de9` (Turn 80, merged PR #454).
**Scope:** The already published Markdown worksheet at `/downloads/ten-bb-tournament-checklist.md`, one local test module, manual release registration and authoring guidance. No new canonical site page.

## Why this is a substantive learning improvement

The 10 BB Playbook's original free worksheet already had six decision prompts, a summary of the three relevant equations, and a single line giving the fictional three-player ICM break-even probability of **63/107 (58.88%)**. But the sheet did not itself show how the finishing-order probabilities and prize payouts produce that fraction, or let a reader practice the important difference between positive chip EV and negative prize-value EV. The full article and executable Python checker provided the detail, but the downloaded worksheet was not self-sufficient for this calculation.

## Change made

1. Retain the original six-check decision table, all three calculation descriptions, the practice review instructions, original example and source route. Leave the November 19 original companion label in place and date the expanded worked calculations November 21.
2. Add a complete state table for the fictional no-ante three-handed, three-paid model: payouts **$100/$60/$40**, total **35 BB**, three outcome states, hero first/second/third probabilities, and exact modeled prize values.
3. Derive the fold prize value **$64** and call-win value **$1696/21 (about $80.76)** directly from the probability terms. Preserve the **$40 third-place loss payout**. Show explicitly how the **9/20 (45%)** chip price and **63/107 (about 58.88%)** ICM break-even probability answer different questions.
4. Add an after-play practice exercise comparing hypothetical **55%** and **60%** call-win rates with a four-row 45/50/55/60 sensitivity answer key. At 55% the model shows **+2 BB chip EV but −$1.58 modeled prize value** relative to folding. At 60%, **+3 BB** and **+$0.46**. The supplied rates are assumptions, not measured opponent ranges or a solver verdict.
5. Link the existing fixed-input standard-library Python checker from the worksheet. Do not edit the calculator, the published Playbook HTML, betting recommendations, author metadata or site sitemap.
6. Add `_tests/test_turn81_10bb_worksheet_math.py` with eight source/negative-control and independent rational-arithmetic regression methods; register in the existing manual `_scripts/local_release_checks.py` and document mathematical source ownership and scope in AGENTS.md.

## Verification: executed versus not executed

| Gate | Observation | Evidence boundary |
| --- | --- | --- |
| Arithmetic independently recalculated with Python `Fraction` and all three-player finishing orders | **Pass: 10 exact-rational assertions** | Executed in local container, not a copy of the published verifier's calculation routine |
| Fold first/second/third probabilities | **9/35, 3/7, 11/35** | Independent enumeration, sums to one |
| Call-win first/second/third probabilities | **4/7, 34/105, 11/105** | Independent enumeration, sums to one |
| Prize values and break-even threshold | **$64; $1696/21; $40; 63/107** | Independently reproduced |
| 45/50/55/60 sensitivity prize differences | **−$5.66; −$3.62; −$1.58; +$0.46** | Independent exact fractions, currency rounded to cents |
| Existing worksheet checks and original text | **Preserved** | Authenticated GitHub main/branch text comparison, six original numbered rows unchanged |
| Published Python script | **Unchanged** | Existing GitHub blob SHA `1b781df7e38567aac1a0c43b4649d5c248a36bcd` |
| New source-aligned unittest methods | **8 authored, not executed from a complete checkout** | Requires repository files and generator assets |
| Deterministic build, HTML5, internal links, Playwright and local full release | **Not run** | A complete checkout is unavailable because the isolated container cannot resolve GitHub |
| Direct production status and exact worksheet bytes | **Not checked** | GitHub source update is not a live GET or deployment receipt |
| Google/Bing query clicks and AI citations | **Unavailable** | Connected GSC Wizard account reported an expired trial/subscription requirement; missing data is not zero |

## Local acceptance from a matching complete checkout

```powershell
py -3 -m unittest discover -s _tests -p test_turn81_10bb_worksheet_math.py -v
py -3 -m unittest discover -s _tests -p test_turn72_reader_release_coverage.py -v
py -3 -m unittest discover -s _tests -p test_turn52_10bb_playbook.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope priority --only /poker/10bb/ --only /downloads/ten-bb-tournament-checklist.md --only /downloads/ten-bb-playbook-icm-verify.py --attempts 2 --interval 2
```

Only a successful direct status-and-exact-byte `verified_routes` receipt for the changed worksheet establishes production parity. A public extractor's text or a GitHub commit does not. Report transport failures as inconclusive, not an observed 404. Keep any site changes independent of a paid connector or GitHub Actions.

## Position relative to SEO/GEO sprint

**Advanced:** the site's already discoverable 10 BB resource offers a more rigorous, genuinely usable worked calculation and practice activity that readers can inspect away from the table, without adding thin canonical content or inventing a tournament result. This is a substantive content-quality improvement, not a demonstrated ranking change.

**Open:** full current-source release/browser/mobile execution, exact production bytes, owner-authenticated Search Console/Bing/assistant observations, performance measurements, and verified book editions. The sitemap remains 230 canonical source URLs; that does not establish indexing.

**Next highest-value turn:** run the complete manual release suite and exact byte comparison from a network-capable checkout, then prioritize measured content improvements once settled owner data are available.
