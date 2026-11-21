# SEO/GEO Turn 50: practical AI first-screen identity and proof links

**Review date:** November 20, 2026 (Pacific/Honolulu)  
**Base main:** `d4d0942cc93d44a1895a25d26f13cd7899f53698`  
**Roadmap:** Turn 50 of 37 to 61  
**Scope:** Home and About's first introductory navigation, plus offline guardrails and report.

## Observed reader problem

A read-only browser audit inspected the public homepage and About page at desktop 1366 × 768 and mobile 375 × 812. It reported the primary identity tagline and introductory text clearly visible, with no evident horizontal overflow or broken checked fragments. The Home hero nevertheless presented six actions including links to categories already available in the site's top navigation. At 375 px the actions stack and consume additional first-screen scrolling. About's first paragraph introduced practical AI, business operations and accounting research but offered no adjacent, direct proof action. The page's original project records appeared later.

The same current `main` source contains the six-link Home hero, first-person About intro and separate, source-bounded AI, research and poker proof sections. This turn does not invent a usability conversion rate, repeat a biographies rewrite, or create a new search landing page.

## Bounded improvement

1. **Home:** Replace six hero links with three: one prominent link to the real historical AI-assisted website defect and correction, one secondary link to a free local browser AI task-brief tool, and the existing `#home-proof-title` link to three different kinds of evidence. Other personal interests remain in the global section menu and lower-page evidence. The separate tested mobile route to `#selected-reading-title` remains.
2. **About:** Immediately after the existing 51-word intro, add one clearly named, native `nav.link-row.about-first-proof` with a primary link to the recorded website repair and a secondary link to `/projects/#projects-checks`. The original `#who-is-nolan-kido` answer, `#about-evidence-title`, source citations, 2012 publication, NolanPoker distinction and existing About jump list stay in place.
3. **Access and semantics:** Reuse shared `.button`, `.text-link` and wrapping `.link-row` styling, including the already defined 44 px minimum link height. No new stylesheet, script, display-only mock button, modal, tracking, schema, or sitemap URL.

The recorded website repair is evidence that a real markup defect was identified and corrected before release, not an assurance that every AI-coded release is error-free. The task brief is a local browser utility; it does not secretly call an AI model. The About project evidence includes distinct simulated and real tests and is not a claim of production adoption.

## Changed and unchanged files

Source plus corresponding committed output:
- `_source/home.html`, `index.html`
- `_source/about.html`, `about/index.html`

Added `_tests/test_turn50_first_screen_identity.py`, registered in `_scripts/local_release_checks.py` and documented in `README.md` and `AGENTS.md`.

Not changed: the site-wide `_source/site.json` identity phrases; Person structured identity and external `sameAs`; canonical Home and About metadata; `_source/pages.json` dates; all underlying project/research/poker records; Books catalog and exercise links; `sitemap.xml`; privacy/analytics behavior.

## Tests and evidence boundaries

Before the PR, the connected GitHub repository confirmed:
- Exact one-to-one replacements in source and committed generated HTML.
- One Home `#home-proof-title` link and matching section ID, plus retained mobile free-tool fragment.
- The About proof navigation follows its intro and precedes the existing identity section.
- The `/projects/` page has a unique `#projects-checks` target and the AI repair case has an actual published page.
- Canonical H1 and Person structured identity survived in the changed public copies.

These are static source and output checks, not a complete regenerated build or live screenshot of the **new** design. The site browser audit was conducted before the changes. The container's outbound DNS for the full Git checkout is blocked, so unless separately observed, mark `_scripts/build.py --check`, the full local unit suite, HTML5, Playwright at 320/375 px and production byte parity as **not run**. Merge does not by itself prove the public site reflects the commit. Search Console clicks/impressions, Bing citations, AI answer citations and actual visitor task success are unmeasured.

### Full local verification commands
```powershell
py -3 _scripts/build.py --check
py -3 -m unittest discover -s _tests -p test_turn50_first_screen_identity.py -v
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only / --only /about/ --attempts 3 --interval 5
```

## Next

**Turn 51:** Map canonical topic ownership and remove proven duplicate entry explanations only where the contents actually overlap. Preserve old URLs and existing authority evidence; don't mass-delete pages or manufacture GEO-specific schema.
