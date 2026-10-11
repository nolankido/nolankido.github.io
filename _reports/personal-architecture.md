# Personal website architecture

Date: 2026-10-10

## Purpose

Introduce Nolan Kido before presenting the content collections. Preserve the
Quiet Signal design and the subject order: Technology, Living Well, Poker,
Creative Work. Practical AI is a leading interest, not an unsupported credential.

## Reader path

1. Home: personal purpose, useful published reading, subject doors, conversation.
2. Start here: meet the person or choose one short route through the libraries.
3. Technology: connect practical tasks, independent checks, and human judgment.
4. About and biography: a consistent, selective introduction without a resume,
   private project inventory, or real-time personal diary.
5. Deep pages: retain their local navigation and a site-wide route back to the
   personal introduction.

## Publishing boundaries

Do not add credentials, testimonials, adoption figures, measured outcomes,
unreleased work, guessed social links, or personal stories without an approved
source. Keep private work, personal records, and operational details out of this
public repository. Do not publish a portrait or other person's image without
approval. No synthetic personal imagery is used in this release.

The selected cards distinguish a worked example, a practical guide, and a
fictional poker hand. The orientation page distinguishes authored guidance,
external resources, and proposed experiments. No new essays or purported
firsthand experiments are introduced by this architecture change.

## Implementation

The identity configuration controls navigation and the three selected readings.
Canonical titles are resolved from the full page manifest at build time. Sources
stay in their existing collections. Start here is additive; all existing public
routes, local navigation, feeds, and directories are preserved. The About page
uses ProfilePage structured data with only approved name, URL and biography.

Contact code, form provider, verification key, analytics settings, privacy notice,
base design stylesheet, and hosting configuration remain unchanged. No new
runtime dependencies, scripts, accounts, tracking, or third-party services.

## Verification

Run the complete unit suite and committed-output check, then browser reflow,
keyboard, contact-recovery and accessibility checks. Before merging, compare
against current main. Verify both GitHub Pages deployment and exact public bytes.
The one-off branch preparation workflow must not appear in the final release tree.
