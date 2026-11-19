# SEO/GEO/AEO sprint Turn 16: answer-first book continuity case and editorial log

- **Date:** November 18, 2026 (Hawaii)
- **Property:** https://nolankido.com/
- **Sprint position:** Turn 16 of 25
- **Base checkpoint:** `e7e89f9a95a4c73897aa3c521a703df3d6c41f91` (Turn 15, merged PR #387)
- **Canonical retained:** https://nolankido.com/technology/ai-book-continuity-checker/
- **Scope:** Source-bounded direct answer, a free reusable writing resource, and descriptive links from the existing Technology and Creative pages. No new canonical article, invented benchmark, hosted editor, paid integration or GitHub Actions.

## Reader problem and content change

The existing Preflight case documented the real Sherlock Holmes passage comparisons, source-linked pipeline stages, the complete October 27 seeded benchmark and the important shortcomings. It was evidence-rich but did not directly answer the core search question near the top: **Can AI find continuity errors in a book series, and what should an author do with a flagged passage?**

The revised first section answers that AI can flag real inconsistencies, **but it is not reliable enough to bypass editorial review**. It uses the same rescored benchmark's precise scope: 8 found and 12 missed among 20 deliberately planted changes, with 2 false positives and one separately classified finding. The article avoids implying this is a general accuracy rate.

A new `#continuity-decision` section provides a source-first four-step procedure: save the two actual passages, check whether context explains the difference, record a human disposition, and actively look for facts missed during extraction. It links the [pinned project's source record](https://github.com/nolankido/canonKeeper/blob/947e9c3d7dbc9bfa719579ca1e697d4479567684/README.md#what-it-found-in-sherlock-holmes) and [saved revised scoring report](https://github.com/nolankido/canonKeeper/blob/947e9c3d7dbc9bfa719579ca1e697d4479567684/evals/results/holmes-seed0-2026-10-27/result.md).

The new downloadable [editorial review log](../../downloads/book-continuity-editorial-review-log.md) includes the real Watson shoulder/leg question, a contrasting false positive where disguise or name history changes interpretation, a reusable blank decision record, and a bounded interpretation of the seeded test. It is a static Markdown document, not a manuscript upload, model runner or source of private data. The direct download is explicitly registered with the site's existing read-only public target inventory.

The Technology hub's writing-intent question now offers the new decision fragment. The Creative hub, where prospective authors already discover Preflight, also leads directly to it. The site's search description names the question, sourced results and free log. The original article date, other anchors, canonical, identity and public project sources remain intact. The Creative hub received a substantive update; the article was already modified on November 18 and retains that review date.

## Source verification boundaries

Before editing, I independently fetched the pinned `canonKeeper` source files at `947e9c3d7dbc9bfa719579ca1e697d4479567684`: `README.md`, `evals/results/holmes-seed0-2026-10-27/README.md` and `result.md`. The stored report shows 20 planted, 11 reported, 8 true positives, 2 false positives, 12 misses, precision 0.80 and recall 0.40, with one other finding classified separately. The benchmark README states that the same output was rescored without new model calls, that eight misses were lost at extraction and four at judgment, and that several planted changes had quality problems. The displayed worksheet and page cite these as one imperfect experiment, not a measured result from a new test or proof of the system's current capabilities.

No private manuscript, authenticated customer data, new model run, payment or third-party service interaction was used to create the worksheet. The hosted Preflight demo is not recommended as a destination for private manuscripts.

## Local release verification

| Check | Recorded result |
| --- | --- |
| `python _scripts/build.py` | 253 generated outputs; 8 changed outputs |
| `python _scripts/build.py --check` | 253 checked, no drift |
| `python _scripts/check_search.py` | Pass, 225 sitemap URLs; no metadata errors |
| `python _tests/check_html5.py` | Pass, 230 HTML pages; no parser failures |
| `python _scripts/check_internal_links.py` | Pass, 232 HTML pages and 16,255 internal links; zero issues after registering the new download |
| `python -m unittest discover -s _tests -p 'test_turn16_continuity_answer.py' -v` | Four passed, including source/public agreement, original dates, download inventory and synthetic negative controls |

The site audit checks the local static publication, not search rankings, crawl frequency, assistant citations, author satisfaction or real model accuracy. The full historical unit suite and browser passes are not claimed. Live byte verification of this new release is separate and must be observed after merging.

## Suggested Turn 17

Improve an underanswered practical-AI question around small-business review replies or author checking, with direct source comparisons and a native path from the relevant topic hub. Preserve existing case evidence, protect private data, and avoid repeating another generic AI checklist.
