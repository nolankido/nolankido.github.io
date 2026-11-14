# Website improvement: make the published AI citation audit findable

Date: November 14, 2026
Canonical article: https://nolankido.com/technology/ai-website-visibility/
Public site search: https://nolankido.com/find/

## Issue

The article now contains a concrete, downloadable manual AI-answer citation measurement method and offline validator, but its site-search card still used the older generic website-change description. The local Find JavaScript only searches titles, summaries, subject labels, a small approved acronym list, URL words and visible major headings. The new citation guide is under h3/h4 headings and was not discoverable for common phrases like "citation audit" or "ChatGPT citation" from the card. This is a local on-site search issue, not evidence of how Google or ChatGPT ranks the website.

## Change

Update the existing article's author-reviewed summary to:

> Follow Nolan Kido's documented AI website changes and learn to audit Search Console clicks, ChatGPT citations, and AI-answer links with a free offline checker.

Use the same summary in:
- `_source/pages.json`, the canonical published manifest
- `technology/ai-website-visibility/index.html` HTML meta/OG/Twitter description and Article JSON-LD
- `find/index.html` public Find card
- `technology/feed.xml` and `writing.xml` (same existing item identities and original publication date)

Keep the article's headline, actual teaching content, tools and downloads unchanged. The summary states what the guide explains, not that Nolan Kido has received increased citations or traffic. Preserve `2026-11-03` as the original article publication date and `2026-11-14` as the modification and sitemap date. No artificial freshness date, extra tracking, or new page is added.

## Query check

Using the local Find scoring rules, the previous description had no matching terms for "citation audit", "ChatGPT citation" or "AI answer links" on this article's card. The reviewed description returns a positive match for all three while retaining positive results for "Search Console", "SEO" and "website improvements". Nonrelevant queries such as "private client revenue" remain unmatched.

## Tests and preservation

Added `_tests/test_ai_citation_find_discovery.py` with five focused checks:
1. Manifest, date, accuracy and limitation language
2. Published HTML meta/OG/Twitter/JSON-LD summary consistency and canonical path
3. Find card projection from the revised manifest
4. The **real** offline Find scoring module for six relevant and two irrelevant queries, not a second independent keyword implementation
5. Both feed descriptions and unchanged sitemap/publication dates

Registered the test in `_scripts/local_release_checks.py`. The test makes no network request, queries no private account and creates no scheduled jobs.

Validation in this workspace: reviewed the exact original and new descriptions and the Find scoring logic, verified the new query outcomes through a local Node fixture, and checked the regenerated text placements and RSS records for parity. A complete checkout was not available for the full site generator and all release groups; do not claim they passed without running them. A GitHub merge is also distinct from a verified live public-domain response.

## Outcomes not established

This corrects a local search and reader-discovery defect. It does not establish Google rankings, AI assistant citations, click growth, or increased reader satisfaction. Google's Search Central explains that search snippets may be selected from page content and are not guaranteed to use the metadata text: https://developers.google.com/search/docs/appearance/snippet
