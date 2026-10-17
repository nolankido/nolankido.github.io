# Website growth, Turn 03: An easier AI task brief

Updated October 17, 2026. Scope: existing `/technology/task-brief/` only.

## Visitor benefit

The current five-field builder remains local and deterministic. Three additional, explicitly illustrative presets show how to convert meeting notes to a plan, a rough article outline to a reviewable draft, and a small website change into a bounded proposal. They join the three earlier writing, shared-plan, and learning examples. No example is a claimed personal experiment or measured productivity result.

Once a brief is assembled, a six-part sectioned reading preview now sits above the complete copyable text. Both are derived from the same validated section data. The preview is built exclusively with DOM `textContent`, not HTML insertion. A new **Select text manually** control provides an explicit fallback for denied clipboard access. Clipboard and download keep their earlier permission and honest result messages. No account, AI API, network submission, storage, query-string state, or new analytics event was added. Existing pagehide/bfcache clearing and replace/clear confirmation remain in force.

The blank text template remains unchanged and downloadable without scripting. All examples remain readable without JavaScript, though preset loading needs it. The title and URL are preserved, and the updated metadata reflects the actual substantive page revision.

## Editorial and safety limits

All six presets are fictional examples; meeting decisions, article evidence, site change tests, and approvals are explicitly not invented. The website-change preset stops at a reviewable patch, not a deployment. Visitor material is never submitted by this builder. Browser clipboard, extensions, local downloads, and the external AI provider still have separate data handling; prompts cannot enforce security.

## Bounded release and regression evidence

The seven intended production deltas are `_source/pages.json`, `_source/technology/task-brief.html`, `assets/task-brief.css`, `assets/task-brief.js`, `technology/task-brief/index.html`, `find/index.html`, and `sitemap.xml`. There are no new public pages or runtime assets. The pinned release record in `_tests/task-brief-growth-change.json` stores SHA-bound original bytes so older release tests can reconstruct the previous published state without rewriting historical baselines; any unapproved new bytes do not match and remain visible. Its adapter runs only under tests, not in production.

Run `python _scripts/build.py --check`, `python _tests/check_html5.py`, `python _scripts/check_search.py`, focused unit and browser tests for the brief, and the full Site checks workflow before merge. Verify deployed bytes after publishing. Track any browser limitations explicitly. No traffic, visitor-comprehension improvement, or workflow time saving is claimed from engineering tests alone.

## Follow-on

Turn 04 requires genuine source material for a practical-AI case with approval to publish; this release does not substitute an illustrative example for that experience. Existing free resources and the person's introduction remain unchanged.
