# Nolan Kido personal website

A small static website for introductions, selected writing, and practical resources. GitHub Pages serves committed HTML. There is no runtime application server or database. Optional, cookie-free Umami Cloud pageview analytics is installed through the shared layout; the site works when analytics is blocked. See `ANALYTICS.md`.

## Site architecture

The homepage introduces Nolan first, shows three selected pieces of published
writing, then opens the four subject libraries in their established order:
Technology, Living Well, Poker, Creative Work. `/start-here/` is the cross-site
orientation page. It is available in the shared utility bar on every page.
The homepage is not a chronological feed, project portfolio, or popularity counter.

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

Set `CHROMIUM_PATH` to use an installed Chromium binary. Set `SCREENSHOT_DIR` outside the repository for optional screenshots. Set `ALLOW_WEB_FONTS=1` on a separate `design_browser.py` run to verify the three real font families. Default browser checks use fallbacks.

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
