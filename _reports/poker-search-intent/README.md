# Poker search: question matching and precise repairs

Prepared October 16, 2026 UTC. This advances the technical portion of roadmap
cycle 12 while qualified teaching review and beginner observations remain open.
The observation-dependent learning-screen redesign is still deferred. No review,
participant, query log, learning gain or user-relevance judgment is invented.

## Reproduced problem and result

At `1d6afff35e16d74a04415f8bc85dafe6f5b369bd`, the actual Poker index returned
six matches for **why did my two pair lose**, omitting the dedicated ranking
guide. Its leading results were the full course, betting-purpose lesson and
long hold'em guide. The question's conversational word “did” was treated as a
required content term, while losing/comparing vocabulary was not connected.

The changed matcher puts [Which hand wins?](https://nolankido.com/poker/hand-rankings/)
first, with its [best-five comparison section](https://nolankido.com/poker/hand-rankings/#ties).
The displayed sentence explains comparing the higher pair, lower pair and fifth
card. It comes from the existing article, not a generated poker answer.

The bounded repair recognizes common question words, multiword poker concepts,
several inflections, and a small explicit set of spelling/notation forms: `tournment`,
`tournamnet`, `kikcer`, `kicer`, `pot ods`, and `2pair`/`two pairs`. It does not
perform arbitrary fuzzy matching. Short abbreviations match whole words, so
BB does not mean BBA. Free does not match freezeout. Unrelated remaining words
still have to match; “two pair football” does not return a hand-ranking answer.
Literal object-property names cannot become inherited alias functions.

Ranking adds bounded subject-title hints and rewards a relevant, complete
passage over matches scattered through a long article. The snippet and section
jump use the same selected existing passage. Prepared text is normalized once,
and each eligible card is scored once per update. This is an implementation
bound, not a measured mobile-performance or accessibility certification.

## Declared regression evidence

| Measure | Frozen baseline | Candidate |
| --- | --- | --- |
| Declared targets in the first three results | 18/30 | 29/30 |
| Original two-pair question | Dedicated reference absent | Dedicated reference first, comparison section linked |
| Previously passing declared cases retained | 18 | All 18 |

[queries.json](queries.json) declares the 30 questions, acceptable destinations
and reasons. It was finalized before modifying the matcher. They were authored
for this regression exercise, not collected from beginners or private analytics.
The initial audit question is a reproduced engineering observation, not a
participant record. The same frozen expectations are used before and after.

[baseline.json](baseline.json) records the old script and index hashes from the
actual Git commit above, with all leading results.
[results.json](results.json) records the current script/index hashes, target
counts, leading results and selected passage evidence. This measures whether
declared destinations appear, not whether every result is useful or correct.
Acceptable lists are deliberately explicit and not an exhaustive relevance set.

The remaining declared miss is **what is ICM**: the dedicated tournament-equity
guide stays outside the first three. A relevant external ICM primer appears in
the first three, so a declared miss does not mean no useful answer exists.
That case and broader ranking quality remain open for human relevance review.
No target was changed to hide it. Commercial sources are not independently
tested or endorsed by their position in a search list.

The roadmap's target of useful results for 27 of 30 real, human-judged beginner
questions is **not closed** by this authored corpus. Nolan's expected-answer
review, actual beginner questions and the deeper resource comparisons remain
pending. Extra changed-wording and adversarial regressions are software checks,
not a held-out learner study or evidence of broad search generalization.

## Scope, privacy and preservation

Only `assets/poker-finder.js` and its generated cache token in `/poker/find/`
change in production. The complete searchable cards, source metadata, article
prose, closed-answer exclusions and native browse fallback stay byte-identical.
Existing filter and study-list workflows retain their contracts. No lesson or
teaching-review snapshot is revised.
Queries remain on the page and are not sent to URLs, requests, storage or
analytics. There is no new dependency, service, account or paid API.

`_tests/poker-search-baseline.json` fingerprints 480 files in the existing
source, script, asset and download directories, plus all 221 generated outputs
from the pinned Git commit. The new history adapter
reverses only the exact SHA-bound script/cache delta before older preservation
checks run. Earlier evidence and golden files are not regenerated. Unreviewed
mutations cannot receive that reversal. The legacy submission contract still
checks its exact old script after this one narrowly scoped adapter.

## Reproduce

From the repository root:

```sh
python _scripts/build.py --check
python _reports/poker-search-intent/evaluate.py --baseline
python _reports/poker-search-intent/evaluate.py
python -m unittest discover -s _tests -p test_poker_search_intent.py -v
python _tests/finder_browser.py
```

The baseline evaluator extracts constants from the pinned old script and uses
its original matching/ranking formula. In a shallow checkout without the parent
Git objects, it reconstructs that snapshot only from the exact reviewed delta,
checking both hashes; it never fetches history or accepts modified input bytes.
The same 18/30 baseline is tested with Git-object access deliberately disabled.
The six-match audit failure is an explicit
regression assertion. The candidate imports the exact browser core and prepares
the same card text parsed from the committed index. Browser regressions check
the real result order, visible sentence, section URL and unrelated-word rejection
alongside the existing input, filter, privacy, print and fallback checks.

After a deliberate candidate edit, rebuild, regenerate `results.json` with
`evaluate.py --write`, and inspect the diff. The frozen baseline writer refuses
a different result. `capture_history.py` can recapture only this release's exact
two-file delta against its fixed parent; any other source or output edit fails.
It never refreshes an earlier release's baseline. A later release needs its own
evidence and adapter rather than widening this one.
