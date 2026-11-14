# Incremental-game upgrade economics: a checkable companion guide

Prepared: November 13, 2026

## Purpose

The existing public incremental-game lab explains a small sparks economy,
including its first pencil and routine prices. This turn gives readers a
separate way to reason about those prices. It adds one original guide, a
browser-local comparison calculator, and a blank worksheet. The goal is
useful, source-inspectable educational depth in the Creative section, not a
claim that any unpublished game has been balanced or released.

## New public materials

- `/creative/incremental-upgrade-payback/`: original explanation of the
  difference between a profitable click upgrade and a passive upgrade over
  a fixed horizon. It compares buying nothing, buying one pencil, and buying
  one routine, and gives two fully specified arithmetic examples.
- `assets/incremental-upgrade-payback.js`: deterministic integer inputs,
  affordability checks, exact final balances, ties, first-purchase payback
  counts, focus and error feedback, and local reset. It makes no outgoing
  calls and does not use persistent browser storage.
- `assets/incremental-upgrade-payback.css`: scoped responsive form and outcome
  styles, keyboard focus affordances, scrollable tables, and print handling.
- `downloads/incremental-upgrade-payback-worksheet.md`: blank private-use
  comparison record that separates model results from later player
  observations. It requests consent before recording another person.

## Exact model and representative results

Let B = starting sparks, N = future taps, T = visible active seconds,
C = first pencil price, R = first routine price. All paths use the same
N and T, and make no later purchases. A base tap gives one spark.

| Path | Final sparks when affordable |
| --- | --- |
| Buy nothing | B + N |
| One pencil | B - C + 2N |
| One routine | B - R + N + T |

The routine-minus-pencil difference is C - R + T - N. With B = 25,
C = 10, R = 25, T = 60 and N = 20, the three balances are 45, 55 and 80.
Change N to 60 and they become 85, 135 and 120. These are synthetic
worked examples, not actual player observations or recorded game outcomes.

## Discoverability and evidence boundaries

- The page has a unique canonical URL, description, publication date,
  Article JSON-LD with an identified author, and a calculator identified
  as its SoftwareApplication main entity.
- The author archive, public search index, and sitemap include the guide.
- The About page, Creative hub, Projects overview, and original game lab
  have routes into this guide. The new guide links back to the game lab,
  source code, and its worksheet.
- The project remains explicitly described as an original teaching demo.
  No private game code or identifiers, actual users, enjoyment scores,
  retention metrics, commercial outcomes, site-search growth, or AI answer
  inclusion is asserted.

## Verification scope

- The JavaScript unit and isolated form interaction checks test the default
  balances, reversed leader, ties, invalid data, unaffordable purchases,
  repeatable formulas, keyboard-focus feedback, and resetting.
- Python publication contracts verify author archives, metadata, source
  asset versions, cross-links, worksheet text, data boundaries, and GET
  targets.
- `python _scripts/build.py --check`: 238 deterministic generated files,
  zero drift.
- `python _scripts/check_search.py`: 209 unique public page titles and
  descriptions, 209 sitemap URLs, 118 structured Article records, no errors.
- `python _scripts/check_internal_links.py`: 14,420 internal links and
  fragments across 214 public HTML pages, no issues.
- `python _tests/check_html5.py`: all 214 public HTML pages parsed.
- `python _scripts/local_release_checks.py`: **89/89 release check groups
  passed**, without any GitHub Actions.
- A headless visual browser is not required for this mathematical unit
  gate. Do not imply viewport or assistive-technology testing happened
  unless it is separately observed.

This change requires no GitHub Actions, scheduled jobs, paid APIs,
third-party analytics, or collection of private visitor data.
