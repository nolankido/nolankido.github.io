# Nolan Kido personal website

A small static website for introductions and occasional notes. GitHub Pages serves the committed HTML. No application server, database, runtime package installation, analytics, or advertising scripts are needed.

## Edit and publish

Use Python 3.10 or later. Edit public copy in `_source/*.html`, article bodies in `_source/notes/`, shared structure in `_source/layout.html`, and page metadata in `_source/pages.json`. Shared public identity and the existing contact endpoint are in `_source/site.json`.

```sh
python _scripts/build.py
python _scripts/build.py --check
python -m unittest discover -s _tests -p "test_*.py" -v
python -m http.server 8000
```

Open `http://localhost:8000` for a local preview. Commit both source files and regenerated output. Do not edit generated root or route HTML directly: the next build replaces it. The build also updates the sitemap, RSS feed, and minimal contact card. It never fetches private data.

For a new note, write its public body, add a manifest entry with a unique ID/path and an explicit publication date, then rebuild. Do not commit unpublished or private drafts here. The public repository is not private storage, even for files excluded from the rendered website.

## Visual design handoff

See `DESIGN_HANDOFF.md`. The original `styles.css` remains the visual foundation. Functional additions and styles for new content are isolated in `assets/site.css`. The contact script is independent of both. Preserve accessibility and form behavior during redesign.

## Tests

The dependency-free tests cover generated output, links, fragments, metadata, structured data, RSS, sitemap, and public-data boundaries. Browser tests render the same committed pages and CSS offline, using mocked service responses. They cover validation, missing/expired verification, retries, network errors, request timeouts, duplicate prevention, no-JavaScript behavior, keyboard navigation, and layout at five viewport widths.

```sh
python -m pip install -r requirements-test.txt
python -m playwright install chromium
python _tests/browser.py
```

Set `CHROMIUM_PATH` to use an installed Chromium executable. Set `SCREENSHOT_DIR` to a directory outside the repository to save review screenshots. Tests never send real contact messages. CI runs these checks with read-only repository permissions and does not modify or deploy code. The existing GitHub Pages branch deployment remains in place.

## Contact service boundaries

The existing Formspark endpoint and public Turnstile site key are retained. Only the contact page loads Turnstile. The receiving service must validate the token with the matching secret configured in Formspark's Spam Protection settings. Never put a secret key into this repository.

Local tests prove client behavior against simulated responses, not delivery to an inbox or the provider's dashboard settings. After service configuration changes, an owner should send a clearly labelled test through the live form and confirm its arrival. The success screen confirms service acceptance, not that a message was read. Failed or ambiguous requests are never automatically resent.

Provider references:
- https://documentation.formspark.io/setup/spam-protection.html
- https://documentation.formspark.io/examples/ajax.html
- https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/widget-configurations/

## Release checklist

Review every change for public suitability. Run the build check and tests. Preview core pages and the contact form. Check the current branch head before merging to avoid replacing another contributor's work. Wait for the Pages deployment to finish and inspect the live pages. A regression can be rolled back by reverting its commit; do not rewrite public history for ordinary changes.
