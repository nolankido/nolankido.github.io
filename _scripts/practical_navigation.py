"""Connect existing AI checkpoints without changing their content or tool state."""
from hashlib import sha256
from html import escape
from pathlib import Path

import practical_path

BEGIN = '<!-- Practical AI navigation: start -->'
END = '<!-- Practical AI navigation: end -->'
CSS = Path('assets/practical-ai-navigation.css')
IDS = frozenset(stage[0] for stage in practical_path.STAGES)

# These are possible onward choices, not completion indicators or requirements.
ONWARD = (
    ('If an AI draft fits this task,', 'write a brief with a finish line', 'task-brief'),
    ('When you have an answer,', 'check the parts that matter', 'ai-answer-review'),
    ('To judge the time benefit,', 'compare the whole cost of the task', 'ai-time-savings'),
    ('Keep, adjust, stop or gather more observations.', 'Return to the whole workflow', None),
)


def marked(content):
    return BEGIN + '\n' + content + '\n' + END + '\n'


def blocks(page, pages, root):
    if page['id'] not in IDS:
        return ()
    entries = practical_path.records(pages, root)
    index = next(i for i, entry in enumerate(entries) if entry['id'] == page['id'])
    links = []
    for i, entry in enumerate(entries, 1):
        label = '<span class="ai-workflow-number">' + str(i).zfill(2) + '</span> ' + escape(entry['short'])
        if entry['id'] == page['id']:
            item = '<span class="ai-workflow-current" aria-current="page">' + label + '<span class="ai-workflow-here">This page</span></span>'
        else:
            item = '<a href="' + escape(entry['path'], quote=True) + '">' + label + '</a>'
        links.append('<li>' + item + '</li>')
    top = marked(
        '<nav class="ai-workflow-navigation folio-row" id="ai-workflow-navigation" aria-labelledby="ai-workflow-navigation-title">'
        '<div class="section-meta"><p class="section-label">Optional path / One task</p></div>'
        '<div class="section-content"><p class="ai-workflow-title" id="ai-workflow-navigation-title">Practical AI workflow</p>'
        '<ol>' + ''.join(links) + '</ol>'
        '<p class="ai-workflow-note">Use the stages you need. Save results in your own notes before moving between pages.</p>'
        '<p class="ai-workflow-links"><a href="/technology/#practical-ai-path">See the whole path</a>'
        '<a href="/downloads/practical-ai-workbook.txt" download>Save the blank workbook (.txt)</a></p></div></nav>'
    )
    lead, label, target = ONWARD[index]
    destination = next(entry['path'] for entry in entries if entry['id'] == target) if target else '/technology/#practical-ai-path'
    after = marked(
        '<aside class="ai-workflow-onward folio-row" aria-labelledby="ai-workflow-onward-title">'
        '<div class="section-meta"><p class="section-label" id="ai-workflow-onward-title">Another useful checkpoint</p></div>'
        '<div class="section-content"><p>' + escape(lead) + ' <a href="' + escape(destination, quote=True) + '">' + escape(label) + '</a>.</p>'
        '<p class="ai-workflow-note">A simpler method or a decision to stop is a valid end.</p></div></aside>'
    )
    return top, after


def decorate(page, body, pages, root):
    additions = blocks(page, pages, root)
    if not additions:
        return body
    if BEGIN in body or 'id="ai-workflow-navigation"' in body:
        raise ValueError('Practical AI navigation must be added exactly once')
    return additions[0] + body + additions[1]


def head(page, root):
    if page['id'] not in IDS:
        return ''
    version = sha256((root / CSS).read_bytes()).hexdigest()[:12]
    return '\n  <link rel="stylesheet" href="/assets/practical-ai-navigation.css?v=' + version + '">'
