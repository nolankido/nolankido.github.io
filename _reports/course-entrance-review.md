# Poker Foundations: put the course route first

Reviewed October 16, 2026, against published commit
`2e9f369d57be882cc9ffbaf983056af3f4d1e07e`.
This is a source, task and interface review, not an observed beginner study.

## Finding

The course already has six short lessons and a complete-hand finish. In document
order, its overview places card foundations and ten changed card-building hands,
a six-scene guided hand and three betting-rehearsal starts before the lesson map.
The copy calls these tools optional, but the page order still presents them as
the route to reach the course. A novice has to distinguish the supporting tools
from the six lessons while choosing where to begin.

## Change

| Visitor task | New route |
| --- | --- |
| Start the first lesson | Primary start controls directly under the course title, plus a lesson-1 link at the map |
| Learn unfamiliar card names first | Card basics and a worked selection, with a direct continuation to lesson 1 |
| Find the course sequence | The six-lesson map and finish come before the supporting tools |
| Repair one difficulty | A three-tool menu explains when card practice, a guided hand or betting rehearsal is useful |
| Return after practice | Visible lesson-map links and direct lesson-1 continuation from card foundations |

The existing six lessons, goals, quick checks, worked exercises, complete hands,
downloads and permanent targets remain. The supporting tools stay usable in the
native document and with scripts enabled. Moving them does not hide an exercise
or require another interaction to reach a known fragment. The reading estimate
still includes the whole page and is explicitly distinguished from a class
duration. This release does not add another syllabus, question bank, script file,
account, stored learner state, email service or purchase flow.

The first captures showed the original article header pushing the start controls
below the opening screen. The renderer now moves that existing control row under
the course title. The browser journey checks that the primary action is in the
initial viewport at all four tested widths; titles and other page headers retain
their existing structure.

Native section navigation on this long course overview uses immediate arrivals,
matching the short lessons. This lets a keyboard visitor move between the map
and practice without competing focus and smooth-scroll movements. It does not
change the content or the exercise logic.

Moving the map ahead of the card lab exposed an early bookmark scroll that could
finish before the page and fonts settled. The existing hand-lab script now
aligns its selected hand after those layout changes and cancels a pending
alignment when a learner has focused a control. Scoring and exercise data are
unchanged. Browser checks include held-font arrivals and interaction before the
fonts arrive; the fifteen other JavaScript files remain byte-identical.

## Verification and limits

Check that the core route precedes all three tools, that the six lesson titles
and destinations match the canonical course data, and that every prior fragment
survives once. Preserve the exact predecessor through a SHA-bound adapter.
Verify primary lesson entry, each practice-menu arrival, card-basics continuation,
return-to-map links, narrow layouts, keyboard use, disabled scripts and unchanged
exercise behavior. Review fresh mobile and desktop captures before publication.
Record executed checks in the PR and verify production bytes afterward.

The initial CI run passed all 702 unit tests in 587 seconds, then reached the
build job's ten-minute deadline during the remaining checks. The build deadline
is now fifteen minutes. All unit, syntax, browser and publication gates remain;
the change gives the existing suite time to finish rather than skipping checks.

The design inference is that presenting the course before its supporting tools
makes the intended sequence easier to distinguish. It remains untested with real
beginners. Observe whether a new visitor can find lesson 1, explain what is
optional, use one tool for a stated difficulty and return to the lesson without
coaching. Do not treat a clicked link or completed automated journey as evidence
of learning or willingness to pay for a later course.
