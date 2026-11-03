# Visibility sprint, Turn 12: Cross-platform identity coherence

**Review date:** November 3, 2026  
**Site:** https://nolankido.com/  
**Objective:** Associate Nolan Kido with practical AI, “AI Works Human Decides,” technology and tournament poker using accurately linked public work.

## Verified public identity links

1. [GitHub / nolankido](https://github.com/nolankido). Previously owner-approved source account for the site.
2. [DEV / kidon](https://dev.to/kidon). Previously reviewed public project-writing profile linking to the same GitHub account.
3. [Nolan Kido's Substack](https://nolankido.substack.com/). The public publication identifies Nolan Kido. Its [AI Works, Human Decides essay](https://nolankido.substack.com/p/ai-works-human-decides) links back to the canonical website and About page.
4. [NolanPoker on YouTube](https://www.youtube.com/@NolanPoker). The public channel's description identifies Nolan Kido by name, and the published Portland Meadows video watch pages link to that channel.

Public pages were inspected on November 3, 2026. The identity links show published work, not external verification of every strategy claim or AI result.

## Changes

- Expanded the narrowly bounded public-work profile list from two to four verified, descriptive links.
- Exposed those four profiles as visible `rel="me"` links on the [About page](https://nolankido.com/about/) and as `sameAs` values in the homepage and About `Person` structured data.
- Added a contextual About paragraph connecting the Substack philosophy essay and NolanPoker videos while clearly distinguishing publication from independent evidence.
- Added the same verified accounts to the richer, separately published [identity JSON-LD document](https://nolankido.com/assets/nolan-kido-identity.jsonld), retaining previous links and claims.
- Updated source and generated HTML consistently. No new standalone identity, invented credentials, awards, location, or performance data.
- Updated local regression tests. Historical release tests use an exact Git-blob predecessor bridge so older approved snapshots remain independently inspectable.

## Review and verification limits

- The existing professional identity record remains a separate, obscure publication and is not newly linked into visible page navigation.
- No additional personal addresses, employer claims, credentials, private analytics, contact details, tracking, scripts, forms, paid APIs, GitHub Actions or scheduled jobs were added.
- Source-to-generated parity, four unique visible `rel="me"` links, Person `sameAs` consistency, rich JSON-LD parity, unique HTML IDs, and the no-em-dash prose rule were checked statically.
- Python syntax was checked for all modified and newly authored Python modules.
- The full local unittest, HTML and browser suites were unavailable in this read-only workspace. No full-suite pass is claimed.
- A changed structured-data record is not proof of Google indexing, a knowledge-panel change, an AI-assistant citation, or higher search rankings.
- Public deployment is verified below.

## Post-merge public verification

- [Pull request #168](https://github.com/nolankido/nolankido.github.io/pull/168) merged into main on November 3, 2026, with commit `3f53b3aacd43a4be0e3fd71d8bae6faa87d40532`.
- GitHub main was checked for the expected generated About-page blob `53f0230fef94558288629b017f99aa2ebb766f4e`.
- The public [About page](https://nolankido.com/about/) was retrieved after propagation. It presents the new “Public work across platforms” explanation and visible links to both Substack and NolanPoker alongside GitHub and DEV.
- The public [rich identity document](https://nolankido.com/assets/nolan-kido-identity.jsonld) was retrieved and includes the Substack and NolanPoker URLs. The homepage's matching Person markup was verified in the exact merged Git blob, since the public text extractor omits embedded script data.
- These observations establish publication, not search indexing, knowledge graph adoption or AI-answer citations.
