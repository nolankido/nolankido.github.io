"""Living Well: static editorial pages, explicit evidence status, and local resource discovery."""
from __future__ import annotations
from datetime import datetime, timezone
from email.utils import format_datetime
from hashlib import sha256
from html import escape, unescape
from pathlib import Path
import json
import math
import re
from xml.etree import ElementTree as ET
import living_well_resources as resources
import living_well_directory as directory
import living_well_utility as utility

DATE = '2026-10-08'
PREFIX = '/living-well/'
TOPICS = [
    ('meaning', 'Meaning & spirituality', 'Wonder, uncertainty, gratitude, ritual, and the question of what matters.', 'Spiritual inquiry does not have to become a productivity technique. Start with a question you genuinely care about, and distinguish what you experienced from what you think it means.', ['spiritually-curious', 'ordinary-moments', 'ai-generated-reflections']),
    ('attention', 'Attention & presence', 'Make room to experience life, not just organize or document it.', 'The aim is not a perfect screen-time score. It is a workable relationship with your attention, your responsibilities, and the people and places around you.', ['time-you-save', 'quiet-morning', 'documenting-your-life']),
    ('everyday-ai', 'AI for everyday life', 'Small, understandable uses of technology, with a simpler alternative beside them.', 'Begin with a real inconvenience rather than a new subscription. These guides keep the purpose, the information you share, the checks you must make, and the option not to use AI visible.', ['weekly-reset', 'household-friction', 'free-afternoon']),
    ('relationships', 'Relationships & care', 'Remember, listen, follow through, and keep the human part human.', 'A relationship is not a system to optimize. Technology can support logistics and expression, but it should not manufacture your feelings, assume another person\'s motives, or take away their choices.', ['preserve-family-story', 'what-to-decide-yourself', 'thoughtful-friend']),
    ('choices', 'Choices & growth', 'Clarify values, make decisions, and improve without treating yourself as a defect.', 'Some decisions trade one worthwhile life for another. A useful method makes the tradeoffs easier to see without pretending that a score, a prompt, or a disappointing outcome settles everything.', ['decide-what-matters', 'growth-without-self-rejection', 'two-good-lives']),
]
KINDS = {'essay': 'Essay', 'guide': 'Practical guide', 'experiment': 'Proposed experiment'}

def date_label(value: str) -> str:
    date = datetime.strptime(value, '%Y-%m-%d')
    return f'{date.strftime("%B")} {date.day}, {date.year}'

HUBS = [
    ('', 'Living Well', 'Spirituality, practical wisdom, and technology for everyday life.'),
    ('free-resources', 'Free resources for a thoughtful ordinary life', 'A curated directory of useful tools, thoughtful reading, and free learning, with task-based choices and clear access requirements.'),
    ('ideas', 'Essays, notes & reading paths', 'Essays about meaning, attention, relationships, and the kind of life our tools are meant to serve.'),
    ('guides', 'Try something useful', 'Practical guides with a simple starting point, an optional technology-assisted approach, and clear stopping rules.'),
    ('field-notes', 'Field notes & small experiments', 'Ready-to-try experiment plans, with proposed methods kept separate from completed personal findings.'),
    ('topics', 'Five ways into Living Well', 'Browse meaning, attention, everyday AI, relationships, and choices without needing a particular belief system.'),
    ('worksheets', 'Private-use worksheets', 'Five blank, printable or editable worksheets. No account, answer box, upload, or AI subscription required.'),
    ('conversations', 'A conversation worth having', 'Open-ended questions for a real conversation about meaning, technology, and how ordinary life is changing.'),
    ('editorial-standards', 'How to read and trust this section', 'The distinctions between reflection, spiritual interpretation, evidence, practical guidance, and firsthand experience.'),
    ('sources', 'Sources & further reading', 'A small annotated reading shelf, with each source linked to the limited claims it actually supports.'),
]
SHEETS = [
    ('weekly-reset', 'A small weekly reset', 'For a week that feels scattered. Capture commitments, choose what matters, and leave breathing room.', 'weekly-reset', '''# A small weekly reset
Living Well | Nolan Kido
Blank worksheet for private use. Optional, not a scorecard.

Week of:
What genuinely needs attention this week?
Which dates or obligations did I verify against the original source?
What can wait, be declined, or be simplified?
One person I would like to show up for:
One thing I would like to enjoy without making it productive:
The smallest useful next action:
What will I deliberately leave unplanned?
At the end of the week: did this page help, or add work?

Optional AI use: share only a de-identified task list. Verify dates yourself.
Do not include passwords, private correspondence, health records, or another person's story.
No need to upload the completed worksheet to this website.
'''),
    ('values-before-advice', 'Values before advice', 'For a decision that needs clarification, not a machine-generated verdict.', 'decide-what-matters', '''# Values before advice
Living Well | Nolan Kido
Blank worksheet for private use. Not professional advice.

The decision, in one sentence:
What matters most here, and why?
Who else is affected, and what have they actually said?
My non-negotiable constraints:
Options, including doing less or postponing:
Facts checked against an original source:
Assumptions that could be wrong:
What I give up with each option:
What would change my mind?
A small reversible test, where appropriate:
What needs a real conversation or qualified help?
My next action and a sensible review point:

Optional AI use: ask for missing questions or competing interpretations, not a verdict.
Do not use a single score to decide another person's rights, needs, or worth.
'''),
    ('family-story', 'A family story, with permission', 'For a small, consent-led recording or written conversation. This planning aid is not a legal release.', 'preserve-family-story', '''# A family story, with permission
Living Well | Nolan Kido
Blank planning aid. Not a legal consent or copyright form.

What story does the speaker want to tell?
Who is this for?
May I record? May I take notes instead?
What subjects should we avoid?
Where will the recording and copies be stored?
Who may listen or read?
Is a third-party transcription service acceptable to the speaker?
What will the speaker review before anything is shared?
Any restrictions on editing, excerpts, or future use?

Three open-ended questions:
1.
2.
3.

Afterwards:
Check names, dates, and uncertain passages with the speaker.
Keep the original recording separate from an edited copy.
Describe cuts or corrections; do not invent missing words.
Confirm permission for the specific version and audience.
Keep a backup in an agreed location and check that it opens.

Permission to record is not blanket permission to publish or clone a voice.
'''),
    ('small-experiment', 'One small experiment', 'For testing a low-stakes idea without turning a personal impression into scientific proof.', 'notebook-or-ai', '''# One small experiment
Living Well | Nolan Kido
Blank private field note. Status: proposed until actually completed.

The ordinary problem:
The change I will try:
The simplest alternative:
What I expect, written before I start:
What would count as useful, and what would count against the idea?
Start and review dates:
Setup time and ongoing effort:
Privacy, accessibility, care, or safety needs to preserve:
When I will stop or revert:

After trying it:
What I actually did, including missed attempts:
What changed:
What did not change:
Other things that might explain the difference:
Costs, friction, and unintended consequences:
Did this help someone beyond me?
Keep, change, stop, or still unsure?
What this small observation cannot establish:

Do not upload private answers. No result is required to justify stopping.
'''),
    ('attention-check', 'An attention check', 'For noticing interruptions without grading your character or disabling essential access.', 'quiet-morning', '''# An attention check
Living Well | Nolan Kido
Blank private reflection. No score, streak, or completion target.

One situation in which my attention feels pulled away:
What I intended to be doing:
Which interruptions were genuinely useful?
Which were not?
Who must still be able to reach me?
Accessibility, care, work, navigation, or safety functions I must preserve:
One small change to try:
An easy way to reverse it:
What I would like to make room for instead:
Afterwards: did I participate more fully, or just measure more things?

A paper note is enough. No tracking app is required.
'''),
]


def load(root: Path) -> list[dict]:
    entries = []
    for name in ('launch.json', 'further.json', 'discovery.json', 'expansion.json'):
        data = json.loads((root / '_source/living-well' / name).read_text(encoding='utf-8'))
        entries.extend(data['entries'])
    seen = set()
    topics = {t[0] for t in TOPICS}
    for entry in entries:
        slug = entry['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in seen:
            raise ValueError('Invalid or duplicate Living Well slug: ' + slug)
        seen.add(slug)
        published = entry.get('published')
        if not isinstance(published, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', published):
            raise ValueError('Living Well needs an explicit publication date: ' + slug)
        date_label(published)
        if entry.get('updated'):
            date_label(entry['updated'])
            if entry['updated'] < published:
                raise ValueError('A Living Well revision cannot precede publication')
        if entry.get('revision') and not entry.get('updated'):
            raise ValueError('A Living Well revision needs an update date')
        if entry['topic'] not in topics or entry['kind'] not in KINDS:
            raise ValueError('Invalid Living Well topic or kind: ' + slug)
        if entry.get('format') not in {None, 'reading-path', 'practice-path', 'short-read'}:
            raise ValueError('Unknown Living Well reading format')
        if not entry['sections'] or not entry.get('question'):
            raise ValueError('Living Well entries need substance and a closing question')
        if entry.get('format') == 'practice-path' and entry['kind'] != 'guide':
            raise ValueError('Practice paths must be guides')
        if entry.get('format') == 'short-read' and entry['kind'] != 'essay':
            raise ValueError('Short reads must be essays')
        if not isinstance(entry.get('sources', []), list):
            raise ValueError('Living Well sources must be a list')
        for citation in entry.get('sources', []):
            if not isinstance(citation, dict):
                raise ValueError('Living Well source must be an object')
            for field in ('label', 'url', 'note', 'checked'):
                if not isinstance(citation.get(field), str) or not citation[field].strip():
                    raise ValueError('Missing Living Well source field: ' + field)
            resources.safe_url(citation['url'])
            date_label(citation['checked'])
        utility.validate(entry)
        headings = [s['heading'] for s in entry['sections']]
        if len(headings) != len(set(headings)):
            raise ValueError('Duplicate Living Well section heading: ' + slug)
        raw = json.dumps(entry)
        if re.search(r'<\s*(script|iframe|form|input|textarea|style)\b|\bon\w+\s*=|javascript:', raw, re.I):
            raise ValueError('Interactive or executable content is not permitted in Living Well prose')
    for entry in entries:
        if any(slug not in seen or slug == entry['slug'] for slug in entry.get('related', [])):
            raise ValueError('Invalid related Living Well reading: ' + entry['slug'])
    for resource in resources.load(root)['resources']:
        if resource['companion'] not in seen:
            raise ValueError('Unknown Living Well resource companion: ' + resource['companion'])
    collisions = seen & ({h[0] for h in HUBS} | {'topics'})
    if collisions:
        raise ValueError('Living Well route collision')
    return entries


def manifest(root: Path) -> list[dict]:
    pages = []
    for slug, title, description in HUBS:
        route = PREFIX + (slug + '/' if slug else '')
        pages.append({'id': 'living-well' + ('-' + slug if slug else ''), 'path': route,
                      'title': title, 'seo_title': title + ' | Nolan Kido', 'description': description,
                      'kicker': 'Nolan Kido / Living Well', 'source': 'living-well/page.html',
                      'section': 'living-well', 'living_well_hub': slug or 'home', 'updated': '2026-10-10' if slug in {'', 'guides', 'free-resources'} else '2026-10-09'})
    for slug, title, description, introduction, sequence in TOPICS:
        pages.append({'id': 'living-well-topic-' + slug, 'path': PREFIX + 'topics/' + slug + '/',
                      'title': title, 'seo_title': title + ' | Living Well | Nolan Kido',
                      'description': description, 'kicker': 'Living Well / Topics',
                      'source': 'living-well/page.html', 'section': 'living-well',
                      'living_well_topic': slug, 'updated': '2026-10-10'})
    for entry in load(root):
        pages.append({'id': 'living-well-' + entry['slug'], 'path': PREFIX + entry['slug'] + '/',
                      'title': entry['title'], 'seo_title': entry.get('seo_title', entry['title'] + ' | Nolan Kido'),
                      'description': entry['description'], 'kicker': 'Living Well / ' + entry_label(entry),
                      'source': 'living-well/page.html', 'section': 'living-well',
                      'living_well_entry': entry['slug'], 'living_well_kind': entry['kind'], 'date': entry['published'],
                      **{key: entry[key] for key in ('updated', 'revision') if entry.get(key)}})
    return pages + resources.manifest(root) + directory.manifest(root)


def minutes(entry: dict) -> int:
    text = entry['lead'] + ' '.join(s['heading'] + ' ' + ' '.join(s['paragraphs']) for s in entry['sections']) + entry.get('practice', '') + entry['question']
    text += ' '.join(c['label'] + ' ' + c['note'] for c in entry.get('sources', []))
    text += ' ' + utility.reading_text(entry)
    return max(1, math.ceil(len(re.findall(r'\b[\w\'-]+\b', unescape(re.sub('<[^>]+>', ' ', text)))) / 220))


def link(slug: str, title: str) -> str:
    return '<a href="' + PREFIX + escape(slug, quote=True) + '/">' + escape(title) + '</a>'


def entry_label(entry: dict) -> str:
    if entry.get('series') == utility.SERIES and entry['slug'] == utility.SERIES:
        return 'Practical starting point'
    return {'reading-path': 'Reading path', 'practice-path': 'Free practice path', 'short-read': 'Short read'}.get(entry.get('format'), KINDS[entry['kind']])


def cards(entries: list[dict]) -> str:
    result = []
    for e in entries:
        result.append('<article class="lw-card"><p class="lw-eyebrow">' + entry_label(e) + ' · ' + str(minutes(e)) + ' min read</p><h3>' + link(e['slug'], e['title']) + '</h3><p>' + escape(e['description']) + '</p></article>')
    return '<div class="lw-cards">' + ''.join(result) + '</div>'


def section(ident: str, label: str, title: str, content: str) -> str:
    return '<section class="section folio-row lw-section" aria-labelledby="' + ident + '"><div class="section-meta"><p class="section-label">' + label + '</p></div><div class="section-content"><h2 class="section-title" id="' + ident + '">' + title + '</h2>' + content + '</div></section>'


def topic_cards() -> str:
    return '<div class="lw-cards">' + ''.join('<article class="lw-card"><h3>' + link('topics/' + t[0], t[1]) + '</h3><p>' + escape(t[2]) + '</p></article>' for t in TOPICS) + '</div>'


def worksheet_exports() -> dict[Path, str]:
    return {Path('downloads/living-well-' + slug + '.md'): content for slug, title, desc, guide, content in SHEETS}


def source_notes(entry: dict) -> str:
    citations = entry.get('sources', [])
    if not citations:
        return ''
    return ('<aside class="lw-source-notes" aria-labelledby="sources-and-context"><h2 id="sources-and-context">Sources and context</h2>'
            + ''.join('<p>' + resources.external(c['url'], c['label']) + '. ' + escape(c['note'])
                + ' <span class="small-copy">Source checked <time datetime="' + escape(c['checked'], quote=True) + '">'
                + escape(date_label(c['checked'])) + '</time>.</span></p>' for c in citations) + '</aside>')


def article(entry: dict, entries: list[dict]) -> str:
    by_slug = {e['slug']: e for e in entries}
    body = '<article class="lw-article" aria-label="' + escape(entry['title'], quote=True) + '"><div class="article-body shell prose"><p class="article-lead">' + entry['lead'] + '</p>'
    body += utility.brief(entry)
    if entry['kind'] == 'experiment':
        body += '<aside class="lw-callout"><p><strong>Status: proposed experiment.</strong> This is a ready-to-try plan, not a completed trial, personal result, or claim of effectiveness. No findings are being reported.</p></aside>'
    for number, s in enumerate(entry['sections'], 1):
        body += '<h2 id="part-' + str(number) + '">' + escape(s['heading']) + '</h2>'
        body += ''.join('<p>' + p + '</p>' for p in s['paragraphs'])
    body += utility.starter(entry)
    if entry.get('practice'):
        body += '<aside class="lw-callout"><h2 id="try-it">One optional practice</h2><p>' + entry['practice'] + '</p><p class="small-copy">Keep any notes privately. Skip or adapt this exercise if it does not fit your circumstances.</p></aside>'
    # Preserve the introductory essay's original section/exercise bookmarks.
    if entry['slug'] == 'what-i-mean-by-living-well':
        body += '<span id="part-6"></span><span id="try-it"></span>'
    body += '<h2 id="one-question">One question to take with you</h2><p>' + entry['question'] + '</p>'
    body += '<p class="editorial-note">Prepared with AI assistance. These are editorial reflections and practical guides, not accounts of Nolan\'s personal experiences. Illustrative examples are hypothetical; sources and their context are identified where used. <a href="/living-well/editorial-standards/">Read the editorial standards</a>.</p>'
    body += source_notes(entry)
    if entry.get('related'):
        body += '<nav class="lw-next" aria-label="Related Living Well reading"><h2>Continue with a related question</h2>' + ''.join('<p>' + link(slug, by_slug[slug]['title']) + '</p>' for slug in entry['related'][:2]) + '</nav>'
    body += '<nav class="article-navigation" aria-label="After this article"><a href="/living-well/">Living Well home</a><a href="/living-well/topics/' + entry['topic'] + '/">More in this subject</a><a href="/contact/">Send a correction</a></nav></div></article>'
    return body


def render(page: dict, root: Path) -> str:
    if page.get('directory_kind'):
        return directory.render(root, page, section)
    if page.get('living_well_collection'):
        return resources.detail(root, page['living_well_collection'], section)
    entries = load(root)
    by_slug = {e['slug']: e for e in entries}
    if page.get('living_well_entry'):
        return article(by_slug[page['living_well_entry']], entries)
    if page.get('living_well_topic'):
        topic = next(t for t in TOPICS if t[0] == page['living_well_topic'])
        sequence = [by_slug[s] for s in topic[4]]
        more = [e for e in entries if e['topic'] == topic[0] and e['slug'] not in topic[4]]
        body = section('start-reading', 'Start here', 'A useful starting sequence', '<p class="section-deck">' + escape(topic[3]) + '</p>' + cards(sequence))
        if more:
            body += section('further-reading', 'Go further', 'Another angle', cards(more))
        return body + section('across-subjects', 'Keep exploring', 'Another way in.', resources.related_shelf(topic[0]) + '<p class="section-deck">A practical problem can open a larger question. Browse another subject, or take one idea into ordinary life before reading more.</p><p><a href="/living-well/topics/">All five subjects</a> · <a href="/living-well/worksheets/">Private-use worksheets</a></p>')
    hub = page['living_well_hub']
    if hub == 'home':
        return resources.home(root, entries, section, cards, topic_cards)
    if hub == 'free-resources':
        return resources.render(root, section)
    if hub in {'ideas', 'guides'}:
        kind = 'essay' if hub == 'ideas' else 'guide'
        intro = ('You do not need to agree with every argument or settle a spiritual identity before reading. These are invitations to examine a question, not declarations of universal truth.' if kind == 'essay' else 'Each guide starts with an ordinary situation. Use the no-AI route first when it is enough, share less rather than more, verify important details, and stop when the method becomes more work than the problem.')
        collection = [e for e in entries if e['kind'] == kind]
        if kind == 'essay':
            paths = [e for e in collection if e.get('format') == 'reading-path']
            short_reads = [e for e in collection if e.get('format') == 'short-read']
            essays = [e for e in collection if e.get('format') not in {'reading-path', 'short-read'}]
            return (section('reading-paths', 'A few places to begin', 'Follow a question.',
                    '<p class="section-deck">Selected routes through a question, with reasons to explore the sources rather than a syllabus to finish.</p>' + cards(paths))
                    + section('short-reads', 'A shorter visit', 'Worth a few minutes.', '<p class="section-deck">One specific thing to read or notice, without a program to complete.</p>' + cards(short_reads))
                    + section('reading-collection', 'Read at your pace', 'Essays to explore.', '<p class="section-deck">' + intro + '</p>' + cards(essays)))
        paths = [e for e in collection if e.get('format') == 'practice-path']
        collection = [e for e in collection if e.get('format') != 'practice-path']
        projects = [e for e in collection if e.get('series') == utility.SERIES]
        collection = [e for e in collection if e.get('series') != utility.SERIES]
        return section('free-practice-paths', 'No paid plan needed', 'Find a starting point.', '<p class="section-deck">Start with an ordinary task or a low-pressure practice. Neither requires a new subscription.</p>' + cards(paths)) + section('real-life-guides', 'Technology for real life', 'Leave with something useful.', '<p class="section-deck">Seven worked guides with a simple starting point, a reusable text template, and a clear way to check the result. AI is optional.</p>' + cards(projects)) + section('reading-collection', 'Try something', 'One useful change is enough.',
            '<p class="section-deck">' + intro + '</p><p><a href="/living-well/weekly-reset/#part-7">Start with a fictional worked example</a> · '
            '<a href="/living-well/worksheets/">Use a blank worksheet</a> · <a href="/living-well/free-resources/">Find a free outside resource</a></p>' + cards(collection))
    if hub == 'topics':
        return section('subject-map', 'Browse by subject', 'Five subjects, one human purpose.', '<p class="section-deck">You can explore spirituality without adopting a doctrine, and use technology without making it the center of your life. Each subject has a short reading sequence and a different angle to explore next.</p>' + topic_cards())
    if hub == 'field-notes':
        body = section('honest-status', 'Evidence status', 'A plan is not a result.', '<p class="section-deck">No completed personal field notes are published here yet. The three plans below are usable now, but they do not claim that Nolan has carried them out or that they will work for you.</p><p>Choose a small, reversible change. Write down what would count against the idea as well as what you hope to see. An awkward, inconclusive, or abandoned attempt can be informative.</p>' + cards([e for e in entries if e['kind'] == 'experiment']))
        body += section('reporting-method', 'What happened?', 'The field-note format', '<div class="prose"><p>A completed note should name the original problem, the actual dates and circumstances, the change tried, setup and maintenance effort, observations, competing explanations, and the decision to keep, modify, or stop. It should say what the experience cannot establish.</p><p>Observations from one person are not a controlled demonstration of a general benefit. Record departures from the plan rather than rewriting the plan to make the result look cleaner. Do not infer another person\'s feelings without asking them.</p><p>A future conversation or photograph will be published only with suitable permission. No testimonial, interview, or personal result has been invented to fill this collection.</p><p><a href="/downloads/living-well-small-experiment.md" download>Download the blank field-note worksheet</a> or <a href="/living-well/worksheets/#small-experiment">preview it before downloading</a>.</p></div>')
        return body
    if hub == 'worksheets':
        body = section('keep-your-answers', 'Private by design', 'Use these away from the website.', '<p class="section-deck">Read a guide first, then use the blank page that fits. Read the prompts below without downloading anything. For a paper copy, use your browser’s print command; all five blank sheets are included. An editable plain-text (Markdown) file is also available for each sheet.</p><p>There are no answer fields or uploads here. This section does not collect worksheet responses. Ordinary page visits still follow the site\'s <a href="/privacy/">existing privacy notice</a>. A third-party AI service has its own data practices.</p>')
        body = body.replace('class="section folio-row lw-section"', 'class="section folio-row lw-section lw-worksheet-intro"', 1)
        for slug, title, desc, guide, content in SHEETS:
            sheet = section(slug, 'Blank worksheet', escape(title), '<p class="section-deck">' + escape(desc) + '</p><div class="link-row"><a href="/downloads/living-well-' + slug + '.md" download>Download editable text (.md)</a>' + link(guide, 'Read the companion guide') + '</div><details class="lw-preview" open><summary>Blank worksheet: read here or print</summary><pre>' + escape(content) + '</pre></details>')
            klass = 'lw-worksheet-sheet' + (' lw-worksheet-first' if slug == SHEETS[0][0] else '')
            body += sheet.replace('class="section folio-row lw-section"', 'class="section folio-row lw-section ' + klass + '"', 1)
        return body
    if hub == 'conversations':
        return section('conversation-not-content', 'With another person', 'A conversation, not an interview to extract.', '<div class="prose"><p>This is a guide you can use now, not a transcript of a conversation that has already happened. Invite someone who wants to participate. A disagreement can be interesting without becoming a debate to win, and a conversation does not have to become publishable content.</p><h3>Begin with permission and a manageable question</h3><p>Ask whether the topic interests them. Agree that either person may skip a question, change direction, or stop. Listening without recording is the simplest starting point. Do not use an AI listener, transcription service, or recording device without discussing it first.</p><h3>Six questions to choose from</h3><ol><li>What ordinary moment has felt meaningful to you recently?</li><li>Is there a question you are more comfortable leaving open than you used to be?</li><li>What does spiritual language help you express, and what does it make harder?</li><li>Where has technology made it easier for you to show up for someone?</li><li>What part of your life would you rather not measure or optimize?</li><li>What have you changed your mind about, and what helped you reconsider?</li></ol><h3>Stay with the answer</h3><p>Ask for the speaker\'s meaning rather than supplying yours. What did that word mean to them? Did their interpretation change? What do they still find difficult? Do not turn a pause into a demand for a dramatic revelation. Their experience is not a general proof of a spiritual or scientific claim.</p><h3>End without converting the person into content</h3><p>You can simply thank them and keep the exchange between you. Before sharing a quotation, recording, transcript, or AI-assisted summary, agree on the exact version, audience, and attribution. Make room for corrections and for material to remain private. A yes to talking is not automatically a yes to publication.</p><p>For a recorded family conversation, use the more detailed <a href="/living-well/preserve-family-story/">family-story guide</a>. The consent and review approach there draws on the <a href="https://oralhistory.org/oha-statement-on-ethics/">Oral History Association\'s ethics guidance</a>.</p><p><strong>One question afterwards:</strong> Did I become more curious about this person, or mostly more interested in explaining myself?</p></div>')
    if hub == 'editorial-standards':
        return section('what-kind-of-claim', 'Editorial standards', 'Keep the kinds of knowledge distinct.', '<div class="prose"><p>Living Well explores spirituality, practical wisdom, and technology. It is not a spiritual authority, a clinical service, or a promise that the right routine can solve every difficulty.</p><h3>Reflection is not research</h3><p>Essays offer interpretations and arguments. Spiritual possibilities are not presented as established mechanisms. A moving experience can matter to someone without proving its proposed explanation. Research claims need identifiable sources, appropriate context, and limits. Practical exercises are invitations, not validated treatments.</p><h3>Traditions deserve specificity</h3><p>When a piece discusses a tradition, it should name the particular tradition, source, interpreter, and context rather than claim that all religions or philosophies teach the same thing. This launch collection does not claim lineage, initiation, or authority within a spiritual tradition. Readers may approach the questions through faith, uncertainty, or secular thought.</p><h3>No invented experience</h3><p>The initial essays and guides were prepared with AI assistance. They do not claim that Nolan has had the experiences described, completed the proposed experiments, or conducted an interview. Hypothetical examples are labeled. Real field notes require actual observations and clear limits. A future first-person story must come from its human author.</p><h3>AI is assistance, not revelation</h3><p>Verify quotations, citations, dates, and practical details against appropriate originals. Do not treat an AI response as evidence of hidden destiny, another person\'s motives, or the user\'s spiritual status. NIST\'s generative AI profile identifies false outputs, privacy risks, and problematic human reliance as risk areas; see the <a href="/living-well/sources/">source notes</a>.</p><h3>Agency, access, and privacy</h3><p>No exercise requires uploading intimate thoughts. No guide requires buying a subscription. Keep essential accessibility, care, and safety functions intact when changing technology use. Some difficulties require material support, a change in circumstances, or qualified help rather than an individual habit. Skip exercises that are not useful or feel distressing.</p><h3>Corrections and publication dates</h3><p>Publication dates are explicit. A substantive revision should display its date and explain what changed instead of silently resetting the original date. Use the <a href="/contact/">contact page</a> to identify a specific passage, source, or broken link. Do not send private worksheet answers or another person\'s confidential story.</p><h3>No hidden commercial agenda</h3><p>The launch collection contains no affiliate links or sponsored recommendations. Any future commercial relationship should be disclosed next to the relevant material. Links in the reading shelf identify sources, not blanket endorsements.</p></div>')
    if hub == 'sources':
        return section('reading-shelf', 'Primary sources', 'A small shelf with a clear purpose.', '<div class="prose"><p>Looking for something to read, hear, or try? <a href="/living-well/free-resources/">Browse the free-resource collection</a>. This page explains sources behind specific article claims. The launch essays are principally original editorial arguments. The sources below support specific risk and oral-history guidance. They do not establish that the optional practices improve wellbeing or prove any spiritual interpretation. Links were checked during the October 8, 2026 build.</p><h3>NIST: Generative Artificial Intelligence Profile</h3><p><a href="https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence">Read the publication page</a> or <a href="https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf">the report (PDF)</a>. The 2024 profile discusses confabulation, data privacy, and human-AI configuration among its risk areas. It informs the cautions about verification and dependence in <a href="/living-well/ai-generated-reflections/">AI-generated reflections</a> and <a href="/living-well/decide-what-matters/">values before advice</a>. It is a risk-management document, not a study validating the exercises on this website.</p><h3>Oral History Association: ethics and best practices</h3><p><a href="https://oralhistory.org/oha-statement-on-ethics/">Read the ethics statement</a> and <a href="https://oralhistory.org/best-practices/">best-practice guidance</a>. These support the emphasis on informed participation, agreed use, narrator review, and preservation in the <a href="/living-well/preserve-family-story/">family-story guide</a>. The website\'s worksheet is an editorial planning aid, not the association\'s form or a legal release.</p><h3>Library of Congress: preserving family stories</h3><p><a href="https://blogs.loc.gov/families/2020/09/preserving-family-stories/">Read Preserving Family Stories</a>. This introduction offers a way into oral-history collections and family interviewing. Use it to broaden your questions, not to assume that any person owes you a recorded story.</p><h3>Two related places on this website</h3><p><a href="/notes/trustworthy-tools/">A working tool versus a trustworthy one</a> examines independent checks. <a href="/resources/#decision-record">The decision-record worksheet</a> helps preserve what was known at the time of a decision. The <a href="/technology/">Technology section</a> focuses on tools; Living Well asks what those tools are for.</p><h3>How this shelf will grow</h3><p>Add sources when a real article needs them. Prefer the original work, identify translations or adaptations, and explain disagreements. A long link list is not a substitute for reading carefully. Broken links and misattributions can be reported through <a href="/contact/">contact</a>.</p></div>')
    raise ValueError('Unknown Living Well hub: ' + str(hub))


def section_navigation(page: dict) -> str:
    if not page['path'].startswith(PREFIX):
        return ''
    active = 'free-resources' if page.get('living_well_collection') else page.get('living_well_hub')
    if page.get('living_well_entry') == 'what-i-mean-by-living-well':
        active = 'start'
    elif page.get('living_well_kind'):
        active = {'essay': 'ideas', 'guide': 'guides', 'experiment': 'field-notes'}[page['living_well_kind']]
    elif page.get('living_well_topic'):
        active = 'topics'
    primary = [('what-i-mean-by-living-well', 'Start here', 'start'),
               ('ideas', 'Essays &amp; paths', 'ideas'), ('free-resources', 'Free resources', 'free-resources'),
               ('guides', 'Try something', 'guides')]
    secondary = [('', 'Home', 'home'), ('topics', 'Topics', 'topics'),
                 ('worksheets', 'Worksheets', 'worksheets'), ('field-notes', 'Field notes', 'field-notes')]
    def navigation(items):
        result = []
        for slug, label, key in items:
            route = PREFIX + (slug + '/' if slug else '')
            current = ' aria-current="page"' if page['path'] == route else (' aria-current="location"' if active == key else '')
            result.append('<a href="' + route + '"' + current + '>' + label + '</a>')
        return ''.join(result)
    return ('<div class="subsite-bar"><div class="shell"><span class="subsite-name">Nolan Kido / Living Well</span>'
            '<nav class="subsite-links" aria-label="Living Well section">' + navigation(primary) + '</nav>'
            '<nav class="lw-secondary-links" aria-label="More Living Well">' + navigation(secondary) + '</nav></div></div>')


def decorate(page: dict, root: Path, header: str, schema: dict) -> tuple[str, str]:
    if not page['path'].startswith(PREFIX):
        return header, ''
    extra = '\n  <link rel="stylesheet" href="/assets/living-well.css?v=' + sha256((root / 'assets/living-well.css').read_bytes()).hexdigest()[:12] + '">\n  <link rel="alternate" type="application/rss+xml" title="Nolan Kido Living Well" href="/living-well/feed.xml">'
    if page.get('directory_kind'):
        extra += directory.header(root, page)
    crumbs = '<nav class="lw-breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true"> / </span><a href="/living-well/">Living Well</a>'
    if page.get('living_well_entry'):
        entry = next(e for e in load(root) if e['slug'] == page['living_well_entry'])
        topic = next(t for t in TOPICS if t[0] == entry['topic'])
        crumbs += '<span aria-hidden="true"> / </span>' + link('topics/' + topic[0], topic[1])
        meta = '<p class="note-meta">' + entry_label(entry) + ' · ' + str(minutes(entry)) + ' min read · Published <time datetime="' + page['date'] + '">' + date_label(page['date']) + '</time></p>'
        if page.get('revision'):
            meta += '<p class="editorial-note"><strong>Revision, <time datetime="' + page['updated'] + '">' + page['updated'] + '</time>:</strong> ' + escape(page['revision']) + '</p>'
        outline = '<details class="lw-outline"><summary>On this page</summary><nav aria-label="On this page"><ol>' + ''.join('<li><a href="#part-' + str(i) + '">' + escape(s['heading']) + '</a></li>' for i, s in enumerate(entry['sections'], 1)) + '<li><a href="#one-question">One question to take with you</a></li></ol></nav></details>'
        outline = utility.outline(entry, outline)
        if entry.get('sources'):
            outline = outline.replace('</ol>', '<li><a href="#sources-and-context">Sources and context</a></li></ol>', 1)
        header = header.replace('</section>', meta + outline + '</section>', 1)
        schema.update({'@type': 'Article', 'headline': page['title'], 'datePublished': page['date'], 'author': {'@type': 'Person', 'name': 'Nolan Kido', 'url': 'https://nolankido.com/about/'}})
        extra += '\n  <meta property="article:published_time" content="' + page['date'] + '">'
        if page.get('updated'):
            extra += '\n  <meta property="article:modified_time" content="' + page['updated'] + '">'
    else:
        schema['@type'] = 'CollectionPage' if page.get('living_well_collection') or page.get('living_well_topic') or page.get('living_well_hub') in {'home', 'ideas', 'guides', 'topics', 'field-notes', 'free-resources'} else 'WebPage'
    if page.get('living_well_collection') or page.get('directory_kind'):
        crumbs += '<span aria-hidden="true"> / </span><a href="/living-well/free-resources/">Free resources</a>'
    crumbs += '</nav>'
    if page['path'] != PREFIX:
        header = header.replace('<p class="page-kicker">', crumbs + '<p class="page-kicker">', 1)
    return header, extra


def exports(root: Path, site_url: str) -> dict[Path, str]:
    result = worksheet_exports()
    rss = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(rss, 'channel')
    for k, v in [('title', 'Nolan Kido Living Well'), ('link', site_url + PREFIX), ('description', 'Spirituality, practical wisdom, and technology for everyday life.'), ('language', 'en-us')]:
        ET.SubElement(channel, k).text = v
    ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link', {'href': site_url + PREFIX + 'feed.xml', 'rel': 'self', 'type': 'application/rss+xml'})
    for entry in sorted(load(root), key=lambda e: (e['published'], e['slug']), reverse=True):
        if entry['kind'] == 'experiment':
            continue
        item = ET.SubElement(channel, 'item')
        url = site_url + PREFIX + entry['slug'] + '/'
        for k, v in [('title', entry['title']), ('link', url), ('description', entry['description'])]:
            ET.SubElement(item, k).text = v
        ET.SubElement(item, 'guid', {'isPermaLink': 'true'}).text = url
        ET.SubElement(item, 'pubDate').text = format_datetime(datetime.strptime(entry['published'], '%Y-%m-%d').replace(tzinfo=timezone.utc), usegmt=True)
    ET.indent(rss, space='  ')
    result[Path('living-well/feed.xml')] = '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(rss, encoding='unicode') + '\n'
    return result
