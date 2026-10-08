# Growing the Poker resource directory

Owner request: build broad, useful coverage of poker information across the internet.
Started October 7, 2026. This is a working editorial process, not an automatic publishing schedule.

## Purpose and boundaries

Use `/poker/resources/` for external destinations. Keep `/poker/library/` for the site's own explanations and `/poker/` for Nolan's work and the principal entry points. External-resource research does not require an autobiographical approval packet. This broader directory is a new owner-requested workstream, separate from the earlier six-piece personal-content slate.

Aim for comprehensive useful coverage, not a raw link quota. Start with original sources and specific reader questions. Include different formats, levels, variants, and viewpoints when they add something. A second article about the same topic can earn a place when its treatment is meaningfully different; a second URL to the same material cannot.

The initial release contains 62 listings in 13 categories. Public page text or the public catalogue was read for 61 destinations; the Poker TDA entry is explicitly marked as search-index-only because direct page reading was unavailable. A page read is not a full review of every article, a completed course, a tested software product, a watched video, or a guarantee of availability in every region.

## The working loop

1. Discover candidates for a specific topic or uncovered reader question.
2. Inspect the original destination and its actual public content. Record limits rather than inferring them away.
3. Classify access, audience, format, and purpose; normalize the URL and remove duplicates.
4. Write a short original description and a useful caveat where needed.
5. Release a small, checked batch with source and generated output together.
6. Revisit dated listings, resolve reported changes, and retire links that no longer serve the stated purpose.

Candidates do not automatically enter the published catalogue. An HTTP response, search result, vendor claim, or existing backlink is evidence to inspect, not sufficient editorial approval by itself. No accounts, purchases, downloads, contact messages, or social posts are prerequisites to the basic research pass.

## Discovery map

| Category | Questions to cover next | Preferred discovery sources | Manual review interval |
| --- | --- | --- | --- |
| Basics | Action order, betting conventions, hand reading, beginner vocabulary | Original rules explanations and structured teaching libraries | 90 days |
| Rules | Full raises, reopening, all-ins, showdown, etiquette, devices | Rule-making bodies and event operators, with version and scope checked | 30 days |
| Strategy | Cash versus tournaments, preflop, postflop, exploitative versus equilibrium models | Signed instructional articles, original books, training-library descriptions | 60 days |
| Math | Pot odds, equity, combinations, ranges, EV, assumptions | Worked explanations that identify the modeled situation | 90 days |
| Tournament study | Short stacks, ICM, satellites, PKO and mystery-bounty incentives | Specialist articles and documented tools, not universal charts | 60 days |
| Tools | Capabilities, inputs, documentation, limits, access | Official product pages and help centres | 30 days |
| Events | Structure sheets, schedules, official event information | Organizer schedules; link to the source rather than recopying dates | 14 days |
| Results | Reporting, hand histories, results databases, rankings | Original reporters and database publishers | 30 days |
| Watch and listen | Strategy shows, interviews, vlogs, broadcast libraries | Publisher or creator-controlled pages that establish the real channel | 30 days |
| Community | Hand discussion, rules discussion, home-game organization | Public forums with clear topical scope and moderation context | 30 days |
| Variants | PLO, Omaha hi-lo, stud, razz, draw and mixed games | Rules sources and specialist teaching material | 90 days |
| Research | Imperfect-information games, CFR, evaluation, poker libraries | Paper landing pages, author pages, maintained documentation | 90 days |
| Mental game and support | Process, tilt, variance, help resources | Original author material and established support organizations | 30 days |

These intervals generate proposed work priorities only. No checks run merely because a due date has arrived. An urgent reader report or suspicious redirect takes precedence over the interval. A current schedule is always checked again before it is used for travel or an event decision.

Useful query patterns include `site:<publisher> <specific concept>`, `<variant> rules official`, `<tool> documentation <feature>`, `<series> official schedule structure`, and `<paper title> author`. Search broadly before selecting a provider; do not let the seed catalogue become the only source of future links.

## Review each candidate

Check the canonical domain, page title, publisher or author, actual subject, reader benefit, publication or revision context when supplied, and the access required to use the linked material. Prefer a deep link to the useful explanation over a homepage when that explanation is the reason to include it.

Describe what was actually inspected. A free public help page for paid software is classified Free, while the software product is Paid or Mixed. Do not classify a trial as permanently free. Leave prices out unless a separate task requires them and verifies them at the time. Mention account or regional limitations when observed; do not invent restrictions.

For software, describe documented capabilities without certifying accuracy, profitability, platform permission, security, or compatibility. A study tool is not an invitation to use it during a live hand. For charts, identify the game and action assumptions. For records, do not equate reported winnings with net profit. For papers, distinguish an abstract or documentation review from reading the full paper or reproducing the result.

Use `review_method: "page"` only after reading the destination's public text or catalogue. An exceptional `"index"` listing must be an identifiable original source, carry a visible limitation in `notes`, and enter the direct-review queue immediately. Do not accumulate a large published list of unread search results. Prefer holding unverified candidates instead.

Do not include pirated books, scraped course mirrors, cheating services, real-time assistance marketed for prohibited play, deposit-bonus funnels, impersonated domains, or links requiring credentials to inspect their basic identity. Keep gambling promotions separate from informational usefulness. Forum posts are discussion, not authoritative rules. A changed domain is a review trigger, not proof of misconduct.

## Catalogue and editorial metadata

The single published source is `_source/poker/resources.json`. Every entry has exactly:

| Field | Meaning |
| --- | --- |
| `id` | Stable lower-case hyphenated identifier; retained when a link is corrected |
| `title` | Descriptive label, up to 140 characters |
| `url` | Direct public HTTPS URL, without referral or tracking parameters |
| `publisher` | Who controls or publishes the destination |
| `category` | One of the 13 category keys in `_scripts/poker_resources.py` |
| `kind` | Article, documentation, tool, book, forum, schedule, research, or another accurate short label |
| `access` | `Free`, `Mixed`, or `Paid`, describing the linked resource |
| `level` | `Beginner`, `Intermediate`, `Advanced`, `Technical`, or `All levels` |
| `description` | Original summary of the specific benefit, up to 400 characters |
| `notes` | Specific limitations or scope; can be empty when nothing material needs adding |
| `reviewed_on` | Actual listing-review date in YYYY-MM-DD; not a fabricated freshness stamp |
| `review_method` | `page` or the limited `index` exception |

The validator rejects malformed fields, duplicate IDs, equivalent destinations with www/fragment/trailing-slash variations, invalid access labels, tracking/referral parameters, and future review dates. It escapes rendered text. It does not decide whether a publisher's claims are true.

The separate `RESOURCE_BACKLOG.json` records public candidates and unresolved discovery questions. It is deliberately not loaded into the site build. Never put credentials, private notes, allegations, raw user correspondence, or the owner's personal approval packet into either file.

## Linking and reader experience

Every listing provides a reason to open it, a publisher, an access label, a level, and a visible review basis. Search combines titles, publishers, descriptions, formats, notes, levels, categories, and access. Topic and free-only filters combine with the text query. All links remain available without JavaScript. Native category jumps clear filters so a hidden section does not become a dead end.

Use direct links with normal browser behavior. Do not introduce redirect tracking, affiliate codes, remote thumbnails, embedded players, cookies, local search history, or custom click analytics in this workstream. Existing pageview-only analytics stays unchanged. The site does not copy complete articles, PDFs, course text, images, or tables from the destinations.

The overview, library, and Study Desk link to the directory. Category sections point back to relevant local explanations. Add a few exact deep links to a local guide only when they help that guide; do not append all 62 links to every page. Create category subpages only when a single directory becomes demonstrably hard to browse. Keep one catalogue as the source rather than copying lists across pages.

## Batch size and expansion priorities

For the next discovery pass, aim to evaluate roughly 15 to 25 candidates around two or three gaps. The number is a work-sizing suggestion, not a required publication quota. Publish only the accepted subset. A research pass that rejects duplicated or poor resources is still useful.

Priority gaps after the first release are satellite and bounty-specific study, stronger mixed-game depth, beginner-friendly video series, independently verified creator/vlog channels, and additional openly accessible technical research. Expand beyond the publishers already represented. Consider official regional rule and consumer-information sources separately, with jurisdiction and date made explicit rather than giving broad legal conclusions.

Do not call this an exhaustive internet index or claim a target of 100 or 500 links has been achieved before it has. Report published entries, category coverage, directly read destinations, and unresolved review items separately.

## Maintenance and corrections

Run the manual work queue with an explicit date:

```sh
python _scripts/poker_resources.py --as-of 2026-10-07
```

The JSON output says `network_checks_performed: false`. It lists index-only items first, then entries whose category review interval is due. This command does not fetch URLs, change the catalogue, refresh dates, schedule work, or publish anything.

During an actual recheck, record the final destination and whether it still answers the stated question. A 200 page may be a generic homepage or a soft 404. A 403, 429, blocked browser, or timeout does not establish that the page is dead. Try an ordinary permitted public read later or leave it in the review queue. Do not bypass access controls.

Correct stable redirects after confirming the new identity and content. Mark changed access or changed scope honestly. Remove a confirmed irrelevant, unavailable, or unsafe destination in a reviewed change and keep the reason in the non-sensitive change history. Do not silently replace a specific teaching article with a casino landing page. An automated HTTP-checking service, if later added, may propose review items but must never auto-publish or certify editorial quality.

## Release checklist

```sh
python _scripts/build.py
python _scripts/build.py --check
python -m unittest discover -s _tests -p 'test_*.py'
python _tests/resources_browser.py
```

Run the existing full CI suite before merge. The resource browser checks also execute from the existing library browser suite. They cover search/filter intersections, free-only behavior, keyboard interaction, empty/reset states, injection strings, category jumps, small screens, text spacing, print, disabled JavaScript, and blocked-script fallback. They do not visit resource providers.

Review the source and generated output together, inspect phone and desktop previews, recheck the current main branch, and merge only the tested head. Verify Pages deployment and byte-matched live files afterward. Keep external-page review evidence separate from the browser tests that only validate this site's interface.

## Current measured scope and limitations

Initial catalogue: 62 resources, 13 categories, 61 public-page or catalogue reads, one explicitly limited index-only listing. No complete paid course, software binary, subscription, or full broadcast was evaluated. Research-paper landing pages do not imply full-paper replication. No reader-comprehension study or traffic-growth result is claimed.

No recurring discovery run, automatic link check, publication job, or notification has been scheduled. A recurring research-and-review cadence can be authorized separately. New source discovery and final publication remain separate decisions.
