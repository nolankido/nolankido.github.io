# Poker reader release: October 6, 2026

Adds a complete, static educational library with six topic filters, local-only
search, explicit reading-time estimates, level labels and related-reading cards.
All guides remain visible without JavaScript. Search never sends requests, updates
the URL, saves history or calls analytics. The only added runtime script is scoped
to the library. The Umami tracker, privacy policy and contact code are unchanged.

Adds one visual fictional river Decision Lab with five native answer disclosures.
Its price, weighted range and alternative showdowns are independently tested.
The feature uses HTML cards and existing typography rather than stock photos,
fabricated episodes, fabricated results or a simulated live poker interface.

The guide source files are unchanged except the Poker overview and study desk.
Shared navigation, reader metadata and related links alter rendered Poker pages.
Non-Poker generated HTML, existing CSS, contact code and global layout must remain
byte-identical to the base release. Tests enforce complete catalogue coverage and
fail when a newly published guide has not been added to the editorial index.

Reading estimates are an explicitly chosen convention of 225 words per minute,
including explanations, not reader telemetry. Five keyboard disclosures work
without JavaScript. Local browser tests inspect filtering, no-match recovery,
search/category intersections, literal hostile input, no network/storage effects,
blocked-script fallbacks and narrow/wide layouts. Automated accessibility tests
are not a complete manual accessibility certification.

Reference checks: PokerStars pot-odds lesson, GTO Wizard combinatorics and ICM
background, MDN search input documentation, W3C status-message guidance. The
river scene is original and explicitly conditional on its simplified chip model.
