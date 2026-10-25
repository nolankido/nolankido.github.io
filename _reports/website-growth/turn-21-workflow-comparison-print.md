# Turn 21 independent engineering pass: printable workflow comparisons

Prepared October 25, 2026, Pacific/Honolulu. This follows the Task Brief print repair with a bounded improvement to the existing AI Time Savings calculator. The consenting-visitor study [NK-UTILITY-01](https://github.com/nolankido/nolankido.github.io/issues/123) and the plan's subsequent investment decision remain open. Synthetic checks do not establish visitor demand or participant outcomes.

## Reproduced problem

In Chromium 140 print media, a normal completed comparison contained 25 lines and 1,328 characters in a textarea with a 278-pixel client height and 739-pixel scroll height. The print rule set `height:auto`, which still left the full report inside a scrolling control. Six editable inputs also remained in the printed output, the root canvas retained its tinted background, and the closed blank worksheet stayed hidden even with scripts disabled.

## Change and resulting behavior

Add **Print comparison** beside the existing copy and text-download actions. A print-only text block receives the exact existing report string after a successful calculation. It includes all six inputs, estimate/observation basis, fictional-example provenance when present, totals, thresholds, quality conditions, decision guidance, sensitivity example and final model limitations. Arithmetic and export wording are unchanged.

Completed-result print mode shows that whole record on a white page, with wrapping text and normal pagination. It hides the editing controls and duplicated article content. The existing invalidation function also clears the print copy, so numeric, basis or quality changes, invalid calculations, confirmed clearing, example replacement and navigation cannot leave an outdated printable comparison.

When there is no valid result, browser Print retains the static article and exposes the complete blank worksheet without changing its screen disclosure state. Script-disabled and blocked-script cases use that same fallback. Print cancellation preserves the current entries. If the print API is absent or throws, the page selects the existing comparison text and explains the copy/download alternatives. Status messages report a print request, never confirmed printing or saving.

## Scope and evidence

Five production paths change from parent `83b76d0b5670c9c022b5e7cef72d0f0a47089c98`: calculator source, calculator JavaScript, shared evidence stylesheet, calculator generated HTML and the verification article's generated stylesheet cache token. The verification article's content remains byte-identical after normalizing that token. Existing baseline records are retained, with exact-hash restoration of the complete 714-file production predecessor.

Local verification completed:

- 222 generated files checked with zero drift; HTML5 and search validation passed across 194 pages.
- 32 focused unit tests passed across time utilities, workflow evidence and the preceding Task Brief print history.
- Browser checks passed: 18 functional cases, 16 existing layouts, eight enlarged-spacing layouts, seven downloads, six entry journeys and 12 evidence-link keyboard journeys.
- Added 16 print layouts across four viewport widths, four exact report comparisons, 11 draft-state guards, two print-API fallbacks and two script-free worksheet fallbacks.
- Keyboard print activation and cancellation lifecycle preserve the draft. Print actions add no network requests, storage, cookies or URL changes.
- Eight axe scans reported no automated violations. Some color-contrast checks were marked incomplete by axe, so this is not a manual accessibility certification.
- Three A4 PDFs were rendered and visually inspected: a one-page normal comparison, one-page maximum-value comparison with fictional-origin text, and five-page script-disabled article with the complete blank worksheet. Final model and quality limitations are retained.
- JavaScript syntax and whitespace checks passed. The existing numeric-output screenshot comparison also passed unchanged.

Final-head hosted checks, automated review, merge and live deployment receipts are recorded in the pull request. Local browser/PDF checks cover Chromium and a simulated print dialog, not physical printers or all browser engines. No participant records or completed-study claims are included.
