# RightsReceipt: Run the software, inspect the evidence, decide what remains unverified

Nolan Kido | November 20, 2026 | Public, read-only software acceptance worksheet

This is a repeatable local inspection of a **publicly submitted, runnable prototype**, not a completed financial transaction or an independent audit of real creative licensing. Use the pinned RightsReceipt source snapshot below, not an unverified later revision. The example participants, creative work and proposed USD 425.00 license are project-authored fiction.

## Provenance and version

- [Public PayPal AI Hackathon submission](https://devpost.com/software/rightsreceipt) establishes that this specific project was publicly entered and describes its demo and evidence boundaries.
- [Pinned public MIT-licensed source](https://github.com/nolankido/rightsreceipt-hackathon/tree/646182a95faf6ab5448f10927ded1650ff38bdf5) allows source and tests to be inspected without a private repository.
- [Pinned judge guide](https://github.com/nolankido/rightsreceipt-hackathon/blob/646182a95faf6ab5448f10927ded1650ff38bdf5/JUDGES.md) states Node version, run commands, expected outcomes and limits.
- [Public site case study](https://nolankido.com/technology/rightsreceipt-ai-licensing/) explains the seven different authorities, the classifier's visible mistake and the uncompleted genuine payment gate.

A public source checkout and a Devpost submission prove a published **software prototype and demonstration method**. They do not prove a hosted production service, genuine legal permission, model accuracy across customers, actual PayPal payment, or adoption.

## First: keep the input and permissions bounded

Use **Node 22.13 through 22.x** and a clean checkout of the pinned public snapshot:

```powershell
git clone https://github.com/nolankido/rightsreceipt-hackathon.git
cd rightsreceipt-hackathon
git checkout 646182a95faf6ab5448f10927ded1650ff38bdf5
node --version
```

The pinned judge commands do not require PayPal credentials, a paid AI API, `npm install` or authentic customer information. Do not place real buyers, creator identity documents, copyrighted files or credentials in test fixtures. Review the [judge guide](https://github.com/nolankido/rightsreceipt-hackathon/blob/646182a95faf6ab5448f10927ded1650ff38bdf5/JUDGES.md) before running any local script.

## Check A: actual handler flow with deliberately simulated payment

Read the [smoke implementation](https://github.com/nolankido/rightsreceipt-hackathon/blob/646182a95faf6ab5448f10927ded1650ff38bdf5/scripts/judge-console-real-smoke.mjs), then run:

```powershell
node scripts/judge-console-real-smoke.mjs
```

The script exercises the real localhost judge-console handler route and verifies the report and JSON output from a local application rehearsal. The code's success contract includes:

| Field | Expected in a passing local smoke |
| --- | --- |
| `status` | `passed` |
| `mode` | `local_injected` |
| `scenarioCount` | `3` |
| `resetCount` | `3` |
| `externalRequests` | `0` |
| `paymentEvidence` | `simulated_only` |

The three scripted journeys include the ordinary license path, ambiguous invoice-send recovery, and repeat/reset behavior. The current fixture's deterministic proposed quote is USD 425.00. A passing local test demonstrates **application behavior under injected provider responses**, not a genuine payment or authorization from real customers.

If the smoke fails, record the error locally and do not turn an incomplete or failed run into an advertised pass. A source file containing a success assertion is not proof that the code succeeded when **you** ran it.

## Check B: real local AI inference on synthetic rights requests

Read the [model proof script](https://github.com/nolankido/rightsreceipt-hackathon/blob/646182a95faf6ab5448f10927ded1650ff38bdf5/scripts/judge-ai-proof.mjs), then run:

```powershell
node --no-warnings --experimental-strip-types scripts/judge-ai-proof.mjs
```

The expected contract is `modelExecution: "real_local_inference"`, `syntheticRequestCount: 2`, `evaluatedRightsFields: 24`, `contradictionWarningVisible: true`, and `paymentEvidence: "none"`. This invokes a bundled, hash-checked learned classifier and a separate source-span extractor. It is **not** hosted-model inference or a real buyer's request.

The important counterexample is intentional: a synthetic request says **"Germany only"**, while the model proposes the **United States and Canada** as resolved territory. The diagnostic exposes that conflict and asks for a human decision. Do not convert numeric classifier margins into confidence probabilities, or silently adopt a proposed scope when the request contradicts it.

## Check C: interact with the local demonstrator

Read the [judge-console source](https://github.com/nolankido/rightsreceipt-hackathon/blob/646182a95faf6ab5448f10927ded1650ff38bdf5/scripts/judge-local-console.mjs), then run:

```powershell
node scripts/judge-local-console.mjs
```

Open the printed `http://127.0.0.1:PORT/` address in your own browser, run **Run application rehearsal**, and separately run **Run read-only AI diagnostic**. The interface displays status and evidence on the local device. It is not evidence that there is a public production service. Stop the local console with Ctrl+C.

For each route, record the actual status, source commit, local Node version, and whether the displayed outcome matched the contract. Do not share local server tokens, confidential data or private request payloads.

## Human acceptance boundary

| Decision or fact | Rightful authority | What remains outside the local proof |
| --- | --- | --- |
| Use rights and creator identity | Actual rightsholder and independent identity evidence | Demo artwork and a typed creator name cannot establish copyright ownership |
| License scope | Creator approval and buyer's acceptance of the exact reviewed version | AI labels do not authorize missing, conflicting or unmentioned terms |
| Proposed price | Creator's explicit pricing policy | The model does not set a binding or independently fair market rate |
| Invoice paid | Authenticated PayPal status and verified webhook for the same invoice | `simulated_only` and browser redirects cannot establish financial settlement |
| Receipt and permission | The consented scope plus verified provider state, subject to legal review | A SHA-256 record is not a digital signature or proof of enforceability |

The developer's [separate genuine Sandbox acceptance runbook](https://github.com/nolankido/rightsreceipt-hackathon/blob/646182a95faf6ab5448f10927ded1650ff38bdf5/docs/paypal/SANDBOX_ACCEPTANCE.md) describes a future verification requiring actual buyer-side Sandbox payment and authenticated provider evidence. **This worksheet does not run that path** or certify its completion.

## Outcome record, to fill in privately

- Pinned source commit checked:
- Local Node version:
- Application smoke run date and result:
- `scenarioCount`, `resetCount`, `externalRequests`, `paymentEvidence` actually observed:
- Classifier proof run date and result:
- Conflicting-territory warning actually observed:
- Browser console paths inspected:
- Failed or inconclusive checks:
- Human decision on whether to keep testing, revise, or hold the prototype:
- Outstanding requirements before a real user or payment:

The public [Devpost project](https://devpost.com/software/rightsreceipt) reports that the pinned source's local smoke and model proof passed on Node 22.16.0 on November 10, 2026. **That is an attributed historical release result.** The public code and published article can be inspected now; this worksheet does not silently repeat the November 10 execution or guarantee a later result. Do not publish a filled acceptance record without removing any private details.

**Conclusion:** A runnable local prototype, a working simulated handler exercise, and actual model inference are three different observations. Human acceptance of real licensing terms and provider-confirmed payment still require separate evidence.
