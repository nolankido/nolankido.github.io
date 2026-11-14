# Poker guide contextual-link audit: November 14, 2026

Scope: the 60 published guides in `/poker/library/` and the actual generated
Poker HTML. This is a publicly reproducible editorial check, not a search-engine
crawl, search-rank claim, traffic measurement or the owner's private sprint plan.

## The reader problem

Every guide has a place in the library and the topic navigation, and the
generator also appends related-reading cards. However, a reader finishing a
particular explanation benefits more from a relevant, named next step at the
point of confusion. The earlier directories and generic footers can conceal
articles with little contextual support from other guides.

## How the graph is measured

`python _scripts/poker_link_graph.py` reads generated public HTML using
`check_live.targets()`, the same route inventory used by the local link check.
It resolves internal anchor destinations to canonical paths and counts unique
guide-to-guide links within the page's main body.

The stricter **prose** graph includes anchors in paragraphs and list items,
but excludes global navigation, page headers, breadcrumbs, reading outlines,
topic-context strips, automatic related-reading cards and sharing widgets.
Multiple anchors from one guide to the same destination count as **one**
directed edge. Every guide's inbound count reflects **distinct other guides**,
not sitewide navigation and not the number of hyperlink occurrences.

Reachability is measured separately using all links within the main area,
starting from the Poker home, library and topics pages. It confirms the
published reader journey, not whether any web crawler has indexed a page.
The script does not rewrite pages or select links automatically. Broken routes,
fragments and local Finder states remain the responsibility of
`python _scripts/check_internal_links.py`.

## Measured outcome

| Measurement | Before | After |
| --- | ---: | ---: |
| Published library guides | 60 | 60 |
| Generated Poker HTML pages in audit | 95 | 95 |
| Unique directed guide-to-guide prose edges | 273 | 284 |
| Guides with zero or one prose inbound guide | 7 | 0 |
| Guides unreachable from the Poker entry points | 0 | 0 |

The eleven newly measured edges are ordinary editorial links added within
ten existing source articles. No guide was duplicated, no canonical path was
changed, and no external source was reclassified or endorsed.

## Edits where the reader needs them

| Source guide | Added guide destination | Reason at the insertion point |
| --- | --- | --- |
| `holdem-basics` | `follow-along` | After checking action order, pause before fictional hand reveals. |
| `hand-rankings` | `follow-along` | Move from knowing showdown ranks to tracking decisions as they unfold. |
| `poker-math` | `practice-room` | Test whether call-price and draw-probability distinctions transfer to changed questions. |
| `range-combinations` | `practice-room` | Apply physical combination counts separately from assumed betting frequencies. |
| `choosing-study-tools` | `poker-books-and-courses` | Consider explanatory reading before paying for calculation software. |
| `poker-media-study` | `poker-books-and-courses` | Choose structured text when a lecture has not answered the question. |
| `poker-media-study` | `practice-room` | Move from passive viewing into a short applied calculation check. |
| `poker-research-guide` | `evaluating-poker-advice` | Separate a paper's stated scope from claims repeated in media or discussions. |
| `hand-to-vlog` | `poker-media-study` | Analyze a viewer's information before a reveal, without a claim about retention. |
| `evaluating-poker-advice` | `poker-research-guide` | Check the actual game and evaluation behind an AI or solved-game claim. |
| `omaha-hi-lo-workshop` | `stud-and-lowball-workshop` | Avoid transferring Omaha-low rules to a different lowball game. |

These paths are distinct reader questions, not automated keyword insertions.
The links do not recommend playing for money, assert solver outputs or change
the original fictional hands and source-review limits.

## Reproduce and check

From the repository root:

```sh
python _scripts/build.py --check
python _scripts/poker_link_graph.py
python -m unittest discover -s _tests -p 'test_poker_link_graph.py' -v
python _scripts/check_internal_links.py
python _scripts/check_search.py
python _tests/check_html5.py
```

The focused tests verify origin handling, the exclusion of global/automatic
navigation, all 60 guide routes, graph-count consistency, entry-point
reachability and a minimum of two other guide-prose inlink sources for every
existing guide. Future guide creation should meet that threshold with
editorially justified links, not filler text. A successful link graph does
not certify the quality of the underlying strategy examples or measure SEO
benefits.

The next editorial release should fill the highest-priority topical content
gaps identified by the coverage matrix, while adding incoming context links
from the parent topic and relevant existing articles before publication.
