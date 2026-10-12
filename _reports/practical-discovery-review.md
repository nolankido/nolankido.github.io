# Practical work discovery and publication review

Review date: October 11, 2026, Hawaii time.
Baseline: `eaf08e16bad12601934f1d704df4403b2d6c6027`.

## Decision

The last two releases established search metadata and actual practical-AI work.
The next useful release should make that work easier to discover and judge, not
inflate the biography or add more generic articles. This pass changes the existing
reader paths and publication machinery. It adds no HTML pages, external profile
claims, accounts, forms, runtime scripts, or analytics.

A concrete omission was found: the recorded Technology case was linked from the
Technology, About and Resources pages, but was absent from the Writing gateway
and combined feed. Preserving old feed bytes across the preceding release had
also preserved an incomplete subscription inventory. There are two real tools,
but the main Technology page previously described them without showing output.

Search Console properties were read again through GSC Wizard. nolankido.com is
still absent from the connected account inventory. This provides no evidence of
zero traffic or non-indexing. No other property's metrics were substituted. A
parent property for the domain is also unavailable, so the folder-property action
cannot establish ownership of this domain. No new property or submission is claimed.

## Implemented

### Immediate evidence from the homepage

A compact native-link block joins the two existing free browser tools and the
recorded website case. It follows the selected writing and precedes the existing
four-interest destinations. The exact personal introduction, original selected
readings and interest hierarchy remain in place. A visitor no longer needs to
open Technology or Search to find the calculator or recorded case.

### Actual work, visibly differentiated

Technology's work section now contains two tool cards and a distinct recorded-case
card. Each tool includes a locally hosted screenshot of its real output, captured
with fictional teaching inputs. Captions distinguish illustrative results from
measured outcomes. These are result excerpts, not portraits, client endorsements,
AI-generated mockups, or new research results. The calculator's 15-minute saving
is explicitly fictional. The full-size preview is linked for inspection.

Images have accurate alternative text, explicit dimensions, lazy loading and
asynchronous decoding. Each PNG is limited to 160 KB. No screenshot is placed in
Article structured data as an illustration of unrelated writing. The screenshot
source inputs, dependencies and asset hashes are recorded in
`_reports/work-preview-provenance.json`; `_scripts/capture_work_previews.py`
reproduces the capture with a locally installed browser, network blocked, and
fallback fonts. Pixel identity across browser/operating-system versions is not
promised. The source dependency hashes prevent silently stale screenshots.

### A complete publishing path

`/technology/feed.xml` contains two explicitly selected practical-AI Notes and all
published Technology evidence articles. Tool updates are not made into dated
articles. The existing Writing gateway now includes the recorded case inside
Technology. Future dated, indexable Technology evidence articles enter the same
Writing and feed paths automatically.

The combined `/writing.xml` feed consumes the additional source and deduplicates
canonical entries. Every prior item retains its title, summary, publication date,
permalink GUID and original source attribution. The three original section feeds
remain byte-for-byte unchanged. Only the omitted case is added to the combined
inventory, with its original publication date. Subscription apps control when
existing or newly discovered entries appear; this release does not guarantee a
notification in a particular reader.

Follow provides the new narrower feed, Technology pages advertise it in their
heads, and the recorded case has native links back to practical writing and
subscription options. Existing URLs and historical publication dates are retained.

## Verification approach

The source build, metadata audit and HTML5 parser check run before publication.
The new independent tests pin the original introduction, identity, article sources,
source feeds, and all historical combined-feed item fields, while presentation
snapshots are rebased only for intentionally edited output. Tests cover invalid
configuration, future-case discovery, noindex/draft rejection, literal-text escaping,
PNG dimensions, provenance hashes, scoped CSS, exact live targets and canonical
feed deduplication. Existing unit, arithmetic and browser suites remain required.

The new browser suite exercises five routes at four widths, with JavaScript enabled
and disabled, increased text spacing, actual image loading, unavailable-image
fallback, keyboard journeys and byte-matched feed responses. Offline mode explicitly
omits HTTP URL/feed checks and is not represented as a substitute for the GitHub
runner. Automated accessibility tests retain inconclusive manual-review notes.
Published responses must be checked separately after deployment. Final run identifiers,
commit and live-response counts belong in the pull request completion receipt.

## Expected benefit and limits

The homepage and work previews should make the identity more concrete: a person
who produces useful things and checks them. Descriptive ordinary links and relevant
images improve the available discovery surfaces; the feed repair makes existing
writing available to subscribers. Those are observable implementation changes,
not measured increases in search position, personal credibility or readership.

Google's people-first, image and linking guidance supports concentrating on useful
original material, representative images, clear context and crawlable descriptive
links. RSS is a distribution feature here, not a claimed ranking factor. There is
no keyword-volume baseline, backlink result, Google indexing confirmation or
real-user performance measurement for this release. Existing broad libraries
remain intact, and no new generic articles or manufactured credentials were added.

The remaining owner contribution is authentic material: a chosen real portrait,
confirmed public profiles, and a real everyday-workflow record with both successes
and failures. The search-measurement prerequisite is access to the correct verified
Search Console property. These require genuine inputs or account ownership, not
more ambitious copy in the site template.

## Primary guidance

- Google Search Central, people-first content:
  https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Google Search Central, crawlable links and descriptive anchor text:
  https://developers.google.com/search/docs/crawling-indexing/links-crawlable
- Google Search Central, relevant images, alt text and image performance:
  https://developers.google.com/search/docs/appearance/google-images
