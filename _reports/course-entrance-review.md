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
| Start the first lesson | A primary lesson-1 link at the entrance and the start of the six-lesson map |
| Learn unfamiliar card names first | Card basics and a worked selection, with a direct continuation to lesson 1 |
| Find the course sequence | The six-lesson map and finish come before the supporting tools |
| Repair one difficulty | A three-tool menu explains when card practice, a guided hand or betting rehearsal is useful |
| Return after practice | Visible lesson-map links and direct lesson-1 continuation from card foundations |

The existing six lessons, goals, quick checks, worked exercises, complete hands,
downloads and permanent targets remain. The supporting tools stay usable in the
native document and with scripts enabled. Moving them does not hide an exercise
or require another interaction to reach a known fragment. The reading estimate
still includes the whole page and is explicitly distinguished from a class
duration. This release does not add another syllabus, question bank, script,
account, stored learner state, email service or purchase flow.

Native section navigation on this long course overview uses immediate arrivals,
matching the short lessons. This lets a keyboard visitor move between the map
and practice without competing focus and smooth-scroll movements. It does not
change the content or the exercise logic.

## Verification and limits

Check that the core route precedes all three tools, that the six lesson titles
and destinations match the canonical course data, and that every prior fragment
survives once. Preserve the exact predecessor through a SHA-bound adapter.
Verify primary lesson entry, each practice-menu arrival, card-basics continuation,
return-to-map links, narrow layouts, keyboard use, disabled scripts and unchanged
exercise behavior. Review fresh mobile and desktop captures before publication.
Record executed checks in the PR and verify production bytes afterward.

The design inference is that presenting the course before its supporting tools
makes the intended sequence easier to distinguish. It remains untested with real
beginners. Observe whether a new visitor can find lesson 1, explain what is
optional, use one tool for a stated difficulty and return to the lesson without
coaching. Do not treat a clicked link or completed automated journey as evidence
of learning or willingness to pay for a later course.
