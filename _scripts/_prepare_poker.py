#!/usr/bin/env python3
"""One-time, fail-closed preparation of the approved personal-home and poker release."""
from pathlib import Path
import json
import textwrap

ROOT = Path(__file__).resolve().parents[1]

def write(path, content):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(textwrap.dedent(content).lstrip('\n'), encoding='utf-8', newline='')

def replace(path, old, new):
    target = ROOT / path
    source = target.read_text(encoding='utf-8')
    if source.count(old) != 1:
        raise RuntimeError(f'Expected exactly one reviewed anchor in {path}: {old[:80]!r}')
    target.write_text(source.replace(old, new), encoding='utf-8', newline='')

write('_source/home.html', '''
<section class="hero folio-row brand-home" aria-labelledby="home-title">
  <div class="section-meta"><p class="section-label">Personal home</p></div>
  <div class="section-content">
    <div class="hero-heading"><h1 id="home-title">Nolan Kido</h1></div>
    <p class="hero-copy brand-statement">Poker, technology,<br>and creative work.</p>
    <p class="hero-caption">${intro}</p>
  </div>
</section>
<section class="section folio-row destination-section" aria-labelledby="destinations-title">
  <div class="section-meta"><p class="section-label">Explore</p></div>
  <div class="section-content">
    <h2 class="visually-hidden" id="destinations-title">Choose a direction</h2>
    <div class="destination-grid">
      <a class="destination destination-poker" href="/poker/" aria-labelledby="poker-destination-title poker-destination-action" aria-describedby="poker-destination-description">
        <span class="destination-label">01 / At the table &amp; beyond</span>
        <h3 id="poker-destination-title">Poker</h3>
        <p id="poker-destination-description">Tournament play, the decisions behind the hands, and the work of getting better.</p>
        <span class="destination-action" id="poker-destination-action">Explore poker <span aria-hidden="true">↗</span></span>
      </a>
      <a class="destination destination-notes" href="/notes/" aria-labelledby="notes-destination-title notes-destination-action" aria-describedby="notes-destination-description">
        <span class="destination-label">02 / A wider lens</span>
        <h3 id="notes-destination-title">Notes</h3>
        <p id="notes-destination-description">Selected writing on technology, decisions, learning, and making things.</p>
        <span class="destination-action" id="notes-destination-action">Browse notes <span aria-hidden="true">↗</span></span>
      </a>
    </div>
  </div>
</section>
<section class="section folio-row home-connection" aria-labelledby="connection-title">
  <div class="section-meta"><p class="section-label">The person behind it</p></div>
  <div class="section-content"><h2 class="visually-hidden" id="connection-title">About and contact</h2>
    <p>A little more about me, or a place to start a conversation.</p>
    <div class="link-row"><a class="text-link" href="/about/">About Nolan <span aria-hidden="true">→</span></a><a class="text-link" href="/contact/">Get in touch <span aria-hidden="true">→</span></a></div>
  </div>
</section>
''')

write('_source/poker/home.html', '''
<section class="section folio-row poker-introduction" aria-labelledby="poker-intro-title">
  <div class="section-meta"><p class="section-label">Play / Study / Story</p></div>
  <div class="section-content">
    <h2 class="intro" id="poker-intro-title">The game, the decisions, and the work between tournaments.</h2>
    <p class="section-deck">I play tournament poker. I am interested in what happens at the table, how to learn from it afterward, and how to tell the story clearly.</p>
    <p class="poker-lede">This is the poker side of my site: a place to look past the final result and spend time with the choices behind it.</p>
    <div class="poker-principles">
      <div><h3>Play</h3><p>The situation matters. A hand belongs to a table, a stack, and a moment in a tournament.</p></div>
      <div><h3>Study</h3><p>Separate what was known at the table from what became clear in the review.</p></div>
      <div><h3>Story</h3><p>Make the action understandable without pretending the uncertainty was never there.</p></div>
    </div>
  </div>
</section>
<section class="section folio-row" aria-labelledby="poker-feature-title">
  <div class="section-meta"><span class="section-number" aria-hidden="true">01</span><p class="section-label">Start here</p></div>
  <div class="section-content poker-feature">
    <p class="note-category">A practical hand-review guide</p>
    <h2 class="section-title" id="poker-feature-title">Review a hand,<br>not just the result.</h2>
    <p class="section-deck">Reconstruct the action, pause at one decision, and keep your original thinking separate from the review. A worked fictional hand shows the process.</p>
    <a class="button" href="/poker/reviewing-a-hand/">Read the hand-review guide <span aria-hidden="true">→</span></a>
  </div>
</section>
<section class="section folio-row" id="study" aria-labelledby="poker-study-title">
  <div class="section-meta"><span class="section-number" aria-hidden="true">02</span><p class="section-label">Between sessions</p></div>
  <div class="section-content">
    <h2 class="section-title" id="poker-study-title">A useful record beats a perfect memory.</h2>
    <p class="section-deck">Save the details you have, mark the ones you do not, and leave yourself one question to study. The blank hand-review sheet is yours to edit privately.</p>
    <div class="link-row"><a class="button" href="/downloads/poker-hand-review.md" download>Download the review sheet <span aria-hidden="true">↓</span></a><a class="text-link" href="/poker/reviewing-a-hand/#review-sheet">See how to use it <span aria-hidden="true">→</span></a></div>
    <p class="small-copy resource-help">Editable plain text (.md). No account or email required. Your completed sheet stays with you; this site does not collect its contents.</p>
  </div>
</section>
<section class="section folio-row" aria-labelledby="poker-connect-title">
  <div class="section-meta"><p class="section-label">Conversation</p></div>
  <div class="section-content"><h2 class="section-title" id="poker-connect-title">A hand, a question, a different perspective.</h2><p class="section-deck">A poker conversation does not need a pitch. Questions about the guide, corrections, and ideas for a story are welcome.</p><a class="text-link" href="/contact/">Get in touch <span aria-hidden="true">→</span></a></div>
</section>
''')

write('_source/poker/reviewing-a-hand.html', '''
<div class="article-body shell prose poker-guide">
  <p class="article-lead">A useful hand review starts before the result. Preserve the situation, choose one decision, and ask what the available information actually supported.</p>
  <p>This is a recording and study method, not a chart telling you which action to take. Use it after play. The example below is fictional and deliberately stops before the decision is resolved.</p>
  <h2>First, preserve the situation.</h2>
  <p>Write down the game, positions, blinds and antes, relevant stacks, and action in order. Record bet sizes as total amounts when a player raises. Mark an estimate as an estimate rather than making a remembered number look exact.</p>
  <p>For a tournament hand, add any payout or stage information relevant to the question. Keep an observation such as “the player raised twice in the last orbit” separate from an interpretation such as “the player is aggressive.” Do not include another person's identifying details in a public example without permission.</p>
  <h2>Pause at one decision.</h2>
  <div class="fictional-hand" aria-labelledby="example-title">
    <p class="note-category">Fictional example / No-limit hold'em</p>
    <h3 id="example-title">Facing a flop raise</h3>
    <p>Six-handed play, no antes, and 30 big blinds effective at the start. Blinds are 0.5 and 1 big blind (BB). Everyone folds to the button.</p>
    <figure class="hand-illustration">
      <div class="card-groups" aria-hidden="true">
        <div><p class="card-group-label">Button</p><div class="card-row"><span class="playing-card">K♠</span><span class="playing-card">Q♠</span></div></div>
        <div><p class="card-group-label">Flop</p><div class="card-row"><span class="playing-card card-red">Q♦</span><span class="playing-card">8♣</span><span class="playing-card card-red">3♥</span></div></div>
      </div>
      <figcaption>The button holds king of spades and queen of spades. The flop is queen of diamonds, eight of clubs, three of hearts.</figcaption>
    </figure>
    <dl class="hand-facts">
      <div><dt>Before the flop</dt><dd>The button raises to 2.5 BB. The small blind folds. The big blind calls. The pot is 5.5 BB: 2.5 + 2.5 + 0.5.</dd></div>
      <div><dt>On the flop</dt><dd>The big blind checks. The button bets 2 BB. The big blind raises to 7 BB total.</dd></div>
      <div><dt>The decision</dt><dd>The pot is now 14.5 BB: 5.5 + 2 + 7. The button faces 5 BB more to call, not 7 BB.</dd></div>
    </dl>
    <p><strong>Stop here.</strong> There is no supplied opponent hand or eventual result. The exercise is to record the decision accurately, not to infer a solved answer from the example.</p>
  </div>
  <h2>Separate the record from the interpretation.</h2>
  <p>The board, recorded stacks, and bet sizes describe the situation. The opponent's possible hands, reasons for raising, and likely later actions are interpretations. Write those in a separate paragraph, together with what would support or weaken them.</p>
  <p>In the fictional hand, you might ask what hands the big blind could raise for value and what bluffs are plausible. That is a study question, not evidence that a particular range is correct. If you cannot justify an assumption, leave it visible as an unknown.</p>
  <h2>Compare the alternatives before choosing a verdict.</h2>
  <p>For this decision, describe what would make folding, calling, or reraising reasonable. State the assumptions each option relies on. A strong review may conclude that more than one action is defensible, or that the missing information prevents a confident judgment.</p>
  <p>A calculation or study tool should answer a stated question under stated inputs. Record those inputs and its limits. Do not turn a rough reconstruction into an exact-looking strategy claim, or treat a tool's output as a faithful model of the hand without checking.</p>
  <h2>Keep the result in its own paragraph.</h2>
  <p>In a real review, save your best recollection of what you thought at the table before writing the later analysis. Do not rewrite that account to match what you now believe.</p>
  <p>The outcome belongs in the record, but it does not replace the analysis. Ask whether the decision used the information available at the time and whether an avoidable omission affected it. A good outcome is not, on its own, a complete defense of the process.</p>
  <h2 id="review-sheet">Leave one useful next step.</h2>
  <p>Choose a question small enough to investigate: reconstruct the pot, check a remembered stack, compare explicit range assumptions, or review one decision with a study partner. Save the answer next to the original record rather than replacing it.</p>
  <p>The blank sheet follows this sequence: situation, action, decision, original thinking, later review, result, and next step. Download it and open it in a text editor or notes app. In a short session, just record the situation and the unanswered question.</p>
  <div class="link-row"><a class="button" href="/downloads/poker-hand-review.md" download>Download the review sheet <span aria-hidden="true">↓</span></a><a class="text-link" href="/notes/decision-quality/">Read about decision quality <span aria-hidden="true">→</span></a></div>
  <p class="small-copy resource-help">Editable plain text (.md), for your own private use. This is a thinking aid, not a validated assessment or a promise of improved results.</p>
  <p class="editorial-note">Published October 5, 2026. Prepared with AI assistance. The hand and all its numbers are fictional. No personal tournament result, solver validation, or optimal strategy is claimed.</p>
  <nav class="article-navigation" aria-label="After the hand-review guide"><a href="/poker/">Back to poker</a><a href="/contact/">Send a question or correction</a></nav>
</div>
''')

write('downloads/poker-hand-review.md', '''
# Poker hand review

A private, editable record for study after play. A thinking aid, not a solved strategy recommendation.
Keep other people's identifying information out of any copy you share.

## 1. Situation
- Game and tournament context:
- Stage or payout information relevant to the question:
- Blinds and antes:
- Positions and relevant starting stacks:
- Your cards and the board:
- Which details are exact, approximate, or unknown?

## 2. Action
Write the action in order. For a raise, distinguish the total bet from the extra amount.
- Preflop:
- Flop:
- Turn:
- River:
- Pot and amount to call at the selected decision:

## 3. The decision
- The one choice being reviewed:
- Available alternatives:
- Observations known at the time:
- Interpretations or assumptions, kept separate:

## 4. What you thought at the table
Write this before the later review. Mark uncertain recollections. Do not rewrite it afterward.

## 5. What you think after reviewing
- What supports or weakens each alternative?
- Which assumptions matter most?
- What is still unknown?
- Any study tool, exact inputs, and limits of its relevance:
- What changed in your thinking, and why?

## 6. Result, recorded separately
What happened? What does it establish, and what does it not establish?

## 7. One next step
- One question to investigate:
- A small action for the next study session:
- Later follow-up, without replacing the original record:

For a shorter review, complete only the situation and the unanswered question.
Guide: https://nolankido.com/poker/reviewing-a-hand/
''')

write('_source/about.html', '''
<section class="section"><div class="shell editorial-grid"><div class="section-meta"><h2 class="section-label">An introduction</h2></div><div class="section-content prose">
<p class="intro">${intro}</p>
<p>My interests connect poker, technology, and creative work. I like the point where a difficult idea becomes understandable, a rough version becomes useful, or a familiar question needs another look.</p>
<h2>At the table and away from it.</h2>
<p>Tournament poker brings play and study together. The <a href="/poker/">poker section</a> is a place for the decisions behind the hands and the work of reviewing them, with room for visual storytelling as well as analysis.</p>
<h2>A wider lens.</h2>
<p>Building a tool and explaining an idea ask different things of you. One has to work for an actual task. The other has to make sense to someone who does not already share your assumptions. I am interested in both.</p>
<p>The <a href="/notes/">Notes collection</a> looks more broadly at technology, decisions, learning, and making things. A few <a href="/resources/">practical resources</a> accompany the writing.</p>
<p>Not every interest needs to become a public project. This site is a selection, not a record of everything I do.</p>
<p>For introductions, there is a <a href="/bio/">short biography</a>. For a question, a different perspective, or a simple hello, <a href="/contact/">get in touch</a>.</p>
</div></div></section>
''')

write('assets/hubs.css', '''
/* Personal gateway and poker section. The approved base design stays unchanged. */
.brand-home { padding-bottom: 32px; }
.brand-home .hero-heading { padding-bottom: 24px; }
.brand-home .brand-statement { max-width: 800px; font-size: clamp(1.9rem, 3.5vw, 3rem); line-height: 1.2; margin-top: 4px; }
.brand-home .hero-caption { max-width: 640px; margin-bottom: 0; }
.destination-section { padding-block: 30px 42px; }
.destination-grid { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr); gap: 20px; }
.destination { display: flex; flex-direction: column; min-width: 0; padding: 30px; border: 1px solid var(--line-dark); text-decoration: none; }
.destination h3 { font-size: clamp(2rem, 4vw, 3.5rem); margin: 22px 0 16px; }
.destination p { font: 1.1rem/1.6 var(--serif); max-width: 33ch; margin-bottom: 28px; }
.destination-label { font: .68rem/1.6 var(--mono); text-transform: uppercase; }
.destination-action { display: flex; justify-content: space-between; align-items: center; gap: 15px; margin-top: auto; padding-top: 16px; border-top: 1px solid currentColor; font: 500 .9rem/1.5 var(--sans); }
.destination-action > span { font-size: 1.4rem; }
.destination-poker { background: var(--green); color: var(--paper-light); border-top: 4px solid var(--red); }
.destination-notes { background: var(--panel); }
.destination:hover h3, .destination:focus-visible h3 { text-decoration: underline; text-underline-offset: .15em; }
.destination:focus-visible { outline: 3px solid var(--red); outline-offset: 4px; }
.home-connection { padding-block: 28px 36px; }
.home-connection p { font: 1.1rem/1.6 var(--serif); margin-bottom: 12px; }
.subsite-bar { border-bottom: 1px solid var(--line); background: var(--panel); }
.subsite-bar .shell { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px 20px; padding-block: 8px; }
.subsite-name { font: 500 .7rem/1.5 var(--mono); text-transform: uppercase; }
.subsite-links { display: flex; flex-wrap: wrap; gap: 8px 24px; }
.subsite-links a { display: inline-flex; align-items: center; min-height: 44px; font: .8rem/1.5 var(--sans); }
.subsite-links a[aria-current] { font-weight: 700; text-decoration-color: var(--red); }
.poker-introduction { padding-top: 24px; }
.poker-introduction .intro { font-family: var(--serif); font-weight: 400; }
.poker-lede { max-width: 680px; font: 1.1rem/1.65 var(--serif); }
.poker-principles { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; margin-top: 32px; }
.poker-principles > div { border-top: 2px solid var(--line-dark); padding-top: 18px; min-width: 0; }
.poker-principles h3 { font-size: 1.35rem; margin-bottom: 10px; }
.poker-principles p { font: 1rem/1.65 var(--serif); margin: 0; }
.poker-feature { padding: 30px; background: var(--panel); border-left: 3px solid var(--red); }
.resource-help { margin-top: 18px; max-width: 640px; }
.fictional-hand { margin-block: 28px; padding: 26px; background: var(--panel); border: 1px solid var(--line-dark); }
.fictional-hand h3 { margin-bottom: 18px; }
.hand-illustration { margin: 24px 0; }
.card-groups { display: flex; flex-wrap: wrap; gap: 24px 32px; }
.card-group-label { font: .7rem/1.5 var(--mono); text-transform: uppercase; margin-bottom: 10px; }
.card-row { display: flex; flex-wrap: wrap; gap: 8px; }
.playing-card { display: grid; place-items: center; width: 52px; height: 72px; border: 1px solid var(--line-dark); border-radius: 3px; background: var(--paper-light); color: var(--basalt); font: 700 1.45rem/1.2 var(--sans); }
.card-red { color: var(--red); }
.hand-illustration figcaption { margin-top: 16px; font: .85rem/1.65 var(--sans); }
.hand-facts { margin: 24px 0; }
.hand-facts > div { border-top: 1px solid var(--line-dark); padding: 14px 0; }
.hand-facts dt { font: 600 .85rem/1.5 var(--sans); margin-bottom: 5px; }
.hand-facts dd { margin: 0; }
.poker-guide .link-row { align-items: flex-start; }
@media (max-width: 760px) {
  .destination-grid { grid-template-columns: minmax(0, 1fr); }
  .destination { padding: 24px; }
  .destination h3 { margin-top: 16px; }
  .destination p { max-width: 46ch; }
  .poker-principles { grid-template-columns: minmax(0, 1fr); gap: 22px; }
  .poker-feature { padding: 24px; }
  .subsite-bar .shell { align-items: flex-start; flex-direction: column; gap: 0; }
  .subsite-links { gap: 6px 20px; }
  .fictional-hand { padding: 18px; }
}
@media print {
  .subsite-bar { display: none; }
  .destination, .poker-feature, .fictional-hand { background: white; color: black; }
  .playing-card { color: black; background: white; }
}
''')

write('_scripts/poker_navigation.py', '''
"""Small local navigation for the poker section; no client-side routing."""
from html import escape


def section_navigation(page: dict) -> str:
    if not page['path'].startswith('/poker/'):
        return ''
    links = []
    for route, label in [('/poker/', 'Overview'), ('/poker/reviewing-a-hand/', 'Hand review'), ('/poker/#study', 'Study')]:
        current = ' aria-current="page"' if page['path'] == route else ''
        links.append(f'<a href="{escape(route, quote=True)}"{current}>{label}</a>')
    return ('<div class="subsite-bar"><div class="shell"><span class="subsite-name">Nolan Kido / Poker</span>'
            '<nav class="subsite-links" aria-label="Poker section">' + ''.join(links) + '</nav></div></div>')
''')

site_path = ROOT / '_source/site.json'
site = json.loads(site_path.read_text(encoding='utf-8'))
site.update({
    'tagline': 'Poker, technology, and creative work.',
    'intro': 'I play tournament poker, build tools, and explore ideas through writing and visual storytelling.',
    'bio_short': 'Nolan Kido plays tournament poker and builds tools. His website connects poker, technology, and creative work, with a dedicated poker section and selected general writing.',
    'bio_long': 'Nolan Kido plays tournament poker, builds tools, and explores ideas through writing and visual storytelling. His website is a personal home with a dedicated poker section and a broader collection of notes on technology, decisions, learning, and making things. The poker section focuses on the choices behind the hands and the work of reviewing them. The site is a selection of interests and public material, not a record of everything he does.'
})
site_path.write_text(json.dumps(site, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
manifest_path = ROOT / '_source/pages.json'
pages = json.loads(manifest_path.read_text(encoding='utf-8'))
for page in pages:
    if page['id'] == 'home':
        page.update(seo_title='Nolan Kido | Poker, Technology & Creative Work', description='Nolan Kido: tournament poker, useful tools, and creative work. Explore the poker section or browse selected writing on technology, decisions, and learning.', updated='2026-10-05')
    elif page['id'] == 'about':
        page.update(description='About Nolan Kido: tournament poker, building tools, writing, and visual storytelling. A personal introduction and a few ways into the site.', updated='2026-10-05')
if any(p['path'].startswith('/poker/') for p in pages):
    raise RuntimeError('Poker routes already exist; review instead of overwriting')
pages.extend([
    {'id':'poker', 'path':'/poker/', 'title':'Poker.', 'seo_title':'Poker | Nolan Kido', 'description':'The poker side of Nolan Kido: tournament play, hand review, and the work between sessions. Start with a practical guide and a private-use review sheet.', 'kicker':'Nolan Kido / Poker', 'source':'poker/home.html', 'section':'poker', 'updated':'2026-10-05'},
    {'id':'poker-hand-review', 'path':'/poker/reviewing-a-hand/', 'title':'Review a hand, not just the result.', 'seo_title':'Review a Poker Hand, Not Just the Result | Nolan Kido', 'description':'A practical method for reviewing a tournament poker decision, with a worked fictional hand, clear uncertainty labels, and a blank review sheet.', 'kicker':'Poker / Hand review', 'source':'poker/reviewing-a-hand.html', 'section':'poker', 'updated':'2026-10-05'}
])
manifest_path.write_text(json.dumps(pages, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
replace('_scripts/build.py', 'from catalog import supplement', 'from catalog import supplement\nfrom poker_navigation import section_navigation')
replace('_scripts/build.py', "    values['site_css_version'] =", "    values['hubs_css_version'] = hashlib.sha256((ROOT / 'assets/hubs.css').read_bytes()).hexdigest()[:12]\n    values['site_css_version'] =")
replace('_scripts/build.py', "        section = 'notes' if p.get('note') else p['id']", "        section = p.get('section') or ('notes' if p.get('note') else p['id'])")
replace('_scripts/build.py', "(' aria-current=\"page\"' if section == name else '')", "((' aria-current=\"page\"' if p['path'] == '/' + name + '/' else ' aria-current=\"location\"') if section == name else '')")
replace('_scripts/build.py', "for name in ['about', 'notes', 'resources', 'contact'])", "for name in ['poker', 'notes', 'about', 'contact'])")
replace('_scripts/build.py', "'primary_nav': nav,", "'primary_nav': nav, 'section_nav': section_navigation(p),")
replace('_source/layout.html', '  ${extra_head}', '  <link rel="stylesheet" href="/assets/hubs.css?v=${hubs_css_version}">\n  ${extra_head}')
replace('_source/layout.html', 'Notes · Tools · Conversation', 'Poker · Technology · Creative work')
replace('_source/layout.html', '  <main id="main"', '  ${section_nav}\n  <main id="main"')
replace('_source/layout.html', '<a href="/bio/">Bio</a><a href="/card/">Card</a>', '<a href="/poker/">Poker</a>')
replace('_scripts/check_live.py', "assets = ['assets/contact.js'", "assets = ['assets/hubs.css', 'downloads/poker-hand-review.md', 'assets/contact.js'")
replace('_tests/browser.py', "(ROOT / 'assets/site.css').read_text()", "(ROOT / 'assets/site.css').read_text() + '\\n' + (ROOT / 'assets/hubs.css').read_text()")
replace('_tests/test_content.py', 'I build useful things and write about what I learn.', 'I play tournament poker, build tools, and explore ideas through writing and visual storytelling.')
path = ROOT / '_tests/test_design.py'
source = path.read_text(encoding='utf-8')
start = source.index('    def test_homepage_is_curated_not_a_statistics_display(self):')
end = source.index('    def test_fonts_disclosed_and_reviewed_asset_contracts(self):', start)
source = source[:start] + '''    def test_homepage_is_a_static_destination_selector(self):
        content = build.build_outputs()[Path('index.html')]
        for destination in ['/poker/', '/notes/', '/about/', '/contact/']:
            self.assertIn(destination, content)
        for obsolete in ['stat-strip', 'selected-notes', 'reading-table', 'class="resource-list"', 'featured_note', '<time']:
            self.assertNotIn(obsolete, content)
        self.assertEqual(content.count('class="destination destination-'), 2)
        self.assertLess(content.index('destination-poker'), content.index('destination-notes'))

''' + source[end:]
path.write_text(source, encoding='utf-8')
replace('_tests/design_browser.py', "entry['id'] in ['home', 'about', 'resources', 'contact', 'trustworthy-tools']", "entry['id'] in ['home', 'poker', 'poker-hand-review', 'about', 'resources', 'contact', 'trustworthy-tools']")
replace('_tests/design_browser.py', "        page.get_by_role('link', name='Start reading').click()\n        assert page.url.endswith('#selected-notes')", "        page.locator('.destination-poker').click()\n        assert page.url.endswith('/poker/')\n        page.get_by_role('link', name='Read the hand-review guide').click()\n        assert page.url.endswith('/poker/reviewing-a-hand/')\n        with page.expect_download() as info:\n            page.get_by_role('link', name='Download the review sheet').click()\n        assert Path(info.value.path()).read_bytes() == (ROOT / 'downloads/poker-hand-review.md').read_bytes()\n        page.get_by_role('link', name='Back to poker', exact=True).click()\n        assert page.url.endswith('/poker/')\n        page.get_by_role('link', name='Nolan Kido home', exact=True).click()\n        assert page.url == base + '/'")
replace('_tests/design_browser.py', '3 byte-matched downloads', '4 byte-matched downloads')

write('_tests/test_poker.py', '''
"""Gateway, poker navigation, public boundaries, and worked-hand regressions."""
import hashlib
import json
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
from poker_navigation import section_navigation

class PokerTests(unittest.TestCase):
    def test_poker_is_local_and_complete(self):
        outputs = build.build_outputs()
        for path in ['poker/index.html', 'poker/reviewing-a-hand/index.html']:
            page = outputs[Path(path)]
            self.assertIn('aria-label="Poker section"', page)
            self.assertIn('/poker/reviewing-a-hand/', page)
            self.assertIn('/downloads/poker-hand-review.md', page)
            for forbidden in ['<iframe', 'youtube.com', 'youtu.be', 'coming soon', 'solverPoker', 'OverlayPoker', 'Thunder Valley', 'mailto:']:
                self.assertNotIn(forbidden, page)
        self.assertNotIn('aria-label="Poker section"', outputs[Path('index.html')])
        self.assertEqual(section_navigation({'path':'/notes/'}), '')
        self.assertIn('href="/poker/" aria-current="page"', outputs[Path('poker/index.html')])
        self.assertIn('href="/poker/" aria-current="location"', outputs[Path('poker/reviewing-a-hand/index.html')])

    def test_guide_is_honest_and_hand_arithmetic_matches(self):
        text = build.build_outputs()[Path('poker/reviewing-a-hand/index.html')]
        self.assertIn('fictional', text)
        self.assertIn('Prepared with AI assistance.', text)
        self.assertIn('Use it after play.', text)
        self.assertEqual(Fraction('2.5') * 2 + Fraction('0.5'), Fraction('5.5'))
        self.assertEqual(Fraction('5.5') + 2 + 7, Fraction('14.5'))
        self.assertEqual(7 - 2, 5)
        for phrase in ['5.5 BB: 2.5 + 2.5 + 0.5', '14.5 BB: 5.5 + 2 + 7', '5 BB more to call, not 7 BB', '30 big blinds effective']:
            self.assertIn(phrase, text)
        self.assertNotIn('<form', text)
        sheet = (ROOT / 'downloads/poker-hand-review.md').read_text()
        self.assertIn('What you thought at the table', sheet)
        self.assertIn('Result, recorded separately', sheet)

    def test_new_assets_have_content_versions_and_live_checks(self):
        version = hashlib.sha256((ROOT / 'assets/hubs.css').read_bytes()).hexdigest()[:12]
        for path, content in build.build_outputs().items():
            if path.suffix == '.html':
                self.assertIn('/assets/hubs.css?v=' + version, content)
        targets = check_live.targets()
        for route in ['/poker/', '/poker/reviewing-a-hand/', '/assets/hubs.css', '/downloads/poker-hand-review.md']:
            self.assertIn(route, targets)

    def test_general_notes_and_their_dates_are_preserved(self):
        pages = json.loads((ROOT / '_source/pages.json').read_text())
        notes = [p for p in pages if p.get('note')]
        self.assertEqual(len(notes), 5)
        self.assertTrue(all(p['path'].startswith('/notes/') for p in notes))
        self.assertTrue(all(p['date'] == '2026-10-05' for p in notes))
        self.assertTrue(all(not p.get('note') for p in pages if p['path'].startswith('/poker/')))

if __name__ == '__main__':
    unittest.main(verbosity=2)
''')

write('POKER_RELEASE.md', '''
# Personal gateway and poker section

The main page is now a stable personal introduction and destination selector. Poker is the primary destination; the existing general Notes collection is secondary. About and shared biographies use the same approved broad identity.

## Published scope

- `/poker/`: an introduction, a hand-review entry point, a private-use worksheet, and a contact path.
- `/poker/reviewing-a-hand/`: a substantive guide with a clearly fictional example and independently checkable pot bookkeeping. No optimal action, solver result, or actual tournament result is asserted.
- `/downloads/poker-hand-review.md`: an editable blank record. No visitor answers are collected.

No unreviewed footage, social profile, real hand, tournament story, results table, travel schedule, or private project has been published. Future stories need approved source material and verified media links. Do not create empty content archives or promise a release date.

## Implementation

Source remains under `_source/`; `pages.json` defines the two new routes. The primary navigation is Poker, Notes, About, Contact. Poker has a small server-rendered local navigation with a clear route back to the main site. Existing article URLs, resource paths, general RSS entries, domain settings, contact code, and the two reviewed stylesheets are preserved. New presentation rules live in `assets/hubs.css`, with content-derived cache versions.

## Verification

Run the committed-build check, dependency-free tests, mocked-contact browser tests, real-page design browser tests, and the full accessibility/reflow audit from README. Browser tests cover the gateway-to-poker-to-guide path and the exact new download bytes. The live verifier includes both poker routes, the new stylesheet, and the review sheet. No real contact submission is part of these tests.

## Editorial direction

The root page is not an activity feed. Add a destination only when it leads to useful content. Poker may grow around approved tournament stories, hand reviews, and study material. A subsite separates subjects, not privacy: all committed files in this repository are public. Keep unpublished footage, source conversations, private drafts, and completed worksheets outside this repository.
''')
replace('EDITORIAL_GUIDE.md', '## What belongs', '## Personal gateway and poker\n\nThe root page is a relatively static identity and destination selector. Poker is the first major subject section; Notes remains a broader reading collection. Public poker material is now an intentional part of the site, but private project details and other people\'s information remain private. Add real stories, videos, and hands only from approved material. Do not invent results or publish placeholder media links. See `POKER_RELEASE.md`.\n\n## What belongs')
replace('README.md', '## Edit and publish', '## Site architecture\n\nThe main page is a static personal gateway. Poker at `/poker/` is the primary destination, with its guide at `/poker/reviewing-a-hand/`. Notes remains the general reading collection. New styles are isolated in `assets/hubs.css`; existing visual and contact assets are unchanged. See `POKER_RELEASE.md` for scope and publishing boundaries.\n\n## Edit and publish')
replace('_tests/test_live.py', 'self.assertEqual(len(values), 31)', 'self.assertEqual(len(values), 35)')
replace('_config.yml', '  - SITE_REVIEW.md', '  - SITE_REVIEW.md\n  - POKER_RELEASE.md')
print('Prepared personal gateway, poker guide, worksheet, navigation, and regression tests. Run the build and all release checks before publishing.')
