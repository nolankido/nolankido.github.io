# A source-backed research record for Nolan Kido

Date: November 13, 2026

## Objective

Strengthen the public professional record with independently attributable
scholarship instead of relying on a short credential-style claim. Publish a
plain-language reader's guide to the 2012 peer-reviewed government-accounting
paper in a page that is indexable, linked to the same Person entity, and
careful about the limits of observational research and historical affiliation.

## Independent primary records reviewed

- Publisher: https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1475-679X.2012.00447.x
- DOI: https://doi.org/10.1111/j.1475-679X.2012.00447.x
- MIT manuscript listing: https://dspace.mit.edu/entities/publication/9e5c8e82-34b0-4931-a8cc-6ea0ae938829

Both independent records list Nolan Kido, Reining Petacchi and Joseph Weber
as authors. The journal article was first published February 6, 2012, later
appearing in Journal of Accounting Research 50(2), pages 443-476.

The publisher and repository abstracts report systematically lower compensated
absence and unfunded pension liabilities in election years, and correlations
with proxies for gubernatorial incumbents' incentives and ability to influence
financial reporting. The paper interprets these findings as consistent with
manipulation of accounting numbers, but this website does not infer an
individual's illegal conduct, causal certainty or a general effect size.

The full manuscript download returned an HTTP 429 rate-limit response in the
public verification environment. Do not claim its tables, sample design or
model specifications were independently reanalyzed in this release. Readers
can follow the MIT link themselves for the exact methods and original tables.

## Changes

- Add `/about/accounting-research/` with the original paper citation, a
  layperson explanation of the studied accounts and the reported findings,
  transparent caveats, an evidence table, and an explicitly personal link to
  the current AI-judgment philosophy.
- Link to it directly from Home, About and Projects while keeping the original
  publisher and MIT links visible.
- Record the 2012 paper as a `ScholarlyArticle` entity in JSON-LD, separate from
  the 2026 `Article` that describes it; share the stable author Person ID.
- Add a reproducible Article test and the existing no-CI local release runner.
- Update homepage modification date to the actual material-content revision.

## What this does not establish

- A current academic appointment, MIT affiliation or additional credential.
- An AI publication, a proven model result, causal attribution, or an audited
  current government financial statement.
- Improved search impressions, referrals, AI citations or rankings. These
  remain measurements for the existing monthly visibility protocol.

## Validation

Run the deterministic build, search and HTML5 audits, 85-item local release
checklist, and direct live-byte comparisons. Never enable GitHub Actions.
