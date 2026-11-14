# Resources hub: four-card layout and heading reflow

Prepared: November 14, 2026
Canonical page: https://nolankido.com/resources/
Prior content release: https://github.com/nolankido/nolankido.github.io/pull/333

## Observed gap

The prior release added four practical kits to the Resources page using the existing `identity-readings` component. The shared grid was built for **three columns**, leaving the fourth card alone on the next row at wide viewports. The shared card-heading rule targeted `h3`, but the new cards correctly used `h4` under their section `h3`, so their typography did not inherit that heading rule.

This is a bounded layout/typography issue. It is not an SEO or visitor-metric result.

## Focused repair

- Add rules scoped to `.page-resources .resource-kit-index` in `assets/resources-reader.css`.
- Render the four cards as two equal-width columns above 800 CSS pixels and one column at or below that breakpoint.
- Match the existing card-title typography for the nested `h4` elements, without changing semantic heading levels.
- Allow long linked filenames to break safely; add spacing between descriptions and downloads.
- Include the new `#resource-new-kits` anchor in the mobile sticky-header offset selector.
- Update only the generated Resources HTML's versioned stylesheet URL to match the CSS SHA-256 short hash `c2294111009c`.
- Add two scoped assertions to the existing local Resources test module, bringing its tests from six to eight.

## Verification performed

- The exact proposed CSS passed a local `tinycss2` syntax parse with no parser errors.
- An offline Chromium/Playwright **layout fixture** using the existing three-column baseline and the exact proposed CSS passed seven viewport widths: 1440, 1024, 800, 768, 620, 390 and 320 CSS pixels.
- The fixture showed two cards per row at 1440 and 1024, single-column stacking from 800 downward, and no horizontal overflow at any tested width. The heading's computed font size was 20 CSS pixels.
- Verified the old generated page is unchanged except for the stylesheet version reference, and the new CSS Git blob matches the exact locally tested file bytes.
- Static checks confirmed the stylesheet is loaded only on the Resources route by `_scripts/build.py`. The four cards, ten downloads, page copy, metadata, canonical URL and sitemap date were not modified.
- Eight permanent `test_resources_hands_on_kits.py` tests are included in the existing local release checklist. The complete site-wide release gate and a live-site visual browser check are not claimed here.

The browser check was a controlled local fixture of the Resources component, not a loaded production page. The repository and production deployment still require verification after merge.

## Boundaries

No new tracking, paid service, GitHub Actions, background tasks, publication date changes, private file exposure, user testimonials, search ranking claims or external changes were introduced.
