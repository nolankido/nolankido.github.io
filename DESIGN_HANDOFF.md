# Editorial design maintenance

The approved PDF design is implemented and remains the visual foundation. Read `DESIGN_IMPLEMENTATION.md` for the design system, `CONTENT_RELEASE.md` for the latest content revision, and `EDITORIAL_GUIDE.md` for public writing and maintenance boundaries.

Edit public page bodies in `_source/`, shared structure in `_source/layout.html`, and routes and metadata in `_source/pages.json`. `_source/selection.json` controls the featured essay and curated reading order. `styles.css` owns the visual system; `assets/site.css` owns accessibility and state rules. Both stylesheets were preserved byte-for-byte in the personal-home content revision.

`_scripts/catalog.py` builds reading selections and resource pages. Blank editable downloads live in `downloads/`; completed fictional examples live in `_source/examples/`. Guidance and limitations belong alongside the resources, not in a separate hidden document.

Run `python _scripts/build.py` after source changes and commit generated output. Editing generated HTML alone will be overwritten. Preserve existing URLs, RSS, sitemap, and the minimal contact card. Publication dates are explicit; substantive revisions use `updated` and `revision` fields rather than resetting the original publication date.

Do not replace `assets/contact.js` with a demonstration form. Preserve IDs `contact-form`, `contact-fields`, `contact-submit`, `form-error`, `form-success`, `contact-challenge`, `verification-status`, and `verification-retry`. Name, email, and message are required. Topic (`reason`) and context are optional. Keep the configured endpoint, public site key, validation, retry behavior, and hidden success state. Never commit secret keys.

Keep `[hidden] { display: none !important; }`, labelled inputs, visible keyboard focus, skip navigation, and reduced-motion behavior. Avoid private drafts and records in this public repository. Do not reintroduce unverified statistics, placeholder details, or achievement counters. Preserve the invitation to ordinary conversation as well as professional inquiries.

Run the build and all test commands documented in README before publishing. Tests do not prove inbox delivery or provider account settings; those need a separate authorized live check.
