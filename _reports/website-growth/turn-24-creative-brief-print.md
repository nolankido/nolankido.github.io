# Turn 24: print the complete blank Creative Work brief

Prepared October 25, 2026 (Pacific/Honolulu). Follows the released answer-checking print repair. The separate consenting visitor study in issue #123 remains open, with no observed participants or traffic finding.

## Reproduced gap

The Creative Work page includes a complete, privately reusable planning sheet inside a native `<details>` element. On screen, the folded preview keeps the page short. In Chromium print media, the closed details contents were omitted. A visitor printing the page without first expanding the disclosure received no blank worksheet.

The source is not a portfolio, AI-generated creative work, a transcript or evidence of a published vlog. This repair preserves that distinction.

## Narrow change

- In the Creative section only, print the entire blank brief even when the details preview is folded on screen.
- Retain the native summary as a print heading without a disclosure triangle.
- Allow long prompt lines to wrap and paginate without clipping, with an ink-friendly white background.
- Hide the page's download action and screen-only print hint on paper.
- Add one visible sentence explaining how to use browser Print / Save as PDF. The blank file remains an exact match to the on-page text and receives no visitor entries.
- Retain the previous unaltered screen disclosure state after printing, both with and without JavaScript.

The scoped CSS lives in the already loaded `assets/first-steps.css`. Its content-addressed token updates only on Home and Creative. The Creative source and generated HTML change by the same single instructional sentence. No new runtime JavaScript, account, request, storage, cookie, form, route, template content, publication-date claim or sitewide print rule.

## Verification

The new `creative_print_history` adapter reverses only four fully SHA256-bound production files from published parent `e30cbee4656917c105724614c6ea8821a21af002`. Original snapshots and old baselines are not modified. Unknown changes remain visible, invalid offsets and hash drift fail closed, and old release-contract views are reconstructed only for their original versions.

The focused Chromium component reproduction checked the prior closed-state print failure and the CSS fix. The extended `first_steps_browser.py` tests actual Creative Work documents at 320, 390, 768 and 1440 CSS pixels with JavaScript on and off. It verifies that print exposes the exact sheet, hides screen actions, stays within the viewport, and returns to the same folded state. Where screenshot artifacts are enabled, it captures an A4 PDF for visual review.

Required release gates: deterministic build with zero output drift, 194-page HTML and search audits, the complete unit suite, five hosted browser groups, final-head automated review, exact-base merge, GitHub Pages deployment and independent public-byte verification. Do not mark a gate complete without its receipt.

## Research boundary and next step

This is a software repair, not evidence that people find the Creative brief useful or understand its permission and AI-assistance cautions. Conduct the separate consenting visitor study before claiming human effectiveness, and base the following usability changes on specific observed friction rather than an invented case.
