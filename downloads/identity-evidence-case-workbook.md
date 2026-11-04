# Case record: AI-assisted identity metadata, with an evidence gate

Nolan Kido | November 4, 2026 | Public-source example | AI Works Human Decides

Canonical explanation: https://nolankido.com/technology/#identity-claim-audit

## Why this was a real task

The personal website already presented practical-AI work, business context, accounting scholarship and tournament poker. An older, separately downloadable JSON-LD identity document contained more ambitious professional claims than the public About page was prepared to support. The practical task was to make those claims consistent with evidence while keeping valid author identity, publication and profile links intact.

The identity record was already public. This was a correction, not a private draft review or evidence of search-traffic growth. The document is not loaded into the visible Home or About HTML. Its existence does not establish that a search engine or assistant used it.

## Fixed source trail

- Before: [standalone identity asset at the reviewed base commit](https://github.com/nolankido/nolankido.github.io/blob/fa03f1b355d4b71291215168a7960fad97ec3ff0/assets/nolan-kido-identity.jsonld).
- After: [standalone identity asset at the published correction](https://github.com/nolankido/nolankido.github.io/blob/a1e2f1c64e185c3d97fc813f47c75968cc769ab9/assets/nolan-kido-identity.jsonld).
- [Exact code review, PR #180](https://github.com/nolankido/nolankido.github.io/pull/180), merged November 4, 2026.
- [Review notes and evidence boundaries](https://github.com/nolankido/nolankido.github.io/blob/a1e2f1c64e185c3d97fc813f47c75968cc769ab9/_reports/visibility-sprint/sprint50-turn24-2026-11-04.md).
- [The scholarly article's DOI](https://doi.org/10.1111/j.1475-679X.2012.00447.x), for the factual claim of coauthorship, not a current MIT job.
- [MIT-hosted manuscript record](https://dspace.mit.edu/entities/publication/9e5c8e82-34b0-4931-a8cc-6ea0ae938829), also not proof of employment or awarded degrees.

## Before and after

| Item | Before review | After review | Evidence decision |
| --- | --- | --- | --- |
| Public Person ID | `https://nolankido.com/about/#nolan-kido` | Unchanged | Preserve the canonical entity identifier. |
| `jobTitle` | “AI Startup Founder and Angel Investor” | Field removed | The claim lacked sufficient reviewed public support for this release. Removal is not a claim it was never true. |
| `hasCredential`, `alumniOf` | Two University of Hawaiʻi degrees and alumni record | Fields removed | No confirming credential record was examined here. Do not infer that the degrees were not earned. |
| `affiliation` | MIT “Research Affiliate” | Field removed | A paper deposited at MIT does not prove an institutional appointment. |
| `description` | Startup and investor language plus practical work and prior COO title | More specific practical-AI focus with historical COO wording retained | Descriptions still require independent factual review; this correction is not certification. |
| Publication, names, links | Journal article, author identity and existing `sameAs` profiles | Preserved | Keep the evidence and connections that are not part of this correction. |

## What AI did, and what a human still must decide

An AI assistant inspected the repository's public identity data and the source-linked About page, identified fields requiring further evidence, proposed the narrower description, edited the source and generated JSON-LD, and opened a pull request. The user authorized the improvement workflow. There was **not** a line-by-line, independent human verification of every historical professional, academic and account-ownership claim in this record. Do not describe the automation as a formal background investigation.

The editorial boundary was conservative: when a prominent credential or current-role claim could not be substantiated from the evidence reviewed, leave it out of search-facing structured data rather than guessing. The owner may later restore a correctly sourced fact after verifying dates, institution, title, and permission to publish. Human accountability includes the right to correct this report.

## Reproduce the structural part without contacting a service

The public site provides a [standalone Python checker](https://nolankido.com/downloads/identity-evidence-gate.py). It requires Python 3.10+ and uses only the standard library. It does not call a model, crawl websites, verify degrees or track visitors.

1. Open the two fixed GitHub blob URLs above. Use GitHub's **Raw** control and save the complete files as `before.jsonld` and `after.jsonld` in one folder.
2. Save the checker to the same folder.
3. On Windows run:

```powershell
py -3 identity-evidence-gate.py --self-test
py -3 identity-evidence-gate.py --before before.jsonld --after after.jsonld
```

On macOS/Linux replace `py -3` with `python3`. The self-test runs five synthetic comparisons. The second command checks the real files you downloaded. Code 0 means its **limited structural invariants** passed; 2 means a field or identity change needs review; 1 means invalid input or an execution error. Code 0 does not establish that the biography is true, lawful, indexable or endorsed.

The checker verifies the canonical Person ID, scholarly DOI, unchanged publication and WebSite nodes, existing identity links, and removal of the specific sensitive fields in this case. It notes description changes for manual review. Do not use private documents or person records as inputs. The tool is tailored to this public example, not a universal JSON-LD compliance validator.

## Apply the method to your own public identity

- **Scope:** list the exact URLs and source files that actually publish personal or professional claims. Note whether data is visible in HTML, supplied in linked JSON-LD, or merely present as an unused asset.
- **Separate fact from inference:** authorship of a paper does not prove employment at the institution hosting it; a former title does not establish a current job; an unverified degree claim is not safely rescued by a confident description.
- **Evidence worksheet:** for each claim, record the literal field, its proposed wording, a primary source, what that source actually establishes, the reviewer, the decision (keep, narrow, remove, verify later), and a dated correction reference.
- **Protect invariants:** preserve stable IDs, verified authorship, canonical URLs, public links and publication dates unless evidence justifies a change.
- **Compare output with source:** rebuild the published page or asset, parse JSON-LD, inspect the diff, and run an independent check for unintended removals.
- **Human release gate:** ask the owner to confirm sensitive role, affiliation, degree and biography claims before featuring them. Make corrections reversible.
- **Measure honestly:** track branded queries, relevant entry pages and dated AI citations only with actual measured data. A corrected file is not a traffic win.

## Limitations and next checks

The source and published asset were confirmed equal after the correction; the larger local test and browser suites were not executed in the GitHub connector session. The automated checker above is deliberately narrower than human fact-checking. Historical COO language remains an owner-approved self-description, not an independently verified employer record in this audit. External profile ownership was not reauthenticated. The correction made the public record more conservative; its effect on ranking, citations and visitor trust has not been measured.

Google's [people-first content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) and [generative-content accuracy guidance](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content) explicitly prioritize accurate, helpful material, including metadata and structured data. Those are editorial principles, not proof of a ranking benefit for this page.

**The reusable rule:** before publishing an AI-assisted introduction to a person or organization, separate what is publicly evidenced from what a model can fluently assert. Preserve verifiable history, remove unsupported prominence, and keep the final publication decision with a responsible person.
