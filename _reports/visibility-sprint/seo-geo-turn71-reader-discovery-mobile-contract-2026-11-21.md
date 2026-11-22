# SEO/GEO Turn 71: connect first-time readers to real AI release proof and define a repeatable narrow-screen gate

**Date:** November 21, 2026 (Pacific/Honolulu)
**Starting main:** `22154df986bd19fd779074808e812d41fe62c382` (Turn 70, PR #444)
**Canonical entry:** https://nolankido.com/start-here/
**Scope:** One existing page's evidence route, one static regression module, and one offline browser acceptance script. No new canonical page, search claim, subscription, tracker, or workflow.

## Why this turn

The completed 37-61 roadmap and the November 21 Turn 70 report distinguish site publication from externally observed discovery. The full 320 px reader-path and release checks still lack a current executable receipt. A read-only public default-desktop audit of Home, Start Here, Technology, Books and the 10 BB Playbook confirmed legible navigation and descriptive AI/evidence resource links in the sampled viewport. The browser tool could not set 320 px, so that is **not** a mobile pass.

The existing Start Here projects list led first to three projects or demonstrations. Home already linked to the independently sourced website HTML repair, but Start Here did not provide an equally direct project-area route to that stronger release evidence. Fixing this navigation gap is more relevant to practical-AI credibility than publishing another broad landing page.

## Implementation

1. In `_source/start-here.html` and the paired `start-here/index.html`, place one clearly labeled source-checked release link immediately below the existing `#start-projects-title` heading. It routes to `/technology/checking-ai-website-changes/`, where original before-and-after source, a parser explanation, and the free `/downloads/website-check-offline-runbook.md` live. The link explicitly says one repaired defect does not prove AI time savings or increased search rankings.
2. Add `_tests/test_turn71_start_here_release_navigation.py` with source/published text parity, existing sections and canonical preservation, real case/download existence, 2026-11-21 revision continuity, browser-script scope, and deliberately malformed negative controls.
3. Add `_tests/visibility_core_journeys_browser.py` to run an offline Chromium check at 320, 390, 768 and 1440 CSS pixels across five priority routes. The 320 and 390 cases also repeat with 200% text enlargement, giving 30 intended viewport assessments. It loads the true checked-in `/styles.css` and `/assets/` CSS in the original cascade positions, forbids network and scripts, and checks root overflow, missing/overlapping/clipped primary navigation and skip/main presence.
4. Register the static module in the existing manual `_scripts/local_release_checks.py`. The browser script is automatically discovered by the runner's existing `*_browser.py` opt-in when `--browser` is requested. Add source ownership and verification constraints to `AGENTS.md`.

## Evidence and limitations

| Check | Result | Qualification |
| --- | --- | --- |
| Current latest main at start | `22154df986bd19fd779074808e812d41fe62c382` | Read from authenticated GitHub connector; not a fresh executable checkout |
| Source and published Start Here paragraph | Same new literal paragraph added to both | Repository write; deterministic generator has not been executed in this tool environment |
| Target case and release worksheet | Both paths found in committed source and public GitHub HTML | Does not prove new Start Here link already deployed |
| Browser default-desktop five-page exploration | Clear navigation and no observed page-wide overflow | A bounded read-only public-site audit, not a mobile or accessibility certification |
| 320/390 px and 200% zoom coverage | Scripted for five priority routes | Browser not executed against a full checkout; status **not run** |
| Python unit tests, build, HTML5, sitewide internal links | New module and script authored; current full suite **not run** | Local container cannot resolve GitHub to obtain complete checkout |
| Exact status-and-byte HTTP production verification | **Not run** | Public text extraction alone is not sufficient |
| Google Search Console, Bing Webmaster numeric SEO data | **Unavailable** | Connected GSC Wizard returned `payment_required` for both services; no paid plan authorized |
| Google AI appearances, Bing AI citations, Umami assistant referrals | **Unavailable** | Missing inputs must not be replaced by zeroes or inferred from sitemap counts |

## Sprint gate reconciliation after this change

| Original gate | Current status |
| --- | --- |
| Trustworthy release | **Partial**: current repo inventory, bounded live content, tests authored; complete build and exact live bytes still need an executable receipt |
| Baseline and assistant observations | **Open**: owner-authenticated data and eligible frozen-panel results missing |
| Practical AI authority | **Substantially strengthened editorially**: original repair, human approval/stop rules and source-backed cases are discoverable; search impact unmeasured |
| Books and poker integration | **Published source paths**: two author book work pages/catalog and 10 BB free guide; retail editions and current media-cut verification remain separate |
| Navigation/usability | **Progress**: stronger first-visit evidence route and repeatable five-route narrow-screen check; the new mobile check still must be run |
| Performance and search-relevance experiments | **Open**: no comparable Lighthouse observations or actual query/page based experiment yet |
| Final impact scorecard | **Qualified, not certified**: inventory and source provenance recorded; rankings, clicks, citations and referrals require owner data |

## Next execution and acceptance

From a complete current checkout with Python 3.10+, playwright and installed Chromium, run:

```powershell
py -3 -m unittest discover -s _tests -p test_turn71_start_here_release_navigation.py -v
py -3 _tests/visibility_core_journeys_browser.py
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _scripts/check_live.py --only /start-here/ --only /technology/checking-ai-website-changes/ --attempts 3 --interval 5
```

Any actual mobile or full-release failure needs repair, not a lower assertion. Do not mark the browser script passed until it has run; separately test keyboard and touch behavior. Once this turn merges and deploys, verify the new Start Here paragraph from the actual public route before claiming live publication.

**Highest next priorities:** full executable release and live-byte receipts; free owner-private Search Console/Bing/Umami exports; actual 320 px keyboard completion on all three reader journeys; measured performance lab; and truthful book retailer facts. December 2026 is still the first complete potential postsprint month and has not yet happened on this date.

**No owner-authored GitHub Actions, cron, new CI, paid API, private source exports, synthetic outcome claims, new canonical pages or AI-only metadata were added.**
