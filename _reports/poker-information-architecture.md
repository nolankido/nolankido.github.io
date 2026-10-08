# Poker information architecture review and release

Date: October 8, 2026
Baseline: 7c08856882ec8eb243b0422e2ea5fdff5198af59
Scope: Poker subsite only. The Technology-first personal gateway is unchanged.

## Diagnosis

The baseline had 39 practical guides, 138 external resources, eight guided
collections and a unified answer finder. The limiting issue was no longer the
number of links. Visitors had to understand the site's internal publishing
history before deciding where to go.

The homepage had accumulated overlapping viewer routes, player routes, eight
collection cards, a prominent fictional hand and repeated directory invitations.
The guide library and external directory used different specialist taxonomies.
Those taxonomies are useful for filtering a specific catalogue, but they did not
provide a shared subject map. A reader could reach a guide without an obvious
route to the related outside sources.

The change therefore prioritizes task completion and subject navigation, not a
larger headline count. This is an editorial and implementation assessment, not a
user study, traffic analysis or claim of competitive superiority.

## Implemented architecture

The primary Poker navigation is Home, Topics, Search, Guides, External links,
Study desk and Glossary. A clear distinction remains between the personal site's
primary navigation and the Poker subsection.

The homepage offers a shared search entry, quick references, three task-based
starting paths, ten subject cards, a bounded practice area and a separate space
for actual stories and episode companions. Previous public section anchors and
all existing page URLs remain intact.

The compact topic map lives at `/poker/topics/`. Each subject has a focused page:

| Subject | Route |
| --- | --- |
| Learn poker | `/poker/topics/learn/` |
| Cash games | `/poker/topics/cash-games/` |
| Tournaments | `/poker/topics/tournaments/` |
| Strategy and math | `/poker/topics/strategy/` |
| Omaha and mixed games | `/poker/topics/variants/` |
| Study tools and training | `/poker/topics/study/` |
| Places to play and home games | `/poker/topics/places-to-play/` |
| News, results and creators | `/poker/topics/poker-world/` |
| Research and development | `/poker/topics/research/` |
| Safer play and rules | `/poker/topics/safer-play/` |

Each topic page has two or three starter questions, an expandable list of related
guides, three selected outside sources, direct access to all matching sources,
and a clear route back to the subject map. Source cards reuse the existing
publisher, access, description, caution, review date and review method. They do
not imply that a source was independently re-reviewed during this reorganization.

The guide library, external directory and guided collections are preserved. They
are different views of the same material, not competing definitions of where a
subject belongs. Every guide now has a primary-topic breadcrumb and a contextual
return path to related outside sources. Topic pages are navigation collections,
not extra strategy guides or personal experience claims.

## One catalogue, several useful views

`_source/poker/topics.json` is the editorial subject registry. The build derives
topic cards, focused pages, counts, finder memberships and breadcrumbs from it.
Every guide has exactly one primary topic and can have related-topic placements.
Every approved external source belongs to at least one topic. Overlapping topic
counts are explicitly explained rather than added to the inventory total.

The build rejects missing guide assignments, duplicate assignments, unsafe IDs,
unknown source IDs, unknown directory sections, invalid starter links, invalid
overview routes and unknown glossary references. Existing resource records and
review dates are unchanged. The manifest and live checker now share one route
inventory, including dynamically generated topic pages.

The existing finder adds a topic filter alongside source type and free access.
Topic links can open a specific source-type subset. Only whitelisted filter values
appear in a URL fragment. Search words remain local and are not written to the
address bar, storage or analytics events. Back, Forward, reload, Clear and Escape
have defined behavior. A changed history location clears the text query instead
of exposing it in navigation history. No extra server, account, dependency or
third-party script is introduced.

The topic map and guide disclosures work without JavaScript. With JavaScript
disabled or the finder script blocked, the complete search index remains visible;
filter fragments do not pretend to work without the script.

## What this does not solve

The directory is not yet the best or most complete poker reference on the web.
Better navigation makes the existing material easier to use; it does not prove
that its strategy content is superior or that every outside link is current.

The current strength is beginner hold'em, tournament preparation, study workflows
and links to original research. Cash games and mixed games have useful starting
material, not complete in-house curricula. Venue listings, home-game organization,
poker history, live reporting and geographic coverage remain thinner. The site
does not maintain live seat availability, a complete worldwide room database,
current tournament results, or jurisdiction-specific gambling and tax advice.

## Next quality priorities

1. Validate real visitor tasks. Observe whether a new player can find hand
   rankings, a cash player can compare rake and study sources, a tournament
   player can locate a structure sheet, and a mixed-game player can find the
   correct rules. Track task success and wrong turns, not just page count.
2. Improve subject depth selectively. Prioritize rigorous cash-game references,
   dedicated PLO and split-pot explanations, home-game administration and a
   region-aware route to official room and event information. Add substantive
   pages only when there is a distinct reader problem and an adequate source.
3. Publish original work. Verified hand records, documented study experiments,
   actual event preparation and episode companions can differentiate this site.
   Never substitute invented personal stories or unverified solver conclusions.
4. Maintain source quality. Review changing rules, operator policies, product
   access and event links more frequently than stable research papers. Record
   whether a page was read, merely reached, blocked, redirected or retired. Do
   not silently turn a successful HTTP response into an editorial endorsement.
5. Make trust inspectable. Keep correction paths, access labels, evidence limits
   and clear fictional-case labels visible. Any future commercial relationship
   must be disclosed and must not silently determine the topic selections.

## Verification record

Local: deterministic build and all 187 Python regression tests passed. JavaScript
syntax checks passed. Static desktop and mobile renderings were inspected without
remote font loading. The container's browser policy blocked localhost navigation,
so local end-to-end browser runs were not counted as passing. The GitHub Actions
release gate runs the full browser, HTML5, accessibility and failure-recovery
suites, including the new topic navigation tests. The merge and public-byte check
must be verified separately; a generated build is not evidence of deployment.

The release adds a compact topic index and ten focused topic pages, not eleven
new strategy guides. Existing 39-guide and 138-source totals are preserved.
