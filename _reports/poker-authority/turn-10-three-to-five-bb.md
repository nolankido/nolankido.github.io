# Poker authority sprint: Turn 10, three to five big blinds

Date: November 15, 2026

## Editorial result

Prepared an original, substantially worked tournament study guide for
[`/poker/three-to-five-bb-tournament-decisions/`](https://nolankido.com/poker/three-to-five-bb-tournament-decisions/).
This is a locally generated release candidate. Public availability needs
confirmation after merging and deployment.

Turn 09 closed the three-bet-pot river lesson sequence. Turn 10 instead
fills the distinct gap below the existing 10–20 BB short-stack guide.
It avoids presenting solver frequencies or a purported universal shove
chart where no verified range model was supplied.

The common fictional setting is nine-handed no-limit Hold'em, 0.5/1 BB
blinds and **one fully funded 1 BB big-blind ante**. Unposted cutoff
stacks are specified before posting, and each alternative branch
resets rather than accumulating unrelated contributions.

### Independently auditable decision cases

- Cutoff first-in **3, 4 and 5 BB shoves**, each called solely by a
  covering big blind: additional calls of **2, 3 and 4 BB**; final pots
  of **7.5, 9.5 and 11.5 BB**; no-tie chip call prices of approximately
  **26.67%, 31.58% and 34.78%**.
- The same **4 BB cutoff shove** called by the button, small blind or
  big blind as **separate one-caller histories**. Respectively, they
  owe 4, 3.5 or 3 BB and face prices of **38.10%, 35% or 31.58%**.
  The single big-blind ante never acts as a live call credit.
- An all-fold branch returns the unmatched four-chip shove to cutoff,
  who profits by the existing **2.5 BB** forced pot rather than the
  larger temporary pot after announcing all-in.
- One explicitly invented conditional chip-EV model: at a 30% joint
  fold probability and a 40% conditional win probability against the
  only covering caller, shoving gains **+0.61 BB** relative to folding.
  Replacing 40% with 30% makes it **-0.055 BB**. Its pure zero-equity
  fold thresholds with versus without the ante are **61.54%** and
  **72.73%**, respectively. None are predictions of opponent behavior.
- A legal **2 BB total minimum open** from a 4 BB stack, followed by
  a 1 BB big-blind call for a **5.5 BB** flop pot, or a big-blind
  re-raise to 4 BB total, costing cutoff 2 BB more and resulting in a
  **9.5 BB** all-in pot. This branch shows why restricted push/fold
  input trees cannot select among unmodeled small raises.
- A separately reset **3 BB starting big blind** that fully posts both
  the blind and ante, then calls with its last 1 BB against a 4 BB
  cutoff shove. Only 2 BB of cutoff's shove is matched, 2 BB returns,
  and the contested pot is **5.5 BB**. The simplified extra-chip call
  price is **18.18%**. No partially funded blind or ante is invented.
- A **5 BB full rejam** over a 2 BB hijack open. Hijack owes 3 BB to
  call into a **12.5 BB** final pot, a **24%** no-tie price. An
  unmatched 3 BB is returned if hijack folds.
- A **3 BB short all-in** over a 2.5 BB hijack open. The all-in's
  half-blind increment does not reopen hijack's raising option under
  **Poker TDA 2026 Rule 49** when there is no intervening full raise.
  Hijack owes 0.5 BB into an **8.5 BB** final pot, about **5.88%**.
- Eight native hidden-answer self-checks, a six-line hand-reconstruction
  worksheet, a model-limits table and an explicit responsible study
  boundary, with no recommendation to play a named hand.

The relevant primary references are the [Poker TDA 2026 rules](https://www.pokertda.com/view-poker-tda-rules/)
(Rules 45 and 49), [HoldemResources' free restricted Nash ICM tool](https://www.holdemresources.net/nashicm)
and [GTO Wizard's custom-solution model inputs](https://help.gtowizard.com/how-to-build-custom-solutions/).
None is described as having solved the article's fictional scenarios.
The TDA is used as a rules reference, not a claim about every venue.

## Site integration and reader experience

- Registered the canonical page and its dated publication metadata in
  `_source/pages.json`, plus one primary tournament topic in the Poker
  Library and a related placement in the strategy topic hub.
- Added distinct contextual prose inlinks from the existing 10–20 BB
  short-stack guide, chart-reading lesson, ICM primer, tournament-format
  explainer and betting-rules guide. The new guide also links outward to
  seven relevant original guides.
- Kept the two five-column comparison tables inside keyboard-focusable,
  horizontally scrollable regions with visible mobile scroll cues.
  Reused the existing short-stack stylesheet and its print treatment,
  with no new external CSS or JavaScript dependency.
- Regenerated the original article, Poker Library, Poker Finder, topic
  navigation, main index, Poker and combined RSS feeds and sitemap.
- The page supports non-JavaScript disclosure questions using native
  `<details>` markup. The planned visual/browser verification remains
  separate from these source and HTML claims.

## Locally measured navigation

These measurements cover **locally generated source routes**. They do
not prove search rankings, indexation, live reach, or reader outcomes.

| Measure | Turn 09 | Turn 10 |
| --- | ---: | ---: |
| Original Poker guides | 66 | 67 |
| Distinct guide-to-guide prose links | 358 | 370 |
| Guides with at most one incoming prose link | 0 | 0 |
| Guides unreachable from the Poker entry routes | 0 | 0 |
| New guide's direct prose inlinks | Not published | 5 |
| New guide's direct prose outlinks | Not published | 7 |

The generated coverage matrix now lists **67 original Poker guides**,
**146 externally catalogued resources**, **10 topic hubs** and
**13 curated resource collections**. Resource review metadata is not a
new live link recheck; no additional external catalogue record was made.

## Local verification and limitations

- `python _scripts/build.py`: **245 generated files**; the final
  deterministic `--check` produced **zero differences**.
- `python _scripts/poker_coverage_matrix.py --write`: regenerated the
  current 67-guide inventory from versioned manifests.
- `python _scripts/check_internal_links.py`: **15,198 internal links**
  in **221 HTML pages**, **zero link or fragment issues**.
- `python _scripts/check_search.py`: **216 sitemap URLs**, unique
  titles/descriptions, **zero SEO check errors**.
- `python _tests/check_html5.py` with the repository's pinned
  `html5lib==1.1`: **221 pages passed**.
- `python -m unittest`, with `_tests` on the Python import path:
  **43 focused tests passed**, including ten new Turn 10 rational-
  arithmetic and navigation tests, Turn 09 river regression coverage,
  Poker Library, topic and link-graph tests.
- A new browser smoke script verifies four viewport widths, keyboard
  answer reveals, contextual source-link arrivals, and the no-JavaScript
  page. **Browser execution could not run here**: system Chromium failed
  at its process-singleton socket with `Operation not permitted`.
  Therefore no measured mobile layout, interactive browser result or
  visual accessibility outcome is claimed.
- The broad historical local-release checklist ended **81 of 92 groups
  passing**, with 11 known historical failures. Examples include an
  old Stand Off test hard-coding **95** Poker results in site-wide Find,
  a standalone Find packed-data size cap, and older expectations about
  search ordering and unrelated Technology pages. These are not
  evidence that this new guide's focused tests failed, but the full
  historical release suite is **not** green.
- The main builder regenerated an unrelated Technology visibility
  page with pre-existing drift. Exclude
  `technology/ai-website-visibility/index.html` from this turn's
  commit instead of treating unrelated output as an approved edit.

No GitHub Actions, CI subscription, scheduled task, paid API, tracking
service, client data or private analytics were added.

## Suggested Turn 11

Add a distinct **6–10 BB tournament decision guide** that makes the
transition from nearly forced short-stack play to meaningful
minraise/reshove response trees auditable. Specify fully independent
positions and pre-posting conventions. Compare first-in shoves,
small opens, reshoves and blind-defense action points without importing
exact ranges from incompatible push/fold charts. Verify arithmetic,
link it to this 3–5 BB guide and the existing 10–20 BB guide, and keep
satellite-seat-bubble calculations for a later separately sourced
lesson. Preserve the same local deterministic checks and privacy rules.
