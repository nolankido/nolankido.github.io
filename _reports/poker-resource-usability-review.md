# Poker resource directory: usability and source-context review

Prepared October 7, 2026, Pacific time. This is an implementation audit, not a deployment receipt. Release status belongs to the pull request and its exact-commit checks.

## Decision

Improve selection and navigation before adding more links. The directory already has enough breadth to overwhelm a new reader. A larger total would not solve the immediate problem: finding the right kind of resource, at an appropriate level, with its access requirements and limitations visible before leaving the site.

Preserve the 108 published records, their IDs, destinations, descriptions, access classifications, and review dates. Do not refresh review dates just because the presentation changed. Keep the 24 local guides distinct from external resources. No publisher ranking, affiliate program, software endorsement, or claim of internet-wide superiority was added.

## What was inspected

The verified repository baseline is `b537c507e3135cca40874c65177d18e13b7fa6e4`, tree `384a495af4645519073c6e2ddc6d1bfb850b23e1`.

The structural inventory covers all 30 generated Poker HTML pages and every external anchor in their main content. It found 116 distinct literal destinations: the directory's 108 records and eight additional contextual references in local guides. Repeated citations do not count as new resources.

The catalogue has 13 topics, 42 detailed resource kinds, and five audience labels. Access is 91 Free, seven Mixed, and ten Paid. Audience labels are 22 Beginner, 32 Intermediate, ten Advanced, 11 Technical, and 33 All levels. Labels are editorial descriptions, not certifications of difficulty or accessibility.

All 108 records were inspected structurally for category, audience, kind, access, destination identity, duplication, notes and rendering. Public page text or abstracts were opened for 20 selected catalogue destinations spanning all 13 topics, plus the eight references outside the directory. Those 28 reads are not a fresh HTTP availability audit of all 116 URLs. Web retrieval can use cached page text. No paid course was purchased, video fully watched, software installed, calculator accuracy certified, dataset downloaded, paper replicated, or linked PDF audited.

Direct navigation from the local execution environment was blocked. Local interactive previews therefore used in-memory HTML with local styles and scripts, without provider requests. The existing GitHub Actions suite performs the separate HTTP browser and deployment checks. No workflow or permission changes were made for this release.

## Main findings and repairs

### 1. Topic and price were not enough

A beginner could search a topic and still face an undifferentiated mixture of courses, technical papers, software and documentation. Detailed kind labels existed on cards, but were not usable filters.

The finder now combines text, topic, Free-only, resource type and experience. Forty-two detailed kinds map to seven explicit discovery groups. The detailed kind remains on each card, so a broad filter does not replace the more precise description. Unknown new kinds fail the build until their mapping is reviewed.

Selecting an experience level also includes resources explicitly marked All levels. This behavior is explained beside the control. It is not an inferred claim that every advanced source is suitable for beginners. Topic counts update with the other filters, and the active-filter summary makes an empty result understandable.

### 2. The page needed a fast route to a useful subset

Six visible starting choices replace conflicting filters and move keyboard focus to the result heading: free basics, tournament study, creator/video/audio material, study tools, official events, and Omaha/mixed games. Typing does not move focus; pressing Enter in search opens the matches. Reset returns focus to the search field.

The existing six curated reading paths remain available separately. Their links resolve to the actual records, rather than duplicating titles and access labels in another catalogue. The beginner path now uses hold'em rules, hand rankings and Pokerology's lesson library instead of the intermediate historical MIT course. Cash-game and Omaha links are explicitly separate starting points, not one transferable strategy.

### 3. Card hierarchy obscured the decision

Publisher identity and destination domain now appear first. The title opens the external source. Detailed format, Free/Mixed/Paid and experience appear before the description. Notes are visibly labeled "Before you use it" and remain present in both the card and compact list views. The review date and review-method explanation are retained.

Each record has a native "Link to listing" anchor with a descriptive accessible label. It is a bookmarkable link to the site's explanation and limitations, not a tracking redirect or a second external listing. Native anchors preserve browser history, reveal filtered-out targets, and focus the destination when activated. Malformed or unrelated fragments are ignored safely.

### 4. Simplification must not erase caveats

The old page already contained important editorial work. It would be a regression to remove it merely to make the cards shorter. The compact view changes the layout, not the underlying evidence or cautions.

Examples preserved include the heads-up/restricted-action scope of the HoldemResources chart; the difference between free PioSOLVER documentation and product licensing; historical dates on creator essays and rulebook archives; the distinction between interface inspection and verified calculator accuracy; and the distinction between a preprint abstract and a replicated finding.

The PokerBank archive states that it is no longer updated. The Home Poker Tourney rulebook page links 2013 TDA rules. These are useful only with their historical context. A recent review date does not make their underlying content recent.

### 5. Official, secondary and community sources need different expectations

Every topic now has a short explanation of when to use it and what not to assume. Event pages point readers toward the organizer's current structure and terms. Results and room directories are distinguished from event authority and net-profit records. Forum interpretations are not presented as binding floor rulings. Research and development material is separated from tested commercial products.

The unusual percent-encoded Jaman Burton article URL was opened successfully. It was not "cleaned up" into an unverified destination. A strange-looking URL is a reason to inspect, not evidence that a link is broken.

### 6. Filtering must not become a barrier

All 108 cards and native topic links remain in the HTML. Controls start hidden and appear only after initialization. A blocked script or disabled JavaScript leaves the full directory readable. The topic index remains available without script.

Support shortcuts stay outside filtered groups, including when no results match. The US and GamCare links retain their regional context and are not framed as performance coaching. Printing shows the complete directory, retains limitations, and prints external destination URLs; returning from print restores the active filters.

### 7. Preserve the rest of the site

The change adds one resource-only stylesheet and updates the existing resource script, renderer and source page. Shared styles, primary navigation, the Technology-first homepage, local guide content, contact implementation and pageview-only analytics are unchanged. No remote thumbnails, video embeds, saved searches, custom tracking events, accounts or backend services were introduced.

A prominent Resources entry in the shared Poker navigation is a separate remaining discoverability improvement. This release retains the existing links from the Poker overview, library and study desk rather than silently changing navigation across every Poker page.

## Topic-by-topic assessment

| Topic | Records | Main reader need and review priority |
| --- | ---: | --- |
| Learn the basics | 6 | Prioritize rules, rankings and introductory lessons. Keep historical collections contextual. |
| Rules and procedures | 5 | Prefer the actual organizer's rules and staff ruling over general explainers or archived rules. |
| Strategy libraries and books | 8 | Explain what question a library answers. Keep free articles separate from paid memberships. |
| Poker math and ranges | 6 | Make inputs and assumptions explicit. Call-price arithmetic alone is not a universal strategy verdict. |
| Tournament study and ICM | 10 | Distinguish regular events, satellites, bounties and heads-up models. Do not transfer restricted charts to six-player play. |
| Study tools and documentation | 12 | Identify manuals versus products. Do not imply the software was installed or validated. |
| Official events and schedules | 9 | Favor original schedules and structure sheets. Recheck before travel or registration. |
| Results and reporting | 6 | Distinguish organizers, journalists and secondary directories. Cashes are not net profit. |
| Watch and listen | 13 | Separate actual video, audio and written creator context. Playback, transcripts and captions remain unverified. |
| Communities and home games | 6 | Preserve the difference between rules, forum advice, historical material and home-game planning. |
| Omaha and other variants | 12 | Read the exact game's rules before studying ranges or comparing hand selection. |
| Research and development | 11 | Label documentation, papers, preprints, code and datasets accurately. No replication is implied. |
| Mental game and support | 4 | Separate performance material from gambling-harm support and explain regional coverage. |

## Selected catalogue destination reads

These are short review findings, not copied articles or endorsements. The URLs are the original published destinations.

| Destination | Read basis and material distinction |
| --- | --- |
| https://www.pokertda.com/view-poker-tda-rules/ | Official 2026 rules page. Current rules belong apart from old rulebook archives. |
| https://www.pokerstarslive.com/poker/rules/ | Operator-specific rules and responsibilities, not universal filming or software permission. |
| https://www.pokerology.com/lessons/ | Public lesson index. A beginner route into material, not a completed-course review. |
| https://upswingpoker.com/pot-odds-step-by-step/ | Call-price arithmetic and worked examples. Ranges, future betting and equity realization still matter. |
| https://blog.gtowizard.com/icm-basics/ | Public model explanation with assumptions and limitations. |
| https://www.holdemresources.net/hune | Heads-up, restricted-action charts, not six-player tournament solutions. |
| https://piosolver.com/docs/ | Public quick-start documentation. Licensing and actual program behavior remain separate. |
| https://www.wsop.com/schedule/ | Organizer schedule landing page. Individual dates and terms need a current event check. |
| https://www.thehendonmob.com/ | Results database entry point. Recorded cashes alone do not establish profit. |
| https://www.pokeratlas.com/las-vegas-nevada | Secondary room and tournament directory. Confirm details with the room. |
| https://www.thepokerbank.com/videos/ | Public video archive explicitly marked no longer updated. Playback not tested. |
| https://jonathanlittlepoker.com/wph-428-how-to-destroy-recreational-poker-players-ft-jaman-burton%EF%BF%BC/ | Historical written/video-linked hand analysis. Exact encoded URL retained after reading it. |
| https://www.homepokertourney.org/poker-rule-book.htm | Historical rulebook landing page including 2013 TDA material and many commercial links. PDFs not reviewed. |
| https://www.pagat.com/poker/rules/betting.html | General betting and home-game conventions, not venue authority. |
| https://plomastermind.com/blog/ | Public Omaha blog distinct from paid training and solver products. |
| https://www.pokerstars.com/poker/games/omaha/ | Rules for the specific game, including hole-card selection requirements. |
| https://phh.readthedocs.io/en/stable/ | Public hand-history specification, not parser execution or dataset validation. |
| https://arxiv.org/abs/2608.06362 | AV-AIVAT preprint abstract and submission information only. No replicated performance claim. |
| https://www.ncpgambling.org/help-treatment/ | Public US gambling-harm help page. No treatment or clinical assessment. |
| https://www.gamcare.org.uk/get-support/ | Public regional support routes, distinct from poker-performance training. |

## Contextual references outside the directory

All eight were opened as public page text. They remain with their relevant guides rather than being added solely to inflate the directory count. The literal destination inventory and in-page occurrences are available in the accompanying audit JSON.

| Source | Main use in the local guides |
| --- | --- |
| https://www.playwsop.com/poker-hands/ | Hand rankings and glossary reference. |
| https://www.pokerstars.com/help/articles/trn-knockout/ | Operator-specific knockout tournament explanation. |
| https://www.pokerstars.com/poker/games/rules/hand-rankings/full-house/ | Full-house ranking context. |
| https://www.pokerstars.com/poker/learn/lesson/position/ | Position and action-order reading. |
| https://www.pokerstars.com/poker/learn/lesson/pot-odds/ | Pot-odds workshop and decision-lab reference. |
| https://www.pokerstars.com/poker/learn/lesson/the-flop-and-your-hand/ | Board-reading context. |
| https://www.pokerstars.com/poker/learn/strategies/combinatorics-an-introduction-to-the-study-of-card-combinations/ | Card combinations and range reading. |
| https://www.pokerstars.com/poker/learn/strategies/how-to-think-about-hand-ranges-in-poker/ | Introductory range-thinking reference. |

## Maintenance and acceptance criteria

Continue using `_source/poker/resources.json` as the single published catalogue. New records need a concrete reader question, an inspected original destination, accurate access and audience labels, a concise limitation, and an explicit type mapping. Broad libraries and individual articles may coexist when they answer different needs; aliases and repeated citations are not additions.

Keep the existing manual review queue and its shorter intervals for schedules, products and rules. Reports of changed domains, unexpected redirects, new paywalls or misleading claims take priority. A successful HTTP response is not sufficient evidence to refresh a review date. No continuous monitor or automatic publication was enabled.

Next editorial priorities are stronger creator playlists with verified playback and captions or transcripts; game-specific study paths for four-card PLO versus split-pot and draw games; more geographically diverse organizer sources; and a shared-nav Resources link tested across the Poker pages. These are coverage and navigation tasks, not a quota to reach an arbitrary link total.

## Verification at preparation

The deterministic build checked 50 generated outputs. All 147 Python tests passed. A Chromium in-memory interaction run passed 80 combinations of resource type, experience and Free-only, with expected counts derived from the catalogue. It also exercised the six quick choices, keyboard result focus, compact-view caveats, print restoration and support links in empty states. Five widths, 320 through 1440 CSS pixels, were checked for overflow, including expanded text spacing. No script exceptions were reported.

The repository browser test was extended for the new controls, bookmark focus, browser back/forward, collapsed topic-index recovery and no-JavaScript behavior. These navigation tests require the existing HTTP-based CI environment. The new CSS asset is included in the published-file verifier. This document does not predeclare their outcome or claim deployment.
