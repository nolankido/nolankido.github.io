# Website analytics

Installed October 6, 2026. The owner supplied the Umami Cloud website ID.
The tracking script is in `_source/layout.html` and is emitted once in the
head of each public HTML page, including the custom 404. Future generated
pages inherit it. Do not paste another copy into individual page bodies.

## Scope and privacy

- Originally pageviews only at installation. On November 22, the author
  approved exact Kindle product links with three named, click-only Umami
  events for the Books catalog and two existing standalone book pages.
  The events use a fixed `source` property of `books-catalog` or
  `book-page-hero`; no reader-supplied properties, user IDs, email,
  form fields or session recordings are sent. They represent outbound
  link clicks, not Amazon product views, book orders or verified receipts.
- No advertising pixels or automatic affiliate/attribution redirects.
  Existing Do Not Track and domain restrictions remain in effect.
- `data-domains` permits `nolankido.com` and `www.nolankido.com`; local
  previews and alternate development hostnames do not send pageviews.
- `data-do-not-track="true"` respects the browser Do Not Track preference.
- `data-exclude-search="true"` and `data-exclude-hash="true"` omit query
  strings and fragments from recorded page URLs. This intentionally
  sacrifices query-based campaign/UTM analysis in the initial setup.
- The deferred external script is optional. The site does not call Umami
  from its contact JavaScript, and blocked analytics must not break use.
- The website ID is a public tracker identifier, not an account password
  or private API key. Never commit account credentials or private keys.

Umami's documented standard tracking is cookie-free. Loading the script
and sending requests still involves a network connection to the provider;
do not describe this as collecting no information at all. The public
privacy page discloses analytics separately from hosting, fonts and forms.
This implementation is not a blanket legal-compliance certification.

## PBG-05: read-only Kindle link audit

Run `python _scripts/poker_book_click_path_audit.py` from a complete local
checkout before releasing changes to any book page, Amazon href or
Umami event. This command checks five native Amazon anchors across
the three first-party book pages, each `data-umami-event` and
`data-umami-event-source`, exact author-supplied URLs from the public
edition ledger, source/output HTML parity, one tracker with existing
privacy flags, and the public disclosure. It emits JSON and exits
nonzero on mismatch. It does not load Amazon, send a click, emit an
Umami event, collect traffic or write any private file.

The checker has twelve source/mutation unit tests in
`_tests/test_pbg05_book_click_path_audit.py` and is part of
`_scripts/local_release_checks.py`. A separate
`_reports/poker-book-growth/pbg-05-live-click-path-observation-2026-11-22.json`
freezes one **read-only** observation: all three public pages showed
all five expected links, while Amazon returned a shopping interstitial
for all three user-supplied product URLs. Those observations do not
authenticate actual Amazon product metadata, Umami event ingestion,
purchasing availability or sales. No test clicks were generated.

For actual outcome data, use the owner-approved Umami **Events**
report, break down by the fixed `source` property and a matching
month's pageviews, and feed only operator-confirmed private aggregates
to `_scripts/poker_book_growth_scorecard.py`. KDP Orders and Royalties
reports are **separate total-book measures**, not proof of website
attribution. Amazon Attribution may be an eligible KDP option through
the Amazon Ads console, but do not invent tags or change Amazon URLs
without an actual account-generated tag and owner approval. Store
authenticated real event, KDP and Attribution reports privately.
This revision does not install another tracker or change the Privacy
page; it documents the existing behavior.

References:
- https://docs.umami.is/docs/track-events
- https://docs.umami.is/docs/event-data
- https://advertising.amazon.com/solutions/products/amazon-attribution
- https://kdp.amazon.com/en_US/help/topic/GVTTXHKHVPAPBEDQ

## Verification and maintenance

Build and test locally with `python _scripts/local_release_checks.py`,
plus `--browser` where browser behavior changed. The existing
`test_analytics.py` checks coverage, duplicate prevention, the public
website ID and privacy flags without sending synthetic events to production.
The former `.github/workflows/site-checks.yml` was intentionally removed
on November 1, 2026. Do not restore, dispatch or rely on it, any other CI
workflow or a scheduled substitute. Verify deployed bytes with direct
public GETs after publication.

The private, zero-network monthly visibility scorecard at `downloads/visibility-private-scorecard.py` keeps Search Console Web clicks, Google AI appearances, Bing AI citations, and Umami assistant pageviews in separate measures. It outputs null for uncollected sources; an observed count requires a source-specific report, property and period confirmation. Store inputs and results outside GitHub, not in `_reports/`. See `_reports/visibility-sprint/seo-geo-turn39-first-party-baseline-2026-11-20.md` for the dated access limitations.

After Pages deployment, open the Umami dashboard for `nolankido.com`,
visit a public page and check that a pageview appears. Browser blockers
or Do Not Track may exclude a test visit. Successful publication and a
valid script tag do not by themselves prove ingestion into the private
dashboard. Do not claim ingestion is verified without observing it.

The three already-installed Amazon book-click events are:
`poker-book-kindle-amazon-click`, `one-workflow-kindle-amazon-click`,
and `ai-works-human-decides-kindle-amazon-click`. For baseline work,
use the Umami Events report by event name and fixed source to count
outbound book-link clicks, without interpreting them as orders or even
proof that Amazon loaded. The tracker code is configured, but live event
ingestion and actual counts remain unverified until the owner's dashboard
confirms them. Do not sum unique visitors or sessions across pages as
though they were one independent audience.
YouTube clicks, downloads, contact acceptance events and Google Search
Console are not automatically configured by this original tracker installation.
Add only explicitly named, non-personal events with a defined use, and
update the public notice and regression tests at the same time.

References:
- https://docs.umami.is/docs/collect-data
- https://docs.umami.is/docs/tracker-configuration
- https://docs.umami.is/docs/faq
- https://umami.is/privacy
