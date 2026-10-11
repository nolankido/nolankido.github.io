# Professional interest entry points

Date: 2026-10-11
Baseline: cc278c1acddd99597bfb1e562595deb8ec4b45e9

## Reader problem

The person-first introduction is established. The remaining gap is practical
orientation: the global Resources page primarily exposed three general worksheets,
while the larger libraries lived in separate sections. Original notes ended with
a generic writing/contact choice instead of a small, relevant continuation.

## Changes

Start here now begins with four bounded interest paths, followed by selected
reading. Existing section anchors and content-type disclosures remain available.
Resources becomes a cross-site entry point while retaining all original thinking
worksheets, downloads, examples, and their fragment URLs. Labels distinguish guides
and worksheets on this site from directories of other people's work. The wording
about accounts is scoped to the three local worksheets, not outside providers.
Home, Technology and Creative Work give readers direct routes to the resources.
Each original note ends with two editorially selected next readings and a reason
for each. The article bodies, original dates, reading-time estimates, and feeds
are unchanged. No article is duplicated or presented as a firsthand case study.

## Maintenance

`_source/entrypoints.json` records destinations and short reader context, not a
second article or provider inventory. `_scripts/entrypoints.py` resolves canonical
titles from the public manifest, escapes plain text, validates local published
routes, and rejects proposals, hidden pages, duplicates, and self-links. A new
original note needs two relevant next-reading entries. Keep these small selections
deliberate rather than filling them from publication order or keyword matches.
`assets/entrypoints.css` is loaded only by Start here, Resources and original notes.
There is no new runtime JavaScript, network endpoint, tracking, or external service.

## Boundaries and verification

Identity, About, biographies, contact, privacy, shared design, social cards,
analytics, hosting settings, original note bodies, other-section source collections,
and all three feeds are preserved. Unit tests protect these static baselines.
Validate the complete build and links, targeted semantic reader paths, keyboard and
no-JavaScript navigation, narrow-screen reflow, and automated accessibility before
merge. Review browser screenshots. Verify production deployment and exact public
bytes separately. Automated checks are not an accessibility certification.
