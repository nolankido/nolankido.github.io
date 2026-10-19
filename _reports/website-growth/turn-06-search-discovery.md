# Website growth, Turn 06: Search discovery guard
October 17, 2026. Public release record; no private search-query or visitor records included.

## Evidence
Seven priority pages returned HTTP 200, self-referencing canonicals and indexable content in the live audit. Search Console URL Inspection reported five indexed priority pages, Hand Rankings discovered but not indexed, and Poker School unknown to Google. A later tracker inspection reported both latter URLs unknown; external indexing states can change. Search Console's submitted sitemap has no warnings or errors. Bing Webmaster API access is not configured. Neither an indexed status nor schema validity proves traffic or citations.

## Improvement
The new `_tests/check_discovery.py` validates all seven priority generated pages and the two Poker homepage links, canonical sitemap entries, metadata, structured page URL, and lack of noindex or blanket robots exclusion. `_tests/test_discovery_gate.py` supplies positive and negative test cases. The existing CI unit-test discovery runs the guard tests without altering the frozen site-check workflow. It uses no network access or visitor tracking, and makes no changes to public pages or URLs.

## Further actions
Review Google Search Console's URL Inspection of Hand Rankings and School and request indexing at most once when appropriate; it does not guarantee indexing. Track these alongside the five indexed pages. Set up Bing Webmaster Tools separately. Prefer improving distinctive, original content and actual links over duplicate pages, invented schema images, bot-focused keyword text, or special AI markup. Complete Turn 07 by improving the reader-facing answer-verification guide.

This checks generated release files, not external crawler delivery, index inclusion, Search rankings, AI answers or conversion.

## October 18 recovery: consolidation of parallel Turn 06 work

PR #115 and PR #116 started from the same production commit and address the same seven-page discovery gate. This branch (#116) is the designated consolidation candidate because it adds only files under `_tests` and this public report. It does not add a new `_scripts` source file, modify CI execution order, or change any deployed bytes. The earlier #116 guard accidentally contained repeated blocks and an unterminated regular expression; it has been replaced rather than patched piecemeal.

The rewritten guard retains the useful coverage from both branches: a currently active sitemap declaration, blanket-robots rejection, one self-canonical entry per priority page with a parseable revision date, plausible HTML title/description, one H1, canonical/Open Graph and structured-data URLs, case-insensitive noindex/none detection without treating image-preview settings as exclusion, and actual Poker `<a>` links rather than prefetch-only hints. The initial 17 positive/negative tests cover these invariants. The check is wired into the existing unit discovery by `test_discovery_gate.py`, without creating a new production asset. These tests must pass on the actual final commit before merge.

The recovery does **not** authorize ignoring old golden tests, rewriting recorded baseline hashes, inferring crawlability from third-party indexing, or claiming the page was released before postmerge verification. All branch results must be rechecked after any future main-branch changes.

## October 18 follow-up: robots group semantics and lastmod syntax

The original #116 guard merged as `c259a83dbdb83b334db68e427919d85ef17decc2`. Review of the later combined About/Bio candidate found two non-release-blocking but real false results in the guard. The follow-up distinguishes wildcard `User-agent: *` crawl blocks from named-bot-only exclusions and enforces the `YYYY-MM-DD` sitemap lastmod syntax rather than accepting basic or week dates. The expanded guard has **20 independent positive and negative tests**, including examples that reject a shared wildcard block, permit a named-crawler-only block, and reject two non-W3C date strings. The guard and tests remain under `_tests`; no production page, crawler rule, old baseline, or external indexing state is altered.
