"""Temporary branch-only integration; remove after generating the reviewed release."""
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
def replace(path,old,new):
    file=ROOT/path;content=file.read_text(encoding='utf-8')
    if content.count(old)!=1:raise ValueError(f'{path}: expected one replacement, found {content.count(old)}')
    file.write_text(content.replace(old,new),encoding='utf-8')

file=ROOT/'_source/pages.json';pages=json.loads(file.read_text())
for slug,title,description,guide in [
    ('library','The Poker library.','Find every Poker guide by topic, search its title and summary, and choose a next read with estimated reading times.',False),
    ('decision-lab','One river. Two different stories.','A visual, fictional river exercise: price a call, test the assumed range and reveal two endings without confusing the result with the decision.',True)]:
    route='/poker/'+slug+'/'
    assert not any(p['path']==route for p in pages)
    p={'id':'poker-'+slug,'path':route,'title':title,'seo_title':title.rstrip('.')+' | Nolan Kido','description':description,'kicker':'Poker / '+('Decision Lab' if guide else 'Read, study, create'),'source':'poker/'+slug+'.html','section':'poker','updated':'2026-10-06'}
    if guide:p.update(date='2026-10-06',poker_guide=True)
    pages.append(p)
for p in pages:
    if p['path'] in ['/poker/','/poker/study/']:p['updated']='2026-10-06'
    if p['path']=='/poker/study/':p['description']='After-play workshops, a visual Decision Lab, practice questions and private-use worksheets for tournament study and poker vlog planning.'
file.write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

replace('_scripts/build.py','import poker_content\n','import poker_content\nimport poker_library\n')
replace('_scripts/build.py','    pages = public_pages()\n','    pages = public_pages()\n    reader_entries = poker_library.load(ROOT, pages)\n')
replace('_scripts/build.py','    values.update(poker_content.supplement(catalog, ROOT))\n','    values.update(poker_content.supplement(catalog, ROOT))\n    values.update(poker_library.supplement(reader_entries))\n')
extra='''        if p['path'].startswith('/poker/'):
            reader_version = hashlib.sha256((ROOT / 'assets/poker-reader.css').read_bytes()).hexdigest()[:12]
            extra += f'\\n  <link rel="stylesheet" href="/assets/poker-reader.css?v={reader_version}">'
            if p['id'] == 'poker-library':
                library_version = hashlib.sha256((ROOT / 'assets/poker-library.js').read_bytes()).hexdigest()[:12]
                extra += f'\\n  <script defer src="/assets/poker-library.js?v={library_version}"></script>'
            reader_meta = poker_library.reader_meta(p, reader_entries)
            if reader_meta:
                header = header.replace('</section>', reader_meta + '</section>', 1)
                body += poker_library.related(p, reader_entries)
'''
replace('_scripts/build.py',"        data = {**values",extra+"        data = {**values")
replace('_scripts/poker_navigation.py',"[('/poker/', 'Overview'),", "[('/poker/', 'Overview'), ('/poker/library/', 'Library'),")
replace('_scripts/check_live.py','    assets = [',"    assets = ['assets/poker-reader.css', 'assets/poker-library.js', ")

# Preserve legacy source guides and anchors; make the overview less repetitive.
home=ROOT/'_source/poker/home.html';text=home.read_text()
text,n=re.subn(r'<aside class="viewer-home-next">.*?</aside>', '<div class="reader-shortcuts"><a href="/poker/library/">Browse all ${poker_library_count} guides</a><a href="/poker/decision-lab/">Try the featured decision</a></div>',text,flags=re.S)
assert n==1
feature='''<section class="section folio-row" id="after-play" aria-labelledby="after-play-title">
  <div class="section-meta"><p class="section-label">Featured / Decision Lab</p></div>
  <div class="section-content"><div class="reader-feature"><p class="reader-eyebrow">Pause before the result</p><h2 id="after-play-title">One river.<br>Two different stories.</h2><p>A pair of aces faces a river bet. Open the call price, inspect the assumed range, then reveal two possible endings. Can your explanation survive both?</p>
    <div class="reader-deal"><div class="reader-deal-group"><span class="reader-deal-label">Your hand</span><div class="reader-cards"><span class="reader-playing-card" role="img" aria-label="Ace of spades">A<small aria-hidden="true">♠</small></span><span class="reader-playing-card" role="img" aria-label="Queen of clubs">Q<small aria-hidden="true">♣</small></span></div></div><div class="reader-deal-group"><span class="reader-deal-label">River board</span><div class="reader-cards"><span class="reader-playing-card is-red" role="img" aria-label="Ace of hearts">A<small aria-hidden="true">♥</small></span><span class="reader-playing-card is-red" role="img" aria-label="Seven of diamonds">7<small aria-hidden="true">♦</small></span><span class="reader-playing-card" role="img" aria-label="Two of clubs">2<small aria-hidden="true">♣</small></span><span class="reader-playing-card" role="img" aria-label="Nine of spades">9<small aria-hidden="true">♠</small></span><span class="reader-playing-card is-red" role="img" aria-label="Three of hearts">3<small aria-hidden="true">♥</small></span></div></div></div>
    <a class="reader-feature-link" href="/poker/decision-lab/">Step into the Decision Lab <span aria-hidden="true"> →</span></a><p class="reader-published-note">Fictional teaching case. Use away from play.</p></div>
    <h3>Find the question you are working on.</h3><p class="section-deck">The library brings every guide into one searchable directory. Choose a topic and a starting level, or use a study route when you already have a hand or an episode in mind.</p><div class="reader-shortcuts"><a href="/poker/library/">Explore the full Poker library</a><a href="/poker/short-stack-decisions/">Short-stack study</a><a href="/poker/practice-room/">Practice questions</a><a href="/poker/hand-to-vlog/">The vlog workbench</a></div></div>
</section>
'''
text,n=re.subn(r'<section class="section folio-row" id="after-play".*?</section>\n',feature,text,flags=re.S)
assert n==1
home.write_text(text,encoding='utf-8')

study=ROOT/'_source/poker/study.html';text=study.read_text()
text=text.replace('Seven workshops','Workshops &amp; Decision Lab').replace('Seven after-play workshops.','Study workshops and a Decision Lab.')
text=text.replace('<nav class="poker-jump" aria-label="Study desk shortcuts">','<nav class="poker-jump" aria-label="Study desk shortcuts"><a href="/poker/library/">Search all guides</a>')
target='<div class="viewer-library-grid">';assert text.count(target)==1
card='''<article><p class="note-category">Featured / Decision Lab</p><h3><a href="/poker/decision-lab/">One river. Two different stories.</a></h3><p>A visual decision, an exact price and an uncertain range. Reveal two endings and test whether your review survives both.</p></article>'''
text=text.replace(target,target+'\n'+card)
study.write_text(text,encoding='utf-8')

# Extend exact script allowlists for one local-only, page-scoped enhancement.
old="            self.assertEqual(len(other_scripts), 1 if path == Path('contact/index.html') else 0)\n            for src in other_scripts:\n                self.assertFalse(urlsplit(src).scheme or urlsplit(src).netloc)\n                self.assertEqual(urlsplit(src).path, '/assets/contact.js')"
new="            allowed = {Path('contact/index.html'): '/assets/contact.js', Path('poker/library/index.html'): '/assets/poker-library.js'}\n            self.assertEqual(len(other_scripts), 1 if path in allowed else 0)\n            for src in other_scripts:\n                self.assertFalse(urlsplit(src).scheme or urlsplit(src).netloc)\n                self.assertEqual(urlsplit(src).path, allowed[path])"
replace('_tests/test_site.py',old,new)
old="            expected = (['/assets/contact.js?v=' + hashlib.sha256((ROOT / 'assets/contact.js').read_bytes()).hexdigest()[:12]] if path == Path('contact/index.html') else []) + ['https://cloud.umami.is/script.js']"
new="            expected = (['/assets/contact.js?v=' + hashlib.sha256((ROOT / 'assets/contact.js').read_bytes()).hexdigest()[:12]] if path == Path('contact/index.html') else []) + ['https://cloud.umami.is/script.js']\n            if path == Path('poker/library/index.html'):\n                expected.append('/assets/poker-library.js?v=' + hashlib.sha256((ROOT / 'assets/poker-library.js').read_bytes()).hexdigest()[:12])"
replace('_tests/test_content.py',old,new)

# The direct file tests still see original sources; the browser HTML helper must
# include the new Poker-only sheet when it inlines local CSS for offline reading.
replace('_tests/browser.py',"        css += '\\n' + (ROOT / 'assets/poker.css').read_text()", "        css += '\\n' + (ROOT / 'assets/poker.css').read_text()\n        css += '\\n' + (ROOT / 'assets/poker-reader.css').read_text()")

# New related-reading cards can contain the same guide URL as its original link.
# Tests that target existing directory cards already use scoped selectors.
report=ROOT/'_reports/poker-reader-release.md';report.parent.mkdir(exist_ok=True)
report.write_text('''# Poker reader release: October 6, 2026

Adds a complete, static educational library with six topic filters, local-only
search, explicit reading-time estimates, level labels and related-reading cards.
All guides remain visible without JavaScript. Search never sends requests, updates
the URL, saves history or calls analytics. The only added runtime script is scoped
to the library. The Umami tracker, privacy policy and contact code are unchanged.

Adds one visual fictional river Decision Lab with five native answer disclosures.
Its price, weighted range and alternative showdowns are independently tested.
The feature uses HTML cards and existing typography rather than stock photos,
fabricated episodes, fabricated results or a simulated live poker interface.

The guide source files are unchanged except the Poker overview and study desk.
Shared navigation, reader metadata and related links alter rendered Poker pages.
Non-Poker generated HTML, existing CSS, contact code and global layout must remain
byte-identical to the base release. Tests enforce complete catalogue coverage and
fail when a newly published guide has not been added to the editorial index.

Reading estimates are an explicitly chosen convention of 225 words per minute,
including explanations, not reader telemetry. Five keyboard disclosures work
without JavaScript. Local browser tests inspect filtering, no-match recovery,
search/category intersections, literal hostile input, no network/storage effects,
blocked-script fallbacks and narrow/wide layouts. Automated accessibility tests
are not a complete manual accessibility certification.

Reference checks: PokerStars pot-odds lesson, GTO Wizard combinatorics and ICM
background, MDN search input documentation, W3C status-message guidance. The
river scene is original and explicitly conditional on its simplified chip model.
''',encoding='utf-8')
