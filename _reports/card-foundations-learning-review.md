# Card foundations and constructive hand practice

Reviewed October 15, 2026 against published commit
`dd80b250369b61da19220f23c58324c2936dfd8f`.

The current course already has a coherent six-stage route, a continuous guided
hand, eighteen varied questions, mixed practice, specific feedback and private
study cards. Repeating those additions would not address the next gap.

This is a task and content audit, not observation of actual beginners. It cannot
measure learning gains, retention or completion. The expected instructional
effects below are design judgments.

## What a complete beginner still had to supply

The opening guided scene starts with six seats, blinds, stacks and a button.
The first lesson begins by treating knowledge of the hand rankings as a starting
point. Its first pass reaches cards, actions, call amounts and best-five rules,
but the complete visual ranking reference sits on a different page. A learner
could reach decisions about a pair and a draw without first constructing a
five-card hand.

The guided hand and practice room ask readers to select descriptions or stated
five-card results. Their explanations are useful, but recognizing the correct
description does not demonstrate that a learner can choose those actual cards
from seven. This is an observable difference between tasks, not a claim about
the performance of unseen learners.

## Implemented learning sequence

| Step | Beginner task | Implementation |
| --- | --- | --- |
| Orientation | Explain the goal and identify cards | Two ways a hand can end, ranks and face-card codes, four suits, private versus shared cards, flop/turn/river order. |
| Worked selection | Explain why two cards are excluded | A seven-card example shows a complete best five and why a private low card does not play. |
| Construction | Choose the actual five | Ten fixed hands cover all nine mathematical hand categories, zero/one/two private cards, ace-low straights, kickers and equivalent physical selections. |
| Feedback | Identify the rule behind a weaker selection | Separate a weaker category from lower ranks within the correct category. Provide an optional hint and worked solution. |
| Review | Choose one correction to revisit | Retain weaker attempts after correction and distinguish a hint or requested solution. Report only hands actually attempted or helped during this visit. |
| Continue | Connect cards with decisions | Continue to the existing guided hand, six stages and varied question bank. Stages 1, 3 and 4 link to relevant construction cases. |

The bank is returnable practice: the course explicitly suggests trying one hand,
pausing or continuing to the guided hand, then returning to other cases later.
There is no requirement to finish the ten hands before studying the actions.

The foundations and lab live within the existing free course. No new page,
article, guide count or competing course is introduced. The opening provides
four direct routes. The existing visual chart is reused from the hand-ranking
reference, so its explanations and graphics are not maintained twice.

All exercises use completed fictional Hold'em boards. They do not infer hidden
opposing cards, evaluate a betting strategy or grade readiness for real-money
play. A board-only best hand is not assumed to beat every opponent. Equally
strong five-card selections using different physical cards are accepted.

## Evidence and limits

The [IES study practice guide](https://ies.ed.gov/ncee/wwc/PracticeGuide/1)
supports worked examples alternating with attempts, graphics paired with words,
concrete and abstract representations, retrieval and explanatory questions.
Applying those recommendations to a card-selection interface is an inference;
the source does not validate this site or establish a poker-study schedule.

Rules were checked against [PokerStars' Hold'em rules](https://www.pokerstars.com/poker/games/texas-holdem/)
and [traditional hand rankings](https://www.pokerstars.com/poker/games/rules/hand-rankings/).
Their commercial offers are not required to use this course. There are no
invented solver outputs, personal hands or learner success statistics.

The fixed bank and repeated examples are disclosed. A correct selection does not
verify the learner's spoken explanation or transfer to an unfamiliar hand.
Review labels describe interface events, not mastery or whether visible material
was read. Reloading clears answers and notes; the lab has no network or storage
API. Existing pageview analytics is separate.

## Verification contract

An independent Python evaluator checks each solution, all twenty-one selections
per seven-card exercise, and deterministic sampled hands against the production
JavaScript evaluator. Separately, every one of the 2,598,960 five-card hands is
classified and compared with category counts derived from rank/suit combinations.
Native content, hints and solutions work when JavaScript is unavailable; print
shows the full bank and explanations. Browser verification covers keyboard use,
equivalent selections, errors and corrected retries, deep links, partial reviews,
privacy, phone/desktop reflow, text spacing and accessibility checks.

The exact predecessor inventory and hashes are pinned independently. Historical
snapshots are not refreshed; a SHA-gated adapter reverses only this reviewed
change, and unreviewed mutations stay visible. Actual release and deployment
results belong in the pull request and its logs, not inferred learner metrics.
