"""Preparation-only deterministic edits, removed from the final release tree."""
from pathlib import Path
import re,json,subprocess,hashlib
root=Path(__file__).resolve().parents[1]
def read(p):return (root/p).read_text()
def write(p,s):(root/p).write_text(s,encoding='utf-8')
s=read('_source/home.html')
steps={
 'technology':('/technology/task-brief/','Build an AI task brief','A browser tool for defining the task, boundaries, and checks. No AI runs here.'),
 'living-well':('/living-well/worksheets/#weekly-reset','Make room in your week','A blank weekly-reset worksheet to use privately in your own notes.'),
 'poker':('/poker/study-calculators/','Check the poker math','Study calculators with visible assumptions. For review away from play, not strategy advice.'),
 'creative':('/creative/#creative-brief','Plan a small creative piece','A blank brief for the reader, idea, material, and finish line.')}
for key,(href,label,desc) in steps.items():
 m=re.search(rf'<a class="destination destination-{key}".*?</a>',s,re.S)
 assert m,key
 block=m.group(0)
 block=re.sub(r'^<a class="destination destination-'+key+r'"[^>]*>',f'<article class="destination destination-{key}" aria-labelledby="{key}-destination-title">',block)
 match=re.search(rf'<span class="destination-action" id="{key}-destination-action">(.*?)<span aria-hidden="true">→</span></span>\s*</a>$',block,re.S)
 assert match,key
 section='/'+key+'/'
 action=(f'<div class="destination-links"><a class="destination-action" id="{key}-destination-action" href="{section}">{match.group(1)}<span aria-hidden="true">→</span></a>'
  f'<div class="destination-first"><p class="destination-first-label">A useful first step</p><a class="destination-first-link" href="{href}">{label} <span aria-hidden="true">→</span></a><p class="destination-first-note">{desc}</p></div></div>\n      </article>')
 block=block[:match.start()]+action
 s=s[:m.start()]+block+s[m.end():]
s=s.replace('Technology is a means, not the whole point. These are the interests it sits alongside.','Explore a subject, or go straight to something you can use. Technology is a means, not the whole point.')
write('_source/home.html',s)
write('downloads/creative-brief.txt','''ONE SMALL CREATIVE PIECE
A blank planning sheet from Nolan Kido
https://nolankido.com/creative/#creative-brief

Use only the prompts that help. Complete your copy privately.
This is a thinking aid, not a scoring system or a publication checklist.

READER OR VIEWER
Who is this for? What do they already know?

ONE IDEA
What should they understand, notice, or feel?

SMALLEST USEFUL FORM
A short note, a single scene, a few pictures, or another small format:
What belongs in this version? What can wait?

MATERIAL AND PERMISSION
What facts, observations, or source material can I support?
What is uncertain or remembered rather than recorded?
Whose words, image, or story require permission before sharing?
Keep private details and other people's personal material out of public copies.

THREE BEATS
Opening: give the person a reason to care.
Middle: show the detail, change, or example that matters.
Ending: leave them with one clear thought or next step.

OPTIONAL AI ASSISTANCE
What limited help would be useful: organizing, alternatives, or a clarity check?
What must remain in my voice or under my control?
Do not upload private or restricted material without authorization.
Check any suggested facts, quotations, or claims against the source.

READY ENOUGH TO SHARE
What would let the intended person follow this piece?
What factual, permission, or accessibility questions still need resolving?
What is one optional improvement I can leave for another version?

NEXT ACTION
One small action I can take, or a reason to set this aside:
''')
write('_source/creative/home.html','''<section class="section folio-row topic-introduction" aria-labelledby="creative-intro-title">
  <div class="section-meta"><p class="section-label">Ideas into expression</p></div>
  <div class="section-content prose">
    <h2 class="intro" id="creative-intro-title">Make an idea connect.</h2>
    <p>I work with writing, design, and visual storytelling as ways of inviting someone into an idea. I am interested in the choices behind them: what to include, what to leave out, and where to give the reader room.</p>
    <p>Start with one person and one thing worth sharing. Use a small planning sheet, follow a guide, or read about the choices behind the work.</p>
    <div class="link-row"><a class="button" href="#creative-brief">Plan a small creative piece <span aria-hidden="true">↓</span></a><a class="text-link" href="#creative-reading">Explore the writing <span aria-hidden="true">↓</span></a></div>
    <nav class="creative-jumps" aria-label="On this creative page"><a href="#creative-brief">Use the brief</a><a href="#creative-practice">Choose a format</a><a href="#creative-reading">Read the thinking</a></nav>
  </div>
</section>
<section class="section folio-row" id="creative-brief" aria-labelledby="creative-brief-title">
  <div class="section-meta"><p class="section-label">One page, one idea</p></div>
  <div class="section-content prose">
    <h2 class="section-title" id="creative-brief-title">Give the idea a manageable shape.</h2>
    <p>The blank brief asks who the piece is for, what belongs in it, and what would make it ready enough to share. Use it for a short article, a video, a visual story, or another small piece. Skip the prompts that do not help.</p>
    <p><strong>The smallest useful version:</strong> name the person, name the idea, and choose the next action. The rest is there when you need it.</p>
    <div class="creative-brief-card"><p class="creative-brief-kind">Blank template / Plain text</p><h3>One small creative piece</h3><p>Reader → idea → material → three beats → finish line.</p><p class="small-copy">Includes a permission check and an optional place to define AI assistance. It does not generate a story or collect your answers.</p><a class="button" href="/downloads/creative-brief.txt" download>Download the creative brief (.txt)</a></div>
    <details class="creative-template"><summary>Read or copy the complete blank brief</summary><pre>${creative_brief}</pre></details>
    <p class="small-copy">No account is needed. Open the text file in your own notes or text editor and keep the completed copy private. This page has no answer form. Using a cloud notes app or AI service is a separate sharing decision.</p>
    <p class="small-copy">This is an AI-assisted planning aid, not a report of a completed personal project. A brief cannot establish permission, verify a fact, or guarantee that a piece will connect.</p>
  </div>
</section>
<section class="section folio-row" id="creative-practice" aria-labelledby="creative-practice-title">
  <div class="section-meta"><p class="section-label">From reading to making</p></div>
  <div class="section-content"><h2 class="section-title" id="creative-practice-title">Choose the kind of piece.</h2>
    <p class="section-deck">Three practical routes through material already on the site. These are approaches to try, not a portfolio of completed personal projects.</p>
    <div class="notes-list creative-routes">
      <article class="note-entry"><p class="note-category">Writing / A first version</p><h3><a href="/living-well/rough-idea-to-small-creation/">Turn a rough idea into something you can share.</a></h3><p>Choose a reader, a small scope, and a finish line. Use optional AI assistance without letting it replace the idea you wanted to express.</p><p class="creative-route-outcome"><strong>Work toward:</strong> one small version, rather than a growing list of possibilities.</p></article>
      <article class="note-entry"><p class="note-category">Visual storytelling / A poker-specific guide</p><h3><a href="/poker/hand-to-vlog/">From hand note to poker vlog</a></h3><p>Follow a poker-specific workflow from recorded action to narration, graphics, and a companion page. Separate what happened from later interpretation.</p><p class="creative-route-outcome"><strong>Work toward:</strong> a coherent explanation built from supportable facts. This is a guide, not a published vlog episode.</p></article>
      <article class="note-entry"><p class="note-category">Personal stories / Someone's voice</p><h3><a href="/living-well/preserve-family-story/">Preserve a family story without losing the person's voice.</a></h3><p>Start with permission, listen to the speaker, and let them review what you keep. The technology should serve the story.</p><p class="creative-route-outcome"><strong>Work toward:</strong> a version the speaker has had a chance to review, not a polished replacement for their voice.</p></article>
    </div>
    <p class="small-copy">For a broader view, <a href="/resources/#resources-creative">see the resource starting points</a>. For materials and tools, explore <a href="/living-well/free-resources/books-creativity/">free books, art, and creative resources</a> or <a href="/living-well/free-resources/creative-tools/">tools for making things</a>.</p>
  </div>
</section>
<section class="section folio-row" id="creative-reading" aria-labelledby="creative-reading-title">
  <div class="section-meta"><p class="section-label">Selected reading</p></div>
  <div class="section-content"><h2 class="section-title" id="creative-reading-title">The choices behind the work.</h2>
    <div class="notes-list">
      <article class="note-entry"><p class="note-category">Communication</p><h3><a href="/notes/generous-explanations/">What makes an explanation feel generous.</a></h3><p>Two versions of the same instruction show how writing can save the reader effort without simplifying away what matters.</p></article>
      <article class="note-entry"><p class="note-category">Making things &amp; making room</p><h3><a href="/notes/finishing-is-a-decision/">Finishing is a decision.</a></h3><p>Distinguish a necessary repair from another possible improvement, define done, and leave room for the rest of the day.</p></article>
    </div>
    <p class="small-copy">For related ideas across the site, <a href="/notes/#creative">browse the writing</a>. When AI would help with a defined part of the work, <a href="/technology/task-brief/">build a task brief</a> before delegating it.</p>
    <div class="link-row"><a class="text-link" href="/contact/">Talk about something you are making <span aria-hidden="true">→</span></a><a class="text-link" href="/">Back to Nolan Kido <span aria-hidden="true">→</span></a></div>
  </div>
</section>
''')
s=read('_source/resources.html')
s=s.replace('<p class="small-copy"><strong>Something to use now:</strong> <a href="/technology/task-brief/">Build an AI task brief</a> locally, with a blank template and three illustrative starting points.</p>', '<p class="small-copy"><strong>Something to use now:</strong> <a href="/technology/task-brief/">build an AI task brief</a> in the browser, or <a href="/creative/#creative-brief">plan a small creative piece</a> in your own notes. Both include a complete blank text template.</p>')
write('_source/resources.html',s)
pages=json.loads(read('_source/pages.json'))
for p in pages:
 if p['id']=='creative':
  p['description']='Writing, design, and visual storytelling. Use a blank creative brief, follow a practical making guide, or read Nolan Kido on explanation and finishing.'
  p['updated']='2026-10-11'
write('_source/pages.json',json.dumps(pages,ensure_ascii=False,indent=2)+'\n')
s=read('_scripts/build.py')
s=s.replace("values = {k: text(v) for k, v in site.items()}","values = {k: text(v) for k, v in site.items()}\n    # Keep the visible planning-sheet preview identical to its downloadable source.\n    values['creative_brief'] = text((ROOT / 'downloads/creative-brief.txt').read_text(encoding='utf-8'))")
s=s.replace("        if p['id'] == 'task-brief':", "        if p['id'] in {'home', 'creative'}:\n            starts_version = hashlib.sha256((ROOT / 'assets/first-steps.css').read_bytes()).hexdigest()[:12]\n            extra += f'\\n  <link rel=\"stylesheet\" href=\"/assets/first-steps.css?v={starts_version}\">'\n        if p['id'] == 'task-brief':")
write('_scripts/build.py',s)
s=read('_scripts/check_live.py');s=s.replace("    assets += ['assets/task-brief.css'", "    assets += ['assets/first-steps.css', 'downloads/creative-brief.txt']\n    assets += ['assets/task-brief.css'");write('_scripts/check_live.py',s)
s=read('_tests/design_browser.py')
for key in ['technology','creative','poker']:
 s=s.replace(f"page.locator('.destination-{key}').click()",f"page.locator('.destination-{key} .destination-action').click()")
write('_tests/design_browser.py',s)
s=read('_tests/test_gateway.py').replace("if tag == 'a' and 'destination' in", "if tag == 'a' and 'destination-action' in")
s=s.replace("self.assertIn('Start with selected writing on explanation', creative)","self.assertIn('Start with one person and one thing worth sharing.', creative)\n        self.assertIn('href=\"/downloads/creative-brief.txt\" download', creative)")
write('_tests/test_gateway.py',s)
s=read('_tests/test_poker_content.py').replace("BASELINE_DIGEST = 'ead5c431f430abcdab43770459f58ec45a301e889aec53415b2a016c3e1fa18d'", "# October 11: reviewed home first actions and Creative brief; protected sources remain unchanged.\nBASELINE_DIGEST = '2a73c46058e2d9e27be067d95545d31da576e22d5cc990cb44632ca2988e1492'")
write('_tests/test_poker_content.py',s)
s=read('_tests/test_viewer_next.py').replace('6cd9247237fd9e5cdee2c119966c72ee92e792cd67dbd3ee3ede0eeb8b3877bd','02049a0af1336c84d1a66c656ab70281ff12cb309feeca2c6c819b2ba788c3a3').replace('deb46f1ba2cf0e9ca0c31bace2dd7bde9a7e798b71233fc0d26e758dbc428389','d4db5c22e657eafd7079509e5129029d76ea7976fab9480fc67f7f31db3d18fc')
s=s.replace('# Original Poker source, contact code, design, site CSS, original feed and catalog hashes are retained.','# October 11: reviewed home first-step links and Creative blank-brief presentation.\n# Original Poker source, contact code, design, site CSS, original feed and catalog hashes are retained.')
write('_tests/test_viewer_next.py',s)
subprocess.run(['python','_scripts/build.py'],cwd=root,check=True)
# These are the independently reviewed local output fingerprints, not self-issued baselines.
for path,sha in {'index.html':'02049a0af1336c84d1a66c656ab70281ff12cb309feeca2c6c819b2ba788c3a3','creative/index.html':'d4db5c22e657eafd7079509e5129029d76ea7976fab9480fc67f7f31db3d18fc'}.items():
 assert hashlib.sha256((root/path).read_bytes()).hexdigest()==sha,path
