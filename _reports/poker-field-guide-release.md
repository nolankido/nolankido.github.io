# Poker field guide release

## Scope

Seven educational guides, a field-guide hub and a printable-sheet page, published October 8, 2026. The guide library grows from 24 to 31 entries with a distinct Live tournament preparation category. The 108-resource external directory is preserved; new editorial links explain how to choose and evaluate those resources.

New guides: first-live-tournament, choosing-a-tournament, registration-and-reentry, tournament-day, recording-hands, choosing-study-tools, evaluating-poker-advice.

Three blank Markdown downloads share exact source text with their visible printable previews: poker-event-planner, poker-hand-capture and poker-resource-check. No answers are submitted or stored by the site.

## Editorial boundaries

No personal hands, results, footage, relationships or private project details are added. Worked event, cost and hand examples are fictional. Planning suggestions are not recommendations to wager, re-enter or spend up to a limit. Rules and product descriptions link to official public sources checked October 8, 2026. Public documentation review is explicitly distinguished from product testing.

The Technology-first root page, shared navigation, design assets, contact configuration, privacy notice, analytics, existing personal-account catalogue and all 24 original guide routes are preserved. Existing guides receive only limited cross-links where useful. No new runtime JavaScript is added. A small stylesheet loaded only on the new printable-sheet page prevents mobile overflow and formats printed previews.

## Verification

Run `python _scripts/build.py`, `python _scripts/build.py --check`, and the complete `_tests/test_*.py` suite. New tests cover discovery, feed and sitemap presence, printable/download parity, scope boundaries and independently calculated examples. Browser checks cover new pages at narrow and wide viewports, disclosure behavior, filters, print visibility and blocked external requests. The existing main-branch live verifier automatically covers all manifest pages; three new download targets are added explicitly.

The two historical tests that assumed a permanent 24-entry library now derive the expected size from the publishing manifest. The new release test checks complete manifest coverage and the five new live-preparation guides without blocking future approved additions.

Do not infer deployment from a generated artifact alone. Check the Pages deployment and the exact public-byte verifier after merge.
