# Visibility sprint, Turn 21: Truth-to-screen QA for an AI-assisted poker vlog

**Review date:** November 3, 2026 (America/New_York)  
**Site:** https://nolankido.com/  
**Reader section:** https://nolankido.com/technology/#poker-vlog-qa  
**Reusable worksheet:** https://nolankido.com/downloads/poker-vlog-truth-to-screen-qa.md

## Why this is useful public evidence

The Technology hub explains how Nolan Kido applies AI in real work. The Poker section already publishes a carefully bounded record of two decisions in Portland Meadows Episode 1, but readers had no reusable way to check whether an AI-assisted edit represents the reported hand accurately. Turn 21 connects these areas with an original, openly inspectable editorial release gate.

The new method tests the *agreement* of a voiceover, the screen and the source record. It does not make the source record more authoritative, create missing facts, certify a solver decision, or demonstrate higher retention. This is a proposed reusable control, not a representation that it was applied to every existing video.

## What changed

- Edited `_source/technology/home.html` and the manually maintained `technology/index.html` output with one source-identical semantic section. It includes a screen-reader accessible table and a five-step process, linked to the public Episode 1 companion.
- Published `downloads/poker-vlog-truth-to-screen-qa.md`, an original standalone template covering provenance categories, scene acceptance, factual uncertainty, graphics/VO reconciliation, and a final release gate. It calls no API.
- Added `_tests/test_turn21_poker_vlog_qa.py` to check source/public parity, anchors, precise math, worksheet content, old page identity, generator output and SHA-gated predecessor behavior.
- Added `_tests/turn21_poker_vlog_qa_history.py` to undo only the reviewed two Git blobs, with an exact content check and a fail-open policy for unknown mutations. Narrowly updated `_tests/turn17_site_visibility_evidence_history.py`, `_tests/test_turn17_site_visibility_evidence.py`, and `_tests/brand_positioning_history.py` to preserve old snapshot tests.

All existing article routes, page canonical, metadata date, three project cards, feeds, sitemap and pre-existing graphics remain intact. No scheduled task, GitHub Actions workflow, paid API, collection form, private video clip or personal production note was introduced.

## Facts used, and facts deliberately not filled in

The [Portland Meadows Episode 1 companion](https://nolankido.com/poker/episodes/portland-meadows-ep1/) is the public source for the worked examples.

| Scene | Supported public account | Editorial limit |
| --- | --- | --- |
| 6-4 offsuit | Small blind, 13 remaining, 10 paid, around 148k chips at 15k BB: about 9.87 BB if stack timing is pre-posting. Shove called by A-K suited; a four comes and the hand wins. | No individual suits, complete board, exact effective stack, or proven solver/ICM result. |
| Pocket sevens | Big blind four-handed, about 585k at 30k BB: 19.5 BB. Button opens to 75k total: 2.5 BB. Reshove is called by A-T offsuit; 77 holds. | No invented runout, opponent range, or contemporaneous solver thought. |
| Tournament result | Advertised first prize was $5,100; reported receipt after a four-way deal was $2,900. | Do not substitute prize for payment, or claim net profit. |
| Edit timing | Archived version 7 was the companion's chronology source. | The live upload is a newer cut. Old chapter offsets are not assumed current. |

## Review and checks

- [PR #177](https://github.com/nolankido/nolankido.github.io/pull/177) was squash-merged into `main` as `be8e34fecefdb2aaff7539566711b015673bbdf2`.
- Compared the eight-file diff to `main`. Only the planned article, worksheet and test-history changes were present.
- Re-fetched all eight files from the review branch and compared their full content exactly with the prepared changes.
- Verified after merge that the source HTML, generated HTML and worksheet blobs on `main` match the reviewed content exactly.
- Ran Python AST syntax checks for all five new/modified Python test/history modules. HTML tag nesting, table counts, linked companion IDs, arithmetic, metadata, no remote script/iframe and no em dashes were checked from the prepared content.
- Confirmed the inserted section can be removed exactly from both edited files to reproduce their previous reviewed contents.
- Full in-repository build, unittest discovery and browser interaction tests could not be run in this read-only, connector-backed environment. The committed test module contains additional assertions intended for a normal local checkout; those assertions were not represented as already executed.
- **Live publication:** Confirmed. After GitHub Pages propagation, the live Technology hub returned the new QA section, supported hand examples, explicit limits and Markdown download anchor. The public worksheet URL returned its complete title and release-gate content on a separate direct fetch. No browser playback or end-to-end video edit was inspected..

The connected Search Console opportunity endpoint and property listing returned `INVALID_ARGUMENT` during this turn. No private impressions, clicks, rankings, referral sources or claims of SEO uplift were inferred or published.

## Next direction

For another substantial turn, seek a public and reproducible before/after outcome where AI changes an actual workflow. Keep the boundary between a proposed method and completed, observed practice explicit. Only use private analytics to prioritize edits in a private work note, not in the public sprint report.
