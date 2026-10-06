"""One-time source integration, removed before merge."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def replace(path, old, new):
    f=ROOT/path;s=f.read_text(encoding='utf-8')
    if s.count(old)!=1:raise ValueError((path,s.count(old),old))
    f.write_text(s.replace(old,new),encoding='utf-8')
f=ROOT/'_source/pages.json';pages=json.loads(f.read_text())
new=[('flush-and-redraw','The flush arrives. What can still change?','Follow a fictional flush through the turn and river, count all remaining cards, and distinguish improving from winning.', True),
('side-pot-lab','Three all-ins. Two pots.','Separate a fictional three-way all-in into a main pot, side pot and refund, then check the winners and final stacks.',True),
('decision-labs','The Decision Labs.','Three visual, fictional poker cases: read a range, follow a runout and untangle side pots. Predict before revealing each explanation.',False)]
for slug,title,desc,guide in new:
    route='/poker/'+slug+'/'
    assert not any(p['path']==route for p in pages)
    page={'id':'poker-'+slug,'path':route,'title':title,'seo_title':title.rstrip('.')+' | Nolan Kido','description':desc,'kicker':'Poker / Decision Labs','source':'poker/'+slug+'.html','section':'poker','updated':'2026-10-06'}
    if guide:page.update(date='2026-10-06',poker_guide=True)
    pages.append(page)
f.write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=ROOT/'_source/poker/library.json';base=f.read_text()
entries=[
    {'slug':'flush-and-redraw','title':'The flush arrives. What can still change?','description':'Follow a face-up replay, count all 44 possible rivers and see how a different opposing hand changes the answer.','topic':'practice','level':'Practice','keywords':'decision lab flush redraw runout full house outs equity probability board pair'},
    {'slug':'side-pot-lab','title':'Three all-ins. Two pots.','description':'Separate matched chips, side-pot eligibility and uncalled refunds, then reconcile every final stack.','topic':'practice','level':'Practice','keywords':'decision lab all in side pots refund uncalled chips main pot eligibility accounting'}]
line=next(line for line in base.splitlines(True) if '"slug":"decision-lab"' in line)
insert=''.join('    '+json.dumps(e,ensure_ascii=False,separators=(',',':'))+',\n' for e in entries)
f.write_text(base.replace(line,line+insert),encoding='utf-8')
replace('_scripts/build.py','import poker_library\n','import poker_library\nimport poker_reading\n')
replace('_scripts/build.py',"header = header.replace('</section>', reader_meta + '</section>', 1)","header = header.replace('</section>', reader_meta + poker_reading.section_outline(body) + '</section>', 1)")
replace('_scripts/poker_library.py','import re\n','import re\nfrom poker_reading import next_reads\n')
replace('_scripts/poker_library.py',"    peers = [e for e in entries if e['route'] != item['route'] and e['topic'] == item['topic']]\n    if len(peers) < 2:\n        peers += [e for e in entries if e['route'] != item['route'] and e not in peers]", "    peers = next_reads(item, entries)")
replace('_scripts/poker_library.py','<a href="/poker/library/">All Poker guides</a><a href="#main">Back to top</a>', '<a href="/poker/library/">All Poker guides</a><a href="/poker/decision-labs/">All Decision Labs</a><a href="#main">Back to top</a>')
replace('_source/poker/home.html','<h3>Find the question you are working on.</h3>', '<div class="reader-shortcuts"><a href="/poker/decision-labs/">Explore all three Decision Labs</a><a href="/poker/flush-and-redraw/">Follow the flush and the redraw</a><a href="/poker/side-pot-lab/">Untangle a three-way all-in</a></div><h3>Find the question you are working on.</h3>')
replace('_source/poker/library.html','<a href="/poker/decision-lab/">Featured: one river, two stories</a>','<a href="/poker/decision-labs/">Explore three Decision Labs</a>')
replace('_source/poker/study.html','Study workshops and a Decision Lab.','Workshops and three Decision Labs.')
replace('_source/poker/study.html','Workshops &amp; Decision Lab','Workshops &amp; Decision Labs')
replace('_source/poker/study.html','<div class="viewer-library-grid">','<div class="viewer-library-grid">\n<article><p class="note-category">Decision Lab / 02</p><h3><a href="/poker/flush-and-redraw/">The flush arrives. What can still change?</a></h3><p>Follow a face-up replay, enumerate the rivers and test a changed opponent hand.</p></article>\n<article><p class="note-category">Decision Lab / 03</p><h3><a href="/poker/side-pot-lab/">Three all-ins. Two pots.</a></h3><p>Assign each chip to the right pot or refund, then explain the complete result.</p></article>')
css='''
/* Decision Lab series and optional in-page navigation. */
.reader-outline { max-width:780px; margin-top:22px; border-top:1px solid var(--line-dark); border-bottom:1px solid var(--line-dark); font:.92rem/1.6 var(--sans); }
.reader-outline > summary { cursor:pointer; min-height:44px; padding:14px 4px; font-weight:600; }
.reader-outline-count { margin-left:12px; font:.74rem/1.6 var(--mono); color:var(--ink-soft); }
.reader-outline ol { columns:2; column-gap:30px; margin:0 0 18px; padding-left:24px; }
.reader-outline li { break-inside:avoid; margin:0 0 8px; padding-left:3px; }
.reader-outline a { display:inline-flex; min-height:44px; align-items:center; overflow-wrap:anywhere; text-underline-offset:.2em; }
.reader-outline summary:focus-visible,.reader-outline a:focus-visible,.lab-series-card a:focus-visible { outline:3px solid var(--red); outline-offset:4px; }
.lab-series-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:18px; margin-top:30px; }
.lab-series-card { min-width:0; padding:24px; border:1px solid var(--line-dark); border-top:3px solid var(--red); background:var(--paper-light); }
.lab-series-card h3 { font:700 1.4rem/1.25 var(--sans); letter-spacing:-.025em; margin:0 0 22px; }
.lab-series-card h3 a { color:inherit; text-underline-offset:.2em; }
.lab-series-card > p:not(.reader-eyebrow) { font:1rem/1.7 var(--serif); }
.lab-series-card .lab-skill { padding-top:18px; margin-bottom:0; border-top:1px solid var(--line); }
.lab-hand-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:24px; margin:22px 0; }
.lab-hand-grid h3 { font:700 1.25rem/1.3 var(--sans); margin-bottom:16px; }
.lab-three-hands { grid-template-columns:repeat(3,minmax(0,1fr)); }
.lab-three-hands p { font:500 .95rem/1.5 var(--mono); }
.lab-pot-layers { display:grid; gap:14px; margin:24px 0; }
.lab-pot-layers > div { border:1px solid var(--line-dark); border-left:4px solid var(--red); padding:20px; background:var(--panel); }
.lab-pot-layers > div:nth-child(2) { border-left-style:double; border-left-width:6px; }
.lab-pot-layers > div:nth-child(3) { border-left-style:dashed; background:var(--paper-light); }
.lab-pot-layers .reader-eyebrow { display:block; }
.lab-pot-layers strong { display:block; font:700 1.75rem/1.25 var(--sans); }
.lab-pot-layers p { margin:12px 0 0; }
@media(max-width:1050px) { .lab-series-grid { grid-template-columns:minmax(0,1fr); } }
@media(max-width:760px) { .reader-outline ol { columns:1; } .lab-hand-grid,.lab-three-hands { grid-template-columns:minmax(0,1fr); } .lab-series-card { padding:20px; } }
@media print { .reader-outline { display:none; } .lab-series-grid,.lab-hand-grid { display:block; } .lab-series-card { break-inside:avoid; margin-bottom:18px; } .lab-pot-layers > div { break-inside:avoid; background:white; color:black; } }

.lab-series-card { display:flex; flex-direction:column; }
.lab-series-card > .reader-cards { margin-bottom:18px; }
.lab-series-card .lab-skill { margin-top:auto; }
@media(min-width:1051px) { .lab-series-card h3 { min-height:2.5em; } }
'''
f=ROOT/'assets/poker-reader.css';f.write_text(f.read_text()+css,encoding='utf-8')
