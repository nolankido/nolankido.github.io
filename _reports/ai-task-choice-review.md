# AI task decision guide and recognizable site icons

Assessment date: October 12, 2026.
Baseline production commit: `4f80aeb5b20678d4a95e965043342a3f992eb8ad`.
Baseline tree: `46d7d7f82f24d7ea11f68fa896e06f62760c033c`.

## Assessment and priority

The current Technology area gives readers ways to brief a task, inspect a summary and compare workflow time. Its first-visit gap is the prior decision: whether the contemplated task is suitable for a small AI-assisted trial at all. The existing Living Well articles on personal judgment and the proposed notebook experiment are useful but address narrower situations. A task decision guide adds a different action rather than another generic AI essay.

The intended public impression is useful, careful judgment: a person can offer a method that sometimes recommends no AI. This is an editorial assessment, not a measured credibility result or a claim of established authority. The new page follows the existing identity and does not add credentials, private projects, social profiles, testimonials or personal experiments.

A second concrete gap was icon compatibility: the site declared only an SVG favicon. Google's current documentation lists PNG among its supported formats, asks for a square image, recommends larger than 48x48, and requires a stable crawlable address. The new raster versions convert the existing NK mark, without a rebrand.

## Implementation

`/technology/should-i-use-ai/` contains six questions, fixed visible decision rules, four explicitly fictional worked examples, a full blank worksheet and an optional rule-based form. The form never asks for task text or a document. It is not AI, a risk score, a validated instrument, or approval to act.

The six answer domains concern the finished result, input permission, consequences, independent review, a simpler alternative and the scope of action. There are 144 combinations. Input restrictions or serious/unclear consequences take precedence, then missing purpose or review, then an adequate or untested simpler method, then an action boundary. A bounded draft is suggested only when none of these conditions remains unresolved. Every applicable caution is still listed. Invalid or incomplete inputs never produce a positive result.

Changes to answers hide and erase the stale result. Reset, pagehide and restored-page handling clear selections. All explanations, example outcomes, worksheet content and ordinary links remain available without JavaScript. The new script has no network, storage, upload, telemetry or model integration. Existing site analytics and external font-file delivery remain unchanged.

Technology has a marked early entry section, and Resources has a matching guide and worksheet link. The new worked-guide manifest record automatically participates in bylines, Article metadata, breadcrumbs, Writing, internal search, sharing controls, sitemap and both relevant RSS feeds. The new search title is `Should I Use AI? Task Decision Guide & Checklist | Nolan Kido`. It reflects the content, not measured keyword volume. Historical publication dates and every old feed item remain unchanged.

`/favicon.png` is 96x96 and `/apple-touch-icon.png` is 180x180. Both are derived from the original `favicon.svg`, which remains byte-identical. Each page links the new formats while retaining the SVG. No favicon display, Google indexing or improved ranking is guaranteed.

## Verification design and candidate observations

The new 13-test unit suite independently compares all 144 answer combinations, checks every applicable caution, rejects malformed data, validates configuration and escaping, checks the complete worksheet preview, metadata and discovery, and enforces source/history preservation. Its pre-edit baseline is generated from the exact verified production tree, not from a changed candidate. The baseline pins 211 source/asset/download files, every original manifest record, every prior item in five feeds, and all 169 previous page bodies.

Older golden contracts keep their historical digests. A narrowly scoped predecessor-view helper reverses only this release's marked insertions, new publication records, icon declarations and new sitemap URL. The independent new test also checks those reversals against all 169 actual old bodies. This avoids silently resetting historical expectations to changed content.

The candidate's deterministic build has 196 outputs. Its static audit covers 170 HTML pages, 170 unique titles/descriptions, 89 Articles, 168 breadcrumb pages, 165 sitemap URLs and the five existing noindex pages. An independent traversal of rendered HTML links, excluding noindex utilities as intermediate nodes, reaches all 165 indexable pages: 1, 19, 96 and 49 at depths 0, 1, 2 and 3. The new guide is two ordinary links from Home.

Local offline browser checks passed 13 scenarios, 16 layouts, eight expanded-text-spacing checks, two fallback modes and page-lifecycle clearing. Desktop and mobile screenshots were inspected. The local managed browser cannot navigate a localhost HTTP server, so these checks use offline rendering; they do not establish downloads, native HTTP journeys or axe results. The new hosted browser suite tests those separately with external services blocked. All 27 old browser suites remain present, plus the new one. The full final-head CI gate must pass before merge.

The published response inventory contains 274 targets. That is an expected count, not evidence of a live deployment. Release verification requires the Pages deployment and the separate exact-response job to pass on the merged commit; the PR completion receipt records the final result.

## Measurement and remaining work

GSC Wizard was queried in this pass. Its connected properties do not include nolankido.com. No impressions, clicks, query volume, indexing result or Search Console submission was obtained. An absent connected property does not establish zero traffic or non-indexing. A connected verified property remains necessary for evidence-led ranking and click-through decisions.

The guide and recognizability improvements make existing positioning more useful and consistent. They do not establish visitor learning outcomes, measured AI productivity, conversion gains, outside recognition or increased traffic. Owner-approved original imagery, verified public identity details and genuine measured examples require real contributions rather than invented substitutes.

## Maintenance

Edit question labels in `_source/ai-task-choice.json`, with fixed rule domains enforced by `_scripts/ai_task_choice.py`. Rule behavior lives in `assets/ai-task-choice.js` and is checked independently in `_tests/test_ai_task_choice.py`. Keep the written rule order and worksheet aligned with any change. Never describe the rules as a certified safety check. Rebuild generated output with `_scripts/build.py` and preserve all earlier feed records.

PNG icons were explicitly converted from the existing source mark. `_scripts/render_site_icons.py` is a regeneration utility requiring CairoSVG; it is not a runtime or build dependency. Inspect any regenerated raster output before committing it. The production build uses the committed small PNGs.

## Sources checked

- Google Search Central, helpful content and accurate authorship: https://developers.google.com/search/docs/fundamentals/creating-helpful-content (current page updated October 5, 2026).
- Google Search Central, favicon formats, dimensions and eligibility: https://developers.google.com/search/docs/appearance/favicon-in-search (current page updated August 28, 2026).
- NIST, AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework. Used only as clearly labeled broader background, not a source of the guide's editorial scoring or certification.
