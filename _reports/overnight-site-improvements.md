# Website continuation: useful navigation and publishing quality

The current pass starts from production commit
`5650693ef66763d1b22cfc1688bd629d183711f6`, tree
`cb2fe6895dcab1ddfb1998fdfefa7cb11424560b`.

The practical AI hub already describes Decide / Brief / Check / Measure and
offers one complete workbook. Its four destinations did not show the same path.
A reader arriving directly at a guide or tool could miss the other checkpoints.
This release connects those existing pages, without adding another article,
route, runtime script, storage mechanism or tracking event.

Each destination shows the four stages in order, identifies the current page,
links to the other three, and offers the complete blank workbook. The current
stage is text rather than a self-link, so activating it cannot reload a tool.
An onward link offers the next relevant check; the final calculator returns to
the whole path. The path remains optional, and stopping or using a simpler
method remains a valid decision. A visible reminder tells readers to save
results in their own notes before moving between pages. No entries are carried
between tools. Print copies omit the navigation panels.

The build decorates finished pages after their reading time and outline are
calculated. Original article content, section outlines, reading estimates,
metadata, publication dates and original blank sheets therefore stay intact.
All 315 original source, asset and download files and all five feeds are
protected by independently captured production hashes. Of the 198 generated
outputs, only the four destination pages change. Eighty-eight article outputs
remain byte identical; the two affected articles restore exactly after removing
only the two reviewed navigation blocks and their scoped stylesheet link.
Historical snapshot digests remain unchanged. The adapter removes exact frozen
blocks on four named pages; changed copy inside a marker remains detectable.

Validation before merge must include committed-build and HTML checks, the full
existing unit/content suite, and all existing browser suites plus the new
navigation suite. The new suite covers four widths with scripts on/off,
expanded text spacing, all sibling destinations, keyboard onward navigation,
Back, exact workbook downloads and a private-input return journey. Hosted CI
owns browser execution and preview images. Review its actual outcomes before
merging. Published status requires Pages success and all 372 public response
targets matching the merged release, followed by a fresh main ref check.

Search Console read on October 13, 2026 confirmed that Google downloaded the
existing sitemap on that date. It contains 166 submitted URLs and reported no
warnings or errors. This does not establish indexing or ranking gains. This
release adds no indexable route, so an unchanged sitemap needs no resubmission.

## Continuation priorities

Read current main, recent pull requests and actual release evidence first.
Do not reopen completed work or merge the outdated PR #48. Preserve the
Technology-first personal homepage and approved identity. Prefer one reproducible
reader, accessibility, performance or publishing defect per pass over more
generated articles or speculative copy changes. Follow the existing full release
gate and inspect browser previews for visual changes. Record executed evidence
and the next useful priority; do not present prospective checks as completed.

The pull request carries the executed checks and exact deployment receipt when
verified. Future sessions must read that receipt and current refs before treating
this pass as complete. This document describes the release contract; prospective
checks above are not execution evidence.

Executed local checks for the candidate: the committed build matched all 198
outputs, all 171 HTML pages passed the HTML parser check, the reduced historical
failure was still detected, the search audit passed, and all 463 unit/content
tests passed. The eight new preservation and navigation checks are included in
that total. Local browser execution was not used. Hosted browser outcomes and
publication evidence belong in the release receipt after execution.

The first hosted run passed the new navigation suite. It exposed two inherited
test assumptions: the task-brief fallback checked every download as the original
sheet, and an archive keyboard journey checked the next action before the prior
navigation had fully loaded. The fallback now selects both original sheet links
explicitly and requires exactly two; their destination and file-byte assertions
remain. The new workbook has its separate exact-download checks. Archive links
use keyboard activation inside a full-load navigation wait, retaining every
original destination and disclosure assertion. No website script is changed.

The navigation uses ordinary HTML links to existing canonical destinations.
Google's current link guidance recommends crawlable anchors, relevant link text
and helpful contextual cross-references. This is a discovery and reader-flow
improvement, not evidence of increased search traffic:
https://developers.google.com/search/docs/crawling-indexing/links-crawlable

## Calculator export recovery

This pass starts from verified production `7f8bb0055ba469db6bb36a431cc0ea29d47c874b`.
The calculator's file-export handler had no error recovery. An independent Node
VM fixture injected an unavailable object-URL API into the existing production
script. Saving raised an uncaught error, left the comparison unselected, and
provided no download feedback. This is a reproduced failure condition, not a
claim that ordinary downloads were broken for all visitors.

The handler now keeps the complete comparison visible, focuses and selects it
for manual copying when file creation or activation fails, and gives a clear
recovery message. Successful activation says a download was requested; it does
not claim the browser saved a file. Temporary links are removed and any created
object URL is revoked. Feedback belongs only to the current visible comparison.
The arithmetic, input validation, source articles, dates, worksheets, contact
behavior and analytics stay intact. No new runtime dependency or collection.

Independent production capture verified all 198 generated outputs and 316
original source, asset and download files against Git objects before editing.
The only generated-page change is the calculator script's content-derived cache
version. All 90 article HTML files and all five feeds remain byte identical.
Historical integrity restores only the exact reviewed handler and that one
version change. Unmarked code or page edits remain detectable, and old golden
digests are unchanged.

The failure-injection fixture covers Blob creation, object URL creation, element
creation, insertion and activation, plus successful exact-text export and stale
or hidden results. The hosted browser suite injects creation and activation
failures, checks complete text selection and visible recovery, confirms cleanup,
and verifies a subsequent real download. Recovery views are checked at mobile
and desktop widths with expanded text spacing. The historical work-preview
record is retained with its exact captured script; the hosted suite separately
requires identical normal-result pixels with the old and new export handlers.
The existing full release gate and all
33 browser suites are required. Executed results and final deployment belong in
the pull request receipt after verification.

Executed local checks: all 198 committed outputs matched the build, all 171 HTML
pages passed parsing, the search audit passed, and all 469 unit/content tests
passed. The six new export and preservation tests are included in that total.
The first full local run correctly rejected a historical preview dependency
against the changed script. Its check now restores only the exact captured
export handler; the recorded preview and dependency digests are not rewritten.
The focused preview suite and the complete 469-test run then passed. Hosted
failure journeys, pixel equivalence and mobile/desktop views remain required
before merge. Local browser execution was not used.

The first hosted run passed the build/content gate and normal-result pixel
equivalence. The new failure test's setup returned its injected function to
Playwright, which immediately invoked it before the download interaction.
Setup and restoration now use explicit function bodies with no returned
function. All recovery, exact-download and cleanup assertions are retained.
An unrelated collection suite's browser process crashed during startup before
loading its page. The complete existing gate is still required on the corrected
candidate; these failures are not publication evidence.

Next useful work: review a different concrete visitor or publishing defect from
current source and live evidence. Do not repeat completed navigation or export
work or expand article volume just to fill a work pass.

## Finder submission and composition

Production was re-read at `b42894f9483705d08798562095058380590e3ac2`.
PR #54 is merged and deployed. Its 469 unit/content checks and all 33 browser
suites passed before merge, Pages run 38359845075 succeeded, and published-byte
job 115171188773 passed all 372 targets for that exact main SHA. Its post-merge
Site checks run 38359844453 has also completed successfully. The detailed
receipt is https://github.com/nolankido/nolankido.github.io/pull/54.

The next inspection found that an explicit site-wide search left keyboard focus
above the results. Enter was also prevented during input-method composition,
and a pending live-filter timer was not cancelled when composition began. A
small independent event fixture reproduced these behaviors against production.

Explicit Enter or Search button activation now filters and focuses the existing
results heading. Live typing, interest/type changes, native search clearing and
composition completion keep focus in their control. Composition Enter retains
its native default, including the 229 boundary case documented by MDN. Starting
composition cancels a pending filter, avoiding a partial-query announcement.
This is an input-handling fix, not a claim of multilingual search coverage:
https://developer.mozilla.org/en-US/docs/Web/API/Element/keydown_event

The search algorithm, index records, results grouping, styles, privacy behavior,
native fallback and original source pages are unchanged. Only the finder event
block and its generated script cache version change in the public site.
Before editing, all 198 generated outputs and 316 source/asset/download files
were independently verified against production Git objects. Their complete
path-and-byte digests, all 90 article pages, all five feeds and metadata remain
protected. The historical adapter restores only the exact frozen event block
and that one cache version; existing golden digests are retained, with mutation
checks that detect unrelated changes.

Executed locally: 473 unit/content tests passed, including four new interaction
and preservation checks; the committed build matched all 198 outputs; all 171
HTML pages parsed; and the search audit passed. The existing hosted finder suite
now verifies real explicit-search focus and tab order, unchanged typing/filter
focus, synthetic composition and boundary events, and viewport visibility at
five widths. Synthetic events test handler behavior, not a real operating-system
IME session. All existing browser suites and final live-release proof remain
required before completion. The pull request receipt records their executed
results. No local browser was installed or run.

The first hosted candidate passed all 473 unit/content tests and 33 browser
suites. Visual review of its four submitted-search screenshots found that the
sticky header could overlap the focused heading in the narrow empty state.
Explicit submission now focuses without an intermediate scroll and immediately
centers the heading. The browser checks measure against the actual sticky
header, including after expanded text spacing, and retain the existing focus,
keyboard, privacy and result assertions. A complete gate on this corrected
candidate is required; the earlier pass does not authorize its merge.

Next useful work: inspect a separate concrete reader-entry issue from current
source and live evidence. If the archive keyboard timing failure recurs, add
targeted route, focus and input-mode diagnostics before changing its assertions.

## Poker finder composition handoff

Production was re-read at `b041a9ebcb733581e23d42fd9a1af4433a5244fa`.
PR #55 is merged and deployed; its release receipt records 473 unit/content
checks, all 33 browser suites, successful Pages deployment, and 372 exact live
targets for that SHA. The only other open pull request is the stale PR #48 and
it remains untouched.

The main Poker finder intercepted Enter and Escape while an input method was
still composing text. A delayed live-filter callback could also survive the
start of composition and replace the completed query state. The finder now
cancels that pending callback, ignores both the standard composing flag and the
legacy key-code 229 boundary, applies the completed composition without moving
focus, and reserves results-heading focus for an explicit completed search.
The focused heading is centered below the sticky site header.

Search terms still stay on the page and out of URLs, storage and requests. The
index, scoring, aliases, filters, source records, article prose and dates, five
feeds, contact behavior and analytics are unchanged. A narrow historical
adapter restores only the exact reviewed event block and its one generated
cache version; unrelated script mutations remain detectable. The existing
production-preservation layers continue to protect all 198 outputs, 316 source,
asset and download files, 90 article pages and five feeds.

Executed locally: the committed build matched all 198 outputs, all 171 HTML
pages passed the search audit, and all 475 unit/content tests passed. The hosted
finder suite now exercises composing Enter, the 229 boundary, delayed-filter
cancellation, completed-composition results, explicit focus and sticky-header
clearance. Local browser execution was not used. The complete hosted browser
gate, merge, Pages deployment and exact public-byte verification are still
required before this change can be reported live.

Next useful work: inspect a separate concrete entry or recovery defect after
this candidate is fully verified. Do not broaden this pass to the other Poker
filters without reproducing their behavior independently.


## Archive keyboard release checks

The next user-directed pass starts from main
`419a504b49f84d311732f8f30fe927d8626409e4`. PR #56 passed the complete
pre-merge gate in run 38441955195. Pages run 38443252261 succeeded; published-byte
job 115454964399 passed 372/372 targets and printed the exact merged SHA. A fresh
main read and a direct public Poker-finder script hash matched that release.

The post-merge run 38443252774 repeated a historical archive keyboard timeout
at the article-link activation. All other browser groups, the build and live
bytes passed. That old log did not identify the subject, input mode, target,
focus or disclosure state, so it does not establish a public navigation defect
or prove the exact cause of the intermittent failure.

The archive browser check now verifies that the disclosure opened and the list
and anchor are visible before focusing the anchor and sending a real Enter.
It requires the exact expected href, destination URL, completed document load
and visible main heading. Playwright does not automatically check visibility
for focus or press; the previous fixture lacked those explicit preconditions:
https://playwright.dev/python/docs/actionability

The deprecated navigation-event wait is replaced by an exact URL-and-load wait.
No click fallback, scripted navigation, retry, timeout increase or relaxed
assertion is added. All four subject destinations and the About-to-archive route
now run at 390 and 1440 pixels with JavaScript enabled and disabled: twenty
complete keyboard journeys instead of ten. Existing eight layouts, eight
expanded-text checks, thirty-two disclosure checks, accessibility scan, no-write
and no-page-error assertions remain.

Every journey logs mode, width, subject, expected destination, document state,
focus, disclosure state and target visibility. Failed link journeys preserve a
structured diagnostic and viewport screenshot in the existing CI artifact,
then re-raise the original failure. The evidence uses only public local test
pages and does not capture user messages, private inputs or credentials.

Independent Git-object comparison confirmed that all 198 generated outputs and
all 316 source, asset and download files are exactly the current production
bytes. No public page, stylesheet, script, article, feed, author claim or search
metadata changes in this reliability pass. The build and static search audit
passed. All 475 unit/content tests and the HTML5 parser check on 171 pages also
passed. The full hosted gate and final release receipt belong in the pull
request after execution. Browser execution stays in GitHub Actions.

Next useful work: use any new archive failure diagnostics to distinguish a
real focus/route defect from test synchronization. Once the gate is stable,
inspect a separate reader-facing issue from current evidence.

## Local typography and current indexing evidence

This user-directed pass begins from live main
`87a733313e01592474bf06cb9ab2adf0f5140ea3` after PR #57. The existing
Pages deployment and complete post-merge checks succeeded. Only the stale PR #48
was open; it remains untouched.

A fresh Google Search Console inspection on October 13, 2026 reports the
Technology hub as Submitted and indexed, with a successful mobile crawl at
10:40:39 UTC and matching declared and Google-selected canonical URLs:
https://nolankido.com/technology/
The queried September 13 to October 10 search-query window returned no rows.
That does not establish zero traffic or a ranking change. No unchanged sitemap
was resubmitted, and no indexing request was made.

The remaining font dependency was visible in production HTML and the preserved
font stylesheet: all pages preconnected to Google and requested font binaries
from fonts.gstatic.com. Blocking that origin leaves fallback typography rather
than the reviewed typefaces. This pass moves the exact existing WOFF2 binaries
to the existing GitHub Pages host. There is no typeface redesign, font generation,
binary modification, subsetting, extra preload or added runtime code.

All 38 font-face declarations retain the original family, style, weight, display
policy and Unicode ranges. Their 24 distinct files total 422,284 bytes across
all language subsets. Browsers still choose the subsets and faces they need;
this is not the download size of every page. Content-addressed filenames and the
existing stylesheet versioning support caching. The three original licenses
are bundled. Provenance records the provider URLs and exact sizes and hashes.
Builds remain offline and reject missing, changed or unmapped files/licenses.

The font preconnection is removed from all 171 pages. The privacy notice now
accurately describes same-site font hosting and is dated October 13. All 170
other complete page bodies, article metadata, five feeds, original font source
CSS, design styles, analytics, contact behavior and public identity remain intact.
Original URLs, CNAME and .nojekyll remain. The only modified pre-existing source
or asset files are the privacy notice, its manifest update, and generated font
CSS. An independent baseline was captured from production Git objects before
editing. Historical adapters reverse only the frozen font URL/head substitutions
and exact privacy change, with negative controls; old golden hashes are retained.

The hosted browser gate adds exact geometry comparison against the original
provider-font arrangement, using identical font bytes with all external traffic
blocked. It also exercises all font subsets, blocked-font fallback text, mobile
reflow, no-script navigation, exact asset responses and scoped accessibility.
The existing design suite now runs with real local typefaces across every page.
The published-byte inventory expands from 372 to 399 targets, including every
font and license. Executed check results and the final deployment receipt belong
on the pull request after completion.

This removes one external delivery dependency and preserves the intended design
when Google Fonts is blocked. It does not establish a measured speed improvement,
Core Web Vitals change or ranking gain. Relevant primary guidance:
https://web.dev/learn/performance/optimize-web-fonts
https://web.dev/articles/font-best-practices

Next useful work: prioritize a genuine new practical-AI case or an observed
reader task over generic content expansion. Search Console now confirms one
important entry page is indexed; meaningful performance comparison requires
more time and actual search data.

The first hosted candidate passed all 481 unit/content checks and all 33
existing browser suites, including 855 full-site page/viewport checks with the
real local typefaces. Six mobile/desktop arrival previews were inspected. The
new font comparison fixture then stalled and the identity job reached its time
limit. That candidate was not merged. The fixture now separates binary decoding
from the rendered CSS faces, bounds its readiness checks, provides matching CORS
headers for the mocked old provider, and logs each decode and view. Exact
rendering parity, no-script coverage, fallbacks and all 27 asset-byte checks
remain required. The corrected candidate needs the complete gate again.

The second candidate again passed 481 unit/content checks and the original
browser suites. All 24 binary decode checks and the three JavaScript-enabled
viewport parity comparisons passed. Its new fixture timed out in Playwright's
in-page font-status polling on the no-script About reference. The fixture now
polls the native FontFaceSet from the driver, keeping the same 10-second bound,
loaded-state requirement and complete no-script comparisons, with the exact
font state included in any timeout. No public file changed in either repair.
The final candidate still requires the complete hosted gate before merging.

The third candidate passed the original gate checks and reached all 72 old/new
font-rendering views, including no-script pages, before the new test's four-minute
watchdog stopped it. The remaining fallback fixture's text-spacing CSS is now
delivered in the test HTML rather than waiting on an injected style's load event
with page scripting disabled. It explicitly checks the resulting letter, word
and line spacing. Keyboard, parity, fallback and asset stages now log progress.
Coverage and public files remain unchanged; publication still requires a full
successful candidate run.

PR #58 subsequently passed all 481 unit/content checks and all 34 browser
suites in run 38463359878. The font fixture passed all 36 paired views, 24
binary decodes, 12 fallback views, six keyboard journeys and 27 exact asset
responses. Six arrival previews were inspected. Main
`9558826cd0098f68e46e0b07349e38d486e3186d` has the same reviewed tree
`a234b678c8aadf4a2f44511254277ced831bcc5a`. Pages run 38464630611 succeeded;
published-byte job 115528279801 passed 399/399 targets with that exact main
marker. The later post-merge browser launch crashed with SIGSEGV before loading
a page or running a test. The unchanged failed workflow was rerun, and its full
aggregate check passed. No website code was changed to mask the runner crash.
Final receipt: https://github.com/nolankido/nolankido.github.io/pull/58

## Search directly into a useful section

The next user-directed pass starts from the verified PR #58 release above.
Only the stale PR #48 was open at the initial current-repository read. Its
outdated branch remains untouched. No new Search Console submission or
inspection was needed immediately after the previous pass.

Current evidence showed that global search could not find visible, published
headings absent from page titles and summaries. For example, "recovery" missed
"Keep access and recovery simple" in the document-finding guide. Other
reproduced misses were "bounded job" in the judgment essay, "commitments" in
the AI-answer guide, "manageable shape" in Creative Work and "practical needs"
in the poker access section. The original search score rejected each example.

The existing search page now indexes 914 visible major headings across its
151 current destinations. Each heading comes from the generated public page
and retains its exact existing fragment and label. The reading-outline parser
excludes disclosures, navigation, hidden subtrees, scripts and styles. The
search page retains its current indexing policy and is not added to the sitemap.
No new page, service, crawler, tracking or visitor-query transport is introduced.

Results retain their existing collection groups. Title and summary matches
rank ahead of heading-only matches. Up to three relevant section links are
shown per result, with the page title still available. A query must match one
section plus the page context; words in unrelated sections do not create a
false combined match. Empty queries show the original browse view. Missing or
malformed optional section data leaves the title/summary search working.

The section-data block adds 55,581 bytes to `/find/` only. Its 141,113-byte HTML
uses the existing search JavaScript and stylesheet; typing or filtering fetches
nothing. The original 151-page browse index works with JavaScript disabled.
Search wording now states its scope accurately: headings are included, article
body paragraphs and hidden exercise answers are not full-text indexed.

An independent baseline was captured from production Git objects before edits.
All 198 output paths and 343 source/asset/download paths are retained. Only the
search HTML changes among generated outputs; all 170 other pages, article
metadata, five feeds and sitemap remain exact. The only changed original
source/assets are search copy, search JavaScript and its scoped stylesheet.
Frozen, narrow inverse patches adapt historical checks without resetting any
golden hash. Negative controls detect unrelated code, style, copy and index
changes. Six new unit checks passed, including real old/new query comparisons,
source anchors, hidden-answer exclusion and JSON breakout protection.

The hosted browser fixture adds ten real keyboard search-to-section journeys,
four expanded-text views, optional-data failure recovery and no-script browsing.
All existing suites remain required. The full gate, preview review, Pages
deployment and exact published-target receipt belong on this pass's pull
request after execution. This improves on-site discovery and navigation; it
does not establish an external search-ranking or traffic improvement.

Next useful work: use actual reader/search evidence or genuine firsthand
material to choose the next change. Do not expand the article catalogue or
repeatedly submit an unchanged sitemap simply to create activity.
