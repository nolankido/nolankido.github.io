# Poker quality: current handoff

Updated October 6, 2026. This is a non-public-site maintenance record, not an
article, a personal result, or a promise of future work. Check the current branch,
open pull requests and actual authorization before starting another change.

## Completed in this change

The stale-page check now covers every generated HTML file under `poker/`, not
only episode, hand and story subdirectories. A removed study guide, library,
series hub, deeply nested generated page or legacy HTML filename causes a clear
build refusal. It does not silently remain eligible for the next release.

The check runs before output writes and never deletes files. A maintainer must
review and deliberately remove or restore an orphan. Manually maintained HTML
without the generator marker and non-Poker sections are unchanged.

## Observed local evidence

Source baseline: `09a4543ec142c0465d1ce4c35e13670d529b4c74`.
The recovered source tree, after removing the three already-deleted temporary
utilities, matched Git tree `722fc948f7ce3ef1a19ddcb8dadc00d1a57b8d7a` exactly.

Before repair, an isolated copy with a fabricated stale generated study guide
returned exit zero from `python _scripts/build.py --check`. The new seven-test
suite failed on that baseline, including eight failing assertions/subtests.
After repair, all 98 unit tests passed and all 49 generated files matched their
committed bytes. No page, CSS, browser script, analytics setting, private record
or publishing configuration was changed. Browser appearance is unchanged.

Commands actually executed:

```
python _scripts/build.py --check
python -m unittest discover -s _tests -p 'test_poker_release_safety.py'
python -m unittest discover -s _tests -p 'test_*.py'
git diff --check
```

PR checks, merge status and live verification must be read from GitHub. These
local results are not a claim that a later remote commit was tested or deployed.
This guard is not enforced on an unchecked direct push that bypasses the normal
PR workflow. It does not certify that arbitrary unmarked files are publishable.

## Next useful priorities

1. Inspect the outstanding manual contrast flags from the existing whole-site
   accessibility report in actual rendered Poker pages. Distinguish confirmed
   defects from scanner uncertainty. Preserve the existing design and test any
   narrowly scoped fix with phone and desktop screenshots.
2. Exercise the current reader experience rather than creating another app:
   keyboard focus, long outlines, expanded answers, print output, and search
   recovery. Reproduce a concrete usability problem before altering behavior.
3. Review the existing episode publishing workflow using fictional test data.
   Check that missing media, chapter times, spoilers and empty catalog states
   are understandable without inventing an actual episode or result.

Avoid expanding the library merely to raise its page count. Keep the 24 current
guides, three Decision Labs, established URLs, Technology-first homepage,
contact handling and Umami settings intact unless the selected fix requires a
specific, reviewed Poker-only adjustment. Do not expose private notes or footage.

## Release procedure

Use an isolated, narrowly scoped branch. Inspect current refs and existing PRs;
do not compete with another writer. Run tests without weakening them. Require
checks to pass for the exact head before merging, then verify Pages and live
content separately. Leave a precise next step and factual evidence for the next
session. Do not publish guessed test results or accessibility certifications.
