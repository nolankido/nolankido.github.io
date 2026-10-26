# Turn 23 independent engineering pass: complete AI answer-review printing

Prepared October 25, 2026, Pacific/Honolulu. This is a bounded usability repair to the existing AI answer-checking guide. The separate consenting-visitor study in issue 123 remains open. Automated checks do not establish visitor comprehension or demand.

## Reproduced gap

The guide keeps six worked examples and its blank review record inside native disclosures. On screen that reduces clutter. In print media, however, closed disclosures omitted their contents. A reader following the existing print instruction could receive an incomplete guide and no blank record unless every disclosure had first been opened manually.

## Change

Browser Print now includes all six authored examples and the complete blank review record whether their disclosures are open or closed on screen. The disclosure labels remain as printed section headings, while their interactive markers are removed from paper. The answer-type picker and download button are hidden in print because they are navigation and screen actions rather than worksheet content.

The ordinary screen page is unchanged except for an accurate sentence explaining the print behavior and a class used to hide the download action on paper. Every disclosure still starts closed and retains its native keyboard behavior. Returning from print preserves that closed state.

No new script, form, storage, network request, account, public route, answer-entry field, model connection, or accuracy claim is added. The original download bytes and all six teaching examples remain unchanged.

## Verification design

The focused unit contract checks the print selectors, all six closed examples, the exact blank-record embedding and the absence of added runtime code. The browser suite tests the complete print copy at 320, 390, 768 and 1440 pixels with JavaScript enabled and disabled. It verifies that every closed disclosure becomes visible only in print, the blank record exactly matches the download, screen state is restored, navigation actions are omitted, horizontal overflow is absent and an A4 PDF can be rendered.

Three production paths are bound to published parent `2809bbf4a234331ab6413323f3d100ccc823bd0f`: the guide source, its page-scoped stylesheet and the generated page. The test-only predecessor adapter reverses only exact reviewed hashes and leaves unknown edits visible. Full hosted release checks, automated review, merge, deployment and independent public-byte verification remain release gates.
