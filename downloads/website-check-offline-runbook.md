# An offline release check for AI-assisted website changes

Free, local and reusable. Prepared November 18, 2026.

This worksheet accompanies Nolan Kido's [documented website-repair case](https://nolankido.com/technology/checking-ai-website-changes/). It is a practical check sequence, not a claim that all defects, security issues, accessibility barriers or search problems can be found automatically.

## Start with a negative control

Download [website-check-reproduction.py](https://nolankido.com/downloads/website-check-reproduction.py) beside this file. Read the script before running it. The script parses embedded examples by default, makes no network requests, and writes no files.

Install the open-source parser separately if it is missing (installation may use your network):

    python -m pip install html5lib==1.1

Then run:

    python website-check-reproduction.py

Expected: a JSON result with \`"status": "pass"\`. The deliberately invalid fragment must report \`"code": "end-tag-too-early"\` with \`"name": "div"\`; the corrected fragment must have no errors. A different parser error, or success for both fragments, is not the intended negative-control result.

## Check one of your own built pages

Run this command with a path to a **local built HTML file** you own or may inspect:

    python website-check-reproduction.py --file path/to/built/index.html

- Exit 0: this HTML5 parser returned no structural errors for that file.
- Exit 1: the parser found one or more errors. Inspect the reported code and position, fix the source, rebuild and retest.
- Exit 2: the local file could not be read. This is not a validation result.

The file check does not upload content or send a network request. A clean HTML5 parse does **not** establish that links, forms, scripts, responsive layout, accessibility, data handling or deployment work.

## For this site, run complementary local gates

From the repository root:

    python _scripts/build.py --check
    python _scripts/check_search.py
    python _tests/check_html5.py
    python _scripts/check_internal_links.py

These commands are specific to this site and need its source tree. The HTML5 checker needs the test dependencies from \`requirements-test.txt\`. Run the local unit and browser suites relevant to the files you changed. Check the delivered public response separately after publication. Do not add or rely on GitHub Actions, cron or an external CI service for this project.

| Gate | What it can show | What it cannot show alone |
| --- | --- | --- |
| Deterministic build | Generated output matches the source | Valid HTML, correct claims or working controls |
| Search metadata | Expected titles, descriptions and canonical values | Actual indexing, ranking or assistant citations |
| HTML5 parser | The checked page has no parser-reported errors | Functional behavior, complete accessibility or security |
| Internal-link checker | Links target registered local pages or files | Live HTTP availability or third-party destinations |
| Browser and keyboard checks | Sampled navigation and control behavior | Every device, input method or future release |
| Public GET comparison | Sampled deployed bytes match the intended release | Ranking gains, contact-message delivery or uptime |

## A documented example of the boundary

The pre-repair source at [commit 2bf8908](https://github.com/nolankido/nolankido.github.io/blob/2bf8908339e06f604cea00f0254494e17171ecf4/_source/technology/task-brief.html) ended with:

    </div></div></section>

The repaired source at [commit 73782ca](https://github.com/nolankido/nolankido.github.io/blob/73782caa4697204690c679626b36427c28201234/_source/technology/task-brief.html) ended with:

    </div></section>

Those exact closing strings were checked against the two public, pinned source files on November 18, 2026. The historical test counts and deployment checks were reported in the archived release records; this worksheet does not recreate the 2026 release or rerun those historical suites. The embedded Python example reproduces only the **same error class**.

## A release note you can fill in privately

- Intended change and unchanged constraints:
- Source revision and build output:
- Negative control result and parser version:
- Build, search, HTML, link and relevant unit checks:
- Browser width, keyboard path and observed result:
- Delivered page checks and time observed:
- Remaining unknowns, reviewer and release decision:

Keep private credentials, unpublished content and customer records out of public logs or issue reports. A release is ready only to the extent that its particular acceptance criteria have been checked.
