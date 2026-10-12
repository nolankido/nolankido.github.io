# Reading delivery and public-link presentation

Baseline: `cb801f284c3f046044da071db6c0b7732fcc48fc` (PR 45).
Scope: nolankido.com. Preserve Nolan's approved public identity and all existing writing.

## Assessment and priorities

The site already has descriptive metadata, connected authorship, accessible task guides, working tools, a recorded case and complete publishing routes. More general articles or another biography rewrite would add little without evidence of actual reader demand. This pass improves the existing work's delivery and distribution instead.

Every generated page still requested a render-blocking stylesheet from fonts.googleapis.com before its fonts could be discovered. That extra external CSS dependency is avoidable while retaining the actual typography. Most guides and both practical-AI tools also had no explicit copy-link or native-share actions. Finally, three substantial Technology destinations reused the general identity preview rather than communicating their own purpose when shared.

The intended public-image benefit is a coherent, usable site whose shared work is recognizable as Nolan's, without stronger claims of expertise. The intended search benefit is better page experience and clearer presentation, not another assumed keyword opportunity. Social sharing controls and preview cards are distribution features, not claimed ranking factors.

GSC Wizard was checked during this pass. nolankido.com is absent from its connected properties. No query or traffic baseline, Google URL inspection, sitemap submission, or real-user Core Web Vitals reading was obtained. The access gap is not evidence of zero traffic or non-indexing. No unrelated site's metrics were used.

## Implemented changes

### Local font declarations, unchanged font files

`_scripts/font_delivery.py` replaces the existing Google Fonts CSS link with a versioned local `assets/site-fonts.css` on all 169 pages and removes the now-unneeded fonts.googleapis.com preconnection. The fonts.gstatic.com preconnection remains. The local stylesheet is exactly the reviewed 15,630-byte provider response: 38 font-face rules, the same three families, ten style/weight combinations, Unicode subsets, WOFF2 URLs and font-display:swap.

No font binaries are copied or bundled. The actual files still come from Google Fonts, and browsers still disclose technical request information to that provider. Privacy text now states that distinction accurately. This is not a claim of fully local or isolated font loading, fewer total CSS requests, or smaller font payloads.

The build validates the source hash, descriptor grammar, allowed provider host, original request and preconnections. It rejects new styles, imports, altered families or display behavior until reviewed. All original source CSS and the existing core bundle remain byte-identical. Builds make no network requests.

The captured CSS and request provenance are in `_source/font-faces.css` and `_reports/font-css-provenance.json`. This deliberately pins provider declarations instead of automatically receiving future API changes. Maintenance should check the declared font URLs and explicitly review new captures when updating fonts. The implementation targets browsers with WOFF2 support; fallback stacks remain available if fonts are blocked or fail.

### Canonical sharing on 90 article/tool pages

`_scripts/page_sharing.py` renders a compact native disclosure at the end of 88 Article pages and the two practical-AI tools. Existing Notes disclosures are enhanced in place, not duplicated. Copy page link appears after successful initialization. Share page appears only when the browser supports the requested native share action. There is no fixed or floating share rail.

The script copies only the canonical public URL. The native share payload contains only the public page title and canonical URL. Neither reads location, query strings, fragments, calculator fields, worksheet content, cookies or browser storage. It adds no analytics event, tracking parameter, server request, third-party widget, account or connected AI service. Choosing an external app through the browser has that app's own data handling.

Denied or unavailable clipboard access selects the visible public link and explains the fallback. Native sharing cancellation does not claim success; denied sharing leaves the public link available. A pending action prevents repeated overlapping calls and restores controls afterwards. Disabled or blocked JavaScript preserves the ordinary link and disclosure. Buttons have at least 44px height and wrap on narrow screens. Print styling retains a public origin link and author identity without printing controls.

### Three specific link-preview cards

The AI Time Savings Calculator, summary-checking guide and recorded website-repair case now have distinct 1200 by 630 PNG cards. Their titles and labels distinguish a free calculator, a worked guide and a recorded case. Nolan Kido and the page address remain visible. Open Graph and Twitter metadata point to the corresponding local card with descriptive alternative text.

These are title cards, not portraits or article illustrations. No Article image claim was added. All prior approved sharing cards remain byte-identical. Platform caching, supported metadata and user settings control whether a recipient actually sees a preview; metadata does not guarantee image-search inclusion or social display.

## Verification and preservation

Local checks: 404 unit/content tests passed; the committed build has 195 generated outputs and zero differences; HTML5 and search audits pass across all 169 pages. The sitemap still has the same 164 URLs, with five unchanged noindex pages and 88 Articles. No new HTML route, rewritten article, artificially refreshed article date, altered canonical URL or new feed item is introduced.

The new immutable `_tests/reading-delivery-baseline.json` was taken from the exact PR45 tree before editing. The new tests remove only explicitly marked sharing blocks and reverse only the reviewed Privacy update, then check every one of the original 169 body hashes. Original source identity, biographies, article text, five feeds, downloads, prior runtime scripts and core CSS are independently hash-pinned. Legacy snapshots are refreshed only for this reviewed rendering/privacy change; their inventories and equality assertions remain intact. Script allowlists still require exact per-page scripts, with Article schema independently deciding the sharing allowance.

Local offline browser checks pass 24 layouts, 24 enlarged-text-spacing checks, six copy actions, six stubbed native-share payloads, 15 fallback scenarios and six print checks. Desktop/mobile screenshots and all three title cards were inspected. These local tests do not establish HTTP request behavior, origin storage, font timings or accessibility scans. The added hosted browser suite covers those independently, including a deliberately delayed external-CSS reference compared with local declarations. Its timings are a controlled dependency experiment, not field performance measurements.

All 26 previous browser suites remain in the release workflow; the new reading-delivery suite is the 27th. Full pre-merge checks and a separate published-response comparison are required before calling this release live. The final pull-request receipt records their actual outcomes, the tested and published commit/tree, and the deployed response count.

## Research basis and interpretation

Google Search Central: page experience and Core Web Vitals are relevant to overall experience; good metrics do not guarantee high rankings.
https://developers.google.com/search/docs/appearance/page-experience

web.dev: font loading is part of rendering and layout behavior; font-display and discovery are separate concerns.
https://web.dev/articles/font-best-practices

Google Search Central: original usefulness, identifiable authorship and honest descriptions are preferable to indiscriminate content expansion.
https://developers.google.com/search/docs/fundamentals/creating-helpful-content

No ranking increase, measured credibility improvement, outside recognition, subscriber growth or real-user timing benefit is claimed. The next measurement step is access to the actual site's Search Console property and field-performance data, not a manufactured success story.
