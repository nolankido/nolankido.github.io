# Visibility sprint, Turn 13: Evidence-led links between practical AI and poker

**Review date:** November 3, 2026  
**Site:** https://nolankido.com/  
**Objective:** Improve accurate discovery of Nolan Kido's practical AI, technology and tournament-poker work by connecting existing substantive pages with clear contextual explanations.

## The specific discovery gap

The Technology landing page already explained “AI Works Human Decides” with a reviewed website-repair example. The Poker landing page provided independently identified tournament records, hand studies and episode material. Readers and search systems had to infer how these two bodies of work relate.

This turn adds two human-readable explanatory sections, not a new unsupported credential or speculative ranking claim.

## Published changes

1. [Technology: AI judgment in software, small-business workflows, and poker](https://nolankido.com/technology/#ai-judgment-across-domains). Explains why checks must match the claim, using three specific, already published first-party records.
2. [Poker: What can an AI solver actually tell me about a tournament hand?](https://nolankido.com/poker/#poker-ai-judgment). Describes separating recorded action from assumptions, checking a model's scope, and limiting retrospective conclusions.
3. Reciprocal links between these sections and an existing [hand-review framework](https://nolankido.com/poker/reviewing-a-hand/).
4. Contextual links to the previously verified authored Substack essays [AI Works, Human Decides](https://nolankido.substack.com/p/ai-works-human-decides) and [When to Trust the AI vs. When to Trust Human Instinct](https://nolankido.substack.com/p/when-to-trust-the-ai-vs-when-to-trust).

## Evidence and claim boundaries

| Link used | What can be said | What is not claimed |
| --- | --- | --- |
| [Website repair](https://nolankido.com/technology/checking-ai-website-changes/) | The source-reviewed repair passed 347 tests but retained an HTML defect. | A green test suite guarantees browser quality. |
| [Review-reply audit](https://nolankido.com/technology/review-reply-evidence-audit/) | Archived example drafts and counterexamples illustrate a bounded review method. | Measured production error rates or small-business ROI. |
| [Portland Meadows hand](https://nolankido.com/poker/episodes/portland-meadows-ep1/#hand-64o-record) | A documented first-person hand account illustrates information known during play versus later interpretation. | A complete verified GTO/ICM solution or an independently proven strategic edge. |
| Two Substack essays | Nolan Kido's published views on human review of AI outputs. | Independent validation of technical or poker outcomes. |

## Source integrity and regression coverage

- Updated original source templates `_source/technology/home.html` and `_source/poker/home.html`.
- Updated generated `technology/index.html` and `poker/index.html` to contain byte-identical new sections.
- Added `_tests/test_turn13_topic_paths.py` to check source/generated parity, link destinations, reciprocal anchors, bounded claims, exact-history reconstruction and unknown-edit preservation.
- Added `_tests/turn13_topic_paths_history.py`, a test-only SHA-gated predecessor for six reviewed files. Connected the existing Turn 11 and Turn 12 test-history adapters to it. No production builder imports the new predecessor.
- Python AST parsing succeeded for the modified test adapters and both new Python files.
- Existing internal destinations and the `#hand-64o-record` anchor were checked through the merged-branch GitHub content API.
- The full local test suite was unavailable in this read-only workspace. No full-suite pass is claimed.

## Publication and measurement

- [Pull request #169](https://github.com/nolankido/nolankido.github.io/pull/169) was squash-merged into `main` on November 3, 2026 at commit `22c69859e1d085b94f051e6d1e1df235e4a9d0d1`.
- The expected source and generated blobs were confirmed on the PR branch before merge, and GitHub `main` resolved to the merge commit.
- Public Pages propagation was independently checked after merge. See the final live verification note below.
- Publication itself does not establish a change in indexing, traffic, search rankings, third-party citations or inclusion in AI-generated answers.
- No GitHub Actions, scheduled jobs, new analytics, tracking, paid API configuration, private contact data or new runtime dependency were added.

## Next recommended improvement

Measure actual branded and non-branded impressions in Search Console for the Technology and Poker landing pages, then prioritize one additional, source-backed page or snippet revision based on observed query demand instead of presumed SEO benefit.

## Live verification

After built-in GitHub Pages propagation, the public [Technology page](https://nolankido.com/technology/#ai-judgment-across-domains) was retrieved and its rendered `#ai-judgment-across-domains` section returned the expected heading, comparison list, and supporting links. The public [Poker page](https://nolankido.com/poker/#poker-ai-judgment) was retrieved and its rendered `#poker-ai-judgment` section returned the expected heading, three-step decision framework, and links. The standalone public HTML sections were checked with element-scoped extraction, which verified more than prose alone. Neither observation measures search indexing or referral changes.
