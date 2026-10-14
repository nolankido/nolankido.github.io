# Beginner understanding: practice, repair and real feedback

Base production: `7d8bf3fddc63fe1cc1fd5f1751fcda93823527e5`, PR #73.
Reviewed October 14, 2026. The owner explicitly asked to improve lesson quality
and content around the remaining uncertainty about actual beginner use.

## What the existing evidence establishes

The preceding release is published: its exact reviewed candidate passed 571
unit/content tests and 42 browser suites. Pages succeeded, and the publication
job passed all 413 targets with the matching merged-SHA marker. The existing
four foundation lessons, range introduction and betting-purpose lesson are
available to readers. Their card and chip models have independent checks.

Those results do not establish what a novice understood. The main checks are
worked examples with answer panels. A reader could recognize an answer, guess
correctly or skim the explanation without being able to handle another scene.
The earlier course also leaves its two follow-on lessons outside the numbered
foundation route, and its generic correction links give little guidance on the
kind of feedback that would help a revision.

A narrow search of the connected inbox for poker/beginner/lesson feedback tied
to the website and its contact service found no matching messages. This is not
an assertion that every possible feedback source was exhausted. No participant
observations, survey responses or learning outcomes were invented.

## Implemented changes

The new `/poker/beginner-checkpoint/`, “Can you explain the next hand?”, contains
about 2,700 words of original teaching content. It has six main situations and
six changed situations for retry, with 12 native answer panels. Each main
situation supplies three explanations, a correct explanation, reasons the other
two fail, and a precise repair link. Correct letters vary across BCABCA.

| Skill | Misunderstanding exposed | Fresh retry |
| --- | --- | --- |
| Call accounting | Announced total confused with additional chips | A new flop bet after preflop payments |
| Position | Button or a matched wager treated as the end of everyone else's action | A heads-up flop that checks through |
| Hand and draw | Four suited cards treated as a flush, or a draw hides a made pair | An unsuited turn changes a kicker but leaves the draw incomplete |
| River call price | Current pot used as final prize, or price treated as a win chance | A different relative bet changes the threshold |
| Ranges | A hand label overrides a known card, or a check exposes hidden strength | One shown hand still cannot validate frequencies |
| Betting purpose | A pair or an eventual fold treated as sufficient proof of a good bet | Two supplied opposing alternatives make checking better than betting |

The reader chooses two situations, gives a reason before opening the answer,
and optionally records certainty in private notes. A correct letter is not an
automatic mastery label. The retry supplies another application after a repair,
rather than asking the reader to repeat the revealed letter.

The new blank TXT workbook contains the same six main prompts, their choices,
six retry prompts, answer/repair URLs and spaces for reasoning. Its complete
native preview is rendered from the actual file, not a second copy. Nothing is
uploaded or saved by the lesson. Existing worksheets and their contents remain
exact.

All six beginner lessons now contain a small native invitation to try a changed
situation and report unclear wording. The free learning path adds a short next
step connecting ranges, betting purpose, checkpoint practice and the workbook.
The original four-lesson route and five-session source text remain exact.
Only the learning path's description and revision record change; original
publication date, URL and title remain stable.

Reader feedback uses the existing contact route. Four prompts ask for the page
or situation, intended understanding, confusing wording/step and what would
help. It is voluntary; the contact form's required name/email and privacy terms
are stated. No quiz responses are transmitted automatically. The contact code,
form fields, anti-spam behavior, endpoint, analytics and privacy text remain
exact. An optional friend activity asks the learner to explain before coaching,
then use a repair and retry. It is a proposed activity, not a completed study.

## Checking the work

The production snapshot pins 177 page records, 204 outputs and 363 input files,
including the five affected build scripts. Every old article source is exact.
Only four catalogs and four build/live-check scripts change among those inputs.
Frozen inverse adapters require the entire reviewed current-file digest before
reversing exact offsets. Earlier golden digests remain intact; an unreviewed
claim or arithmetic change remains visible.

Ten new independent tests check the six varied answer keys and repair/retry
pairs, legal cards and best-five hands, both call thresholds, known-card
exclusions, the two-hand check/bet payout comparison, exact workbook preview
and prompts, six invitations, publication targets, prior source/metadata and
feed identity, privacy boundaries and negative controls. Current counts advance
only for the new article, title card and workbook.

Build reproduction, HTML5 and search audits pass at 178 pages, 97 articles,
173 sitemap URLs and 205 generated outputs. Search section data is 59,659 bytes
under the unchanged 60,000-byte limit. The typographic sharing preview was
inspected. All 581 local unit/content tests pass after the corrections below. The hosted
candidate gate and publication receipt are recorded in the PR after execution.

The hosted checkpoint journey checks four widths, 48 keyboard answer openings,
all five displayed cards, six lesson invitations, the course arrival, three
search arrivals, an actual repair/return/retry journey, exact download and
preview, print headings, no-JavaScript use, storage/cookie invariants and two
scoped accessibility scans. Six mobile/desktop opening/card/answer images are
required for visual review. This managed environment uses the existing hosted
browser workflow; no local browser was installed.

The first focused run found a wording assertion mismatch, a current-versus-
historical live-body comparison, and a temporary catalog fixture that had not
copied the new workbook dependency. The arithmetic and card checks passed.
Those fixtures retain their original invariants after correction. The first full
regression caught a missing visible revision note on the study path and two
outline assertions that omitted the new build decorator. The visible note was
added and the outline checks now include the complete rendered source. A static
review also corrected the browser invitation selector to target its containing
aside instead of the heading. No card, chip or strategy model changed.

## A concrete next round with real beginners

No one has been contacted or enrolled by this change. When volunteers are
available, use a short manual session on their usual device and keep observations
private. Explain the purpose, allow pauses and let them decline. Do not record
audio, video or identifying information by default.

1. Ask the person what they want to understand: watching a hand, interpreting
   an action or studying a decision. Observe whether they can choose a useful
   first lesson or checkpoint situation through the public navigation.
2. Choose two relevant situations before any answer is open. Ask what the
   wording means and what their reasoning is. Keep guesses, terminology issues
   and navigation issues distinct from a conceptual error.
3. Let the person open the explanation and follow its repair link. Observe
   whether they can return and explain the changed situation without the first
   answer in view. Note where a hint was required instead of counting that as
   unassisted success.
4. Ask which sentence or example made a difference and what remains confusing.
   Record their meaning in a private note without publishing their words or
   identity. A successful retry is an observation within that attempt, not
   evidence of durable learning.
5. Revise the specific explanation supported by those observations, verify its
   card/chip model and links, then revisit that task with another willing
   reader. Preserve contradictions and failed repairs rather than selecting
   only praise or successful attempts.

Use a private row with the situation, initial reasoning, certainty, repair used,
retry reasoning, help given, exact sticking point and next content change.
There is no planned public leaderboard or learning-effect percentage. Pageviews
and answer-panel availability do not establish comprehension. The optional
feedback form route is a way to obtain reports, not proof that reports arrived.

## Primary references and limits

Mechanics were checked against the publisher's own references on October 14:

- https://www.pokerstars.com/poker/games/rules/hand-rankings/
- https://www.pokerstars.com/poker/learn/lesson/pot-odds/

The observation approach was informed by GOV.UK's guidance about task completion,
neutral facilitation and listening to the participant:
https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing.
It is not evidence that this particular adult poker lesson improves learning.
School feedback guidance was considered but is not used as proof of an adult
self-study outcome. Card scenes, alternatives and calculations are original.
No profit, solver validation, participant endorsement, ranking gain or completed
learner study is claimed.
