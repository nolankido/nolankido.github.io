# SEO/GEO improvement Turn 46: Four-case AI reliability and human stop rules

**Date:** November 20, 2026 (Pacific/Honolulu)  
**Website:** https://nolankido.com/  
**Canonical guide:** https://nolankido.com/technology/check-ai-answers/#review-stop-rules  
**Starting GitHub main:** `1ae6d3246645f09bd979130742d938aee0779b7b`  
**Roadmap:** Turn 46 of 37 through 61, final Phase B practical-AI expertise improvement

## What this turn accomplishes

The existing How to Check AI Answers page already taught six differentiated source, number, summary, message, code and advice checks. It lacked one crucial operational decision: **after running a check, when should the person proceed, fix the output, hold the consequential action, or stop using AI for that task?**

Instead of adding another near-duplicate SEO article, this turn adds one early **four-case decision matrix** to the existing canonical guide, links it from the Technology task hub, and offers a detailed offline **AI stop-rules field guide** with a private release decision record. The source examples and permission boundaries are explicitly attributed, not generalized into model failure rates.

The scope is practical and evidence-bound. A model can help draft a response, classify licensing terms or summarize a poker hand. It cannot turn a narrow green check into authorization, truth outside the tested scope or a verified commercial result. **Proceed in scope, revise, hold and stop using AI for this task** are review decisions, not claims that software can make them automatically.

## Evidence and test boundaries

| Existing original case | Actual evidence used | Required decision or limitation |
| --- | --- | --- |
| [AI-assisted website repair](https://nolankido.com/technology/checking-ai-website-changes/#case-source-diff) | Historical build and 347 unit/content tests passed before a distinct HTML5 parser detected an extra closing tag. Pinned pre-repair and repaired source endings were previously checked. | Rebuild and parse before the site release. This demonstrates a different check, not universal correctness or increased Google visibility. |
| [Review Reply Writer](https://nolankido.com/technology/local-ai-review-replies/#reply-operator-decision) | Historical Gemma output for a fictional review lost a precise 25-minute duration in a retry. Four **constructed** test sentences yielded two missed financial offers and one quoted-warning overflag in a narrow independent screen. | Human owner must inspect actual source details, the real authorized policy and exact saved reply. Neither a green screen nor the customer authorizes a refund or gift card. No production error percentage is inferred. |
| [RightsReceipt](https://nolankido.com/technology/rightsreceipt-ai-licensing/#rightsreceipt-software-proof) | A publicly submitted prototype has a source-backed local scripted application test with **simulated payment responses** and a separate real local learned-model proof on synthetic requests. The source visibly raises a conflicting US/Canada suggestion despite Germany-only wording. | The model's label cannot override source rights, creator and buyer acceptance or authenticated provider settlement. The actual paid Sandbox and legal-authorization gate remains unverified. |
| [NolanPoker editorial study](https://nolankido.com/technology/ai-poker-video-evidence/#poker-ai-approval) | Three proposed captions and a source-limited structured fact screen, with historical synthetic negative controls. The structured evidence still marks current-cut graphics and human release approval false. | A published written proposal is not a certified overlay in the released video. Check the actual current export, narration, card graphics and media rights or omit unsupported claims. |

The new field guide states precisely which of these observations are historical, which examples are deliberately fictional or constructed, and which proposed outcomes were never checked. These four different cases cannot be combined into a general AI accuracy or economic performance estimate.

## Changed publication artifacts

1. `_source/technology/check-ai-answers.html` gained a **direct first-screen anchor** to `#review-stop-rules` and one accessible H3-level source-linked matrix before the existing six-claim teaching examples. The table uses native semantic markup and the site's existing horizontally scrollable table pattern, including a keyboard-focusable region and reading guidance. No new styles or scripts.
2. `technology/check-ai-answers/index.html` received those same content changes and an updated publication-revision label, `dateModified` and reading estimate.
3. `downloads/ai-stop-rules-field-guide.md` is a new self-contained public, copyable worksheet. It gives decision definitions; the four original linked cases; six checks from permission through cost and current-version release; four worked decision outcomes; and a blank **owner-private** verdict record. It does not transmit or process user data or run an AI model.
4. `_source/technology/home.html` and `technology/index.html` gained a single contextual link in the existing Checking reader-task group. The first destination and all previous task routes stay intact.
5. `_source/pages.json` records a **real substantive modification** of the guide from November 19 to **November 20**, retaining its original **October 12** publication date. `sitemap.xml` now uses November 20 as this one canonical page's `lastmod`; all other sitemap entries remain untouched.
6. The guide's original **nine H2 sections** and six fictional teaching disclosures remain. Because this adds a meaningful cross-case comparison, the generated reading estimate advances from **22 to 24 minutes**, rather than misleadingly reusing the old label.
7. `_scripts/check_live.py` includes the new download in the existing read-only, exact-byte inventory. `_scripts/local_release_checks.py` includes **11 new regression tests** in `_tests/test_turn46_ai_stop_rules.py`.
8. Updated the Turn 21 Google source-check and Turn 24 poker claim tests so they continue to enforce their original factual boundaries while accepting the legitimately later November 20 revision of the shared guide. Other pages' original November 19 dates in those tests remain enforced.
9. `README.md` and `AGENTS.md` document the new canonical topic destination, direct sources, date ownership and no-GitHub-Actions restriction.

No new indexable or duplicate Article was created. There is no special "GEO schema" markup, changed Person identity, paid analytics connector, public form, customer dataset or remote model evaluation.

## Source checks and published evidence observed

Before authoring, a live read-only public fetch confirmed the existing AI checking guide, repaired website case, newly deployed owner decision example, RightsReceipt software proof and NolanPoker caption study were all retrievable on their canonical paths. The now-expanded owner decision checklist was also publicly retrievable. This verifies source availability at that observation, **not** the later Turn 46 deployment.

The new comparison preserves each individual truth boundary:
- 347 prior tests and the historical HTML5 defect are specifically recorded site-release results, not fresh test counts;
- a real archived Gemma reply differs from later **synthetic** checker probes;
- real local classifier inference is different from simulated payment evidence;
- a structured proposed-caption check is not a review of current MP4 frames, voiceover or released overlays.

The field guide explicitly treats matched full-workflow review cost as a separate gate. The six-case matched reply productivity protocol has not been executed. Unknown time savings, Google impressions, Bing citations and AI assistant answer citations are **unknown**, not zero.

## Verification status and complete-checkout commands

**Static checks performed in this turn:** GitHub source fetches, manifest/date checks, case/fragment reference validation, content-insertion inspection, source-versus-rendered comparison, new download inventory inspection and existing test expectation audit. The targeted tests are authored for both original and generated pages, source links, stop rules, change dates and offline download registration.

**Unexecuted:** The full deterministic static-site generator, the new 11-test Python module, original Turn 21/24 regression runs, HTML5 and browser suites, and exact post-merge public response-byte comparison. The local model container cannot resolve GitHub to obtain a complete checkout. These are **not** falsely described as passed.

From a complete local checkout:

```powershell
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 -m unittest discover -s _tests -p test_turn46_ai_stop_rules.py -v
py -3 -m unittest discover -s _tests -p test_turn21_ai_search_source_check.py -v
py -3 -m unittest discover -s _tests -p test_turn24_ai_poker_claim_bridge.py -v
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/check_live.py --only /technology/check-ai-answers/ --only /downloads/ai-stop-rules-field-guide.md --attempts 3 --interval 5
```

A full generated page and public byte-parity check are needed before calling the release fully validated. A GitHub main merge alone does not prove publication, search ranking gains, user satisfaction or commercial results.

## Next roadmap turn

**Turn 47: Verify actual book editions and retailer identities.** Inspect primary author, distributor, publisher and retail edition records for the two currently described books. Match each format and edition's authoritative title, author identity, public retailer URL, ASIN/ISBN and cover only where records actually support them. Leave unverified offers or purchase links unresolved rather than manufacturing them for SEO.

No GitHub Actions, scheduled tasks, paid APIs, tracking pixels, private customer records, unapproved payment flows or model-generated verdict automation were added in this turn.
