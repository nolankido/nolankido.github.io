# SEO/GEO improvement Turn 43: A published content-production workflow with an explicit video hold

**Date:** November 20, 2026 (Pacific/Honolulu)  
**Website:** https://nolankido.com/  
**Existing article:** https://nolankido.com/technology/ai-poker-video-evidence/  
**Starting GitHub main:** `ede87053f394696e9b4522d4b4b3426f758a39b5`  
**Roadmap position:** Turn 43 of the 37–61 improvement plan.

## Editorial decision

Publish a **concrete, original production receipt** rather than a new generic article about AI writing. The publicly available NolanPoker example already includes a first-person episode companion, three proposed AI-assisted captions, structured source facts, an offline verifier, and clear limitations. It lacked a single obvious answer to: **Which deliverable was actually published, and which part still requires human approval?**

The result is a source-to-publication handoff for the **written content**, with the current-video graphics explicitly not approved by the cited record. The update deepens an existing indexed canonical page, creates one reusable public Markdown download, and adds no new competing indexable URL.

## Sources examined and what they establish

| Source | Direct observation | Limit |
| --- | --- | --- |
| [_source/poker/portland-meadows-ep1.html](../../_source/poker/portland-meadows-ep1.html) | Existing companion first published November 2, current linked Episode 1 video, narrated 6-4 offsuit and 7-7 hand accounts, sponsor/organizer schedule context and distinct payout labels | Account mixes documented organizer program with first-person narration and older version 7 edit history; not independently certified current video transcript |
| [Published Episode 1 companion](https://nolankido.com/poker/episodes/portland-meadows-ep1/) | Independent content retrieval found the public companion at its self-canonical URL | Successful HTML extraction is not verification of each asserted tournament hand |
| [AI/poker source article](../../_source/technology/ai-poker-video-evidence.html) | Worked, explicitly AI-assisted editorial proposal with three captions, source links and factual limits | Does not prove the proposals appeared as graphics in the current YouTube upload |
| [Original public editorial source snapshot](https://github.com/nolankido/nolankido.github.io/blob/da8de1e4022490c851a618778c564cedaf70f03c/_source/technology/ai-poker-video-evidence.html) | A pinned, existing earlier version of the published AI/poker editing case was retrieved | Not a complete history of private prompts, footage work or human approvals |
| [Scene-claims JSON](../../downloads/portland-meadows-ep1-scene-claims.json) | Three structured proposed scenes, explicit absent current-cut checks and no human video-graphics release approval | This is not an audiovisual file analysis or verified payout database |
| [Fact gate](../../downloads/poker-vlog-fact-gate.py) and [article evidence explanation](https://nolankido.com/technology/ai-poker-video-evidence/#poker-ai-check) | The site records zero targeted findings in three structured proposals and seven planted conflicts detected during historical synthetic controls | Historical narrow checker results, not an end-to-end AI or MP4 QA run in Turn 43 |
| [Truth-to-screen QA worksheet](../../downloads/poker-vlog-truth-to-screen-qa.md) | Human review criteria for media, statements, card graphics, sound and rights | A template is not evidence that final video approval has occurred |
| [Public AI/poker article](https://nolankido.com/technology/ai-poker-video-evidence/) | Independently retrieved a source-linked article with self-canonical and November 4 published date | Search rankings, assistant citations, viewer response and conversion metrics unavailable |

The public written companion reports about **148,000 / 15,000 = 9.87 BB**, **585,000 / 30,000 = 19.5 BB**, a **75,000 / 30,000 = 2.5 BB** button raise-to figure, and distinguishes **$5,100 advertised first** from **$2,900 gross reportedly received after a four-way deal**. Those arithmetic ratios were independently recomputed against the checked source JSON in Turn 43. They are not solver findings or an independently audited profit statement.

## Actual change

1. Added the detailed, original [public source-to-publication receipt](../../downloads/nolanpoker-content-production-receipt.md). It gives an evidence-bounded five-stage route: source → drafted captions → narrow independent checking → human review boundary → actual written publication. Each stage links to the existing public artifact or evidence record, including the archived original editorial source snapshot.
2. Added one accessible, direct answer paragraph with `id="poker-ai-publication-status"` near the top of the **existing** AI/poker article. It states that the written companion and caption-study article were published, whereas the three captions are published **only as proposals**, not proven current-video overlays.
3. Added an in-page "What shipped" navigation link pointing to that paragraph. The article retains all six original H2 sections, all three candidate captions, the original audio-review caveat, and its nine-minute reading estimate.
4. Applied the **same two HTML changes** to both the editable `_source/technology/ai-poker-video-evidence.html` and the committed generated `technology/ai-poker-video-evidence/index.html`. Compared to the starting `main` blobs, no other article bytes changed.
5. Registered the new public Markdown receipt as an exact-byte static target in `_scripts/check_live.py`. Added ten offline regression tests in `_tests/test_turn43_published_content_receipt.py` and registered them in `_scripts/local_release_checks.py`.
6. Updated `README.md` and `AGENTS.md` to preserve the meaning of the written/video distinction and to keep future editing turns from turning the released example into a false endorsement of an unreviewed video caption.

### Publication and change-date constraints

The source article retains **datePublished November 4, 2026** and **dateModified November 19, 2026**, its last substantive article revision. The companion retains its original November 2 publication date; this Turn 43 change does **not** edit the companion. The 2026-11-20 date belongs to the **new separate receipt**, not to the historical Episode 1 video release or a newly proven approval. The canonical page route, structured author identity, article titles/descriptions and sitemap entries are unchanged.

## Reproducible evidence checks

The Turn 43 source review checked:

- Both actual public page paths returned readable content and expected canonical metadata.
- The scene JSON states `current_public_cut_timestamps_checked=false`, `current_public_cut_graphics_checked=false`, `confirmed_board_runouts=false`, and `human_release_approval=false`.
- Three arithmetic ratios match the public narrated values, assuming the reported stack timing.
- The original article release snapshot exists at the pinned GitHub commit.
- The new receipt describes five distinct production stages without adding an unverified human signoff or claiming current-video frame accuracy.
- The new article source and committed generated HTML contain **exactly the same added paragraph and navigation link**, with unchanged existing headings, dates and canonical.
- Ten new unit-test definitions and manual release inventory/checklist integration were source-reviewed.
- There are no repository-authored GitHub Actions workflow files.

**Important test limit:** This execution environment cannot resolve `github.com` from the shell to clone the full repository. The new ten-test Python module, complete local generator, full HTML5/unit/browser suite and production byte parity **were not run in a complete checkout**. An inspectable GitHub source change is not an executed test. The original article's archived claims of structured-fact-gate success are kept as historical results, not claimed as a fresh current-video inspection.

### Suggested complete-checkout acceptance commands

```powershell
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 -m unittest discover -s _tests -p test_turn43_published_content_receipt.py -v
py -3 -m unittest discover -s _tests -p test_turn35_ai_poker_case.py -v
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/check_live.py --only /technology/ai-poker-video-evidence/ --only /downloads/nolanpoker-content-production-receipt.md --attempts 3 --interval 5
```

Record source and live HTTP results separately. A failed or blocked network request is inconclusive, not an assumed HTTP 404. Google Search Console clicks/impressions, Bing AI citations, assistant answer-panel results and verified content-business outcomes remain unavailable, not zero.

## Next improvement

**Turn 44:** Find a separate real AI-assisted software-development case with public code, tests, a playable/released artifact and a person-in-the-loop acceptance boundary. Prefer an existing game/site repository and work at a canonical practical-AI case instead of adding generic AI-software articles. Keep simulated demos distinct from live users and actual business value.

No GitHub Actions, paid tooling, cron, new tracking, private footage, unpublished hand histories or third-party participant information were introduced.
