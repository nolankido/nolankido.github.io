# AI Works Human Decides: release regression repair

Prepared October 27, 2026, Pacific/Honolulu.

## Purpose

Complete the release qualification for the approved Nolan Kido positioning in
[PR #143](https://github.com/nolankido/nolankido.github.io/pull/143). The homepage,
About page, Technology introduction, public biographies, profile metadata and
selected sharing image connect Nolan's name with **AI Works Human Decides** and
practical AI use. This turn repairs the regression checks that blocked that
release. It does not add a new authority claim or publish another case study.

## Why the old checks failed

Historical tests deliberately retain earlier output counts and content hashes.
The separately published identity JSON-LD and later approved branding changes
had not all been reconstructed before those old comparisons. Several tests
therefore compared the current release with an earlier inventory. Replacing
the recorded hashes or ignoring every changed path would lose the protection
those tests were intended to provide.

## Repair

- Add a common test-only history boundary in
  `_tests/later_release_history.py`. It reverses the identity build insertion
  only when the complete successor SHA256 matches, then verifies the exact
  predecessor SHA256.
- Remove approved added production files from an earlier inventory only when
  their full hashes match. Unknown files and altered bytes remain visible to
  the old tests. Two specifically named fixture-authoring tools are treated as
  test support rather than runtime production files.
- Compose the branding metadata reversal before the earlier profile history.
  Preserve the existing historical dates, counts and fingerprints.
- Keep the historical live-target count of 475 while separately asserting all
  476 current targets, including the exact new sharing image response. A wrong
  status, changed bytes or unknown route cannot be hidden by the history view.
- Rebuild the scoped social-card fixture from pinned Git trees rather than
  working-tree differences. Its non-writing `--check` reproduces the existing
  record, covering 87 edited paths and one added asset.
- Update the homepage browser journey to click the approved primary button,
  arrive at `/technology/#ai-works-human-decides`, and check the visible method
  heading before continuing through the existing journey.
- Keep the full homepage sharing-metadata comparison while allowing exactly
  the approved card URL and alternative text. All 107 distinct article and
  subject-hub preview checks remain intact.
- Increase only the build job's time limit from 15 to 30 minutes after the
  complete hosted run exhausted its earlier budget. Preserve every test and
  browser group. An exact SHA-bound reversal keeps the older workflow fixture
  check meaningful, including rejection of changes to other job limits.

The regression adapter commit is
[`9be895ec7503d78a3b543dcd761a0a851b339c50`](https://github.com/nolankido/nolankido.github.io/commit/9be895ec7503d78a3b543dcd761a0a851b339c50).
Its tree, `6ef59a2feba8a7ae28c9514b636b21aacf09f3ee`, exactly matches the
independently reviewed local candidate. The browser-journey assertion, build-job
time limit and this record follow that commit in the same PR.

## Verification record

Local preflight checks passed for all 223 committed generated files and the
static search audit of 194 public pages, including 189 sitemap URLs. The
28 newly added history, composition and fixture-authoring tests passed. Their
negative cases reject unknown mutations, wrong response types, corrupt
predecessors, unapproved fixture scope and stale fixture records. A separate
read-only code review found no must-fix issue in the history repair.

The final PR head must pass the complete unit suite, HTML validation and all
five existing hosted browser groups before merge. The current receipts belong
to the PR's checks and release description; preflight results alone do not
establish completion of those gates. After squash merge, verify the Pages
deployment and the complete published-byte check against the resulting main
commit. Keep the existing branch-based Pages configuration.

## Scope and evidence limits

This repair changes tests, test history helpers, a fixture-authoring script,
the build job's time budget and this report. It does not change the approved
public page content or runtime
behavior. The separate unlinked identity JSON-LD stays separate, and the two
untracked uploaded portraits are outside the release.

Passing software checks establishes the behavior and publication of the site.
It does not establish search-engine indexing, AI citations, reader recognition
or expertise. The next content priority remains an inspectable ordinary-task
case with permitted inputs, the actual brief, output, corrections and a clear
human decision. Private source material and unobserved results must not be
invented or added to this public repository.
