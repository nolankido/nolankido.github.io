# Website growth: Turn 02 homepage selection

October 17, 2026. Engineering release candidate; use the pull request and deployed-file receipt for final publication status. Actual visitor clarity and growth remain unmeasured.

## Reader-facing change

The homepage now has one primary selection, in this order:

| Purpose | Destination | What a visitor can do |
|---|---|---|
| Use a free tool | `/technology/task-brief/` | Define a task, finish line, boundaries and checks before asking AI |
| Inspect a recorded case | `/technology/checking-ai-website-changes/` | Inspect a real defect, its repair and the limits of the checks |
| Understand the approach | `/notes/keep-the-judgment/` | Read the argument for keeping purpose and judgment in human hands |

The former overlapping practical-work invitation and extra answer-checking paragraph are consolidated into this selection and a native **More tools and reading** disclosure. All previous homepage links remain available, including the calculator, fictional hand review and weekly-reset worksheet. All previous fragment IDs survive. The secondary disclosure can open by keyboard without JavaScript.

The four sections retain their established order. Technology still starts with the task brief; Living Well now starts with the weekly-reset guide rather than its worksheet collection; Poker now starts with first-live-tournament preparation rather than a calculator; Creative Work still starts with its creative brief. The two former first-step destinations remain in the secondary links.

## Boundaries

Nolan's name, introduction, personal biography, brand statement, primary navigation, public/private boundaries and existing Start Here page are unchanged. No portrait, credential, testimonial, personal experience or measured time-saving claim was added. The existing recorded website case is not a substitute for Turn 04's new ordinary-task evidence.

No new public URL, JavaScript, form, account, analytics event, third-party service or signup was introduced. Existing analytics and Poker School consent are unchanged. The homepage date reflects its actual revision; no article was redated or republished. The shared first-step stylesheet gains homepage-only layout rules; the Creative page changes only its stylesheet cache token.

## Engineering checks

The production delta is limited to six files: three source/asset inputs, the homepage, the Creative page's stylesheet cache token, and sitemap freshness. The new test-only history adapter reverses only whole-file SHA-256 matches and verifies both offsets and restored hashes. It keeps older release records intact. Independent tests compare all 222 previous generated outputs and all 487 previous source/asset/download files after only this exact delta. Unknown edits remain visible.

The same suite checks all former homepage destinations and anchors, the three distinct primary choices, four first actions, private-boundary preservation, and false or corrupt history records. Browser regressions cover keyboard disclosure, all primary destinations, script-free reading, and reflow with 200% root text size plus increased text spacing. Existing real-HTTP first-step and practical-work journeys are updated to follow the new visible routes, including opening the secondary group before visiting the calculator.

Useful commands:

```sh
python _scripts/build.py --check
python _tests/check_html5.py
python _scripts/check_search.py
python -m unittest discover -s _tests -p 'test_*.py' -v
python _tests/browser.py
python _tests/first_steps_browser.py
python _tests/practical_discovery_browser.py
```

`capture_turn02.py` reproduces the new compatibility record from the pinned parent. Its default is read-only; `--write` is only for preparing an unapproved candidate before review. No earlier `*-baseline.json` or `*-change.json` is refreshed. The normal full Site checks and published-response checks remain mandatory. Offline browser rendering is not a substitute for the runner's real URL-journey tests.

## Human check still needed

Ask three to five people unfamiliar with the site: What does Nolan do? What would you open first, and why? What do you expect to get from that page? Can you find another interest without assistance?

Record their actual words and obstacles privately, not in this public repository. Do not describe this engineering pass as a proven increase in comprehension, visitors, conversion or brand recognition. No participant observation has been completed in this turn.

## Next turn

Turn 03 strengthens the existing AI task brief with three clearly illustrative examples and better output readability. It should reuse this homepage entry point rather than adding a second generator or another homepage card.
