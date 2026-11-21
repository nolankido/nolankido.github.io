# SEO/GEO Turn 60: restore the missing Bayesian range-update equation

**Review date:** November 20, 2026 (Pacific/Honolulu)
**Starting main:** 774ae49331f31051299ba1de738d024e68af5b85
**Canonical:** https://nolankido.com/poker/poker-under-uncertainty/#bayes-range-update-formula
**Existing reproducible source:** https://nolankido.com/downloads/poker-under-uncertainty-reproduce.py
**Fixed public evidence:** downloads/poker-under-uncertainty-evidence.json

## The actual content defect

The long-form Poker Under Uncertainty research essay explains Bayes' theorem, prints original class priors and conditional betting likelihoods, calculates three resulting posterior fractions, and shows an accompanying graphic. But just after the worked example it explicitly says "The range-update process can be represented as:" and then skips directly to "The deeper lesson is that a blocker ...". The promised update expression was absent. That is a continuity and teaching defect, not an incorrect result in the underlying example.

The article is an advanced research essay, and a reader should be able to identify precisely where card removal enters the posterior instead of inferring the missing equation. Repairing this single existing section is more useful than another generic introduction to ranges or another SEO-only landing page.

## Reproduced model from the public evidence

The original hypothetical three classes are value, draw and bluff/air. Existing post-card-removal priors are:

- Value: 3/10
- Draw: 9/20
- Air: 1/4

The explicitly assumed betting action likelihoods are 4/5, 3/5 and 1/5 respectively. Multiply likelihood by prior before normalizing:

| Class | Post-card-removal prior | Model P(bet given class) | Unnormalized mass | Posterior |
| --- | ---: | ---: | ---: | ---: |
| Value | 3/10 | 4/5 | 6/25 = 0.24 | 3/7, about 42.86% |
| Draw | 9/20 | 3/5 | 27/100 = 0.27 | 27/56, about 48.21% |
| Air | 1/4 | 1/5 | 1/20 = 0.05 | 5/56, about 8.93% |

The total weighted mass is 14/25 = 0.56, and the three exact posteriors sum to 1. Those are the preexisting numbers in the essay and its published reproducible evidence. No new empirical hand or player behavior was supplied. The correction makes the denominator explicit for card-filtered prior weights, and labels likelihoods as assumed rather than observed.

The general expression is posterior_i = prior_i(K) × likelihood_i(K) / sum_j [prior_j(K) × likelihood_j(K)]. K represents known cards. Impossible holdings are removed first, with zero feasible prior mass; the model sums only remaining possible classes. The artificial blocker negative control uses feasible combination counts (3,4,0) and the above likelihoods, giving posterior (1/2,1/2,0). A card removal is a change to a range prior and to its normalization, not evidence of the opponent's betting policy.

## Scope of changes

1. On the existing source and compiled research essay, inserted one named accessible formula paragraph #bayes-range-update-formula immediately after the formerly dangling "as:" sentence and a second independently reconciled example paragraph #bayes-range-update-check. Linked the original already-published offline reproduction. Did not introduce a new hypothetical solver range, chart, iframe, table, image or independent page.
2. Preserved exactly 190 existing native MathML expressions in the original article, all 11 tables and 3 uncertainty images. The extra text remains within the original 50-minute reading estimate, avoiding unrelated generated Poker Library or topic-label drift.
3. Preserved the October 14, 2026 original publication date, added a meaningful November 20, 2026 revision to the manifest, canonical public Article metadata, visible reader label and sitemap lastmod.
4. Added standard-library _tests/test_turn60_bayes_update.py: reads the existing public evidence JSON, independently recomputes rational posteriors and a synthetic blocked-hand control, verifies unique published anchors and source/output paragraph parity, the 190-math original structure, dates and negative mutations. Registered in local release suite.
5. Restricted the historical predecessor regression's *historical inventory comparison only* to the predecessor state, excluding this subsequently modified current article. The old tests' explicit mutation rejection, 190 MathML content check, real data reproducibility, old image/table and safety checks remain intact.
6. Updated README and AGENTS with scope and the original provenance. No user-authored GitHub Actions, paid API, account data, real hand evaluation or new canonical route.

## Verification and limits

The preflight independently computed exact priors, likelihoods, weighted masses and posteriors from public evidence, verified new source and compiled HTML paragraphs have the same text and stable unique anchors, checked the original publication and updated revision dates, and confirmed original MathML count and 50-minute estimate. A normal complete local generator build, historic unit suite, HTML5 parser, browser navigation, and postmerge public publication must be run separately before those gates can be called passed.

This static content repair does not measure or establish search rankings, generative AI citations, reader comprehension, poker win rate or opponent tendencies.

### Full-checkout verification

~~~powershell
py -3 -m unittest discover -s _tests -p test_turn60_bayes_update.py -v
py -3 -m unittest discover -s _tests -p test_uncertainty.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /poker/poker-under-uncertainty/ --only /sitemap.xml --attempts 3 --interval 5
~~~

## Next

Turn 61: audit a different existing poker range or tournament practice exercise for an exact mismatch between its listed assumptions and answer key. Prefer one measurable repair over multiplying overlapping pages.
