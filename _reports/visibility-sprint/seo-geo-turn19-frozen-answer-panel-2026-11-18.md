# SEO/GEO/AEO Sprint Turn 19: frozen 25-question AI-answer audit kit

- **Date:** November 18, 2026 (Hawaii)
- **Property:** https://nolankido.com/
- **Sprint position:** Turn 19 of 25
- **Base checkpoint:** `59c27c2cb41b04fa5e8bf0d3ac0b16348293fbf6` (Turn 18, merged PR #390)
- **Existing canonical retained:** https://nolankido.com/technology/ai-website-visibility/
- **Reader question:** How can I test whether AI answers cite my site across different topics?
- **Scope:** One new direct-answer section in the existing website-evidence case, three original public offline files, Technology and Resources routes, a regression suite, and a private-use measurement protocol. No new canonical page, paid service, automation or GitHub Actions.

## First-party measurement access and editorial decision

The connected GSC Wizard account returned `payment_required` with reason `subscription_required`: its trial has ended and no active plan exists. No subscription was started, no private Google Search Console data was retrieved, and no impression, ranking, click, AI-assistant session or observed citation count is claimed. Official [Google Search documentation](https://support.google.com/webmasters/answer/16984139) describes the dedicated generative AI impression view, and [Bing Webmaster Tools](https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/) describes citations across its covered experiences, but neither provider's authenticated dashboard was accessible from this turn. Provider-wide query metrics remain **unavailable**, not zero. Free owner-exported reports and separate private analytics remain valid future options.

The existing [Turn 04 opportunity map](seo-geo-turn04-query-opportunity-map-2026-11-17.md) already froze a twenty-five-question assistant panel, with **20 nonbranded practical-AI/poker tasks and five branded Nolan Kido questions**, to be repeated later without rewording misses. The website separately exposed an older eight-unbranded-question monthly checker. Without explicitly distinguishing the methods, a future reviewer might compare eight-question and twenty-five-question citation percentages as though they were the same baseline. Turn 19 fixes that research-method gap without inventing observations or rewriting the frozen prompts.

## New reader path and offline tools

The existing page now answers the question at `#ai-answer-sprint-panel`. Its core method is to freeze exact questions, test each in a new search-enabled assistant conversation, inspect actual clickable links manually, and keep branded recognition separate from unbranded discovery. For each prompt, the predetermined expected page is scored separately from a citation to another on-site page; a text-only mention is not a citation. The section also preserves the original eight-question monthly method as a distinct shorter panel.

Three public assets support the broader sprint panel:

1. [`downloads/ai-answer-sprint-25-prompts.csv`](../../downloads/ai-answer-sprint-25-prompts.csv) copies the **exact frozen November 17 prompt file** from `_reports/visibility-sprint/assistant-answer-panel-v1-2026-11-17.csv`. The two files are byte-identical with SHA-256 `b9d29feaaea2d4a593ef3e2d9c86fe04d67f076c1c78d53ac7c7ddbf8f491d74`.
2. [`downloads/ai-answer-sprint-25-blank.csv`](../../downloads/ai-answer-sprint-25-blank.csv) is a header-only observation log. A user keeps completed rows, answers and screenshots privately.
3. [`downloads/ai-answer-sprint-25-audit.py`](../../downloads/ai-answer-sprint-25-audit.py) uses Python's standard library only. It pins the frozen prompt checksum, rejects repeated assistant/mode/prompt observations, unknown IDs, malformed dates, inconsistent labels, inappropriate outcomes on uncompleted trials, unverified claimed URLs, HTTP links and lookalike domains. It calculates segment-specific sampled citation fractions, expected-page versus other-site-page citations and coverage gaps. It cannot perform an assistant query or establish that a human really saw the cited link.

An empty 25-question log with two preselected assistant/search-mode combinations is expected to show 50 planned trials, 50 missing, zero completed and `sample_fraction: null` in each segment. **This is not a measured zero-citation outcome.** Completed answer correctness and task completion are manually assigned labels, not independently judged by the script. The CLI prints aggregate JSON without raw cited URLs. No private responses, query history, credentials, screenshots or site analytics were committed.

The existing Technology hub and Resources link to the deep anchor. The monthly worksheet now explicitly notes that the eight-question monthly method and the 25-question sprint panel must never be pooled. All three new downloads are registered as read-only live-byte targets. The original article publication date, November 3, 2026, remains unchanged; the previously meaningful November 18 revision date is retained.

## Verification observations

| Check | Recorded result |
| --- | --- |
| `python _scripts/build.py` | 253 generated files, three changed outputs |
| `python _scripts/build.py --check` | 253 outputs checked, zero drift |
| `python _scripts/check_search.py` | Pass, 225 sitemap URLs, zero metadata errors |
| `python _tests/check_html5.py` | Pass, 230 HTML pages, zero failures |
| `python _scripts/check_internal_links.py` | Pass, 232 HTML pages, 16,284 internal links, zero issues |
| `_tests/test_turn19_frozen_answer_panel.py` | Seven passed, including frozen-file parity, full and partial branded/nonbranded denominators, spoof and tamper negative controls, blank-log null semantics and legacy checker compatibility |
| `_tests/test_turn15_ai_website_release_answer.py` | Three passed |
| `_tests/test_ai_citation_panel.py` | Fifteen passed on the older monthly kit |

The old `_tests/test_ai_citation_find_discovery.py` and `_tests/test_resources_hands_on_kits.py` retain historical November 14 metadata expectations even though the current base repository dates those pages November 18. The former additionally expects a local Find query result that the unchanged current Find index does not return. These suites failed on stale expectations; no Find index or resource publication date was changed by this turn. The broader `python _scripts/local_release_checks.py` ran to completion with exit code 1: several historical suites depend on old Git objects absent from this shallow checkout, while other suites enforce outdated dates and fixed content snapshots. Its current-source builders, internal-link, search and HTML5 gates passed, but the historical failures mean **the full release checklist did not pass**. Local build, metadata, HTML validity, link and Turn 19 tests are reported independently.

No claim is made about increased rankings, search demand, indexing, traffic, AI model citation frequency or a causal SEO effect. Live deployed-byte parity, if checked after merge, is a separate publication result.

## Suggested Turn 20

Use one priority canonical, likely the About page for the branded identity prompt or the AI answer-checking guide for a nonbranded question, to verify a source-to-answer chain and improve its answer completeness. If genuine Search Console or completed assistant-panel observations become available, use them as a separately dated input rather than tuning the frozen questions to a favorable response.
