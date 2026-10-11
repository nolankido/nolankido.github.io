# Reading and sharing presentation

The person-first architecture is described in `_reports/personal-architecture.md`.
The October 11 refinement is documented in `_reports/public-image-20261011.md`.

## Published writing

A new original note needs a record in `_source/pages.json`, its body in
`_source/notes/`, and its ID in `_source/selection.json`'s `note_order`.
Use an explicit publication date. Featuring an old article is not a new publication.

Selected homepage cards and cross-site reading routes live in
`_source/identity.json`. They resolve canonical titles and dates from the published
page manifest. Do not copy a second version of an article into another section.

Note headers include a linked author, a reading-time estimate, and a link to their
AI-assistance disclosure. A note may supply an `editorial_note` describing its
specific scope; the build escapes that text. Do not claim personal review or
firsthand results without an approved source. Fictional examples stay labelled.

## Sharing cards

`_source/presentation.json` selects the default social image and explicit page
exceptions. Both current images are local 1200 by 630 PNGs with descriptive
alternative text. `_scripts/presentation.py` validates their paths and dimensions
and emits image metadata alongside the existing titles and descriptions. The
live verifier checks their exact bytes. Image delivery does not guarantee when
an external platform refreshes its cached preview.

The optional renderer `_scripts/render_social_cards.py` uses Pillow and installed
DejaVu fonts to reproduce the two typographic cards. It is not part of the site
build or browser runtime. No fonts are bundled with the site. To redraw cards
in a development environment with Pillow installed:

```sh
python _scripts/render_social_cards.py
python _scripts/build.py
python _scripts/build.py --check
python -m unittest discover -s _tests -p 'test_*.py' -v
```

Use `--regular`, `--bold`, and `--serif` with installed font paths where necessary.
Review the resulting images before committing. Do not substitute synthetic
portraits or unapproved personal photographs for these typographic graphics.

## Release checks

The public-image test fixture preserves original article bodies and sensitive
site boundaries. New metadata and selected dates are tested independently of
legacy generated-output hashes. Browser tests cover reading journeys, keyboard
access to the disclosure, and global Writing navigation without JavaScript.
The normal read-only Site checks workflow saves a small `public-image-previews`
artifact for desktop/mobile visual review, alongside the existing full-site audit.
