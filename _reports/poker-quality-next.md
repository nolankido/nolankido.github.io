# Poker quality: current handoff

Updated October 7, 2026. This is a non-public-site maintenance record, not an
article, a personal result, or a promise of future work. Check current refs, open
pull requests and actual authorization before starting another change.

## Prepared in this change

The public Poker catalog now refuses a `published` or `updated` date later than
the current UTC date. The catalog already documented that it has no scheduled
release mechanism, but the validator previously accepted a future-dated approved
record and the normal build would render it immediately. The new check makes the
validator match that documented release model.

The validator accepts today's date, rejects tomorrow's date, retains the existing
rule that an update cannot precede publication, and rejects a non-date test clock.
The injected `as_of` date exists so boundary tests are deterministic; normal builds
use the current UTC date automatically. Existing catalog entries and generated
site files are unchanged.

## Executed evidence

Reconstructed source tree before this change matched current main's Git tree
`5b1a9088606ed1bfbe5d5b2436f09a9890ba2b3d`, corresponding to main commit
`3c4f66032f5c50841106283907fe6454cc05ab02` at the start of this work.

Before the repair, a synthetic approved story dated one day in the future was
accepted by `poker_content.load`. After the repair, the future publication and
future update cases are rejected while same-day publication and update cases are
accepted.

Commands actually executed after the repair:

```
git diff --check
python _scripts/build.py --check
python -m unittest discover -s _tests -p 'test_poker_content.py' -v
python -m unittest discover -s _tests -p 'test_*.py' -v
python -m py_compile _scripts/poker_content.py _tests/test_poker_content.py
```

Results: 49 generated files checked with zero changes; 13 focused catalog tests
passed; all 99 unit tests passed; Python compilation and whitespace checks passed.
No browser appearance changed, and no browser pass is claimed for this validator
only change.

## Previous release-safety repair

Main already contains the stale-generated-page guard from PR #10. It refuses
orphaned generated Poker HTML before any build output writes and does not delete
files automatically. That earlier change is separate from this date validation.

## Next useful priorities

1. Publish this date-validation change only after rechecking current main, the
   branch head and exact-head CI. Verify deployment separately after any merge.
2. Exercise the existing episode publishing flow with fictional fixtures for
   missing media, chapter times, spoiler placement and empty collection states.
3. Inspect confirmed reader issues before changing presentation: mobile focus,
   long outlines, answer disclosures, print output and local search recovery.
4. Revisit manual contrast flags only when a rendered element can be identified
   as an actual problem; do not change the palette from scanner uncertainty alone.

Avoid expanding the library merely to raise its page count. Preserve the current
guide set, Decision Labs, established URLs, Technology-first homepage, contact
handling and Umami settings unless a specific reviewed Poker-only repair requires
otherwise. Do not expose private notes or footage.

## Release procedure

Use an isolated, narrowly scoped branch. Do not compete with another writer. Run
checks without weakening them. Require passing checks for the exact submitted
head before merging, then verify Pages and live content separately. Record actual
evidence and limitations rather than inferred deployment state.
