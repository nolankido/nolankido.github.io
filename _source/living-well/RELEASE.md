# Living Well initial release

Editorial date: October 8, 2026.

## Scope

Living Well is a major section at `/living-well/`, second after Technology in the main navigation and homepage. Poker and Creative Work remain their own destinations. The shared footer, Notes, Technology, and Resources lead readers into the section without moving or replacing existing articles.

The release contains 33 new pages: nine supporting hubs, five subject pages, nine essays, seven practical guides, and three proposed experiment protocols. The nineteen long-form entries contain approximately 10,500 words of original editorial material. Five blank Markdown worksheets and a dedicated RSS feed are generated from the same source. The sixteen essays and guides appear in the feed; proposed experiments do not masquerade as completed reports.

Subject areas are Meaning & spirituality, Attention & presence, AI for everyday life, Relationships & care, and Choices & growth. Reader routes are Ideas, Guides, and Field notes, with Topics and Worksheets available in the section navigation. The supporting pages include editorial standards, annotated primary sources, and a usable conversation guide rather than a fabricated interview.

## Reader and editorial boundaries

Every long-form entry includes a clear title, description, reading-time estimate, publication date, keyboard-accessible outline, substantial sections, an optional private exercise, one closing question, and two relevant next reads. Publication and revision metadata have separate fields. Source catalogs must declare publication dates; revisions cannot precede publication and revision notes require update dates.

No personal experiment results, memories, interviews, spiritual experiences, or testimonials have been invented. The field-note hub explicitly says that no completed personal field notes have been published. AI assistance is disclosed. Hypothetical examples remain hypothetical. Research claims are distinguished from editorial interpretation; linked NIST, Oral History Association, and Library of Congress sources support limited identifiable guidance rather than validating the optional practices.

Worksheet responses are not collected. There are no new forms, application accounts, JavaScript files, trackers, or third-party services. Existing pageview analytics and the existing contact flow remain in place. Guidance retains a no-AI route, data-minimization advice, essential-access protections, and clear limits on professional or spiritual authority.

## Implementation and preservation

`_scripts/living_well.py` validates and renders the catalogs, manifest, article metadata, navigation, RSS, and worksheet exports. `_source/living-well/launch.json` and `further.json` are the editable article sources. `assets/living-well.css` provides section-scoped styling using the site's existing type and color tokens. The small reviewed `assets/hubs.css` addition supports the fourth homepage destination and six-item mobile navigation.

`build.public_pages()` includes all Living Well routes, so link checks, sitemap generation, and exact-byte live verification cover the new section. The live checker also covers the new stylesheet, feed, and all five downloads. Stale generated Living Well HTML is rejected in the same manner as stale Poker pages.

The original `styles.css`, `assets/site.css`, `assets/contact.js`, original Poker article source, original Poker catalog, original Notes feed, and site configuration retain their independent protected hashes. Reviewed gateway/shared-navigation baselines were updated deliberately, not removed. Existing permanent CI permissions remain read-only, with all earlier suites retained. Temporary integration scripts and the temporary branch build workflow are removed before merge.

## Completed pre-merge verification

Isolated source commit: `f55505d74360f594119158e6a4b555693a1cc204`.

GitHub Actions verification run: `37896870022`.

- Reproducible build check: 132 generated outputs checked with zero changes.
- Full automated test suite: 216 tests passed, including seven Living Well tests.
- Living Well browser suite: all 33 pages passed at 320, 390, 620, 768, 1024, and 1440 CSS pixels.
- axe-core 4.10.3 WCAG A/AA scans: no violations reported by the configured scans.
- Keyboard reader route, article outline, exact download bytes for all five worksheets, worksheet print visibility, and no-JavaScript navigation/downloads passed.
- Browser report: no JavaScript errors, failed local responses, write requests, local/session storage entries, or cookies under the offline test configuration. External services were blocked during these tests.
- Desktop and mobile screenshots were inspected. Automated checks do not constitute a guarantee of accessibility in every browser or assistive technology.

The final pull request must also pass the repository's retained whole-site browser and accessibility suites. Deployment confirmation is separate: the main-branch release workflow checks actual published bytes and records `LIVE_VERIFIED_COMMIT` only after that check passes.

## Next content that requires real participation

Publish firsthand field notes only after an experiment has actually been completed and reviewed. Add personal essays or conversations only from genuine supplied experiences and with appropriate permission. The launch material is usable without those later contributions; there are no empty promised interviews or invented findings to fill the gap.

## Narrow-screen text-spacing correction

The retained whole-site audit caught overflow in the shared closing heading on all five topic pages at 320 CSS pixels with user-defined text spacing. The heading was shortened, Living Well section and article headings gained safe wrapping, and the dedicated browser regression now applies text-spacing overrides at every tested width rather than only 390 pixels. All existing accessibility and whole-site regression gates remain required.
