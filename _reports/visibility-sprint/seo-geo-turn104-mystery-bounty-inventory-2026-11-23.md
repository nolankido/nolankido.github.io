# SEO/GEO Turn 104: teach mystery-bounty inventory and conditional cash expectations

Date: November 23, 2026.
Base main: `ecccb91874030c14b0f0939d0bf56003f269cf02` (merged Turn 103).
Existing guide: `/poker/bounty-knockout-equity/`.

## Reader need

An advertised mystery-bounty jackpot is not the expected award of an eligible elimination. The existing guide already distinguishes ordinary prizes, fixed KOs, PKOs, and an unknown mystery-bounty distribution. This turn gives the reader an original fully specified mathematical example instead of inferring any real tournament's available envelopes.

## Implemented

- Add one native, initially collapsed disclosure, `#bounty-mystery-draw`, after the original mystery-bounty warning and before the existing practice section. Link to it from the existing jump navigation using "Mystery draw inventory".
- In the fixed fictional event, six equally likely envelopes remain: three $50 awards, two $100 awards, and one $650 award. Their total is $1,000. Assume an active bounty phase, one immediate cash draw per eligible knockout, no intervening draw, and uniform sampling without replacement.
- The conditional award mean is $500/3 (approximately $166.67), not the $650 maximum. An explicitly invented 2/5 chance of earning a draw gives $200/3 (approximately $66.67) in expected immediate receipts and a 1/15 chance of the jackpot. Neither is a total action EV or an opponent estimate.
- If the $650 award is removed, the next conditional mean becomes $70. Removing a $50 or $100 award instead gives $190 or $180, respectively.
- Two guaranteed draws from the original inventory have expected total $1,000/3 and a 1/3 chance of including the unique jackpot. This deliberately conditions on two draws already being granted, not on an uncertain future knockout.
- Preserve the original eight practice questions, four scrolling tables, all article prose outside the new disclosure and jump link, original canonical route, metadata and sitemap. No new page, data collection, script, dependency or external request.

## Actual validation

Six standard-library arithmetic tests passed in the isolated local fixture. They checked the weighted mean, the separation of earning a draw and winning a particular award, all three post-draw inventories, enumeration of all 30 ordered pairs of distinct physical envelopes, the unconditional second-draw expectation, and rejection of impossible inventories/probabilities.

The exact new static disclosure passed a balanced-markup check. Eight isolated Chromium checks at 320, 390, 768 and 1440 pixels, with JavaScript enabled and disabled, opened and closed it using the keyboard. No network requests or script errors were observed in the isolated fragment wrapper. This is a fragment test, not a complete styled site/browser pass.

Authenticated repository readback confirms the inserted disclosure is identical in both HTML files. The regression module's Git blob is `8eb4263260fac871047898e55fa0e2391d0c54d8`, identical to the locally executed test file. The existing Finder parser deliberately excludes navigation and collapsed details from its searchable article prose. A full generated-index comparison remains a site-integration gate.

Three additional integration checks were authored for source/public disclosure and link parity, Finder text parity, and deterministic full-page build plus manual runner/no-Actions safeguards. The full integration suite has not been executed here.

## Remaining release acceptance

Confirm publication with the existing public page and the new anchor after merging. Presence of the public disclosure does not establish exact live bytes. Run the full repository release checks from a complete checkout.

```powershell
py -3 -m unittest discover -s _tests -p test_turn104_mystery_bounty_inventory.py -v
py -3 -m unittest discover -s _tests -p test_poker_bounty_knockout.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _scripts/local_release_checks.py --full --browser
py -3 _scripts/check_live.py --only /poker/bounty-knockout-equity/ --attempts 8 --interval 15
```

The lesson is entirely fictional after-play study. It neither estimates actual tournament prizes or odds nor offers a live decision recommendation. No paid service, automated job, GitHub Actions, tracking, or inferred search-visibility gain is introduced.
