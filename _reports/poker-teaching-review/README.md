# Poker Foundations: teaching-review handoff

Roadmap cycle 2, prepared October 16, 2026 UTC (October 15 in Hawaii).

**Status: prepared for a qualified human reviewer. Human review is pending.**
The mechanics evidence is an AI-prepared independent cross-check. No reviewer
identity, review session, beginner observation, learning gain or signoff has
been supplied. This preparation does not close the cycle's human-review gate.

## Start here

1. Give the reviewer [packet.md](packet.md), [reference-text.md](reference-text.md)
   and a private copy of [review-form.md](review-form.md). All examples are
   fictional; a deck and counters are sufficient. No wager or outside account
   is needed.
2. Ask the reviewer to solve each attempt before opening
   [answer-key.md](answer-key.md). Then inspect the existing teaching explanation,
   feedback, full reference article and exact repair destinations. The review
   covers all six lessons, 12 short examples, eight stops in two final hands,
   and the six-scene guided hand. The twelve isolated checkpoint situations,
   best-five lab, betting rehearsal, optional practice banks and other guides
   are outside this review's scope.
   Use the snapshot source links and readable exhibits to judge repair content.
   Live links are for navigation checks and may show later edits. Every guided
   scene's repair and any optional feedback paragraph are included in the key.
3. Record **unreviewed / accept / revise / block** against each of the 18
   criteria. Use exact task IDs, an independent reason and an issue ID. A correct
   number alone does not establish that the explanation teaches the right reason.
4. Resolve material mechanics issues and record author/reviewer disagreements.
   Material severity includes wrong cards, action order, contribution, winner,
   call price or an unsupported strategic or learning claim. Teaching issues
   concern unclear instructions, missing assumptions or inadequate repair.
   Editorial issues concern presentation without a change in meaning. An open
   material issue, unresolved disagreement or unreviewed criterion prevents
   signoff. Record any deferred teaching/editorial issue and its reason.
5. Recheck corrections against a new material commit and fingerprint. Keep
   completed forms and personal details outside this public repository until
   Nolan approves a specific public summary. A later summary should name the
   actual scope, date, material revision, reviewer qualifications and unresolved
   limitations. Record an actual review decision separately, bound to the packet
   fingerprint; this preparation record does not become a human signoff.

Nolan can ask an available volunteer first. A suitable reviewer should be able
to independently explain standard no-limit hold'em mechanics, five-card hand
comparison, betting-round contributions and position, and critique beginner
explanations. Ask them to describe relevant teaching or rules experience and
conflicts. Playing experience alone does not establish teaching expertise.

## Files and evidence

| File | Purpose |
| --- | --- |
| [packet.md](packet.md) | Six-skill rubric, current explanations and model/attempt exhibits, final-hand prompts, guided-hand choices |
| [reference-text.md](reference-text.md) | Complete plain text of the six source articles, with links to the pinned originals |
| [answer-key.md](answer-key.md) | Current feedback, repair links, recomputed ranks, candidate comparisons, ledgers and call prices |
| [review-form.md](review-form.md) | Blank 18-criterion scorecard, issue/disagreement log and final disposition |
| [scope.json](scope.json) | Material commit, 14 scoped input hashes, current TDA record, review-instrument hashes and packet fingerprint |
| [mechanics.json](mechanics.json) | 28 reproducible mechanical evidence rows; no human approval or optimal-action score |
| [rubric.json](rubric.json) | Authored acceptance criteria, misconception checks and cross-task mappings |
| [build_packet.py](build_packet.py) | Standard-library generator and stale-packet check; no network requests |

The scope includes the course configuration, all six article sources, the
overview and checkpoint sources, and their three teaching renderers. It pins the
TDA record separately, so refreshing an unrelated resource review does not
invalidate this course review. Site chrome and unrelated pages are outside the
teaching scope. The named material commit remains the source of truth for the
exhibits, even as this repository moves forward.

The card evaluator enumerates five-card selections independently of the site's
renderers. It recomputes the 12 short examples, eight final-hand stops, two
showdowns and six guided scenes. Numeric final-hand fields are checked for
monotonic contributions, current-round calls, river reconciliation, winner and
ending-stack conservation. The guided states and ending must preserve 600 counters.
The checker does not parse prose numbers, judge free-text explanations, estimate
opponent frequencies or prove a legal scripted betting sequence solely from
ledger snapshots. Those are explicit reviewer tasks. No material correction is
proposed from this bounded cross-check; that is not a human accuracy finding.

## Reference basis

Primary pages were read October 16, 2026 UTC. The references establish the
mechanics below, not the effectiveness of this course. Commercial publishers
may advertise gambling. No listed service is needed to conduct the review.

| ID | Primary reference | Use and limitation |
| --- | --- | --- |
| R1 | [PokerStars: Texas hold'em rules](https://www.pokerstars.com/poker/games/texas-holdem/) | Available cards, betting actions, initial action order and street sequence. Strategy suggestions on that page are not imported into this rubric. |
| R2 | [PokerStars: hand rankings](https://www.pokerstars.com/poker/games/rules/hand-rankings/) | Standard high-hand categories, kickers, flush comparison and ties. Other variants are outside scope. |
| R3 | [Poker TDA: current rules](https://www.pokertda.com/view-poker-tda-rules/) | 2026 v1.1 dated September 21; rules 36C, 44-45 and 52 inform heads-up distinctions, raise totals and acting in turn. House/event rules control actual play; these examples omit all-ins and procedural disputes. |
| M1 | Derivation in answer-key.md | Incremental chip expectation for a final heads-up call, with assumptions stated; no empirical equity or strategy claim. |
| M2 | Reasoning check in answer-key.md | A possible holding or one compatible reveal does not identify frequencies; no measured opponent data. |

The six-skill editorial rubric is a proposed review instrument. Its categories
and acceptance labels have not been validated with learners or calibrated
between reviewers. Cycle 3 still requires actual adult beginner observations;
the next screen and practice decisions should use those findings. A later
learner assessment should record independent explanations and hints separately
from this editorial scorecard. No learner score is inferred from these files.

## Reproduce and maintain

From the repository root:

```sh
python _reports/poker-teaching-review/build_packet.py
python -m unittest discover -s _tests -p test_teaching_review.py -v
```

The first command is read-only and is also called by the new regression tests.
It fails if the packet or its scoped teaching inputs have changed. It does not
refresh dates, approve reviews or rewrite the existing preservation baselines.

To prepare a new draft after a deliberate teaching change, first commit that
material. Then use its full SHA:

```sh
python _reports/poker-teaching-review/build_packet.py --write --material-commit FULL_COMMIT_SHA
```

The writer compares all 14 inputs and the TDA record with that actual Git
revision before naming it. It emits a new fingerprint and a blank, pending
review form. Do not overwrite the only copy of a completed private review when
preparing another draft. Check the rubric mappings and generated diffs, then
run the ordinary release gates. Fresh packet generation is preparation for a
new human review, not a replacement for one.
