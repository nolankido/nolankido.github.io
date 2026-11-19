# SEO/GEO/AEO Sprint Turn 20: Nolan Kido identity answer with source boundaries

- **Date:** November 18, 2026 (Hawaii)
- **Property:** https://nolankido.com/
- **Sprint position:** Turn 20 of 25
- **Base checkpoint:** `8a07f065793ee9b3bff76c98a0a5f00af16e1f9f` (Turn 19, merged PR #391)
- **Canonical retained:** https://nolankido.com/about/
- **Reader questions:** Who is Nolan Kido? What public AI projects has he built or tested? What can a person independently verify?
- **Scope:** Source-bounded answer in the existing ProfilePage, three direct internal entry links, honest metadata freshness and focused tests. No additional canonical profile, new credentials, paid API, GitHub Actions or background automation.

## Why this turn

The existing About page had a strong first-person introduction, evidence cards, public identity markup and multiple links to research, software and poker records. However, a new reader or search assistant had to piece together a brief factual answer across separate sections. The frozen twenty-five-question sprint panel contains **BR01** about Nolan Kido's identity and professional background and **BR02** about inspectable AI projects. Neither question had one compact answer with source-type boundaries on the canonical About page.

The new `#who-is-nolan-kido` section is an answer-first introduction on that **same canonical URL**. It preserves the original introduction, all evidence cards and their existing anchors, as well as the `ProfilePage`'s established `Person` identity `@id` and `sameAs` references. It explains Nolan's practical AI work, 2012 coauthored accounting research and tournament poker interests without blending self-published claims with independent records.

## Sources and the claims they support

| Reader claim | Linked public source | Support and limits |
| --- | --- | --- |
| Review Reply Writer is an inspectable local-AI software case | [Pinned application snapshot](https://github.com/nolankido/reviewReplyWriter/tree/1c5e0487c331d5202410c9f342557d9355951c3a) and [documented case](https://nolankido.com/technology/local-ai-review-replies/) | First-party code and fictional review-reply records; not independent user adoption, client productivity or production safety |
| Preflight has source-linked continuity test outcomes | [Pinned source record](https://github.com/nolankido/canonKeeper/blob/947e9c3d7dbc9bfa719579ca1e697d4479567684/README.md) and [case](https://nolankido.com/technology/ai-book-continuity-checker/) | Archived Sherlock Holmes audit with flags, misses and source limitations; not universal model accuracy |
| Nolan Kido coauthored an accounting research article | [Journal of Accounting Research publisher DOI](https://doi.org/10.1111/j.1475-679X.2012.00447.x), independently checked this turn | The 2012 journal byline, not a current faculty appointment or evidence of AI-product results |
| Nolan reports tournament poker work and creates videos | [Source-linked player profile](https://nolankido.com/poker/nolan-kido/#player-record-title), original event listings there, and [NolanPoker](https://www.youtube.com/@NolanPoker) | Separate independent result listings from self-published accounts; no net-profit inference, official creator-program status or complete results guarantee |

The author may describe his own current projects and interests, but **a public repo, journal paper, or result page independently supports only the relevant bounded claim**. None is a ranking, assistant-citation, conversion or measured client-success signal. The page explicitly warns against turning historical paper affiliation into a present role or gross tournament cashes into profit. No residence, private personal details or unsupported career titles were added.

Home, Projects and the reusable Biography now link natively to `#who-is-nolan-kido`; the original homepage About-evidence link, About section landmarks and Bio fact-check anchor remain. The About meta description answers the named query and retains **AI Works, Human Decides**. Home, About and Bio were meaningfully revised on November 18, 2026; Projects already had that revision date. The `sitemap.xml` uses the existing truthful dates. No duplicate JSON-LD Person object was introduced.

## Local verification observed

| Check | Result |
| --- | --- |
| `python _scripts/build.py` | 253 generated files, six outputs changed from the base checkpoint |
| `python _scripts/build.py --check` | 253 files, zero drift |
| `python _scripts/check_search.py` | Pass, 225 sitemap URLs, zero metadata errors |
| `python _tests/check_html5.py` | Pass, 230 HTML pages, zero failures |
| `python _scripts/check_internal_links.py` | Pass, 232 HTML pages and 16,293 internal links, zero issues |
| `_tests/test_turn20_identity_answer.py` | Four passed, including canonical Person schema, unchanged `sameAs`, original anchors, direct links and negative claim mutations |

Several older identity/biography unit suites have hard-coded November 13 dates, an earlier About description or an older homepage navigation string. Those old assertions now differ from the intentionally revised source. The historical `test_identity_jsonld.py` also expects an older capitalized biography fixture. These suites were inspected but did not all pass; **no full-suite pass is claimed**. The focused Turn 20 source-contract tests plus current static build, metadata, HTML and link checks are distinct and clean. Browser layout tests, authenticated analytics and a fresh citation-panel run were not performed.

## Publication measurement limit

This release can establish that a clearer factual answer and native links were built and served after deployment. It **cannot** show higher rankings, more AI-answer citations, increased impressions, user trust or independent verification of a complete career history. The first-party Search Console connector remained unavailable due to an expired paid trial; no payment or substitute analytics service was initiated.

## Suggested Turn 21

Improve the top nonbranded practical AI query destination, `/technology/check-ai-answers/`, using an actual source-to-claim decision record and a clear answer to the question of when an AI-generated statement is safe to reuse. Keep a separate link to the Turn 19 frozen nonbranded panel, which remains an unrun observation protocol rather than measured visibility.
