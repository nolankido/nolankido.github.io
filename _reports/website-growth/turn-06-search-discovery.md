# Website growth Turn 06 — discovery and answer-engine release checks

October 17, 2026. This **public** repository report deliberately excludes private Search Console query rows, indexing inspection results, analytics, referrers, and visitor information.

## Implementation
The existing build/HTML job now runs `python _scripts/check_discovery.py` before full unit/browser tests. This network-free command checks seven existing priority pages, including provisional Poker School, for their canonical URL, valid metadata, visible H1, structured-data page URL, sitemap membership, lastmod date, noindex status, and Open Graph URL. It also requires a working sitemap reference in robots.txt, no blanket root disallow, and native Poker homepage links to Hand Rankings and Poker School. Seven new unit tests include six deliberate regressions.

This is **a release guard, not an indexing test**. The seven pages existed beforehand. No new public HTML page, crawler rule, personal claim, artificial FAQ, special AI text file, or tracking event is added. All live site output should remain byte-identical after this change.

## Follow-up owned outside GitHub
Check the existing sitemap in Google Search Console; use URL Inspection for individually unindexed pages and optionally request crawling once in the Search Console user interface. An indexing request and sitemap submission are not guarantees. Investigate true crawl blocks with edge logs if needed. Connect Bing Webmaster Tools for independent Bing/AI Performance evidence before reporting Bing results. Use real source material and audience value, not artificial long-tail pages or keyword stuffing. Keep a separate private index tracker for the priority URLs.

Do not treat automated schema warning about Article.image as a mandatory requirement for Google. Add visible, relevant, original imagery on a future editorial turn if warranted. Do not add fake expertise or generative-AI citation guarantees.

## Run
```
python _scripts/check_discovery.py
python -m unittest discover -s _tests -p test_discovery_gate.py -v
python _scripts/build.py --check
```

Outcome is bounded to preventing accidental **future** search-discovery regressions. It does not establish visitor growth, rankings, indexing, or AI citations.
