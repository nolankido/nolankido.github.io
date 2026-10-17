# Poker Foundations: qualified review and observation handoff

**Status: draft. There is no qualified human acceptance or beginner observation on record.** This is a practical next step after the 72-case inventory milestone, not a claim that the practice bank is instructionally validated.

## The next human decision, with manageable scope

The existing [six-lesson teaching-review packet](../poker-teaching-review/README.md) has 18 separate criteria and remains unsigned. The [72-case bank](README.md) also has no qualified reviewer decision. Both facts matter. Automated card, chip and link checks cannot establish whether a novice can understand the prompts or whether their explanations genuinely demonstrate learning.

Use a two-stage review before inviting people to test the material:

1. **Triage 18 cases.** Inspect A, B and one distinctly changed situation in each of the six skills. This stage helps find systematic problems before asking a reviewer to read all 72. It does **not** validate unreviewed cases, equalize form difficulty, approve the overall course or authorize learner sessions.
2. **Review the actual intended teaching and case scope.** Correct material errors, regenerate the bank, complete the full 72-case review if considering the whole bank for public course navigation, and independently finish the existing six-lesson teaching review. If planning a small supervised test involving fewer cases, obtain explicit qualified approval of every **selected case** and the relevant teaching material. A triage exercise is not a substitute for that explicit selected-case approval.
3. **Only then consider 6 to 8 consenting adults for a qualitative observation round.** Follow the separate [A/B observation protocol](protocol.md) or an explicitly approved selection plan with exact case IDs and revisions. One isolated learner card per attempt. Record first explanations and assistance separately. No gambling accounts, stakes, or learner data collection on the public site.

### What the offline tool adds

[review_round.py](review_round.py) prepares a case-bound reviewer bundle with the question file separate from the facilitator key, a human-readable case checklist, a blank machine-readable response file, and a manifest of the exact Git commit and SHA-256 fingerprints of case definitions, question text and answer-key sections.

The script runs on the reviewer's own machine with Python 3.12 or later and standard-library modules. It refuses to prepare material from locally changed case sources, cards, key or generator: commit any proposed corrections first, then generate from a pinned revision. The audit also checks the assembled first-pass questions, answer key and blank review sheet against hashes in the manifest. It makes **no network requests**, records no observations, and has no ability to publish anything or to create a signature. The recipient can inspect material offline and store any completed review record privately. A SHA-256 digest detects changes to the reviewed material; it cannot authenticate a person's qualifications or signature.

From a clone of the repository on the exact commit to review, run:

    python _reports/poker-transfer/review_round.py prepare --mode triage --out ../poker-review-triage

After a first-pass review, use a separate new directory for the full-bank packet:

    python _reports/poker-transfer/review_round.py prepare --mode full --out ../poker-review-full

To review only an explicitly selected subset, never implicitly all 72:

    python _reports/poker-transfer/review_round.py prepare --mode custom --cases S1-A,S2-B,S3-A --out ../poker-review-selected

Each output directory contains five files. **Keep those source packet files unchanged** so the audit can verify them. If using the readable review form, copy 03-review-form.md to a separate private working file before entering any findings; the machine-readable review-record.json is the editable source for the audit:

| Local file | Reader and purpose |
| --- | --- |
| manifest.json | Source commit and exact scope, source/case/question/key hashes, status pending |
| 01-independent-questions.md | Reviewer first pass without the facilitator answer key |
| 02-facilitator-key.md | Proposed reasoning, misconception and precise repair links, opened afterward |
| 03-review-form.md | Blank per-case mechanics, clarity, explanation, repair and accessibility checklist |
| review-record.json | Blank private machine-readable decision record, **not** evidence of completed review |

**Keep the output outside the public Git checkout and do not upload a completed record to GitHub.** The program refuses to write inside this repository or overwrite an existing review directory. The case source and the question/key text can already be read in this public repo; only real reviewer identifiers, signatures, observations and consent records require private handling.

## Checking a real review record

A reviewer must actually inspect the listed cases, provide an independent reason and issue references, disclose relevant teaching/rules qualifications and conflicts, and record confirmation privately. Fill the local review-record.json as an accurate transcription of that review, not as an automatic score. Each reviewed case has five criteria, three separate reasoning-point evidence fields, and an explicit overall disposition. An accepted case cannot have an incomplete/adverse criterion, missing evidence for even one reasoning point, or an unresolved issue. Every non-unreviewed case requires an independent written summary.

Run:

    python _reports/poker-transfer/review_round.py audit --packet ../poker-review-full

The checker rejects changed source, card, key, manifest or case identity, incomplete case scope, missing evidence for claimed decisions, open issues marked accepted, malformed dates, and conflicting case results. A blank record reports human_review_pending and exits with code 2. Errors exit with code 1.

Even a fully filled, consistent record returns **full_review_record_claimed_authentication_required** rather than permission to publish. Someone independent must verify the actual reviewer's identity, qualifications, signed decisions, case scope, and underlying course approval. The result always includes release_authorized: false. A triage or custom scope **cannot** receive a full-bank clearance. A reviewed bank is not a measure of retention, mastery or profitable decisions.

## For a later human observation round

Use the earlier [private session form](session-form.md) and [private aggregate](summary-form.md) after the exact planned cases and six-lesson material receive the required review. Retain exact case IDs, lesson revision, time since learning, all three independent and assisted reasoning points, prior exact/answer/similar exposure, any hints, navigation or repetitions, withdrawals and case flaws. Record each later paired attempt separately rather than treating it as immediate improvement or seven-day retention.

Do not put names, recordings, consent, raw answers or identifiable quotations in this public repository. Store private artifacts with restricted access and a deletion schedule. Do not infer causal effects, mastery, comparative form quality or outcomes for other learners from a small qualitative group.

## Future release decision

A future public course integration needs a **real** and scoped teaching review, material corrections with a new commit where appropriate, successful software checks, and explicit editorial authorization. If any content changes after a reviewer has inspected it, regenerate the packet and request a recheck of affected cases. The current practice bank remains available for inspection and private self-study without being promoted into the main course navigation.
