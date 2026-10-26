# Turn 22 independent engineering pass: visible best-five showdowns

Prepared October 25, 2026, Pacific/Honolulu. This follows the printable workflow comparison release with a bounded usability improvement to the existing hand-ranking guide. The separate consenting-visitor study remains open. Automated checks do not establish visitor demand or participant outcomes.

## Reproduced gap

The four fictional showdown answers named each resulting rank string, but readers still had to translate that string back to the physical cards. This was most demanding in the shared-board tie, the competing full houses and the ace-low straight example.

## Change

Each existing answer disclosure now includes two labeled five-card groups, one for each player, before the unchanged explanation. The cards reuse the site's native responsive card components and remain hidden until the reader opens the answer. No script, remote request, storage, form, strategy recommendation or personal claim was added.

The eight selected hands are:

- Kicker: A uses Qs Qd As 9h 7c; B uses Qh Qd Jh 9h 7c.
- Shared board: both use Ah Ad Kc Kd Qs.
- Full houses: A uses As Ah Ad Kc Kd; B uses Ks Kc Kd Ah Ad.
- Ace low: A uses As 2d 3s 4h 5d; B uses 3s 4h 5d 6c 7c.

## Verification design

The unit test independently evaluates each declared five-card group, confirms that it contains five distinct available cards, and verifies that its score equals the best score available from the player's seven cards. It also confirms that the visible card elements exactly match the declared card codes. The browser suite adds the guide to all five viewport and enlarged-spacing passes, opens the four native disclosures, verifies eight groups with five cards each, and checks horizontal overflow and accessibility with the existing poker suite.

The focused authoring workflow runs the site build, HTML validation, search validation, the viewer-guide unit suite and whitespace checks before committing generated output. Full hosted release checks and automated review remain merge gates.
