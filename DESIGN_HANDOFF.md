# Editorial design maintenance

The approved PDF design has been implemented. Read `DESIGN_IMPLEMENTATION.md` for the mapping from the reference to the site's real content and for responsive decisions.

Edit public page bodies in `_source/`, shared structure in `_source/layout.html`, and page routes and metadata in `_source/pages.json`. Use `styles.css` for the visual system; keep accessibility and state rules in `assets/site.css`. `_scripts/catalog.py` builds the real note/resource collections. Editable downloads live in `downloads/`.

Run `python _scripts/build.py` after source changes and commit generated output. Editing generated HTML alone will be overwritten by the next build. Keep all existing routes, RSS, sitemap, and contact-card behavior.

Do not replace `assets/contact.js` with a demonstration form. Preserve IDs `contact-form`, `contact-fields`, `contact-submit`, `form-error`, `form-success`, `contact-challenge`, `verification-status`, and `verification-retry`. Preserve the name/email/reason/message required fields, optional context, and configured service endpoint and public site key. Never commit secret keys.

Keep `[hidden] { display: none !important; }`, labelled inputs, visible keyboard focus, skip navigation, reduced-motion behavior, and the accessible error/success states. Avoid placing private drafts or records in this public repository. Do not reintroduce the mockup's unverified statistics or placeholder contact details.

Run the build and all test commands documented in `DESIGN_IMPLEMENTATION.md` before publishing.
