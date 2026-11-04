# Visibility sprint, Turn 22: Offline fact gate for AI-assisted poker vlog edits

**Review date:** November 4, 2026 (America/New_York)  
**Site:** https://nolankido.com/  
**Reader section:** https://nolankido.com/technology/#poker-vlog-qa-demo  
**Executable checker:** https://nolankido.com/downloads/poker-vlog-fact-gate.py  
**Companion worksheet:** https://nolankido.com/downloads/poker-vlog-truth-to-screen-qa.md

## Why this was the next improvement

Turn 21 published an editorial method for reconciling a poker narration, the hand source, and on-screen graphics. The method was useful but did not include a runnable example that demonstrated what an independent structured-data check can and cannot catch.

Turn 22 publishes a bounded offline checker and four paired before/after examples. It uses the already public Portland Meadows Episode 1 companion as its finite fact source. It reports exactly which deliberately fabricated edit claims conflict with that public source and shows their correction. This is original practical technology evidence, not a claim that the tool watched an actual video, used an AI model, or repaired a previously released vlog.

## Files changed

- `_source/technology/home.html` and `technology/index.html`: identical new accessible case-study section, four-row before/after table, direct downloadable checker link and explicit evidence limits.
- `downloads/poker-vlog-fact-gate.py`: standalone Python 3.10+ standard-library tool with `--self-test`, `--example` and `--check SCENES.json`. It reads only explicitly selected local JSON and never sends data to a remote service.
- `downloads/poker-vlog-truth-to-screen-qa.md`: added clear offline commands, supported cases, input/output semantics and limits.
- `_tests/test_turn22_poker_vlog_fact_gate.py`: local-only checks for deterministic examples, JSON validation, source/public parity, preserved page metadata, generator output and exact Git predecessor integrity.
- `_tests/turn22_poker_vlog_fact_gate_history.py`: restores only the three precisely reviewed HTML/worksheet blobs and recognizes the one added script SHA. Unknown edits pass through unchanged.
- `_tests/turn21_poker_vlog_qa_history.py` and `_tests/test_turn21_poker_vlog_qa.py`: narrow predecessor-chain updates so archived Turn 21 blob assertions remain meaningful after this additive release.

Unrelated routes, existing article dates, Person identifiers, canonical URLs, site metadata, three project cards, feeds, sitemap and private working files were not changed. No GitHub Actions, CI, cron, scheduled service, paid API or model call was added.

## What was measured, and what was not

The self-test operates on four **deliberately constructed** incorrect structured scene records, each paired with a corrected version. They are test fixtures, not actual edit defects or model outputs.

| Synthetic before case | Expected targeted findings | Observed flags | After correction |
| --- | ---: | ---: | ---: |
| Unverified hole-card suits and complete board shown as known | 2 | 2 | 0 |
| Pocket sevens stack mislabeled 18 BB and button open mislabeled 2 BB | 2 | 2 | 0 |
| Advertised $5,100 first prize shown as actual receipt instead of the reported $2,900 deal payment | 1 | 1 | 0 |
| A verified solver decision and archived version 7 chapter timecode claimed for the current cut | 2 | 2 | 0 |
| **Total** | **7** | **7** | **0** |

The script validates only explicit structured input fields against its three public source records: `hand_64o`, `hand_77`, and `event_payout`. A result of `no_targeted_flags` does not establish that audio and visuals agree, footage permissions exist, a solver analysis is correct, the source itself is independently verified, an edited video is improved, or viewers are more satisfied.

## Checks and publication

- [PR #178](https://github.com/nolankido/nolankido.github.io/pull/178) squash-merged the intended eight-file diff into `main` as commit `d561e88410116cb73dfdb42cc25b539b71597c89`.
- Re-fetched all eight files from the review branch before merging. Each matched the fully reviewed prepared content exactly.
- Verified after merging that the edited source, generated HTML, worksheet and checker content matched `main` exactly.
- Ran the checker in local Python memory. AST syntax parse, all four synthetic before/after cases, seven-to-zero exact targeted findings, clean JSON, flagged JSON, invalid JSON and documented exit codes passed.
- Python AST checks passed for the new and modified test/history modules. Checked balanced HTML nesting, accessible table headers, source/public section parity, exact predecessor reconstitution, canonical URL, site modification date and absence of em dashes.
- **Live publication:** Confirmed on the live Technology page after propagation: the new four-row example, human-review caveat and Python download hyperlink were present in the page HTML. The updated Markdown worksheet returned its new command section in a separate live fetch. The page-fetching tools could not retrieve the standalone `.py` download directly (`target_unreachable`), but the complete Python file was re-fetched from the merged GitHub `main` branch and matched the reviewed source byte-for-byte..
- Full repository builder, HTML5 sweep, full unittest discovery and browser suites could not be run because this execution environment has no writable local repository checkout. The committed test module includes further checks for a local checkout; these are not represented as already passed.

The GSC Wizard Search Console connector returned `INVALID_ARGUMENT` again for property listing. No private click, impression, keyword, CTR or traffic uplift data was inferred or added to this public record.

## Next direction

The next useful advancement is to apply the same source/claim/evidence separation to another publicly documented work product with an observable outcome, rather than adding more speculative SEO copy. An end-to-end actual video analysis would require source media, a current-cut review and explicit privacy/rights checks; these synthetic controls do not substitute for that review.
