# Facilitator protocol

**Draft for review and rehearsal. No sessions have been conducted.**

## Before the round

Confirm the two actual human decisions described in README.md: core teaching
review and new follow-up task/key review. A pending decision or unresolved
material error means learner sessions wait. A colleague can rehearse the draft
for timing and clarity; label that rehearsal and exclude it from learner counts.

Plan 40 to 50 minutes per adult. Choose a target of 6 or 8 usable skill slots
before the round; if recruitment ends at 7 or earlier, report the actual number
and missing coverage. Six to eight is a planned target, not a cap on all starters.
Use these slots, assigned before seeing anyone's performance:

| Planned slot | Lesson and follow-up | Purpose |
| --- | --- | --- |
| 1 | L1 / T1: first-decisions | Cards, legal response, additional call |
| 2 | L2 / T2: starting-hand-decisions | Blind contribution and action order |
| 3 | L3 / T3: first-flop-decisions | Made hand, draw, available action |
| 4 | L4 / T4: turn-and-river-decisions | Rebuild hand and separate price from equity |
| 5 | L5 / T5: ranges-for-beginners | Possible holdings versus frequencies |
| 6 | L6 / T6: betting-with-a-purpose | Bet purpose and missing response information |
| 7, if planned | L1 / T1 | Repeat the first skill |
| 8, if planned | L2 / T2 | Repeat the second skill |

If a planned slot's follow-up is exposed, missing or interrupted, retain the
original record and add a separately labeled replacement session for that skill.
Use an already reviewed problem with a new adult who reports not seeing it;
do not improvise a replacement problem. A new problem needs its own review and
fingerprint and belongs to a separately labeled extension. More than eight
actual starters is allowed. Report the original cohort and replacements
separately, including why each was added, and retain an all-starters total.
Do not add people to reach a favorable entry ratio or replace an observed error.

Record self-reported prior play/study, prior site exposure, device/browser,
viewport and access setup. No exact age, gambling history, account details or
identifying life story is needed; confirm only that the participant is an adult.
These are likely learners, not expert poker evaluators. Do not select only
successful sessions or change the skill after seeing a response.

Make a private copy of the blank forms. Choose a private storage location,
access list and deletion date before recruiting. Default to written notes with
no audio/video recording. If recording is useful, obtain separate explicit
consent and explain its scope and deletion date first. A refusal to record is
compatible with participating. Completed forms and raw quotations stay private;
Nolan reviews any proposed anonymized public summary before publication.

Run `check_kit.py` in the checkout that matches the deployed release. Run the
ordinary `_scripts/check_live.py` release-byte check if using nolankido.com.
Record the full release SHA and fingerprint, not just today's URL. Keep site
content fixed during the round. A local rehearsal can use `python -m http.server`
with that checkout, but must be labeled local and must not be pooled silently
with live-site navigation results. Do not change analytics or add answer tracking.

## Opening, about 5 minutes

Read, with the agreed dates and storage details filled in:

> We are checking how this learning website explains poker. We are assessing the
> website, not judging you. We will take coded notes about what you try and say,
> stored privately until [date] with access for [people]. There is no wager,
> account or purchase. You can skip a question or stop at any time. We will not
> publish your name or raw answers. May we proceed with written notes?

Confirm adult status, consent and preferred input/reading setup. Allow questions.
Do not teach poker mechanics before the tasks. Read ordinary task text aloud if
requested as an access accommodation; do not explain its meaning. Record that
accommodation separately from content or navigation help.

## E: Find the first learning task, up to 3 minutes

Start everyone at `https://nolankido.com/poker/`, at the top in a fresh tab with
no retained scroll or open feedback. Start timing after reading:

> You want to learn the basics of hold'em using this site. Find where you would
> start learning, and show me the first activity you would try. Tell me when
> you have found it.

Say no menu, course, lesson or button labels. At 30 seconds, quietly record
whether they have reached either advertised starting activity without help:

| Accepted route | Observed activity required |
| --- | --- |
| /poker/first-decisions/ | Learner identifies its short first-pass explanation, worked example or independent attempt. |
| /poker/free-poker-learning-path/#card-basics | Learner identifies the card names, goal or worked selection offered by the site's explicit new-to-cards route. |

The course overview alone or an unrelated reference is not arrival. A person
choosing the advertised card-basics prerequisite has found a valid first activity;
record which route they chose and analyze the two routes separately as well as
combined. Do not code card basics as a wrong destination because it precedes
lesson 1. The URL fragment alone does not prove the activity was identified.
Record the URL/fragment and what they identify, not just a yes/no. Continue
unaided to 180 seconds unless they stop. Record eventual arrival separately
from arrival within 30 seconds. This same start/prompt/definition can be reused
after cycle 4. A timing comparison is descriptive, not proof of learning.

Do not rescue during the independent interval. If they request help, record the
request and end the unaided attempt. Then assist only enough to move on, logging
the exact words. A later correct destination does not erase that intervention.
Any live-site error, access barrier or interruption gets its own note and actual
elapsed time; do not quietly remove that session from the round.

## L: One assigned short lesson, up to 10 minutes

After locking the entry observation, navigate to the assigned lesson if needed.
This setup is not an independent navigation success. Start at the page top; use
its normal first-pass explanation and worked example. Read:

> Use this page to work through its short lesson. When you reach its try-it
> question, explain your answer before opening its feedback. You can say
> anything you are unsure about.

Record the explanation verbatim or in close notes and what was visible when
given. Stop the independent attempt at 10 minutes, a help request, or feedback
exposure. Feedback opened early is exposure, not a scored independent answer.
Do not prompt with content such as "subtract the blind" or "count the spades."
If silence needs clarification, use only "What are you thinking?" Record every
prompt; a task restatement adds no content, while any directional cue counts
as help. Allow uncertainty and wrong answers without confirming either.

Use the cycle 2 answer key for L1-A through L6-A only after locking the response.
Score the lesson against the applicable rubric criteria and record the exact
error. This isolated-lesson sample may reveal missing prerequisite knowledge;
it is not evidence about completing the entire six-lesson course.

## R: Use the repair, up to 5 minutes

Read after the independent response has been preserved:

> Use the page's feedback and any further explanation it offers. Show me where
> you would go to resolve something you were unsure about, then explain what
> you would change or keep in your answer and why.

Observe feedback discovery, repair-link discovery, arrival and the explanation
separately. Let the person choose and follow a repair even when their answer was
correct; mark it as confirmation rather than error repair. If no uncertainty
or change is identified, record that, not an invented repaired error. Do not
point out a particular link or teach a reason until this observation is locked.
Anything the facilitator then explains is logged as content help.

## B: Short break, target 10 minutes

Close lesson/feedback and take a neutral break without poker study or discussion.
Record the actual interval from the last poker explanation until the follow-up
problem is shown. Allow a shorter interval if needed and label it. Do not describe this
as week-later retention or a validated spacing interval. No answers or follow-up
problem are shown during the break.

## T: Changed problem, up to 5 minutes

Show only the assigned T1 to T6 section of participant-tasks.md, in a separate
plain-text view or on paper, with no key or lesson beside it. Ask first:

> Have you seen this particular problem or its answer before today?

Record yes / no / unsure. Public availability is not proof of exposure or
unfamiliarity. If yes or unsure, retain the attempt labeled exposed/uncertain,
and exclude it from the unfamiliar-problem denominator. Do not improvise an
unreviewed replacement to recover a favorable count.

Read the printed prompt without hints. The participant may explain aloud or
write, using blank paper if helpful. Record the first response before any
feedback, prompts beyond a neutral restatement, or external lookup. Score each
of the three proposed points separately: supported / error / not demonstrated.
A correct number with an incorrect reason is an error for that reasoning point.
Not attempted, early answer exposure or a technical interruption is not a zero
understanding score. Log its status, elapsed time and any help separately.

Do not combine the three points into a mastery grade or combine different skills
as an equivalent test. The fresh problem changes cards, payments or response
assumptions, but has not been validated as equally difficult to its lesson.
This round cannot establish a causal learning gain without a comparable pretest
or control. These six probes do not cover every cycle 2 rubric criterion.

## Close and analyze

After all independent observations, explain any unresolved mechanics accurately,
ask what was hardest and what they expected next, and thank them. Record the
debrief separately from scored attempts. Honor a request to stop or remove notes
under the agreed consent arrangement.

Use summary-form.md for actual counts with denominators, including incompletes,
help requests, early feedback exposure and task familiarity. Review doubtful
explanations with the qualified reviewer; retain disagreements. Report device
and recruitment limitations. At 6 to 8 people, use cases and counts, not a
population percentage, significance claim, or validated pass threshold.

Choose the next change by observed impact: blocked entry/repair or a material
misunderstanding first, then repeated confusion, then isolated friction. Tie
each proposed fix to specific coded observations and a follow-up check. One
severe access barrier can merit a fix even without repetition. Cycle 4's planned
7-of-8 within 30 seconds is a future iteration target, not a result of this kit.
Keep its first eight preplanned entry observations distinct from any supplemental
sessions; replacement sessions must not improve the original cohort's ratio.
