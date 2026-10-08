from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-10-08'
S = ROOT / '_source/poker'
TDA = 'https://www.pokertda.com/view-poker-tda-rules/'
WSOP = 'https://www.wsop.com/registration/'
TYPES = 'https://www.pokerstars.com/poker/tournaments/types/'
LIVE = 'https://www.pokerstarslive.com/poker/rules/'
NCPG = 'https://www.ncpgambling.org/help-treatment/'

def put(path, content):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + '\n', encoding='utf-8')

def replace(path, old, new):
    target = ROOT / path
    content = target.read_text(encoding='utf-8')
    if content.count(old) != 1:
        raise ValueError(f'Expected one replacement in {path}: {old[:70]}')
    target.write_text(content.replace(old, new), encoding='utf-8')

GUIDES = [
('first-live-tournament', 'Your first live tournament, without the guesswork.', 'Prepare for registration, finding your seat, asking procedural questions, and leaving with one useful observation.', 'live', 'Start here', 'first live tournament beginner registration seat dealer floor preparation', '''
<p class="article-lead">The unfamiliar part of a first tournament may not be the cards. It may be finding the registration desk, knowing when to sit down, or asking what a dealer's announcement means. Prepare for those moments before trying to learn every strategic detail.</p>
<h2 id="before-you-go">Start with the day, not a promise of winning.</h2>
<p>Choose an event whose game, total entry cost and possible duration you understand. Check whether it can continue on another day. Decide what you are comfortable spending for the whole outing, including transport and food, without relying on a payout. Choosing to watch, or deciding not to enter, is also a complete plan.</p>
<p>Read the <a href="/poker/choosing-a-tournament/">structure-sheet guide</a> before comparing events. A large starting chip count is not enough to judge the pace. Save the official event page and the organizer's contact information, then confirm anything that would change your decision to go.</p>
<h2 id="registration">Remove the avoidable registration surprises.</h2>
<p>Ask the organizer what identification, membership card, payment method and eligibility checks apply. Confirm the event number and starting flight, not just its headline name. Ask whether advance payment still requires an in-person verification step. As a concrete example, the <a href="https://www.wsop.com/registration/">WSOP registration page</a> describes identification and Caesars Rewards checks. It is an example of one organizer's process, not instructions for every room.</p>
<p>Allow space in your plan for finding the desk and resolving an issue. Keep your ticket and receipt private. A photograph that includes a barcode, membership number or payment detail is not a suitable public trip update.</p>
<h2 id="taking-a-seat">Let the dealer help you get oriented.</h2>
<p>Before taking a seat, check the table and seat assignment with staff. Tell the dealer that this is your first live tournament. Ask which denominations you have, what the current blinds and ante are, and where the button is. These are procedural questions, not requests for advice about which hand to play.</p>
<p>Under <a href="https://www.pokertda.com/view-poker-tda-rules/">TDA rules</a>, players are responsible for following the action, acting in turn and making intentions clear. Rather than copying a chip motion you saw in a video, ask staff to explain an unfamiliar procedure before using it.</p>
<aside class="viewer-example"><h3>A useful question is specific.</h3><p>“Is the total bet 2,000, and is it my turn?” asks for clarification. “Should I call with this hand?” asks someone else to make part of your decision. Save strategic discussion for a completed-hand review away from play.</p></aside>
<h2 id="unclear-action">When something is unclear, ask instead of improvising.</h2>
<p>Before acting, ask the dealer to clarify the action or amount. For a disputed procedure, ask for the floor and describe what happened calmly. Do not reach into another player's stack, announce an opponent's cards, or try to settle a disagreement with a louder argument. The floor can explain the event's applicable procedure.</p>
<p>The <a href="/poker/table-etiquette/">table-context guide</a> explains common moments such as oversized chips and floor calls. Reading it beforehand is useful; opening a strategy aid at the table is not the purpose of this site.</p>
<h2 id="a-useful-finish">Define a useful finish that does not require a cash.</h2>
<p>Pick one process goal: understand the announcements, keep track of your position, or preserve one hand accurately afterward. Avoid making “prove that I belong” the day's assignment. A first outing does not have to establish your ability or fund the next one.</p>
<p>When play is over, record what was unfamiliar and one question worth following up. Keep the result separate. The <a href="/poker/tournament-day/">tournament-day guide</a> covers breaks, moves and the end of a day; the <a href="/poker/tournament-checklists/">printable planning sheets</a> give you a small place to start.</p>
<details class="poker-details viewer-question"><summary>What should I do before paying if I cannot stay for a possible second day?</summary><div><p>Confirm the event's continuation schedule first. Do not treat a late-registration deadline or a starting-flight label as the event's finish time. An event that does not fit your commitments is not a suitable plan just because the entry price fits.</p></div></details>
''', [(WSOP, 'WSOP: event-specific registration process'), (TDA, 'Poker TDA: player responsibilities and tournament procedures')]),
('choosing-a-tournament', 'Read the structure before choosing the tournament.', 'Compare total cost, starting big blinds, blind progression and time commitments using two fictional event structures.', 'live', 'Start here', 'structure sheet compare tournament event fees buy in big blinds deep stack levels schedule', '''
<p class="article-lead">“Deep stack” and “big guarantee” are headlines. The structure sheet tells you what you are considering. Read it as a description of the time, cost and format, not as a forecast of how well you will do.</p>
<h2 id="the-five-checks">Find five things before comparing the advertising.</h2>
<p>Find the game and format, the full amount payable, the starting stack and blinds, the level schedule, and the event's stopping or continuation conditions. Read the rules about late registration, re-entry and multiple starting flights. Confirm which document applies to the exact date and event number.</p>
<p>The <a href="/poker/tournament-formats/">format guide</a> explains freezeouts, bounties and satellites. These are not interchangeable prize structures. A ticket event is not simply a normal tournament with a different name.</p>
<h2 id="stack-comparison">Compare big blinds, not the biggest printed number.</h2>
<p><strong>Fictional comparison:</strong> Event A starts with 30,000 chips at blinds of 100/200. Event B starts with 50,000 chips at 200/500. Their starting depths are 30,000 / 200 = <strong>150 BB</strong> and 50,000 / 500 = <strong>100 BB</strong>. The smaller chip count is the deeper starting stack.</p>
<table class="viewer-table"><caption>Two fictional schedules, with no breaks during the first hour</caption><thead><tr><th scope="col">Scheduled play time</th><th scope="col">Event A: big blind</th><th scope="col">Event B: big blind</th></tr></thead><tbody><tr><th scope="row">Start</th><td>200</td><td>500</td></tr><tr><th scope="row">15 minutes</th><td>200</td><td>600</td></tr><tr><th scope="row">30 minutes</th><td>300</td><td>800</td></tr><tr><th scope="row">45 minutes</th><td>300</td><td>1,000</td></tr><tr><th scope="row">60 minutes</th><td>400</td><td>1,200</td></tr></tbody></table>
<p>If the stacks were held constant solely for this comparison, an hour later A would represent <strong>75 BB</strong>, while B would represent about <strong>41.7 BB</strong>. Actual stacks will change through play and forced bets. These figures compare units and schedules; they do not predict survival, hands played or strategic advantage.</p>
<p>Also check when antes begin and how they are posted. Dividing by the big blind does not capture every forced cost. Longer levels do not by themselves tell you how many hands will be dealt.</p>
<h2 id="full-cost">Give every percentage its denominator.</h2>
<p>Suppose a fictional event lists $250 toward prizes plus a $50 fee. The total entry price is <strong>$300</strong>. The fee is <strong>16.7% of the total payment</strong>, but <strong>20% of the prize contribution</strong>. Both percentages can be arithmetically correct; comparing them as though they use the same denominator would be misleading.</p>
<p>Read the actual breakdown instead of assuming every dollar goes into the regular prize pool. Ask about any mandatory charges not included in the headline. A lower fee alone does not establish that an event is profitable or appropriate for you.</p>
<h2 id="time-and-prizes">Check the commitments that a headline leaves out.</h2>
<p>Find the start, registration cutoff, scheduled breaks, day-ending condition and any restart. Put these beside your own commitments. A late-registration cutoff is not a finishing time, and a published starting stack is not necessarily the depth you would receive after several blind increases.</p>
<p>Read what the prize actually is and how it is allocated. For a satellite, confirm ticket restrictions; for a bounty event, confirm when bounties become eligible and how the advertised payment is split. The organizer's terms are more useful here than a screenshot shared without a date.</p>
<h2 id="decision-note">Leave with a comparison, not a ranking.</h2>
<p>Complete this sentence: “This event fits my time and spending limits; I understand its format; these details still need confirmation.” Mark missing information instead of replacing it with an assumption. Use the <a href="/poker/tournament-checklists/#event-planner">event planner</a> to compare a small number of options.</p>
<details class="poker-details viewer-question"><summary>Does Event A's 150 BB starting depth make it the better event?</summary><div><p>Not by itself. It is deeper at the start in this fictional comparison. You would still need the full schedule, costs, format and your own time constraints. The arithmetic does not supply a universal event ranking.</p></div></details>
''', [(TYPES, 'PokerStars: tournament-format definitions'), (WSOP, 'WSOP: entry-price and registration information')]),
('registration-and-reentry', 'Registration, re-entry and the cost of another attempt.', 'Separate advance registration, starting flights, re-entry and rebuys, then account for each payment without treating previous losses as a reason to continue.', 'live', 'Start here', 'registration late entry reentry rebuy add on flight freezeout budget total cost tickets', '''
<p class="article-lead">A registration window tells you when entry may be possible. It does not tell you whether another attempt fits your plan. Separate the event's permissions from your own limits before the first entry.</p>
<h2 id="different-terms">Four similar-sounding terms describe different things.</h2>
<p><strong>Late registration</strong> allows a first entry after play begins, within the stated window. <strong>Re-entry</strong> allows a new entry after elimination, subject to the event's conditions. A <strong>rebuy</strong> is a purchase of additional chips under a rebuy event's eligibility rules. An <strong>add-on</strong> is a separate offered chip purchase at a specified stage. Do not assume one is available because another is.</p>
<p><a href="https://www.pokerstars.com/poker/tournaments/types/">PokerStars' format definitions</a> illustrate these distinctions for its tournaments. For a live event, the applicable structure sheet decides the actual limits, timing and eligibility.</p>
<h2 id="ask-before-paying">Resolve the entry details before paying.</h2>
<p>Confirm the event number, starting flight, full payment and registration deadline. Ask whether a deadline refers to payment, completion of verification or being seated. Check how alternates are handled and whether advance registration guarantees an immediate seat. Do not assume an online receipt completes every on-site step.</p>
<p>The <a href="https://www.wsop.com/registration/">WSOP registration page</a>, for example, describes an in-person verification process for initial online registration. Use your organizer's current instructions rather than carrying that particular process over to another event.</p>
<p>For multiple flights, ask whether qualifying more than once is possible and what happens to multiple qualifying stacks. Do not assume they combine, or that an existing qualifying stack can be abandoned. For entry through a ticket or satellite, check the restrictions attached to that ticket.</p>
<h2 id="your-limit">An allowed re-entry is not an obligation.</h2>
<p>Before play, decide a maximum total entry spend and a latest time at which you would even consider a new entry. Those are ceilings, not targets. Being permitted to spend more is different from having a reason to do so. Leaving after the first attempt remains an option even if your original plan allowed another.</p>
<p>After elimination, step away before making a new purchase. Ask whether you still want the new experience at its current starting depth and time commitment. The earlier entry has already been spent. A desire to get it back does not reduce the next entry's price or improve its prospects.</p>
<h2 id="worked-ledger">Count all attempts in the same record.</h2>
<aside class="viewer-example"><h3>Fictional costs, not a suggested budget</h3><p>Two entries at $300 each cost <strong>$600</strong>. With $90 of transport and food, the outing has cost <strong>$690</strong> before any return. A $500 payout would leave a <strong>$100 tournament loss</strong> and a <strong>$190 loss including those trip costs</strong>. Counting only the last entry would conceal part of the cost.</p></aside>
<p>Keep the entry ledger and broader trip costs in separate columns so both remain visible. Record amounts actually paid, including additional chip purchases when relevant. Keep receipts and completed records private. For the distinction between cashes and overall results, read <a href="/poker/variance-and-results/">variance and honest results</a>.</p>
<h2 id="a-stop-is-complete">A stop does not need to be justified by a poker argument.</h2>
<p>Time, fatigue, a changed mood or simply not wanting another attempt are sufficient reasons to stop. Watching a video or reviewing a completed hand later does not require paying another entry.</p>
<p>When gambling is becoming difficult to control, changing the study plan is not the only response available. The <a href="https://www.ncpgambling.org/help-treatment/">National Council on Problem Gambling</a> provides a current route to support. That resource is separate from coaching or performance advice.</p>
<details class="poker-details viewer-question"><summary>Does a second $300 entry become cheaper because the first one ended quickly?</summary><div><p>No. It is another $300 payment. The first outcome changes neither that price nor the limit chosen beforehand. Confirm the event's rules, but do not confuse its permission to re-enter with a reason to do so.</p></div></details>
''', [(TYPES, 'PokerStars: re-entry, rebuy and tournament formats'), (WSOP, 'WSOP: registration and verification'), (NCPG, 'NCPG: gambling support')]),
('tournament-day', 'From the first seat to the end of the day.', 'Prepare for breaks, table moves, bagging chips and finishing a tournament day without treating each logistical step as a strategic problem.', 'live', 'Start here', 'tournament day breaks table change bagging chips restart dinner break floor logistics checklist', '''
<p class="article-lead">A tournament day includes small logistical decisions that rarely make the highlight reel. Know what to check when the table changes, when a break ends and when staff announce the end of a playing day.</p>
<h2 id="before-play">Set up a day you can actually manage.</h2>
<p>Before entering, check the possible continuation schedule and your route home. Pack only what the venue permits and what you will use: required identification, a layer for comfort, and appropriate food or water if allowed. Plan around the event rather than assuming a convenient break or early finish will appear.</p>
<p>Locate the official tournament clock and know where to ask a procedural question. Confirm the current blinds and ante before play rather than relying on an old photograph of the display.</p>
<h2 id="breaks">Know when you are expected back.</h2>
<p>At a break, confirm the announced restart time. Treat that time as the end of the break, not the moment to join a food queue. Allow room to return to the correct table and settle in without rushing.</p>
<p>Leaving a seat is not necessarily a pause in its forced costs: <a href="https://www.pokertda.com/view-poker-tda-rules/">TDA procedures</a> address absent players and the posting of blinds and antes. Ask staff what applies rather than assuming your stack is protected while you are away.</p>
<p>Use a break for something restorative before turning it into another work session. A short private note about a completed hand can wait until you are away from play and the event permits it. No hand is worth delaying the game to document.</p>
<h2 id="table-moves">Treat a move as a staff-directed handover.</h2>
<p>Confirm the destination table and seat, and follow staff instructions for moving your chips. Ask about the approved carrying method rather than pocketing chips or improvising. At the destination, verify that you are in the intended place and clarify the next blind obligation with the dealer.</p>
<p>Check the denominations at the new table rather than estimating value from pile height. A new seat and new opponents also mean that an earlier hand note should not silently inherit the new table's positions or stacks.</p>
<h2 id="end-of-day">Bagging is a continuation procedure, not a cash result.</h2>
<p>If staff end the day with players returning later, follow their counting, recording and bagging instructions. Confirm the recorded total and the required identifying information before finishing. Check the restart date, time and location directly with the organizer.</p>
<p>Keep your private record of the count and restart details. Do not publish a bag label or receipt containing a name, barcode or other identifier. An account can simply say what the verified chip count represents without showing the document.</p>
<p>Whether that stage also earns a payout depends on the event. Do not infer “in the money” from a bag, a surviving stack or the words “Day 2.” The <a href="/poker/tournaments/">tournament-progression guide</a> separates stage changes from prize eligibility.</p>
<h2 id="finishing">Give the end of play a small, definite routine.</h2>
<p>Confirm any required organizer steps, collect your belongings and record the actual costs and return. A receipt is more useful than an estimate when the exact figure is available. Keep an unresolved payment question for the organizer rather than declaring it settled in a public post.</p>
<p>For study, save one question and the facts needed to revisit it. Do not force a complete strategic explanation immediately after elimination. The <a href="/poker/recording-hands/">hand-note guide</a> distinguishes a quick factual record from a later analysis.</p>
<details class="poker-details viewer-question"><summary>Does a photo of a sealed chip bag establish that someone cashed?</summary><div><p>No. It documents a continuation step only to the extent the photo can be understood and verified. Prize eligibility requires the actual event conditions and result. A public account should not convert one into the other.</p></div></details>
<p>For a compact version, use the <a href="/poker/tournament-checklists/#event-planner">event and day planner</a>. You do not need to complete every field to benefit from checking the few details that matter to your outing.</p>
''', [(TDA, 'Poker TDA: seating, chips and absent-player procedures'), (TYPES, 'PokerStars: tournament stages and formats')]),
('recording-hands', 'Keep a hand note you can actually review.', 'Capture positions, stacks, actions and uncertainty after play, with a checked fictional pot ledger and a reusable private note template.', 'live', 'Build understanding', 'hand history record capture notes notation raise to amount pot ledger unknown reconstruction privacy', '''
<p class="article-lead">“Lost with ace-queen” records a result, not a reviewable hand. A useful note preserves who could act, the amounts involved and the moment you want to revisit. It can be short without pretending to be complete.</p>
<h2 id="when-to-write">Capture after play, away from the action.</h2>
<p>Use the record after the hand and only where the organizer allows it. The safest default is to wait until you are away from the table and active play. <a href="https://www.pokertda.com/view-poker-tda-rules/">TDA rules</a> restrict device use with a live hand and strategy tools at the table. A note template is not an exception to those rules.</p>
<p>Do not record covertly, slow the game to write or assume a filming permission includes unrestricted recording. A missing detail can remain missing.</p>
<h2 id="minimum-note">The smallest useful note has a situation, an action and a question.</h2>
<p>Record the game and stage, blinds and ante, number of players, positions and relevant starting stacks. Keep your cards and the board in street order. Then list each action with its amount, including checks and folds that explain who remained in the hand.</p>
<p>Write <strong>raises to 2,200</strong> when 2,200 is the new total for that street. Write <strong>adds 1,200 to call</strong> when that is the extra amount paid. “Raises 2,200” can leave the reader unsure which you meant. For unfamiliar notation, use words instead of compact symbols.</p>
<p>Mark an estimate where it appears: “about 28,000 before forced bets,” “turn suit unknown,” or “reconstructed from memory after the session.” Do not reserve uncertainty for a general disclaimer at the bottom.</p>
<h2 id="worked-note">A fictional note with a checkable pot.</h2>
<aside class="viewer-example"><h3>Illustration only, not one of Nolan's hands</h3><p>Eight-handed no-limit hold'em. Blinds 500/1,000; a 1,000 big blind ante. Button has 32,000 and big blind 28,000 before forced bets. Button holds ace of spades, queen of clubs. Everyone folds to the button, who raises to 2,200. Small blind folds; big blind adds 1,200 to call. Flop: ace of hearts, seven of diamonds, two of clubs. Big blind checks; button bets 1,800; big blind folds.</p><p>The preflop pot is <strong>500 + 1,000 + 1,000 + 2,200 + 1,200 = 5,900</strong>. The small blind, big blind, big blind ante, button's raise and additional call are separate contributions. The uncalled <strong>1,800</strong> is returned; the contested pot is <strong>5,900</strong>. The button's net chip gain is <strong>3,700</strong>, not 5,900 or 7,700.</p></aside>
<p>The note does not establish the opponent's cards or whether the flop bet was the best action. A useful review question could be: “Which worse hands could continue against this size, under a stated range assumption?” That question belongs after the record, not inside it as an observed fact.</p>
<h2 id="missing-information">Make gaps visible before calculating around them.</h2>
<p>If the ante is unknown, do not publish an exact starting pot as though it were recorded. If a suit is uncertain, do not assign a specific blocker. When only a range of stack sizes is plausible, either keep the analysis conditional or choose a different hand for an exact worked example.</p>
<p>Check that the pot ledger and final stacks agree with the described payments and refunds. Keep both chips and big blinds where helpful, but name the blind level used. The <a href="/poker/pot-odds-workshop/">pot-odds workshop</a> handles the extra amount required to call; the <a href="/poker/reviewing-a-hand/">review guide</a> takes the next step into interpretation.</p>
<h2 id="private-and-public">A public explanation needs fewer identifiers than a private record.</h2>
<p>Use position labels rather than names. Remove ticket numbers, faces and identifying details that are unnecessary to understand the decision. Keep remembered thoughts separate from later analysis, and obtain appropriate permission for any material involving others.</p>
<p>The <a href="/poker/tournament-checklists/#hand-capture">blank hand-capture sheet</a> is available to copy, print or download. Complete it privately. There is no upload field and the website does not receive your answers.</p>
<details class="poker-details viewer-question"><summary>In the example, why is the 1,800 flop bet not part of the contested pot?</summary><div><p>No opponent called any of it. It is an unmatched wager returned to the bettor. The button receives the 5,900 contested pot but had already contributed 2,200 to it, leaving a net gain of 3,700.</p></div></details>
''', [(TDA, 'Poker TDA: device restrictions and tournament procedures')]),
('choosing-study-tools', 'Choose a study tool by the question it answers.', 'Distinguish equity calculators, ICM calculators, solvers, solution libraries and trainers before spending money or interpreting a result.', 'results', 'Build understanding', 'study tool software equity calculator ICM solver trainer library comparison free paid documentation', '''
<p class="article-lead">An equity calculator, a solver and a trainer can all display impressive numbers while answering different questions. Start with the question you need to answer, not the product with the most features.</p>
<h2 id="five-tool-types">Five useful categories, five different jobs.</h2>
<h3>Equity calculator: how often do these hands or ranges win at showdown?</h3>
<p>You supply cards, ranges and any known board. The result describes showdown equity for those inputs, not automatically the value of calling when later betting remains. <a href="https://www.pokerstrategy.com/poker-software-tools/equilab-holdem/">Equilab's official introduction</a> is one example of this category. An opponent's entered range is still your assumption.</p>
<h3>ICM calculator: how does this payout model value the stacks?</h3>
<p>An ICM calculation uses the remaining stacks and payouts to estimate prize equity under its model. It is not a cash-out offer or, by itself, a full strategy for the next hand. See <a href="https://support.icmpoker.com/en/articles/3699969-what-is-the-icm-model">ICMIZER's model explanation</a> and this site's <a href="/poker/tournament-equity/">worked tournament-equity guide</a>.</p>
<h3>Solver: what strategies does a specified game model produce?</h3>
<p>A solver works within the configured game, including allowed actions, sizes, ranges and objective. A well-computed result for the wrong situation can still be the wrong reference. The <a href="https://piosolver.com/docs/">PioSOLVER documentation</a> and <a href="https://www.holdemresources.net/docs">HoldemResources documentation</a> provide official starting points for understanding setup rather than only looking at the output.</p>
<h3>Solution library: which previously calculated spot am I looking at?</h3>
<p>A stored solution saves setup work but still needs to match the hand. Check the format, positions, stack depth, ante and action sequence. <a href="https://gtowizard.com/">GTO Wizard's official product overview</a> distinguishes pre-solved material from custom solving. Availability within a particular subscription needs to be checked with the provider.</p>
<h3>Trainer: can I practice against this reference?</h3>
<p>A trainer compares choices with its reference. Treat the score as feedback within that exercise, not independent proof of broad poker ability. Before drilling, learn which game and solution the exercise uses and how errors are scored.</p>
<h2 id="match-the-question">Try the smallest tool that addresses the uncertainty.</h2>
<p>For an unclear call price, a pot ledger and ordinary arithmetic may be enough. For a question about showdown equity, compare clearly specified ranges. For a payout question, inspect the stacks and prizes before asking a tournament model. For strategic comparisons across future actions, read the model's setup requirements first.</p>
<p>When the uncertainty is “I do not know the opponent's range,” a more expensive subscription does not make that range observed. Try explicit alternative assumptions rather than reporting one output as the truth.</p>
<h2 id="before-paying">Use a buying check, not an unsupported ranking.</h2>
<p>Identify one repeatable study task and confirm that the product supports its exact game, operating system and required features. Check the provider's current access limits, renewal terms, cancellation process and trial conditions. Do not rely on prices or feature claims copied into an old comparison article.</p>
<p>Try a small example whose arithmetic you can check. Learn what you can save or export and whether an explanation remains understandable without a screenshot of colored cells. Choose no subscription when the documentation or existing free exercises already meet the need.</p>
<h2 id="model-limits">Read the assumptions alongside the answer.</h2>
<p>Record the starting pot, stacks, ranges, available actions, payouts where relevant, and any convergence or approximation information the product supplies. <a href="https://blog.gtowizard.com/how-solvers-work/">GTO Wizard's explanation of solvers</a> discusses why the game tree is a modeling choice. A displayed decimal does not eliminate a mismatched input or an omitted action.</p>
<p>This is a category guide, not a hands-on product test or an accuracy certification. Public documentation was read for scope; paid software and calculation quality were not independently tested for this article. The <a href="/poker/resources/#tools">software directory</a> keeps provider links and access labels together.</p>
<h2 id="use-after-play">Keep the study session separate from the playing session.</h2>
<p><a href="https://www.pokerstarslive.com/poker/rules/">PokerStars Live's published rules</a> prohibit strategy software, charts and qualifying AI assistance at the table, including assistance relayed by spectators. Other operators have their own restrictions. Use these resources after play and check the actual operator's current policy.</p>
<p>Complete one <a href="/poker/tournament-checklists/#resource-check">resource-check sheet</a>: the question, inputs, answer, remaining uncertainty and next step. A reproducible small study is more useful than collecting tools you cannot yet explain.</p>
''', [('https://www.pokerstrategy.com/poker-software-tools/equilab-holdem/', 'PokerStrategy: Equilab'), ('https://support.icmpoker.com/en/articles/3699969-what-is-the-icm-model', 'ICMIZER: ICM model'), ('https://piosolver.com/docs/', 'PioSOLVER: quick start'), ('https://www.holdemresources.net/docs', 'HoldemResources: documentation'), ('https://gtowizard.com/', 'GTO Wizard: product scope'), ('https://blog.gtowizard.com/how-solvers-work/', 'GTO Wizard: solver models'), (LIVE, 'PokerStars Live: permitted use')]),
('evaluating-poker-advice', 'Read poker advice without borrowing its certainty.', 'Evaluate a video, chart, article or forum answer by its question, evidence and assumptions, then turn it into one checkable study task.', 'results', 'Build understanding', 'advice resources video vlog chart forum source evidence claim study critical review learning path', '''
<p class="article-lead">A clear explanation can still leave out the condition that makes it useful. Before adopting a rule from a video, chart or discussion, work out what it actually claims and whether the situation matches yours.</p>
<h2 id="name-the-claim">Turn the headline into a specific question.</h2>
<p>Replace “this is how professionals play” with something narrower: “What is the claimed response at this position, stack depth and action sequence?” Distinguish a definition, a calculation, a strategic opinion, a personal account and a product claim. They need different checks.</p>
<p>A rules question belongs with the event's current official rules and staff. A product-feature question belongs with current provider documentation. A personal story can be valuable without becoming a general recommendation.</p>
<h2 id="match-the-spot">Read the missing row above the chart.</h2>
<p>Check the game, number of players, positions, stack convention, ante, action history and objective. Is the chart for an unopened pot or for facing a raise? Does it allow calls and small raises, or only push and fold? Does “20 BB” describe stacks before posting, chips remaining, or something else?</p>
<p>A heads-up reference is not automatically a six-player reference. The <a href="/poker/short-stack-decisions/">short-stack input guide</a> explains these compatibility checks. For a solver screenshot, the <a href="https://blog.gtowizard.com/how-solvers-work/">provider's explanation of game-tree inputs</a> is a useful reminder that the visible answer is only part of the model.</p>
<h2 id="watch-the-edit">Enjoy the story and separate the information sets.</h2>
<p>When watching a hand, note which cards the player knew then and which cards the audience sees later. A revealed bluff can explain the outcome without proving that the call was justified beforehand. A selected tournament story also does not contain every entry cost or all of a player's results.</p>
<p>Pause before the reveal and write one reason for each plausible action. Then ask what the outcome actually teaches. The <a href="/poker/decision-lab/">river Decision Lab</a> provides a fictional exercise in keeping the same decision record through two different endings.</p>
<h2 id="compare-explanations">Find the disagreement before picking a side.</h2>
<aside class="viewer-example"><h3>A fictional disagreement worth inspecting</h3><p>Two explanations give different answers for an apparently similar 20 BB spot. One assumes an unopened pot in chip EV. The other faces a raise near a payout jump and uses a prize-equity model. The first task is not to vote for the more confident author. It is to check whether they answered the same question.</p></aside>
<p>If the inputs do match, ask what supports each conclusion: a worked calculation, a documented model, recorded action, or an asserted population tendency. “Players at these stakes never bluff” is not a measured frequency merely because it is repeated often.</p>
<p>For community discussions, look for explanations that expose their assumptions and respond to counterexamples. Agreement among commenters is not a substitute for checking the pot, range or event condition yourself.</p>
<h2 id="one-study-output">Give the resource a job and a stopping point.</h2>
<p>Choose one output you can inspect: reconstruct a pot, explain a term in your own words, compare two range assumptions, or identify why a reference does not match the hand. If the material does not help with that job, set it aside rather than adding it to a compulsory reading queue.</p>
<p>Use a short route through the site and the wider web. For a procedure, start with the <a href="/poker/table-etiquette/">table-context guide</a>, then the <a href="/poker/resources/#rules">official rules directory</a>. For a calculation, start with the <a href="/poker/pot-odds-workshop/">pot-odds workshop</a>, then the <a href="/poker/resources/#math">mathematics resources</a>. For a software question, read the <a href="/poker/choosing-study-tools/">tool-category guide</a> before opening the <a href="/poker/resources/#tools">provider links</a>.</p>
<p>The <a href="/poker/tournament-checklists/#resource-check">resource-check sheet</a> keeps the original claim, your assumptions and what remains unresolved in one private note. One useful answer is a better stopping point than ten open tabs.</p>
<details class="poker-details viewer-question"><summary>Two articles recommend different actions. Must one be wrong?</summary><div><p>No. They may be addressing different games, stacks, action sequences or objectives. Compare those first. If they do match, the disagreement still requires evidence rather than a popularity contest.</p></div></details>
''', [('https://blog.gtowizard.com/how-solvers-work/', 'GTO Wizard: solver inputs and model scope')]),
]

for slug, title, desc, topic, level, keywords, body, refs in GUIDES:
    refs_html = '; '.join(f'<a href="{url}">{label}</a>' for url, label in refs)
    guide = f'''<div class="article-body shell prose viewer-guide field-guide">
<nav class="viewer-breadcrumb" aria-label="Guide location"><a href="/poker/">Poker</a><span aria-hidden="true"> / </span><a href="/poker/live-tournament-guide/">Live tournament field guide</a></nav>
{body.strip()}
<section class="viewer-sources" aria-labelledby="guide-sources"><h2 id="guide-sources">Sources and scope</h2><p>{refs_html}.</p><p>Public reference pages checked October 8, 2026. Planning suggestions and fictional examples are original educational material. Confirm current event details with the organizer; provider documentation is not an independent product test.</p></section>
<p class="editorial-note">Published <time datetime="2026-10-08">October 8, 2026</time>. Prepared with AI assistance. Examples are fictional, not personal tournament accounts. Use these guides before or after play, not as assistance during a live hand.</p>
<nav class="article-navigation" aria-label="Continue learning"><a href="/poker/live-tournament-guide/">Field guide and reading routes</a><a href="/poker/tournament-checklists/">Printable planning sheets</a><a href="/poker/library/">All Poker guides</a><a href="/contact/">Send a correction</a></nav>
</div>'''
    put('_source/poker/' + slug + '.html', guide)

SHEETS = {
'poker-event-planner': '''# Event and day planner

Blank private-use planning sheet. Confirm details with the organizer.
This is not a recommended budget or a reason to enter another event.

## Before paying
Event name / number / flight:
Official event and structure URLs:
Date checked:
Game and prize format:
Full price per entry, including required fees:
Personal total entry-spend ceiling (not a target):
Transport / food / accommodation costs:
Maximum attempts and latest time to consider another:
Starting stack / starting blinds / ante:
Expected arrival level and stack in big blinds:
Registration cutoff and what must be completed by it:
Identification / membership / payment requirements:
Unresolved question for the organizer:

## Plan the day
Start / scheduled breaks / day-ending condition:
Possible restart date / time / location:
Other commitments and return-home plan:
One process goal unrelated to a payout:

## After play
Each entry or additional purchase actually paid:
Actual total entry cost:
Actual return:
Separate trip costs:
One completed hand or procedural question to revisit:
Next small step, or stop here:

Keep completed records, tickets and identifying documents private.
Prepared with AI assistance. Guide: https://nolankido.com/poker/live-tournament-guide/
''',
'poker-hand-capture': '''# Completed-hand capture

Blank private-use note. Write after the hand, away from active play,
and only where the event permits it. No covert recording or live assistance.

Game / event stage / number of players:
Blinds / ante and how it was posted:
Relevant positions (use labels rather than names):
Starting stacks and when they were measured:
Your cards:

Preflop actions in order (write raises TO and extra amounts to call):
Flop cards and actions:
Turn card and actions:
River card and actions:
Showdown or folds; cards actually shown:
Uncalled wagers returned / pot awarded:

Pot ledger, including blinds and antes:
Known starting and final stacks:
Exact details / estimates / unknowns:
When and how this note was reconstructed:
What you remember thinking then:

Later review question:
Assumptions added for review, not observed facts:
One calculation or source to check:
Details to remove before any public explanation:

Keep the completed copy private. A gap can remain unknown.
Prepared with AI assistance. Guide: https://nolankido.com/poker/recording-hands/
''',
'poker-resource-check': '''# One poker resource, one question

Blank private-use study sheet. Use away from play.
No purchase or completed worksheet is required to read the site.

Question I am trying to answer:
Resource title / publisher / public URL:
Publication or update date, if available:
Date I read it:
Type: rule / calculation / strategy / story / product claim:
The specific claim in my own words:

Game / format / players / positions:
Stacks, ante and action sequence:
Objective: chips / prizes / another stated model:
Observed inputs versus assumptions:
Important mismatch or missing input:

Evidence offered:
One calculation, alternative assumption or official source to check:
What I learned:
What this does not establish:
One next step, or stop here:

For paid tools, separately check current access, renewal and cancellation terms.
Keep completed records private. The site does not receive your answers.
Prepared with AI assistance. Guide: https://nolankido.com/poker/evaluating-poker-advice/
'''
}
for slug, content in SHEETS.items(): put('downloads/' + slug + '.md', content)

cards = ''.join(f'<article class="reader-card"><p class="reader-eyebrow">{"Before and around play" if topic == "live" else "After-play study"}</p><h3><a href="/poker/{slug}/">{title}</a></h3><p>{desc}</p></article>' for slug,title,desc,topic,*_ in GUIDES)
put('_source/poker/live-tournament-guide.html', '''
<section class="section folio-row" aria-labelledby="field-intro"><div class="section-meta"><p class="section-label">Before / Around / After play</p></div><div class="section-content"><h2 class="intro" id="field-intro">Make the unfamiliar parts easier.</h2><p class="section-deck">Understand the event before paying, get comfortable with the day's procedures, and leave with a question worth reviewing. Start with the part you need, not a requirement to read every guide.</p><p>These are practical educational guides, not accounts of Nolan's tournaments or a substitute for the organizer's rules. Watching and learning do not require entering an event.</p><div class="reader-shortcuts"><a href="/poker/first-live-tournament/">First live tournament?</a><a href="/poker/choosing-a-tournament/">Compare an event</a><a href="/poker/tournament-checklists/">Print or copy the checklists</a></div></div></section>
<section class="section folio-row" aria-labelledby="field-routes"><div class="section-meta"><p class="section-label">Choose a route</p></div><div class="section-content"><h2 class="section-title" id="field-routes">Three ways to use the field guide.</h2><div class="viewer-learning-paths"><article><h3>I am considering a first event.</h3><ol><li><a href="/poker/first-live-tournament/">Get oriented.</a></li><li><a href="/poker/choosing-a-tournament/">Read the structure.</a></li><li><a href="/poker/tournament-checklists/#event-planner">Write a small day plan.</a></li></ol><p>Output: an event you understand, or a decision not to enter.</p></article><article><h3>I want fewer surprises on the day.</h3><ol><li><a href="/poker/registration-and-reentry/">Check the entry conditions.</a></li><li><a href="/poker/tournament-day/">Understand the day's transitions.</a></li><li><a href="/poker/table-etiquette/">Recognize common table procedures.</a></li></ol><p>Output: the questions to resolve with staff before they matter.</p></article><article><h3>I have a completed hand to study.</h3><ol><li><a href="/poker/recording-hands/">Preserve a useful note.</a></li><li><a href="/poker/choosing-study-tools/">Choose the right kind of tool.</a></li><li><a href="/poker/evaluating-poker-advice/">Check one explanation.</a></li></ol><p>Output: one checked calculation or a clearly named uncertainty.</p></article></div></div></section>
<section class="section folio-row" aria-labelledby="field-all"><div class="section-meta"><p class="section-label">Seven practical guides</p></div><div class="section-content"><h2 class="section-title" id="field-all">Read the part you need.</h2><div class="reader-grid">''' + cards + '''</div><p>For terminology, use <a href="/poker/glossary/">the glossary</a>. For the action itself, use <a href="/poker/start-here/">the viewer guide</a>. For other publishers, use <a href="/poker/resources/">the external resource directory</a>.</p></div></section>
<section class="section folio-row" aria-labelledby="field-boundaries"><div class="section-meta"><p class="section-label">Keep it useful</p></div><div class="section-content prose"><h2 id="field-boundaries">Preparation does not require more spending.</h2><p>A personal time or spending limit is a ceiling, not a target. Do not rely on a payout to cover the outing or treat an allowed re-entry as an obligation. <a href="https://www.ncpgambling.org/help-treatment/">NCPG's support resources</a> are available separately from poker study.</p><p>Prepared with AI assistance. New guides published October 8, 2026. Worked examples are fictional. Keep completed worksheets private and use study tools away from play.</p><div class="link-row"><a class="text-link" href="/poker/tournament-checklists/">Open printable sheets</a><a class="text-link" href="/poker/study/">Go to the Study Desk</a><a class="text-link" href="/poker/">Back to Poker</a></div></div></section>
''')
put('_source/poker/tournament-checklists.html', '''
<div class="article-body shell prose viewer-guide field-guide"><nav class="viewer-breadcrumb" aria-label="Guide location"><a href="/poker/">Poker</a><span aria-hidden="true"> / </span><a href="/poker/live-tournament-guide/">Field guide</a></nav><p class="article-lead">Three small sheets for before and after play. Copy the text into your notes, download the editable Markdown version, or use your browser's Print command. You can select and print just one sheet where your browser supports it.</p><p>The visible previews and downloads come from the same blank files. No account, form or upload is involved. Keep completed copies private. Ordinary pageview analytics remains described in the <a href="/privacy/">privacy notice</a>.</p>
<h2 id="event-planner">Event and day planner</h2><p>For comparing a possible event and planning the day. Confirm unknown details with the organizer rather than filling them from memory. The <a href="/poker/choosing-a-tournament/">structure-sheet example</a> shows the calculations; <a href="/poker/registration-and-reentry/">the entry guide</a> shows a fictional cost ledger. A plan is not a reason to spend up to its ceiling.</p><p><a href="/downloads/poker-event-planner.md" download>Download the event planner</a></p><pre class="field-sheet">${poker_event_planner}</pre>
<h2 id="hand-capture">Completed-hand capture</h2><p>For preserving one hand after play, away from active action and only where permitted. The <a href="/poker/recording-hands/#worked-note">fictional worked note</a> shows the level of detail that makes a pot checkable. This sheet does not turn unknown cards into known facts.</p><p><a href="/downloads/poker-hand-capture.md" download>Download the hand-capture sheet</a></p><pre class="field-sheet">${poker_hand_capture}</pre>
<h2 id="resource-check">One resource, one question</h2><p>For a single article, video, chart or tool rather than an entire reading backlog. The <a href="/poker/evaluating-poker-advice/#compare-explanations">fictional comparison</a> shows how apparently conflicting advice may answer different questions. Finish with a check or a named uncertainty, not an unsupported confidence score.</p><p><a href="/downloads/poker-resource-check.md" download>Download the resource-check sheet</a></p><pre class="field-sheet">${poker_resource_check}</pre>
<p class="editorial-note">Prepared with AI assistance. Published October 8, 2026. These are optional thinking aids, not live assistance, financial plans or validated strategic recommendations.</p><nav class="article-navigation" aria-label="Continue learning"><a href="/poker/live-tournament-guide/">Read the field guide</a><a href="/poker/study/#creator-workbench">Existing study and episode worksheets</a><a href="/contact/">Send a correction</a></nav></div>
''')

pages_path = ROOT / '_source/pages.json'
pages = json.loads(pages_path.read_text())
for slug,title,desc,topic,level,keywords,*_ in GUIDES:
    pages.append({'id':'poker-'+slug,'path':'/poker/'+slug+'/','title':title,'seo_title':title.rstrip('.')+' | Nolan Kido Poker','description':desc,'kicker':'Poker / '+('Live tournament field guide' if topic=='live' else 'Study resources'),'source':'poker/'+slug+'.html','section':'poker','date':DATE,'updated':DATE,'poker_guide':True})
for slug,title,desc in [('live-tournament-guide','The live tournament field guide.','Seven practical guides for choosing an event, preparing for tournament day, recording completed hands and evaluating study resources.'),('tournament-checklists','Plan the day. Keep the hand. Check the source.','Three printable, copyable and downloadable private-use sheets for event planning, completed-hand capture and evaluating a poker resource.')]:
    pages.append({'id':'poker-'+slug,'path':'/poker/'+slug+'/','title':title,'seo_title':title.rstrip('.')+' | Nolan Kido Poker','description':desc,'kicker':'Poker / Practical preparation','source':'poker/'+slug+'.html','section':'poker','date':DATE,'updated':DATE})
changed_pages={'poker','poker-library','poker-study','poker-resources','poker-start-here','poker-tournament-formats','poker-table-etiquette'}
for page in pages:
    if page['id'] in changed_pages:page['updated']=DATE
pages_path.write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lib_path=S/'library.json'
lib=json.loads(lib_path.read_text())
for slug,title,desc,topic,level,keywords,*_ in GUIDES:lib['entries'].append(dict(slug=slug,title=title,description=desc,topic=topic,level=level,keywords=keywords))
lib_path.write_text(json.dumps(lib,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
replace('_scripts/poker_library.py', "'practice': 'Try a decision',", "'live': 'Live tournament preparation', 'practice': 'Try a decision',")
related={
'first-live-tournament':('choosing-a-tournament','tournament-day'),
'choosing-a-tournament':('registration-and-reentry','tournament-formats'),
'registration-and-reentry':('tournament-day','variance-and-results'),
' tournament-day':('recording-hands','table-etiquette'),
'recording-hands':('reviewing-a-hand','pot-odds-workshop'),
'choosing-study-tools':('evaluating-poker-advice','tournament-equity'),
'evaluating-poker-advice':('choosing-study-tools','decision-lab')}
related = {key.strip(): value for key, value in related.items()}
replace('_scripts/poker_reading.py','NEXT_READS = {','NEXT_READS = {\n'+''.join(f'    {slug!r}: {pair!r},\n' for slug,pair in related.items()))
replace('_scripts/build.py','    values.update(poker_library.supplement(reader_entries))','    values.update(poker_library.supplement(reader_entries))\n    # The on-page and printable previews use the exact downloadable blank files.\n    for slug in ("poker-event-planner", "poker-hand-capture", "poker-resource-check"):\n        values[slug.replace("-", "_")] = text((ROOT / "downloads" / (slug + ".md")).read_text(encoding="utf-8"))')
replace('_scripts/check_live.py',"    assets += ['downloads/' + name + '.md'", "    assets += ['downloads/' + name + '.md' for name in ['poker-event-planner', 'poker-hand-capture', 'poker-resource-check']]\n    assets += ['downloads/' + name + '.md'")

home_new='''<section class="section folio-row" id="field-guide" aria-labelledby="field-guide-title"><div class="section-meta"><p class="section-label">New / Practical preparation</p></div><div class="section-content"><h2 class="section-title" id="field-guide-title">Before the first hand. After the last one.</h2><p class="section-deck">Read a structure sheet, understand registration and re-entry, prepare for the day's logistics, and preserve a completed hand you can actually review. Seven practical guides, with fictional examples and private-use checklists.</p><div class="reader-shortcuts"><a href="/poker/live-tournament-guide/">Explore the field guide</a><a href="/poker/first-live-tournament/">Prepare for a first tournament</a><a href="/poker/choosing-study-tools/">Choose a study tool</a><a href="/poker/tournament-checklists/">Print or copy the sheets</a></div></div></section>\n'''
replace('_source/poker/home.html','<section class="section folio-row" id="watch"',home_new+'<section class="section folio-row" id="watch"')
replace('_source/poker/library.html','<p>Looking beyond this site?', '<p>Preparing for an event rather than watching one? The <a href="/poker/live-tournament-guide/">live tournament field guide</a> connects seven practical guides and <a href="/poker/tournament-checklists/">printable planning sheets</a>.</p><p>Looking beyond this site?')
replace('_source/poker/study.html','<section class="section folio-row" id="study-routes"','<section class="section folio-row" aria-labelledby="field-study-title"><div class="section-meta"><p class="section-label">Before and after play</p></div><div class="section-content prose"><h2 id="field-study-title">A useful note starts before the analysis.</h2><p>The <a href="/poker/live-tournament-guide/">live tournament field guide</a> covers event preparation and day-to-day procedures. After play, use <a href="/poker/recording-hands/">the hand-capture guide</a> to preserve the facts, <a href="/poker/choosing-study-tools/">the tool guide</a> to match a question to a calculation, and <a href="/poker/evaluating-poker-advice/">the advice guide</a> to inspect an explanation.</p><p><a href="/poker/tournament-checklists/">Copy or print the three new blank planning sheets</a>. The existing hand-review, session and episode worksheets remain below.</p></div></section>\n<section class="section folio-row" id="study-routes"')
resources_path=S/'resources.html'
resources=resources_path.read_text()
needle='<section class="section folio-row" id="review-policy"'
assert resources.count(needle)==1
resources_path.write_text(resources.replace(needle,'<section class="section folio-row" aria-labelledby="resource-choice-title"><div class="section-meta"><p class="section-label">Put a resource to use</p></div><div class="section-content prose"><h2 id="resource-choice-title">Choose by the question, not the biggest claim.</h2><p>The <a href="/poker/choosing-study-tools/">study-tool guide</a> distinguishes equity calculators, ICM models, solvers and trainers. The <a href="/poker/evaluating-poker-advice/">advice-reading guide</a> helps compare articles, videos and charts without overlooking their assumptions. Try one <a href="/poker/tournament-checklists/#resource-check">private resource-check sheet</a> rather than building a reading backlog.</p><p>Choosing an actual event? Start with the <a href="/poker/choosing-a-tournament/">structure-sheet guide</a>, then confirm the details with the <a href="#events">official organizer</a>.</p></div></section>\n'+needle),encoding='utf-8')
target=ROOT/'_source/poker/start-here.html'
txt=target.read_text(); marker='<div class="section-content prose">'
if marker not in txt:marker='<div class="section-content">'
assert marker in txt
target.write_text(txt.replace(marker,marker+'<p>Thinking of attending rather than only watching? Start with the <a href="/poker/live-tournament-guide/">live tournament field guide</a> for event choice, registration and practical preparation.</p>',1),encoding='utf-8')
for slug, link in [('tournament-formats','<p>Comparing actual events? Use <a href="/poker/choosing-a-tournament/">the structure-sheet guide</a> to compare stack depth, costs and schedule before paying.</p>'),('table-etiquette','<p>Preparing to sit down yourself? The <a href="/poker/first-live-tournament/">first live tournament guide</a> covers arrival, registration and the procedural questions worth asking.</p>')]:
    replace('_source/poker/'+slug+'.html','  <section class="viewer-sources"',link+'\n  <section class="viewer-sources"')
replace('_tests/test_labs_expansion.py','        self.assertEqual(len(self.entries), 24)',"        self.assertEqual(len(self.entries), len([p for p in self.pages if p.get('poker_guide')]) + 1)")
replace('_tests/test_poker_resources.py','        self.assertEqual(len(indexed), 24)',"        self.assertEqual(len(indexed), len([p for p in build.public_pages() if p.get('poker_guide')]) + 1)")

put('assets/poker-fieldguide.css', '''/* Only the printable-sheet page loads these preview and print rules. */
.field-sheet { box-sizing:border-box; max-width:100%; white-space:pre-wrap; overflow-wrap:anywhere; padding:20px; border:1px solid var(--line-dark); background:var(--panel); font:.87rem/1.7 var(--mono); }
@media print { .field-sheet { padding:0; border:0; background:none; font-size:10pt; line-height:1.4; break-inside:auto; } }
''')
replace('_scripts/build.py', "            if p['id'] == 'poker-resources':", '''            if p['id'] == 'poker-tournament-checklists':
                sheets_version = hashlib.sha256((ROOT / 'assets/poker-fieldguide.css').read_bytes()).hexdigest()[:12]
                extra += f'\\n  <link rel="stylesheet" href="/assets/poker-fieldguide.css?v={sheets_version}">'
            if p['id'] == 'poker-resources':''')
replace('_scripts/check_live.py', "    assets = ['assets/poker-resources.css'", "    assets = ['assets/poker-fieldguide.css', 'assets/poker-resources.css'")
print('Prepared seven guides, two hubs and three worksheets. Run the normal build and tests before publication.')
