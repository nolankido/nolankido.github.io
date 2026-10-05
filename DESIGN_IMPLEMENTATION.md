# Editorial design implementation

The supplied three-page design reference is adapted to the site's existing public identity. Its oversized sans-serif headings, red ledger margin, double-rule name underline, circular NK seal, pale green panels, numbered sections, serif reading text, monospace labels, striped reading table, and dark contact block are implemented across the site.

## Content decisions

The reference's publication count, quantitative-finance work descriptions, career and location placeholders, unverified milestones, and direct email placeholder are not published. The homepage instead uses the previously approved interests and actual public notes. Its counts are derived from the note and resource catalogs where applicable.

The reference's four-part structure becomes Interests, Notes, Resources, and Contact. Primary navigation is About, Notes, Resources, Contact. The existing three note URLs remain unchanged. Resources contains three real editable Markdown worksheets, with inline previews and direct downloads. These are thinking aids, not validated assessment instruments.

## Design system

`styles.css` is the complete visual stylesheet. `assets/site.css` contains hidden-state, focus, skip-link, reduced-motion, and print rules. `_source/layout.html` controls the shared document structure. `_source/home.html` is the homepage. `_scripts/catalog.py` produces the reading table, catalog counts, resource list, and full resource previews from the actual content.

The three type families named in the reference are requested through Google Fonts, with display=swap and readable system fallbacks. No font files are committed. The privacy page discloses these third-party font requests. No trackers, additional JavaScript framework, or animation library are added.

## Responsive adaptation

The continuous red margin and lateral labels are desktop structure, not fixed mobile requirements. On smaller screens labels move above the content, the margin rule is removed, multi-column sections stack, the stamp is hidden at phone widths, and the reading table retains date and title without forcing a horizontal scroll. The form keeps 16px input text, working focus states, and recoverable errors.

## Functional boundaries

The contact JavaScript, existing form endpoint, public Turnstile key, domain configuration, and branch-based Pages hosting are preserved. Tests bind the exact contact script Git blob to prevent silent replacement during this redesign. Real inbox delivery and account-side token validation are outside the offline test suite.

## Development and verification

Edit source files, run `python _scripts/build.py`, and commit regenerated output. Run:

```sh
python _scripts/build.py --check
python -m unittest discover -s _tests -p 'test_*.py' -v
python _tests/browser.py
python _tests/design_browser.py
```

The design browser suite serves the actual files over localhost, blocks external traffic by default, visits every page at five widths, opens resource previews, and verifies downloaded bytes. Set `ALLOW_WEB_FONTS=1` for a separate run that loads and checks the three Google Fonts families. The existing suite covers contact submission failure modes using mocks. Neither submits a real contact message.
