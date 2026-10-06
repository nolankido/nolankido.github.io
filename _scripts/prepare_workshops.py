"""One-time, branch-only integration. Remove before merging the release."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def replace_once(path, old, new):
    file = ROOT / path
    content = file.read_text(encoding='utf-8')
    if content.count(old) != 1:
        raise ValueError(f'{path}: expected one target, found {content.count(old)}')
    file.write_text(content.replace(old, new), encoding='utf-8')

entries = [
    ('pot-odds-workshop', 'The price is exact. The range usually is not.', 'Pot Odds Workshop', 'Price calls and raises, distinguish draw probabilities from equity, and test the assumptions behind a bluff or call.'),
    ('short-stack-decisions', 'A short stack is a situation, not a chart.', 'Short-Stack Study Workshop', 'Record stacks, antes, action trees and tournament objectives before comparing short-stack decisions or push/fold references.'),
    ('tournament-equity', 'When more chips are not enough.', 'Tournament Equity and ICM', 'A checkable three-player ICM example explains prize equity, risk premiums and why gaining chips can lower expected payout.'),
    ('range-combinations', 'Count the hands. Then ask how they got here.', 'Range Combinations Workshop', 'Count physical combinations, remove known cards, weight betting frequencies and test a fictional river range.'),
    ('variance-and-results', 'Results deserve context.', 'Tournament Variance and Results', 'Separate tournament ROI, trip costs, sample uncertainty and decision evidence with worked accounting and probability examples.'),
    ('hand-to-vlog', 'Give the viewer a question worth staying for.', 'From Hand Notes to a Poker Vlog', 'An editing workbench for honest hand reconstruction, clear graphics, useful narration and poker episode companion pages.'),
    ('practice-room', 'Twelve checks. One useful repair.', 'Poker Study Practice Room', 'Twelve answer-reveal exercises on pot odds, ranges, short stacks, ICM, results and honest poker storytelling.'),
]
manifest_file = ROOT / '_source/pages.json'
pages = json.loads(manifest_file.read_text(encoding='utf-8'))
for slug, title, seo, description in entries:
    if any(p['path'] == f'/poker/{slug}/' for p in pages):
        raise ValueError(f'Route already exists: {slug}')
    pages.append({'id': 'poker-' + slug, 'path': f'/poker/{slug}/', 'title': title,
                  'seo_title': seo + ' | Nolan Kido', 'description': description,
                  'kicker': 'Poker / After-play study', 'source': f'poker/{slug}.html',
                  'section': 'poker', 'date': '2026-10-06', 'updated': '2026-10-06',
                  'poker_guide': True})
for page in pages:
    if page['id'] == 'poker-study':
        page['description'] = 'Seven after-play workshops, twelve practice questions, a five-session study cycle and private-use records for tournament study and poker vlog planning.'
        page['updated'] = '2026-10-06'
    elif page['id'] == 'poker':
        page['description'] = 'Tournament poker, beginner viewer guides, after-play study workshops, hand reviews and a practical poker vlog workbench by Nolan Kido.'
        page['updated'] = '2026-10-06'
    elif page['id'] == 'poker-start-here':
        page['updated'] = '2026-10-06'
manifest_file.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

replace_once('_source/poker/home.html', 'Seven deeper guides, 48 glossary entries, and worked examples.', 'Thirteen topic guides, 48 glossary entries, and worked examples.')
replace_once('_source/poker/home.html', '>All seven guides</a>', '>Browse the viewer library</a>')
replace_once('_source/poker/home.html', 'Simple records to keep a useful question from getting lost.', 'Workshops, practice questions, and useful records for after play.')
replace_once('_source/poker/home.html', 'The study desk has editable hand-review and session-debrief sheets, with instructions and blank previews.', 'The study desk combines hand-review and session records with short-stack, results, study-cycle, and episode-planning worksheets.')
home_addition = '''<section class="section folio-row" id="after-play" aria-labelledby="after-play-title">
  <div class="section-meta"><p class="section-label">New / After-play workshops</p></div>
  <div class="section-content"><h2 class="section-title" id="after-play-title">Study the decision. Then tell the story.</h2><p class="section-deck">Go beyond identifying the winning hand. Price a call, inspect a short-stack reference, count a weighted range, and see why tournament chips and prizes can disagree. Turn what you learn into a clearer account rather than a more confident guess.</p><div class="poker-paths" role="group" aria-label="After-play study shortcuts"><a href="/poker/short-stack-decisions/"><span class="note-category">Tournament study</span><strong>Start with the right spot</strong><span>Stacks, antes, action history and the assumptions behind a chart.</span></a><a href="/poker/practice-room/"><span class="note-category">Try it yourself</span><strong>Twelve questions to check</strong><span>Work an example, reveal the explanation, and name one repair.</span></a><a href="/poker/hand-to-vlog/"><span class="note-category">Creator workbench</span><strong>From hand note to story</strong><span>Reliable reconstruction, readable graphics and honest narration.</span></a></div><div class="link-row"><a class="text-link" href="/poker/study/#workshops">Explore all seven workshops</a><a class="text-link" href="/poker/study/#study-routes">Choose a study route</a></div><p class="small-copy resource-help">Use away from the table. Fictional teaching examples, not solved ranges or personal tournament results.</p></div>
</section>
'''
replace_once('_source/poker/home.html', '<section class="section folio-row" id="watch"', home_addition + '<section class="section folio-row" id="watch"')

replace_once('_source/poker/study.html', 'These two records separate the details you have from the question you want to investigate.', 'Start with one question, follow a workshop, and keep only the record that helps you investigate it. The original hand and session sheets remain below.')
replace_once('_source/poker/study.html', '<nav class="poker-jump" aria-label="Choose a worksheet">', '<nav class="poker-jump" aria-label="Study desk shortcuts"><a href="#study-routes">Choose a route</a><a href="#workshops">Seven workshops</a><a href="#creator-workbench">Creator workbench</a>')
study_addition = '''<section class="section folio-row" id="study-routes" aria-labelledby="study-routes-title"><div class="section-meta"><p class="section-label">Choose one question</p></div><div class="section-content"><h2 class="section-title" id="study-routes-title">Three routes through the work.</h2><p class="section-deck">You do not need to read everything. Choose the route closest to your current question, produce one small output and stop there.</p><div class="viewer-learning-paths"><article><h3>I have a hand to review.</h3><ol><li><a href="/poker/pot-odds-workshop/">Reconstruct its price.</a></li><li><a href="/poker/range-combinations/">Inspect the assumed range.</a></li><li><a href="#hand-review">Record one conditional conclusion.</a></li></ol></article><article><h3>I am studying tournaments.</h3><ol><li><a href="/poker/short-stack-decisions/">Define the short-stack state.</a></li><li><a href="/poker/tournament-equity/">Separate chips from prize value.</a></li><li><a href="/poker/practice-room/#spot-check">Test the inputs before the answer.</a></li></ol></article><article><h3>I am making an episode.</h3><ol><li><a href="/poker/hand-to-vlog/">Choose the question and evidence.</a></li><li><a href="/poker/variance-and-results/">Put the result in context.</a></li><li><a href="#creator-workbench">Plan a small, honest release.</a></li></ol></article></div><p class="small-copy resource-help">New to the action itself? Start with the <a href="/poker/start-here/#viewer-library">beginner viewer library</a>. The workshops assume the basic hand, betting and position vocabulary.</p></div></section>
<section class="section folio-row" id="workshops" aria-labelledby="workshops-title"><div class="section-meta"><p class="section-label">Read / Work / Check</p></div><div class="section-content"><h2 class="section-title" id="workshops-title">Seven after-play workshops.</h2><p class="section-deck">Worked examples with visible assumptions, not a collection of unexplained hand recommendations. The practice room turns the reading into twelve questions you can answer before revealing an explanation.</p><div class="viewer-library-grid">
<article><p class="note-category">01 / Price the decision</p><h3><a href="/poker/pot-odds-workshop/">Pot odds without double-counting</a></h3><p>Call prices, raises, draw probabilities and zero-equity bluffs. Leave with a correct pot ledger and a named uncertainty.</p></article>
<article><p class="note-category">02 / Match the state</p><h3><a href="/poker/short-stack-decisions/">Short stacks beyond the chart</a></h3><p>Starting stacks, chips behind, antes, action families and reference compatibility. No unsupported shove ranges.</p></article>
<article><p class="note-category">03 / Choose the objective</p><h3><a href="/poker/tournament-equity/">Chips, prizes and ICM</a></h3><p>Audit a three-player example where a chip-profitable gamble reduces modeled prize equity.</p></article>
<article><p class="note-category">04 / Count the range</p><h3><a href="/poker/range-combinations/">Combinations and betting weights</a></h3><p>Remove known cards, count candidate hands and see why a possible bluff is not a full-weight bluff.</p></article>
<article><p class="note-category">05 / Read the record</p><h3><a href="/poker/variance-and-results/">Variance and honest results</a></h3><p>Separate tournament ROI, trip costs, concentrated returns and evidence about decisions.</p></article>
<article><p class="note-category">06 / Explain the hand</p><h3><a href="/poker/hand-to-vlog/">From hand note to poker vlog</a></h3><p>A practical workflow for reconstruction, narration, graphics, captions and a useful companion page.</p></article>
<article><p class="note-category">07 / Check understanding</p><h3><a href="/poker/practice-room/">The twelve-question practice room</a></h3><p>Reveal one answer at a time. Find a specific repair without turning the result into a skill score.</p></article>
</div><p class="small-copy resource-help">All worked hands and financial examples in these workshops are fictional. The site adds no answer forms or at-table assistance.</p></div></section>
<section class="section folio-row" id="creator-workbench" aria-labelledby="creator-workbench-title"><div class="section-meta"><p class="section-label">Use it privately</p></div><div class="section-content prose"><h2 id="creator-workbench-title">A smaller study cycle and a clearer episode.</h2><p><strong>For ongoing study:</strong> the five-session cycle moves from pot arithmetic to ranges, input compatibility, prize value and explanation. Each session has a small version for a limited-energy day. These are sessions, not mandatory consecutive days.</p><p><strong>For an episode:</strong> start with one coherent question and one reliably documented hand. Keep recorded action, remembered thoughts and later analysis separate. Raw notes, filenames and completed worksheets belong outside this public repository.</p><ul><li><a href="/downloads/poker-study-cycle.md" download>Five-session study cycle</a>: a reading order, exercises and one output per session.</li><li><a href="/downloads/poker-short-stack-record.md" download>Short-stack input record</a>: the information needed before a chart comparison.</li><li><a href="/downloads/poker-results-review.md" download>Results and review sheet</a>: entry costs, returns, trip costs and a separate decision queue.</li><li><a href="/downloads/poker-episode-plan.md" download>Episode planning sheet</a>: selection, evidence, graphics, rights and release checks.</li></ul><p>These are blank, editable Markdown files. Download only what helps, open it in a text editor or notes app, and keep the completed copy private. The website does not receive your answers. Ordinary pageview analytics remains described in the <a href="/privacy/">privacy notice</a>.</p></div></section>
'''
replace_once('_source/poker/study.html', '<section class="section folio-row" id="hand-review"', study_addition + '<section class="section folio-row" id="hand-review"')
start = ROOT / '_source/poker/start-here.html'
start.write_text(start.read_text(encoding='utf-8') + '''\n<section class="section folio-row" id="after-play-workshops" aria-labelledby="after-play-workshops-title"><div class="section-meta"><p class="section-label">Ready to study?</p></div><div class="section-content"><h2 class="section-title" id="after-play-workshops-title">Move from following the action to checking the reasoning.</h2><p class="section-deck">The after-play workshops cover pot odds, short-stack inputs, combinations, tournament equity, results and poker storytelling. Keep the beginner library as a reference rather than feeling you need to memorize it first.</p><div class="link-row"><a class="button" href="/poker/study/#workshops">Explore the study workshops</a><a class="text-link" href="/poker/practice-room/">Try twelve self-check questions</a></div></div></section>\n''', encoding='utf-8')

assets = ['poker-short-stack-record.md', 'poker-results-review.md', 'poker-episode-plan.md', 'poker-study-cycle.md']
replace_once('_scripts/check_live.py', '    assets = [', '    assets = [' + ', '.join(repr('downloads/' + name) for name in assets) + ', ')
readme = ROOT / 'README.md'
readme.write_text(readme.read_text(encoding='utf-8') + '''\n## After-play workshops\n\nThe Poker study desk now connects seven substantial workshops, twelve self-check\nexercises and four new private-use worksheets. See `POKER_WORKSHOPS_RELEASE.md`.\nAll examples are fictional and the existing publishing approval workflow remains\nin place. Run `python _tests/workshops_browser.py` for the targeted disclosure and\nreading-flow checks. The Technology-first gateway and Umami configuration are\nunchanged.\n''', encoding='utf-8')
