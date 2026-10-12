# Reader entry points and recognizable public links

Implementation date: October 12, 2026.
Baseline production: `f35b1504ee921a02785bbc0402eff8fb817c8876` (PR 49).
The user explicitly requested implementation and publication to nolankido.com.

## Assessment

The existing site has working practical-AI tools, original guides, authorship,
canonical metadata, breadcrumbs, sitemap, native discovery, and a recorded case.
The next addressable gap is how existing material is introduced in search and
when someone shares it. Several collection titles are vague outside the site:
“Try something useful,” “Five ways into Living Well,” and “The Poker library.”
Most article links also still use the generic identity image.

This release makes the material's purpose clearer while keeping Nolan as the
public identity across Technology, Living Well, Poker, and Creative Work. It
does not introduce another biography, invent credentials, or publish another
batch of articles. This is an editorial judgment about presentation, not a
keyword-demand or measured-credibility finding.

## Implemented

Twelve existing hubs have reviewed titles and descriptions, matching visible
purpose summaries, and explicit modification dates. Five vague headings become
concrete collection names: essays on meaning/everyday life, practical everyday
guides, Living Well topics, everyday worksheets, and poker hand explanations.
The other established visible titles remain. Search, sharing, structured page
metadata, breadcrumbs, and internal destination labels use the same public
manifest. Internal search reflects the new labels, summaries, and sorting.

The twelve hubs are Start Here, Writing, Resources, Creative Work, Poker library,
Poker Study Desk, and Living Well's home, essays, guides, topics, worksheets,
and free-resource directory. Technology and the personal homepage are retained.

Eighty-nine new 1200 × 630 PNG title cards cover 86 articles and the three other
subject hubs. Together with the retained four article cards, all 90 Articles
have individual previews. The existing Technology and tool cards also remain.
The new assets total 903,159 bytes; the largest is 14,947 bytes. They are metadata
assets, not new in-page image requests. Actual platform display and cache refresh
remain controlled by the receiving platform.

Each new card uses the actual current title and a truthful material label.
The three experiment plans are explicitly labelled Proposed Experiment. There
are no generated portraits, client claims, invented experiences, or completed
results. These typographic graphics are not representative article illustrations
and are not added to Article image markup.

Normal builds validate the card's title, status, canonical path, complete line
layout, safe bounds, and SHA256 against its committed bytes. Changing a known
title or status requires deliberately regenerating and reviewing its card.
Pillow and installed fonts are maintainer-only dependencies, not website or
normal-build requirements. All 89 cards were inspected in three contact sheets.
The existing design, core stylesheets, fonts, runtime scripts, contact, privacy,
and analytics remain. One small scoped stylesheet supports entry summaries and
long-heading reflow. No new form, account, upload, storage or tracking event.

## Integrity and validation

An independent pre-edit baseline records all 220 original source, asset and
download files, all 171 page bodies, the complete public manifest, old sharing
declarations and old script declarations. Script declarations were captured
from the untouched production Git objects, not from the modified candidate.

The new tests directly preserve every original source/asset/download, every
article's metadata and body text, and all five feeds. Bounded predecessor views
normalize only declared collection copy, generated destination labels, visible
summaries, stylesheet reference, preview declarations, and title-driven index
ordering. Historical golden digests are retained. An unmarked article change
remains detectable by a negative control.

The new native browser suite tests all twelve hubs at four widths with JavaScript
enabled and disabled, expanded text spacing, ordinary keyboard journeys, and
exact bytes for every new card. Three scoped axe scans are included. The local
managed environment has no browser-control plugin, so browser verification is
assigned to hosted CI rather than claimed locally. Existing suites remain.

Before reporting this release live, require the full candidate CI gate, GitHub
Pages deployment, and the complete public-response inventory to pass. The final
receipt is recorded on the pull request after those results are observed.

## Measurement and references

The connected Search Console properties were checked again and still do not
include nolankido.com. No search clicks, impressions, keyword volume, ranking
gain, Google indexing inspection or sitemap submission was obtained. An absent
connected property does not establish zero traffic or non-indexing.

Google Search Central recommends concise, descriptive title text, specific
descriptions, and a clear primary heading. Google decides the displayed search
title and snippet after processing pages; these preferences are not guarantees:
https://developers.google.com/search/docs/appearance/title-link
https://developers.google.com/search/docs/appearance/snippet

Open Graph defines a page-specific representative image, description, canonical
address and image alternative text for link presentation:
https://ogp.me/

Sharing cards are distribution/presentation improvements, not a claimed direct
ranking factor. No traffic, credibility, conversion or performance gain is
inferred merely from publishing this release.
