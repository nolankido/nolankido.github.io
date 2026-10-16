# Poker Foundations: beginner observation kit

Roadmap cycle 3, prepared October 16, 2026 UTC.

**Preparation only. Teaching review, recruitment and observations are pending.**
There are no participant records or results in this kit. It does not close cycle
2 or 3, establish learning gains, or authorize a claim that the course works.

## Use the kit

1. Complete the qualified human review in
   [the cycle 2 handoff](../poker-teaching-review/README.md), resolve material
   issues, and retain its actual decision and fingerprint privately. Ask the
   same reviewer to inspect the six new follow-up problems and scoring points
   in [facilitator-key.md](facilitator-key.md), using a private copy of
   [probe-review-form.md](probe-review-form.md). Record corrections and a separate
   decision for the exact kit fingerprint. Both decisions are prerequisites for
   learner sessions. The checker cannot grant either decision.
2. Read [protocol.md](protocol.md). Nolan plans 6 to 8 consenting adults who
   want introductory hold'em instruction. No invitations have been sent. Use
   their usual devices and include different screen sizes and access needs
   where possible. Do not exclude someone because they use assistive technology.
   Additional labeled sessions may fill an exposed or incomplete skill slot;
   retain every original starter and report replacements separately.
3. Copy [session-form.md](session-form.md) and [summary-form.md](summary-form.md)
   **outside this public repository** before filling anything in. Use one session
   form per person. Keep contact details and consent records separately from
   coded observations. The public GitHub source is public even when unlinked.
4. Run the read-only check below. Record its fingerprint, the deployed release
   SHA, actual dates, reviewer decisions and any deviations in the private forms.
   Use the same verified release throughout a round. A teaching or kit change
   requires a new fingerprint, review of the change and a separately labeled round.
5. Show only the assigned problem from [participant-tasks.md](participant-tasks.md)
   at the follow-up stage. Keep the key closed until the independent response is
   recorded. These tasks are public, so ask about prior exposure rather than
   assuming they are secret or unfamiliar.
6. Aggregate actual counts and explanation errors using the summary form. Retain
   incomplete, assisted and previously exposed attempts with explicit labels.
   Use the observations to choose cycle 4's first screen change. Do not substitute
   generated answers, colleagues' rehearsals or browser tests for adult sessions.

```sh
python _reports/poker-beginner-baseline/check_kit.py
python -m unittest discover -s _tests -p test_beginner_baseline.py -v
```

The standard-library checker verifies the existing teaching packet, renders the
separate prompt/key files, and checks the new problems' physical cards, best-five
ranks, candidate comparisons and numeric call prices. It reuses the independent
cycle 2 card oracle, not the production renderer. It cannot grade a person's
explanation, validate the research instrument, prove every prose claim, observe
unfamiliarity, or certify a reviewer. It makes no network requests and reads no
learner records. All forms remain blank.

To edit a draft, change `tasks.json` and regenerate only the two derived exhibits:

```sh
python _reports/poker-beginner-baseline/check_kit.py --write
```

The fingerprint covers this folder's authored protocol, forms, problem data,
checker, generated exhibits, and the cycle 2 scope fingerprint. It is a revision
identifier, not a human approval. No dated readiness or result file is generated.

## What this round can establish

The round asks where people get stuck finding the course, attempting one short
lesson, using its repair, and explaining a changed problem after a short break.
Each person samples one skill. Six sessions cover all six; eight add repetitions
of skills 1 and 2. A single observation per skill cannot validate that skill or
rank lessons by effectiveness. The common entry task is the only task shared
by everyone. This is an initial qualitative baseline, not a controlled learning
experiment, population estimate, or week-later retention study (cycle 9).

The session design uses neutral task goals, observation and an advance discussion
guide, following [GOV.UK's moderated usability guidance](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing).
Its [research planning guidance](https://www.gov.uk/service-manual/user-research/plan-user-research-for-your-service)
distinguishes small qualitative rounds from large quantitative benchmarks.
These references were read October 16, 2026. The specific poker tasks, allocation,
time boxes and scoring points are proposed here and require review and rehearsal;
neither source validates them or the course.
