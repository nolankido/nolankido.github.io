# Poker resource collections release

## Scope

This pass adds 24 individually reviewed destinations to the existing 108-resource catalogue, producing 132 unique resources. It adds five substantive educational guides plus a collection hub. The local guide library grows from 31 to 36. There are no invented personal stories, results or videos.

New guides: free-poker-learning-path, cash-game-study, omaha-and-mixed-games, poker-books-and-courses, poker-research-guide. Each combines original explanation, a fictional worked exercise or study task, and selected resources derived from the main catalogue. A source reused in a collection does not become a second directory entry.

The Poker landing page now leads with resources and collections while retaining the existing personal-publication workflow and anchors. The Technology-first root homepage, all non-Poker pages, personal-account catalogue, contact, shared styles and analytics are preserved. No runtime JavaScript or storage is added.

## Resource review

The accepted destinations and deferred candidates are recorded in `resource-expansion-batch-004.json`. Only their public text, catalogue, transcript or abstract was inspected, as specified per listing. Full paid books, videos, software, research proofs and experiments were not independently tested. Previous review dates remain unchanged. There is no claim of a complete internet inventory or independent superiority over other guides.

The additions cover Omaha and lowball rules, cash-game calculations and operator fees, author/publisher book descriptions, a signed book review, original research records, international event information and peer support. A candidate cash/tournament article was not added because of misleading statements; blocked or incomplete destinations were not promoted into verified listings.

## Reusable architecture

`_source/poker/collections.json` stores only collection descriptions and reviewed resource IDs. `_scripts/poker_collections.py` validates those relationships and renders current source titles, access, dates and cautions. Unknown IDs, duplicate destinations within a collection, unsafe slugs, and paid resources on the free path fail validation.

The normal build also produces Markdown and JSON directory snapshots, preserving every listing and its limitations. Export contents are deterministic and checked against the source catalogue. The directory's stale 24-guide label is replaced by the actual generated guide count. Hostname statistics are explicitly not a count of independent publishers.

## Verification

The local deterministic build and all 163 unit tests pass. Added coverage includes collection discovery, safe rendering, rejection of invalid metadata, exact exports, unique IDs and independently recomputed call-price, rake and Omaha high/low examples. The new browser suite covers six routes at four widths, expanded text spacing, keyboard answers, print, no-JavaScript access, exports and navigation back to individual directory listings.

The container's browser policy blocked local HTTP navigation, so browser execution must be confirmed in GitHub Actions before merging. No local browser pass is claimed. The ordinary CI includes the new suite. The live verifier includes the six routes and two exports in addition to the prior targets. A successful build is not a completed release; verify deployment and exact live bytes after merge.

## Further work

Prioritize signed PLO8 worked strategy from more independent authors, creator-owned video catalogues with usable transcripts, event accessibility information, and country-specific player protection. Review suggestions before publishing. Do not automatically add links or overwrite their review dates based only on a successful HTTP response.
