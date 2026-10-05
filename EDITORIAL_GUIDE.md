# Editorial guide

## Purpose

A personal home for useful work, clear ideas, and conversation. The visual identity is stable. Develop the substance instead of repeatedly redesigning the site. Public copy should be specific about ideas without disclosing private projects, finances, relationships, schedules, or other people's information.

## What belongs

Publish a worked explanation, a genuinely useful resource, a reflection the owner endorses, or a creative observation worth sharing. Do not invent experiences, favorite things, credentials, testimonials, or a past change of mind. Mark fictional examples. Link research where used and state what the research does not establish. A public statement of principle is not evidence of a biography or a specialist qualification.

The site is not a sales funnel, relationship profile, exhaustive resume, project dashboard, or activity feed. Keep social and professional invitations ordinary and mutual. Do not add visitor tracking, forms for private worksheet answers, or public achievement counts to make a small collection look larger.

## Publishing workflow

Start with the owner's actual idea or material approved for public use. Draft away from this public repository. Check the argument, examples, arithmetic, source links, and private/public boundary. Confirm the owner endorses the final meaning. Only then add public source and regenerate pages. AI can help structure, edit, and test; it must not invent the owner's identity. Articles retain an assistance disclosure.

Edit `_source/notes/`, `_source/pages.json`, and `_source/selection.json`. The selection file sets curated homepage links and reading order independently of RSS publication order. Dates are explicit and never advanced by a build. Substantive revisions use `updated` and a concise `revision` in the manifest; visible update notes and structured data follow those fields. Do not backdate new work or describe a correction as cosmetic. Keep existing URLs stable.

Resources have a blank Markdown file in `downloads/`, an example in `_source/examples/`, and intended-use/limit text in `_scripts/catalog.py`. Examples use invented people and numbers. The same blank file is previewed and downloaded. Adapt the example before recommending the tool for a new kind of use. A worksheet is not a substitute for conversation, consent, or qualified advice.

## A small review, not a content treadmill

After launch, revise when feedback, a correction, or an actual new contribution warrants it. A quarterly review is a suggested manual practice, not a scheduled task. Ask what remains useful, what is misleading or stale, whether an important link or contact path is broken, and whether maintaining the site is consuming too much attention. Keep any feedback log private. Do not collect names or score personal relationships for this purpose.

For informal feedback, ask a few people from different backgrounds what the site suggests the owner contributes, what feels distinctive, and what seems exaggerated or confusing. Do not manufacture answers or publish praise without permission.

## Continuity

Keep domain renewal, account recovery, backup checks, and access arrangements in the owner's private records. No credentials or recovery codes belong here. Maintain a private backup of the public source and a simple local build path. Changes go through a staging branch, regression tests, a non-forced update of main, and a live release check. Revert a faulty release rather than rewriting history. No private material becomes safe merely because it is excluded from navigation or marked noindex.
