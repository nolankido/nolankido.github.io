# Sprint Turn 27: invite adults to help test the existing guides

Date: October 26, 2026 (Pacific/Honolulu). Parent release: `1c6a1f1123ce8000ca6f43a016d3bb8714f18d58`.

## Evidence-led priority

Study NK-UTILITY-01 (issue #123) has an externally verified preparation kit, task definitions and synthetic validator tests, but **zero recruited or observed adults**. The first real session is blocked on a selected willing participant. Prior releases focused on engineering and print issues; these cannot tell whether first-time readers find or understand the six flagship workflows.

## Bounded activation

Add a clearly optional invitation near the end of the existing `/start-here/` introduction, available as static HTML without scripts. It asks adults new to the site whether they would consider a roughly 25-minute session of two fictional tasks using their own device. It explicitly allows declining and stopping, clarifies that the existing Contact form is for expressions of interest only, links to the existing `/privacy/` policy, warns against sending worksheets or private information, and makes clear that future session-level informed consent, withdrawal and deletion terms must be explained separately. Recording is off by default.

The invitation is not a new data-collection form. It has one native, named `/contact/#contact-form` link and retains every existing route. The Contact page already requires a name, email and message, receives submissions through Formspark and uses Cloudflare verification. That existing service processing is disclosed on `/privacy/`. No extra field, third-party service, identity leak, UTM parameter, analytics event, local storage, mailing list, unsolicited email or study data is added.

Only two production paths change: `_source/start-here.html` and generated `start-here/index.html`. No publication/date field, sitemap or other page is rewritten for this bounded opt-in note. The existing public site design and content routes are preserved.

## Acceptance

- Exact-hash `study_interest_history.py` reverts only the approved addition from the two complete files and fails closed for corrupted history, preserving earlier golden snapshots without changes.
- `test_study_interest.py` checks the source/output and consent/recording/withdrawal boundaries, unchanged task-route inventory, no forms/scripts, intact existing Contact form and privacy destination.
- Extended `entrypoints_browser.py` tests the real keyboard link to the actual Contact form without JavaScript, and at multiple sizes with script blocked; confirms no form submission and no new storage.
- Full GitHub build, historical unit tests, all five browser groups, independent review, deployment and exact-byte public verification remain merge/release gates.

## Research limits

No participant has been contacted through this change, volunteered, consented, or completed a task. The existing visitor-study checkbox remains open. No visitor, conversion, search or signup claim can be inferred from pageview tracking. If interest arrives, the owner still needs private note storage, a working withdrawal contact, a 30-day deletion arrangement and a valid prospective session-release amendment before any observation. Do not send raw observations to this public repository.
