# SEO/GEO Sprint Turn 07: a usable AI answer-checking reference

**Prepared:** November 18, 2026

**Source base:** `8a10fe67421bb7f999cbab6cdde73b45857712c2` (Turn 06)

**Canonical destination:** <https://nolankido.com/technology/check-ai-answers/>
**Task:** improve the existing guide for a reader asking how to verify an AI-generated claim before acting, without presenting historical examples as current benchmarks.

## The reader problem and the intervention

The existing guide already contained six worked checks, a reusable full record and three traceable archived failures. Its early answer was lengthy, and the six-choice navigation appeared after the long archived-case and mini-check introduction. A reader with one consequential claim did not have a short route to the relevant test.

This turn keeps the original canonical URL and October 12 publication date, while making these substantive November 18 improvements:

1. Lead with the answer: isolate a claim, independently check it, then mark it supported, contradicted or unresolved before deciding what action is justified.
2. Add a six-row evidence matrix with warning sign, discriminating independent check, narrowed or repaired answer, and remaining unknown. Its cases are explicitly **fictional instructional scenarios**, not new model outputs or measured rates.
3. Move the existing six-method navigation before the long archived cases, preserving every original anchor and worked exercise.
4. Add the offline, approximately one-page plain-text [quick checklist](../../downloads/ai-answer-quick-check.txt) with six steps and a fill-in one-claim record. It sends no content, invokes no model and contains no private data.
5. Expand the archived Review Reply Writer example to show why a polished, accepted response can still omit an original detail. An editorial rewrite is clearly marked as a **proposed human edit**, not an observed model response, delivered reply or endorsement.
6. Link the Preflight and HTML5 repair cases back to the evidence matrix. Review Reply Writer and Task Brief Builder already contained backlinks; these remain intact. No competing FAQ or extra article URL was added.

## Independent claims and source checks

| Demonstration | Verified source or computation | Safe takeaway and limit |
| --- | --- | --- |
| Misleading citation in the fictional facts exercise | [NIST AI 600-1, section 2.2, Confabulation](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf#page=9), printed page 6, PDF page 9 | This passage discusses confident generated errors and misleading reasoning/citations. It does not say two agreeing chatbots confer 99% reliability. The example is a deliberately fabricated claim, not a NIST finding or a measured tool failure. |
| Incomplete time-saving calculation | Fictional inputs: usual 12 × 20 = 240 minutes; assisted 30 + 12 × (6 + 7) + 18 = 204; difference = **36 minutes**, not the **168 minutes** obtained by counting only drafting | Arithmetic is reproducible. None of the times was measured in a real workflow. |
| Polished but detail-losing reply | [Review Reply Writer, archived fictional review and model attempts](https://github.com/nolankido/reviewReplyWriter/blob/1c5e0487c331d5202410c9f342557d9355951c3a/examples/evaluation/live-smoke-2026-10-13.json) | The user input stated a 25-minute wait; accepted retry said “extended wait.” An empty targeted findings list is not human approval or proof of full fidelity. The prior rejected candidate was falsely flagged for “should have addressed.” This is historical output, not a new run or a real customer record. |
| Apparent contradictions in a novel | [Preflight's archived Sherlock Holmes corrections](https://github.com/nolankido/canonKeeper/blob/947e9c3d7dbc9bfa719579ca1e697d4479567684/src/canonkeeper/preflight/samples/sherlock-holmes-reviews.json) | Holmes's eye description was part of a disguise, and Nancy Devoy was a maiden name, not an unexplained conflicting married surname. Quotation traceability alone does not prove accurate interpretation. |
| A passing test suite that missed malformed HTML | [Pinned before-and-after website repair](https://github.com/nolankido/nolankido.github.io/compare/2bf8908339e06f604cea00f0254494e17171ecf4...73782caa4697204690c679626b36427c28201234) and the existing [case explanation](../../technology/checking-ai-website-changes/index.html) | The historical candidate passed 347 unit/content tests; a separate HTML5 parse identified an extra closing tag. This establishes a particular failure and repair, not overall correctness or time savings. |
| Discount counterexample | Intentionally wrong `return price - percent` passes 100 with 20%, but returns 30 instead of independently expected 40 for price 50 with 20% | The second input distinguishes a fixed reduction from a percentage. Production input handling and rounding still require review. |

The summary, message and advice examples also remain fictional. The published date of the answer guide is unchanged; `dateModified` and the two substantive case-page link revisions use November 18, 2026. Canonical paths, author `@id`, privacy links and the existing full printable record are retained.

## Reproducible local verification

- `python3 _scripts/build.py`: **pass**, 253 generated files checked with eight changed outputs on the first run.
- `python3 _scripts/build.py --check`: **pass**, zero drift.
- `python3 _scripts/check_search.py`: **pass**, 224 sitemap URLs, unique titles/descriptions and no metadata errors.
- `python3 _scripts/check_internal_links.py`: **pass**, 231 HTML pages, 16,106 inspected internal links and no missing targets or fragments.
- `python3 _tests/check_html5.py`: **pass**, 229 parsed pages, no errors.
- `python3 -m unittest _tests.test_turn07_ai_answer_entry -v`: **pass**, five focused checks covering matrix consistency, sourced case framing, offline checklist, reciprocal links and publication metadata.
- `PYTHONPATH=_tests python3 -m unittest _tests.test_answer_review _tests.test_turn07_ai_answer_entry -v`: **12 passed, three failed**. The three legacy historical-baseline fixtures fail on `_source/404.html`, generated `404.html` and `feed.xml`, which are unchanged relative to the Turn 06 base. These failures are not accepted as a clean legacy-suite gate, and the fixtures were not rewritten to manufacture a pass.
- The new 320/390/768/1440px offline browser script was **attempted but could not launch Chromium** in this environment: the process failed to create its required socket (`Operation not permitted`). The static 49rem scroll-region and print-width rules were checked, but a live visual mobile pass is still outstanding. No release is described as browser-verified here.

No GitHub Actions, scheduled tests, third-party messages, external model calls or paid services were created or run for this change. The published page continues to describe the existing Umami pageview analytics and font-delivery privacy behavior. The new download itself has no form, JavaScript or outbound requests.

## Search and AI visibility limits

This release improves specificity, direct answers, original source-backed examples and navigation. It does **not** show any measured gain in rankings, Search Console clicks/impressions, Bing indexing or citations, assistant citations, page engagement or reader satisfaction. Those values remain unverified, not zero. The technical indexability checks establish on-site eligibility properties, not engine inclusion.

## Next decision: Turn 08

Inventory the publicly shareable original task fixtures, local hardware measurements, model versions, review time and comparable hosted-run evidence. Run a matched local-versus-hosted task **only if both sides are genuinely available and approved**. Otherwise improve a reproducible offline local-check artifact and explicitly record the missing hosted counterpart, without inventing laptop benchmarks or whole-task time savings.
