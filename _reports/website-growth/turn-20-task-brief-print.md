# Turn 20 independent engineering pass: print a completed task brief

Prepared October 24, 2026, Pacific/Honolulu. This is an independent usability repair from the website-growth work. The original plan's consenting-visitor study, [NK-UTILITY-01](https://github.com/nolankido/nolankido.github.io/issues/123), and the subsequent evidence-based investment decision remain pending. Synthetic checks do not establish visitor demand or complete either milestone.

## Problem and result

The Task Brief page's print stylesheet hid the entire interactive workspace, including a completed brief. Browser Print therefore omitted the visitor's assembled result. The closed blank-template disclosure also did not expose its contents for script-free printing.

Add a keyboard-accessible **Print brief** action alongside the existing copy and text-download actions. Print mode uses the existing validated, text-only preview and includes all six sections, a short explanation that no AI has run, and the page address. It removes the form, duplicate plaintext export, examples and navigation from the completed-brief printout. Text can wrap and continue across pages on a white background.

The result's existing hidden state controls the print layout. Unassembled, edited, invalidated or cleared drafts are not printed as completed briefs. With no assembled result, the article and blank template remain printable, including when scripts are disabled or the script asset fails. Returning from print preserves the working draft.

The interface says printing was requested, never that a document was printed or saved. The browser's own dialog controls the printer or PDF destination. If the print API is absent or throws, the existing plain text is selected and the visitor receives copy/download guidance. This follows the [Window.print API contract](https://developer.mozilla.org/en-US/docs/Web/API/Window/print).

## Scope and verification

Production changes are limited to the Task Brief source, its generated HTML, CSS and JavaScript. No other production file changes from parent `f3067cc36286eb4adbe7aa15024f49a414008d4d`. Existing privacy boundaries, routes, template download, publication metadata and pageview-only analytics remain intact.

Local verification completed:

- Generated output check: 222 generated files, zero drift.
- HTML5 and search validation: 194 pages each, no errors.
- Focused Task Brief unit tests: 39 passed; related Weekly Reset historical tests: 16 passed.
- Existing Chromium browser suite passed, including 19 functional checks, 15 layouts, 15 enlarged-spacing checks and four URL journeys.
- Added eight print layouts across 320, 390, 768 and 1440-pixel widths, seven draft-state guards, two unavailable-print fallbacks and two script-free print fallbacks.
- Keyboard print request, cancellation lifecycle, literal HTML-looking input, maximum field lengths, draft preservation and no new network/storage/cookie/URL effects were checked.
- Rendered and visually inspected a one-page normal brief and a two-page maximum-length A4 brief. All sections and final text were retained without clipping.
- JavaScript syntax and whitespace checks passed. Exact-hash predecessor restoration preserves the complete 714-file production snapshot and earlier historical tests without rewriting their baselines.

Hosted pull-request checks and review, merge, and deployment receipts establish the final release state. Local browser coverage is Chromium with an intercepted print dialog and rendered PDFs, not a physical printer or a cross-browser certification. Local axe was unavailable; the hosted browser workflow supplies its own accessibility dependency. No participant records or completed-study claims are included.
