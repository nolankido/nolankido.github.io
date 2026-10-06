# Poker Decision Labs expansion

Prepared October 6, 2026 against main f651f5a674c98e5ff7c2faeeb86ad9f04caa3122.

## Reader changes

The new `/poker/decision-labs/` series index joins three fictional teaching cases.
Original Lab 01 keeps its existing URL and source text. Lab 02 at
`/poker/flush-and-redraw/` follows a face-up hand, counts all 44 possible rivers
with both hands known, and tests a changed opposing hand. Lab 03 at
`/poker/side-pot-lab/` separates pot eligibility, contribution layers and refunds,
then reconciles final stacks and tests a smaller-stack variant.

The library has 24 educational entries. All new cases are reachable from the
library, study directory, homepage, RSS and sitemap. Optional native On this page
panels use existing visible major-section anchors and exclude hidden answers.
Related reading is curated across the complete educational index.

## Boundaries

No actual hand, personal result, episode or solver finding is invented. This is
after-play study, not a live strategy service. No runtime script, answer form,
saved answer or analytics event is added. Umami, contact code, the Technology-first
homepage, global layout, previous guide sources and publishing catalogue remain.
Only the Poker reader stylesheet is extended; original global styles are intact.

## Verification

The new unit suite independently evaluates the displayed cards, enumerates every
river for both opposing hands, derives pot layers and refunds, checks conservation,
validates discovery and checks spoiler-safe outline anchors. The browser suite
checks local HTTP pages at four widths, nine keyboard answer panels, outline links,
no-JavaScript use, and closed/expanded accessibility states. Existing tests remain.

Before submission, local 91-test and original workshop keyboard suites passed.
Sixteen offline render states passed, including expanded content and text spacing.
Desktop and phone screenshots were inspected. PR CI must run real HTTP and all
existing browser/accessibility checks before merge. Verify live deployment bytes
separately. Automated accessibility is not a complete manual certification.

## Background verified

- https://www.pokerstars.com/poker/games/rules/
- https://www.pokerstars.com/poker/games/rules/hand-rankings/full-house/
- https://www.w3.org/WAI/WCAG22/Techniques/general/G64

The scenarios and calculations are original and conditional on their stated
inputs. Temporary authoring/preparation files must be removed before merge.
