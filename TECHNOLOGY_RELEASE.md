# Technology-first personal homepage

The permanent destination hierarchy is Technology, Poker, Creative Work. Technology has the first full-width, dark panel and largest destination heading. Poker is second, with a wider secondary panel than Creative Work. Mobile, keyboard, and document reading order preserve the same hierarchy. Notes remains accessible as the shared writing collection, not a fourth subject panel.

## Honest starting points

`/technology/` introduces the technology focus and connects existing writing on trustworthy tools to the tool-check resource. It explicitly states that it is not yet a project portfolio or released-software library. `/creative/` introduces writing, design, and visual storytelling, with two existing essays and a clear statement of scope. Neither page promises a launch date or unpublished work.

## Preservation

Poker pages and guide source, all five general essays and their publication dates, downloads, form behavior, the approved base stylesheets, and domain settings remain unchanged. The shared introduction, biographies, navigation, metadata, and footer now lead with Technology. New styling remains in `assets/hubs.css` with content-based cache versions.

## Release checks

Run the existing build, unit, browser, and accessibility suites. The browser suite verifies the measured panel hierarchy at five viewport widths and follows all three destination paths. The live verifier checks 37 responses, including both new overview pages. Do not call a build a deployment: verify the main-branch Pages job and exact public response bytes. Form tests use mocked services; inbox delivery is not tested.
