# Nolan Kido personal website

A small static website for introductions, selected writing, and practical resources. GitHub Pages serves committed HTML. There is no runtime application server or database. Optional, cookie-free Umami Cloud pageview analytics is installed through the shared layout; the site works when analytics is blocked. See `ANALYTICS.md`.

## Beginner Poker course

Lesson 2 includes native six-seat maps for its worked and changed situations.
Their `table` records in `_source/poker/course-lessons.json` hold the current
seat, round payments and folds. `_scripts/poker_lessons.py` renders those same
records as clockwise seat lists and conditional flop-order comparisons. Keep
the changed comparison inside its closed answer. These are bounded six-player
preflop examples, with 100 starting counters and 1/2 blinds, without all-ins.
See `_reports/position-maps-learning-review.md` and `test_position_maps.py`;
`poker_course_browser.py` covers narrow layouts, enlarged text, print and
script-free use. The original study-card prompts remain unchanged.

The overview puts the six-lesson route and finish before the optional practice
tools. `_scripts/poker_beginner_path.py` owns that order and the three-tool menu.
`poker_course.entry` moves the source's existing start controls under the course
title. Keep one source control row and one title so the build can check the move.
Card basics provide a direct lesson-1 continuation before the extra exercises.
All practice anchors remain available. See `_reports/course-entrance-review.md`;
`test_course_route.py` and `learning_path_browser.py` check the core and optional
journeys without adding learner tracking or saved progress.

The course finish now connects its six skills across two complete fictional
hands at `/poker/beginner-checkpoint/#course-hand`. The later streets, feedback
and results use closed native disclosures. `_source/poker/final-hands.json`
owns the cards, ledgers and eight open prompts; `_scripts/poker_final_hands.py`
renders both the page and the prompts in the existing six-stage study card.
Keep results separate from decision quality and do not turn unspecified ranges
into action grades. Run `test_final_hands.py`; `checkpoint_browser.py` also
checks both hands, paper parity and script-free use. See
`_reports/connected-final-hands-review.md` for the learning audit and its limits.

The public entry is now **Poker Foundations**, at the existing
`/poker/free-poker-learning-path/` URL. Poker home leads with the free course;
its compact syllabus uses the same lesson data as the six core lessons.
The shared Poker bar links to the course and identifies its lessons and practice
pages as the current section. Outcomes, starting choices and the finish guide
are explained in `_reports/free-poker-foundations-concept.md`.

Each of the six lessons starts with a native short lesson: one idea, a worked
example, an open explanation task and its answer with a precise repair link.
`_source/poker/course-lessons.json` owns these examples; `_scripts/poker_lessons.py`
validates and renders them through the existing course module. Full articles
remain below, with the same section targets. No new JavaScript or saved progress
is used. The study card includes the six changed prompts without answers. See
`_reports/short-course-lessons-review.md` and `test_short_lessons.py`; the existing
`poker_course_browser.py` also checks the complete short-lesson journey.

The course also includes a branching betting rehearsal. Three starting ledgers
live in `_source/poker/round-practice.json`; `_scripts/poker_round_practice.py`
renders native tables and worked lines, while `assets/poker-round-practice.js`
tracks full raises, pending turns and uncalled returns. Its bounded model omits
stack limits and short all-ins. Do not turn accepted moves into strategy grades.
Run `test_round_practice.py` and `round_practice_browser.py`; the audit is in
`_reports/betting-rehearsal-learning-review.md`. The exact prior release is pinned
in the new baseline and reversed only by its SHA-bound history adapter.

The free course begins with card foundations and a constructive best-five lab.
`_source/poker/hand-lab.json` owns one worked selection and ten fixed exercises;
`_scripts/poker_hand_lab.py` renders the native version and reuses the published
ranking chart. `assets/poker-hand-lab.js` checks any five-card selection, including
equally strong alternatives, without sending or storing answers. Run
`test_hand_lab.py` and `hand_lab_browser.py` with the ordinary release gate. The
unit suite includes independent Python oracles and complete five-card category
enumeration. See `_reports/card-foundations-learning-review.md` for the audit.

`/poker/beginner-practice/` is the supporting practice utility. Its six short
models and eighteen questions live in `_source/poker/beginner-practice.json`;
`_scripts/poker_practice.py` validates and renders the native version. Keep the
three fixed mixed sets transparent and verify every changed card or counter
example independently. The optional script hides choices until requested,
supports uncertainty, and retains mistakes in the current visit's review after a
corrected retry. It sends and stores no answers. Run `test_poker_practice.py` and
`poker_practice_browser.py` alongside the ordinary release gate. See
`_reports/beginner-practice-learning-review.md` for the learning audit and limits.

`_source/poker/beginner-course.json` owns the six-stage order, first-pass section
links, recall prompts, specific checkpoint targets and six-scene fictional hand.
`_scripts/poker_course.py` validates those destinations and cards, decorates the
existing lessons and generates `downloads/poker-beginner-study-card.txt` plus its
exact preview. Edit the configuration and rebuild rather than editing the TXT.
`assets/poker-course.js` adds optional per-scene practice on the course overview;
it has no network or storage API. Native answers and the full sequence work when
the script is blocked. Keep search scene anchors stable and exclude answer panels.

Run `python -m unittest discover -s _tests -p test_poker_course.py -v` and
`python _tests/poker_course_browser.py` for focused verification, then the normal
release gate. The independent hand oracle checks accounting and ranks, not
optimal strategy. See `_reports/free-poker-learning-path-review.md` for the
beginner-task audit, research basis and limits of the evaluation.

## Site architecture

The homepage introduces Nolan first, links three public AI projects and three
use/inspect/understand choices, then opens the four subject libraries in their established order:
Technology, Living Well, Poker, Creative Work. `/start-here/` is the cross-site
orientation page. It is available in the shared utility bar on every page.
The introduction remains curated rather than chronological. Each project links
to its permanent case page and the available evidence.

`_source/identity.json` owns the primary navigation and three curated reading
choices, plus four cross-subject reading routes on `/notes/` (Writing). The five
original general notes and all feed scopes are retained. No article is moved or
republished when it is featured. `_scripts/identity.py` validates their destinations against the complete
public manifest and renders the canonical titles. Existing content stays at its
original URL. Shared biographies come from `_source/site.json`. Change the
identity configuration deliberately rather than promoting whichever library
happens to have the most recent content expansion.

## Edit and publish

Use Python 3.10 or later. Public page bodies are in `_source/`; shared markup is in `_source/layout.html`; routes, descriptions, and explicit dates are in `_source/pages.json`. `_source/selection.json` controls featured reading independently of publication order. Shared approved identity and the existing contact endpoint are in `_source/site.json`.

```sh
python _scripts/build.py
python _scripts/build.py --check
python -m unittest discover -s _tests -p "test_*.py" -v
python -m http.server 8000
```

Open `http://localhost:8000` for a local preview. Commit source and generated output together. Do not edit generated HTML directly. The build also generates RSS, sitemap, and the minimal contact card. New notes need both a manifest entry and a reading-order entry. Publication dates are explicit; substantive revisions use `updated` and `revision` rather than resetting publication dates. Changed contact JS and supporting CSS automatically get content-derived cache versions.

## Design and content

The approved editorial design remains in `styles.css`. Functional state, focus, reflow, print, and accessibility adjustments are in `assets/site.css`. The contact script is separate in `assets/contact.js`. Preserve the form contract and accessibility when editing the design. See `DESIGN_HANDOFF.md`, `DESIGN_IMPLEMENTATION.md`, and `EDITORIAL_GUIDE.md`.

Blank resources live in `downloads/`, completed fictional examples in `_source/examples/`, and intended-use guidance in `_scripts/catalog.py`. The preview and download use the same blank file. Never add private worksheet answers, unpublished drafts, credentials, or private records to this public repository. Excluded or unlinked source files are still public in GitHub.

## Tests

The dependency-free suite checks output determinism, metadata, links, fragments, dates, feeds, examples, reviewed assets, and the live-checker's simulated responses. Browser suites use blocked external traffic or mocked form services and never deliberately submit a real message.

```sh
python -m pip install -r requirements-test.txt
python -m playwright install chromium
python _tests/browser.py
python _tests/design_browser.py
```

Set `CHROMIUM_PATH` to use an installed Chromium binary. Set `SCREENSHOT_DIR` outside the repository for optional screenshots. The HTTP design suite verifies the three real font families from local files. The dedicated font suite also checks readable fallbacks when those files fail.

The comprehensive audit additionally uses axe-core. Install it outside the repository:

```sh
npm install --prefix /tmp/nk-qa --no-audit --no-fund axe-core@4.10.3
AXE_PATH=/tmp/nk-qa/node_modules/axe-core/axe.min.js python _tests/review_browser.py
```

For Windows, choose a temporary folder and set the `AXE_PATH` environment variable to its `node_modules/axe-core/axe.min.js` file. The audit checks HTML5 parsing, seven viewport widths, user text-spacing overrides, automated accessibility, and additional contact recovery failures. `--report-only` is for diagnosis, not a passing release gate. Inconclusive automated checks are reported for human review; passing automation is not an accessibility certification.

## Contact boundaries

Only name, email, and message are required; topic (`reason`) and context are optional. Keep all form IDs, the existing Formspark endpoint, and the public Turnstile site key. The provider must separately validate verification tokens with its secret setting. Never put that secret here.

Verification failures must offer a usable retry. Failed or ambiguous submissions preserve text in the open form but not in browser storage. The form never resubmits automatically. Network/server errors do not establish non-delivery; a retry may duplicate a submission. The success screen confirms service acceptance, not inbox arrival or that a message was read. Actual inbox delivery and provider configuration require a separate authorized live test.

Provider references:
- https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/
- https://documentation.formspark.io/examples/ajax.html

## Release verification

Check the current main head before merging, run the tests, and retain the existing branch-based Pages configuration. The `Site checks` workflow uses read-only permissions and does not modify code or hosting settings. On main-branch pushes it runs a bounded public-byte check after local tests, allowing time for Pages propagation. Pull-request checks never query a release as though it were deployed. Superseded commits defer to the newer release's check.

```sh
python _scripts/check_live.py --attempts 10 --interval 10
```

The live verifier makes GET requests to nolankido.com only. It checks public pages, assets, downloads, the custom 404, and excluded source paths. It does not send form messages. A successful build or artifact upload is not a completed deployment: check Pages job status as well as the live bytes. If the bounded live check times out during a provider delay, inspect the deployment before retrying; do not automatically rewrite or roll back working code.

See `SITE_REVIEW.md` for the October 5 review, reproduced failures, repairs, and remaining limits. The original design stylesheet was kept intact; the contact logic and functional CSS now include the tested repairs. Revert faulty changes rather than rewriting history.

### Search-engine change notifications

After a main-branch release passes the public-response check, the workflow uses
`_scripts/submit_indexnow.py` to notify IndexNow about meaningful changes between
the push's actual before/after commits. The script selects canonical sitemap URLs,
verifies the current main commit and deployed public bytes, and checks the root
ownership file before sending public URLs to the fixed IndexNow endpoint.
It does not submit unchanged pages or visitor data. Without `--submit`, it makes
no network requests and prints the proposed change list for two full commit IDs.

The notification receipt is retained as an Actions artifact for 30 days.
HTTP 200 means the URLs were received; HTTP 202 means receipt with key validation
pending. Neither proves indexing, ranking, or AI citations. A failed notification
produces a separate warning while preserving the successful publication receipt.
Inspect the reason and any requested retry delay before making a bounded retry.
See `_reports/visibility-sprint/discovery-follow-up.md` for scope and protocol sources.

## Technology-first subject hierarchy

Technology remains the first subject, followed by Living Well, Poker, and
Creative Work. The personal introduction sits above all four. The technology
hub connects trust checks to practical everyday guides, without duplicating
articles or presenting proposed experiments as completed evidence. The live
checker derives page coverage from the complete manifest, including Start here.

## Poker publishing

See `POKER_PUBLISHING.md` for the approved-content workflow, private draft helper,
episode companions, hand reviews, chapter links, and Poker feed. The main landing
page remains the Technology-first baseline. Run `python _tests/poker_browser.py`
for the temporary-fixture publishing and reader-flow checks.

## Poker viewer library

The beginner directory is `/poker/start-here/#viewer-library`. See
`VIEWER_LIBRARY_RELEASE.md` for the seven new guides, the downloadable reference,
and the regression coverage. Keep new viewer explanations separate from actual
episode records, and preserve existing viewer-guide anchors when editing.

## Follow-on viewer guides

The Poker viewer library now includes three reading routes and six further guides
on positions/stacks, board texture, ranges/bets, event formats, table context and
worked viewing scenes. See `VIEWER_NEXT_RELEASE.md`. The directory, links, examples
and download are covered by the existing CI suite and `test_viewer_next.py`.
No changes to the Technology-first landing page are part of this release.

## After-play workshops

The Poker study desk now connects seven substantial workshops, twelve self-check
exercises and four new private-use worksheets. See `POKER_WORKSHOPS_RELEASE.md`.
All examples are fictional and the existing publishing approval workflow remains
in place. Run `python _tests/workshops_browser.py` for the targeted disclosure and
reading-flow checks. The Technology-first gateway and Umami configuration are
unchanged.

## Poker subject architecture

The Poker homepage and guide library share four reader paths and a curated
in-depth shelf from `_source/poker/reading-routes.json`. `_scripts/poker_discovery.py`
validates every destination against the published guide library and uses its
current titles and reading estimates. Edit that configuration to change the
selection; do not maintain a second copy of article titles or durations. The full
guide catalogue retains its own order, topic filters and no-script fallback.
Keep the existing hub fragment targets when rearranging their sections. Run
`python _tests/poker_discovery_browser.py` for keyboard arrivals, narrow layouts,
section jumps, no-script reading and optional axe scans.

`/poker/topics/` is the shared subject map across original guides and outside
sources. Ten focused subject pages are generated from `_source/poker/topics.json`.
Every guide needs one primary topic; related placements are allowed. Every
external source must be reachable through the map. The existing library and
resource-directory categories remain available as more specialized filters.

Run `python _tests/topics_browser.py` for deep-link, topic/source filtering,
Back/Forward, keyboard, query-privacy and no-JavaScript checks. Search text is
never serialized; only whitelisted editorial filters use URL fragments. See
`_reports/poker-information-architecture.md` for the review, scope and next
quality priorities. Topic pages are not counted as additional strategy guides.

## Living Well

`/living-well/` is a major, publicly linked section between Technology and Poker.
The two catalogs in `_source/living-well/` hold the authored launch content;
`_scripts/living_well.py` validates them and renders the shared manifest, subject
pages, reader routes, article metadata, separate RSS, and blank worksheets.
The launch has 16 essays/guides, 3 proposed experiment protocols, 5 subject pages,
and 9 supporting hubs. Proposed protocols are not completed field notes and are
excluded from the editorial RSS feed. No private answers, new JavaScript, or
new third-party services are introduced. The current contact and analytics
configuration is preserved. Run `_tests/test_living_well.py` and
`_tests/living_well_browser.py` alongside the existing full regression suite.

## Search visibility and personal identity

The site search at `/find/` includes the visible, named major section headings
of its existing 151 public destinations. `_scripts/search_sections.py` extracts
these from generated page HTML, using the same exclusions as reading outlines.
Disclosure contents, hidden answers, form values and excluded pages are omitted.
The compact JSON data is embedded only in the search page, so filtering makes
no network request and requires no separate search service. Title and summary
matches rank before heading-only matches. Up to three matching section links
lead to the original page anchors; article copy and URLs are not duplicated.
The existing browse index and title/summary search survive absent or malformed
section data. Browser checks cover actual keyboard arrival at the headings,
expanded text, privacy boundaries and JavaScript-disabled browsing.

Reviewed reader-entry copy lives in `_source/search-entrypoints.json` and is
applied by `_scripts/search_entrypoints.py`. It supplies specific search titles,
five clearer hub headings, and visible purpose summaries on twelve existing
hubs. Article identities, wording, dates, and feed records are not republished.

`_source/reader-previews.json` records the current title, publication kind, layout,
and exact bytes of individual typographic previews. All ninety articles and the
three additional subject hubs have distinct cards; the previous hand-designed
cards remain in place. These are sharing title cards, not article illustrations
or photographs. They are not added to Article image markup.

After changing an existing article title or proposed/recorded status, regenerate
and inspect its previews with the maintainer tool, which requires Pillow and
installed DejaVu fonts:

```sh
python _scripts/render_reader_previews.py
python _scripts/build.py
```

Normal builds need no image renderer or fonts. The renderer preserves every card
declared in `_source/presentation.json`; its separate catalogue rejects stale
titles, wrong scopes, and unreviewed image bytes. New articles can retain the
standard card until previews are deliberately regenerated. Font rasterization
may differ across machines, so inspect any newly rendered cards before release.

`_scripts/search_visibility.py` connects published page types, the existing author
profile, visible breadcrumbs, and explicit utility-page indexing policy. Do not
add credentials, social profiles, outcomes, ratings, or representative article
images without genuine supporting material. Social title cards are not article
illustrations. Keep indexing choices separate from reader navigation and existing
RSS identities.

```sh
python _scripts/check_search.py
python _tests/search_visibility_browser.py
```

The search checker runs in Site checks and reads committed HTML. The browser test
uses the same `CHROMIUM_PATH`, `AXE_PATH`, and `SCREENSHOT_DIR` options as the other
suites. Its `--offline` mode checks rendered layouts only when local networking is
unavailable; it does not claim live navigation or no-script validation. See
`_reports/search-visibility-2026-10-11.md` for the audit and remaining measurement
priorities, and `_reports/search-audit.json` for the static coverage summary.

## Practical AI evidence and time comparison

`/technology/ai-time-savings/` compares the whole workflow in minutes, including
setup, review/repair and total upkeep. `assets/workflow-time.js` exposes a pure
integer calculation tested against independent exact fractions. The script and
its styles are page-scoped; there is no input collection or browser persistence.
The blank worksheet is the source for its exact visible preview.

`/technology/checking-ai-website-changes/` documents a historical pre-release HTML
failure and its correction, with a reduced public reproduction and a bounded
record of what the checks establish. Historical test counts must not be silently
updated to current counts. Run `python downloads/website-check-reproduction.py`
with `html5lib==1.1`, and `python _tests/workflow_evidence_browser.py` for the new
reader and calculator journeys. Both are in Site checks; all 21 earlier browser
suites remain. See `_reports/workflow-evidence-release.md` for scope and the
Search Console property-access limitation.

## Practical work previews and writing distribution

`_source/practical-discovery.json` selects the two existing browser tools and the
recorded Technology case. `_scripts/practical_discovery.py` renders the work links,
previews and Technology writing cards, and creates `/technology/feed.xml`.
The combined `/writing.xml` feed deduplicates by canonical article identity.

The four practical AI checkpoints share optional navigation from
`_scripts/practical_navigation.py`. It decorates finished pages after reading
times and outlines are calculated. The current stage is text, not a tool-resetting
self-link. Existing page sources, sheets, scripts, publication metadata and feeds
stay intact. The exact additions and a separately verified production baseline
are protected by `test_practical_navigation.py`; historical adapters remove only
the frozen reviewed blocks on the four named pages. Run
`_tests/practical_navigation_browser.py` in the existing hosted browser workflow
to check direct arrivals, sibling links, onward choices and private tool return.
New published Technology evidence articles are included automatically; calculators
and site edits are not fabricated into new dated articles. Historical section
feeds and existing combined-feed item fields remain independently tested.

Real preview capture is developer-only, requires Playwright Chromium and Pillow,
and blocks external requests:

```sh
python _scripts/capture_work_previews.py --baseline <reviewed-full-commit-sha>
python _scripts/build.py
python _scripts/check_search.py
python -m unittest discover -s _tests -p test_practical_discovery.py -v
python _tests/practical_discovery_browser.py
```

Review the resulting PNGs and `_reports/work-preview-provenance.json` together.
Browser/font rasterization can change pixels; dependencies and fictional inputs
are recorded rather than claiming a cross-platform pixel benchmark. See
`_reports/practical-discovery-review.md` for scope and limitations.

## Everyday task discovery and portable worksheets

`_source/everyday-tasks.json` selects seven existing worked guides, describes their
reader tasks, and supplies eight bounded search-title/description overrides.
`_scripts/everyday_tasks.py` renders the Technology task cards and the additional
worksheet menu. These are links into the existing Living Well series, not copies
of articles or a new topical subsite. Original article titles, dates, bodies,
evidence labels, and all five feed records stay with their original sources.

`_scripts/living_well_utility.py` exports each visible `utility.starter` unchanged
as `downloads/living-well-<slug>.txt`. Do not maintain a separate worksheet body:
the preview and download must remain byte-identical. Existing five reflection
Markdown sheets remain unchanged. The new task-sheet directory is linked at
`/living-well/worksheets/#everyday-task-sheets`.

```sh
python _scripts/build.py
python _scripts/build.py --check
python _scripts/check_search.py
python _tests/check_html5.py
python -m unittest discover -s _tests -p 'test_*.py'
python _tests/everyday_tasks_browser.py
```

The browser suite checks native journeys and downloads with JavaScript enabled
and disabled, print previews, narrow layouts and text spacing. Its `--offline`
mode does not claim HTTP, download, or axe results. It is added to Site checks
without removing the previous 23 suites. See `_reports/everyday-task-review.md`.

## Local typeface delivery

`_source/font-faces.css` remains the reviewed provider capture. The build changes
only its font URLs to the exact content-addressed WOFF2 files in `assets/fonts/`,
with original licenses and `_reports/local-fonts-provenance.json`. Normal builds
make no font-provider requests. Replacing a typeface or subset requires a new
review of binary provenance, licenses, descriptor coverage and rendered geometry.
The full hosted gate includes `local_fonts_browser.py`; the live verifier checks
every font and license. The privacy notice describes the current local hosting.
