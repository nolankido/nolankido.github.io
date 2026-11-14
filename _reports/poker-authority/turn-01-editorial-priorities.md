# Poker source coverage: November 2026 editorial review

Prepared November 14, 2026. Scope: original Poker articles, topic navigation,
curated external resources and the on-site Finder. This is a public-safe
editorial handoff, not a publication claim for any proposed article.

## Decision

**This is a source inventory and editorial gap review.** The immediate constraint is
not the absence of a beginner introduction or a lack of resource links. It is
uneven depth once readers move beyond introductory no-limit Hold'em, particularly
advanced preflop and postflop decisions, tournament formats, and individual
Omaha and mixed-game rules. Future work should add distinct, verifiable
answers and build the right paths between them. Do not pad the library with
near-identical summaries merely to increase its count.

The [generated coverage matrix](turn-01-coverage-matrix.md) is the reproducible
inventory. It maps **all 60 original guides** to exactly one primary hub,
records their secondary topic placements, counts **146 reviewed external-resource
records** across **10 hubs**, and verifies that the generated Poker Finder
includes all 60 library routes and all 146 resource records. The site also has
**13 curated resource collections**. These are catalogue facts, not independent
quality ratings.

## Evidence checked for this turn

1. Inspected the checked-out `_source/poker/library.json`, `topics.json`,
   `resources.json`, `collections.json` and generated `poker/find/index.html`.
   The source-based matrix checks uniqueness and primary-topic coverage, the
   topic membership of every external record, and representation of all library
   routes and external records in Finder.
2. Read selected existing guide prose and section headings, including
   `no-limit-holdem-guide`, `starting-hand-decisions`, `ranges-and-bets`,
   `short-stack-decisions`, `cash-game-study`, `cash-game-study-path`,
   `omaha-and-mixed-games` and `omaha-hi-lo-workshop`. This was a targeted
   overlap review, not a new fact-check of all 60 articles.
3. **Live GET spot check, November 14, 2026:** all 15 requested public routes
   returned HTTP 200: `/poker/`, `/poker/library/`, `/poker/resources/`,
   `/poker/find/`, `/poker/topics/` and the ten individual topic-hub routes.
   This confirms reachability at the moment checked, not indexing, ranking,
   exact deployed-byte equality, full-content correctness or visitor success.
4. Examined existing development records in
   `_reports/poker-information-architecture.md` and
   `_source/poker/RESOURCE_PROCESS.md` to avoid relaunching an already completed
   navigation or external-source inventory.

The stored `reviewed_on` dates in `resources.json` are preserved. The 146
external destinations were **not** freshly visited in this turn. Likewise,
no Search Console impressions, search rankings, AI citations, click-through
rates or traffic effects were measured here.

## Ten-hub editorial decision matrix

The counts and assignments below come from the generated matrix. A "missing"
item means **no dedicated guide with that precise scope appears among the 60
library entries**, not that the broader idea is never mentioned in an article.

| Hub | Existing foundation | Next distinct reader question | Recommended action |
| --- | --- | --- | --- |
| Learn poker | Sixteen primary guides, a broad hold'em overview, a sequenced beginner path and practice checks | How do I move from general starting-hand concepts to an actual, specified preflop action tree? | Link future scenario-specific guides to the existing lessons. Do not create another generic "poker for beginners" article. |
| Cash games | Six primary guides, first-session and cost references, multiway examples and a study route | What changes in a straddled, deep-stacked cash pot when position and SPR differ? | Develop a dedicated deep-stack example with a venue-dependent straddle convention and exact pots. |
| Tournaments | Nine primary guides, structure selection, short-stack models, ICM and live-play preparation | How do satellites, PKO bounties and distinct 3-to-5 BB versus 10-to-20 BB actions change the decision objective? | Separate future guides by structure, stack and payout objective. |
| Strategy and math | Nine primary guides, ranges, combinations, board-reading, pot odds and chart-reading | How do I reason through a three-bet, four-bet, continuation bet or river bluff-catching decision in a specified game tree? | Give each new article a different action point and worked decision. |
| Omaha and mixed games | Three primary guides, including Omaha hi-lo and stud/lowball workshops; 21 external sources matched by the hub | What are the exact legal holdings, hand rankings, street order and draw constraints in one specific variant? | Develop individual variant articles with independently checked hand constructions. |
| Study tools and training | Nine primary guides plus practice and advice-evaluation material | Which resource is suitable for this particular question, with which input and access assumptions? | Add a question-to-resource route, not a promotional software ranking. Pair sources with new guides and planned practice workbooks. |
| Places to play and home games | One primary venue guide, related planning and etiquette guides, plus 19 matched external sources | How do I find and verify original house rules, structures or home-game procedures without mistaking old schedules for live dates? | Link official destinations and provide a visible verification checklist. |
| News, results and creators | Three primary guides on results context, media study and vlog production, plus 24 matched outside sources | Where can a reader trace important people, game variants and tournament milestones to original sources? | Create a primary-source history index, not recycled unsourced trivia. |
| Research and development | One primary research guide, related evidence-evaluation and uncertainty work, and 16 matched research resources | How can a non-researcher distinguish a paper's proved scope, training setup and practical limitations? | Build an annotated original-source index with explicit paper-versus-documentation labels. |
| Safer play and rules | Three primary rules, protection and fairness guides; 18 matched outside resources | Which rules apply to a disputed live action, and what is the difference between a TDA recommendation and an operator rule? | Add versioned rule-specific explanations and a correction route. |

## Overlap review: expand or link?

The automatically computed hub intersections measure navigation sharing, **not
duplicate prose**. The principal editorial boundaries are:

| Existing material | Overlap finding | Editorial boundary for a new article |
| --- | --- | --- |
| [`no-limit-holdem-guide`](https://nolankido.com/poker/no-limit-holdem-guide/), [`getting-started`](https://nolankido.com/poker/getting-started/), [`holdem-basics`](https://nolankido.com/poker/holdem-basics/) | These all serve beginners with different depth and reading commitments. | Preserve the comprehensive reference and short entry points. Advanced preflop articles should address a decision in a defined game, not repeat rules and hand rankings. |
| [`first-decisions`](https://nolankido.com/poker/first-decisions/), [`starting-hand-decisions`](https://nolankido.com/poker/starting-hand-decisions/), [`reading-preflop-charts`](https://nolankido.com/poker/reading-preflop-charts/) | Beginner decision framing and chart assumptions are already taught. | New positional comparisons should address facing action and pot sizing with explicit assumptions. Cross-link to the earlier instruction rather than restating it. |
| [`short-stack-decisions`](https://nolankido.com/poker/short-stack-decisions/), [`tournament-equity`](https://nolankido.com/poker/tournament-equity/) | There are already worked 10-to-20 BB action comparisons and an ICM calculation, so "short stacks" and "ICM" are not blank topics. | Distinguish 3-to-5 BB inputs, 6-to-10 BB mixed actions, reshoves, bounties and satellites. No universal unexplained push/fold chart. |
| [`cash-game-study`](https://nolankido.com/poker/cash-game-study/), [`cash-game-study-path`](https://nolankido.com/poker/cash-game-study-path/), [`cash-game-costs`](https://nolankido.com/poker/cash-game-costs/) | One treats study assumptions, one sequences practice and one examines game costs. | A new deep-stack article should include a distinct straddled game state, not duplicate the study plan or rake primer. |
| [`omaha-and-mixed-games`](https://nolankido.com/poker/omaha-and-mixed-games/), [`omaha-hi-lo-workshop`](https://nolankido.com/poker/omaha-hi-lo-workshop/), [`stud-and-lowball-workshop`](https://nolankido.com/poker/stud-and-lowball-workshop/) | The existing guides teach rule differences and some detailed split-pot examples; there are already 19 variant-category external records. | Future variant work should offer game-specific, fully checked examples and rule indexes. Do not claim no variant coverage exists. |
| [`choosing-a-tournament`](https://nolankido.com/poker/choosing-a-tournament/), [`first-live-tournament`](https://nolankido.com/poker/first-live-tournament/) | Both intentionally appear under Tournaments and Places to play; shared hub placement aids discovery. | Add a fully specified historical structure-sheet example while leaving changing schedules at official source links. |

## Ranked unanswered-question backlog

The ranking is an editorial judgment based on distinct intent, existing coverage,
potential instructional value and evidence requirements. It is **not** search
volume or keyword-difficulty data. Each candidate must be compared against the
current library again immediately before writing.

| Priority | Distinct question that deserves a deep answer | Content form | Initial internal anchors | External source review needed |
| --- | --- | --- | --- | --- |
| P0 | When should an otherwise playable starting hand be folded, called, three-bet or four-bet against a particular opening range and stack? | Scenario guide series | `starting-hand-decisions`, `reading-preflop-charts`, `range-combinations` | Verify original range-methodology or solver documentation; never invent action frequencies. |
| P0 | What assumptions change postflop decisions in single-raised and three-bet pots, including river bluff catches? | Distinct action-point guides | `ranges-and-bets`, `reading-the-board`, `pot-odds-workshop` | Independently verify arithmetic, betting actions and any illustrative model. |
| P0 | How do 3 to 5, 6 to 10 and 10 to 20 big blinds create different legal and strategic options? | Stack-depth scenarios | `short-stack-decisions`, `reading-preflop-charts`, `side-pot-lab` | Check `hu-push-fold`, `icm-calculator` and original action-tree assumptions. |
| P0 | Why can a satellite seat bubble or knockout bounty change a chip-EV conclusion? | Format-specific guide series | `tournament-equity`, `tournament-formats` | Re-review `satellite-guide`, `bounty-models`, `mystery-bounty-guide`, `bubble-factor`; verify the modeled payout or bounty. |
| P0 | How do PLO wraps, redraws, exact two-hole-card construction and low split outcomes really work? | Variant-specific worked guides | `omaha-and-mixed-games`, `omaha-hi-lo-workshop` | Check official variant rules and independently enumerate any card outcomes; start with `omaha-rules`, `omaha-eight-rules`, `five-card-omaha-rules`. |
| P1 | How does exposed-card order alter decisions in Stud high, Stud eight, Razz, 2-7 and Badugi? | Variant rule and hand comparison series | `stud-and-lowball-workshop`, `omaha-and-mixed-games` | Recheck `stud-eight-rules`, `razz-rules`, `deuce-seven-rules`, `pagat-badugi`; distinguish venue exceptions. |
| P1 | What changes when a cash-game straddle or unusually deep effective stack reshapes the pot? | Deep-stack worked case | `first-live-cash-game`, `cash-game-study`, `cash-game-costs` | Cite an identifiable straddle convention; check arithmetic and house-dependent rules. |
| P1 | How should a player read blind pressure and re-entry rules from an actual tournament structure? | Structure-sheet explainer | `choosing-a-tournament`, `registration-and-reentry` | Use dated official organizer structure, not an inferred or current-looking schedule. |
| P1 | What exactly does the current TDA text say about common verbal, chip and showdown disputes? | Versioned rules question index | `poker-rules-and-fair-play`, `table-etiquette` | Recheck `tda-rules` edition/version and `stars-live-rules` or a specified operator's rulebook. |
| P1 | Where are the operator-controlled event, room and variant rule references, with clear verification steps? | Vetted official-source index | `poker-access-and-protection`, `choosing-a-tournament`, `omaha-and-mixed-games` | Recheck official organizer destinations, access conditions, version and region. |
| P2 | Which primary records substantiate a poker-history claim or explain what a research paper actually established? | Annotated original-source index | `poker-research-guide`, `poker-media-study` | Prefer original paper landing pages, historical archives and identified authors; flag disputes and incomplete access. |
| P2 | What is the shortest deliberate study route through advanced decisions and variant hand comparisons? | Scenario workbook and learning paths | `free-poker-learning-path`, `practice-room`, `reviewing-a-hand` | Use validated fictional examples and link directly to a verified explanation for each answer. |

## Priority internal-link audits

The manifest already gives each guide a primary topic and gives every resource
a topic. That is an important baseline, but **membership alone does not prove
that a reader sees a useful prerequisite or next step in article prose**.

1. Give each topic hub and library route a clear entry progression:
   Start, Deepen, Practice and Sources. Preserve all existing canonical URLs,
   the current Poker navigation, the complete no-JavaScript browse path and
   the Finder's private in-page query behavior. A short existing page should
   link to the relevant section of a longer one, not simply repeat its title.
2. Build a deterministic graph of actual generated anchor links
   and report guide pages unreachable from Poker entry points, contextual
   prerequisite gaps, bad destinations, weak related links and misleading
   broad-link loops. The existing `_scripts/check_internal_links.py` already
   validates route and fragment correctness, so extend its diagnostic utility
   rather than duplicating that validator. Do not auto-insert arbitrary links.
3. With every new article, add contextually justified links **into** the new
   guide from at least its parent hub and two older relevant guides, and links
   **out** to its prerequisites, next-depth answer and vetted original sources.
   This is an editorial target for future reviews, not a claim about the
   current site's measured link count.

## Publishing and quality considerations

- A proposed guide must have one distinct reader question, a defined audience,
  a truthful summary and a non-cannibalizing canonical scope. Reconcile it
  with existing guide content before creating its slug.
- Worked hands and numerical results must be independently checked. Declare
  game type, seats, stack convention, blinds, antes, action, pot, payout or
  variant rule where relevant. Hypothetical teaching cases are labelled.
- Use primary rules, official event details and original research where
  possible. Record access or date limitations. Never imply a directory-page
  review means a complete course, solver or event listing was audited.
- External resources stay in the single canonical `resources.json` catalogue.
  Follow `_source/poker/RESOURCE_PROCESS.md` to admit or retire sources;
  neither a search result nor a successful HTTP response is approval.
- Do not publish a user's private session notes, unreleased poker hands,
  opponent details, private solver outputs, earnings claims or sensitive data.
  Do not add scheduled GitHub workflows, cron, third-party tracking or paid APIs.
- Do not claim best-in-class status, rankings, AI citations or user learning
  gains without comparative evidence. Keep the monthly visibility scorecard
  separate from this editorial coverage record.

## Reproduce the coverage review

From the repository root, with the generated site current:

```sh
python _scripts/build.py --check
python _scripts/poker_coverage_matrix.py --check
python _scripts/check_internal_links.py
python _scripts/check_search.py
```

To update the numeric matrix after a **reviewed source change**, run the site
build, then `python _scripts/poker_coverage_matrix.py --write`, review the
diff, update this editorial document if appropriate and rerun checks. This
does not contact outside providers or publish a new guide.

**Next content-navigation opportunity:** improve the ten subject hubs and `/poker/library/` as
reader journeys using the current accurate topic memberships, with emphasis
on linking entry lessons to advanced preflop, tournament and variant learning.
Do not repeat the existing census as if it were new content. The detailed
private sprint schedule is maintained separately from this public report.
