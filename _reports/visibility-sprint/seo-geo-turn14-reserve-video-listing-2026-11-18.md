# SEO/GEO/AEO Sprint Turn 14: current Reserve video listing and answer path

- **Date:** November 18, 2026 (Hawaii)
- **Property:** https://nolankido.com/
- **Sprint position:** Turn 14 of 25
- **Base repository checkpoint:** `837ace4`, merged Turn 13
- **Canonical companion retained:** https://nolankido.com/poker/episodes/reserve-day-1/
- **Publication scope:** Replace stale public video title and local thumbnail, strengthen the A-K answer pathway, and give future maintainers an offline source-agreement check plus an optional manual public check. No new article route, publication date, sitemap, background service or paid API.

## What changed in the public evidence

The official [YouTube oEmbed response](https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=edNSD5BjIV8&format=json) on November 18, 2026, returned the NolanPoker title **My Ace-King Reshove in a 3-Way All-In | WSOP Circuit**. The previously verified November 13 title was **7 BB Near the Money... Then a Massive A-K Pot | WSOP Circuit**. Both use the same public video ID `edNSD5BjIV8`; there was no evidence of a URL replacement.

The [public 480 × 360 YouTube thumbnail](https://i.ytimg.com/vi/edNSD5BjIV8/hqdefault.jpg) also changed. Its November 18 SHA-256 was `01cb25ef4f2efb238a5180faa478a2275b0e2ded9348c051819d20170c45eb5e`, compared with the earlier recorded `83ddd68755529a9fae4134cd614fe5ca1c6728fe13bb555cad2657a138082b6f`. The new visible artwork depicts an A-K illustration under the words “3-WAY ALL-IN.” An illustration and title do not independently establish cards dealt, stack depths, full boards, the spoken cut or the strategic quality of a decision.

The current YouTube watch page advertised English auto-generated caption tracks, but both publicly available track endpoints returned zero transcript bytes during this review. Therefore **no full current-audio or in-video-frame comparison was possible**. Archived v8 narrative details remain explicitly labeled as such in the companion; unverified old chapter timestamps, missing board cards and solver verdicts remain absent.

## Implementation

1. Updated the public title and stored local thumbnail in the Poker video gallery and source inventory, without changing the video ID or using a remote hotlinked image in the site.
2. Updated the standalone Nolan Kido player profile's video list and linked directly to the Reserve companion's approximate 10-BB refund explanation.
3. Added a fourth native Poker hub hand-study arrival to the Reserve main/side-pot question and the existing side-pot lab, without representing a retrospective outcome as a solver conclusion.
4. Added a concise present-day listing/status note near the top of the Reserve companion, preserving its original publication date and canonical URL.
5. Updated the public JSON ledger to version 2. It retains both the former and current public titles with their separate dates, the current thumbnail SHA-256, and the distinction between public packaging and unverified footage.
6. Added `_scripts/check_reserve_video_listing.py`. Offline by default, it requires matching title, checked-on date, video identity, public source text, image SHA-256 and evidence disclaimers. With `--live` it checks public YouTube oEmbed and thumbnail over two read-only GET requests; no scheduled run or paid service was introduced. Synthetic negative controls test title drift, channel impersonation, changed artwork and a falsely asserted current-cut verification.

## Local verification observed

| Check | Result |
| --- | --- |
| Main build and `--check` | 253 generated outputs, zero drift after regeneration |
| Player profile and Reserve standalone builders | Both `--check` exact |
| Reserve listing offline check and optional manual `--live` check | Both passed; live title, channel and thumbnail SHA-256 matched |
| Turn 14 listing contracts | 3 passed, including synthetic negative controls |
| Turn 13 companion contracts | 7 passed; evidence limits retained |
| Gallery, thumbnail and first-video chooser tests | 3, 4 and 3 passed respectively after review of current revision |
| On-site Find/search audit | 225 sitemap URLs, no metadata errors |
| Internal-link audit | 232 HTML pages, 16,240 internal links, zero issues |
| HTML5 parser | 230 HTML pages, zero failures |
| Full-site baseline and section search | 8 and 12 tests passed respectively |

These are specific local checks, not proof that the entire historical test suite, mobile browsers or search-engine indexing passed. The static page's existing publication date was preserved and the local thumbnail is now included in the read-only public-byte target inventory.

## Verification boundaries

The local builds are deterministic and source-backed. The read-only live check may establish current public title, channel and artwork at the time it is run, but not transcript accuracy, YouTube editorial history or lasting title stability. Future changed metadata should be detected and intentionally reviewed; it must never be silently promoted into a new hand fact.

The connected GSC Wizard provider refused analysis because its trial ended and has no active subscription. No paid subscription was started. Consequently this turn uses a directly observed public title/thumb mismatch, not a fabricated impression, position, CTR or AI-citation forecast. An improved internal entry point and more accurate video packaging do not by themselves prove search-engine or generative-answer gains.

## Suggested Turn 15

Improve one AI-related, first-party canonical page's direct answers and verifiable evidence for Nolan Kido's main technology identity, using existing no-cost data and already published cases. Avoid duplicating another generic SEO checklist, and keep measurable outcomes distinct from expected search benefits.
