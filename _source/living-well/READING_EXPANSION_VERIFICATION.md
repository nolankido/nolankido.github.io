# Living Well reading expansion: verification receipt

Reviewed on October 9, 2026.

Verified source and generated-output commit: `ba2d2165886921dca65e01da7b2ded33afc8ca1d`.
Branch verification run: `37983905078`.
Artifact: `living-well-expansion-checks`, ID `11642372368`.
Artifact SHA-256: `8b2f875621e79609b06844aecf00e0a8b9313d52afdeba75cfdc45b0977df821`.

## Executed checks

- The source payload and original file hashes were checked before patching; resulting hashes were checked afterwards. Only eleven explicitly allowed Living Well sources, tests and section CSS files were patched.
- Deterministic build: 140 generated files checked, zero differences.
- Full unit discovery: 240 reported test executions in 79.306 seconds, all passing.
- Living Well browser checks: all 41 pages at 320, 390, 620, 768, 1024 and 1440 CSS pixels, including enlarged text spacing.
- Keyboard reading routes, source-note anchors, resource navigation, five exact worksheet downloads, print visibility, browser storage and no-JavaScript paths passed.
- The dedicated browser report has no axe-core violations, JavaScript errors, failed local responses or write requests. External services were blocked during the browser tests.
- Retained whole-site review: 127 page records, 889 viewport checks and 254 axe runs; no failures. The report retains color-contrast items requiring manual review. These are not silently treated as a universal accessibility certification.
- Desktop and mobile rendered previews were examined separately. The local rendered test did not claim to exercise HTTP navigation; the successful GitHub Actions browser run supplied that coverage.

## Scope and limitations

This adds five readings and expands two existing articles. There are 23 published Living Well readings, three explicitly proposed experiments, 18 outside-resource selections and five unchanged text worksheets. All previous public routes remain.

Research notes identify exactly what was read. The AI-consciousness discussion uses a publicly available abstract and original philosophical sources; it does not claim to assess a current commercial model. The poem note links to the original transcript without reproducing the poem. The learning example is explicitly fictional and illustrative, not an executed model result. No personal stories, favorite resources, practice history or completed experiment results have been invented.

App installation, course completion, third-party media playback, clinical efficacy and third-party security were not tested or claimed. Existing global layout, privacy, analytics, contact and Poker files are unchanged. No permanent workflow or permission change is part of the release.

The temporary branch workflow and transfer fragments are removed in the clean review commit. Full retained PR checks remain required before merge. GitHub Pages deployment and the main workflow's exact public-byte verification are separate post-merge requirements.
