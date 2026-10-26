# Turn 25: stabilize and broaden poker library script-free navigation checks

Prepared October 25, 2026, Pacific/Honolulu. This is a test/release-reliability improvement, not a new public feature or a visitor-study result.

## Reproduced evidence

In the previous [PR #134 Site checks run 40264662232](https://github.com/nolankido/nolankido.github.io/actions/runs/40264662232), the first `Browser / poker` job failed in `_tests/library_browser.py` when Playwright attempted to click the distant `/poker/decision-lab/` link while checking the library with JavaScript disabled. The locator resolved and was visible, but Playwright reported `element is outside of the viewport` after scrolling, then timed out. The targeted rerun passed on the same commit, demonstrating a flaky acceptance step, not a confirmed visitor-facing content defect.

The site's shared CSS uses smooth scrolling under ordinary motion preferences and explicitly disables it under `prefers-reduced-motion: reduce`. The test's single mouse-click route combined scrolling, actionability checks and an unbounded long-grid position, but did not separately verify the destination URL or keyboard activation.

## Focused test improvement

Within only the existing browser test:
- Run the two no-script fallbacks (JavaScript disabled and the library JavaScript request blocked) at 320, 390 and 1440px, six cases instead of two.
- Use reduced-motion media in these fallback contexts so Playwright does not race the site's smooth scroll while keeping pointer navigation real.
- At 320 and 1440px, explicitly scroll the actual destination link into view, assert it is in the viewport and click it. At 390px, focus the actual link and activate it with Enter.
- Check that navigation reaches the exact existing `/poker/decision-lab/` URL and that its first native answer disclosure opens by the matching pointer/keyboard method.
- Require the full guide inventory and correct hidden filter state with scripts disabled/blocked. Ensure neither fallback writes localStorage, sessionStorage or cookies.
- Preserve all existing enabled-script search, filter, XSS, navigation, viewport, accessibility and external-request checks.

## Boundaries and release gates

Exactly one test file changes; this report is the other new file. No production source, generated HTML, scripts, CSS, metadata, feeds, sitemap, analytics, cookies or release workflow changes.

This does not prove human usability or resolve [study #123](https://github.com/nolankido/nolankido.github.io/issues/123). The connected Search Console provider requires a subscription and was not used; no plan was purchased or traffic number inferred.

Required before merging: full hosted deterministic build, complete unit suite, all five browser groups, aggregate gate and reviewed PR head. Public release deployment is expected to be byte-identical because production files are unchanged.
