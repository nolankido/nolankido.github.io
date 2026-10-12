# Public introductions and core stylesheet delivery

Baseline: `0f356fdf543a4de2331b79f417cd4d5376d95fae` (PR 43).
Scope: nolankido.com only. Preserve the approved personal identity, original writing, private-project boundaries, and visual design.

## Assessment

Recent releases already supplied connected authorship, descriptive page metadata, concrete tools, a recorded case, task-level navigation and portable worksheets. Another batch of broad articles would not resolve the remaining proof and measurement gaps.

Two addressable gaps remained. First, the existing `/bio/` page provided two paragraphs but no direct copying/download controls or compact selection of work for someone preparing an introduction. Second, every HTML page loaded the same three consecutive core stylesheets independently. Those three local requests can be consolidated while retaining their exact declarations and cascade order.

The practical priorities remain genuine outcome evidence and Search Console measurement, not an inflated biography or promises of authority. No portrait, credentials, private contact details or unconfirmed social profiles are introduced here.

## Implemented

### Reusable public introductions

The existing `/bio/` route now provides the exact short and longer biographies from `_source/site.json`, progressive copy buttons, two ordinary UTF-8 text downloads, a copyable canonical site address, and links to the working task-brief tool, recorded website-check case, and judgment essay. No new biography claims were written. About, the homepage introduction and all four interests remain intact.

The title is `Nolan Kido | Short Biography & Public Introductions`. It describes this page's distinct purpose without changing its canonical address or creating a competing About page. Structured data refers to the existing Person identity rather than inventing credentials or another author.

The script is loaded only on `/bio/`. It copies only a selected public paragraph/address after a button is pressed. If copying is denied or unavailable, the visible text can be selected and the downloads remain available. Blocked or disabled JavaScript leaves the complete content, ordinary navigation and downloads intact. No messages, analytics events, inputs, storage or network calls are added by the copying feature. Existing site analytics and fonts remain separately in place.

### One cache-versioned core stylesheet

`_scripts/core_styles.py` generates `assets/site-core.css` from `styles.css`, `assets/site.css`, and `assets/hubs.css`, preserving every declaration and its order. Page-specific styles remain separate and scoped. There is no minification, asynchronous CSS, font change or deletion of the original editable source files.

All 168 pages replace those three stylesheet links with one content-hashed link. This removes two core stylesheet requests per cold page load. For example, the homepage and Technology each change from six local stylesheet links to four; About changes from four to two. The profile adds its own scoped stylesheet, so its net local stylesheet count falls from four to three. The source CSS totals 31,149 bytes and the bundle is 31,306 bytes, including source labels. This is a request-count optimization, not a claim of reduced uncompressed CSS bytes.

The build rejects missing, duplicate, reordered or conditional core stylesheet links. It also refuses imports, namespaces, charset declarations or CSS URLs that would require explicit concatenation/path review. Changes in any core source change the bundle's cache version. The live verifier now checks the bundle, both profile assets and both biography downloads.

No measured improvement in Core Web Vitals, search ranking, indexing or traffic is claimed. Reducing requests is not a guarantee of faster rendering on every network or cache state. External fonts can still influence rendering. This release makes a bounded delivery change that can be evaluated separately from actual search and real-user performance data.

## Preservation and validation

An independent baseline signature checks the unchanged body bytes of 166 pages. `/bio/` is deliberately revised; `/find/` reflects the profile's revised title/description. The original public identity, About and Home sources, shared layout, contact script, three CSS source files, all five feeds, and sitemap are independently hash-pinned.

Prior fixtures were refreshed only for the reviewed biography source, biography metadata in the page manifest, and the rendered stylesheet references in older page snapshots. The composite page snapshot and three protected rendered pages were refreshed with no body edits outside the profile; 166 unchanged bodies are independently signed against the pre-release baseline. Their exact comparisons remain enabled. New tests additionally protect original body content and identity text. Three older stylesheet assertions now require the versioned core bundle rather than the superseded links; the original files are still checked live. The script allowlist adds the profile script only for `/bio/`.

The new browser suite compares computed styles and element geometry between the original three-link loading arrangement and the consolidated version on six representative pages at three widths. HTTP mode additionally checks actual request counts, exact download bytes, keyboard navigation, copy failure states, and the new page's accessibility. Local offline checks cannot substitute for those HTTP checks; the local browser blocks loopback navigation by policy. Full hosted CI is required before merging, followed by published-response verification.

No existing browser suite is removed. The release workflow gains one suite and a JavaScript syntax check. The completion receipt is recorded on the pull request after deployment, not preclaimed here.

## Research basis

Google Search Central recommends clear authorship and content that provides original usefulness rather than mass expansion for rankings:
https://developers.google.com/search/docs/fundamentals/creating-helpful-content

Google's web performance documentation distinguishes rendering, font loading and layout-shift concerns. This release does not modify font delivery or infer real-user results from local tests:
https://web.dev/articles/font-best-practices

The implementation is maintenance and usability work. Publication alone does not establish increased personal credibility, traffic or rankings.
