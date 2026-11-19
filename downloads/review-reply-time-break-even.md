# Does AI save time on customer review replies?

An original, source-bounded review sheet from [Nolan Kido's AI Workflow Time Calculator](https://nolankido.com/technology/ai-time-savings/#reply-time-break-even). It separates historical machine case timings, missing human observations and fictional planning arithmetic. It makes no model or network calls and is not a business outcome study.

## Part 1: What an archived test actually recorded

The [October 2026 Review Reply Writer Gemma 3 4B smoke record](https://github.com/nolankido/reviewReplyWriter/blob/1c5e0487c331d5202410c9f342557d9355951c3a/examples/evaluation/live-quality-smoke-2026-10-13.json) contains three model-written outputs for fictional reviews. The saved results report these elapsed times:

| Fictional case | Recorded case elapsed time | Manual equivalent | Human review and repair | Owner approval |
| --- | --- | --- | --- | --- |
| Cafe praise | 19.536 seconds | Not recorded | Not recorded | Not performed |
| Cafe complaint | 18.157 seconds | Not recorded | Not recorded | Not performed |
| Mixed hotel stay | 19.325 seconds | Not recorded | Not recorded | Not performed |

These are historical Linux CPU evaluation cases, not MSI laptop measurements, paired employee trials or total customer-service task times. The source lacks observed preparation, policy review, repairs, setup, upkeep and ordinary manual-task baselines. An automatic pass is not a quality guarantee. **No time-saving conclusion follows from these three timings.**

## Part 2: A deliberately fictional cafe calculation

These are invented planning assumptions, **not** the three Gemma observations above and not a real cafe:

| Input | Assumed value |
| --- | --- |
| Usual acceptable manual reply, M | 6 minutes each |
| AI preparation and production, A | 2 minutes each |
| Human review and repair, R | 3 minutes each |
| One-time setup, S | 20 minutes |
| Total upkeep during the window, K | 5 minutes |
| Repetitions, N | 10 |

```text
Usual total = N * M = 10 * 6 = 60 minutes
Assisted total = S + K + N * (A + R) = 20 + 5 + 10 * 5 = 75 minutes
Net saved = usual - assisted = -15 minutes (15 extra minutes)
Per-reply difference before overhead = M - A - R = 1 minute
Fixed overhead = S + K = 25 minutes
No net time loss starts at N = 25; positive savings begin at N = 26.
```

**Sensitivity:** If checking takes 4 minutes instead of 3, the per-reply difference becomes 6 - 2 - 4 = 0 minutes. With 25 minutes of fixed overhead, repeating the workflow never recovers that overhead unless the assumptions change.

Even when arithmetic is positive, the comparison is only meaningful if each assisted reply meets the same acceptance standard as the manual one. A human must review the exact saved text, [owner policy and commitments](https://nolankido.com/technology/local-ai-review-replies/#reply-owner-gate). A rejected or unreviewed reply is not an acceptable replacement.

## Part 3: Blank evidence log for an owner-controlled pilot

Do not submit private customer reviews or owner policies to this public website. Keep completed logs locally with anonymous case IDs. Record active effort consistently and note blocked waiting separately so it is not counted twice.

| Field | Your private observation |
| --- | --- |
| Task and acceptance standard defined before testing | |
| Number of matched or comparable tasks | |
| Usual active minutes for each task | |
| AI input preparation and generation minutes for each task | |
| Human source and policy review minutes for each task | |
| Repairs, rejected tries, retry minutes | |
| One-time setup minutes | |
| Total upkeep over the same period | |
| Human assessment of each output | Accepted / Rejected / Unreviewed |
| Matching quality standard reached? | Yes / No / Unknown |
| Staff time not captured, privacy or service costs | |
| Decision and remaining uncertainty | |

For a simple one-off estimate, enter values in the [browser calculator](https://nolankido.com/technology/ai-time-savings/#time-workspace). For several observed cases, use the [free paired AI workflow pilot kit](https://nolankido.com/technology/ai-workflow-pilot/#pilot-kit) with quality labels and offline arithmetic. That pilot is proposed methodology, not a claim that a real business has already saved time using Review Reply Writer.
