# Search visibility and personal image review

Review date: October 11, 2026, Hawaii time.
Repository baseline: `ef46ac969d99d8ffe5b71fc4b903dd15af30f52d`.
Scope: the published site, all generated page metadata, source architecture,
reader journeys, and the highest-value improvements implementable without
inventing personal evidence or changing hosting accounts.

## Assessment

The site already has a coherent person-first identity, a restrained editorial
design, four ordered interests, useful static resources, explicit AI-assistance
disclosures, canonical URLs, a sitemap, and RSS. The baseline has 166 pages,
166 unique titles, 166 unique descriptions, and 86 Article records. This is not
a missing-meta-tags problem. The better opportunity is to connect the author,
make the main Technology entry more specific, and let readers inspect useful
work instead of asking them to accept broad expertise claims.

There was no complete connected authorship identity across articles. Home and
About already identified the same Person, but article authors lacked that stable
identifier. General pages lacked a full breadcrumb trail; existing Poker and
Living Well trails had no structured counterpart. Internal finder pages and the
contact-card utility were included as search landing pages. Technology's search
title was simply "Technology | Nolan Kido", despite a working AI task-brief tool
and a library of relevant guides.

These are technical and editorial observations, not a diagnosis of search traffic.
No authenticated Search Console data, verified Google indexing inventory, keyword
volume estimates, ranking baseline, backlink audit, or real-user Core Web Vitals
was used. Failed requests from a tool are not evidence of a production outage.

## Implemented changes

### A consistent author and site identity

All 166 page records now refer to one WebSite identifier and its Person publisher.
All 86 Article records link author and publisher to the established About profile.
Articles and their containing WebPages have distinct identifiers. About remains
a ProfilePage. Relevant collection hubs are described as CollectionPage, and the
existing task brief is described as the free browser WebApplication it actually is.
No social handles, employers, degrees, awards, ratings, testimonials, or client
outcomes were invented. There is no claim of Google rich-result eligibility.

Articles outside the existing Notes byline system now have a visible linked
Nolan Kido byline and an editorial-method link. Existing Notes attribution,
disclosure, publication dates, and article bodies are retained.

### Navigation and crawl policy

164 pages have one visible breadcrumb and a matching BreadcrumbList. The homepage
and error page deliberately have none. Existing editorial parent links and labels
are preserved rather than replaced by mechanically guessed categories.

The three finder pages, `/find/`, `/poker/find/`, and `/living-well/find/`, plus
`/card/`, now carry `noindex, follow` and are omitted from the sitemap. They remain
publicly reachable and usable. Robots.txt continues to allow crawling so search
engines can see the directive. The existing 404 noindex remains. The sitemap has
161 canonical URLs, with no mass date refresh.

Search indexing is separate from public navigation and historical subscriptions.
The dated Poker finder was already an RSS record. A narrow, named compatibility
exception preserves that exact record and all four existing feeds rather than
silently rewriting feed history. This exception does not admit new hidden pages.

### Stronger practical-AI positioning

Technology now leads with "Practical AI for real life" and a specific search title,
"Practical AI for Everyday Life | Nolan Kido". Its working-examples section joins
three existing, different forms of evidence: a usable tool, a checkable calculation,
and a guide for evaluating a workflow. It does not present them as measured results.

The task-brief page now has a more specific search title and a substantive
"How it works" section on its existing URL. This explains the fixed assembly,
required inputs, stale-output invalidation, no-script fallback, four manual checks,
input handling, and the distinction between local builder behavior and site-level
analytics/web fonts. The browser tool itself and its data boundaries are unchanged.

About now connects its existing personal introduction to work readers can try and
inspect. The previous About prose is preserved exactly around the new section,
with an independent regression assertion. Creative Work and Resources receive
more descriptive search titles without rewriting those sections or moving pages.

Two locally hosted 1200 by 630 sharing cards are added for Technology and the
AI Task Brief Builder. They are each under 12 KB. Existing approved cards are
unchanged. These are social-link previews, not fabricated article illustrations;
no title card is inserted into Article image markup.

### Maintenance and release checks

`python _scripts/check_search.py` audits committed HTML, not just configuration:
one canonical, unique titles and descriptions, valid shared identity, matched
visible/structured breadcrumb parents, explicit indexing policy, preserved dates,
local sharing metadata, and no unsupported identity claims. The deterministic
summary is `_reports/search-audit.json`. It is a search-readiness check, not a
ranking score or Google validation report.

The check is part of Site checks. New unit tests cover policy immutability,
existing feeds, invalid origins, breadcrumb escaping, original About prose,
misleading image markup, real-page tampering, and actual tool/evidence links.
The new browser suite checks 320, 390, 768, and 1440 pixel layouts, text spacing,
native keyboard journeys, no-script fallbacks, and automated accessibility when
axe is available. Offline local runs explicitly skip live URL and no-script
journeys; the full suite runs on the GitHub runner. Existing browser suites remain
in the release gate. Public byte verification remains separate from passing CI.

Only explicitly reviewed presentation snapshots were rebased: the revised About
and sharing configuration, plus generated HTML changed by the shared metadata.
Original Poker and Living Well sources, article bodies, feeds, identity copy,
contact implementation, privacy configuration, design stylesheet, and analytics
settings retain their existing independent protections.

## What remains most valuable

1. Establish a Search Console baseline, submit/confirm the existing sitemap, and
   inspect Home, About, Technology, the task brief, and a representative article.
   Separate branded searches for Nolan Kido from nonbranded practical-AI discovery.
   Compare clicks, impressions, CTR, query relevance, and landing pages over
   successive 28-day windows. Avoid drawing a ranking conclusion from one day.
2. Publish one genuine, bounded practical-AI case study with a real starting task,
   screenshots or artifacts, the checks performed, what failed, the full work
   involved, and any limitations. Obtain permission for third-party material.
   Measured outcomes require actual measurements, not an attractive estimate.
3. Add a chosen real portrait and confirmed public profile links when supplied.
   Authenticity and a few independently checkable examples are a better next
   investment than another large batch of generic articles or an inflated title.

External recognition, relevant references from other sites, and firsthand evidence
cannot be manufactured by adding schema. Re-crawling and improved rankings are
not guaranteed by this release. Existing broad subject libraries remain intact;
no bulk removal or search-first content expansion was justified by the available
evidence.

## Primary guidance consulted

- People-first content and identifiable authors:
  https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Article authorship and representative images:
  https://developers.google.com/search/docs/appearance/structured-data/article
- Profile-page identity:
  https://developers.google.com/search/docs/appearance/structured-data/profile-page
- Breadcrumbs and reader-visible hierarchy:
  https://developers.google.com/search/docs/appearance/structured-data/breadcrumb
- Crawl access for a noindex directive:
  https://developers.google.com/search/docs/crawling-indexing/block-indexing
- Canonical sitemaps and accurate modification dates:
  https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
