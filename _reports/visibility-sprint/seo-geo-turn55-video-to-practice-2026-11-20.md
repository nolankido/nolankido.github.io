# SEO/GEO Turn 55: Video to hand evidence to independent after-play practice

**Review date:** November 20, 2026 (Pacific/Honolulu)
**Starting main:** `bdc9607f8181c4cc681d52ba5a720e82d3ff01b3`
**Scope:** The three source-documented NolanPoker videos, companion question links and free after-play exercises, not six new articles.

## Actual user journey and gap

The existing [Poker gallery](https://nolankido.com/poker/#watch) has six verified public YouTube video IDs and titles, and three separately published companion articles for Deepstack, Stand Off and Reserve Day 1. It also has an established four-case `#nolanpoker-hand-study` bridge. An audit found the new-viewer cards still did not consistently point to their own existing question exercises. The Deepstack card offered the two written hand records, not the independent practice worksheet; Stand Off offered a whole companion and a longer in-page note but no direct action to the specific second-decision question; Reserve offered the pot explanation but not the three after-play quiz questions. Companion articles linked general guides but, in places, did not directly identify a distinct free question or make the separation from the recorded real hand clear.

The existing public-source and generated files were inspected to establish exact anchors before editing. A read-only public fetch also confirmed these targets exist as unique IDs: `#bridge-practice`, `#study-loop`, `#icm-call`, `#all-in-action`, `#hand-64o-record`, `#standoff-second-decision` and `#reserve-questions`. Avoid creating an additional Poker resource index when an owned one is already present.

## The bounded change

| Public video route | Original real-hand evidence | Practice path after watching | Evidence boundary |
| --- | --- | --- | --- |
| Deepstack `qABaiIcvvpU` | [6-4 and 7-7 source-bounded accounts](https://nolankido.com/poker/episodes/portland-meadows-ep1/) including existing reader questions | [Nine separate fictional 6–10 BB questions](https://nolankido.com/poker/six-to-ten-bb-tournament-decisions/#bridge-practice); [personal after-play comparison record](https://nolankido.com/poker/short-stack-decisions/#study-loop) from the 7-7 reading | The six-four shove and pocket sevens win are first-person accounts, not solved examples. |
| Stand Off `I75GOBVXij4` | [A-K second-decision reader question](https://nolankido.com/poker/episodes/portland-meadows-standoff/#standoff-second-decision) reached directly from its video card | [Separate fictional chip-versus-ICM call](https://nolankido.com/poker/short-stack-decisions/#icm-call) from the companion question | The archived v9 record lacks validated opponent ranges and current-cut audiovisual verification. |
| Reserve Day 1 `edNSD5BjIV8` | [Three after-play questions](https://nolankido.com/poker/episodes/reserve-day-1/#reserve-questions) reached directly from its video card; existing `#reserve-pots` retained | [Fictional main/side pot and unmatched-refund lab](https://nolankido.com/poker/side-pot-lab/#all-in-action) from the actual article questions | The fictional side-pot stacks/cards do not represent the separately narrated three-way A-K hand. |

The existing other three videos, full six-video gallery order, thumbnail snapshots, article identities, Poker sitemap dates, and other book and AI content were left unchanged. The change adds one destination-oriented practice link within each of three existing card paragraphs and refines only their corresponding in-companion follow-up prose, reusing existing HTML links and responsive styling, no scripts or duplicate blocks. No new canonical page or redirect.

## Source and regression changes

- `_source/poker/home.html` and `poker/index.html`: exact same action edits for the three relevant source-documented cards, preserving all six public video links and the original four-case `#nolanpoker-hand-study` bridge.
- `_source/poker/portland-meadows-ep1.html` and `poker/episodes/portland-meadows-ep1/index.html`: after-play practice next to both genuine 6-4 and sevens reader questions. The nine short-stack questions use invented states; the sevens link is an after-play checklist, not a solved range.
- `_source/poker/portland-meadows-standoff.html` and `poker/episodes/portland-meadows-standoff/index.html`: existing fictional ICM follow-up is now described as practice separate from the reported A-K hand.
- `_source/poker/reserve-day-1.html` and `poker/episodes/reserve-day-1/index.html`: three genuine written questions now directly link to the public fictional side-pot eligibility/refund lab, with the invented-state limitation.
- Added `_tests/test_turn55_video_to_practice.py` for video-to-evidence-to-fictional-exercise paths, existing six videos and source qualifiers, unique actual guide anchors, source/public inserted passage parity, date preservation and negative broken-link/source-limits controls. Registered in `_scripts/local_release_checks.py`, README and AGENTS.

## Evidence boundaries and tests

These are publicly linked educational pages, not a real-time solver or at-table assistance. The observed public site section and source files establish route existence, not that a visitor clicked, completed or learned from the exercise. An outcome is not an optimal decision, an archived v8/v9 script is not the current published video, and the Deepstack viewer transcript cannot validate its on-screen graphics or producer signoff.

Connected GitHub source and output checks were performed to ensure each exact edit occurs in only one intended place and that new practice target IDs are unique. Full local Python unit tests, generator parity, HTML5, browser keyboard/mobile and site-wide internal link suite were **not run** in the current model workspace unless separately confirmed. The changed HTML pages are not automatically proven live by GitHub merge. No actual search, AI citations, impressions, viewing or conversion metrics were measured.

### Full local verification

```powershell
py -3 _scripts/build.py --check
py -3 _scripts/build_poker_episode.py --check
py -3 _scripts/build_standoff_episode.py --check
py -3 _scripts/build_reserve_day1_episode.py --check
py -3 -m unittest discover -s _tests -p test_turn55_video_to_practice.py -v
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /poker/ --only /poker/episodes/portland-meadows-ep1/ --only /poker/episodes/portland-meadows-standoff/ --only /poker/episodes/reserve-day-1/ --attempts 3 --interval 5
```

## Next improvement

**Turn 56:** Audit the authority and limits of citation-linked poker instruction pages by asking whether a given reader answer is supported by an actual published source, not just its presence in the link graph. Resolve one high-impact citation or factual caveat before expanding more landing pages.
