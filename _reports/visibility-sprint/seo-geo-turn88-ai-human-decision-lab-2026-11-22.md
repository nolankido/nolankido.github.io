# SEO/GEO Turn 88: add an original AI Works, Human Decides decision-review exercise

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Starting main:** `85c062f727d83e9293328e74586d4e56b8b01924` (merged Turn 87)  
**Existing canonical author catalog:** `https://nolankido.com/books/`  
**Existing Technology hub:** `https://nolankido.com/technology/`  
**New free non-indexed-format download:** `/downloads/ai-human-decision-review-worksheet.md`

## User-serving opportunity

The Books author catalog already offered two original, free worked examples linked to the two detailed book pages. The separate, author-supplied Kindle title *AI Works, Human Decides* had a product link and related free reading, but no concrete stand-alone exercise that readers could complete without buying a book or opening an AI service.

This improvement supplies a complete **original site-only practice case** inside the existing Books catalog rather than fabricating a third author-book landing page, claiming an unverified retailer edition, or reproducing book material. It gives readers a direct test of the site's standing approach: define the permitted inputs, check all claims against the source, retain human authorization, and count the real work of review.

## Actual implemented changes

1. **Books catalog.** Insert the `#ai-works-decision-lab` h3 into the existing free learning section, after the previously established AI workflow and poker exercises. Add an accessible `<details>` answer reveal under `#ai-works-decision-answer`. Keep the three author-supplied Kindle destinations, old metadata, two detailed author pages, original practice links and original two-work Book ItemList unchanged. From the *AI Works, Human Decides* comparison card link once to the new exercise.
2. **Source facts and answer.** Use a deliberately fictional free community workshop, with Friday 6:00 p.m. start, Thursday noon registration deadline, 24-person capacity, 18 confirmed registrations at a Tuesday 2:00 p.m. snapshot, unknown accessibility details and a designated organizer as the sole publishing authority. A constructed draft contradicts known facts and invents availability, access and publishing authority. The answer recomputes **24 - 18 = 6 at the snapshot only**, explains why a past capacity number is not a current guarantee, and gives a corrected **unpublished** draft. Decisions are REVISE AND RECHECK, HOLD PUBLICATION, and STOP USING AI FOR THIS TASK when private inputs or unauthorized publishing would be required. These are human process labels, not a model verdict.
3. **Free downloadable template.** Add `downloads/ai-human-decision-review-worksheet.md` with the complete fictional source card, constructed draft, blank claim/evidence/action table, approval and privacy gates, an authorization record, and a *blank* full-workflow manual-versus-AI timing comparison. It makes no performance claim and contains no private data or need for an AI account.
4. **Technology hub handoff.** Add one source/output-parallel paragraph in the existing *AI Works, Human Decides* approach section. It links to the new original exercise and worksheet without creating another canonical page.
5. **Read-only release coverage.** Register the new exact public Markdown download path in `_scripts/check_live.py`; add ten local unittest methods in `_tests/test_turn88_ai_human_decision_lab.py` and include them in `_scripts/local_release_checks.py`. No new external tracker, paid API, script injection or GitHub Actions.

## Authenticated source checks already performed

A GitHub readback of the edited branch verified:

| Check | Observed |
| --- | --- |
| Books catalog source/output identical | Yes |
| Technology introduction fragment matches authored source/public output | Yes |
| Third-book card direct exercise link | 1 |
| New exercise heading and answer reveal | 1 each |
| Worksheet link on Books catalog and Technology | 1 each |
| Source arithmetic and actual human approval boundaries in answer | Present |
| Blank worksheet cells | 17 `| |` separator occurrences |
| Registered exact public download target | Yes |
| Added unittest methods | 10 |
| Existing JSON-LD Book ItemList | 2 documented full author works, unchanged |
| Existing catalog modified date | 2026-11-22, unchanged |
| New canonical or standalone Book entity | None |

The above confirms controlled source text and intended links. It is **not** a substitute for a complete checked-out Python/HTML5 build, rendering check, live byte receipt, browser mobile check or observed search traffic.

## Outstanding release checks in a complete checkout

```powershell
py -3 -m unittest discover -s _tests -p test_turn88_ai_human_decision_lab.py -v
py -3 -m unittest discover -s _tests -p test_turn49_book_catalog_handoff.py -v
py -3 -m unittest discover -s _tests -p test_turn47_book_edition_evidence.py -v
py -3 _scripts/build_books.py --check
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope all --only /books/ --only /technology/ --only /downloads/ai-human-decision-review-worksheet.md --attempts 8 --interval 15 --workers 1
```

No local complete checkout was available in this runtime because the GitHub host cannot be resolved from the container. Public HTML retrieval after merge may confirm serving but not byte-for-byte parity.

## Prior-turn live deployment checked

A fresh public read on November 22 returned the earlier Turn 87 `#tournament-written-playbook` note on `/poker/topics/tournaments/` and the original `/poker/10bb/` heading, closing the prior live-presence gap. The native Poker Finder's earlier source-type filter concern was not reproducible in the Turn 87 targeted browser check.

## Next improvement priority

Verify Turn 88 deployment and full static/regression tests first. Then favor original, first-party examples that readers can reproduce, direct connections between claims and evidence, and only genuinely verified publication metadata. Do not claim new GSC/Bing rankings, AI assistant citations, sales, model error rates, or time saved without actual measured records.
