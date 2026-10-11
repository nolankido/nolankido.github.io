from pathlib import Path
import json
import ast
import hashlib
import re
import subprocess
import sys

ROOT = Path.cwd()
def put(path, content):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + '\n', encoding='utf-8')
def replace(path, old, new):
    target = ROOT / path
    text = target.read_text(encoding='utf-8')
    assert text.count(old) == 1, (path, old[:90], text.count(old))
    target.write_text(text.replace(old, new), encoding='utf-8')

site = json.loads((ROOT / '_source/site.json').read_text())
site.update({
    'tagline': 'Build useful things. Make room for a good life.',
    'intro': 'I work with AI to build useful tools, develop ideas, and make complicated things clearer. Alongside that work: tournament poker, writing, visual storytelling, and curiosity about what makes life worth paying attention to.',
    'bio_short': 'Nolan Kido works with AI to build useful tools and make complicated ideas clearer. His interests connect practical technology, thoughtful living, tournament poker, and creative work.',
    'bio_long': 'Nolan Kido works with AI on useful tools, writing, and creative projects. He is interested in where technology genuinely helps, what still calls for human judgment, and how to leave room for life beyond the screen. His personal website brings together practical technology, Living Well, tournament poker, and creative work, with selected essays, clearly labelled worked examples, and resources to use or explore.'
})
put('_source/site.json', json.dumps(site, ensure_ascii=False, indent=2))
put('_source/identity.json', '''{
  "navigation": [
    {"id": "technology", "label": "Technology"},
    {"id": "living-well", "label": "Living Well"},
    {"id": "poker", "label": "Poker"},
    {"id": "creative", "label": "Creative Work"},
    {"id": "about", "label": "About"},
    {"id": "contact", "label": "Contact"}
  ],
  "selected": [
    {"path": "/notes/trustworthy-tools/", "kind": "Worked example / Technology", "description": "Two calculations agree. Both are wrong. A small, checkable example of why independent evidence matters."},
    {"path": "/living-well/did-the-tool-actually-help/", "kind": "Practical guide / Everyday life", "description": "Look at the effort a tool removes and the work it adds before deciding to keep it."},
    {"path": "/poker/reviewing-a-hand/", "kind": "Fictional hand / Poker", "description": "Separate a decision from its outcome, with a worked hand and a blank review sheet."}
  ]
}''')
put('_scripts/identity.py', '''"""Small, explicit personal gateway. Published content stays in its original section."""
import html
import json

def load(root, pages):
    config = json.loads((root / '_source/identity.json').read_text(encoding='utf-8'))
    by_path = {page['path']: page for page in pages}
    nav = config['navigation']
    ids = [item['id'] for item in nav]
    if len(ids) != len(set(ids)) or not ids:
        raise ValueError('Identity navigation needs unique destinations')
    for item in nav:
        if '/' + item['id'] + '/' not in by_path or not isinstance(item['label'], str) or not item['label'].strip():
            raise ValueError('Identity navigation must point to a published page')
    selected = config['selected']
    paths = [item['path'] for item in selected]
    if len(paths) != 3 or len(paths) != len(set(paths)):
        raise ValueError('Choose exactly three distinct gateway readings')
    for item in selected:
        page = by_path.get(item['path'])
        if not page or page.get('noindex') or page.get('living_well_kind') == 'experiment':
            raise ValueError('Gateway readings must be public, published content')
        if not all(isinstance(item.get(key), str) and item[key].strip() for key in ('kind', 'description')):
            raise ValueError('Gateway readings need a kind and an honest description')
    return config

def navigation(config, page):
    section = page.get('section') or ('notes' if page.get('note') else page['id'])
    links = []
    for item in config['navigation']:
        route = '/' + item['id'] + '/'
        current = ''
        if section == item['id']:
            current = ' aria-current="page"' if page['path'] == route else ' aria-current="location"'
        links.append('<li><a href="' + html.escape(route, quote=True) + '"' + current + '>' + html.escape(item['label']) + '</a></li>')
    return ''.join(links)

def selected_reading(config, pages):
    by_path = {page['path']: page for page in pages}
    cards = []
    for item in config['selected']:
        page = by_path[item['path']]
        cards.append('<article class="identity-reading"><p class="note-category">' + html.escape(item['kind']) + '</p><h3><a href="' + html.escape(page['path'], quote=True) + '">' + html.escape(page['title']) + '</a></h3><p>' + html.escape(item['description']) + '</p></article>')
    return '<div class="identity-readings">' + ''.join(cards) + '</div>'
''')
put('_source/home.html', '''<section class="hero folio-row brand-home" aria-labelledby="home-title">
  <div class="section-meta"><p class="section-label">A personal introduction</p></div>
  <div class="section-content">
    <div class="hero-heading"><h1 id="home-title">Nolan Kido</h1></div>
    <p class="hero-copy brand-statement">Build useful things.<br>Make room for a good life.</p>
    <p class="hero-caption">${intro}</p>
    <div class="link-row identity-actions"><a class="button" href="/technology/">Start with practical AI <span aria-hidden="true">→</span></a><a class="text-link" href="/about/">Meet Nolan <span aria-hidden="true">→</span></a></div>
  </div>
</section>
<section class="section folio-row identity-selection" aria-labelledby="selected-reading-title">
  <div class="section-meta"><p class="section-label">A way into my thinking</p></div>
  <div class="section-content">
    <h2 class="section-title" id="selected-reading-title">Start with something useful.</h2>
    <p class="section-deck">Three pieces from the site: something to question, something to try, and a decision to think through.</p>
    ${identity_reading}
    <p class="small-copy identity-reading-footer"><a href="/start-here/">Find your way around the site</a> or <a href="/notes/">browse the writing</a>.</p>
  </div>
</section>
<section class="section folio-row destination-section" aria-labelledby="destinations-title">
  <div class="section-meta"><p class="section-label">Explore further</p></div>
  <div class="section-content">
    <h2 class="section-title" id="destinations-title">Different interests. A connected life.</h2>
    <p class="section-deck">Technology is a means, not the whole point. These are the interests it sits alongside.</p>
    <div class="destination-grid">
      <a class="destination destination-technology" href="/technology/" aria-labelledby="technology-destination-title technology-destination-action" aria-describedby="technology-destination-description">
        <span class="destination-label">01 / Practical AI &amp; useful tools</span>
        <div class="technology-panel-body"><div class="destination-copy"><h3 id="technology-destination-title">Technology</h3><p id="technology-destination-description">Where AI helps in real life, how to check its work, and what to keep in human hands.</p></div><div class="technology-topics" aria-hidden="true"><span>Start with a real need.</span><span>Check the result.</span><span>Keep what helps.</span></div></div>
        <span class="destination-action" id="technology-destination-action">Explore technology <span aria-hidden="true">→</span></span>
      </a>
      <a class="destination destination-living-well" href="/living-well/" aria-labelledby="living-well-destination-title living-well-destination-action" aria-describedby="living-well-destination-description">
        <span class="destination-label">02 / More room for living</span><h3 id="living-well-destination-title">Living Well</h3><p id="living-well-destination-description">Meaning, attention, spirituality, and everyday life. Questions to explore without turning yourself into a project.</p><span class="destination-action" id="living-well-destination-action">Explore Living Well <span aria-hidden="true">→</span></span>
      </a>
      <a class="destination destination-poker" href="/poker/" aria-labelledby="poker-destination-title poker-destination-action" aria-describedby="poker-destination-description">
        <span class="destination-label">03 / Play, study &amp; uncertainty</span><h3 id="poker-destination-title">Poker</h3><p id="poker-destination-description">Tournament poker, decisions behind the hands, and resources for learning the game.</p><span class="destination-action" id="poker-destination-action">Explore poker <span aria-hidden="true">→</span></span>
      </a>
      <a class="destination destination-creative" href="/creative/" aria-labelledby="creative-destination-title creative-destination-action" aria-describedby="creative-destination-description">
        <span class="destination-label">04 / Make an idea connect</span><h3 id="creative-destination-title">Creative Work</h3><p id="creative-destination-description">Writing, design, and visual storytelling, with attention to the person on the other side.</p><span class="destination-action" id="creative-destination-action">Explore creative work <span aria-hidden="true">→</span></span>
      </a>
    </div>
  </div>
</section>
<section class="section folio-row home-connection" aria-labelledby="connection-title">
  <div class="section-meta"><p class="section-label">Beyond the screen</p></div>
  <div class="section-content"><h2 class="section-title" id="connection-title">There is a person behind the pages.</h2><p>My interests also include food, travel, and learning something unfamiliar. This is a selected introduction, not an attempt to put my whole life online.</p><div class="link-row"><a class="text-link" href="/about/">A little more about me <span aria-hidden="true">→</span></a><a class="text-link" href="/contact/">Start a conversation <span aria-hidden="true">→</span></a></div></div>
</section>''')
put('_source/about.html', '''<section class="section"><div class="shell editorial-grid"><div class="section-meta"><h2 class="section-label">The person, not just the topics</h2></div><div class="section-content prose">
<p class="intro">I like making things useful, understanding difficult ideas, and leaving room for a life beyond the work.</p>
<p>AI is part of how I build, write, and explore ideas. What interests me is not just what a tool can produce, but whether the result helps with something that matters. I want technology to make more room for life, not give every part of it another dashboard.</p>
<p>That is the connection between the different parts of this site. Practical technology, thoughtful living, tournament poker, and creative work ask different questions, but all involve attention, judgment, and the willingness to learn.</p>
<h2>What I spend my attention on</h2>
<p><a href="/technology/">Technology</a> is where I explore useful AI and software: starting with an actual need, checking what comes back, and knowing what still needs a person's judgment.</p>
<p><a href="/living-well/">Living Well</a> leaves space for meaning, spirituality, relationships, and the texture of ordinary life. Some questions deserve exploration rather than an efficient answer. Its <a href="/living-well/free-resources/">free resource library</a> offers ways to follow those questions.</p>
<p><a href="/poker/">Tournament poker</a> combines play, uncertainty, and study. The poker section makes room for understanding the game and reviewing decisions, without confusing a good result with a good decision.</p>
<p><a href="/creative/">Writing and visual storytelling</a> are another way of working through an idea. I care about what the reader or viewer can understand and feel, not just what a tool makes possible.</p>
<h2>Outside the categories</h2>
<p>Food, travel, and the experience of learning something unfamiliar belong in the picture too. Not every interest needs to become a project or a public update.</p>
<p>This site is a selected view of my interests and thinking. It is not a complete biography, a public diary, or a catalogue of everything I work on.</p>
<h2>Start with the work on the page</h2>
<p>The most useful introduction is something you can read or use. <a href="/start-here/">Start here</a> offers a short route through the site, with clear distinctions between essays, practical guides, fictional examples, and outside resources.</p>
<p>For introductions and profiles, use the <a href="/bio/">short biography</a>. For a shared interest, a thoughtful disagreement, something you are making, or a simple hello, <a href="/contact/">get in touch</a>.</p>
</div></div></section>''')
put('_source/start-here.html', '''<section class="section folio-row" aria-labelledby="start-intro-title">
  <div class="section-meta"><p class="section-label">An introduction, not a reading assignment</p></div>
  <div class="section-content prose"><h2 class="intro" id="start-intro-title">One person. A few connected interests.</h2><p>I'm Nolan. I work with AI, build useful things, and explore ideas through writing, poker, and everyday life. The site has grown into several substantial collections. You do not need to explore them all to get a sense of me.</p><p>For the person behind the pages, begin with <a href="/about/">About Nolan</a>. For a taste of the thinking, choose one of the pieces below.</p></div>
</section>
<section class="section folio-row" aria-labelledby="start-reading-title"><div class="section-meta"><p class="section-label">Read one thing</p></div><div class="section-content"><h2 class="section-title" id="start-reading-title">Three different ways in.</h2>${identity_reading}</div></section>
<section class="section folio-row" aria-labelledby="start-routes-title"><div class="section-meta"><p class="section-label">Follow an interest</p></div><div class="section-content prose"><h2 id="start-routes-title">Choose the direction that fits.</h2>
<h3>Practical AI and useful technology</h3><p>Start at <a href="/technology/">Technology</a> for a short path from deciding what matters to checking whether a tool helped. The <a href="/living-well/technology-for-real-life/">Technology for real life guide</a> offers concrete tasks to try.</p>
<h3>Meaning, attention, and everyday life</h3><p><a href="/living-well/">Living Well</a> brings together essays, guides, and free resources. A useful first question: <a href="/living-well/time-you-save/">what is the time you save actually for?</a></p>
<h3>Poker</h3><p>New to watching? Use the <a href="/poker/start-here/">viewer introduction</a>. Looking for a specific answer? Use the <a href="/poker/find/">Poker finder</a>. Already studying? Begin with the <a href="/poker/study/">Study desk</a>.</p>
<h3>Writing and making things</h3><p><a href="/creative/">Creative Work</a> connects writing and visual storytelling. The <a href="/notes/">Notes collection</a> includes worked explanations and reflections on decisions, learning, and knowing when to finish.</p>
</div></section>
<section class="section folio-row" aria-labelledby="reading-this-site"><div class="section-meta"><p class="section-label">What you are reading</p></div><div class="section-content prose"><h2 id="reading-this-site">The labels matter.</h2><p>Essays explore an idea. Practical guides offer an approach to try. Worked examples and fictional poker hands explain a method; they are not personal case studies. Resource directories point to other people's work, not work I am claiming as my own.</p><p>AI assistance is disclosed on the relevant articles. Proposed experiments in <a href="/living-well/field-notes/">Field notes</a> are plans, not completed results. The point is to make each piece useful without claiming more than it shows.</p><p>Read selectively, use what helps, and <a href="/contact/">send a thought or correction</a>.</p></div></section>''')
put('_source/technology/home.html', '''<section class="section folio-row topic-introduction" aria-labelledby="technology-intro-title">
  <div class="section-meta"><p class="section-label">Practical AI / Human judgment</p></div>
  <div class="section-content prose"><h2 class="intro" id="technology-intro-title">Useful AI starts with a life, not a tool.</h2><p>I work with AI to build tools, develop writing, and make difficult ideas easier to work with. The interesting question is not how much it can generate. It is whether the result is useful, trustworthy enough for its purpose, and worth the effort it takes to use.</p><p>This section connects the technical checks with the everyday reasons for doing the work. Start with selected writing on useful tools, then follow a practical guide or try a small check of your own.</p><div class="link-row"><a class="button" href="#technology-path">Find a useful starting point <span aria-hidden="true">↓</span></a><a class="text-link" href="/contact/">Talk technology <span aria-hidden="true">→</span></a></div></div>
</section>
<section class="section folio-row" aria-labelledby="technology-path"><div class="section-meta"><p class="section-label">From purpose to practice</p></div><div class="section-content prose"><h2 id="technology-path">Choose the question you have.</h2>
<h3>Where should AI fit?</h3><p><a href="/living-well/decide-what-matters/">Decide what matters before you ask AI what to do</a>. Start with the purpose and the constraints rather than a list of features.</p>
<h3>What could I use it for?</h3><p><a href="/living-well/technology-for-real-life/">Technology for real life</a> connects specific tasks: organizing notes, making a shared plan, finding a document, and turning a rough idea into something you can share.</p>
<h3>Did it actually make things better?</h3><p><a href="/living-well/did-the-tool-actually-help/">Check whether the tool made life easier</a>, including the checking, cleanup, and maintenance it adds. Then ask <a href="/living-well/what-to-decide-yourself/">what you should still decide personally</a>.</p>
</div></section>
<section class="section folio-row" id="technology-reading" aria-labelledby="technology-reading-title"><div class="section-meta"><p class="section-label">Check the work</p></div><div class="section-content"><h2 class="section-title" id="technology-reading-title">A convincing result is not enough.</h2><div class="notes-list"><article class="note-entry"><p class="note-category">A worked example</p><h3><a href="/notes/trustworthy-tools/">A working tool is not the same as a trustworthy one.</a></h3><p>Two calculations agree. Both are wrong. A small example of why independent checks matter.</p></article><article class="note-entry"><p class="note-category">A practical resource</p><h3><a href="/resources/#tool-trust-check">Tool trust check</a></h3><p>Define the claim, try an independent check, and make untested cases visible. Includes a fictional example and a blank editable copy.</p></article></div><p class="small-copy">These are explanations and thinking aids, not proof that a particular system is correct or a report of measured personal results.</p><p class="small-copy">For the human purpose behind the work, read <a href="/living-well/time-you-save/">what the time you save is actually for</a>. For a wider introduction, <a href="/start-here/">start here</a>.</p></div></section>''')
replace('_source/creative/home.html', 'Writing, design, and visual storytelling are different ways of inviting someone into an idea.', 'I work with writing, design, and visual storytelling as ways of inviting someone into an idea.')
replace('_tests/test_content.py', 'I build useful tools and explore ideas through technology, thoughtful living, tournament poker, and creative work.', 'I work with AI to build useful tools, develop ideas, and make complicated things clearer.')
replace('_source/notes.html', '<p>For a dedicated collection on spirituality, attention, and everyday technology,', '<p>New here? <a href="/start-here/">Start with a short introduction to the whole site</a>.</p>\n<p>For a dedicated collection on spirituality, attention, and everyday technology,')
replace('_source/404.html', '<a class="text-link" href="/notes/">Browse notes', '<a class="text-link" href="/start-here/">Find a starting point')
pages = json.loads((ROOT / '_source/pages.json').read_text())
updates = {
 'home': {'seo_title': 'Nolan Kido | Practical AI, Useful Things & a Good Life', 'description': 'A personal introduction to Nolan Kido: working with AI, building useful things, and exploring thoughtful living, tournament poker, writing, and creative work.'},
 'about': {'title': 'A little about me.', 'description': 'Meet Nolan Kido: practical AI, building, writing, tournament poker, and a life beyond the screen. A selected personal introduction, not a complete biography.'},
 'technology': {'description': 'Practical AI with human judgment: decide where a tool belongs, find a useful real-life task, and check whether it actually helped. A starting point from Nolan Kido.'},
 'bio': {'description': 'Short public introductions to Nolan Kido: practical AI, useful tools, clear ideas, thoughtful living, tournament poker, and creative work.'},
 'creative': {}, 'notes': {}, '404': {}
}
for page in pages:
    if page['id'] in updates:
        page.update(updates[page['id']]); page['updated'] = '2026-10-10'
pages.insert(1, {'id':'start-here','path':'/start-here/','title':'A few good places to begin.','seo_title':'Start Here | Nolan Kido','description':'Meet Nolan Kido, read one useful piece, or find a route into practical AI, thoughtful living, poker, and creative work.','kicker':'New here?','source':'start-here.html','updated':'2026-10-10'})
put('_source/pages.json', json.dumps(pages, ensure_ascii=False, indent=2))
replace('_scripts/build.py', 'import living_well\n', 'import living_well\nimport identity\n')
replace('_scripts/build.py', '    values = {k: text(v) for k, v in site.items()}\n', '    identity_config = identity.load(ROOT, pages)\n    values = {k: text(v) for k, v in site.items()}\n    values[\'identity_reading\'] = identity.selected_reading(identity_config, pages)\n')
start = '        section = p.get(\'section\') or (\'notes\' if p.get(\'note\') else p[\'id\'])\n'
source = (ROOT / '_scripts/build.py').read_text()
i = source.index(start); j = source.index("        canonical = site['url']", i)
source = source[:i] + '        nav = identity.navigation(identity_config, p)\n' + source[j:]
source = source.replace("        if p['id'] == 'home':\n            schema['about'] = {'@type': 'Person', 'name': site['name'], 'url': site['url'] + '/'}", "        if p['id'] in {'home', 'about'}:\n            person = {'@type': 'Person', '@id': site['url'] + '/about/#nolan-kido', 'name': site['name'], 'url': site['url'] + '/about/', 'description': site['bio_short']}\n            schema['about'] = person\n            schema['mainEntity'] = person\n            if p['id'] == 'about':\n                schema['@type'] = 'ProfilePage'")
put('_scripts/build.py', source)
replace('_source/layout.html', '<span class="site-edition">Technology · Living Well · Poker · Creative Work</span>', '<span class="site-edition">Practical AI · A life beyond the screen</span><a class="utility-start" href="/start-here/">Start here</a>')
replace('_source/layout.html', '<p class="footer-types">Schibsted Grotesk · Source Serif 4 · IBM Plex Mono</p>', '<p class="footer-types identity-footer">Build useful things. Make room for a good life. <a href="/start-here/#reading-this-site">About the writing on this site</a>.</p>')
css = '''
/* Personal architecture: identity first, selected reading second, topic libraries third. */
.identity-actions { margin-top: 24px; }
.identity-selection { padding-block: 36px; }
.identity-readings { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; }
.identity-reading { min-width: 0; border-top: 2px solid var(--line-dark); padding-top: 18px; }
.identity-reading h3 { font-size: 1.25rem; line-height: 1.3; margin-bottom: 12px; overflow-wrap: anywhere; }
.identity-reading p:not(.note-category) { font: 1rem/1.65 var(--serif); margin-bottom: 0; }
.identity-reading .note-category { color: var(--ink-soft); line-height: 1.6; }
.identity-reading-footer { margin: 22px 0 0; }
.site-bar .utility-start { text-decoration: underline; min-height: 24px; display: inline-flex; align-items: center; }
.site-bar .shell { align-items: center; }
.identity-footer a { margin-left: 12px; }
@media (max-width: 900px) {
  .identity-readings { grid-template-columns: minmax(0, 1fr); gap: 22px; }
  .identity-reading { max-width: 70ch; }
}
@media (max-width: 620px) {
  .site-bar .site-edition { display: none; }
  .identity-footer a { display: block; margin-left: 0; margin-top: 10px; }
}
'''
put('assets/hubs.css', (ROOT / 'assets/hubs.css').read_text() + css)
replace('_tests/test_gateway.py', "self.assertIn('Technology, living well,<br>poker, and creative work.', home)", "self.assertIn('Build useful things.<br>Make room for a good life.', home)")
put('_tests/test_identity.py', '''"""Personal introduction and curated routes must stay truthful, usable and connected."""
import copy
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import identity
import check_live

class IdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.config = identity.load(ROOT, cls.pages)
        cls.outputs = build.build_outputs()

    def test_identity_precedes_reading_and_libraries(self):
        home = self.outputs[Path('index.html')]
        self.assertLess(home.index('home-title'), home.index('selected-reading-title'))
        self.assertLess(home.index('selected-reading-title'), home.index('destinations-title'))
        self.assertIn('Build useful things.<br>Make room for a good life.', home)
        self.assertIn('href="/about/">Meet Nolan', home)
        self.assertIn('href="/technology/">Start with practical AI', home)
        self.assertIn('Food', self.outputs[Path('about/index.html')])

    def test_curated_entries_keep_canonical_titles_and_status(self):
        by_path = {p['path']: p for p in self.pages}
        for relative in ['index.html', 'start-here/index.html']:
            content = self.outputs[Path(relative)]
            self.assertEqual(content.count('class="identity-reading"'), 3)
            for item in self.config['selected']:
                self.assertIn(item['path'], content)
                self.assertIn(build.text(by_path[item['path']]['title']), content)
            self.assertIn('Fictional hand', content)
            self.assertNotIn('Proposed experiment:', content)
        start = self.outputs[Path('start-here/index.html')]
        self.assertIn('plans, not completed results', start)
        self.assertIn('/start-here/', check_live.targets())

    def test_every_page_can_return_to_the_personal_introduction(self):
        for path, content in self.outputs.items():
            if path.suffix == '.html':
                with self.subTest(path=path):
                    self.assertIn('class="utility-start" href="/start-here/"', content)
                    self.assertIn('/start-here/#reading-this-site', content)

    def test_profile_schema_does_not_invent_credentials(self):
        for relative in ['index.html', 'about/index.html']:
            content = self.outputs[Path(relative)]
            schema = json.loads(re.search(r'<script type="application/ld\\+json">(.*?)</script>', content).group(1))
            person = schema['mainEntity']
            self.assertEqual(person['@id'], 'https://nolankido.com/about/#nolan-kido')
            self.assertEqual(set(person), {'@type','@id','name','url','description'})
            if relative.startswith('about'):
                self.assertEqual(schema['@type'], 'ProfilePage')

    def test_rejects_missing_or_duplicate_curated_routes(self):
        for change in ['missing', 'duplicate']:
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp); (root / '_source').mkdir()
                config = copy.deepcopy(self.config)
                config['selected'][0]['path'] = '/not-published/' if change == 'missing' else config['selected'][1]['path']
                (root / '_source/identity.json').write_text(json.dumps(config))
                with self.assertRaises(ValueError):
                    identity.load(root, self.pages)

if __name__ == '__main__':
    unittest.main()
''')
readme = (ROOT / 'README.md').read_text()
a=readme.index('## Site architecture'); b=readme.index('## Edit and publish')
readme=readme[:a]+'''## Site architecture

The homepage introduces Nolan first, shows three selected pieces of published
writing, then opens the four subject libraries in their established order:
Technology, Living Well, Poker, Creative Work. `/start-here/` is the cross-site
orientation page. It is available in the shared utility bar on every page.
The homepage is not a chronological feed, project portfolio, or popularity counter.

`_source/identity.json` owns the primary navigation and three curated reading
choices. `_scripts/identity.py` validates their destinations against the complete
public manifest and renders the canonical titles. Existing content stays at its
original URL. Shared biographies come from `_source/site.json`. Change the
identity configuration deliberately rather than promoting whichever library
happens to have the most recent content expansion.

''' + readme[b:]
a=readme.index('## Technology-first home'); b=readme.index('## Poker publishing')
readme=readme[:a]+'''## Technology-first subject hierarchy

Technology remains the first subject, followed by Living Well, Poker, and
Creative Work. The personal introduction sits above all four. The technology
hub connects trust checks to practical everyday guides, without duplicating
articles or presenting proposed experiments as completed evidence. The live
checker derives page coverage from the complete manifest, including Start here.

''' + readme[b:]
put('README.md',readme)
put('_reports/personal-architecture.md', '''# Personal website architecture

Date: 2026-10-10

## Purpose

Introduce Nolan Kido before presenting the content collections. Preserve the
Quiet Signal design and the subject order: Technology, Living Well, Poker,
Creative Work. Practical AI is a leading interest, not an unsupported credential.

## Reader path

1. Home: personal purpose, useful published reading, subject doors, conversation.
2. Start here: meet the person or choose one short route through the libraries.
3. Technology: connect practical tasks, independent checks, and human judgment.
4. About and biography: a consistent, selective introduction without a resume,
   private project inventory, or real-time personal diary.
5. Deep pages: retain their local navigation and a site-wide route back to the
   personal introduction.

## Publishing boundaries

Do not add credentials, testimonials, adoption figures, measured outcomes,
unreleased work, guessed social links, or personal stories without an approved
source. Keep private work, personal records, and operational details out of this
public repository. Do not publish a portrait or other person's image without
approval. No synthetic personal imagery is used in this release.

The selected cards distinguish a worked example, a practical guide, and a
fictional poker hand. The orientation page distinguishes authored guidance,
external resources, and proposed experiments. No new essays or purported
firsthand experiments are introduced by this architecture change.

## Implementation

The identity configuration controls navigation and the three selected readings.
Canonical titles are resolved from the full page manifest at build time. Sources
stay in their existing collections. Start here is additive; all existing public
routes, local navigation, feeds, and directories are preserved. The About page
uses ProfilePage structured data with only approved name, URL and biography.

Contact code, form provider, verification key, analytics settings, privacy notice,
base design stylesheet, and hosting configuration remain unchanged. No new
runtime dependencies, scripts, accounts, tracking, or third-party services.

## Verification

Run the complete unit suite and committed-output check, then browser reflow,
keyboard, contact-recovery and accessibility checks. Before merging, compare
against current main. Verify both GitHub Pages deployment and exact public bytes.
The one-off branch preparation workflow must not appear in the final release tree.
''')
replace('_tests/test_living_well_library.py', "        for key in ('tagline', 'bio_long'):\n            self.assertIn('Living Well', site[key])", "        self.assertEqual(site['tagline'], 'Build useful things. Make room for a good life.')\n        self.assertIn('Living Well', site['bio_long'])")
# Advance only deliberately changed, reviewed baseline files.
subprocess.run([sys.executable, '_scripts/build.py'], check=True)
for test_path, paths in {
    '_tests/test_living_well_library.py': ['assets/hubs.css'],
    '_tests/test_viewer_next.py': ['index.html', 'technology/index.html', 'creative/index.html', 'assets/hubs.css']
}.items():
    target = ROOT / test_path
    content = target.read_text()
    for relative in paths:
        digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        pattern = r"('" + re.escape(relative) + r"'\s*:\s*')[a-f0-9]{64}(')"
        content, count = re.subn(pattern, lambda match: match[1] + digest + match[2], content)
        assert count == 1, (test_path, relative)
    if test_path.endswith('test_viewer_next.py'):
        content = content.replace('# October 9: owner-approved public introductions are aligned with Living Well.\n# Only home, Technology and Creative rendered introduction hashes are advanced in this release.', '# October 10: reviewed person-first gateway, Technology, Creative and shared hub styles.\n# These hashes deliberately advance for the owner-requested architecture revision.')
    target.write_text(content)
target = ROOT / '_tests/test_poker_content.py'
content = target.read_text()
paths = ast.literal_eval(re.search(r'^BASELINE_PATHS = (.+)$', content, re.M)[1])
digester = hashlib.sha256()
for relative in paths:
    digester.update(relative.encode() + b'\0' + (ROOT / relative).read_bytes() + b'\0')
content, count = re.subn(r"BASELINE_DIGEST = '[a-f0-9]{64}'", "BASELINE_DIGEST = '" + digester.hexdigest() + "'", content)
assert count == 1
content = content.replace('# October 9: reviewed owner-approved public introductions and bios include Living Well.', '# October 10: reviewed person-first architecture and source-generated shared shell.')
target.write_text(content)
extra = '''        page.goto(base)
        page.locator('a.button[href="/technology/"]').click()
        expect(page).to_have_url(base + '/technology/')
        page.locator('a[href="/living-well/did-the-tool-actually-help/"]').click()
        page.locator('.utility-start').focus()
        page.keyboard.press('Enter')
        expect(page).to_have_url(base + '/start-here/')
        expect(page.locator('.identity-reading')).to_have_count(3)
        page.get_by_role('link', name='About Nolan', exact=True).click()
        expect(page).to_have_url(base + '/about/')
        plain = browser.new_context(java_script_enabled=False)
        plain.route('**/*', lambda route: route.continue_() if urlsplit(route.request.url).hostname == '127.0.0.1' else route.abort())
        plain_page = plain.new_page()
        plain_page.goto(base + '/start-here/')
        plain_page.locator('.identity-reading a').first.click()
        expect(plain_page).to_have_url(base + '/notes/trustworthy-tools/')
        plain.close()

'''
replace('_tests/design_browser.py', "        page.goto(base + '/poker/glossary/#effective-stack')\n", extra + "        page.goto(base + '/poker/glossary/#effective-stack')\n")
replace('_tests/design_browser.py', "['home', 'about', 'resources', 'contact', 'trustworthy-tools'", "['home', 'start-here', 'about', 'resources', 'contact', 'trustworthy-tools'")
replace('.github/workflows/site-checks.yml', '            ${{ runner.temp }}/poker-reading-previews/poker-*.png', '            ${{ runner.temp }}/poker-reading-previews/poker-*.png\n            ${{ runner.temp }}/poker-reading-previews/home-*.png\n            ${{ runner.temp }}/poker-reading-previews/about-*.png\n            ${{ runner.temp }}/poker-reading-previews/start-here-*.png\n            ${{ runner.temp }}/poker-reading-previews/technology-*.png')
print('Reviewed personal architecture applied; independent safety checks retained.')
