# Poker guide library and topic journeys: November 2026 release record

Scope: `/poker/library/` and the ten existing `/poker/topics/{subject}/` pages.
Prepared November 14, 2026. This is a public navigation release note, not the
owner's private sprint schedule or a claim about search rankings.

## Reader problem and change

The topic hubs already had starter questions, guide disclosures and reviewed
source lists, but readers had to infer which item was an introduction, a deeper
explanation or an exercise. The library offered four broad entry paths and a
60-guide filter, but not a compact route across all ten subjects.

This release creates four visible choices for each subject:

1. **Start:** the existing editorial first step, from `topics.json`.
2. **Deepen:** a topic-specific guide selected for more demanding material.
3. **Practice:** an existing workshop, decision check or applied task, rather
   than a generic link labelled practice.
4. **Sources:** the complete topic-filtered external directory in Finder,
   retaining publisher, access and recorded review context.

The new `#subject-routes` section in the Poker Library displays ten subject
cards with these four choices. Each topic hub also shows the four routes
before its longer guide and source lists. Readers can use the links in any
order. All 60 guide destinations and 146 external resource records remain in
their existing catalogues, with unchanged URLs and editorial review dates.

## Editorial route selections

| Subject | Start | Deepen | Practice |
| --- | --- | --- | --- |
| Learn | `first-decisions` | `no-limit-holdem-guide` | `beginner-checkpoint` |
| Cash games | `cash-game-study-path` | `limped-multiway-pots` | `side-pot-lab` |
| Tournaments | `first-live-tournament` | `short-stack-decisions` | `tournament-equity` |
| Strategy and math | `poker-math-reference` | `range-combinations` | `decision-lab` |
| Omaha and mixed games | `omaha-and-mixed-games` | `stud-and-lowball-workshop` | `omaha-hi-lo-workshop` |
| Study tools and training | `poker-books-and-courses` | `choosing-study-tools` | `practice-room` |
| Places and home games | `choosing-a-tournament` | `poker-access-and-protection` | `tournament-trip-budget` |
| News, results and creators | `variance-and-results` | `poker-media-study` | `hand-to-vlog` |
| Research and development | `poker-research-guide` | `poker-under-uncertainty` | `evaluating-poker-advice` |
| Safer play and rules | `poker-rules-and-fair-play` | `poker-access-and-protection` | `table-etiquette` |

Every Start, Deepen and Practice destination must be a different guide and
must belong to the subject as a primary or related guide. The validator
rejects unknown or cross-subject routes. Source links are derived from the
existing topic membership, not hand-copied provider URLs. No new resource
has been added, re-reviewed or endorsed through this navigation work.

## Technical and access boundaries

- A new, small stylesheet, `assets/poker-journeys.css`, is linked only from
  the library and topic-detail pages. Existing sitewide menus, primary Poker
  navigation, unrelated guides and page canonicals remain unchanged.
- The route lists are server-generated HTML with ordinary anchors, visible
  without JavaScript. Each topic route is a labelled navigation region.
- Cards have visible keyboard-focus outlines, wrap long titles, and collapse
  from four columns to two and then one on narrow screens. The library map
  also reduces to one subject per row on smaller screens.
- The original topic guide disclosure, featured sources, complete topic
  sources, Finder filters, search privacy and gambling-support shortcut are
  still available.
- The local read-only target inventory includes the new stylesheet and the
  existing `poker-study-cycle.md` download referenced from two Poker pages.

## Reproduction and evidence

From the repository root:

```sh
python _scripts/build.py --check
python -m unittest discover -s _tests -p 'test_poker_topic_journeys.py' -v
python -m unittest discover -s _tests -p 'test_poker_topics.py' -q
python _scripts/poker_coverage_matrix.py --check
python _scripts/check_internal_links.py
python _scripts/check_search.py
python _tests/check_html5.py
```

The source-derived route checker verifies ten subjects, four unique routes
per subject and forty links on the library overview. It rejects a practice
route from the wrong subject. Existing topic-browser checks were extended
to inspect the library at 320, 390, 768 and 1280 pixel widths, keyboard
navigation, labelled stages and no-JavaScript access.

**Verification limitation:** local Playwright Chromium could not launch in
the available container because the browser process could not create its
singleton socket (`Operation not permitted`). Those browser assertions are
prepared but not counted as passing. CSS breakpoints and DOM structure were
reviewed statically; actual visual and keyboard behavior must still be
confirmed in a permitted browser environment. No user study or ranking gain
is claimed.

The next useful editorial audit is a deterministic graph of actual HTML
links, with attention to contextual prerequisites, weak transitions and
unreachable guides. The existing route/fragment validator should remain
the source of truth for broken-link detection.
