# Turn 14: carry the public page into an optional correction report

Status: candidate. Software behavior is being qualified; no visitor observations or new search metrics are claimed.
Published predecessor: `9ada5f1041f54a311f5142cb520d5f75edf3e2cd`.

## Source-observed gap and bounded change

The six flagship resources already offer correction links, but each goes to an undifferentiated Contact page. The optional context field starts blank, so a reader has to supply the page again. This is a source-reproducible missing handoff, not a claim that study participants reported confusion.

Only those six named correction links gain fixed fragment identifiers. The contact page renders the corresponding public routes and current titles from the existing page manifest. Its existing script recognizes only an exact authored marker and inserts the public canonical page URL into an otherwise empty optional context field. A visible notice identifies the page and explains that the context may be edited or removed. A short reporting hint requests the passage or link, observed behavior and expected result, not private worksheet contents.

Ordinary Contact links and visits remain ordinary. Invalid/unknown fragments and a previously restored context do not trigger a prefill. Initialization runs once; later fragment changes do not overwrite edits. No field is focused automatically. The normal required fields, anti-spam verification, send button, backend and success/failure behavior remain. No message is sent by opening the page. The page selection is not authenticated evidence of a referrer, and the interface does not claim it is.

## Privacy and accessibility boundaries

The handoff carries a finite public-page identifier, not input text, a query string, a referrer, a token or stored browsing history. No new analytics event, persistence, form field, remote call or third-party dependency is introduced. Existing pageview analytics continue excluding fragments and queries. A correction is sent through the existing contact service only after the reader explicitly sends the form. A reader can change or remove the optional context before then.

The explanatory text is associated with the relevant controls only after a valid prefill. Ordinary visits do not receive a hidden accessible description implying that a URL was added. The page remains readable without scripts, but the existing contact form still needs JavaScript for its anti-spam check; this change does not claim a new no-script submission method.

## Scope and qualification

Ten production paths change: the existing renderer, Contact source and script, generated Contact page, and one correction href in each of six generated resource pages. All other bytes on the six resource pages remain exact, including dates, examples, calculations, links and templates. There is no new route, stylesheet, asset, sitemap entry or release workflow.

The new test-only predecessor accepts only complete SHA256-approved files, applies bounded byte edits and verifies the restored parent digest. It retains the prior production inventory and does not refresh old release hashes. Historical assertions that compare a complete revised page to an earlier release use that approved view. Unknown mutations and corrupt offsets remain detectable.

Thirteen focused unit contracts and seven offline browser cases cover all six routes, literal escaped titles, normal/unknown/hostile fragments, restored/edited/cleared context, optional-field length, mocked explicit sending, a failed send retaining edits, keyboard entry and four viewport widths. Existing form fields and submitted payload names are unchanged. These are synthetic and mocked-service tests, not actual contact messages, real visitor evidence or Google indexing data.

Run the unchanged full hosted Site checks workflow and all five browser groups before merge, with final-head review. After merge, independently verify GitHub Pages and the public responses. No deployment is established by the candidate report.

## Follow-up

Search Console access remains unavailable without a current authorized access route; this work does not change crawler rules to compensate. The human task study in #123 remains prepared, not conducted. Future reader feedback can identify a page more easily, but its existence and effect must be observed rather than inferred from this code change.

References: MDN URI fragment documentation explains that fragments are handled by the client and not included in the server request: https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Fragment . The repository's ANALYTICS.md and privacy page define the existing pageview-only, query/fragment-excluding boundaries.
