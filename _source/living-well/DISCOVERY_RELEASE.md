# Living Well: free discovery, first implementation release

Editorial date: October 9, 2026. Implements the first substantive portion of the owner-approved content plan. This is not the full twelve-week roadmap.

## Reader-facing changes

- A shorter, interest-led welcome, with Start Here and Free Resources made prominent.
- Four main section choices: Start here, Essays & paths, Free resources, Try something. Home, Topics, Worksheets, and Field notes remain available in secondary navigation.
- A new `/living-well/free-resources/` hub with eighteen original annotations in six collections. Every entry identifies a specific starting point, access requirements, source, review date, useful context, and a relevant internal companion.
- A new curated reading path, `/living-well/spiritual-curiosity-reading-path/`, connecting a conversation, contextual reading, and competing philosophical perspectives without treating them as interchangeable evidence.
- A new essay, `/living-well/technology-that-helps-you-notice/`, examining nature-identification tools and a no-app alternative. It reports no invented outing or accuracy measurements.
- The existing introductory article is revised rather than duplicated. The weekly-reset, family-story, and free-afternoon guides gain clearly hypothetical examples and practical choices. Existing guide section anchors are preserved by appending the new sections.
- All five blank worksheets are readable on arrival, without downloads or JavaScript. The same underlying text downloads remain unchanged. The print layout separates the five sheets and removes the surrounding navigation and introductory block.
- Topic pages lead to relevant resource collections. The article bibliography stays separate from the browsing directory. RSS keeps original publication dates and excludes proposed experiments.

There are now 36 Living Well pages. The 18 published long-form readings include one labeled reading path; three additional items remain explicitly proposed experiments.

## Sources, access, and personal claims

The source registry is `_source/living-well/resources.json`. The public provider pages and access descriptions were examined for the exact selected items, including account, app, and library requirements. The Closer To Truth selection uses its current Landscape of Consciousness site. Claude Academy points to a readable introductory tutorial rather than assuming course enrollment requirements.

A public source check is not a completed course, installed-app test, security audit, media-player test, or clinical-effectiveness finding. Those limits appear on the resource page. No resource is described as Nolan's favorite or as a tool he personally uses. The first-person welcome reflects the interests and wording approved in the content plan, not invented spiritual beliefs, practices, or memories.

All added prose is original. Poems, exercises, interviews, and course material remain on their creators' sites. There are no affiliate links, paid gates, free-trial-only selections, autoplay embeds, or new visitor-data collection. The examples use fictional information, not personal calendars or private family material.

## Implementation

`_scripts/living_well_resources.py` validates and renders the small resource catalog. `_source/living-well/discovery.json` holds the two new readings. The existing Living Well renderer integrates these with the shared build, manifest, sitemap, feed, navigation, and live-byte verification.

Changes are confined to Living Well source, CSS, tests, generated Living Well files, and the sitemap. Existing global navigation, original design stylesheet, site configuration, contact code, privacy notice, analytics configuration, Poker source and outputs, and the five existing worksheet text files are unchanged. No permanent workflow permissions are increased.

## Verification

The reproducible build has 135 generated outputs. The automated suite includes the original checks plus resource-catalog validation, access labeling, HTML escaping, published/revised date separation, feed ordering, defined CSS-token checks, and preservation of reader routes.

Local rendered-content checks cover all 36 pages at 320, 390, and 1440 CSS pixels with expanded text spacing. Local print verification produced five letter-size pages, one per worksheet, without clipped text. A browser-policy restriction prevented a local HTTP navigation test; the retained GitHub Actions suite is required to verify real navigation, keyboard behavior, no-JavaScript operation, downloads, and axe-core checks before merge. A local rendered preview is not claimed to replace that suite.

The clean pull-request head must pass all retained site checks. After merge, Pages deployment and the existing public-byte verifier must succeed before the release is described as live.

## Remaining roadmap

The meditation entry path, consciousness primer, tool-independence essay, and bounded poker/life expansion remain later editorial work. No completed personal field note is added. A firsthand note requires a genuine supplied experience and appropriate permission. The resource collection can remain selective rather than expanding automatically.
