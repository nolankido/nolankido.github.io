# Public project portfolio: release record

Date: November 13, 2026

## Reader problem

The public site already linked documented AI applications, local browser tools,
creative projects, source-backed poker records, and accounting research, but
the links were distributed across Home, About, Technology, Creative Work, and
the short biography. There was no one canonical project-oriented route where
a new reader could compare those kinds of work and their evidence boundaries.

This is a navigation and comprehension finding based on current published
source, not a measured claim about traffic, dwell time, search rankings, or
generative-AI answers. Existing public work and its caveats were preserved.

## Implementation

- Added `/projects/` as a selected public portfolio, with a clear division
  between browser tools, recorded software demonstrations, specific checks,
  first-person creative work, and independently identifiable scholarship.
- Linked only already published content, including the task-brief tool, the
  workflow-time calculator, poker calculators, Review Reply Writer, Preflight,
  Dinner on Time, the AI test record, checking cases, NolanPoker, poker comics,
  and the 2012 journal article.
- Kept every claim within the evidence available from its existing source.
  Private game projects, unverified outcomes, client records, and unpublished
  work were not presented as released or measured.
- Registered one indexable main-manifest page, a self-referencing canonical,
  a distinct search title and description, a new sitemap entry dated for
  genuine publication, and appropriate `CollectionPage` structured data that
  references the existing stable Person ID.
- Registered the index in the browser-local Find directory under Technology,
  with Poker and Creative Work as additional interests. The index uses the
  existing public title and description; no search-query data is transmitted.
- Added natural links from Home, About, Technology, Creative Work, and Bio,
  without changing primary navigation, site-wide scripts, analytics, or the
  public biographies. The preexisting homepage/section modification dates
  were not advanced for minor navigation additions.
- Added four local regression tests for route uniqueness, schema, sitemap,
  evidence boundaries, and reachability, plus a default local release group.

## Local validation

- `python _scripts/build.py --check`: **232 generated files, zero drift**.
- `python _scripts/check_search.py`: **203 sitemap URLs, 203 distinct page
  titles and descriptions, zero issues**. This is generated HTML and metadata
  coverage, not confirmation of actual Google indexing.
- `python _scripts/check_internal_links.py`: **14,076 internal links**, 4,065
  fragment links, zero issues.
- `python _tests/check_html5.py`: **208 HTML documents**, zero failures.
- New portfolio-specific regressions: **4/4 passed**.
- Default manual `local_release_checks.py`: **82/82 passed** with local
  `html5lib` installed. Some history-based checks initially lacked previous
  PR commit objects in a shallow checkout; they passed once the original
  repository history was available. No historical checks were deleted or
  rewritten to accept this release.
- `git diff --check`: passed.

A local headless Chromium attempt could not launch because the workspace
restricted its process socket. **Mobile and desktop visual review remains
unverified** until a browser capable of opening the deployed page is used.

## Outcome boundary and follow-up

Publication of a portfolio improves the site's inspectable source inventory,
not its measured search or AI citation performance. Future work should seek
real first-hand records and trustworthy editorial links rather than make
unsubstantiated claims or create AI-only text files. Search Console reports
were unavailable in this session because the connected GSC Wizard account
requires a subscription. The free Search Console export workflow on the
existing website remains available if the owner wants a private baseline.

No GitHub Actions workflow, paid API, automated marketing, new tracker, or
recurring service was created or enabled.

## Primary guidance

- Google Search Central, optimizing for generative AI features:
  https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- OpenAI, publishers and developers FAQ:
  https://help.openai.com/en/articles/12627856-publishers-and-developers-faq
- Bing Webmaster Blog, AI Performance public preview:
  https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/
