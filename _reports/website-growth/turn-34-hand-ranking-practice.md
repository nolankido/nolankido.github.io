# Turn 34: connect the ranking reference to card-building practice

Prepared October 27, 2026, Pacific/Honolulu.

## Purpose

The operating map's F6 outcome is a reader who can explain which five cards
count and why a changed comparison wins or ties. Its prescribed next action is
the existing card-basics section of the free learning path. The hand-ranking
guide already contains four complete-board showdowns and eight visible best-five
groups, but its contextual next link led to bets, calls and side pots. The course
was reachable through global navigation without that specific practice handoff.

This turn follows the published first-tournament-plan release at commit
`dfdcdc64dd096f7bdcab0569f19d6cc466c5584b`, tree
`bfce9e3713ff4413450aff2dccb1a0b326f38748`.

## Reader improvement

- Add an opening native jump to a short practice section after the showdowns.
- Ask the reader to name each player's five cards before revealing an answer,
  explain the category and deciding rank or tie, and compare the explanation.
  Different physical selections may have the same five-card value.
- Link directly to `/poker/free-poker-learning-path/#card-basics`, which already
  provides a worked selection, ten optional changed hands, script-enhanced card
  selection and native answer panels when that enhancement is unavailable.
- Invite one changed-hand attempt and one private correction or question. Reuse
  the existing study card and the guide's kicker-and-tie explanation. The reader
  can pause or choose another hand.

The ranking examples, physical cards, answers, source references, viewer-reference
download and next viewer-guide link remain intact. This is a teaching sequence,
not a claim that anyone completed it, learned the material or became ready to
play for money. The original fictional-example and away-from-live-play guidance
continues to apply.

## Bounded scope

Editorial changes are limited to `_source/poker/hand-rankings.html` and its
complete record in `_source/pages.json`. Publication remains October 5, 2026;
the substantive October 27 revision is visible and matches the catalog wording.
The source-review date remains separate.

The existing `assets/poker-hand-lab.css` also gains a course-only system-font
fallback when the browser disables scripting. Five generated paths change: the
ranking guide, the course's stylesheet reference, the general search index, the
poker finder and sitemap. There is no new route, exercise, card set, download,
stylesheet, runtime script, account, answer submission or tracking event.

## Native arrival repair

The new keyboard journey exposed an existing destination defect. With scripting
disabled at 768px, the native `#card-basics` arrival initially placed its heading
at y=207px. A later font swap shortened preceding content by about 739px without
correcting the scroll position, leaving the heading at y=-531px. A separate
1440px attempt also missed the heading. Hidden panels and disclosure states did
not change, and an uninterrupted journey reproduced the problem without the
spacing or print probes.

A scoped `@media (scripting: none)` rule keeps this course's existing fallback
font families for browsers that disable scripting. It does not change the
script-enabled course, add a navigation handler or alter the lesson content.
The native journey then passed at 320, 390, 768 and 1440px, including a 768px
case with the font stylesheet deliberately held until DOMContentLoaded. The
course fetched no WOFF resources in those no-script cases; the headings stayed
below the sticky header and the native answers remained available. The final
browser suite checks the actual shipped CSS without a test-only override.

The [MDN scripting media-feature documentation](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/scripting)
describes this browser setting. Extensions that selectively block scripts can
still report scripting as enabled; the rule targets browsers with scripting
disabled, not every extension's blocking method.

## Review and release qualification

Independent editorial review checks that the destination supports the promised
practice sequence. The existing hand-lab browser suite is extended for the
native reference-to-practice journey, keyboard navigation and fragment visibility,
four screen widths, JavaScript enabled and disabled, enlarged spacing, printing,
and access to the unchanged private study card. The existing numerical and
physical-card checks remain responsible for the original exercises.

A test-only predecessor layer binds the eight production files and the complete
metadata change to the genuine published parent. It reverses only exact approved
current bytes, validates each reverse span and the complete predecessor hash,
and leaves unknown edits visible. Older frozen records and expected historical
values are retained. Current generated-output and discovery checks remain
separate from archived comparisons.

The complete hosted unit suite, all five browser groups and the final aggregate
check must pass on the final candidate before merge. The merge tree must match
that candidate, then Pages deployment and exact live-response verification must
identify the merged release. Final receipts belong in the PR; this preparation
record does not establish that those gates passed. A consenting beginner's
actual comprehension remains a separate observation to collect.
