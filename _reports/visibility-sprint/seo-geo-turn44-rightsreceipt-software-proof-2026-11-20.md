# SEO/GEO Turn 44: A source-backed, runnable software proof path for RightsReceipt

**Date:** November 20, 2026 (Pacific/Honolulu)  
**Main website:** https://nolankido.com/  
**Case:** https://nolankido.com/technology/rightsreceipt-ai-licensing/  
**Starting main commit:** `46383db3a57b8dd8b96895d4a05e8358fd369a6a`

## Turn 43 publication prerequisite

The prior Turn 43 content-production article and receipt are **now independently retrievable on the custom domain**. A fresh, read-only, query-scoped fetch returned the new `Which content was published?` paragraph and the contents of `/downloads/nolanpoker-content-production-receipt.md`. That confirms public **content-level availability**, not exact-byte parity, search indexing or user engagement. The earlier report of the new Markdown returning 404 no longer describes the most recent observation.

## Decision

For a distinct, real AI-assisted software-development case, use **RightsReceipt**, not an invented game-release case or another generic "AI builds apps" article. This project has independently observable publication on [Devpost](https://devpost.com/software/rightsreceipt), MIT-licensed [public source code](https://github.com/nolankido/rightsreceipt-hackathon), a pinned runnable local judge console, a source-level application-handler smoke, and a **separate actual local learned-model proof**. The public project and source state their unverified real payment and licensing gates directly.

The existing canonical article already explained seven authority boundaries and had a deep reproduction section, but a reader could not immediately find the **exact code files** to execute the two distinct tests from the opening. Adding a fast evidence route solves a real traceability gap without creating another indexable page or inventing usage metrics.

## Primary evidence independently inspected

| Evidence | Verifiable observation | Limit |
| --- | --- | --- |
| [Public Devpost entry](https://devpost.com/software/rightsreceipt) | The project is publicly submitted to the PayPal AI Hackathon with source, a recorded demo, synthetic AI diagnostic, and local application rehearsal | Submission is not a prize, endorsement, customer deployment or actual payment |
| [Pinned MIT-licensed source tree](https://github.com/nolankido/rightsreceipt-hackathon/tree/646182a95faf6ab5448f10927ded1650ff38bdf5) | Repository tree and `LICENSE` were read; the snapshot contains a localhost judge console, smoke, model proof and dedicated tests | Source existence alone does not prove those tests passed during this turn |
| [Judge guide](https://github.com/nolankido/rightsreceipt-hackathon/blob/646182a95faf6ab5448f10927ded1650ff38bdf5/JUDGES.md) | Specifies Node 22.13 through 22.x, no-secret local run commands and expected evidence contracts | Original project reports the November 10 run; not re-executed here |
| [Real handler smoke](https://github.com/nolankido/rightsreceipt-hackathon/blob/646182a95faf6ab5448f10927ded1650ff38bdf5/scripts/judge-console-real-smoke.mjs) | The code checks three local scripted journeys, three resets, zero external requests and `paymentEvidence: "simulated_only"` | Injected provider replies are not authenticated PayPal Sandbox settlement |
| [AI model proof](https://github.com/nolankido/rightsreceipt-hackathon/blob/646182a95faf6ab5448f10927ded1650ff38bdf5/scripts/judge-ai-proof.mjs) | The source validates real local learned inference, two authored synthetic requests, 24 rights-field comparisons, a visible contradiction warning and `paymentEvidence: "none"` | Not real-world accuracy, legal approval, or a PayPal transaction |
| [Local judge UI](https://github.com/nolankido/rightsreceipt-hackathon/blob/646182a95faf6ab5448f10927ded1650ff38bdf5/scripts/judge-local-console.mjs) | Node HTTP loopback UI launches separate rehearsal and read-only model diagnostic routes | A local functional demonstration is not a publicly hosted production product |

The publicly submitted example quote is USD 425.00, from a deterministic creator-defined policy, **not** a paid amount. The learned model's unsupported US/Canada classification despite "Germany only" is a documented model disagreement, not an authorized licensing choice. The owner and buyer decisions, copyright ownership and provider payment must each be verified separately before any real permission may be granted.

The [PayPal AI Hackathon rules](https://paypalaihackathon.devpost.com/rules) allow a usable demonstration to be run from documented source instructions without requiring a publicly hosted product. This provides context for why the published **localhost** demo is a real, runnable artifact while still not proving commercial deployment.

## Implemented improvements

1. Added one new, prominent `id="rightsreceipt-software-proof"` evidence block within the existing case's introduction. It links **directly to the three pinned source scripts**, the portable acceptance worksheet, and the explicit real-payment/rights limitations.
2. Added one `Test the code` native in-page navigation link to that anchor. No extra H2, duplicate canonical page or hidden navigation script was created.
3. Created [`downloads/rightsreceipt-local-software-acceptance.md`](../../downloads/rightsreceipt-local-software-acceptance.md), a no-login worksheet for an operator to inspect pinned source, run the local UI, run the handler smoke, run real local inference, record actual results and preserve human approval. It documents exact expected success fields and the synthetic contradiction as a **negative control**. The worksheet does not execute any code or contact PayPal.
4. Applied the **identical** source block and navigation edit to editable `_source/technology/rightsreceipt-ai-licensing.html` and generated `technology/rightsreceipt-ai-licensing/index.html`.
5. Added ten regression cases in `_tests/test_turn44_rightsreceipt_software_proof.py`, covering pinned path/order, early arrival, sections, dated canonical, worksheet commands/limits, the simulation/real-inference separation, release inventory and full generated-output parity.
6. Registered the new test in the manual `_scripts/local_release_checks.py`, the public downloadable file in the exact-byte `_scripts/check_live.py` inventory, and linked the case and worksheet from `README.md` and `AGENTS.md`.

The original November 13, 2026 publication date and seven-section outline remain. The reading estimate remains **about eight minutes**. This is a small evidence-navigation addition, not a new historical event or substantive retest.

## Verification and remaining acceptance

Source and generated article **were compared to the starting main Git blobs** and both differ by exactly the same added proof paragraph and native navigation jump, with no other article bytes changed. The original source claims, public Devpost identity, pinned code files, schema, date, seven headings and canonical remain unchanged. The eight-minute reading estimate is also preserved. The worksheet is an original new public download; it is not represented as a signed acceptance receipt for a real buyer or payee.

**Execution distinction:** This turn read the real public source and scripts via the GitHub connector and checked the public Devpost page. The model's working shell still lacks reliable external DNS to obtain a full checkout. The new ten-test Python module, Node judge smoke, standalone model run, full static generator, HTML5/browser suites and live response-byte comparison were **not executed** in this session. Static source-level assertions and GitHub diff inspection are separate from a successful runtime acceptance. Do not report historical local test counts as fresh Turn 44 results.

A complete, network-enabled checkout can run:

```powershell
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 -m unittest discover -s _tests -p test_turn44_rightsreceipt_software_proof.py -v
py -3 -m unittest discover -s _tests -p test_rightsreceipt_public_case.py -v
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/check_live.py --only /technology/rightsreceipt-ai-licensing/ --only /downloads/rightsreceipt-local-software-acceptance.md --attempts 3 --interval 5
```

For the **external project** and not the website build, use Node 22.13 through 22.x at the pinned source checkout as documented in the worksheet. The two independent proofs each use no paid API and no real financial transaction.

Actual first-party Google/Bing clicks, AI citations, real-world rights/license outcomes and payment receipts remain unavailable or unverified. A new public worksheet, link or software smoke cannot supply these metrics.

## Next improvement

**Turn 45:** Improve the site's topical source-discovery and internal links so visitors researching practical AI software can find specific bounded cases without assuming that a prototype or simulated payment is a production success. Favor one validated relevant path and preserve current canonicals; investigate deployment only from observed errors.

No GitHub Actions, cron, paid APIs, private credentials, new tracking, unverifiable production claims or autonomous payment workflows were added.
