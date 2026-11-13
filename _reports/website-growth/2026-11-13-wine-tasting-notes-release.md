# Wine learning: a source-backed, non-credentialed guide

Reviewed: November 13, 2026

## Goal and gap

Nolan's About page mentioned wine learning as a personal interest, but readers
had no substantial, inspectable public material on that topic. The next
improvement gives the interest a useful destination without presenting an
invented tasting, an earned sommelier credential, a professional endorsement,
or a performance result. It helps search visitors understand the connection
between careful observation in an everyday interest and the site's broader
"AI Works, Human Decides" approach.

## Publication

- Add the original guide at `/living-well/wine-tasting-notes/` through the
  existing Living Well editorial catalog. The guide covers systematic notes,
  appearance, aroma, palate, finish, diagnostic limits, uncertainty,
  a completely fictional example, and a bounded optional AI prompt.
- Add `downloads/living-well-wine-tasting-notes.md`, a blank text worksheet
  with observations and later label checks separated. No upload is required.
- Link the article from About's established `#wine-games-and-life` section
  and a native Living Well home question. The guide also appears in the
  attention topic, guide collection, writing archive, local Find index,
  Living Well feed, combined writing feed, and canonical sitemap.
- Cite primary WSET tasting guidance and the Australian Wine Research
  Institute's sensory guidance, with narrow statements about what those
  sources support. The original template is not their tasting grid.
- Set November 13 modification dates only on actual changed collection
  surfaces: Living Well home, guide listing, attention topic, the public
  writing archive, and the local Find index. The new article has an original
  November 13 publication date.
- Extend local source and discovery contracts for this article, register
  the download with the existing public GET verifier, and keep the prior
  Living Well corpus under its historical content digest rather than
  altering earlier articles to backfill the new interest.

## Not established

No tasting session, personal bottle identification, trained palate, wine
qualification, formal WSET affiliation, consumer recommendation, search
ranking, Google indexing, AI answer inclusion, referral traffic, or general
productivity outcome is claimed. The fictional example is instructional.
WSET and AWRI are sources for limited educational context, not endorsements.
No new analytics, tracking, CI, paid APIs, or GitHub Actions were added.

## Local release verification

- `python _scripts/build.py --check`: deterministic generation, zero drift.
- `python _scripts/check_search.py`: 207 unique public titles, descriptions,
  and sitemap URLs; 116 Article pages, no errors.
- `python _tests/check_html5.py`: 212 validated HTML pages, no failures.
- `python _scripts/check_internal_links.py`: 14,327 internal links, no issues.
- `python -m unittest discover -s _tests -p 'test_wine_tasting_notes.py' -q`:
  all four new source, content, discovery, and download contracts pass.
- `python _scripts/local_release_checks.py`: **87/87 local release groups
  passed** with the existing parser dependency available via `PYTHONPATH`.
  No repository-authored workflows were invoked.
- WSET's two referenced public guides and AWRI's sensory guidance were
  re-opened through public web retrieval on November 13.
- Live GET propagation must be verified after merge. Neither the local
  checks nor an exact live-byte match establishes search indexing or AI
  citation placement.

Historical tests that require the intentionally removed
`.github/workflows/site-checks.yml` or an exact 2026-10-28 full-site output
snapshot do not define the current release gate and must not be used as a
reason to restore GitHub Actions or republish the earlier site wholesale.
