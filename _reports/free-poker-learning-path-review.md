# Free poker learning path review

Reviewed October 15, 2026. Predecessor: `75dabee7daeb0d20bf696c48621b5fe8faf2968a`.

## Scope and method

This is an inspection of the published course, its six supporting lessons, entry
routes, checkpoint, search and downloads. It follows a complete beginner's tasks:
find a starting point, interpret one hand, explain a rule, attempt a different
example, recover from a mistake, continue and return later. It is not a study of
real learners. No completion rate, learning gain or usability success rate has
been measured. Automated checks establish content and interface properties.

## Findings before the change

| Observed property | Likely effect on a beginner | Priority |
| --- | --- | --- |
| The introduction offered five sessions, the practice map and lesson menus offered four lessons, and two further beginner subjects appeared elsewhere. | The reader had to decide which sequence counted as the course. | High |
| The six complete lessons totaled about 71 minutes by the site's reading estimates, with no consistent limited first pass. | A useful reference could feel like a large prerequisite assignment. Reading time does not include practice. | High |
| Accurate fictional examples and native answer panels already existed. Four map checks and six checkpoint situations had specific repair links. | There was a strong foundation for learning mechanics without a wager. | Preserve |
| There was no single progressively revealed hand on the course overview. | Connecting position, street changes, cards, call amounts and final net gain required several page changes. | High |
| Related links supplied many possible next destinations, including advanced study. | A beginner could leave the sequence before resolving the current gap. | High |
| Immediate answers were available, but return practice was less explicit. | Recognizing recently read wording could be mistaken for independent explanation. | Medium |
| The blank study card covered four stages. | It did not match all the beginner material or support the whole-hand exercise. | Medium |

The likely effects are design judgments, not observed learner behavior. The
previous material explained many concepts carefully; its main weakness was how
the reader was asked to use and connect those explanations.

## Implemented course

1. Cards, actions and the pot.
2. Your starting hand in context.
3. Your first decisions after the flop.
4. The turn, river and showdown.
5. Your first range.
6. Betting with a purpose.

Each stage now has an observable goal, a small set of first-pass section links,
a recall question, a specific fresh checkpoint situation, a previous link and a
visible primary next step. Full lesson explanations remain available as reference.
The first stage includes reading ranks, suits, private cards and shared cards.
The map, six current-page menus, entry routes and worksheet share this order.
The old five tasks retain their fragment destinations as optional further study.

The overview adds one fictional six-scene hand. It gradually introduces initial
action, an additional preflop call, a pair plus a draw, a flop raise, the river and
showdown. Card faces have full accessible names; the pot and remaining stacks are
visible counters. Specific feedback explains each selected mistake. Readers can
retry or continue after an incorrect answer. Changing an answer clears stale
feedback; going back preserves the current visit's work. Search reaches the
precise scene and excludes answer panels.

The supplied betting actions illustrate mechanics and accounting. The exercise
does not invent a universally correct betting strategy, infer an opponent's
frequency from a reveal or grade a call by its result. An independent card
evaluator checks the made hands and winner. Per-scene conservation checks account
for all 600 counters, including the folded small blind. The river call price is
10/57 under explicit heads-up, no-fee, no-side-pot, final-call conditions.

Return practice asks readers to close the explanation, try different checkpoint
situations later, repair one gap and keep a private note. The generated blank
study card contains all six stages, whole-hand prompts and the review routine;
its preview and download come from the same generator. No answer or progress is
sent or stored by the practice script. Existing site pageview analytics is
independent of exercise answers. Print, blocked-script and no-JavaScript readers
receive all six scenes and native explanations.

## Evidence and limits

The design applies the general recommendations on worked examples, explanations,
retrieval and spacing in the [IES practice guide, Organizing Instruction and Study
to Improve Student Learning](https://ies.ed.gov/ncee/wwc/PracticeGuide/1).
This is an application of general learning research to course design. The guide
does not validate this poker course or its suggested review timing.

Mechanics were checked against [PokerStars' Texas Hold'em rules](https://www.pokerstars.com/poker/games/texas-holdem/)
and [hand rankings](https://www.pokerstars.com/poker/games/rules/hand-rankings/).
External strategy advice is not an answer key for the scripted hand.

The course remains introductory standard no-limit Hold'em. It does not assess
profitable play, establish readiness to risk money or cover all house procedures,
fees, short all-ins or tournament prize effects. Following fictional examples
without playing for money is a complete learning option.

## Verification contract

`test_poker_course.py` independently checks the card ranks, counters, call amounts,
net result, six-stage order, real first-pass and checkpoint targets, search scene
destinations, exact worksheet preview, script scope and complete predecessor
hashes. Invalid card, anchor, scene and stage fixtures must fail. Exact historical
adapters reject unrelated mutations instead of refreshing prior release hashes.

`poker_course_browser.py` exercises all six scenes by keyboard at 320, 390, 768
and 1440 pixels. It checks unanswered and incorrect attempts, answer changes,
retry, backward visits, focus, fresh-practice arrivals, the complete next-stage
chain, scene search, deep links, downloads, print, blocked-script and native
fallbacks, text spacing, automated accessibility and practice privacy. Human
inspection of desktop and phone screenshots complements these checks.

The existing unit and browser release gates remain in place. This adds a browser
suite and checks two new assets in the published-byte verifier. The pull request
and deployment logs are the record of actual release results. A later human
study could ask first-time learners to explain a changed example after a delay;
that would provide evidence this inspection cannot supply.
