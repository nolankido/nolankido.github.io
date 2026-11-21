# SEO/GEO improvement Turn 48: Reader-first book pages and original teaching exercises

**Review date:** November 20, 2026, Pacific/Honolulu  
**Website:** https://nolankido.com/  
**Starting GitHub main:** `5515b1441ddb7ed8d0541b22359582bccf3ad5e7`  
**Roadmap:** Turn 48 of 37 to 61

## Why this turn

The two existing canonical author book pages already describe their intended readers, offer genuinely free original teaching worksheets, and correctly avoid unverified Amazon retail offers. Turn 47's public edition ledger and verification guide were fetched independently from the live site before this improvement. The missing reader value was an obvious, efficient **page journey** and a way to try the author's explanatory method before choosing a free resource or checking a retailer edition.

The roadmap disallows declaring something an actual excerpt until it has been checked against the final owned edition and cleared for publication. No final chapter text or edition proof was available to that standard here. Accordingly, these are **new original site-only teaching exercises**, not retail-book excerpts, previews of a Kindle edition, or promises of outcomes.

## Source-backed changes to each book page

| Reader task | One Workflow at a Time | How to Play No-Limit Texas Hold’em |
| --- | --- | --- |
| Choose the intended reader | Native `#ai-book-reader` link to the small-business AI reader description | Native `#poker-book-reader` link to adult newcomers and no-wager foundational practice |
| Try actual site teaching | Native `#ai-book-first-exercise` link, then a second fictional whole-task cost problem | Native `#poker-book-first-exercise` link, then a second fictional equity-versus-price decision |
| Continue with a free original worksheet | Existing `/downloads/one-workflow-ai-pilot-worksheet.md` | Existing `/downloads/holdem-river-call-check-worksheet.md` |
| Check precise retail status | Existing `#ai-book-listing` remains source-bounded | Existing `#poker-book-listing` remains source-bounded |

Both pages now have one named, naturally ordered `<nav class="shell book-reader-jumps">` **immediately after the book hero**, before the longer article body. The links use native fragment navigation to existing, uniquely labeled sections. There is no JavaScript dependency, unverified purchase button, additional canonical page or forced user signup.

### Original sample 1: whole-task time, not draft speed

The page already explains a fictional AI-assisted task that takes 15 minutes against a 12-minute manual baseline. The **new** independent website exercise asks a second question: A fictional report takes 12 minutes manually or eight minutes AI-assisted per run, plus 30 minutes of initial setup. Which is faster over ten uses?

The reader can work it out before revealing the native `<details><summary>` explanation:

- Manual: 10 × 12 = **120 minutes**.
- AI-assisted: 30 + (10 × 8) = **110 minutes**.
- Hypothetical advantage: **10 minutes**, conditional on equal accepted quality and a human review gate.

Eleven additional minutes of review or repair would reverse that advantage. The numbers are deliberately invented; no observed productivity, client adoption or business benefit is implied. The text states that it is **not a verified retail chapter excerpt**.

### Original sample 2: correct poker price versus unverified equity

The existing no-rake, heads-up fictional river exercise correctly computes 10 / 40 = **25%** simplified break-even chip equity. The new site-only exercise asks: If the estimated chance of winning were **20%**, would a correct 25% pot-price calculation itself justify calling?

The native `<details><summary>` answer states that 20% is below 25% **under those exact assumptions**, so the simplified calculation would not support a call. It also makes clear that 20% is an invented guess, not a solver output or observed opponent range. A real hand still requires the board, holdings, opponent range and relevant conditions. No cash wager or playing-strategy outcome is prescribed, and the answer explicitly states that it is **not a verified book excerpt**.

## Mobile, keyboard, print and release implementation

Added `assets/book-reader-journey.css`, used only on body classes `.page-book-one-workflow-at-a-time` and `.page-book-how-to-play-no-limit-texas-holdem`, with versioned URL `?v=20261120`. This narrowly scoped CSS provides:

- Native flex-wrapping book-page navigation; at viewport widths **up to 480px**, links stack vertically so the design is intended to work at **320px**.
- Minimum **44px** tap/focus targets for the four links and each disclosure `<summary>`.
- Visible `:focus-visible` outlines; a forced-colors alternative; no focus trap, custom controls or script.
- `overflow-wrap: anywhere` for navigation and answer text, no rigid fixed-width content columns.
- A print fallback that hides page navigation and requests visible answer text in a closed disclosure.

These CSS features were inspected statically. **Static breakpoints are not a rendered 320px/375px screenshot or actual keyboard-tab test**. Real-device/browser visual and keyboard checks are separately listed below. A passing script/HTML test alone is not evidence of zero horizontal scrolling in all browsers.

## Files and regression coverage

Updated each standalone source **and its byte-identical generated HTML**:

- `_source/books/one-workflow-at-a-time.html` and `books/one-workflow-at-a-time/index.html`.
- `_source/books/how-to-play-no-limit-texas-holdem.html` and `books/how-to-play-no-limit-texas-holdem/index.html`.

Created `assets/book-reader-journey.css`. Registered it in the existing read-only exact-byte public inventory `_scripts/check_live.py`.

Added `_tests/test_turn48_book_reader_journeys.py` with nine offline assertions for exact source/generated parity, one four-link route with real target IDs, native disclosure/answer visibility without JS, original math and unverified-excerpt qualification, no fabricated retailer `Book` properties, 320px-minded CSS and keyboard states, unchanged Books catalog, canonical and existing November 20 modification date, public CSS/worksheet paths, and no GitHub Actions. Registered it in `_scripts/local_release_checks.py`. Existing `_scripts/build_books.py --check` and `_tests/test_book_pages.py` remain mandatory.

Updated `README.md` and `AGENTS.md` with the documented narrow scope and manual mobile acceptance criteria.

**Identity and acquisition constraints:** The two `Book` JSON-LD Work entities continue pointing to Nolan Kido's public Person ID. The site still does not assert an independently unverified ASIN, ISBN, product detail URL, price, official cover, date of retail publication, review count or availability. Both existing book pages retain their original `2026-11-20` page modification date because this is another same-day content improvement. The Books catalog and its canonical item links are unchanged. The two free worksheets are original companion methods, not book chapter downloads.

## Acceptance and evidence limits

**Static source acceptance to check before merge:**

- Each standalone source is byte-for-byte identical to the corresponding committed book page.
- Four fragment destinations on each reader path exist once and occur in reading order after the book hero.
- Both `details` have exactly one native `summary`, are keyboard operable without scripts and include a clearly labeled site-original question, answer and limit.
- The hypothetical arithmetic is internally consistent.
- Book-page metadata, shared Person ID, existing canonical URLs, documented free worksheets and the unresolved retailer status remain intact.
- The additional stylesheet is registered for read-only live download verification.
- No GitHub Actions or paid API was introduced.

**Rendered browser acceptance needed for a comprehensive claim:**

1. At **320px and 375px** widths and at desktop, verify no page-level horizontal scroll; all four reader-path links are visible and reachable by tap.
2. From a keyboard, tab to each reader link, activate it with Enter, then tab to the native disclosure summary and open it with Enter or Space.
3. Check that the answer explanation, free worksheet and edition status are readable without JavaScript or official cover images; test readable forced-colors and browser print output where possible.
4. Verify an exact public response for both book routes and the new CSS; distinguish a cached older release from a confirmed 404 and require exact-byte parity for a complete deployment certification.

**Not established by this editorial turn:** Independent final-book excerpt matching, an authenticated KDP Bookshelf state, edition retail availability, actual reader behavior, traffic/conversion lift, valid assistant citation counts, or measured book sales.

The working container still cannot clone the GitHub repo via external DNS. Unless independently executed and observed, the complete Python build, full HTML5 suite and browser checks must be marked unrun, not passed.

### Complete-checkout acceptance commands

```powershell
py -3 _scripts/build_books.py --check
py -3 -m unittest discover -s _tests -p test_turn48_book_reader_journeys.py -v
py -3 -m unittest discover -s _tests -p test_book_pages.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/check_live.py --only /books/one-workflow-at-a-time/ --only /books/how-to-play-no-limit-texas-holdem/ --only /assets/book-reader-journey.css --attempts 3 --interval 5
```

## Next roadmap improvement

**Turn 49: Consolidate topic-to-book pathways.** Audit existing links from the AI workflow pilot, free Hold'em study guides, Home, About, Bio, Creative and the Books hub. Remove redundant promotions or misleading descriptions; maintain a minimal path from each topical article to the relevant book teaching sample and back. Keep the free articles distinct from book previews and the unknown retail editions unadvertised.

No customer records, proprietary book chapters, new paid retailer links, GitHub Actions, remote model calls or invented engagement metrics were created.
