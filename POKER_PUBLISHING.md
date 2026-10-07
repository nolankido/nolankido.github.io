# Publishing the poker section

## The shortest workflow

Give the site editor the approved public video URL, final title, a short summary,
actual chapter times, and the hand notes you want made public. The editor prepares
one catalog record, verifies the details with you, then builds and tests the site.
No homepage redesign or separate page-by-page copying is needed.

A website release does not publish a video to YouTube. Uploading, editing, deleting,
or scheduling a YouTube video is outside this workflow. Do not announce an episode
here until its public video is playable and approved for this website.

## What readers get now

- `/poker/`: introduction, current collection, reader routes, study links and RSS.
- `/poker/start-here/`: viewer guide, notation and linked terminology.
- `/poker/reviewing-a-hand/`: the existing fictional worked hand.
- `/poker/study/`: hand-review and session-debrief sheets, examples and previews.
- `/poker/feed.xml`: a separate Poker feed. The general Notes feed is unchanged.

The catalog is deliberately empty until approved real content is supplied. There
are no invented videos, results, channel links, portfolios or empty archive pages.

## A record becomes a companion page

`_source/poker/catalog.json` contains only `version: 1` and an `entries` list.
Each approved entry creates its own permanent URL:

| kind | URL |
| --- | --- |
| episode | `/poker/episodes/<slug>/` |
| hand | `/poker/hands/<slug>/` |
| story | `/poker/stories/<slug>/` |

The builder creates the page, adds it to the Poker collection and feed, includes
it in the sitemap and live verifier, and connects related entries in both
directions. The newest six records appear first; older records remain accessible
inside a simple expandable collection. No search system is needed for this size.

Changing a title does not change its slug. Keep published slugs and publication
dates stable. For a substantive correction, add an explicit `updated` date and a
short `revision`; neither the build nor a homepage selection changes dates.

## Draft privately

Never put actual unpublished footage, hand notes, private drafts or completed
worksheets in this public repository. `_source`, excluded files and unlinked paths
are still visible on GitHub. Approval checks are not access controls.

Create a blank draft in a folder outside the website checkout:

```sh
python _scripts/poker_draft.py episode first-episode --output ../poker-drafts/first-episode.json
python _scripts/poker_draft.py hand first-hand --output ../poker-drafts/first-hand.json
python _scripts/poker_draft.py story first-story --output ../poker-drafts/first-story.json
```

The helper never publishes, refuses paths inside the repository, and will not
overwrite an existing file. It creates `approved: false` and no invented content.
Fill it in privately. When the owner approves the final meaning and public scope,
copy only the approved record into the public catalog and set `approved` to true.
Do not commit a private draft just to see whether validation rejects it.

## Record fields

Required fields are `slug`, `kind`, `title`, `summary`, `published`, `approved`, and
`sections`. A section has exactly `heading` and `paragraphs` (a list of plain text).
Titles are at most 140 characters; summaries at most 320. Publication dates use
YYYY-MM-DD and must be the actual website publication date, not the session date.
There is no scheduled-release mechanism. The catalog rejects publication and update
dates after the current UTC date, so do not pre-stage a future-dated public record.
Only already-approved public material belongs here. All text is escaped. Raw HTML
and embedded scripts are not supported.

Optional fields:

- `context`: a brief approved situation summary. A session date belongs here only
  if deliberately public. Do not add lodging, future travel or identifying details.
- `video_url`: one standard HTTPS YouTube watch or youtu.be URL. Episodes require it.
- `duration_seconds`: the actual positive integer runtime whenever there is video.
- `chapters`: a list of `{ "seconds": 0, "title": "Opening" }` objects. The first
  starts at zero, subsequent times increase, and each is before the video ends.
  Empty chapters are allowed. Check chapter labels for accidental spoilers.
- `related`: unique slugs of other approved entries. Missing targets are rejected;
  related pages link back automatically. Give every entry its own unique slug.
- `record_type`: required for a hand, either `reconstructed` or `illustrative`.
  Mark approximations and unknown details in the actual paragraphs too.
- `spoiler`: plain-text paragraphs shown inside a closed “Result and later review”
  disclosure. This is spoiler presentation, not privacy. It remains in page source,
  accessible to search engines and any visitor who expands it.
- `sources`: approved public HTTPS references, each with `label` and `url`.
- `image`: `src`, `alt`, `width`, `height`. Use an approved JPG, PNG or WebP with a
  lower-case hyphenated filename under `/assets/poker/`. Use actual dimensions.
  Strip private metadata and inspect faces, badges and screens before committing.
  The builder checks the path and existence, not consent or image contents.
- `updated` and `revision`: required together for a substantive correction.

There is no field for private review notes, unpublished results, credentials, or
raw conversation history. Unknown fields and unapproved entries fail the build.
These checks cannot determine whether a statement is true or safe to publish.

## Episode release checklist

Confirm the final cut is approved and the video plays while signed out. Copy the
actual public URL; do not infer a channel handle. Check title, summary, duration,
chapters and any external references against the published video. See YouTube's
own sharing instructions for timestamp links:
https://support.google.com/youtube/answer/57741?hl=en

Publish only supported cards, action, and outcomes. Separate what happened from
what was thought then and from later interpretation. Label reconstructed or
illustrative hands. Do not call an analysis solver-verified without appropriate
support. Resolve permissions and remove private information before review.

Videos open on YouTube through normal links. No iframe, auto-play, remote thumbnail
or YouTube analytics is added. Sitewide Umami pageview analytics is described in
`ANALYTICS.md` and the public privacy page. Chapter links start playback at the recorded second. Syntax
checks do not prove a video exists, is yours, or is public; the signed-out check is
manual and remains part of owner approval. The website does not collect player data.

## Build and release

```sh
python _scripts/build.py
python _scripts/build.py --check
python -m unittest discover -s _tests -p "test_*.py" -v
python _tests/browser.py
python _tests/design_browser.py
python _tests/poker_browser.py
```

Also run the full accessibility/reflow audit described in README. The poker browser
suite builds synthetic episode, story and hand records in a temporary directory,
verifies navigation, spoilers, chapter URLs, escaping and download bytes, and never
publishes those records or visits their dummy video links. CI deletes no content
and sends no real form messages.

Commit public source and generated output together on a staging branch. Review the
diff, preserve the Technology-first baseline, and merge only after tests pass. Check
Pages deployment and `python _scripts/check_live.py` afterward. A build alone is
not a deployment. Keep raw media outside the website checkout, and no test fixture
should ever be used as published material.

For a takedown, do not silently remove the catalog entry and leave old generated
HTML online. Remove the generated file in the same reviewed change, update related
links and record the reason privately. Stable public content should be corrected
in place where appropriate. Removing something does not erase public Git history.
