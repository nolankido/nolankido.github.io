# Practical AI evidence and useful search destinations

Review date: October 11, 2026, Hawaii time.
Baseline: `6832b5e1edc85c50a3e6eb39a447cd67d9f0f80c` (PR 40).

## Decision

The previous release fixed the immediate search-identity gaps. Repeating title,
breadcrumb, and author changes would add little. The next useful step is to give
readers something distinctive to use and a concrete example of how an AI-assisted
result was checked. The site should demonstrate practical judgment, not advertise
an unsupported expert title or produce another batch of generic essays.

This release adds two focused Technology destinations, with ordinary links from
Technology, About, and Resources. The existing four-interest homepage and all
original articles stay intact.

## What the available search data establishes

GSC Wizard tools are now accessible. The connected-property list did not contain
nolankido.com. Attempts to register `sc-domain:nolankido.com` and
`https://nolankido.com/` both returned not_found from the connected Google accounts.
This establishes a property-access gap, not zero traffic or failed indexing.
No other site's metrics were used. No property was created, no sitemap submitted,
and no performance or URL-inspection report was obtained for nolankido.com.

The owner must add and verify nolankido.com in Search Console, or connect the
Google account that already has verified access. Then inspect the home, About,
Technology, task-brief, time-calculator and recorded-case URLs, confirm the existing
sitemap, and separate branded from practical-AI queries. Use settled reporting
windows and avoid treating immediate fluctuations as effects of this release.

## Implemented reader value

### AI Time Savings Calculator

Route: `/technology/ai-time-savings/`.

A free browser calculation compares the same task over one repetition window.
It counts usual effort, assisted preparation/production, review/repair, one-time
setup and total upkeep. Integer hundredths of minutes avoid decimal drift at
exact break-even. A result may be positive, zero or negative. The interface
separates recovering overhead from strictly positive savings and explains that
break-even assumes overhead stays fixed.

Quality is an explicit, unverified user assessment, not a calculator score. The
comparison distinguishes planning estimates from observations. Costs such as
privacy, reliability, enjoyment and subscription money are not silently reduced
to a time or financial ROI metric. Three fictional examples cover a repeated task,
a one-off that loses time, and review costs that exceed production savings.

Inputs remain in page memory. No task description or personal document is needed;
no calculator inputs are sent, persisted or added to the URL. Editing invalidates
old results, clearing asks before discarding entries, and leaving the page clears
them. Copy and text download are explicit actions; exports retain assumptions and
quality limits. Existing site-level analytics and web-font disclosures remain.

The complete formula, three examples and an exact blank-worksheet preview remain
available without JavaScript. The script loads on this route only.

### Recorded website-verification case

Route: `/technology/checking-ai-website-changes/`.

The case documents the real PR 40 pre-release markup defect: 347 unit/content tests
passed, but a separate full-page HTML5 parser found an extra closing div. It
records the repair, different check scopes, and the final 235-target public-byte
verification. Historical candidate, run and release identifiers appear in a
compact download. These numbers describe that release, not the current site.

A small downloadable Python reproduction accepts corrected embedded markup and
rejects the same class of malformed markup. It is explicitly a reduced teaching
fixture, not a full replay of the historical release. The script has no network
or file-writing operations; installing html5lib is a separate network action.
The public download is executed in CI as a negative-control check.

The case claims no measured time saving, comprehensive security, complete
accessibility, improved ranking, client result, or personal experiment. Its
publication date, linked byline, Article identity and native section outline are
rendered from the existing page system. It is a Technology reference article,
not an entry in the existing Notes or subject RSS publishing catalogs. No historic
feed record is rewritten or duplicated.

## Search rationale and boundaries

The two pages answer different needs: comparing the full time cost of an AI
workflow, and checking an AI-assisted website change. Their titles and descriptions
reflect those actual functions. These are relevance hypotheses, not keyword-volume
research or promises to rank. Both have canonical URLs, sitemap entries, visible
internal links, shared author identity and matching structured data.

No new tracking, sign-up gate, paid service, social handle, portrait, credential,
testimonial, rating or private project material is introduced. No special AI-search
file or invented schema is added. The calculator is described as a WebApplication
that performs arithmetic, not an AI model. The recorded case is an Article and
inherits the established author profile.

## Review and regression coverage

The new arithmetic suite compares 254 scenarios, including 250 deterministic
random cases, with Python Fraction calculations independent of the browser code.
It tests exact break-even, zero savings, negative savings, limits, invalid input,
page-scoped assets, static examples, source preservation and metadata.

The new browser suite exercises required input recovery, changed-input
invalidation, estimates/observations, the quality condition, clear confirmation,
clipboard success/failure, exact text download, no input transport/storage,
pagehide/bfcache clearing, 320/390/768/1440 layouts, expanded text spacing,
keyboard paths, no-script/blocked-script fallbacks and automated accessibility.
Local offline runs do not establish live navigation or axe results; the complete
HTTP suite and all 21 earlier browser suites are required in the GitHub release
gate, for 22 browser suites total.

Visual review found cramped unstyled jump links on the first candidate. Scoped
layout styles now separate these links and give the case outline a readable
presentation. The no-script worksheet journey uses native keyboard navigation.
No fallback coverage was removed to accommodate the test environment.

Only the intended About, Technology and Resources presentation snapshots were
rebased. An independent new baseline pins the original home, identity, layout,
contact code, privacy source, global design, original article sources and feeds.
Source changes and generated output must be committed together. CI success and
public deployment verification are separate requirements; the PR receipt records
the final statuses rather than assuming them here.

## Primary guidance consulted

- Google, people-first content, original value and accurate authorship:
  https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Google, AI features use the same foundational search practices, without
  additional special files or schema requirements:
  https://developers.google.com/search/docs/appearance/ai-features

The remaining high-value personal contribution is a chosen authentic portrait
and a genuinely observed real-life workflow with permission-cleared artifacts.
This release does not substitute fictional measurements for those contributions.
