"""Optional, private course marks on the existing Poker Study Desk."""
from hashlib import sha256
from html import escape
import json

import poker_course


ROUTE = '/poker/study/'
CSS = 'assets/poker-progress.css'
SCRIPT = 'assets/poker-progress.js'
FORMAT = 'nolan-kido-poker-progress'
VERSION = 1
COURSE = 'poker-foundations'
STORAGE_KEY = 'nolan-kido:poker-foundations:progress:v1'
MAX_BYTES = 8192
STATES = (
    ('not-started', 'Not started'),
    ('working', 'Working on it'),
    ('practiced', 'Practiced'),
    ('revisit', 'Revisit'),
)


def config(root):
    """Bind marks to the canonical route and the instructional material it uses."""
    course = poker_course.load(root)
    material = {}
    for name in ['beginner-course.json', 'course-lessons.json', 'final-hands.json']:
        material[name] = json.loads((root / '_source/poker' / name).read_text(encoding='utf-8'))
    for name in [r['slug'] + '.html' for r in course['lessons']] + ['beginner-checkpoint.html']:
        material[name] = (root / '_source/poker' / name).read_text(encoding='utf-8')
    for path in ['_scripts/poker_course.py', '_scripts/poker_lessons.py', '_scripts/poker_final_hands.py']:
        material[path] = (root / path).read_text(encoding='utf-8')
    revision = sha256(json.dumps(material, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()
    lessons = [
        {'id': lesson['slug'], 'title': lesson['title'], 'goal': lesson['goal'],
         'read': '/poker/' + lesson['slug'] + '/#course-first-pass-title',
         'practice': lesson['practice']}
        for lesson in course['lessons']
    ]
    destinations = []
    for number, lesson in enumerate(lessons, 1):
        destinations.extend([
            {'id': 'read:' + lesson['id'], 'label': f'Read lesson {number}: ' + lesson['title'], 'href': lesson['read']},
            {'id': 'practice:' + lesson['id'], 'label': f'Practice lesson {number}: ' + lesson['title'], 'href': lesson['practice']},
        ])
    destinations.extend([
        {'id': 'foundations', 'label': 'Open the Poker Foundations course map', 'href': poker_course.ROUTE},
        {'id': 'checkpoint', 'label': 'Try the beginner checkpoint', 'href': '/poker/beginner-checkpoint/'},
    ])
    return {'format': FORMAT, 'version': VERSION, 'course': COURSE, 'revision': revision,
            'storageKey': STORAGE_KEY, 'maxBytes': MAX_BYTES,
            'states': [{'id': value, 'label': label} for value, label in STATES],
            'lessons': lessons, 'destinations': destinations, 'defaultNext': destinations[0]['id']}


def new_tab_link(href, label, extra=''):
    return (f'<a href="{escape(href, quote=True)}" target="_blank" rel="noopener"'
            f' aria-label="{escape(label + " (opens in a new tab)", quote=True)}"{extra}>{escape(label)}</a>')


def render(root):
    data = config(root)
    options = ''.join(f'<option value="{value}">{escape(label)}</option>' for value, label in STATES)
    rows = []
    for number, lesson in enumerate(data['lessons'], 1):
        ident = lesson['id']
        rows.append(
            '<li class="progress-lesson">'
            f'<h3 id="progress-title-{ident}">{number}. {escape(lesson["title"])}</h3>'
            f'<p class="small-copy">{escape(lesson["goal"])}</p>'
            '<p class="progress-lesson-links">'
            + new_tab_link(lesson['read'], 'Read lesson', f' data-progress-read="{ident}" aria-describedby="progress-title-{ident}"') + ' '
            + new_tab_link(lesson['practice'], 'Practice', f' data-progress-practice="{ident}" aria-describedby="progress-title-{ident}"')
            + '</p>'
            f'<div class="progress-state-control" data-progress-enhanced hidden><label for="progress-status-{ident}">Your note for lesson {number}</label>'
            f'<select id="progress-status-{ident}" data-progress-lesson="{ident}">{options}</select></div>'
            f'<p class="progress-state-print" id="progress-print-{ident}">Your note: Not started</p></li>'
        )
    next_options = ''.join(f'<option value="{escape(item["id"], quote=True)}">{escape(item["label"])}</option>' for item in data['destinations'])
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    first = data['destinations'][0]
    return (
        '<section class="section folio-row progress-companion" id="course-progress" aria-labelledby="progress-heading">'
        '<div class="section-meta"><p class="section-label">Resume / Practice / Keep</p></div><div class="section-content">'
        '<h2 class="section-title" id="progress-heading">Your next Poker Foundations task.</h2>'
        '<p>Keep a place in the six lessons and choose what to revisit. These marks are your own notes, not a skill score. Reading a page or answering an exercise does not change them.</p>'
        '<p class="small-copy">Lesson and practice links open in a new tab so this desk stays open. Use these tools before or after play.</p>'
        '<div class="progress-next">'
        '<div id="progress-next-field" data-progress-enhanced hidden><label for="progress-next">What would you like to do next?</label>'
        f'<select id="progress-next">{next_options}</select></div>'
        '<p>' + new_tab_link(first['href'], first['label'], ' class="button" id="progress-resume"') + '</p></div>'
        '<p id="progress-status" role="status" aria-live="polite" aria-atomic="true"></p>'
        '<p id="progress-summary">Choose a lesson or use the blank study card to keep your own record.</p>'
        '<ol class="progress-lessons">' + ''.join(rows) + '</ol>'
        '<section class="progress-revisit" data-progress-enhanced hidden aria-labelledby="progress-revisit-heading">'
        '<h3 id="progress-revisit-heading">To revisit</h3><p id="progress-revisit-empty">Nothing is marked Revisit. You can change any lesson note above.</p><ul id="progress-revisit-list"></ul></section>'
        '<div class="progress-tools" data-progress-enhanced hidden>'
        '<details class="poker-details" id="progress-storage"><summary>Remember on this device or reset</summary><div>'
        '<label class="progress-checkbox" for="progress-remember"><input type="checkbox" id="progress-remember">Remember on this device</label>'
        '<p class="small-copy">Off by default. When checked, only these six marks and your next task are saved in this browser and updated when you change them. Enabling it replaces this tool’s earlier saved record. No answers, names or hand histories are recorded. Anyone using this browser profile can see the saved marks.</p>'
        '<p id="progress-storage-status" role="status" aria-live="polite" aria-atomic="true"></p>'
        '<div class="progress-buttons"><button type="button" id="progress-forget">Remove saved copy</button><button type="button" id="progress-reset">Reset marks and stop saving</button></div>'
        '<p class="small-copy">Remove saved copy keeps the marks in this open page. Reset also clears the six marks and the next task. Each action affects only this tool’s saved record. Browser data can be cleared or unavailable; export a copy when you want to keep it.</p>'
        '</div></details>'
        '<details class="poker-details" id="progress-transfer"><summary>Keep or restore a progress file</summary><div>'
        '<h3>Keep a copy</h3><p>A progress file contains only the six marks, your chosen next task and the course version. It does not include answers or a saving preference.</p>'
        '<div class="progress-buttons"><a id="progress-download" download="poker-foundations-progress.json" hidden>Download progress file</a><button type="button" id="progress-select-export">Select the complete progress text</button></div>'
        '<label for="progress-export-text">Complete progress file</label><textarea id="progress-export-text" rows="9" readonly spellcheck="false" aria-describedby="progress-export-help"></textarea>'
        '<p class="small-copy" id="progress-export-help">You can copy the selected text with your device’s Copy command and keep it in your own notes. Paste the complete text below on a later visit to restore it.</p>'
        '<h3>Restore a copy</h3><label for="progress-import-file">Choose a progress file to review</label><input type="file" id="progress-import-file" accept=".json,application/json">'
        '<p class="small-copy">The file is read in this browser. It is not uploaded. You review it before replacing anything.</p>'
        '<label for="progress-import-text">Or paste the complete progress text</label><textarea id="progress-import-text" rows="7" maxlength="8192" spellcheck="false" autocomplete="off"></textarea>'
        '<button type="button" id="progress-review-import">Review pasted progress</button>'
        '<p id="progress-transfer-status" role="status" aria-live="polite" aria-atomic="true"></p>'
        '<section id="progress-import-preview" hidden aria-labelledby="progress-import-preview-title"><h3 id="progress-import-preview-title" tabindex="-1">Review this progress</h3>'
        '<p id="progress-import-summary"></p><ul id="progress-import-lessons"></ul><p id="progress-import-saving" class="small-copy"></p>'
        '<div class="progress-buttons"><button type="button" id="progress-apply-import">Replace the current record</button><button type="button" id="progress-cancel-import">Cancel</button></div></section>'
        '</div></details></div>'
        '<p id="progress-fallback">The lesson links and blank study card work without JavaScript. Progress controls become available when scripts run.</p>'
        '<p><a href="/downloads/poker-beginner-study-card.txt" download>Download the complete blank study card (TXT)</a> or <a href="/poker/free-poker-learning-path/">return to the free course</a>.</p>'
        '<p class="small-copy">The course remains usable without saving anything. Progress stays in this page unless you choose device saving or keep a copy yourself. It is not sent to the site. See the <a href="/privacy/">privacy notice</a> for ordinary pageview analytics and browser storage.</p>'
        f'<script type="application/json" id="poker-progress-data">{payload}</script>'
        '</div></section>'
    )


def head(page, root):
    if page['path'] != ROUTE:
        return ''
    css_version = sha256((root / CSS).read_bytes()).hexdigest()[:12]
    js_version = sha256((root / SCRIPT).read_bytes()).hexdigest()[:12]
    return (f'\n  <link rel="stylesheet" href="/{CSS}?v={css_version}">'
            f'\n  <script defer src="/{SCRIPT}?v={js_version}"></script>')
