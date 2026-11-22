# PBG-05: Read-only Amazon click-path validation and attribution boundaries

**Sprint:** Poker Book Growth, Turn 05 of 25  
**Review date:** November 22, 2026 (Pacific/Honolulu)  
**Site:** https://nolankido.com/  
**Primary book:** *How to Play No-Limit Texas Hold'em*  
**Author-provided Kindle ASIN:** `B0HSB98324`  
**Result:** Five first-party Amazon-link contracts are present across three public book pages. No actual Umami event receipts, Amazon product-detail records, attributed orders, or KDP sales reports were obtained.

## Objective and evidence quality

Verify that a reader following an existing native Amazon link reaches the intended **author-provided URL** and that Umami's event properties are correctly encoded without relying on the tracker to make the link clickable.

This turn uses **read-only public retrieval** and **authenticated repository source inspection**. It does not simulate a live visitor click, send an analytics event, purchase a book, log into Amazon KDP or imply ownership of private dashboard data.

The public site rendered all three first-party routes and exposed all five Amazon destination links. Public requests for the three Amazon product URLs reached the same final URLs but returned the generic Amazon **Continue shopping** interstitial, not a readable product detail page. As a result, current purchase availability, matching retailer byline/title, prices, format selection, ratings, covers and release dates remain **unverified**. The interstitial is neither proof of successful purchase availability nor proof of a 404.

## Observed link-path matrix

| First-party origin | Amazon ASIN | Event name | Fixed event `source` | Status |
| --- | --- | --- | --- | --- |
| `/books/` | `B0HSB98324` | `poker-book-kindle-amazon-click` | `books-catalog` | Exact author-supplied href found |
| `/books/how-to-play-no-limit-texas-holdem/` | `B0HSB98324` | `poker-book-kindle-amazon-click` | `book-page-hero` | Exact author-supplied href found |
| `/books/` | `B0HRQNCP7Y` | `one-workflow-kindle-amazon-click` | `books-catalog` | Exact author-supplied href found |
| `/books/one-workflow-at-a-time/` | `B0HRQNCP7Y` | `one-workflow-kindle-amazon-click` | `book-page-hero` | Exact author-supplied href found |
| `/books/` | `B0HSF8K76R` | `ai-works-human-decides-kindle-amazon-click` | `books-catalog` | Exact author-supplied href found |

The three original author-provided destinations are preserved without shortening, redirecting or adding invented Amazon Attribution or affiliate parameters. The Amazon links remain ordinary HTML `<a href="...">` elements. They have `rel="noopener noreferrer"` and no JavaScript `onclick` gate, so the destination is available as a normal link even if analytics is blocked or JavaScript is disabled.

All three first-party pages still load one copy of the existing privacy-configured Umami script, with `data-do-not-track="true"`, `data-exclude-search="true"`, and `data-exclude-hash="true"`. The click attributes are `data-umami-event` and `data-umami-event-source`, which follows the official Umami pattern for custom event data. This establishes a correctly configured **opportunity to record clicks**, not proof that Umami actually ingested one.

Umami documentation:
- [Track events](https://docs.umami.is/docs/track-events)
- [Event data](https://docs.umami.is/docs/event-data)
- [Track outbound links](https://v2.umami.is/docs/track-outbound-links)
- [Tracker configuration](https://docs.umami.is/docs/tracker-configuration)

## New reproducible quality gate

Added `_scripts/poker_book_click_path_audit.py`, a standard-library-only, offline, read-only command.

```powershell
py -3 _scripts/poker_book_click_path_audit.py
```

It validates:

1. The site edition ledger contains the three precisely author-provided ASINs and the corresponding direct Amazon URLs.
2. Exact five native anchor destinations and their match to the correct book, originating page and click-event name.
3. One fixed `source` attribute for each event, in agreement with the previously defined private-scorecard event schema.
4. No duplicate or unknown tagged Amazon link on the inspected three-page cohort.
5. Exact first-party book-page source/output byte equality.
6. One accepted Umami tracker with the privacy flags on each page, no extra `umami.track()` call and no JavaScript click intercept.
7. The public privacy notice explicitly discloses the book-link events and clarifies that a click is not a purchase.

The tool emits machine-readable JSON and returns an error status if a contract is broken. It intentionally returns `null` for Umami events received, Amazon product-details verification, tag availability, and attributed KDP orders. It does not authenticate into accounts, click the live destination or write private files.

Added `_tests/test_pbg05_book_click_path_audit.py` with 12 isolated offline tests, covering the valid contract, provenance registry, direct-link fallback, explicit unmeasured outcomes, wrong URLs, source/public mismatch, tampered event name or source, unexpected Amazon links, forged ASIN, removed privacy disclosure, CLI output and manual runner registration. Registered both the audit command and its tests in `_scripts/local_release_checks.py`. No GitHub Actions, scheduled checks or paid integrations were introduced.

### Verification actually performed

A fresh authenticated repository readback verified the three first-party source/public HTML pairs and all five anchors and event/source properties. A second independent, read-only source check passed **54 static assertions**, confirming exact link count, script tags and privacy flags, the author-supplied ledger, absent fabricated retail claims, event metadata, and the offline tool/test registrations. This is not the same as executing the Python test module.

The [machine-readable observation record](pbg-05-live-click-path-observation-2026-11-22.json) keeps this evidence separate from uncollected traffic and sales metrics.

**Not executed:** the complete Python tests, JavaScript-disabled browser navigation, network event receipt test, Amazon product detail inspection, and KDP or Amazon Ads dashboard review. Those are separate gates. Never report actual clicks, sales lift or conversion improvement from this review.

## How to collect and reconcile actual conversion evidence

This site already has the offline `_scripts/poker_book_growth_scorecard.py` built in Turn 02. It accepts a strictly bounded, **private** Umami aggregate document and defaults unobserved counts to `null`, not zero. Use that rather than committing raw visitor logs.

### Stage A: website actions (Umami)

1. Log into the owner's Umami account and select the actual `nolankido.com` property. No authenticated Umami tab or directly connected Umami analytics provider was accessible in this turn.
2. Select an explicit, settled date range. The new links were incorporated on November 22, so any November series includes a pre-link period and should be labelled as partial. Do not compare it naively with a complete December month.
3. In **Events**, check `poker-book-kindle-amazon-click`. In **Properties**, filter `source=book-page-hero` and `source=books-catalog` separately, then compare events with **pageviews for the same path and range**.
4. Confirm that real event data exist before marking a metric `observed`. A real `0` needs a verified complete report, not the absence of a row, a blocked tracker, a source permission failure or a guessed number.
5. Do not simulate clicks against production to create a green event test. If a controlled human click is later performed, explicitly label and exclude that test from organic outcome data.

### Stage B: retail totals (KDP)

KDP's **Orders** and **Royalties** reports can show units and royalties by title or ASIN, subject to report timing and filters. These are **total KDP observations**, not necessarily attributed to nolankido.com or a particular website link. Use the exact product ASIN and a comparable reporting interval; retain raw data privately and separate free units from paid units and KENP read.

- [KDP Reports guidance](https://kdp.amazon.com/en_US/help/topic/GVTTXHKHVPAPBEDQ)
- [KDP Sales and Royalties Report](https://kdp.amazon.com/en_US/help/topic/G201488550)

### Stage C: optional actual Amazon-side attribution

Amazon Ads officially describes **Amazon Attribution** as a free measurement solution available to eligible KDP authors in supported marketplaces, though the owner's specific account, campaign options and tags were **not** accessible or verified in this turn. Its advertising console can provide an Amazon-generated attribution link and reports. Do **not** invent a URL or tag from an ASIN.

If the owner's eligible Amazon Ads account exposes it, create separate first-party website attribution placements or campaigns for the book-page and catalog sources, using the real Amazon-generated links only after confirming they target the right book. Then explicitly review and authorize replacing the existing public author-supplied direct URLs. Preserve the existing Umami event names and source fields if changes are made, and update the link audit, provenance ledger, public description and tests to match.

Attribution tagging **does not** make unattributed historical KDP orders attributable, does not prove that every click was received, and does not give a causal lift estimate without suitable controls.

- [Amazon Attribution eligibility and pricing](https://advertising.amazon.com/solutions/products/amazon-attribution)
- [Original KDP attribution announcement](https://advertising.amazon.com/en-gb/resources/whats-new/amazon-attribution-kdp-authors)

## Sprint position and next priority

**Turn 05 advances link contract validation, not revenue measurement.** The existing Turn 04 acquisition cohort remains **9 of 11** selected poker education pages directly linking to the first-party book page, with two broad resource hubs intentionally unchanged.

No additional links, Google indexing claims, offer schema, retailer reviews, product-cover images, Kindle Unlimited claims, KDP sales data, redirects, advertising costs or new analytics providers were added. All three book destinations remain author-supplied rather than independently authenticated retailer metadata.

**Next PBG-06:** map actual beginner search intents and content overlaps against existing poker pages, prioritize useful improvements to the guide, free practice and book comparison, and use authenticated Search Console query/page evidence if available. Do not mistake search suggestions or third-party keyword estimates for the user's own actual demand.
