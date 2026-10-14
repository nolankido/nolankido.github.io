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

PR #63 passed all 501 unit/content checks and all 35 browser suites in run
38492412754. Two hosted 390/1440-pixel search previews were inspected. The
reviewed candidate `ada76094ad94886c7f49eaefb454006e808371b7` and merged main
`d042c29288067e170a07e169310ec94d85af86ba` share tree
`af9318a385418bc14d31b1b6d00b420a9dda6f5a`. Pages run 38493473212 succeeded;
published-byte job 115623830028 passed 399/399 targets, including all seven
changed pages, and emitted the exact merged SHA at 2026-10-14T01:03:05Z. A
fresh main read matched at 01:03:55Z. This next pass also confirmed that the
repeated main Site checks run 38493473573 completed successfully. Receipt:
https://github.com/nolankido/nolankido.github.io/pull/63

## Connect Technology search arrivals to the complete existing hub

Another fresh user request continued work on October 14 UTC, October 13 in
Hawaii. Current main `d042c29288067e170a07e169310ec94d85af86ba`, repository
instructions, open pull requests, recent CI/Pages evidence and this record
were reread. Only stale PR #48 remained open; it was left untouched. No new
Search Console request or sitemap submission was necessary. Direct live
reads remain unavailable in this managed session; the existing hosted
published-byte workflow provides the release check.

The Technology hub's search title and description describe its four-stage
workflow, but its opening action row had no link to that workflow. Its first
button went straight to the brief builder, and the checking-guides section
also lacked an opening jump link. The underlying material and all four
workflow stages were already present and useful.

The opening row is now one named, native navigation region with four choices,
in the same order as the page: follow the four-step workflow, try tools and
inspect a recorded case, choose an everyday task, or read checking guides.
The existing contact invitation remains immediately below it. This aligns
arrival choices with the existing search promise and makes the whole hub
easier to scan without adding another article or tool.

Only `_source/technology/home.html` and its generated Technology page change
publicly. There is no new CSS, runtime script, dependency, route, storage,
tracking or hosting behavior. All original article sources, prose, metadata,
dates, feeds, worksheets and preview images remain exact. The previous
seven-title release is retained exactly. The complete four-stage path and
its workbook are unchanged.

An independent baseline captured 198 generated outputs, 343 source/asset/
download files and the current manifest digest from production Git before
edits. A frozen two-path adapter reverses only the exact reviewed navigation
block. Every prior golden hash remains unchanged, and negative controls
expose changed labels, foreign destinations, unrelated copy or contact links.
Three focused local tests passed. The existing hosted practical-path suite
adds 32 keyboard jump-and-continue journeys across four widths, with and
without JavaScript, plus mobile and desktop opening-navigation previews.
The complete local and hosted regression gates and final publication receipt
will be recorded on this pass's pull request after execution.

The initial candidate passed all 504 local and hosted unit/content checks,
and its 32 new hosted keyboard journeys passed. An inherited font-parity
fixture reverted later content changes only in its reference page, so it
incorrectly compared old navigation with the new navigation. The browser
reference now changes font delivery alone. Exact geometry, font bytes,
loaded-state and blocked-font checks remain intact. A new test verifies that
the reference preserves all 171 current page bodies and changes only the
reviewed font head fragment. The complete gate is rerun on the repaired
candidate before publication.

This is a reader navigation improvement for an existing search entry page.
No ranking, traffic or indexing gain is claimed. Google's helpful-content
and page-experience guidance supports making the actual purpose useful and
understandable; it does not establish a measured search benefit from these
links:
https://developers.google.com/search/docs/fundamentals/creating-helpful-content

Next useful work should follow actual reader/search evidence or approved
firsthand material, rather than expanding the site merely to add pages.

PR #64 completed on October 14 UTC, October 13 in Hawaii. The repaired
candidate `7603408ea9d7b551b4aab2a0471aceb101f7b7e9` passed all 505 local tests
and the full hosted gate, including all 35 browser suites, in run
38495579345. The 32 entry journeys passed; both final hosted opening previews
matched the inspected previews byte for byte. Merged main
`4fd2f3bce66ccc44f003887193f2430635e46174` retained the exact reviewed tree
`141fb3203492961ad06771299167b70ecd1cb80c`. Pages run 38496575095 succeeded,
and published-byte job 115633593388 passed 399/399 targets and emitted the
exact merged SHA at 2026-10-14T01:36:30Z. Fresh main matched at 01:37:05Z.
Receipt: https://github.com/nolankido/nolankido.github.io/pull/64

## Name the existing poker study tools clearly in search

A fresh request continued website improvement after PR #64. Current main,
the editorial guide, recent CI/Pages results, open pull requests and this
record were checked. Only stale PR #48 remained open and was left untouched.
No Search Console request or unchanged sitemap resubmission was necessary.

The existing calculators and three fictional Decision Labs are useful study
destinations, but their search titles mostly described scenes rather than
the subject. For example, "Three all-ins. Two pots" did not name its side-pot
exercise, and the calculator title did not identify the calculations. Five
search labels now name the actual material: pot-odds, bluff and pot-limit
calculators; the Decision Labs collection; river pot odds and ranges;
flushes and redraws; and side-pot all-ins and refunds.

Only five `seo_title` fields and the corresponding generated head labels
change publicly. HTML title, Open Graph title, Twitter title and WebPage or
Article name agree. Original visible titles, page bodies, article headlines,
dates, authorship, descriptions, URLs, schemas' other properties and preview
images remain unchanged. The calculator is still a scoped accounting tool,
and the labs remain fictional after-play exercises. No strategy, outcome,
credential or search-performance claim was added.

An independent pre-edit baseline was captured from production Git objects:
198 outputs, 343 source/asset/download files, all manifest records and 171
page-body hashes. A frozen adapter reverses only the five exact head labels
and exact manifest patches. Previous golden hashes are retained. Negative
controls expose unreviewed labels, dates, prose, moved URLs and changed
identity. The new body-hash proof compares all 171 page bodies directly,
without any historical adapter. All five feeds and all asset/download bytes
are unchanged.

Three focused title tests and the six preceding title/navigation tests
passed locally. The existing search-entry browser suite adds 20 arrivals
covering all five destinations at 390 and 1440 pixels, with and without
JavaScript. These verify title, sharing labels, original heading, canonical
URL and reflow. Existing calculator arithmetic and Decision Lab interaction
checks remain in the complete gate. Final local, hosted and publication
evidence will be recorded on the pull request after execution.

This makes the purpose of already published material easier to recognize.
Google recommends descriptive, concise title text but may choose a different
displayed title. No ranking, traffic or indexing gain is measured or promised:
https://developers.google.com/search/docs/appearance/title-link

Next useful work remains evidence-led: allow recrawling, use actual reader or
query feedback to select substantive improvements, and publish firsthand
material only when the owner supplies or approves it.


PR #65 completed on October 14 UTC, October 13 in Hawaii. Candidate
`a1ca7169633cd996759200a8bc0a897c63264e3c` passed all 508 local and hosted
unit/content checks and the complete 35-suite browser gate in run
38497342635. Its 20 new title arrivals and the existing interaction checks
passed. Merged main `2ed0590205d4da419fe6fa5543149894ac6b98e8` retained reviewed
tree `70848838e4ba15ed475a3e7f17ce510751173847`. Pages run 38498497798 succeeded,
and published-byte job 115639628297 passed 399/399 targets and emitted that
exact merged SHA at 2026-10-14T01:58:25Z. Fresh main matched at 01:58:50Z.
Receipt: https://github.com/nolankido/nolankido.github.io/pull/65

## Find pages by their existing descriptive public titles

A fresh request continued improvement after PR #65. The current main,
editorial guide, maintenance record, recent CI/Pages results and open pull
requests were checked again. Only stale PR #48 remained open and was left
untouched. A fresh three-page crawl of Home, About and Technology returned
HTTP 200, self-canonicals, indexable directives, single main headings and
structured data, with no major audit issues. A low-priority description
length heuristic did not justify changing accurate copy. Search Console
returned no page/query rows for September 14 through October 11, 2026; that
absence is not evidence of zero traffic or indexing. No sitemap was
resubmitted.

A real search defect was reproduced locally against production: searching
for "pot odds calculator" missed the calculator, "Texas Holdem rules" missed
the rules guide, and "AI assisted reflection prompts" missed the reflection
guide. Each phrase is supported by that destination's already published
search/browser title. The local index previously omitted those titles.

The index now includes the exact public descriptive title of each of its
151 existing pages as escaped metadata on the existing result card. The
runtime uses those words to recover previously missed pages and relevant
individual sections. Existing headline/summary matches and address matches
retain their scores; newly recovered descriptive-title matches rank between
those two tiers. All words must still match one destination, and unrelated
section headings cannot be combined into an invented match. The visible
cards, headings, summaries, dates, filters, routes and no-script index stay
unchanged. Search remains local, without query transport, storage or URL
persistence. No new content source, synonyms, tracking or request is added.

An independent pre-edit baseline was verified against production Git
objects: 198 outputs, 343 source/asset/download files, all manifest records
and 171 page-body hashes. Only the generated Find page and its existing
runtime change publicly. Every other body is compared directly without an
adapter; all original source records, five feeds, asset bytes other than
the Find runtime, and downloads remain exact. Frozen complete card-opening
attributes, exact runtime patches and one cache token support the older
preservation checks. Negative controls expose unreviewed titles, prose,
URLs and ranking logic. Previous golden hashes were retained.

Four focused regression/preservation tests and the preceding three study
title tests passed locally. The existing browser suite now covers all three
missed queries under its no-query-network assertion and adds six real
keyboard arrivals at 390 and 1440 pixels, checking destination title,
original heading, reflow and private-query reset on browser history return.
The complete local/hosted gate, inspected previews and exact publication
receipt will be recorded on the pull request after execution.

This repairs discoverability inside the site. The crawl shows technical
accessibility to a crawler, not actual Google indexing or improved search
rankings. No ranking or traffic gain is claimed. Next useful work remains
actual search or reader feedback and owner-approved firsthand evidence,
rather than extra pages or speculative search keywords.

The first candidate passed all 512 local and hosted unit/content checks and
the new search journeys in the hosted reader-tools group. Its full-page
captures showed a sticky-header capture artifact, so the final candidate
uses actual viewport captures and explicitly checks heading clearance for
each of the six new search arrivals. The complete gate is rerun on that
exact candidate before publication; a first-candidate pass is not used as
the final release gate.

PR #66 closure: final candidate 5806816dd4c39c319c9cf59bb0c9996a586b4a35,
with tree f8293fb03236123605534f492d4f8fe825d744ea, passed all 512 local
and hosted unit/content checks and all 35 browser suites in run 38507411666.
The six new keyboard arrivals and history resets passed at 390 and 1440
pixels. Both viewport previews were inspected. Main merged as
000477a0684ad1be87615d1b275bdac546fe323d on October 14, 2026. Pages run
38508171212 succeeded; published-byte job 115670345995 verified 399/399
targets and that exact merged SHA. Fresh main matched, and the subsequent
main CI run 38508171447 also completed successfully. Publication receipt:
https://github.com/nolankido/nolankido.github.io/pull/66

## Beginner poker: practice the decisions before calculating percentages

A new owner request specifically authorized more detailed beginner poker
content and its publication. Current main, repository instructions, the
maintenance record, open pull requests and recent deployment results were
read again. Only stale PR #48 remained open and was left untouched.

The existing rules and rankings references were useful, but the free study
path moved quickly from a hand walkthrough to pot odds, while the practice
room opened with calculations and more advanced concepts. A complete
beginner needed a bridge: recognizing the choices, following the action,
counting the amount owed and finding the best five cards before studying
whether a decision was strategically good.

The new /poker/first-decisions/ guide supplies eight short lessons and twelve
native answer-reveal exercises. It covers card notation and starting-hand
vulnerabilities, check/call/bet/raise distinctions, positions and heads-up
order, the big blind's option, current-street call amounts, minimum full
raises, action returning after a raise, kickers, using one or zero private
cards, and a complete four-player practice hand. Each answer explains the
mistake it is intended to catch. The final hand accounts for all 400
fictional counters and distinguishes the pot won from the winner's net gain.

Every scene is explicitly fictional and can be practiced with a deck or
counters. No playing account, purchase or wager is needed. It does not
prescribe a starting-hand range or optimal betting line, imply solver
analysis, describe Nolan's recorded results or promise profitable play.
The guide identifies AI assistance and directs readers to the appropriate
existing next lesson and safer-play support. Rules were checked against
PokerStars' hold'em and hand-ranking references and the current Poker TDA
rules on October 14, 2026. A separate read-only content review found no
remaining blocking rule or clarity issues after corrections.

The Poker homepage's beginner card and Learn topic now open this guide.
One clearly labeled navigation aside links it from the original free study
path. Library and search catalogs, the author archive, feeds and sitemap
include the new article through their existing generators. A new title
preview uses the established typographic design. No new runtime script,
tracking, form or third-party dependency was added. Original routes,
contact behavior, domain settings and hosting remain unchanged.

Preservation evidence starts from main 000477a0684ad1be87615d1b275bdac546fe323d:
171 manifest records, 198 outputs and 343 source/asset/download files were
captured and verified against Git objects before editing. The new tests
retain every old page record and compare all original article source bytes
independently. The only article-source insertion is the exact navigation
aside, which is removed literally for comparison; the homepage change is
one exact beginner card. Original library entries, social preview records
and every field of all existing feed items remain exact. Only the new Poker
and combined-feed article entries are added. Existing assets and downloads
are byte-identical. Frozen full-file digest checks and exact-offset edits
provide the older tests with their predecessor view; prior golden digests
were not refreshed. Negative controls expose unreviewed copy or metadata.

Eight new unit/content checks cover inventory, original-content preservation,
feed identity, all twelve native answers, card names, exhaustive best-five
comparisons, chip conservation, discovery and tamper detection. The new
hosted browser suite covers closed and open answers and increased text
spacing at 320, 390, 768 and 1440 pixels; keyboard operation of every answer;
six real discovery arrivals; no-JavaScript reading; and accessibility audits.
The existing complete gate remains required, now with 36 browser suites.
Exact candidate, executed final gate, inspected previews, Pages deployment
and published-byte results will be recorded in the pull request receipt.

This is a substantive beginner learning addition, not evidence of improved
Google rankings or indexing. Next useful work is real beginner feedback on
which questions remain confusing, then a similarly careful lesson on
starting-hand decisions with explicitly bounded situations. Avoid presenting
an unvalidated universal chart or adding repetitive pages just for volume.

The first candidate, acd2cfca92e68c04b6d2e78e27ee5fd06fc218fc, passed all
520 unit/content checks locally (290.270 seconds) and on GitHub (199.408
seconds). Build, HTML and technical search checks passed. The Poker browser
group passed all 48 answer disclosures across four widths, six discovery
arrivals, no-script operation, and two accessibility audits with no detected
violations. The two opening previews were inspected. Visual review caught
a test-capture issue: the answer viewport was recorded before smooth
scrolling finished. The final candidate waits for fonts, uses an immediate
capture scroll and asserts that the answer is in the viewport and clear of
the sticky header. This changes only the test capture, not public content.
The full gate runs again on that exact candidate before merging; initial
passes do not substitute for final-candidate verification. Final receipt:
https://github.com/nolankido/nolankido.github.io/pull/67

## October 14, 2026: beginner preflop context

The preceding first-decisions release is complete. PR #67 merged as
3ec5f4adf06a232166e8d3c03b9a9be67bee7628 with tree
4f2b8ca1a57846472dbe2c22b7396eb1d02b6a2e. The exact final candidate
2e78d2628e60402115f392c8ae6bd4f9c8de2cb8 passed 520 unit/content checks
and all 36 browser suites in run 38511513021. Four final opening/answer
previews at 390 and 1440 pixels were inspected. Pages run 38512417231
succeeded; published-byte job 115683687712 passed 401/401 targets with
LIVE_VERIFIED_COMMIT=3ec5f4adf06a232166e8d3c03b9a9be67bee7628. A fresh main
read matched, and the later main check run 38512417631 also completed
successfully. Its final receipt is https://github.com/nolankido/nolankido.github.io/pull/67.

The user then explicitly requested more detailed beginner poker material.
A current-content audit identified a useful gap between the first-decisions
mechanics lesson and the existing preflop-chart guide: reconstructing the
situation before trying to transfer a chart's answer.

The new /poker/starting-hand-decisions/ guide supplies 2,701 words, eight
native answer-reveal exercises and a private study-note template. It covers
hand features, players still to act, earlier action, the current call price,
future betting, big-blind depth, different effective stacks and hypothetical
future winnings. A complete final fictional cash-game scene combines those
inputs. This is original teaching material, not a universal range chart,
solver output, recorded Nolan hand or claim of profitable play. No wager,
account or purchase is required. AI assistance and source limits are visible.

A read-only editorial review checked the eight scenes and arithmetic.
Three precision fixes distinguish an open-raise from raising after a limp,
identify the final scene as a cash game, and explicitly leave chips for
future betting in the call-price example. References were checked October
14, 2026: PokerStars' starting-hand and position material and GTO Wizard's
Study Mode documentation. Commercial source charts and generic range
percentages were not copied as recommendations.

The Learn topic places this guide after first-decisions. Generated Read
next cards connect it from first-decisions and the free learning path.
The established catalogs add it to the library, Find, author archive,
Poker and combined feeds, and sitemap. Its social title card uses the
existing renderer. No new runtime script, form, tracking, dependency,
download, domain setting or hosting service was added.

Before editing, all 172 manifest records, 199 generated outputs and 345
source/asset/download files were captured and compared with production Git
objects at main 3ec5f4adf06a232166e8d3c03b9a9be67bee7628. All existing
article source files and page metadata remain exact, including the entire
first-decisions and free-learning-path prose. All prior assets and downloads
remain exact. Only four source catalogs change, with one new source file and
one new PNG. Independent tests compare every previous article source and
all old feed items directly. Whole-file digests and frozen offset edits
provide exact predecessor views for historical golden tests; no prior
golden digest was refreshed. Negative controls expose unrelated changes.

Seven new unit/content checks passed locally, including the eight exercise
contracts, call/stack arithmetic, all original-source preservation, feed
identity, new discovery and tamper detection. Build reproduction and HTML5
validation passed for all 173 pages. The technical search audit passed:
173 unique titles/descriptions, 92 articles and 168 sitemap URLs. Find grew
by 1,303 bytes, including 689 bytes of section data. The new preview is
9,245 bytes. These are delivery checks, not evidence of search ranking or
indexing changes.

The full existing gate remains required for the exact candidate. A new
hosted browser suite adds four-width reflow, all eight keyboard disclosures,
six discovery arrivals, no-JavaScript reading and accessibility audits,
bringing the suite count to 37. Hosted mobile and desktop opening/answer
previews, the final gate, Pages deployment and all 403 published targets
must be verified before claiming completion. The pull-request receipt will
record the exact commit, tree and executed results.

Next useful improvement: observe where real beginners hesitate in the first
two lessons, then teach a bounded postflop decision sequence using existing
board-reading and pot-odds material. Avoid adding another overlapping index
or claiming to be the best resource without user evidence.

The initial full local run executed 527 tests in 265.595 seconds; 524
passed and three fixture expectations needed correction. The original
first-decisions live-byte assertion now compares its complete current
output while its historical checks retain the exact predecessor view.
The old search-entry preservation count stays 90; it must not include the
new article. Current section discovery contains 937 headings, including
the new generated Read next heading. All three affected test files passed
when rerun. The complete 527-test hosted gate is still required on the
exact remote candidate, alongside every existing and new browser suite.


## October 14, 2026: first decisions after the flop

The preceding preflop release is complete. PR #68 merged as
7b0e99ef1a3af29d49a690581c3bf1bb200159af with tree
828895b4ce79fc8e4c1c5683cc881eb1722d8b10. Its exact candidate
1776203c247bc174c3608c6ea69456276bb053ae passed 527 unit/content checks
and all 37 browser suites in run 38514201502. Four mobile and desktop
opening/answer previews were inspected. Pages run 38515033504 succeeded,
and published-byte job 115691802302 passed 403/403 targets with
LIVE_VERIFIED_COMMIT=7b0e99ef1a3af29d49a690581c3bf1bb200159af. Fresh main
and tree reads matched; main CI run 38515034207 also succeeded. Final
receipt: https://github.com/nolankido/nolankido.github.io/pull/68.

The user again requested deeper beginner poker teaching. A fresh main,
open-PR and deployment review found no competing current work. Stale PR
#48 remains untouched. A content audit found a useful bridge between the
first two lessons and the existing board-reading and pot-odds references:
recognizing what changes after the flop before trying to select a strategy.

The new /poker/first-flop-decisions/ guide supplies 2,525 words, eight
native answer-reveal exercises and 30 accessible displayed cards. It
teaches made hands alongside draws, checking and continuation bets,
conditional betting purposes, open-ended and gutshot completions, a flush
losing to a full house, counterfeited two pair, separate street payments,
and a complete check-raise decision snapshot. Worked explanations name
both known facts and missing information. These are original fictional
examples with visible AI assistance and source limits, not Nolan's hands,
solver output, recommended ranges or claims of profitable play. Practice
requires no wager, account or purchase.

Primary references were checked October 14, 2026: PokerStars material on
the flop, outs, continuation bets, betting purposes and counterfeiting.
The references support terminology; generic operator strategy claims were
not copied into recommendations. A read-only editorial review checked all
eight scenes and found two wording ambiguities, both corrected before
publication preparation. Card comparisons were checked independently with
an exhaustive best-five evaluator. Both draw examples enumerate every one
of the 47 unseen next cards. Both accounting examples conserve chips and
separate the existing pot from the additional call.

The Learn topic now offers three ordered beginner lessons. Generated Read
next links connect the preflop lesson and free learning path to the new
guide, then point onward to board reading and betting purposes. Existing
catalogs add the guide to the library, both Find tools, author archive,
Poker and combined feeds, and sitemap. Its 8,841-byte social title card
uses the existing renderer. No runtime, stylesheet, form, tracking,
dependency, download, domain setting or hosting service was added.

Before editing, all 173 manifest records, 200 generated outputs and 347
source/asset/download files were captured and compared with production Git
objects at main 7b0e99ef1a3af29d49a690581c3bf1bb200159af. All prior
article source files and metadata are byte-identical, including both
beginner lessons and the free learning path. All prior assets, downloads
and feed items remain exact. Four source catalogs change, with one new
article source and one new PNG. Independent preservation assertions use
direct hashes, while historical golden checks use exact whole-file gates
and frozen offset reversals. No prior golden digest was replaced. Negative
controls expose unreviewed changes. Current inventory counts advance only
for the actual new guide and its discovery entries.

All 536 unit/content tests passed locally in 365.425 seconds, including
the nine new checks. Build reproduction passed for
201 generated files; HTML5 validation passed for all 174 pages. The search
audit passed with 174 unique titles/descriptions, 93 articles and 169
sitemap URLs. Find grew by 1,329 bytes, including 711 bytes of section data;
the section payload remains below its 60,000-byte limit at 57,630 bytes.
These checks do not establish indexing or search ranking changes.

The complete existing gate is required on the exact remote candidate.
The new hosted browser suite checks four widths, all eight answers from
the keyboard, six discovery arrivals, no-JavaScript reading and two
accessibility audits. This brings the totals to 536 unit/content tests
and 38 browser suites. Six mobile/desktop opening, card-example and answer
previews, Pages deployment, and all 405 published targets must be verified
before completion. The PR receipt will record the exact candidate and
merged trees, executed results and live-byte marker.

Next useful improvement: seek real beginner feedback on the three-lesson
sequence, then address specific hesitation points or build a bounded
first-session practice capstone. Preserve the deeper references instead
of adding another overlapping beginner index. No claim of being the best
resource or of improved rankings is made without supporting evidence.


## October 14, 2026: beginner turn and river interpretation

The preceding flop release is complete. PR #69 merged as
90466011ca43cfd4458a9a470aea9d8712b3cf77 with tree
016d7edb3e92c3848b3e05ac88cc2963c0deac7d. Its exact candidate
4bcdd0b10a11ceeeba443fe6c0e3d5f0308453bf passed 536 unit/content checks
and all 38 browser suites in run 38517815268. Six mobile and desktop
opening, card-example and answer previews were inspected. Pages run
38518793453 succeeded, and published-byte job 115703499744 passed 405/405
targets with LIVE_VERIFIED_COMMIT=90466011ca43cfd4458a9a470aea9d8712b3cf77.
A fresh main read matched. Main CI run 38518793719 subsequently passed
all of its build and browser jobs and aggregate checks job 115706344077.
Final receipt: https://github.com/nolankido/nolankido.github.io/pull/69.

The user requested another substantial beginner improvement. Current main,
open PRs, deployment and source material were reviewed. Stale PR #48 is
untouched, with no competing current work observed. A read-only editorial
audit found that a generic complete-hand capstone would repeat the existing
hold'em walkthrough, follow-along scenes and recent lessons. The more
useful gap was understanding what changes on the final street.

The new /poker/turn-and-river-decisions/ guide supplies 2,327 words, six
native answer-reveal exercises and 23 accessible displayed cards. A connected
pair-and-draw example teaches an overcard on the turn, a missed river draw
that retains a pair, and checking behind when no new community card remains.
A separate ace-high showdown demonstrates that missing a draw does not
mean having no showdown value. A river-call example separates catching a
bluff from making one. The final shared-straight example shows why zero
outright wins can coexist with 50% equity and a positive call value relative
to folding under explicitly limited assumptions.

The scenes are original fictional teaching material, not Nolan's hands,
solver output, recommendations of a range, or claims of profitable play.
AI assistance and source limits are visible. Practice requires no wager,
account or purchase. A review refined the definition of showdown value to
include sharing the pot. Every listed best-five ranking and all 990 legal
opposing holdings on the final straight board were independently checked.
The examples distinguish known cards from assumed opponent frequencies,
legal raises from a restricted call/fold comparison, and receiving chips
from full-hand profit. No sixth community card or guaranteed best action
is implied.

Primary references were read October 14, 2026: PokerStars' hold'em rules,
showdown explanation, bluff-catcher terminology and pot-odds lesson.
Only mechanics and terminology are used; generic strategy prescriptions
and unqualified approximations from the external pages are not adopted.

The new guide follows first-flop-decisions through generated Read next
navigation, then leads to the existing river Decision Lab and pot-odds
workshop. It is also in the Learn topic's full guide list, library, both
Find tools, author archive, Poker and combined feeds, and sitemap. The
existing three introductory topic steps remain exact. Its social title
card uses the existing renderer. No runtime, stylesheet, form, dependency,
tracking, download, domain setting or hosting service was added.

The production baseline at main 90466011ca43cfd4458a9a470aea9d8712b3cf77
was verified against Git objects before editing: 174 manifest records,
201 generated outputs and 349 source/asset/download files. All prior
article sources and metadata remain byte-identical, including the full
first-flop-decisions text. All prior assets, downloads and feed items are
preserved. Only four source catalogs change, with a new source and a new
PNG. Direct-hash preservation checks are independent of exact historical
adapters; no older golden digest was refreshed. The predecessor adapters
require exact whole-file hashes and frozen offset reversals, and negative
controls reject unrelated changes.

Nine new unit/content checks pass, including all 990 opposing hands and
fractional win/tie accounting. A copied negative-control inventory count
was corrected from 174 to 175, retaining the assertion that an unreviewed
page mutation must not be removed. The corrected test file passes all nine
checks. Build reproduction passes for 202 outputs. HTML5 and search checks
pass for 175 pages, 94 articles and 170 sitemap URLs, with distinct titles
and descriptions. Find grows by 1,198 bytes, including 577 bytes of section
data; that payload remains under 60,000 bytes at 58,207 bytes. The inspected
social preview is 8,466 bytes. These are delivery checks, not evidence of
indexing or ranking improvements.

The complete existing hosted gate remains required on the exact candidate:
545 unit/content tests and all 39 browser suites. The new browser suite
covers four widths, six keyboard answers at each width, five real discovery
arrivals, no-JavaScript reading and two accessibility audits. Six mobile and
desktop opening, card-example and answer previews must be inspected. Pages
deployment, all 407 published targets and a fresh main read are required
before completion. The PR receipt will record the exact tree and executed
release evidence.

Next useful step: obtain real beginner feedback on this connected sequence
and address specific confusion, particularly at hand comparison and the
transition from knowing a price to justifying an action. The site already
has complete-hand walkthroughs and deeper practice, so another generic
beginner index or quota-driven lesson would add less value.


The initial full local suite executed 545 tests in 304.696 seconds. It
loaded the earlier negative-control count before that count was corrected,
so 544 passed and that one assertion reported 175 versus 174. The corrected
file had already been rerun separately: all nine tests passed in 3.934
seconds. No public source, arithmetic or preservation failure was found.
The complete 545-test hosted gate is still required on the exact corrected
candidate, alongside every existing and new browser suite.


Candidate 6e46b614ff42715fe3b29f1cec7c49f5477db633 passed all 545
unit/content checks in 166.176 seconds on GitHub run 38520649756. The
new browser test then exposed a fixture assumption: this new lesson is in
the Learn topic's collapsed All guides panel, not its three visible first
steps. The test attempted to focus a hidden link without opening the panel.
The correction uses the keyboard to open that exact native disclosure,
asserts its list and destination link are visible, then retains the exact
arrival assertion. No public file changes. The complete existing gate must
run on the corrected candidate before merging.
Six initial mobile/desktop opening, card-example and answer previews were
inspected. Their layout is clear and the public files remain unchanged by
the fixture correction. The final candidate still needs its own full gate
and artifact verification before publication.

## October 14, 2026: a connected beginner study route

PR #70 completed the turn-and-river lesson at main
2dcf972a85ab3cf6c5e21539fe489805df5400b9, tree
cd8856ee03bdc47be9d4a876afdc6940b6874786. Final candidate
c64c93ce200e65b1641111a43e01b573b5b31ad2 passed all 545 unit/content
tests and all 39 browser suites in run 38521641061. The six final screenshots
were byte-identical to the six inspected initial mobile/desktop previews.
Pages run 38522834767 succeeded. Published-byte job 115716252234 passed
407/407 targets and emitted the exact main marker at 06:33:53 UTC. Main was
re-read successfully. Its duplicate full CI run 38522834829 subsequently
completed successfully. Receipt: https://github.com/nolankido/nolankido.github.io/pull/70.

The next user request renewed active improvement and publication authority.
Fresh main, open PRs, repository guidance and live-release results were read.
Only stale PR #48 was open; it remains untouched. The beginner collection
already had detailed mechanics, preflop, flop and final-street lessons. The
existing free learning path linked the first lesson but did not present all
four as a route with explicit goals, readiness checks or a way to keep one's
place. Improving that connection was more useful than another overlapping
article.

The existing /poker/free-poker-learning-path/ now has a four-lesson route
with 1,004 words of original teaching and guidance. Each lesson has a goal,
a skill to explain before moving on, a closed native readiness check, a
worked explanation and an exact repair link. Four checks address additional
call amounts, the blinds' remaining turns, a made pair plus an unfinished
flush draw, and a river price versus actual pot-share equity. The fictional
30/10 river ledger uses 10 / 50 = 20%; it states no fees, no side pots, enough
chips and a closing call. It does not claim that a price establishes the best
action or compare the call with every raise. The five-card example is
9-9-A-6-2, with four hearts, not a flush.

All four destination lessons receive an optional native path menu, ordered
links, a current-page marker without a self-link, a return to the route and
the same blank private study card. The Learn topic exposes a direct link to
the complete route while retaining its three existing starting steps. The
2,077-byte TXT card has four blank skill records and ordinary return URLs.
There is no stored progress, answer transport, account, new runtime
or dependency. One small stylesheet applies only to the four path menus. No new route, article or ranking claim is added.

The original five-session source and every previous article source remain
byte-identical. The route is a separate approved fragment inserted at its
existing study-plan anchor. All prior assets and downloads are exact. Only
two source catalogs change. One existing page's search title, description,
update date and revision are intentionally changed for this substantive
addition; its October 8 publication date remains exact. Other article
metadata remains exact. Only that page's description in the two relevant
feeds changes; item identities, publication dates and all other feed items
remain exact. The visible revision and machine-readable date agree. The
library reading estimate includes the new fragment.

The production baseline was checked against Git objects before editing:
175 page records, 202 generated outputs and 351 source/asset/download files.
The exact predecessor adapter requires a complete reviewed file digest and
frozen offsets; unrelated mutations stay visible. Direct preservation tests
bypass adapters, and negative controls reject altered amounts, current-page
labels and unsupported metadata. Old golden digests are retained. Existing
outline fixtures now include the actual decorated public body; the strict
search-section count advances by exactly one, from 957 to 958. Arrival tests
retain exact destinations and select the visible original forward links;
the new optional menus have their own browser coverage. The existing
collection checkpoint retains its exact selector despite four new checks.

Initial local verification ran all 554 tests in 303.983 seconds and exposed
four failures and one fixture error. The new revision was not yet visible;
that content defect was fixed. Two outline fixtures assumed only the old
source fragment, and one section count lacked the new heading. The new
hosting-preservation fixture assumed an absent .nojekyll file existed; it
now independently preserves the actual baseline presence or absence, with
no Git-history dependency in hosted tests. The corrected new nine checks
pass, along with all 26 tests across the four affected existing test files.
Build reproduction, HTML5 and search audits pass for 175 pages, 94 articles
and 170 sitemap URLs. The section-search payload is 58,283 bytes, below the
unchanged 60,000-byte limit. Primary hold'em and pot-odds references were
read October 14, 2026. No operator's broad strategy recommendations are
adopted.

The exact candidate must pass the full hosted gate of 554 unit/content tests
and all 40 browser suites before merge. New browser coverage includes the
four-width route, all readiness panels, current markers, actual forward and
return navigation, the exact study-card bytes, print, no-JavaScript reading,
privacy checks and mobile/desktop accessibility audits. Six hosted route,
answer and menu previews require inspection. Pages success, all 409 exact
published targets and a fresh main read remain required after merge. The
PR receipt will record executed release evidence and exact tree identity.

Next useful task: observe actual beginner use of this sequence, especially
whether readers can explain a call price and identify the missing evidence
for an action. Improve a demonstrated point of confusion rather than adding
another generic beginner index or claiming comparative superiority.

Initial candidate a3366b74f6a8e9fca64b13d6daffae009b322d2e passed all
554 unit/content tests in 156.795 seconds in run 38527141447. All existing
browser suites passed. The new suite passed the route, goals, four-width
reflow, keyboard answers, menus, JavaScript-enabled navigation, exact
download, print and privacy checks, then timed out waiting for a no-script
mouse navigation to finish. The correction uses explicit keyboard
activation for that leg and retains the exact route and destination
assertions. No assertion is removed.

Six initial hosted previews were inspected. The desktop current-lesson
label sat too close to the summary focus outline because its shorter
span inherited a two-column list intended for links. A stylesheet scoped
to these four menus now keeps the numbered route in one column and aligns
the current label with the links. All previous stylesheets remain exact.
The corrected candidate still requires the complete gate, six final
previews, Pages and all 409 published targets before completion.

## October 14, 2026: a beginner introduction to ranges

PR #71 is published and verified at main
0caa7cd17a7b5381721fea59841c1542cc698b71, tree
9f3b1ada2c222a64be90659bb3d093dd96a24c58. Final candidate
512c90b9c2493947e9b806d90f9253dfa5444561 passed all 554 unit/content
tests and all 40 browser suites in run 38528360441. Four final route/answer
previews matched the inspected initial previews byte for byte; both corrected
menu previews were inspected. Pages 38529656209 succeeded. Published-byte
job 115738210159 passed all 409 targets and emitted the exact main marker
at 07:39:24 UTC. Fresh main and receipt reads matched. The duplicate full
main run 38529656766 subsequently passed all jobs. Receipt:
https://github.com/nolankido/nolankido.github.io/pull/71.

The user requested another beginner content improvement. Current main,
repository instructions, open PRs, recent CI, deployment and coverage were
read before editing. Stale PR #48 remains untouched. The existing range
references and combination workshop cover labels, blockers and weights,
but move quickly into group counts. The next useful bridge is a small
set of explicit two-card alternatives before the larger mathematical model.

The new /poker/ranges-for-beginners/ contains 2,254 words, six native
answer-reveal exercises and 15 accessible displayed cards. It separates
known cards, physically possible holdings and an assumed betting range.
One river board and four exact opposing holdings keep the comparison
small. It explains why checking does not expose a weak hand, why a known
card creates a physical exclusion, why one exact holding differs from a
broad hand label, and why a possible bluff is not a measured frequency.

All examples are fictional and visibly AI-assisted. On the unpaired final
board, the hero's K-K-Q-9-5 loses to the three stronger alternatives and
beats only the Q-J high-card alternative. A 40-chip pot and 20-chip river
bet produce a 60 current pot and 80 final pot after calling. Equal weights
give 25% equity and zero call value relative to folding. Giving the only
beaten alternative half weight instead gives 1/7 equity and -60/7 chips
relative to folding. Both models are explicitly invented and incomplete;
neither is claimed to describe an actual player, profitable strategy or
the best action among all legal choices. The lesson also explains why one
revealed hand cannot establish which frequency model was correct.

Primary introductions to ranges and pot odds were read October 14, 2026.
Their terminology is used, but broad prescriptions that checking excludes
strong hands, generic player percentages and specific strategy advice are
not adopted. The card comparisons and fractional arithmetic were checked
independently. No wager, account, purchase, personal result or solver
validation is implied.

The guide follows turn-and-river-decisions through generated Read next
navigation and leads to the existing combination workshop and river lab.
It is in the Learn topic's complete list, library, both Find tools, author
archive, feeds and sitemap. The four-lesson foundation route, current-page
menus, original five-session plan and private study card remain unchanged.
No new runtime, stylesheet, form, tracking, dependency or download is added.
The new 7,449-byte sharing preview is a typographic title card and was
inspected.

The production baseline was verified against Git objects before editing:
175 page records, 202 outputs and 354 source/asset/download files. Every
prior article source, metadata record, asset, download and existing feed
item remains exact. Only the four catalog files gain the new guide. Frozen
whole-file adapters reverse reviewed offsets only when the entire file
matches its reviewed digest. Independent direct hashes and negative
controls retain preservation evidence without refreshing old golden hashes.
The prior learning-path tests use that exact predecessor for historical
views and the current full manifest for their current library lookup.
Archive counters advance by exactly one article; all identity, order,
publication-date and destination assertions are retained.

All nine new tests passed locally in 3.488 seconds. The corrected nine
archive tests and nine learning-path tests also passed. The initial full
local run loaded old article, sharing, preview and search counters plus a
historical-manifest lookup before their corrections. Current counters
advance only by the actual new article and its generated section anchors.
The deterministic search-audit report was regenerated from the passing
audit. The full local result is recorded below when it finishes. Build reproduction, HTML5 and search audits pass for 176 pages,
95 articles and 171 sitemap URLs. The section payload is 58,892 bytes under
the unchanged 60,000-byte limit. No indexing or ranking result is inferred.

The exact candidate requires the complete hosted gate: 563 unit/content
tests and all 41 browser suites. The new browser suite covers four widths,
24 keyboard answer openings, five actual discovery arrivals, no-JavaScript
reading and two accessibility audits. Six hosted opening/card/answer
previews require inspection. Pages, all 411 published targets and a fresh
main read are required after merge. The PR receipt will identify the exact
reviewed tree and executed release evidence.

Next useful task: check actual beginner understanding of known cards versus
assumed frequencies. A correction based on a demonstrated misunderstanding
is more useful than another broad index, an unverified recommended range
or an unsupported claim to be the best resource online.

The initial full local run completed 563 tests in 375.620 seconds: seven
failures and one error. They were two archive counts (95 rather than 94),
the sharing count (97 rather than 96), preview eligibility (98 rather than
97), current Find-card count (156 rather than 155), section anchors (967
rather than 966), the old deterministic audit snapshot, and the library
lookup using a historical manifest against the current catalog. These
current-count fixtures and that lookup were corrected; exact ordering,
identity, destination, metadata escaping and all historical golden checks
remain in place. No card, arithmetic, source-preservation or public build
error was found. The complete hosted gate remains required on the final
candidate after these corrections.
All 59 tests across the seven affected existing test files passed after
correction, in addition to the nine new range tests. The final hosted gate
will execute all 563 tests together on the exact candidate.
