# Website growth: offline assistant-citation panel audit

Prepared: November 14, 2026
Repository: https://github.com/nolankido/nolankido.github.io
Public guide: https://nolankido.com/technology/ai-website-visibility/#ai-citation-offline-audit

## Need

The prior release published a sound human-readable AI-search measurement method and a blank worksheet but supplied no executable check for the manually collected assistant-answer sample. An incorrectly marked domain, duplicate result, text-only mention or incomplete trial could distort a citation fraction. Access to first-party Search Console data is not established in this turn, so no actual search or citation outcome can be claimed.

## Improvement

- Publish `downloads/ai-citation-panel-audit.py`, a standard-library Python CLI for a manually observed, fixed eight-question unbranded panel.
- Publish a strict blank CSV header and an explicitly synthetic two-mode, sixteen-trial fixture.
- Validate dates, month, one row per prompt and assistant/mode, whole-panel size, completed and incomplete statuses, and human-marked clickable HTTPS links to the exact approved hostname.
- Reject lookalike hostnames, impersonated URLs, duplicate trials, broken CSV columns, mixed mode labeling, and links asserted for unfinished trials.
- Report missing rows and uncompleted trials as incomplete coverage, not as missed citations. When no trials were completed, report a null rate, not a zero.
- Count text-only mentions separately; do not combine branded discovery prompts, Google AI impressions, Bing AI citation counts or assistant-referrer visits.
- Return aggregate JSON without raw citation URLs. The script makes no network calls, installs no package, and writes no file on its own.
- Link the checker and both CSV files from the public guide and worksheet, and register all three as public assets.
- Extend the local release-check list with the new regression test suite.

## Verified local tests

The exact Python source and the two CSV fixtures were created and tested locally before upload. The staged Git blob SHA of the script and fixture files matched the locally computed Git hashes. The test suite contains 15 passing tests.

The fictional example has 16 completed trials, 2 manually flagged clickable links, 1 separate text-only mention and a computed sampled fraction of 12.5%. This is not an observation of Nolan Kido's actual website.

The tests cover:
- Positive complete sample and explicit sample fixture
- Blank CSV producing null rather than an invented rate
- Incomplete and missing records excluded from the denominator
- Strict HTTPS domain validation, including lookalike and user-info rejection
- Duplicated prompt/mode trial, ambiguous labels and bad headers
- Conflicting flags and improper outcomes on incomplete trials
- Exact CLI JSON calculation and omission of recorded link URLs

## Publication, privacy and verification limits

The article's original publication date is 2026-11-03, and its prior revision date and sitemap lastmod are already 2026-11-14, so no artificial freshness update is added.

The CSV is a manually observed research log, not raw output from a crawler or search engine. Human confirmation of an assistant's actual clickable link is required, and the script cannot validate the screenshot or live redirect. Real completed logs and Search Console exports must remain private and not enter GitHub.

Local tests passed on the checker and fixtures. Repository source and generated page modifications were checked for matching changes. The full deterministic site build, 89 existing release groups, and a production browser verification cannot be claimed from this isolated checkout. Verify the complete site when a checkout is available. Do not represent a merged PR as proof of increased rankings, citations, or site traffic.

No GitHub Actions, scheduled automation, paid tools, third-party model calls, new trackers or private project details were added.
