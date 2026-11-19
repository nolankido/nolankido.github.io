# SEO/GEO/AEO sprint Turn 15: AI-assisted publication evidence

- **Date:** November 18, 2026 (Hawaii)
- **Property:** https://nolankido.com/
- **Sprint position:** Turn 15 of 25
- **Base checkpoint:** `3780b32238bce4af9f5246180bd67e002e83b088` (Turn 14, merged PR #386)
- **Canonical kept:** https://nolankido.com/technology/ai-website-visibility/
- **Goal:** Answer how Nolan Kido verifies an AI-assisted site improvement with a concrete and independently inspectable worked example. Separate evidence of publication from evidence of search discovery.

## Before and after

The existing case already documented five historically sourced edits, local release checks, a free monthly Google Search Console export procedure, and a separate manual AI-citation sampling method. Its main introduction did not feature the newest public, source-to-live deployment evidence. The Technology hub routed to the article, but its in-page section menu did not link a current worked example.

Turn 15 added a direct question and concise answer to the article's opening, followed by a new section at `#site-visibility-recent-release` with four evidence steps:

1. **Primary source:** YouTube's November 18 public oEmbed listing, the changed thumbnail, and the independently downloadable dated source ledger. Neither listing metadata nor artwork proves footage content.
2. **Site change:** The exact Poker hub, player profile and Reserve article links and copy visible in [merged PR #386](https://github.com/nolankido/nolankido.github.io/pull/386/files). The existing Reserve canonical remains the same.
3. **Local checks:** Offline title/image-source agreement, synthetic negative controls, and the local release counts recorded in the [Turn 14 report](seo-geo-turn14-reserve-video-listing-2026-11-18.md): 253 generated files with no drift, 225 sitemap URLs, 230 HTML pages parsed, and 16,240 internal links without issues. The article identifies what those checks cannot establish.
4. **Public response:** The five post-merge read-only byte comparisons from Turn 14 were independently repeated during this turn: Poker hub, player profile, Reserve companion, local thumbnail and public ledger still matched their committed local bytes. This is a point-in-time serving observation, not a monitor or guarantee.

The article then directly answers whether the release proves higher Google rankings or ChatGPT citations: **No**. The owner did not start a paid Search Console connector subscription after trial expiration. The existing free owner-exported CSV and fixed citation-panel methods remain the next measurement tools. Unavailable data is not counted as zero. The current YouTube cut was not verified from complete transcript audio.

The Technology hub now links the worked-example fragment directly, and the article's SEO description describes the source-to-live evidence. The article keeps its actual November 3 date, advances its substantive revision to November 18, and retains the historical case, all previously supported anchors and canonical URL. No new page, FAQ markup, search service, paid API, schedule or GitHub Action was added.

## Local verification

| Check | Observed result |
| --- | --- |
| `python _scripts/build.py` | 253 outputs built; seven generated changes |
| `python _scripts/build.py --check` | 253 checked; zero drift |
| `python _scripts/check_search.py` | Pass; 225 URLs in sitemap, 224 uniquely titled/described pages; no errors |
| `python _tests/check_html5.py` | Pass; 230 HTML pages, no failures |
| `python _scripts/check_internal_links.py` | Pass; 232 HTML pages, 16,250 internal links, zero issues |
| `python -m unittest discover -s _tests -p 'test_turn15_ai_website_release_answer.py' -v` | Three passed: direct-answer/link parity, original article identity and dates, and negative-control detection of overclaim or source drift |
| Five read-only GETs of the prior release's public artifacts | Five exact byte matches against the Turn 14 committed files; no content was edited remotely |

These are local static checks of the proposed Turn 15 site files and separate spot-checks of the earlier release. Live verification of this **new** article revision is a separate publication step and must be reported only after it is actually observed. None of these figures measures search or assistant referrals.

The optional broad local release checklist was also attempted. Its standalone builders and the focused laptop, reply, poker companion and Reserve checks passed, but historical SHA-based tests failed because this checkout has shallow Git history and cannot resolve their old pinned revisions. One older Search Console demo test also expects a November 6 article modification timestamp, although the article was already updated on November 14 before this turn. The broad run was stopped after these known historical failures; do not treat it as a passing full suite or browser review. The focused Turn 15, search, HTML5 and link checks above completed independently and passed.

## What to measure next

Without a verified export, the honest baseline for this changed page is **unknown**. At a later complete calendar-month boundary, use the already published private Search Console CSV procedure to record impressions, clicks and page/query slices. Revisit a fixed set of unbranded assistant prompts and count actual clickable citations separately. Keep property filters, dates, coverage, sample denominators and later site revisions in the comparison. This can detect changes without asserting this one release caused them.

## Suggested Turn 16

Audit one other practical AI case for an unanswered reader question or unsupported inference, then add a concrete source-bounded answer and internal link from an appropriate high-intent page. Preserve its original evidence and date trail; consider a new no-cost measurement only if verified data is actually available.
