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
search page body changes. The other 170 pages change solely in the exact core
stylesheet cache token for the native anchor-spacing correction below. All
article metadata, five feeds and sitemap remain exact. Changed original
source/assets are search copy, search JavaScript, its scoped stylesheet, the
core accessibility source and its generated CSS bundle.
Frozen, narrow inverse patches adapt historical checks without resetting any
golden hash. Negative controls detect unrelated code, style, copy and index
changes. Six new unit checks passed, including real old/new query comparisons,
source anchors, hidden-answer exclusion and JSON breakout protection.

The hosted browser fixture adds twenty real keyboard search-to-section journeys,
four expanded-text views, optional-data failure recovery and no-script browsing.
All existing suites remain required. The full gate, preview review, Pages
deployment and exact published-target receipt belong on this pass's pull
request after execution. This improves on-site discovery and navigation; it
does not establish an external search-ranking or traffic improvement.

Next useful work: use actual reader/search evidence or genuine firsthand
material to choose the next change. Do not expand the article catalogue or
repeatedly submit an unchanged sitemap simply to create activity.

The first candidate passed all 487 hosted unit/content checks. The new browser
journey stopped at its immediate sticky-header clearance assertion on the
judgment essay. The fixture now waits for native fonts and allows five seconds
for the identical clearance condition, with measured coordinates and an arrival
screenshot retained. No destination scroll is forced and no public file is
changed. The next complete hosted run will distinguish unsettled navigation
from a persistent landing defect before any merge.

The diagnostic run confirmed a real defect: at 390 pixels, the wrapped sticky
header was 149 pixels tall but the essay fragment landed at 123.58 pixels, even
with fonts loaded and after the full five-second wait. The retained screenshot
shows the heading obscured. A narrow-screen rule now gives native fragment
navigation 180 pixels of scroll padding at widths up to 1050 pixels; the
desktop rule, header design, article prose and existing anchors remain intact.
This also protects direct links from outside the site. No runtime scrolling
script was added. All five arrival journeys now run at 320, 390, 768 and 1440
pixels. The exact CSS addition and old/new bundle tokens have narrow inverse
adapters; original baseline hashes remain frozen, with extra negative controls
for unrelated CSS or page-body changes. The complete gate is required again.


PR #59 subsequently passed all 487 unit/content checks and all 35 browser
suites. Main `16f230aaca2bed83addda5536a1f52e79780ee78` has the reviewed tree
`1d1c50382d9e04692fd4145c0924dd4e01886e18`. Pages run 38471966842 succeeded;
published-byte job 115553046543 passed 399/399 targets with that exact main
marker at 2026-10-13T21:38:04Z. The main Site checks run 38471966872 also
completed successfully. Final receipt:
https://github.com/nolankido/nolankido.github.io/pull/59

## Open the original case evidence

This user-directed pass begins from the verified PR #59 release. A fresh
repository read found only the stale PR #48 open; that branch remains untouched.
The homepage and a real missing URL were checked directly. The missing URL
returned HTTP 404 with useful recovery links, so no speculative 404 rewrite
was needed.

The existing recorded AI-assisted website case promises inspectable evidence,
but its commit and run IDs were plain text inside a disclosure. Readers now
have three native links beside the case facts: compare the actual repair,
inspect its candidate checks, and read the merged release record. Brief labels
explain what each source contains. The links remain part of the original page;
there is no new route, runtime, stylesheet, tool state, or externally loaded
content. The destinations open in the current tab when deliberately followed.

The public comparison confirms that the one corrective commit removed the
extra closing div from both source and generated output. Fresh GitHub reads
confirm that run 38196825689 succeeded on candidate
`73782caa4697204690c679626b36427c28201234` and PR #40 merged as
`6832b5e1edc85c50a3e6eb39a447cd67d9f0f80c`. These are the same historical
identifiers already recorded in the article and its downloadable evidence.
The original 347-test, 21-browser-suite, 235-target account is retained; current
release counts are not substituted into the historical story. The linked
release summary is this repository's record, not third-party certification.

An independent baseline was captured from production Git objects before edits.
All 343 source, asset and download files remain exact, including the article
source and evidence download. All 198 generated output paths and the complete
public page metadata remain fixed. Only the case page's evidence navigation is
added. The other 197 outputs, five feeds, sitemap and on-site search index stay
exact. A single-page inverse adapter removes only the reviewed block with its
frozen SHA-256; every older golden hash remains unchanged. Negative controls
retain detection of altered links, labels and article claims.

Four new unit checks cover exact preservation, verified historical link
identity, scoped insertion and negative controls. The existing workflow browser
suite additionally exercises all three links with keyboard Tab and Enter at
390 and 1440 pixels, with JavaScript both enabled and disabled. GitHub
destinations are intercepted by exact URL in that fixture, so browser checks
send no requests or writes to GitHub. Existing case layout, expanded-text and
accessibility checks remain required at 320, 390, 768 and 1440 pixels. Hosted
mobile and desktop evidence-panel previews are retained for visual review.

The local deterministic build, 171-page HTML5 check and search metadata audit
passed. The complete unit/content and hosted browser gate, preview review,
Pages result and exact published-target receipt belong on this pass's pull
request after execution. No unexecuted checks or release are claimed here.

One read-only Search Console query on October 13, 2026 returned no page rows
for September 13 through October 10. Missing rows do not establish zero traffic
or indexing status. No sitemap was resubmitted. Google's people-first content
guidance identifies clear sourcing and evidence as useful trust questions:
https://developers.google.com/search/docs/fundamentals/creating-helpful-content
This change makes existing evidence easier to inspect. It does not establish
an external ranking improvement, measured productivity gain or new credential.

Next useful work: use actual reader/search evidence or approved firsthand
material to select a substantive improvement. Keep the existing historical
case tied to its original release, and do not create new pages solely to
increase catalogue size.


PR #60 subsequently passed all 491 unit/content checks and all 35 browser
suites in run 38477982680. Four source-panel previews were inspected. Main
`9fc67443cabd8090b47c33bba2f11ce0fe6adc05` retained the reviewed tree
`9f1b8f41ad3fd082dd8d450b8c9d8c071cf034c1`. Pages run 38479013340 succeeded;
published-byte job 115576730425 passed 399/399 targets with the exact main
marker at 2026-10-13T22:38:02Z. Main was reread at 22:39:09Z. The next pass
also confirmed that the repeated main Site checks run 38479014640 had
completed successfully. Final receipt:
https://github.com/nolankido/nolankido.github.io/pull/60

## Try the existing time comparisons without retyping them

The next user-directed review starts from the verified PR #60 release. Main,
open pull requests and recent deployments were reread. Only stale PR #48 was
open, and it remains untouched. A link-graph check reached every public page
except the intentional 404 page from the homepage's main-content links, with
no route deeper than three steps. There was no evidence for another broad
navigation rewrite. No new Search Console query or sitemap submission was
needed so soon after the previous read.

The live time-cost calculator matched the current repository exactly. It had
three fictional worked examples, each with six inputs, but no way to load
those values into the calculator. Readers had to transcribe them manually to
try or adjust the comparison. The existing examples can now be loaded through
three native buttons above the inputs: Repeated task, One-off task and Review
costs more. A native link still leads to the original explanations and math.
No new page or example story was created.

Loading fills the six editable values and focuses the first input. Calculation
remains a separate deliberate action. Any existing values or nondefault basis
or quality selections require confirmation before replacement. Cancel preserves
the current inputs, selected basis/quality and exact report. Editing an input
cancels a pending replacement, so stale confirmation cannot discard that edit.
Confirmed replacement resets the basis to planning estimates and quality to
not yet checked. The example's fictional origin remains visible in results
and text exports, including after a reader changes the starting values.
Clear and page-exit behavior remove the example state along with the entries.

All loading happens locally. No new request, tracking, storage, dependency,
stylesheet or runtime file is introduced. With JavaScript unavailable, the
original worked arithmetic and complete blank worksheet remain usable; the
example controls stay hidden. The pure integer calculation code is exact.
The three loaded scenarios reproduce the existing 15-minute saving and two
45-minute losses. These are fictional arithmetic examples, not measured
productivity results.

An independent baseline was captured from current production Git objects
before changes. Of the 198 generated outputs, only the calculator page changes.
Among all 343 original source, asset and download files, only the calculator's
existing script changes. Article source, publication metadata, all five feeds,
sitemap, on-site search index and existing screenshots remain exact. The
historical adapters reverse four frozen script hunks, two exact markup blocks
and one cache token on their two specific paths. All earlier golden hashes
remain fixed; negative controls expose changes to arithmetic, source claims,
new control labels or example provenance.

The local build, 171-page HTML5 validation and search audit passed. Four new
unit checks cover the independent baseline, actual example values and results,
scoped native markup, and tamper detection. The existing hosted workflow suite
adds all three example journeys at 320, 390, 768 and 1440 pixels, exact example
file downloads, replacement cancellation/recovery, provenance retention and
no-script visibility. The complete candidate gate, hosted preview review,
Pages deployment and exact live-target receipt belong on this pass's pull
request after execution. This record does not claim unexecuted checks.

Next useful work: use actual reader feedback or approved firsthand material
to select a substantive improvement. Useful, inspectable tools support the
site's professional presentation; this pass does not demonstrate a change in
external rankings or traffic.


The first local full run executed 489 tests successfully but could not set up
the six export-failure tests: their minimal fake document invented nodes for
missing optional example controls. The fixture now returns null for those
three absent controls, as a real document does. Its original export-success,
five failure-injection, stale-state, cleanup and exact-byte assertions remain
intact. The prior raw-script hash also passes through the new frozen adapter,
without changing the hash itself. All six affected tests then passed locally.
No public file changed in this fixture correction. The next exact candidate
still requires the complete hosted 495-test and 35-browser-suite gate.

The next hosted candidate passed all 495 unit/content checks. Its unchanged
normal-result pixel comparison exposed a fixture geometry mismatch: the old
script leaves the new optional picker hidden while the current script reveals
it above the result. Both captured results were 1044 by 925 pixels with the
same content; text and borders shifted by fractional-layout rounding. The
isolated result comparison now holds that optional surrounding control hidden
for both scripts. The exact pixel equality assertion remains intact. Separate
full-page journeys retain the visible picker at all four widths, including
keyboard actions and mobile/desktop screenshots. No public file changed in
this fixture correction. A new complete hosted gate is required.

PR #61 subsequently passed all 495 unit/content checks and all 35 browser
suites in run 38483859287. The two normal-result PNGs were byte-identical.
Six hosted example previews and desktop full-page sections were inspected.
The exact candidate tree `286e61fe97df417587bc497d17c59b1de616ccca` was merged
as `9ce47a41bad642dbabfdfa4d919350716fc0a6df`. Pages run 38484849045 succeeded;
published-byte job 115595898045 passed 399/399 targets and emitted the exact
merged SHA at 2026-10-13T23:33:04Z. Fresh main and Pages reads matched at
23:33:52Z. This next pass also confirmed that the repeated main Site checks
run 38484848731 completed successfully. Final receipt:
https://github.com/nolankido/nolankido.github.io/pull/61

## Find existing pages by the words in their addresses

The next user-directed pass began on October 14 UTC, October 13 in Hawaii,
from current main `9ce47a41bad642dbabfdfa4d919350716fc0a6df`. Main, repository
instructions, open pull requests and the completed CI/Pages runs were reread.
Only stale PR #48 was open; it remains untouched. Live `/find/` and its search
script matched current main exactly. No new sitemap submission or Search
Console request was needed so soon after the preceding read.

Two concrete misses were reproduced with the actual 151-page search index:
`AI time savings` returned no results, despite the existing calculator at
`/technology/ai-time-savings/`. `poker hand rankings` omitted the dedicated
`/poker/hand-rankings/` guide, whose editorial title is "Which hand wins?"
Both phrases are already present in the pages' descriptive canonical addresses.

Search now considers those existing local destination words as a secondary
signal. A full title/summary match retains its original score and ranks ahead
of an address-assisted match; a matching section still links to its actual
heading. Every non-stopword must match. No guessed synonym, fuzzy correction,
external URL, query parameter, fragment, private input or hidden answer is
added to the index. The scope explanation now mentions page addresses.
The same result link supplies the words, so no extra index or data file is
needed. Filtering still happens locally without URL, network or storage changes.

An independent baseline was captured from production Git objects before edits.
The only generated change is `/find/`, covering its scope sentence and script
cache token. Among 343 source/asset/download files, only the search source's
scope sentence and existing search script change. All article prose, metadata,
dates, five feeds, sitemap, original URLs, contact and analytics remain exact.
A frozen three-path adapter reverses only three contextual script hunks, one
source-copy hunk and one cache token. Earlier golden hashes remain unchanged;
negative controls expose altered ranking, unexpected code and edited copy.

Three new unit checks passed locally: full preservation, the two real missed
destinations plus ranking/scope controls, and historical-adapter tamper
detection. The existing hosted search-section suite adds eight keyboard
search-to-page journeys at four widths, four filter/reset checks and two
missing/malformed section-data fallbacks. Existing section arrivals,
no-script browsing, privacy and accessibility checks remain required.
The complete local and hosted gate, preview review and final publication
receipt will be recorded on this pass's pull request after execution.

This is an on-site discovery repair, not evidence of an external search-ranking
increase. Google's people-first guidance supports useful, navigable content;
it does not establish a ranking gain from this change:
https://developers.google.com/search/docs/fundamentals/creating-helpful-content
Next useful work should follow actual reader/search evidence or approved
firsthand material. No new article or page was manufactured for this pass.

The local full run passed 498 tests in 260.550 seconds; hosted candidate
`3aedd20795f87815d707c735965103778aae1e95` also passed all 498 unit/content
checks. Its new browser filter test incorrectly assumed that the calculator
was a guide. The existing, unchanged index classifies it as collection/reference.
The fixture now verifies that both Essays and Guides exclude the calculator,
then that Collections & reference includes the exact destination. All prior
filter and destination assertions remain. No public file changed in this
test correction. The updated exact candidate still requires the full gate.

PR #62 subsequently passed all 498 unit/content checks and all 35 browser
suites in run 38490038389. Four hosted mobile/desktop search-arrival previews
were inspected. Candidate `6e1a487a71fbebddc4e5ff8ac7e9ac31db85f145`, with tree
`0d97f16a7ccca62ab0b50c20813c85d498562c0e`, was merged as
`2a853aa0dcf14171855008f4f94808b483421bba`. Pages run 38490962170 succeeded;
published-byte job 115615771787 passed 399/399 targets and emitted the exact
merged SHA at 2026-10-14T00:35:22Z. Fresh main and Pages reads matched at
00:36:03Z. This next pass confirmed that the repeated main Site checks run
38490962277 also completed successfully. Final receipt:
https://github.com/nolankido/nolankido.github.io/pull/62

## Describe seven foundational poker guides clearly in search

A fresh user request continued this work on October 14 UTC, October 13 in
Hawaii. The pass began from current main
`2a853aa0dcf14171855008f4f94808b483421bba`. Repository instructions, open pull
requests, the maintenance record and current CI/Pages evidence were reread.
Only stale PR #48 was open; it remains untouched. The preceding release's
exact published-byte receipt covers this starting tree. Direct live reads
from this session were unavailable through the managed network and web
reader, so the existing hosted published-byte check remains the release
verification path. No additional Search Console request or sitemap submission
was needed.

Several foundational viewer guides had accurate but ambiguous search titles,
such as "Which hand wins?", "What the percentages mean" and "Why does the
seat matter?". Each guide's actual source and examples were inspected before
selecting a clearer topic label. This is a metadata-only correction of that
entry-point ambiguity, not a rewrite or new publication of the lessons.

| Existing URL | Search and sharing title |
| --- | --- |
| `/poker/holdem-basics/` | Texas Hold'em Rules: Deal to Showdown \| Nolan Kido |
| `/poker/hand-rankings/` | Poker Hand Rankings: Which Hand Wins? \| Nolan Kido |
| `/poker/betting-and-pots/` | Poker Betting: Calls, Raises and Side Pots \| Nolan Kido |
| `/poker/tournaments/` | How Poker Tournaments Work: Blinds and Payouts \| Nolan Kido |
| `/poker/poker-math/` | Poker Math: Pot Odds, Outs and Equity \| Nolan Kido |
| `/poker/position-and-stacks/` | Poker Position, Effective Stacks and SPR \| Nolan Kido |
| `/poker/reading-the-board/` | Reading a Poker Board: Suits, Pairs and Draws \| Nolan Kido |

The only production source edits are seven `seo_title` fields in the existing
manifest. The existing renderer carries them to the title element, Open Graph,
Twitter title and structured-data name on those seven pages. Original visible
headings, Article headlines, descriptions, authorship, publication and update
dates, URLs, canonical tags, sharing graphics, all five feeds and sitemap remain
exact. No body copy, source article, asset, download, runtime, dependency,
tracking or hosting configuration changes.

An independent baseline was captured from the starting production Git objects
before edits: 198 generated outputs, 343 source/asset/download files, the full
page manifest and all 171 page-body hashes. A frozen adapter reverses only the
seven reviewed metadata values at their exact paths and field contexts. Older
golden hashes remain unchanged. New tests independently compare every raw
page body, constrain all other manifest fields and expose altered titles,
article copy, dates, URLs and metadata on the wrong path. All three focused
tests, the deterministic build check, 171-page HTML5 validation and the search
audit passed locally. The complete regression gate and publication evidence
will be recorded on this pass's pull request after execution.

Google's title-link guidance recommends concise, descriptive titles and notes
that its displayed title may come from other page signals. This pass makes
existing subject matter easier to recognize; it does not establish improved
rankings, indexing or traffic, or promise that a search engine will show the
exact supplied title:
https://developers.google.com/search/docs/appearance/title-link

Next useful work: allow the existing search changes to be recrawled, then use
actual query/page evidence or reader feedback to select a substantive next
improvement. Do not add articles, credentials or promotional claims merely to
increase apparent site size.
