# SEO/GEO/AEO Sprint Turn 22: When a 10 BB poker solver chart fits

- **Date:** November 18, 2026 (Hawaii)
- **Property:** https://nolankido.com/
- **Sprint:** Turn 22 of 25
- **Base:** merged Turn 21 commit `b5fc143bde5aa0b092355d6291c25141c578b0de`, PR #393
- **Canonical retained:** https://nolankido.com/poker/evaluating-poker-advice/
- **New answer fragment:** https://nolankido.com/poker/evaluating-poker-advice/#solver-fit-test
- **Nonbranded search intent:** Can you trust a 10 BB poker solver chart on the tournament bubble? Why do chip pot odds and ICM sometimes imply different calling thresholds?

## Gap and change

The site already had a detailed short-stack education series, including a verified 10 BB money-bubble calculation, a standard-library exact-fraction ICM checker, an independently enumerated test, a chart-reading guide and a recorded NolanPoker hand with explicit unknowns. The broader `/poker/evaluating-poker-advice/` guide addressed confidence, spot matching and source quality, but did not directly answer the specific 10 BB solver-fit question in one compact place. A new near-duplicate article or chart would fragment the existing reference library.

Turn 22 adds a visible answer at `#solver-fit-test` on the existing October 8 article. It links to the exact fully worked four-player example and code rather than copying an unsupported chart or manufacturing a solve. The explanation distinguishes a caller's decision from a first-in shover's decision, chip price from payout equity, and known numbers from an invented 50% chance of winning. The title and description now state the direct educational question and evidence available to a reader.

The Poker hub, external-resource guide and preflop-chart interpretation guide link natively to the same canonical fragment. Their content dates reflect substantive November 18 links where needed; the established source article's publication date remains October 8. No new canonical URL, podcast/video claim, paid solver dependency or standalone runtime was introduced.

## Source-to-claim chain

| Claim in the visible answer | Source or independent check | Boundary |
| --- | --- | --- |
| Four remain, three paid; stacks 40/30/20/10 BB, prizes $50/$30/$20/$0, no ante; BB faces a covering SB shove | [Original source-bounded fictional fixture](https://nolankido.com/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble) | Teaching hand only, not a current WSOP structure or Nolan's actual tournament |
| Hero BB has already posted 1 BB and must add 9 BB; final matched pot is 20 BB | [Exact-fraction code](https://nolankido.com/downloads/ten-bb-bubble-icm.py) and local Turn 12 test of the pot and uncalled 30 BB refund | Closed action, no tie, fees or bounty; direct chip price 9/20 = 45% |
| Classic four-player ICM gives fold prize equity $12.286143 and call-win equity $21.785714, requiring about 56.40% showdown win probability to match folding | Same code, plus `_tests/test_turn12_ten_bb_bubble.py`, which independently enumerates all finishing-order permutations | This is a conditional prize-equity calculation, not an empirically measured hand equity or a universal strategy |
| A made-up 50% chance clears 45% chip price but not 56.40% ICM threshold | Exact inequality 9/20 < 1/2 < 76518591/135682300 | The 50% is hypothetical, not a solved opponent range, observed frequency or real-hand estimate |
| Solver results depend on ranges, players, stacks, pot, legal actions, ante and payout model | [GTO Wizard's current custom-solution documentation](https://help.gtowizard.com/how-to-build-custom-solutions/) | Official vendor documentation about inputs, not an independent accuracy audit or a purchased solution |
| A real NolanPoker 6-4 hand cannot be assigned this fictional ICM verdict | [Source-limited Portland Meadows hand account](https://nolankido.com/poker/episodes/portland-meadows-ep1/#hand-64o-record) | Actual hand has different blinds and antes, and a missing complete opponent-range/field-stack/payout record |

The answer recommends recording a chart mismatch as **unresolved** rather than translating a model output into a verdict. A matched model still does not completely reproduce future blinds, opponent adaptation, player skill or the room's exact event rules. It is for after-play study, not real-time assistance or a claim of positive gambling returns.

## Local verification

| Check | Observed result |
| --- | --- |
| `python _scripts/build.py` | 253 generated files, 19 generated outputs refreshed |
| `python _scripts/build.py --check` | 253 checked, zero drift |
| `python _scripts/check_search.py` | 225 sitemap URLs, 224 pages, no metadata errors |
| `python _tests/check_html5.py` | 230 HTML pages, no failures |
| `python _scripts/check_internal_links.py` | 232 HTML pages, 16,311 links, no issues |
| `_tests/test_turn22_poker_solver_fit_answer.py` | 4/4 pass including exact arithmetic, original heading IDs, metadata, navigation and negative claim mutations |
| `_tests/test_turn12_ten_bb_bubble.py` | 5/5 pass with independent finishing-order enumeration |
| `_tests/test_poker_six_to_ten_bb.py` | 11/11 pass |
| `_tests/test_poker_field_guide.py` | 8/8 pass |
| `_tests/test_turn21_ai_search_source_check.py` | 4/4 pass |
| `git diff --check` | No whitespace errors |

The full historical suite and browser layout tests were not run. The static tests verify generator consistency, markup parseability, input arithmetic and internal links; they cannot measure comprehension, live gameplay outcomes, Google ranking changes or AI-answer citations. After a merge, direct public-byte comparisons should separately establish actual publication. The offline checker, video records, frozen Turn 19 citation panel and all private search analytics were left unchanged.

## Outcome and next opportunity

This turn strengthens a nonbranded educational answer, connects it to a transparent computation and improves its native discovery through related Poker pages. It does not establish a search or AI-answer citation gain. No paid GSC connector was activated, and no private hands, account data or credentials were published.

**Suggested Turn 23:** Improve the public author-to-expertise bridge for poker searches by connecting source-bounded NolanPoker decisions to the relevant study explanations, without claiming solver verdicts or net tournament profit.
