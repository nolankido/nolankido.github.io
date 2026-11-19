# SEO/GEO/AEO Sprint Turn 21: A source-to-claim check for AI search advice

- **Date:** November 18, 2026 (Hawaii)
- **Property:** https://nolankido.com/
- **Sprint:** Turn 21 of 25
- **Base:** merged Turn 20 commit `da815b86a244c885fa29e25b5e7f7948ecbc7c58` (PR #392)
- **Canonical retained:** https://nolankido.com/technology/check-ai-answers/
- **New native answer:** https://nolankido.com/technology/check-ai-answers/#review-search-advice
- **Reader intent:** How can I check an AI answer, especially a claim about what it takes to be cited in Google AI Overviews? When can I repeat a verified statement without overclaiming?

## Prior page and specific gap

The answer-review guide already gave a direct answer, six distinct checks for facts, math, summaries, writing, code and advice, a NIST citation exercise, three source-pinned project examples, a completed fictional evidence record, and private-use checklist downloads. Its HTML, Article markup and canonical route were established. Adding another generic guide, FAQ schema or an AI-only indexing file would not fill a documented reader need.

This turn adds **one inspectable source-to-claim receipt** inside the existing facts/citations section, linked from the opening and three natural neighboring entry points. The receipt demonstrates how to split a plausible but unsupported AI-search claim into individual findings, with a clear decision about which narrower statement may be repeated. It is text-first, accessible without JavaScript and reuses existing typography, print and page styles. It does not add another canonical article, structured-data type, data collection field or paid tool.

## Primary source check and exact boundaries

The deliberately flawed claim is **fictional teaching copy**, not a captured chatbot answer or a vendor quote:

> Google requires special GEO schema to appear in AI Overviews, and adding it guarantees your site will be cited.

The source check used these public Google Search Central pages as of November 18, 2026:

1. [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features) states eligibility for supporting links in AI Overviews and AI Mode follows ordinary Google indexing and snippet rules, with no additional technical or special schema requirements. Google also states technical eligibility does not guarantee indexing or being served. Ordinary SEO fundamentals such as crawl access, visible text, internally linked navigation and correct structured data remain useful.
2. [Optimizing your website for generative AI features](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) describes Google Search's approach to AEO and GEO language while emphasizing people-first, useful, distinctive content and ordinary SEO fundamentals. The guide does not establish a mandatory GEO markup type, a guaranteed citation outcome, or how unrelated AI assistants choose their sources.

| Subclaim or proposed inference | Site's evidence classification | Scope |
| --- | --- | --- |
| Special GEO schema is mandatory for Google AI Overviews | **Contradicted** by Google's published technical requirements | Google AI Overviews and AI Mode only |
| Indexed, snippet-eligible pages can be considered for supporting links | **Supported with conditions** | Eligibility, not inclusion in a given answer |
| Adding markup guarantees a cited answer | **Contradicted** by explicit non-guarantee | No citation warranty can be derived from these sources |
| NolanKido.com has or will have citations for a specific query | **Unresolved** | Requires separate dated observations; not established by the technical build |

The new answer explains the resulting editorial decision: repeat only source-backed requirements with citation and check date; reject the supposed requirement and guarantee, and do not claim observed AI citations. It links back to the existing frozen 25-question audit panel, explicitly identifying that panel as a method rather than a completed observation. External source updates can change a finding, so the example is dated and asks for rechecking before future reuse.

## Internal discovery and preservation

- The source page now links from its early answer to `#review-search-advice`.
- The Technology hub, Resources and the existing AI website visibility case link to the same canonical fragment with descriptive anchor text.
- The manifest's search description now names AI facts, citations, math, code and the independently sourced example, while retaining the established title and original October 12 publication date.
- The page's previously reviewed six methods, their examples, NIST passage reference, private downloads, print contract, Article identity and all earlier heading anchors remain.
- No `FAQPage` markup, duplicate canonical, special GEO schema, AI text file, runtime upload, GitHub Actions, cron, scheduled job, paid search connection or authenticated private evidence was introduced.

## Verification and outcome limit

The focused Turn 21 test checks the bounded answer and its source links, the supported/contradicted/unresolved distinctions, the internal navigation and preserved anchors, canonical Article identity, sitemap revision date, and negative mutations that try to introduce a schema requirement, guaranteed citation or unobserved search win. It uses only local source and generated output.

**Recorded local checks, after the final source revision:**

| Check | Observed result |
| --- | --- |
| `python _scripts/build.py` | 253 public files generated; original final source change refreshed the Technology hub |
| `python _scripts/build.py --check` | 253 files checked, no drift |
| `python _scripts/check_search.py` | Passed, 225 sitemap URLs, 224 pages and zero metadata errors |
| `python _tests/check_html5.py` | Passed, 230 pages and no failures |
| `python _scripts/check_internal_links.py` | Passed, 232 HTML pages, 16,299 internal links, no issues |
| `test_turn21_ai_search_source_check.py` | 4 of 4 passed, including negative claim mutations and canonical/fragment checks |
| `test_turn20_identity_answer.py` | 4 of 4 passed |
| `test_turn15_ai_website_release_answer.py` | 3 of 3 passed |
| `test_turn19_frozen_answer_panel.py` | 7 of 7 passed; fixed 25-question kit preserved |
| `git diff --check` | No whitespace errors |

The generated Technology hub initially lacked a new link placed inside a legacy section that its content generator omits. A focused test caught it. The final revision moved the link into the active Technology navigation, rebuilt the hub and passed the four focused tests and link audit. This is a useful build-output discovery, not evidence of search crawling.

Historical snapshot suites can fail against later legitimate content and feed revisions, so they are not evidence of a current clean full suite. The older `test_answer_review.py` run in this turn reported 3 failures involving the historic `404.html` predecessor hash and an old `feed.xml` snapshot, which are outside the new bounded search-advice example. That suite did not pass. The full historical suite and browser layout suite were not run; no full-suite or browser success is claimed.

The new content improves source transparency and a natural answer pathway. It **does not establish** a ranking increase, search impressions, click growth, actual AI Overview or chatbot citations, client outcomes, or universal safety of AI advice. The paid Search Console connector remained unavailable and was not upgraded. The owner's unchanged frozen panel and free private CSV procedure can support later measurement, but neither was executed here as an observed SERP or AI citation trial.

## Suggested Turn 22

Strengthen a separate, nonbranded poker question's direct answer and source boundaries, especially tournament hand review and solver limits, while preserving the free citation-measurement kit and the site's primary-source standards.
