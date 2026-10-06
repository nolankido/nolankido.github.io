# After-play Poker workshops

Content release: October 6, 2026.

## Scope

Seven new substantial articles connect the existing beginner library to tournament
study and vlog production: pot odds, short-stack compatibility, ICM, weighted
combinations, variance/results, hand-to-vlog workflow, and a twelve-question
practice room. The study desk includes three reading routes and four additional
blank Markdown worksheets. No actual episode, hand, result, range, channel or
private project evidence is invented. All worked cases are explicitly fictional.

The main Technology-first homepage, non-Poker pages, shared layout, CSS, contact
code, Umami settings, prior thirteen topic-guide sources, existing hand-review
article, public catalog and approval workflow are preserved. The Poker home has
updated discovery links and no longer inaccurately describes the viewer library
as only seven guides. Earlier beginner anchors and both worksheet previews remain.

## Implementation

Use existing source HTML, manifest, shared template and Poker-only stylesheet.
New articles are dated October 6 and appear in the Poker feed and sitemap. The
normal live checker includes all new routes and all four new download files.
There are no new scripts, answer forms, event trackers, cookies or stored answers.
Native details panels work without JavaScript. Completed worksheets remain private.

## Verification

`test_workshops.py` checks content scope, discovery, dates, downloads, answer
count and independent arithmetic. It enumerates physical card combinations and
ICM finishing orders; validates the river hand comparison with the existing small
test evaluator; and checks draw, ROI and call-price examples independently.
`workshops_browser.py` checks seven pages at four widths, all twelve keyboard
answer disclosures, and a no-JavaScript read. Network requests are blocked.

Run all existing build/unit/browser/accessibility checks as well. These checks
are not an accessibility certification, proof of poker optimality or confirmation
that private Umami dashboard events were received. Verify Pages deployment and
published bytes after merging.

The temporary branch integration script/workflow must be removed before merge.
The existing Site checks workflow stays read-only; its only intentional extension
is invoking the targeted workshop browser suite alongside the existing suites.
