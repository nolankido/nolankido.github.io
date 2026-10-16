# Poker Foundations: make position visible

Reviewed October 16, 2026, against published commit
`515ca7e2fec02ed8177d3e0aa474a7a28fce5dc6`.
This is a content and interface review, not an observed beginner study.

## Finding

Lesson 2 explains a six-player table, two different seats and the change in
action order after the flop entirely in prose. The private cards have diagrams,
but the surrounding table does not. A complete beginner has to construct a
mental seating chart while counting a call and distinguishing earlier actions
from players who have not yet acted. That is an avoidable requirement for the
first lesson about position.

## Change

The existing worked and changed examples now each include a six-seat table map.
Seats stay in clockwise reading order in the HTML. The visual layout places
them around a table, with numbered seats, the dealer button, the current player,
folds, earlier turns, pending initial turns and payments on this round. Text and
border styles carry the state as well as color. These are ordinary readable
lists, including when scripts or styles are unavailable.

The worked explanation compares the blinds' remaining initial preflop turns
with the order on a hypothetical flop if all three live seats continue. The
changed explanation makes the same comparison with four live seats and the
learner in the small blind. That second comparison remains inside the closed
answer, so the learner can first explain the changed situation. Both explain
that later bets or raises can return action to an earlier player.

The maps reuse the two existing examples, cards and prompts. Their small `table`
records live alongside those cases in `course-lessons.json`. The renderer checks
the bounded scenario: six players who started with 100 counters, 1/2 blinds,
no antes or all-ins, and an initial turn before the big blind acts. These are
teaching diagrams, not a general poker engine or a recommended action. The
conditional flop order does not claim that every seat will actually continue.
The two-player blind rules are explicitly outside this diagram's scope.

The six original full articles, study-card prompts, scoring, scripts, downloads,
course order and URLs remain. No new page or service is added. The short-lesson
revision date now uses its explicit page metadata; the revised lesson is dated
October 16 while unchanged short lessons retain October 15.

## Verification and limits

The [PokerStars Hold'em rules](https://www.pokerstars.com/poker/games/texas-holdem/),
checked October 16, specify clockwise action starting after the big blind before
the flop and at the first remaining seat after the button on later streets.
They support the mechanical order shown here, not a strategy recommendation.

Check both diagrams' seats, current player, folds and payments against the
original examples. Independently check both initial-turn queues and hypothetical
flop orders. Verify that the changed comparison starts closed, all six seats stay
readable at narrow widths and with expanded text, keyboard disclosure works,
printing includes the explanation, and the maps survive disabled scripts.
Retain the exact prior release through a SHA-bound adapter; do not refresh old
golden files. Record executed results in the PR and verify production bytes.

The design inference is that a visible table reduces the need to reconstruct
the same arrangement from prose. It does not establish better comprehension or
retention. Observe a beginner explaining who acts next in an unfamiliar seat,
then repeating the task later without the map before drawing that conclusion.
