"""A native, optional route through existing work. No model or saved progress."""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
from html import escape
from pathlib import Path
import re

BEGIN = '<!-- AI workflow path: start -->\n'
END = '<!-- AI workflow path: end -->\n'
SHEET = Path('downloads/practical-ai-workflow.txt')
CSS = Path('assets/workflow-path.css')
HUB = '/technology/#ai-workflow-path'
STEPS = (
    {'id': 'ai-task-choice', 'label': 'Decide', 'title': 'Decide whether AI belongs in the task.',
     'route': '/technology/should-i-use-ai/', 'kind': 'Decision guide',
     'description': 'Check the purpose, permission, consequences, and a simpler alternative before writing a prompt.',
     'output': 'A next step: pause, use a simpler method, prepare, or try a bounded draft.',
     'sheet': 'downloads/should-i-use-ai.txt'},
    {'id': 'task-brief', 'label': 'Brief', 'title': 'Write a brief you can check.',
     'route': '/technology/task-brief/', 'kind': 'Free browser tool',
     'description': 'Name the allowed inputs, requested output, stopping point, and checks. Set the boundary before production.',
     'output': 'A reusable task brief. The builder formats text; it does not run AI.',
     'sheet': 'downloads/ai-task-brief.txt'},
    {'id': 'ai-summary-review', 'label': 'Check', 'title': 'Practice checking a summary against its source.',
     'route': '/technology/check-ai-summary/', 'kind': 'Worked guide',
     'description': 'Trace claims, conditions, and omissions to original notes. Compare a flawed draft with a repaired version.',
     'output': 'A source-linked review method. The teaching example is fictional.',
     'sheet': 'downloads/ai-summary-review.txt'},
    {'id': 'ai-time-savings', 'label': 'Measure', 'title': 'Count the full workflow, including repairs.',
     'route': '/technology/ai-time-savings/', 'kind': 'Free calculator',
     'description': 'Include setup, preparation, review, repair, and upkeep. Compare like-for-like work at acceptable quality.',
     'output': 'A time comparison based on your inputs, not an observed productivity claim.',
     'sheet': 'downloads/workflow-time-review.txt'},
)
IDS = frozenset(step['id'] for step in STEPS)


def validate(pages: list[dict], root: Path) -> None:
    """Do not quietly publish a dead stage or an incomplete workbook."""
    by_id = {p['id']: p for p in pages}
    for step in STEPS:
        page = by_id.get(step['id'])
        if not page or page['path'] != step['route'] or page.get('noindex'):
            raise ValueError('Workflow stage must be a published, indexable canonical page: ' + step['id'])
        raw = (root / step['sheet']).read_text(encoding='utf-8')
        if not raw.strip() or len(raw.encode()) > 100_000:
            raise ValueError('Workflow worksheet is empty or unexpectedly large: ' + step['sheet'])


def workbook(root: Path) -> str:
    """Bundle the existing blank originals, not independently rewritten copies."""
    parts = [
        'PRACTICAL AI WORKFLOW WORKBOOK\nNolan Kido | https://nolankido.com/technology/#ai-workflow-path\n',
        'Decide / Brief / Check / Measure\n\nUse one task throughout, and complete this copy in your own notes.\nNothing entered in your downloaded copy is sent to this website.\nKeep completed copies private. Do not upload sensitive source material merely\nbecause a worksheet asks you to describe it.\n\nThis is an optional working order, not a course, validated assessment, or\npermission to act. A pause or a simpler method can be the right endpoint.\nThe Check section concerns summaries. Code, calculations, and other outputs\nneed independent checks appropriate to their purpose and consequences.\nDo not send, publish, buy, book, or change anything without the required\npermission and review.\n\nONE TASK\n[Task, intended audience, and the acceptable result.]\n\nThe following four blank worksheets are reproduced from their source files.\nUse the linked guides for their examples, assumptions, and limits.\n',
    ]
    for number, step in enumerate(STEPS, 1):
        raw = (root / step['sheet']).read_text(encoding='utf-8')
        if not raw.strip():
            raise ValueError('Cannot export an empty worksheet')
        parts.append('\n' + '=' * 64 + '\n' + str(number) + '. ' + step['label'].upper() + '\n'
                     + 'Guide: https://nolankido.com' + step['route'] + '\n'
                     + 'Original: https://nolankido.com/' + step['sheet'] + '\n' + '=' * 64 + '\n\n' + raw)
    parts.append('\nFINAL DECISION\n[Keep / revise / choose a simpler method / stop / gather more observations.]\n[Unresolved checks, permissions, and the next review point.]\n\nA completed worksheet does not certify accuracy, safety, or permission.\nPrepared with AI assistance. This blank workbook is not a personal result.\n')
    return '\n'.join(parts)


def marked(content: str) -> str:
    return BEGIN + content + '\n' + END


def hub(root: Path) -> str:
    cards = []
    for number, step in enumerate(STEPS, 1):
        cards.append('<li class="workflow-stage"><p class="note-category">'
                     + str(number).zfill(2) + ' / ' + escape(step['label']) + ' / ' + escape(step['kind']) + '</p>'
                     '<h3><a href="' + escape(step['route'], quote=True) + '">' + escape(step['title']) + '</a></h3>'
                     '<p>' + escape(step['description']) + '</p><p class="workflow-outcome"><strong>Leave with:</strong> '
                     + escape(step['output']) + '</p></li>')
    return marked('<section class="section folio-row workflow-hub" id="ai-workflow-path" aria-labelledby="technology-before-ai">'
                  '<div class="section-meta"><p class="section-label">One task / Four useful stages</p></div>'
                  '<div class="section-content"><h2 class="section-title" id="technology-before-ai">A practical AI workflow, from decision to review.</h2>'
                  '<p class="section-deck">Choose one task and follow it from the first decision to the final comparison. Start at the stage you need. '
                  'A pause or a simpler method can be the right endpoint; there is no sequence you have to finish.</p>'
                  '<ol class="workflow-stages">' + ''.join(cards) + '</ol>'
                  '<p class="small-copy">The checking exercise is about summaries. Other outputs need their own independent tests. '
                  'For an actual implementation record, <a href="/technology/checking-ai-website-changes/">see the website defect caught before publication</a>. '
                  'The tools here do not run AI or connect to your accounts.</p>'
                  '<div class="workflow-workbook" id="ai-workflow-workbook"><h3>Keep one workbook for the whole task.</h3>'
                  '<p>Four existing blank worksheets, with a short route through them, in one editable text file. '
                  'No signup. Complete it privately in your own editor. The original individual downloads stay available.</p>'
                  '<p><a class="button" href="/' + str(SHEET) + '" download>Download the practical AI workbook (.txt)</a></p>'
                  '<details><summary>Preview the complete blank workbook</summary><pre>' + escape(workbook(root)) + '</pre></details>'
                  '</div></div></section>')


def stage_navigation(page: dict) -> str:
    items = []
    for number, step in enumerate(STEPS, 1):
        label = str(number) + '. ' + step['label']
        if step['id'] == page['id']:
            item = '<span aria-current="step">' + label + '<span class="workflow-here">You are here</span></span>'
        else:
            item = '<a href="' + escape(step['route'], quote=True) + '" title="' + escape(step['title'], quote=True) + '">' + label + '</a>'
        items.append('<li>' + item + '</li>')
    return marked('<aside class="workflow-route shell" aria-labelledby="workflow-route-title">'
                  '<p id="workflow-route-title"><a href="' + HUB + '">The practical AI workflow</a></p>'
                  '<nav aria-label="Practical AI workflow stages"><ol>' + ''.join(items) + '</ol></nav>'
                  '<p class="small-copy">Choose the stage you need. A pause or simpler method is a valid finish. '
                  '<a href="/' + str(SHEET) + '" download>Keep the whole workbook (.txt)</a>. These links do not save progress.</p></aside>')


def insert_once(body: str, anchor: str, addition: str) -> str:
    if body.count(anchor) != 1:
        raise ValueError('Workflow insertion point is missing or ambiguous: ' + anchor)
    return body.replace(anchor, addition + anchor, 1)


def decorate(body: str, page: dict, root: Path) -> str:
    if BEGIN in body:
        raise ValueError('Duplicate workflow route')
    if page['id'] == 'technology':
        pattern = r'<!-- AI task choice: start -->\n.*?<!-- AI task choice: end -->\n'
        if len(re.findall(pattern, body, re.S)) != 1:
            raise ValueError('Expected the existing Technology decision entry')
        return re.sub(pattern, lambda match: hub(root), body, count=1, flags=re.S)
    if page['id'] in IDS:
        return stage_navigation(page) + body
    if page['id'] == 'start-here':
        return insert_once(body, '<nav class="entry-jumps" aria-label="On this introduction">',
                           marked('<p class="small-copy"><strong>New to practical AI?</strong> '
                                  '<a href="' + HUB + '">Follow one task through decide, brief, check, and measure</a>, '
                                  'with free tools and one private-use workbook.</p>'))
    if page['id'] == 'resources':
        return insert_once(body, '<h3 id="ai-task-choice-resource">',
                           marked('<aside class="workflow-resource" aria-labelledby="workflow-workbook-resource">'
                                  '<h3 id="workflow-workbook-resource">One task, one practical AI workbook.</h3>'
                                  '<p><a href="' + HUB + '">Follow the four-stage practical AI workflow</a>, or '
                                  '<a href="/' + str(SHEET) + '" download>download all four blank worksheets together (.txt)</a>. '
                                  'The complete preview explains the scope; nothing needs to be filled in on this site.</p></aside>'))
    return body


def head(page: dict, root: Path) -> str:
    if page['id'] not in IDS | {'technology', 'resources'}:
        return ''
    version = sha256((root / CSS).read_bytes()).hexdigest()[:12]
    return '\n  <link rel="stylesheet" href="/' + str(CSS) + '?v=' + version + '">'


def schema(data: dict, page: dict, origin: str) -> dict:
    """Describe the visible collection. Do not claim rich-result eligibility."""
    result = deepcopy(data)
    if page['id'] == 'technology':
        result['@type'] = 'CollectionPage'
        result['mainEntity'] = {
            '@type': 'ItemList', 'name': 'Practical AI workflow', 'numberOfItems': len(STEPS),
            'itemListElement': [{'@type': 'ListItem', 'position': number, 'name': step['title'],
                                 'url': origin + step['route']} for number, step in enumerate(STEPS, 1)],
        }
    return result
