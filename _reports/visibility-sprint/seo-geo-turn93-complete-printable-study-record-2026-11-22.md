# SEO/GEO Turn 93: repair clipped print output in the private poker study record

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Main SHA at start:** `97e97c311360238c0c0ff5f5a6e0694c2524349a`  
**Existing public resource:** `/downloads/poker-pot-odds-sensitivity-lab.html`  
**Existing indexed explanation:** `/poker/pot-odds-workshop/` (unchanged)

## Verified real problem

Turn 92's public read-only study textarea includes three fixed fictional poker models, all four selected assumptions, chip EV results and the final warning that no opponent or payout evidence is known. A fresh November 22 public read confirmed the Turn 92 `#study-record-panel` was deployed.

Direct local Chromium inspection of the exact Turn 92 HTML showed that the read-only `textarea` had **22 explicit lines**, and at a 390px viewport its wrapped content measured **1,223px** of scroll height versus only **391px** of visible form-control height. Emulating print did not change those dimensions. A generated Chromium A4 PDF extracted with PyMuPDF included the study-record heading and beginning but **omitted the later `3. PURE BLUFF` record and final `UNVERIFIED` evidence warning**. That makes print and print-to-PDF unreliable even though native on-screen copying works.

## Implemented fix

1. Preserve the existing on-screen labelled, read-only `#study-record` textarea and existing selection button, four sliders, four boundary presets and three live results.
2. Add one `#study-print` non-interactive `<pre>` immediately after the textarea. Its static contents are initially **byte-for-byte equal** to the textarea's text, so it is also correct without JavaScript. The element is hidden on screen and marked `aria-hidden=true`, avoiding duplicate screen-reader reading.
3. Whenever the original local `render()` recalculates the current controls, assign `el('study-print').textContent = el('study-record').value`. This preserves the exact current input assumptions and natural-line spacing using text-only DOM operations, never untrusted HTML.
4. Under print CSS only, hide the finite-height textarea, show the full `<pre>`, wrap at paper width, and permit `#study-record-panel` to span sheets via `break-inside:auto`.
5. Keep the original offline CSP, noindex, zero-request behavior, empty storage/clipboard/network attack surface, canonical identity, workbook links, 301 Finder entries and sitemap unchanged.
6. Add `_tests/test_turn93_full_print_record.py` with **11 new checks**, register it in the manual local release runner and extend `_tests/pot_odds_sensitivity_browser.py` with screen/print/full-note parity and no-script assertions. Add documentation to `AGENTS.md`.

## Executed verification

Authenticated GitHub source/public commits both returned the **same blob SHA**, `d08b7b868a351a41bcd3ab603290e149fd6b4277`, matching the tested local candidate file.

The **eight standalone Turn 93 regression tests passed**, and a repeat of all **eight existing Turn 92 standalone tests passed** on the revised exact HTML in a three-file fixture. They cover source/output parity, full printable default note contents, exact chip mathematics, no-JavaScript static parity, safe text-only JS wiring, no added submissions or network calls, and negative mutations that remove the print mirror/print CSS or drop the final evidence warning. The remaining **three integrated Turn 93 checks were not run** without a complete checked-out website.

A fresh local Chromium/Playwright print check used the exact candidate HTML at **320, 390, 768 and 1280 px**. At each width it checked current record-to-print parity after selecting the river, raise and bluff boundary presets, reversing an equity interval, and selecting the full record. Generated A4 PDFs were independently text-extracted with PyMuPDF. All four printed output versions contained the **full** `3. PURE BLUFF` section, current 37.5% fold-rate result, correctly sorted reversed range, the `UNVERIFIED` warning, and the final privacy line. No horizontal overflow, external requests or JavaScript errors were observed. JavaScript-disabled static printing also showed the complete record across pages. The previous revision's omission was reproduced as a negative control.

The repaired multi-page output was **visually inspected** on the last two printed pages: the study note continued cleanly across pages 3 and 4 without overlaid text, and the evidence warning and subsequent lesson remained readable.

**These are executed local and source-level checks, not a complete website release pass.**

## Remaining release checks

The complete repository, deterministic generator, broader HTML5/link audit, site-wide browser suite, first-party search performance and exact public-source byte parity have **not** been verified from this runtime. Do not claim higher search rankings, fewer user errors or confirmed deployment until independently observed.

From an owner-controlled full checkout:

```powershell
py -3 -m unittest discover -s _tests -p test_turn92_private_study_record.py -v
py -3 -m unittest discover -s _tests -p test_turn93_full_print_record.py -v
py -3 _tests/pot_odds_sensitivity_browser.py
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope all --only /downloads/poker-pot-odds-sensitivity-lab.html --only /poker/pot-odds-workshop/ --attempts 8 --interval 15 --workers 1
```

## Next priority

Verify the new printable note on the public deployment and run the full site checks. Then prioritize a new, useful reader task based on actual learning gaps instead of repeatedly changing the same three fictional slider models.
