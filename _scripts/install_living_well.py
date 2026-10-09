"""One-time, idempotent integration on the isolated Living Well branch. Remove before merge."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]

def replace(path, old, new):
    target = ROOT / path
    text = target.read_text(encoding='utf-8')
    if new in text:
        return
    if text.count(old) != 1:
        raise RuntimeError(f'Expected one integration anchor in {path}: {old[:70]}')
    target.write_text(text.replace(old, new, 1), encoding='utf-8')

replace('_scripts/build.py', 'import poker_topics\n', 'import poker_topics\nimport living_well\n')
replace('_scripts/build.py', "return base + poker_content.manifest(poker_content.load(root)) + poker_topics.manifest(root)", "return base + poker_content.manifest(poker_content.load(root)) + poker_topics.manifest(root) + living_well.manifest(root)")
replace('_scripts/build.py', "        if p.get('note') or p.get('poker_guide'):\n", "        if p.get('note') or p.get('poker_guide') or p.get('living_well_entry'):\n")
replace('_scripts/build.py', "if (p.get('note') or p.get('poker_guide')) and updated < date_value(p['date']):", "if (p.get('note') or p.get('poker_guide') or p.get('living_well_entry')) and updated < date_value(p['date']):")
replace('_scripts/build.py', "        if p.get('poker_entry'):\n            body =", "        if p['path'].startswith('/living-well/'):\n            body = living_well.render(p, ROOT)\n        elif p.get('poker_entry'):\n            body =")
replace('_scripts/build.py', "[('technology', 'Technology'), ('poker', 'Poker')", "[('technology', 'Technology'), ('living-well', 'Living Well'), ('poker', 'Poker')")
replace('_scripts/build.py', "        data = {**values, 'body': body,", "        header, living_extra = living_well.decorate(p, ROOT, header, schema)\n        extra += living_extra\n        data = {**values, 'body': body,")
replace('_scripts/build.py', "'section_nav': section_navigation(p)", "'section_nav': section_navigation(p) or living_well.section_navigation(p)")
replace('_scripts/build.py', "'og_type': 'article' if p.get('note') or p.get('poker_entry') or p.get('poker_guide') else 'website'", "'og_type': 'article' if p.get('note') or p.get('poker_entry') or p.get('poker_guide') or p.get('living_well_entry') else 'website'")
replace('_scripts/build.py', "    outputs[Path('nolan-kido.vcf')] =", "    outputs.update(living_well.exports(ROOT, site['url']))\n    outputs[Path('nolan-kido.vcf')] =")
replace('_scripts/build.py', "for existing in sorted((ROOT / 'poker').rglob('*.html')):", "for existing in sorted([*(ROOT / 'poker').rglob('*.html'), *(ROOT / 'living-well').rglob('*.html')]):")
replace('_scripts/build.py', "raise ValueError('Orphaned poker page: ' +", "raise ValueError(('Orphaned Living Well page: ' if existing.is_relative_to(ROOT / 'living-well') else 'Orphaned poker page: ') +")
replace('_scripts/check_live.py', "    catalog = build.poker_content.load(root)", "    assets += ['assets/living-well.css', 'living-well/feed.xml']\n    assets += [str(path) for path in build.living_well.worksheet_exports()]\n    catalog = build.poker_content.load(root)")
replace('_source/layout.html', 'Technology · Poker · Creative Work', 'Technology · Living Well · Poker · Creative Work')
replace('_source/layout.html', '<a href="/technology/">Technology</a><a href="/poker/">', '<a href="/technology/">Technology</a><a href="/living-well/">Living Well</a><a href="/poker/">')
replace('_source/home.html', 'Technology, poker,<br>and creative work.', 'Technology, living well,<br>poker, and creative work.')
replace('_source/home.html', 'Technology, Poker, and Creative Work</h2>', 'Technology, Living Well, Poker, and Creative Work</h2>')
replace('_source/home.html', '      <a class="destination destination-poker"', '''      <a class="destination destination-living-well" href="/living-well/" aria-labelledby="living-well-destination-title living-well-destination-action" aria-describedby="living-well-destination-description">
        <span class="destination-label">02 / More room for living</span>
        <h3 id="living-well-destination-title">Living Well</h3>
        <p id="living-well-destination-description">Spirituality, practical wisdom, and technology for everyday life. Thoughtful questions and useful experiments, without optimizing every moment.</p>
        <span class="destination-action" id="living-well-destination-action">Explore Living Well <span aria-hidden="true">→</span></span>
      </a>
      <a class="destination destination-poker"''')
replace('_source/home.html', '02 / At the table &amp; beyond', '03 / At the table &amp; beyond')
replace('_source/home.html', '03 / Ideas into expression', '04 / Ideas into expression')
replace('_source/notes.html', '${notes_list}', '<p>For a dedicated collection on spirituality, attention, and everyday technology, explore <a href="/living-well/ideas/">Living Well essays</a>. Its <a href="/living-well/feed.xml">separate RSS feed</a> includes the new essays and practical guides.</p>\n${notes_list}')
replace('_source/technology/home.html', '    <a class="text-link" href="/">Back to Nolan Kido', '    <p class="small-copy">What are these tools for? <a href="/living-well/">Living Well</a> explores the human purpose, including <a href="/living-well/time-you-save/">what the time you save is actually for</a>.</p>\n    <a class="text-link" href="/">Back to Nolan Kido')
replace('_source/resources.html', '${resources_list}', '${resources_list}') if '${resources_list}' in (ROOT / '_source/resources.html').read_text() else None
resource_path = ROOT / '_source/resources.html'
resource_text = resource_path.read_text()
if 'Living Well worksheets' not in resource_text:
    marker = '</section>'
    addition = '<section class="section folio-row"><div class="section-meta"><p class="section-label">Living Well</p></div><div class="section-content prose"><h2>Room for ordinary life</h2><p><a href="/living-well/worksheets/">Living Well worksheets</a> cover a weekly reset, values before advice, a family story, an attention check, and a small experiment. They are blank private-use files, not answer forms.</p></div></section>\n'
    resource_path.write_text(resource_text + '\n' + addition)
pages_path = ROOT / '_source/pages.json'
pages = json.loads(pages_path.read_text())
for page in pages:
    if page['id'] == 'home':
        page['seo_title'] = 'Nolan Kido | Technology, Living Well, Poker & Creative Work'
        page['description'] = 'Explore technology, Living Well, poker, and creative work: useful tools, spirituality, everyday life, thoughtful decisions, and visual storytelling.'
    if page['id'] in {'home', 'technology', 'notes', 'resources'}:
        page['updated'] = '2026-10-08'
pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + '\n')
css_path = ROOT / 'assets/hubs.css'
css = css_path.read_text()
if 'Living Well major destination' not in css:
    css += '''
/* Living Well major destination; retain Technology first and the existing Poker/Creative pair. */
.destination-living-well { grid-column: 1 / -1; background: var(--paper-light); border-top: 3px solid var(--green); }
.destination-living-well p { max-width: 64ch; }
@media (max-width: 620px) {
  .nav-links li:nth-child(4), .nav-links li:last-child { grid-column: auto; justify-self: auto; }
  .nav-links { grid-template-columns: repeat(3, minmax(0, auto)); gap: 2px 12px; }
}
@media (max-width: 400px) {
  .nav { flex-direction: column; align-items: stretch; }
  .nav .brand { align-self: flex-start; }
  .nav-links { width: 100%; justify-content: space-between; }
}
'''
    css_path.write_text(css)
replace('_tests/test_gateway.py', "def test_three_real_destinations_in_reading_order(self):", "def test_four_real_destinations_in_reading_order(self):")
replace('_tests/test_gateway.py', "['/technology/', '/poker/', '/creative/']", "['/technology/', '/living-well/', '/poker/', '/creative/']")
replace('_tests/test_gateway.py', 'Technology, poker,<br>and creative work.', 'Technology, living well,<br>poker, and creative work.')
replace('_tests/test_design.py', "content.count('class=\"destination destination-'), 3", "content.count('class=\"destination destination-'), 4")
replace('_tests/test_poker_content.py', "+len(build.poker_topics.manifest(root))+1)", "+len(build.poker_topics.manifest(root))+len(build.living_well.manifest(root))+1)")
readme = ROOT / 'README.md'
text = readme.read_text()
if '## Living Well' not in text:
    text += '''
## Living Well

`/living-well/` is a major, publicly linked section between Technology and Poker.
The two catalogs in `_source/living-well/` hold the authored launch content;
`_scripts/living_well.py` validates them and renders the shared manifest, subject
pages, reader routes, article metadata, separate RSS, and blank worksheets.
The launch has 16 essays/guides, 3 proposed experiment protocols, 5 subject pages,
and 9 supporting hubs. Proposed protocols are not completed field notes and are
excluded from the editorial RSS feed. No private answers, new JavaScript, or
new third-party services are introduced. The current contact and analytics
configuration is preserved. Run `_tests/test_living_well.py` and
`_tests/living_well_browser.py` alongside the existing full regression suite.
'''
    readme.write_text(text)
print('Living Well integration applied without changing contact, analytics, or original design assets.')
