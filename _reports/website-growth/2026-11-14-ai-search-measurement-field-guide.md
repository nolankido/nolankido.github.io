# Website growth: manual AI-search visibility audit

Review date: November 14, 2026
Target: https://nolankido.com/technology/ai-website-visibility/

## Reason for the change

The website already contained a reproducible first-party Search Console CSV method, while the larger SEO and GEO reporting protocol was available mainly in a GitHub repository report. Readers needed an on-site explanation of AI-answer citation measurement that does not equate a crawler request, Google impression, Bing citation, ChatGPT link, and actual referral.

## Implementation

- Added an on-page, source-linked measurement section with a four-source comparison table and a five-step monthly protocol.
- Added `downloads/ai-search-visibility-monthly-worksheet.md` as a blank private-use record with eight stable unbranded prompts, sample logging columns, denominator rules, and a clearly fictional 2/16 interpretation.
- Added a direct in-page jump and registered the download in the site's static public target manifest.
- Updated the page's revision metadata and sitemap date to 2026-11-14 without changing the 2026-11-03 original publication date, canonical URL, or feed GUID.
- Kept all owner analytics exports, AI response histories, and account records private.

## Sources and interpretation guardrails

1. Google Search Console's Generative AI performance (Search) measures Search AI impressions, not ChatGPT answer citations: https://support.google.com/webmasters/answer/16984139
2. Bing Webmaster Tools' AI Performance covers citations in listed Microsoft AI experiences and is aggregated and sampled. Its citations are not clicks or general rankings: https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c
3. OAI-SearchBot is the ChatGPT search crawler, separate from GPTBot training controls. Crawl eligibility does not guarantee citation: https://developers.openai.com/api/docs/bots
4. The longer owner-specific protocol predates this guide and remains published at `_reports/visibility-sprint/seo-geo-measurement-v1.md`.

The fictional 2/16 example is not an observation of Nolan Kido's website. The changes make measurement easier to understand but do not establish a search gain.

## Release verification scope

Repository-level assertions for the candidate:
- The new source section and public HTML contain exactly the same body and links.
- Exactly one new heading ID and one navigation link exist on the target page.
- The new worksheet is in the public target registry.
- Metadata and sitemap date use November 14 while the initial article date stays unchanged.
- New links use documented official provider pages and the site's internal worksheet path.

A complete local generation run and full website regression suite need a full repository checkout. They cannot be claimed solely from direct GitHub blob reads. Publication and direct live HTTP checks should be recorded separately after merge.

No GitHub Actions, scheduled tasks, paid API, extra tracker, fabricated traffic, or invented citations were added.
