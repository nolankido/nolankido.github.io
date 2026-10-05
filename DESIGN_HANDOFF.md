# Visual design handoff

The content and functional build-out is ready for a visual redesign. Keep the site a quiet, readable personal home base rather than a product landing page or detailed portfolio.

## Content and structure to retain

The primary navigation is About, Notes, Contact. The homepage introduces Nolan Kido through technology, strategy, and creative work; three connected interest areas; three selected notes; and a simple contact invitation. Supporting Bio, Card, Privacy, and RSS belong in the footer or relevant pages.

Keep the three stable note routes:
- `/notes/trustworthy-tools/`
- `/notes/decision-quality/`
- `/notes/learning-from-the-beginning/`

The notes are general explanatory pieces. Do not invent experiences, credentials, results, endorsements, or named work examples. Preserve source links and the AI-assistance attribution. No new personal disclosures are needed for the design.

## Where to make changes

`_source/layout.html` owns the shared document head, navigation, main landmark, and footer. `_source/*.html` and `_source/notes/*.html` hold public page bodies. `_source/pages.json` owns routes, titles, descriptions, and publication dates. `_source/site.json` owns shared public wording and contact configuration.

`styles.css` is the existing Quiet Signal stylesheet, unchanged by the content build-out. `assets/site.css` contains small functional and new-content additions. Replace or consolidate visual styles as needed, but retain their accessibility and state rules. `assets/contact.js` owns contact behavior and should not be replaced with a decorative mock form.

Run `python _scripts/build.py` after source changes and commit generated pages along with source. Editing only the generated pages will lose the changes on the next build. There is no frontend framework dependency or required client-side rendering.

## Form contract

Preserve these IDs: `contact-form`, `contact-fields`, `contact-submit`, `form-error`, `form-success`, `contact-challenge`, `verification-status`, and `verification-retry`. Keep field names `name`, `email`, `reason`, `context`, `message`, and `_honeypot`. Name, email, reason, and message are required; context is optional. All controls should keep real labels.

Keep the configured Formspark action and Turnstile public site key. The fieldset starts disabled until the script attaches. Errors must not erase the message. Missing verification must not leave Send disabled. Never auto-resubmit after an ambiguous failure. The success section must remain genuinely hidden until the service accepts a request.

The CSS rule `[hidden] { display: none !important; }` is functional, not decorative: existing grid/flex styling must not override hidden states. Preserve visible keyboard focus, the skip link, main landmark, form error announcements, success focus, reduced-motion support, and usable text at narrow widths and zoom.

## Visual freedom

Typography, color, spacing, layout, borders, the monogram treatment, and restrained imagery can change. A portrait is not required. Avoid autoplay media, intrusive animations, tracking embeds, fabricated social proof, or unnecessary navigation categories. A branded social preview image can be added as a design asset later; current metadata intentionally makes no claim that one exists.

## Verify before publishing

Run the static tests and offline browser tests documented in README. Inspect the homepage, About, Notes, all three articles, Contact, Bio, Card, Privacy, and 404. Test narrow mobile through desktop. Preserve working routes, source links, sitemap, RSS, and accessible contact error states. Backend token validation and actual inbox delivery require separate live verification by the site owner.
