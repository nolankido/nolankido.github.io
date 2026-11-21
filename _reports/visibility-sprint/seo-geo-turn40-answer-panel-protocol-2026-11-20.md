# SEO/GEO improvement Turn 40: Frozen assistant-answer panel integrity and first observed pilot

**Date:** November 20, 2026 (Pacific/Honolulu)  
**Website:** https://nolankido.com/  
**Baseline GitHub main:** `31947a86c1f1c82872f9676d439916b8838ba340`  
**Roadmap:** Turn 40 of the 25-turn program (Turns 37 to 61).

## Outcome and honest boundary

This turn attempted to collect an actual answer from a public search-enabled assistant and improved the already frozen 25-question panel measurement tooling. The collected pilot response was **not eligible for the strict 25-question sample**, because the returned browser report did not establish that the exact frozen wording had been submitted. There is **no completed valid frozen-panel trial** recorded for this turn and no measured citation percentage. Do not present a pilot miss as a baseline of 0% or infer what other assistant models would answer.

### Actual public AI answer pilot, separately excluded

- Provider: Perplexity, signed out, fresh public search conversation, standard visible answer mode (not shown as Pro mode).
- Intended frozen question NB01: `How do I verify an AI-written answer before relying on it?`
- The browser agent's output described the submitted question as `How do I verify an AI-written answer before relying it?`, omitting `on`. That leaves exact-question fidelity unconfirmed, regardless of whether the difference arose during submission or reporting.
- The browser agent reported that the AI answer completed and displayed **four clickable source citations**, all to unrelated third-party domains, with **no clickable `nolankido.com` URL or text mention**.
- Interpretation: a genuine, bounded *pilot observation* suggests a citation-visibility challenge for that topic in that specific signed-out context. It is **excluded** from the frozen benchmark. This was not a general Google search result masquerading as an assistant answer, and one answer cannot establish a provider-wide rate or causal SEO outcome.
- The original detailed answer and browser-run evidence were not copied into the public repository. Before a future strict trial can count, exact submitted text and visible citations must be inspected and recorded privately.

### The planned research sample

The frozen November 17 v1 panel remains exactly **20 nonbranded + five branded prompts**. A full predeclared two-assistant/mode design would have **50 planned trials**, one fresh session per prompt and mode. The legacy checker correctly reports `status=no_completed_trials`, `sample_fraction=null` when no eligible observations have been recorded. The signed-out Perplexity pilot is **not** a completed NB01 trial in this denominator. The separate eight-question monthly panel must not be pooled with the frozen 25-question method.

## Concrete code and process improvements

1. Updated `downloads/ai-answer-sprint-25-audit.py` with optional **strict-mode** input files:
   - `--roster`: a predeclared private CSV with exactly the `assistant,mode` header and one to 20 unique assistant/mode combinations.
   - `--submitted-prompts`: a private CSV with `prompt_id,assistant,mode,submitted_prompt` and **one exact submitted question per completed observation**.
   - Both inputs must be supplied together for strict mode. The existing CLI without these flags remains backwards compatible.
2. Strict checks reject post-hoc assistant/mode substitutions, inconsistent case or spelling, duplicate roster entries, unexpectedly missing evidence rows, duplicated or noncompleted evidence, and prompt texts that differ by even one word from the frozen file. An identical copied string can be compared, but the checker cannot independently authenticate an assistant UI: retain screenshots/conversation links privately.
3. Added **per-mode coverage** in output only when the roster exists. All modes retain 25 planned trials, their actually recorded rows, completed counts, missing rows and verified links. Missing modes are not silently converted to zero citations.
4. Added `roster_predeclared` and `submitted_prompt_text_checked` indicators to the aggregate JSON. The legacy observer-only method keeps working, but now makes explicit when those stronger checks were not supplied.
5. Added header-only public templates:
   - `downloads/ai-answer-sprint-25-roster-blank.csv`
   - `downloads/ai-answer-sprint-25-submitted-prompts-blank.csv`
   Fill copies **outside the public repository**. Predeclare the roster before asking questions; copy the actually submitted text from an inspected session, not from the expected question file after the fact.
6. Added **14 offline regression cases** in `_tests/test_turn40_frozen_observation_integrity.py`; integrated them in `_scripts/local_release_checks.py`, registered new public downloads as fixed byte-exact targets in `_scripts/check_live.py`, and documented the protocol in `AGENTS.md` and `README.md`.
7. The original frozen prompt CSV and original header-only observation CSV were **not changed**. The existing frozen-panel SHA-256 remains `b9d29feaaea2d4a593ef3e2d9c86fe04d67f076c1c78d53ac7c7ddbf8f491d74`.

### Standard-library-only strict audit command

Store completed observations, modes, submitted prompt evidence and all response links/screenshots **only in an owner-private directory**, outside this public GitHub repository.

```powershell
py -3 downloads/ai-answer-sprint-25-audit.py --month 2026-11 --expected-modes 2 --prompts downloads/ai-answer-sprint-25-prompts.csv --csv "$env:USERPROFILE\Documents\ai-audit-private\observations.csv" --roster "$env:USERPROFILE\Documents\ai-audit-private\modes.csv" --submitted-prompts "$env:USERPROFILE\Documents\ai-audit-private\submitted-prompts.csv"
```

The original observation CSV headers remain:
`date,prompt_id,assistant,mode,status,clickable_link_verified,linked_url,text_only_mention,answer_correctness,task_completed`.

For `completed` observations, manually check actual clickable citations and the destination host. The strict text evidence CSV only checks that the **submitted** question equals the frozen wording. It does not establish the cited link exists, actually appeared in the assistant answer, or was clicked. Each incomplete or blocked question must have an observation status of `incomplete` with outcome fields blank, and **no submitted-prompt evidence row** unless completed. Store raw response histories privately.

## Validation and limits

| Item | Observed status |
| --- | --- |
| Frozen public prompt and repository original | Both still tracked as the original identical blobs, not edited |
| Genuine Perplexity answer | Observed, but exact question uncertain; excluded pilot |
| Valid frozen v1 completions | **0 recorded; citation rate unknown, not 0%** |
| New Python strict-mode source and regression tests | Committed to GitHub candidate branch; source/diff inspected |
| New 14 regression tests | Added; **not run against a complete checkout** in this connector environment |
| Original Turn 19 regression compatibility | Legacy CLI and `summarize` signatures retained; full original suite not run |
| Full deterministic builder, HTML5 and browser tests | Not run, complete repo checkout unavailable |
| New public downloads served from custom domain | Release inventory updated, but live byte-parity not confirmed |
| Search Console, Bing and Umami visibility | Separately unmeasured as in Turn 39 |

### Remaining work and handoff

This turn improved the measurement process and attempted the first real provider probe, but **did not complete the planned 50-trial, two-mode baseline**. Do not treat a tooling release as a finished visibility study. With a provider interface that permits consistent, correctly copied fresh prompts, run the predeclared roster, score all completed observations and protect the underlying raw answers. If the original question is not confirmed exact, exclude that trial and rerun it without rewriting the frozen CSV.

**Next roadmap turn:** Turn 41, prioritize search and topic opportunities from the verified available evidence, separating published technical assets from still-unavailable traffic and incomplete AI answer observations.

No GitHub Actions, background schedules, paid subscription, crawler bypass engineering, private answer logs, or API keys were added. No new content or canonical URL was published as part of this measurement-tooling turn.
