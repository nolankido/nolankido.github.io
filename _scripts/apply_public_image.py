"""One-off owner-directed source migration; removed before release."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import sys
from xml.etree import ElementTree as ET
R = Path.cwd()

def put(path, content):
    target = R / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + '\n', encoding='utf-8')

def replace(path, before, after):
    source = (R / path).read_text(encoding='utf-8')
    assert source.count(before) == 1, (path, before[:80], source.count(before))
    put(path, source.replace(before, after))

protected = ['_source/site.json', '_source/contact.html', '_source/privacy.html', 'styles.css', 'assets/site.css', 'assets/contact.js', '_config.yml', 'CNAME', 'living-well/feed.xml', 'poker/feed.xml']
protected += ['_source/notes/' + slug + '.html' for slug in ['decision-quality', 'finishing-is-a-decision', 'generous-explanations', 'learning-from-the-beginning', 'trustworthy-tools']]
put('_tests/presentation-baseline.json', json.dumps({path: hashlib.sha256((R / path).read_bytes()).hexdigest() for path in protected}, indent=2))
items = ET.fromstring((R / 'feed.xml').read_text()).findall('./channel/item')
historical_digest = hashlib.sha256(json.dumps([{child.tag: child.text for child in item} for item in items], sort_keys=True).encode()).hexdigest()

pages = json.loads((R / '_source/pages.json').read_text())
new = {'id': 'keep-the-judgment', 'path': '/notes/keep-the-judgment/', 'title': 'Let AI do more. Keep the judgment.', 'seo_title': 'Let AI Do More. Keep the Judgment. | Nolan Kido', 'description': 'Delegating production is not the same as handing over responsibility. An essay on purpose, boundaries, permission, and the choices worth keeping human.', 'kicker': 'Practical AI / An essay', 'source': 'notes/keep-the-judgment.html', 'note': True, 'date': '2026-10-11', 'editorial_note': 'Prepared with AI assistance. This is an argument about delegation and judgment, not a report of measured results. The Saturday-afternoon scenario is fictional.'}
assert not any(p['id'] == new['id'] for p in pages)
pages.append(new)
for page in pages:
    if page['id'] in {'home', 'notes', 'technology', 'about', 'start-here', 'bio'}:
        page['updated'] = '2026-10-11'
put('_source/pages.json', json.dumps(pages, ensure_ascii=False, indent=2))
selection = json.loads((R / '_source/selection.json').read_text())
selection['featured_note'] = new['id']
selection['note_order'].insert(0, new['id'])
put('_source/selection.json', json.dumps(selection, indent=2))
identity = json.loads((R / '_source/identity.json').read_text())
identity['selected'][0] = {'path': new['path'], 'kind': 'Essay / Practical AI', 'description': 'Delegate more of the production without giving up the purpose, boundaries, and decisions you need to stand behind.'}
identity['reading_routes'][0]['paths'] = [new['path'], '/notes/trustworthy-tools/']
put('_source/identity.json', json.dumps(identity, ensure_ascii=False, indent=2))

replace('_source/home.html', 'Three pieces from the site: something to question, something to try, and a decision to think through.', 'A position on using AI, a practical test of usefulness, and a poker decision to think through.')
replace('_source/notes.html', '<p>Choose one piece. There is no sequence to complete, and these selections are not a list of everything I have published. The original <a href="#general-notes">general notes</a> remain below.</p>', '<p>Choose an interest below, or begin with <a href="${featured_note_url}">${featured_note_title}</a>, an essay about what remains your responsibility when AI helps with the work. The complete <a href="#general-notes">Notes collection</a> is below.</p>')
replace('_source/notes.html', 'The original Notes collection', 'The Notes collection')
replace('_source/notes.html', 'Five general pieces on trust, decisions, learning, explanation, and finishing. A few also appear in the routes above.', 'Essays on practical AI, trust, decisions, learning, explanation, and finishing. Published dates are shown; the order is selected for reading, not an activity counter.')
replace('_source/notes.html', '<section class="section folio-row" aria-labelledby="writing-further-title">', '<section class="section folio-row" id="follow" aria-labelledby="writing-further-title">')
replace('_source/technology/home.html', '<div class="link-row"><a class="button" href="#technology-path">Find a useful starting point', '<p><strong>A position to start with:</strong> <a href="${featured_note_url}">${featured_note_title}</a> explores the difference between delegating production and handing over responsibility.</p><div class="link-row"><a class="button" href="#technology-path">Find a useful starting point')
replace('_source/about.html', '<h2>What I spend my attention on</h2>', '''<h2 id="what-matters-in-the-work">What matters to me in the work</h2>
<p><strong>Usefulness:</strong> start with a real purpose, not a demonstration in search of one. <strong>Clarity:</strong> give the reader enough context to understand the choice. <strong>Judgment:</strong> be willing to question a polished result, change direction, or stop when the work has done its job.</p>
<p>Those are priorities, not a claim that every attempt succeeds. <a href="/notes/keep-the-judgment/">Let AI do more. Keep the judgment.</a> develops the distinction behind them.</p>
<h2>What I spend my attention on</h2>''')
replace('_source/about.html', 'This site is a selected view of my interests and thinking. It is not a complete biography, a public diary, or a catalogue of everything I work on.', 'I keep this site focused on the ideas and material that are useful to share. Some work and much of ordinary life belong outside a public website.')
replace('_source/bio.html', 'For more context, visit the <a href="/about/">About page</a>.', 'For more context, visit the <a href="/about/">About page</a>. For a concrete introduction to the thinking, read <a href="/notes/keep-the-judgment/">Let AI do more. Keep the judgment.</a>.')
replace('_source/start-here.html', '<h2 id="reading-this-site">The labels matter.</h2>', '<h2 id="reading-this-site">The labels matter.</h2><p>To start with a point of view, read <a href="/notes/keep-the-judgment/">Let AI do more. Keep the judgment.</a>. It is an argument about responsibility, not a claim that every use of AI succeeds.</p>')
replace('_source/layout.html', '<a class="utility-start" href="/start-here/">Start here</a>', '<nav class="utility-navigation" aria-label="Site shortcuts"><a class="utility-writing" href="/notes/"${writing_current}>Writing</a><a class="utility-start" href="/start-here/">Start here</a></nav>')
replace('_source/layout.html', '<meta name="twitter:card" content="summary">', '${social_metadata}')
put('_source/presentation.json', json.dumps({'default': {'src': '/assets/social/nolan-kido.png', 'alt': 'Nolan Kido. Build useful things. Make room for a good life. nolankido.com.'}, 'pages': {'keep-the-judgment': {'src': '/assets/social/keep-the-judgment.png', 'alt': 'Let AI do more. Keep the judgment. An essay by Nolan Kido on purpose, boundaries, and responsibility.'}}}, indent=2))
replace('_scripts/identity.py', 'import json\n', 'import json\nfrom presentation import publication\n')
replace('_scripts/identity.py', "html.escape(item['description']) + '</p></article>'", "html.escape(item['description']) + '</p>' + publication(page) + '</article>'")
replace('_scripts/identity.py', "html.escape(page['description']) + '</p></article>'", "html.escape(page['description']) + '</p>' + publication(page) + '</article>'")
replace('_scripts/build.py', 'import identity\n', 'import identity\nimport presentation\n')
replace('_scripts/build.py', "    template = (SOURCE / 'layout.html').read_text(encoding='utf-8')", "    presentation_config = presentation.load(ROOT, pages)\n    template = (SOURCE / 'layout.html').read_text(encoding='utf-8')")
replace('_scripts/build.py', "f'<p>{text(p[\"description\"])}</p></article>')", "f'<p>{text(p[\"description\"])}</p>' + presentation.publication(p) + '</article>')")
replace('_scripts/build.py', '<a href="/notes/" class="breadcrumb">All notes</a>', '<a href="/notes/" class="breadcrumb">Writing</a>')
replace('_scripts/build.py', "heading += f'<p class=\"note-meta\">Published <time datetime=\"{p[\"date\"]}\">{date_label(p[\"date\"])}</time> · Nolan Kido</p>'", "heading += f'<p class=\"note-meta\">Published <time datetime=\"{p[\"date\"]}\">{date_label(p[\"date\"])}</time> · <a href=\"/about/\">Nolan Kido</a> · About {poker_library.minutes(body)} min read</p>'\n                heading += '<p class=\"essay-context\"><a href=\"#about-this-essay\">AI-assisted essay</a></p>'")
replace('_scripts/build.py', "'<p class=\"editorial-note\">Prepared with AI assistance. Worked scenarios are fictional; research is linked where used. These essays do not describe private projects or personal events.</p>'", "f'<p class=\"editorial-note\" id=\"about-this-essay\">{text(p.get(\"editorial_note\", \"Prepared with AI assistance. Worked scenarios are fictional; research is linked where used. These essays do not describe private projects or personal events.\"))}</p>'")
replace('_scripts/build.py', 'aria-label="After the note"><a href="/notes/">All notes</a>', 'aria-label="After the note"><a href="/notes/">Writing across the site</a>')
replace('_scripts/build.py', "data = {**values, 'body': body,", "data = {**values, 'social_metadata': presentation.metadata(presentation_config, p, site['url']), 'writing_current': (' aria-current=\"page\"' if p['id'] == 'notes' else ' aria-current=\"location\"' if p.get('note') else ''), 'body': body,")
replace('_scripts/check_live.py', '    catalog = build.poker_content.load(root)', "    sharing = build.presentation.load(root, pages)\n    assets += sorted({card['src'].lstrip('/') for card in [sharing['default'], *sharing['pages'].values()]})\n    catalog = build.poker_content.load(root)")
put('assets/hubs.css', (R / 'assets/hubs.css').read_text() + '''
/* Reading context and utility discovery; preserve the six-item subject navigation. */
.utility-navigation { display:flex; flex-wrap:wrap; gap:18px; align-items:center; }
.site-bar .utility-navigation a { display:inline-flex; align-items:center; min-height:28px; text-decoration:underline; }
.site-bar .utility-navigation a[aria-current] { text-decoration-thickness:2px; }
.reading-date, .identity-reading p.reading-date { font: .78rem/1.6 var(--sans); color:var(--ink-soft); margin:12px 0 0; }
.essay-context { font:.82rem/1.5 var(--sans); color:var(--ink-soft); margin:12px 0 0; }
@media (max-width: 760px) { .site-bar .site-edition { display:none; } }
@media (max-width: 360px) { .site-bar .shell { gap:10px; } .utility-navigation { gap:12px; } }
''')
replace('EDITORIAL_GUIDE.md', 'Technology, Poker, and Creative Work are the three permanent subject destinations, in that order. Technology leads by visual prominence even while its public collection is small. Introductory subject pages may curate existing public notes, but must state their present scope without implying a released portfolio. Notes remains a supporting cross-subject collection. This supersedes the earlier poker-first gateway ranking, not the privacy or approval requirements.', 'The personal introduction leads the four subject destinations: Technology, Living Well, Poker, Creative Work. Technology leads among subjects, but the person is not reduced to an AI brand. Writing at `/notes/` connects the collections, with Start here as a short orientation. Introductory pages select actual published material without implying a released portfolio. A stronger public image must come from clarity and useful work, not invented credentials or private disclosures. This supersedes earlier subject rankings, not the privacy or approval requirements.')
put('EDITORIAL_GUIDE.md', (R / 'EDITORIAL_GUIDE.md').read_text() + '''
## Original essays and public-image improvements

Opinion essays may develop the approved public perspective without inventing a
firsthand experiment. Label illustrative scenarios, disclose AI assistance, and
do not claim that Nolan personally reviewed wording unless he actually did.
Keep observed results, reasoned arguments, and proposed work distinct. Display
original publication dates on reading cards; changing curation is not publication.
Do not add a photo, a guessed social account, biography detail, or client claim to
fill an apparent credibility gap. Shared previews are local typographic graphics,
not photographs of the owner. Their display on a social platform is not guaranteed.
''')
put('_reports/public-image-20261011.md', '''# Public image and editorial clarity

Date: 2026-10-11
Baseline: d0ffcd0396350c556b6f394b87997d26b0692470

## Purpose

Continue the person-first architecture rather than restart the design. Make the
public positioning tangible through an original, AI-assisted argument about
judgment, not a manufactured resume or a private-project portfolio.

## Changes

- Add the essay "Let AI do more. Keep the judgment." with a fictional shared-afternoon
  example, explicit scope, a clear thesis and links to supporting existing reading.
- Select it on Home, Start here, Writing and Technology; connect it from About/Bio.
- Make Writing available beside Start here on every page, without expanding the
  six-item primary subject navigation. Show its active state on notes.
- Show actual publication dates on selected and cross-site reading cards and the
  Notes collection. Add linked author, estimated reading time and a visible link
  to the AI-assistance disclosure on original notes.
- Add locally hosted typographic sharing images with descriptive alternatives,
  real dimensions, metadata validation and exact-byte live verification targets.
- Remove the obsolete five-note count and align the editorial guide with the
  four-subject, person-first hierarchy.

## Boundaries

No private projects, personal records, named third parties, invented experience,
measured results, credentials, testimonials, social accounts or personal portraits.
The original note bodies, Poker and Living Well catalogs, contact code, form keys,
privacy source, base stylesheet, analytics settings and hosting settings are fixed.
The Notes feed gains exactly one article; old dates/GUIDs and both other feeds stay
unchanged. No new client script, tracking or runtime service.

## Verification protocol

Run committed-output checks, the full unit suite and the existing browser and
accessibility suites before merge. Inspect the desktop/mobile reading paths and
social previews. Remove all preparation-only files before release. Verify Pages
and exact live bytes separately. External platform preview caches are outside the
site's control. Automated accessibility passes are not certification.

## Implementation references

Open Graph image properties: https://ogp.me/#structured
Cards are stored as reviewed static PNGs. Source and assets remain in this public
repository; never add private source material merely because it is unlinked.
''')

replace('_tests/test_design.py', "'featured_note', '<time'", "'featured_note'")
replace('_tests/test_design.py', "self.assertEqual(content.count('class=\"destination destination-'), 4)", "self.assertEqual(content.count('class=\"destination destination-'), 4)\n        self.assertEqual(content.count('class=\"reading-date\"'), 3)")
replace('_tests/test_gateway.py', 'self.assertEqual(len(notes), 5)', "self.assertEqual(len(notes), 6)\n        self.assertIn('keep-the-judgment', {p['id'] for p in notes})")
replace('_tests/test_poker.py', "notes = [p for p in pages if p.get('note')]", "notes = [p for p in pages if p.get('note') and p['id'] != 'keep-the-judgment']\n        addition = next(p for p in pages if p['id'] == 'keep-the-judgment')\n        self.assertEqual(addition['date'], '2026-10-11')\n        self.assertTrue(addition['note'])")
replace('_tests/design_browser.py', "'contact', 'trustworthy-tools', 'poker'", "'contact', 'trustworthy-tools', 'keep-the-judgment', 'poker'")
replace('_tests/design_browser.py', "expect(plain_page).to_have_url(base + '/notes/trustworthy-tools/')", "expect(plain_page).to_have_url(base + '/notes/keep-the-judgment/')\n        plain_page.get_by_role('link', name='AI-assisted essay', exact=True).click()\n        expect(plain_page.locator('#about-this-essay')).to_be_visible()\n        plain_page.locator('.utility-writing').focus()\n        plain_page.keyboard.press('Enter')\n        expect(plain_page).to_have_url(base + '/notes/')")
replace('_tests/test_reading_architecture.py', "self.assertEqual(hashlib.sha256(original.encode()).hexdigest(),\n                         '9b3e05a7e14db5b1e751d18a7ff0c8cbaf47b7d60453c1e9c43424e8d57e223a')", "# One authorized essay is new; every historical feed item stays unchanged.\n        historical = [item for item in ET.fromstring(original).findall('./channel/item')\n                      if item.findtext('link') != 'https://nolankido.com/notes/keep-the-judgment/']\n        records = [{child.tag: child.text for child in item} for item in historical]\n        self.assertEqual(hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest(),\n                         '" + historical_digest + "')")
subprocess.run([sys.executable, '_scripts/render_social_cards.py'], check=True)
subprocess.run([sys.executable, '_scripts/build.py'], check=True)
for test, paths in {'_tests/test_viewer_next.py': ['index.html', 'technology/index.html', 'creative/index.html', 'assets/hubs.css', 'feed.xml'], '_tests/test_living_well_library.py': ['assets/hubs.css']}.items():
    source = (R / test).read_text()
    for path in paths:
        digest = hashlib.sha256((R / path).read_bytes()).hexdigest()
        source, count = re.subn("('" + re.escape(path) + r"'\s*:\s*')[a-f0-9]{64}(')", lambda m: m[1] + digest + m[2], source)
        assert count == 1, (test, path)
    put(test, source)
source = (R / '_tests/test_poker_content.py').read_text()
paths = ast.literal_eval(re.search(r'^BASELINE_PATHS = (.+)$', source, re.M)[1])
digest = hashlib.sha256()
for path in paths:
    digest.update(path.encode() + b'\0' + (R / path).read_bytes() + b'\0')
source = re.sub("BASELINE_DIGEST = '[a-f0-9]{64}'", "BASELINE_DIGEST = '" + digest.hexdigest() + "'", source)
put('_tests/test_poker_content.py', source)
print('Presentation migration complete; protected original sources and feed records remain test fixtures.')
