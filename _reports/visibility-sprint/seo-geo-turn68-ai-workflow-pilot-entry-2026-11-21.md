# SEO/GEO Turn 68: direct practical-AI readers to the original workflow pilot

**Date:** November 21, 2026 (Pacific/Honolulu)  
**Starting `main`:** `e4a90aa94a1dc26f3a6f93094fc37445246109ea` (merged Turn 67, PR #441)  
**Existing task destination:** https://nolankido.com/technology/ai-workflow-pilot/#pilot-protocol  
**Scope:** Real user navigation, reader intent and on-site subject coherence. No extra canonical page, AI-optimized schema, paid API, analytics tracking or automated workflow.

## Recent publication verified

A read-only fresh public retrieval found the Turn 67 written version of `/poker/10bb/` on the live custom domain with its corrected title and "Choose a written lesson" section. The site Find page also retained its published Playbook result. A content extractor is not an exact-byte GET verifier or evidence that Google has reindexed the page, but it resolves the previously open **content-level deployment uncertainty**.

## Confirmed practical-AI discovery gap

The indexable guide `/technology/ai-workflow-pilot/` is already published. It explains a practical method for testing whether AI saves real whole-task effort without failing quality checks. It includes a free six-case example, a blank CSV log and an offline audit script, and plainly discloses that the demonstration data are **fictional**, not observed client results or a productivity study.

A direct source inspection of both `_source/home.html` and `_source/start-here.html` found **zero links** to this guide. The Technology hub linked the method, but a newcomer using either principal site entry did not have an immediate task-matched route. Home already had a direct link to the time calculator; it offered no adjacent process for *whether AI should be adopted* in the first place. This is a concrete navigation/discovery gap, not proof of low rankings.

## Actual improvement

1. Add one contextually relevant paragraph immediately after Home's **three original practical-choice cards** and before its existing optional resources disclosure. Its concrete question is "Will AI save your business time?" and its single native link goes to `/technology/ai-workflow-pilot/#pilot-protocol`. Copy tells readers to check preparation, review, corrections and quality and explicitly states the examples are not measured savings.
2. Add one business-reader paragraph immediately after Start Here's **four unchanged task list entries**. It links to the exact same pilot protocol, describes the six-case log and quality check, and discloses the fictional example. The four primary task destinations, their order and mobile/keyboard layout are untouched. There is no extra menu item, no form and no new JavaScript.
3. Update source owners `_source/home.html` and `_source/start-here.html` **together with** their corresponding committed public HTML. Preserve the Home hero's three native actions, original choice cards, optional disclosure with six links, existing canonicals, metadata titles and site structure.
4. Record the actual November 21 change to Home and Start Here via `_source/pages.json`, the two WebPage `dateModified` fields and exactly two corresponding `sitemap.xml` `lastmod` entries. The existing AI workflow guide is unchanged, including its November 20 last modification. The sitemap still lists **230 canonical URLs**, not two new URLs.
5. Add `_tests/test_turn68_workflow_pilot_discovery.py` with seven local contracts: unique task links and exact source/published paragraph parity, original target/protocol and fictional limits, existing Home/Start Here action counts, accurate modification dates and canonical/sitemap invariants, generator-output parity, intentional broken-link and false-proof negative controls, and no authored GitHub Actions. Update the existing Turn 50 Home date expectation to November 21 while preserving About's unchanged November 20 date. Register the new test with the normal **manual** release runner.
6. Update `AGENTS.md` to protect those bounded task routes and their accurate evidence labels in future releases.

## Static source observations

| Signal | Starting main | Turn 68 reviewed change |
| --- | --- | --- |
| Direct AI workflow pilot link from Home | 0 | Exactly 1, next to practical choices |
| Direct AI workflow pilot link from Start Here | 0 | Exactly 1, after existing task list |
| Home primary practical choices | 3 | 3, unchanged |
| Home optional details links | 6 | 6, unchanged |
| Start Here task list items | 4 | 4, unchanged |
| Verified target heading `#pilot-protocol` | 1 | 1, unchanged |
| Home and Start Here source/output pilot paragraphs | Absent | Exact identical markup in each pair |
| Updated date for Home and Start Here | Nov 20 and Nov 4 | Nov 21, respectively |
| AI workflow guide updated date | Nov 20 | Nov 20, unchanged |
| Sitemap URLs | 230 | 230, same canonical URL set |
| Measured clicks, AI citations or business conversions | Unavailable | Still unavailable, **not zero** |

The two live canonical pages and the target pilot page were retrievable before editing, with the pilot's original title and free worksheet link. Source review confirms the new links do not point to nonexistent subjects, invent performance data or promote a proposed pilot as an actual client result. No script, tracking query, new data collection or hosted backend is needed for either link.

## Release gates and limits

**Static checks completed:** GitHub source/public paragraph comparison; original three-card/six-details/four-task counts; one target link in each updated public page; one original `#pilot-protocol` ID; public title and canonical consistency; current-manifest dates; WebPage structured date parity; 230 sitemap entries and the two revised `lastmod` records; source-level presence of explicit fictional and no-measured-savings disclosures.

**Not run:** A complete local Python build or unit suite, full HTML5 parser, browser/mobile/keyboard task completion, comprehensive link checker or exact-byte production comparison. In this session the container cannot resolve `github.com` and no complete checkout is available; the connected GitHub source reads and public content extraction are distinct. No one should call the full release gate passed or a reader-conversion gain measured based only on this PR.

### Commands for a full local checkout

```powershell
py -3 -m unittest discover -s _tests -p test_turn68_workflow_pilot_discovery.py -v
py -3 -m unittest discover -s _tests -p test_turn50_first_screen_identity.py -v
py -3 -m unittest discover -s _tests -p test_turn99_home_useful_first.py -v
py -3 -m unittest discover -s _tests -p test_turn11_task_navigation.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _scripts/check_live.py --only / --only /start-here/ --only /sitemap.xml --attempts 3 --interval 5
```

Verify content-level deployment separately via the two public entry pages and follow each new link to the pilot. Do not treat an unresolved network request as an observed 404. Prioritize actual GSC/Bing/Umami measurements and a 320px/desktop real reader-task audit next; do not infer rankings, AI-answer citations or client adoption merely from new internal links.

## Source ledger

- [Turn 61 evidence scorecard](seo-geo-turn61-release-and-evidence-scorecard-2026-11-20.md)
- [Turn 67 standalone Playbook correction](seo-geo-turn67-playbook-standalone-2026-11-21.md)
- [Existing free AI workflow pilot](../../technology/ai-workflow-pilot/index.html) and [offline CSV worksheet](../../downloads/ai-workflow-pilot-blank.csv)
- [Home source](../../_source/home.html), [Start Here source](../../_source/start-here.html), and [site manifest](../../_source/pages.json)

**Bottom line:** an existing source-backed, free practical-AI method is now one useful click from both main visitor entry points. Whether any visitor takes that route, finds the guide useful or later discovers it through Google or an assistant remains unmeasured.
