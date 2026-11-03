# Visibility sprint Turn 10: repair the public poker-video viewing path

**Review date:** November 3, 2026  
**Status:** Source and compiled-output corrections prepared; deployment must be verified separately.  
**Public companion:** <https://nolankido.com/poker/episodes/portland-meadows-ep1/>  
**Owner requirement:** No GitHub Actions, scheduled workflows, paid APIs or invented event details.

## Problem and directly observed evidence

The Episode 1 companion was sending viewers to <https://www.youtube.com/watch?v=JToB7upHqEM>. A read-only public retrieval on November 3 returned a YouTube **Private video** sign-in wall. This is not a usable viewing path for a new visitor.

The replacement at <https://www.youtube.com/watch?v=qABaiIcvvpU> returned the public title **I Had 6.5 Big Blinds... Then Won a Trophy**. Two other public uploads were independently reachable by title:

- <https://www.youtube.com/watch?v=I75GOBVXij4>: **I Had A-K With 10 Big Blinds. Then TWO Players Shoved.**
- <https://www.youtube.com/watch?v=edNSD5BjIV8>: **7 BB Near the Money... Then a Massive A-K Pot | WSOP Circuit**

The retrieval supported public title and access, not a frame-by-frame check of narration, hand details, precise runtime or chapter timing. Do not treat it as verification of every hand in the newer cuts.

## Implemented editorial boundary

1. The primary Episode 1 watch action and source references now point to the accessible public upload.
2. The old version 7 time-stamped chapter links are removed. The story topics remain useful as an **archived version 7 narration map**, with an explicit warning that offsets were not rechecked in the current video.
3. Two existing first-person hand records, their stable fragment identifiers, original publication date, payout distinctions and uncertainty disclosures are preserved.
4. Two other public videos are linked as **separate uploads**, explicitly without claiming that their source-checked written companions are published.
5. The source and generated companion HTML are updated together; the episode registry refuses the superseded private video identifier. Focused tests check both current links and the absence of unsupported offsets.
6. A test-only exact-blob predecessor restores the previous approved release for older history tests. It does not change visitor-facing content or conceal unknown future edits.

## Verification and follow-up

- The old private-video sign-in wall and the three public replacement titles were observed via read-only public page retrieval.
- Before the GitHub change, the new source appeared exactly once in the generated HTML; one H1, one JSON-LD record, the existing hand fragments, public links and no iframe/form/em dash were checked in memory.
- Seven changed or added Python files passed a local Python AST parse. The entire website and browser suites were **not run** because this execution environment has no writable full checkout. Do not present in-memory assertions as a passing full release gate.
- A post-merge public HTTP retrieval should verify that the companion now exposes the accessible URL. Actual YouTube content, platform permanence, Google indexing, AI citations and search growth remain separate unknowns.
