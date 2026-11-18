# Local AI versus hosted AI: a reproducible task comparison

**Nolan Kido | November 18, 2026 | Status: protocol only, no paired measurements**

Use this packet to answer a narrow question: for **one specified, synthetic writing task**, can a model running on a Windows laptop produce an acceptable answer with less total time, cost, or data exposure than a selected hosted AI service? It cannot answer whether local models in general are faster, more private, cheaper, or better.

This packet accompanies:
- [The original local-only loopback checker](local-ai-loopback-check.py)
- [The empty trial worksheet](local-hosted-ai-comparison-blank.csv)
- [The pre-existing, historical CPU-runner record](local-ai-test-record.json)

## 1. Evidence now, before any test

- The historical three-case Gemma 3 record describes a **GitHub-hosted Ubuntu CPU runner**, not Nolan's MSI laptop, and it used **different fictional customer-review tasks**. It is background evidence, not the local arm of this comparison.
- The current Python script uses the synthetic note below, requests Ollama only on `127.0.0.1`, and defaults to `gemma3:4b` with `temperature=0` and `num_predict=96`. A dry run returns null measurements.
- No recorded run of this fixture on Nolan's laptop and no measured hosted service arm are supplied in the public record. Thus **comparative latency, task quality, net time saved, cost and carbon/energy claims are all unmeasured**.
- A locally served model is not necessarily a fully private workflow. The host application, OS, extensions, network settings and data inputs need separate examination.

## 2. Freeze the task

Copy the following prompt **verbatim**, including punctuation, to *both* arms:

> Classify this synthetic note into Task, Check, and Decision. Note: A fictional team has three meeting notes. Before sending a summary, they must compare each proposed action against the notes and obtain approval. Use exactly three labeled lines. Do not invent a deadline.

Expected behavior is **semantic**, not exact-string matching. One valid illustrative response is:

```text
Task: Prepare a summary of the team's proposed actions.
Check: Compare each proposed action against the three meeting notes.
Decision: Obtain approval before sending the summary.
```

The note gives no meeting-note contents, date or deadline, and no approval outcome. Do not add these facts to the prompt or judge the model by whether it can invent them.

**Fixture fingerprint:** The checker automatically prints the SHA-256 of this prompt. Preserve that fingerprint in the results sheet, and confirm the hosted prompt is character-for-character identical. If you edit the prompt, assign a new fixture ID and do not combine old and new trials.

## 3. Specify the comparison before running

1. Pick exactly **one installed local model** and **one named hosted model/service**, and record precise IDs and versions where available. Do not switch among hosted models mid-test.
2. For each arm, record interface, UTC date, model name/digest (if exposed), application/runtime version, hardware class (coarse public description is enough), context limit, prompt wrapper/system instructions, temperature, output-token cap, and whether settings are known or unavailable.
3. Local arm: use the same Ollama model and settings on each attempt. Hosted arm: request the same prompt, low temperature and approximately the same output cap if the interface permits. If the hosted UI hides generation settings or silently adds instructions, mark **unmatched settings**, not a controlled speed head-to-head.
4. Use synthetic notes only. Do not paste customer information, internal work documents, credentials, manuscript excerpts, or personal identifiers into hosted apps for this test.
5. Decide what counts as cold load (first call after model load or application start) and warm call. Record separately. Do not average them together.
6. Plan at least **three complete, independent attempts per arm**, using a comparable connection and the same reviewer. Three attempts are a small descriptive sample and cannot establish statistical or population-level superiority.
7. If you plan to claim **net labor savings**, also run a manual, no-AI baseline for the same task and measure setup, checking, corrections and repeat frequency. Without that baseline, report model response time only.

The arms must share the same task and quality rubric, even if their inference infrastructure differs. Treat the differences as limitations. Do not compare Ollama's `eval_duration` (token-generation time) against a hosted service's full page load or time to paste and click send. Compare **request-to-complete wall time** only if measured with equivalent boundaries; otherwise describe each timer separately.

## 4. Local procedure (Windows PowerShell)

From the checked-out website repository:

1. To inspect the record shape without any model call:

   ```powershell
   py -3 downloads/local-ai-loopback-check.py --dry-run
   ```

2. Install and download Ollama and the selected model separately if you have not already done so. The check script never installs or downloads anything. Confirm the Ollama server is bound to loopback rather than a public interface.
3. To measure an explicit local run and show its answer for human review:

   ```powershell
   py -3 downloads/local-ai-loopback-check.py --model gemma3:4b --show-output
   ```

   The added `--show-output` flag is **opt-in**. By default the script records an output fingerprint without printing the generated text; showing the text does **not** mark it quality-approved. It is used solely so a human can score a real response against Section 6. Never publish raw outputs from private tasks.

4. Record the printed `fixture_sha256`, `wall_seconds`, `eval_count`, `eval_duration_ns`, `tokens_per_second`, `output_sha256` and `human_quality_review` where present. Leave absent values empty. The last field remains `not_performed` until independently scored. Note warm/cold state and any errors.
5. Repeat with identical local settings at least three times. Do not silently discard failed, timed-out or malformed attempts; assign those an explicit status.

If no installed model or laptop is available, **stop here** and retain the blank worksheet. A `--dry-run` is not a model execution.

## 5. Hosted procedure (explicit and separately authorized)

1. Choose a hosted service and its named model; record its public/model ID, date and available settings. You must have legitimate access and permission to use it. This packet does not call hosted APIs, request credentials, or submit content on the reader's behalf.
2. In a fresh conversation with no unrelated context if supported, supply the **exact same synthetic prompt**. Note any non-removable system prompt, safety layer or model setting.
3. Start the wall clock immediately before the submitted request and stop when the full response is visible. Include client/network effects in this hosted elapsed time, and **label that boundary**.
4. Copy the output into a **private evaluation record**, optionally retain a SHA-256 fingerprint, and apply the identical rubric below. Do not upload raw text to this public repository without a content/privacy review.
5. Run the planned attempts, recording all failures and whether the service provides input/output tokens or cost. Unknown is not zero. No paid account, signup or hosted run is required to use the protocol.

If a comparison has different timer boundaries, settings, cache states or output caps, show **two separate per-arm descriptions** instead of a performance winner.

## 6. Human answer-quality rubric

Score each independent response using the five binary gates below, with **1** if clearly satisfied, **0** if not, and **blank** if not yet reviewed. A pass requires **5/5** and no disqualifying invented fact.

| Gate | Pass condition |
| --- | --- |
| `format_ok` | Exactly three nonempty labeled lines, `Task:`, `Check:` and `Decision:`, in that order. |
| `task_ok` | Identifies the team's task as preparing or sending a summary of proposed actions, without asserting unprovided note contents. |
| `check_ok` | Says **each proposed action** must be compared with the three meeting notes before summary distribution. |
| `decision_ok` | Says approval must be obtained **before** the summary is sent; does not claim it was already granted. |
| `no_invention_ok` | Does not invent a deadline, approval result, meeting participant, action, note content or outside source. |

Record reviewer ID or initials, review timestamp and a short reason for any failed gate. Two reviewers are preferable for stronger claims; where only one reviews, disclose that fact. A response can contain correct words but still be useless or misleading; the rubric does not test broader helpfulness or safety for real decisions.

**Important:** The checker returns `human_quality_review: "not_performed"` even with `--show-output`. Do not change that field to `pass` without a separate documented human judgment.

## 7. Record and compare the whole task

Use [the blank CSV worksheet](local-hosted-ai-comparison-blank.csv). One row per actual attempt, not one row per model. Keep preliminary or test rows labeled `dry_run` or `synthetic_example` and **exclude them from computed averages**. The downloadable worksheet deliberately contains no attempt rows.

For each arm, distinguish:

- **Generation wall seconds:** elapsed from equivalent invocation point to complete response, with timer caveats.
- **Total hands-on minutes:** preparation + prompt setup + generation wait during which the reviewer cannot do other work + quality review + correction/retries. Avoid double-counting overlapping work.
- **Setup and upkeep:** installation, download, updates, prompt/version maintenance, troubleshooting and (if relevant) hosting configuration, amortized across a stated number of tasks.
- **Money and hardware:** fees and local hardware/energy estimates if independently measured or sourced. Report unknown values as unknown.
- **Privacy exposure:** which input crosses a third-party boundary and which technical evidence supports the assertion. Do not infer privacy solely from the word "local."
- **Task result:** 5/5 pass status, rework needed and reviewer notes.

For a meaningful labor comparison, use a separately measured **manual completion time** for the same task. One descriptive formula, with all minutes measured on comparable boundaries:

`Net minutes saved per task = manual baseline minutes - (assisted preparation + supervised wait + review + repair + amortized setup/upkeep minutes).`

If manual baseline, review time or repeated tasks are missing, **do not output a net-savings number**. An unpriced local computer and a free hosted tier are not proof of equal cost.

## 8. What a publishable conclusion requires

You may publish a **descriptive, narrow comparison** only after both arms have real dated outputs, matching synthetic prompt fingerprints, stated settings and timer boundaries, quality reviews, count of failures and privacy review of the evidence. Include each attempt, not only the best one. State sample size, median and range, with no unearned statistical generalization.

Do **not** publish a local-vs-hosted speed winner when either arm is missing. Do **not** describe the October 2026 GitHub CPU experiment as an MSI gaming-laptop test. Do **not** claim time or cost savings without the relevant whole-task and manual-baseline records.

Current release decision: **NO COMPARISON RESULT YET.** This is a ready-to-run protocol, not an observed benchmark.

## Sources and scope

- [Nolan Kido, local AI gaming-laptop case](https://nolankido.com/technology/local-ai-gaming-laptop/)
- [Historical local AI test record](https://nolankido.com/technology/local-ai-test-record/)
- [Ollama script in the website repository](https://github.com/nolankido/nolankido.github.io/blob/main/downloads/local-ai-loopback-check.py)
- [Official LM Studio local server documentation](https://lmstudio.ai/docs/developer/core/server) and [offline operation](https://lmstudio.ai/docs/app/offline), useful alternative context only. This specific fixture and checker use Ollama, **not LM Studio**.

No warranty of equal model capability, technical privacy, profitability or statistical significance is implied. All measured-result cells remain blank until independently run and reviewed.
