# Editorial design implementation

The supplied design reference was adapted to the site's public identity: oversized sans-serif headings, a red margin, double-rule name underline, circular NK seal, pale green panels, numbered sections, serif reading text, monospace labels, striped reading table, and dark contact block. The subsequent personal-home content revision preserves the two stylesheets, favicon, contact JavaScript, and domain configuration.

## Current content structure

The homepage introduces an independent builder and writer, offers a worked explanation as the main reading entry point, connects the core interests, features two reflective/creative pieces, and invites an ordinary conversation. The old numerical status strip is removed. Primary navigation remains About, Notes, Resources, Contact. Existing article URLs are stable.

The prototype's unverified publication figures, work descriptions, location and career placeholders, and direct email placeholder are not public claims. The expanded collection uses worked fictional examples rather than invented autobiographical accounts. Resources contains three blank Markdown worksheets, completed fictional examples, intended-use guidance, and limitations. They are thinking aids, not validated assessments.

## Design system

`styles.css` is the complete visual stylesheet. `assets/site.css` contains hidden-state, focus, skip-link, reduced-motion, and print rules. `_source/layout.html` controls shared structure. `_source/home.html` is the homepage. `_scripts/catalog.py` creates reading tables and resource components. `_source/selection.json` controls homepage selection and archive reading order independently of RSS dates.

The three type families named in the reference are requested through Google Fonts with display=swap and readable system fallbacks. No font files are committed. The privacy page discloses those requests. No tracking scripts, frontend framework, or animation library are added.

## Responsive adaptation

At narrow widths, lateral labels move above content, the margin rule disappears, columns stack, the seal is hidden at phone widths, and the reading table keeps its date/title columns without forcing horizontal scrolling. The form uses 16px input text and preserves keyboard focus and recoverable errors.

## Functional boundaries

The contact script, endpoint, public Turnstile key, CNAME, and branch-based Pages hosting are preserved. Name, email, and message are required; topic and context are optional. Tests bind the exact visual stylesheet and contact-script blobs to detect accidental changes. Actual inbox delivery and provider-side token validation are outside the mocked test suite.

## Development and verification

Edit source, run `python _scripts/build.py`, and commit generated output. Run:

```sh
python _scripts/build.py --check
python -m unittest discover -s _tests -p 'test_*.py' -v
python _tests/browser.py
python _tests/design_browser.py
```

The design browser suite serves actual files over localhost, blocks external traffic by default, visits each page at five widths, opens resource examples/previews, and verifies download bytes. Set `ALLOW_WEB_FONTS=1` for a separate run that loads and checks the three Google Fonts families. Contact tests use mocked service responses. Neither test suite sends a real message. `EDITORIAL_GUIDE.md` explains content approval and sustainable maintenance.
