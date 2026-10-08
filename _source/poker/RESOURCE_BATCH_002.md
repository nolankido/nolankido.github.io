# Poker resources: batch 002

Reviewed October 7, 2026, Pacific time. This record describes a completed research pass; deployment status is recorded by its pull request, not implied by this document.

## What this batch changes

Starting catalogue: 62 resources. Accepted additions: 20, comprising 19 Free listings and one Paid course. Resulting catalogue: 82 resources in the same 13 categories, with 65 Free, seven Mixed, and ten Paid listings. Seven additions expand variants; six expand technical research; four expand tournament study; two expand viewing/course archives; one expands mathematics.

This pass directly read the public destination text, catalogue, documentation landing page, or paper abstract for the 20 additions. It also directly read the existing official Poker TDA page, replacing that entry's former search-index-only review. The other 61 existing resources were not freshly reviewed in this pass. Listing review does not certify accuracy, software security, profitability, or permission to use a tool during play.

## Accepted destinations

Each stable ID below maps to one record in `resources.json`. Descriptions there are original and identify the specific benefit rather than reproducing source articles. Related pages from one publisher were retained only for different subjects or purposes.

| Stable ID and destination | What was inspected | Important limit |
| --- | --- | --- |
| [mit-theory](https://ocw.mit.edu/courses/15-s50-poker-theory-and-analytics-january-iap-2015/) | Public course description and material index | Historical course material, not a current software guide or a profitability guarantee. Course catalogue inspected; lessons were not completed. |
| [mit-holdem](https://ocw.mit.edu/courses/15-s50-how-to-win-at-texas-holdem-poker-january-iap-2016/) | Public course description and material index | The title is the course title, not this directory's promise. Historical instruction; catalogue inspected, not all videos watched. |
| [satellite-guide](https://blog.gtowizard.com/satellite-guide/) | Public article or reference text | Covers multi-seat satellites, not winner-take-all or target-stack formats. Examples are model-dependent; follow event timing rules. |
| [mystery-bounty-guide](https://blog.gtowizard.com/mystery-bounty-guide/) | Public article or reference text | Use the actual event structure. The article's examples and commercial tool links are not a verified solution to your hand. |
| [bounty-models](https://blog.gtowizard.com/bounty-models-explained-solving-knockout-tournaments/) | Public article or reference text | A model explanation from a software provider. Listing the article does not independently validate its models or outputs. |
| [satellite-masterclass](https://www.learnpropoker.com/dara-okearney-satellite-masterclass) | Public course syllabus and offer | Paid course. Only the public syllabus and access offer were inspected; lessons, teaching quality, and results were not assessed. |
| [badugi-introduction](https://www.cardplayer.com/cardplayer-poker-magazines/66431-cppt-ocean-s-eleven-33-6/articles/23940-badugi-an-introduction) | Public article or reference text | Published in 2020. Strategy commentary, not a solved chart; the publisher also carries gambling promotions. |
| [triple-draw-starting-hands](https://www.cardplayer.com/poker-news/24663-poker-strategy-with-kevin-haney-triple-draw-lowball-starting-hands) | Public article or reference text | Published in 2020. The author's strategic judgments depend on the stated game and opponents; not universal opening ranges. |
| [triple-draw-breaking](https://www.cardplayer.com/cardplayer-poker-magazines/66511-dan-zack-36-7/articles/24787-deuce-to-seven-triple-draw-breaking-on-the-turn) | Public article or reference text | Published in 2023. This is an opponent-dependent decision discussion, separate from the starting-hand article. |
| [pagat-badugi](https://www.pagat.com/poker/variants/badugi.html) | Public article or reference text | Rules reference rather than strategy instruction. Confirm local variations before using it to interpret a particular event. |
| [pagat-lowball](https://www.pagat.com/poker/variants/lowball.html) | Public article or reference text | Different conventions treat aces, straights, and flushes differently. Use the section for the game actually being studied. |
| [mixed-game-rotations](https://www.mixedgames.net/the-games/) | Public article or reference text | A companion reference, not an organizer's rulebook. Agree the specific rotation and local rules separately. |
| [pagat-omaha-variants](https://www.pagat.com/poker/variants/omaha.html) | Public article or reference text | This complements the existing basic Omaha link with variant detail. The actual game rules still control. |
| [aivat](https://arxiv.org/abs/1612.06915) | Abstract and bibliographic metadata | Abstract and metadata inspected, not a full-paper audit or replication. The listed method has information and modeling requirements. |
| [deepstack](https://arxiv.org/abs/1701.01724) | Abstract and bibliographic metadata | Abstract and metadata inspected. Heads-up research is not a six-player tournament solution or a verified product recommendation. |
| [av-aivat](https://arxiv.org/abs/2608.06362) | Abstract and bibliographic metadata | Abstract and metadata only. Its asymptotic results and finite-sample guarantees are distinct; headline efficiency claims were not replicated. |
| [rlcard](https://rlcard.org/) | Public documentation or specification introduction | Documentation inspected; no installation or code audit. Check the particular environment's rules and action abstractions. |
| [phh-format](https://phh.readthedocs.io/en/stable/) | Public documentation or specification introduction | The format documents records; it cannot establish that a hand actually happened. Keep private participant details out of shared examples. |
| [phh-dataset](https://zenodo.org/records/17136841) | Public dataset record and download catalogue | Catalogue only; the large archive was not downloaded. Check provenance, licensing, and duplicate-hand warnings before analysis. |
| [pokerbank-videos](https://www.thepokerbank.com/videos/) | Public video index | The archive says it is no longer updated. Older software, HUD, and player-pool references may not apply today; playback was not tested. |

## Corrections and resolved candidates

The `tda-rules` record now identifies the directly readable 2026 rules, version 1.0, dated September 7, 2026. Its review method is `page`, not `index`. The rules supplement house rules and applicable agency requirements; the directory is not an event ruling.

Two previously unresolved MIT candidates had incorrect URL spellings. `mit-theory` is Poker Theory and **Analytics**, not Analysis. `mit-holdem` uses **holdem**, not hold-em, in its canonical course slug. Both original candidate URLs and accepted destinations remain in the backlog's resolved section. Neither failed old URL was treated as proof that the course had disappeared.

Historical material is useful when labeled honestly. The MIT courses are from 2015 and 2016. The Poker Bank explicitly describes its video collection as no longer updated. Older signed Card Player articles remain dated instructional viewpoints, not newly verified universal strategy. None was represented as a new release.

## Unresolved and excluded scope

Triton, Global Poker Index, and the redirected CardsChat forum remain in the existing needs-review queue. This batch does not claim to have rechecked or resolved them. No additional unreviewed search result was promoted into the public catalogue.

No videos were played to completion, courses purchased, software installed or executed, dataset archives downloaded, or research papers replicated. Paper listings are based on abstracts and metadata, not an inspection of every theorem, figure, or experimental detail. The 2026 AV-AIVAT record is explicitly a preprint. The PHH dataset destination was inspected at the catalogue level only.

## Next-pass handoff

`RESOURCE_BACKLOG.json` now supplies six prioritized research briefs, each with its own question, query suggestions, and acceptance criteria: verified creators and beginner video; original live-event information; cash/PLO/split-pot study; documented tools and datasets; community/history/home games; and support/rules/accessibility. These are planned research batches, not scheduled jobs or accepted listings.

Use the reusable research instruction in `RESOURCE_PROCESS.md`. Begin with one or two uncovered questions, evaluate a manageable batch, write only accepted records into `resources.json`, and retain a short difference report. There is no permanent link cap. Grow subject coverage and publisher diversity while preserving direct links, useful access labels, and the separation between editorial decisions and automated checks.

## Release checks

Build source and generated pages together. Run the unit suite and existing full browser CI, including resource filters with the new topic vocabulary. Check mobile and desktop portions of the directory, verify the exact staged tree, and merge only a passing head. Confirm Pages deployment and published-file bytes separately. The temporary source-snapshot workflow must be absent from the final release.

No recurring search, automatic remote-link checker, notification, or automatic publication is enabled by this batch. No private owner material, personal story, tracking change, or shared redesign is part of it.
