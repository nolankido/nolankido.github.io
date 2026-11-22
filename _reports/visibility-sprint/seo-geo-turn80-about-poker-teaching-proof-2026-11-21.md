# SEO/GEO Turn 80: connect the author identity to original poker teaching, with evidence boundaries

**Date:** November 21, 2026 (Pacific/Honolulu)
**Starting main:** `23a6492ef7521ef50d0570b10ffeb3c0b9870888` (Turn 79, PR #453).
**Canonical page:** https://nolankido.com/about/
**Scope:** Existing identity/evidence section and two already published educational routes. No new canonical page, source credential, ranking claim, analytics service or GitHub Actions.

## Concrete reader gap

The public About identity section documents NolanPoker first-person videos and tournament result sources while correctly distinguishing gross cashes from net profit. However, authenticated inspection found **zero direct links** from the About source to either `/poker/free-poker-learning-path/` or `/poker/10bb/`. Those pages are original authored instructional material, relevant to a reader assessing the breadth and substance of the site's poker work. Without a direct evidence route, a visitor evaluating poker teaching must search elsewhere in the site. This is an internal navigation gap, not evidence of lost traffic or rankings.

## Change

1. Add one `small-copy about-poker-study-proof` paragraph immediately after the About identity evidence cards and before the explanation about differing evidence types. It links the published free six-lesson Poker Foundations course and the standalone written 10 BB guide's `#six-checks` section.
2. Explicitly distinguish original teaching resources and a reproducible **fictional** ICM example from independent tournament result records, claimed live-hand solver accuracy, net profit or official professional credentials. No results, credentials or measured outcome are inferred from instructional content.
3. Place **exactly identical** paragraph text in `_source/about.html` and paired public `about/index.html`. Preserve original research DOI, YouTube channel, tournament record links, source-backed identity answer, canonical, H1 and original November 20 metadata.
4. Add `_tests/test_turn80_about_poker_teaching.py` with seven tests for source/output equality, real canonical destinations and the playbook anchor/downloads, preserved independent-result sources, original metadata, builder-output parity and deliberately false/missing-URL negative controls.
5. Register the test in the existing manual `_scripts/local_release_checks.py` and document ownership and limits in `AGENTS.md`.

## Verification evidence

| Gate | Observation | Qualification |
| --- | --- | --- |
| Original About routes to these two teaching pages | 0 | Authenticated GitHub source before change |
| Updated About source and public paragraph | Exact match | Read back through authenticated GitHub branch source |
| Existing public teaching destinations | Both present | Course canonical and six lessons; 10 BB written guide and `id="six-checks"` source checked |
| Original biography evidence | Preserved | Research DOI, NolanPoker channel, tournament records and gross-cash disclaimer retained |
| New paragraph negative-control behavior | Four out of four isolated checks passed | Local HTMLParser of the exact new paragraph and three deliberately altered copies; not the full site |
| Seven focused unittest methods | Authored, registered | Full module/build not executed due lack of complete checkout |
| Sitemap unique URLs | 230 | Committed sitemap inventory unchanged, not indexing |
| Live public HTML byte equality | Not run | GitHub merge/source parity is not a status-bearing production GET |
| True 320px mobile and keyboard acceptance | Not run | Existing browser workflow cannot resize the public viewport; complete checkout/installed browser test needed |
| GSC, Bing, AI assistant citations and user conversions | Unavailable | No observed search or business gain is inferred |

## Acceptance from a full matching checkout

```powershell
py -3 -m unittest discover -s _tests -p test_turn80_about_poker_teaching.py -v
py -3 -m unittest discover -s _tests -p test_turn50_first_screen_identity.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope priority --only /about/ --only /poker/10bb/ --attempts 2 --interval 2
```

The last command is only an explicitly selected priority subset. Run all priority routes and the complete release inventory separately. Real acceptance requires the new About link to work with keyboard and at narrow widths, correct target fragments, deterministic public output, and actual status-bearing, exact source-to-live bytes. Do not infer a passing result from a successful GitHub merge or a content extractor.

## Position relative to the sprint

**Advanced:** a visitor evaluating the site's author's poker experience can now inspect both original teaching material and separately sourced tournament results without conflating their evidence. No duplicate content page or speculative authority signal was added.

**Still open:** complete executable release and mobile checks, live byte parity, owner-private Google/Bing search measurements, eligible frozen assistant citation observations, performance baseline, verified KDP retailer editions. December 2026 is the first possible complete post-sprint month and has not elapsed.

**Next priority:** run the real release suite in a network-capable checkout, resolve observed defects and prioritize subsequent on-page work from settled query/page performance, not assumptions about ranking lift.
