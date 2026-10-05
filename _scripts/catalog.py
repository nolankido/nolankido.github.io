"""Public reading and resource components for the editorial layout."""
from datetime import datetime
from html import escape

RESOURCES = [
    ('decision-record', 'Decision record', 'Separate what you knew before a decision from what you learned afterward.', 'decision-quality'),
    ('tool-trust-check', 'Tool trust check', 'Define a claim, record independent checks, and make untested cases visible.', 'trustworthy-tools'),
    ('learning-loop', 'Learning loop', 'Turn an ambitious goal into a small capability you can practice and check.', 'learning-from-the-beginning'),
]

def supplement(root, notes):
    rows = []
    for note in notes:
        date = datetime.strptime(note['date'], '%Y-%m-%d')
        rows.append('<tr><td><time datetime="' + note['date'] + '">' + date.strftime('%b %Y') + '</time></td><td><a href="' + escape(note['path'], quote=True) + '">' + escape(note['title']) + '</a></td><td>' + escape(note['kicker']) + '</td></tr>')
    table = '<table class="reading-table"><caption class="visually-hidden">Selected notes by publication date, title, and subject</caption><thead><tr><th scope="col">Date</th><th scope="col">Note</th><th scope="col">Subject</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table>'
    summaries, worksheets = [], []
    for slug, title, description, note in RESOURCES:
        summaries.append('<article class="resource-row"><time class="resource-date" datetime="2026-10-05">Oct 2026</time><div><h3><a href="/resources/#' + slug + '">' + escape(title) + '</a></h3><p>' + escape(description) + '</p></div><span class="resource-kind">Template</span></article>')
        content = (root / 'downloads' / (slug + '.md')).read_text(encoding='utf-8')
        worksheets.append('<section class="worksheet" id="' + slug + '" aria-labelledby="' + slug + '-title"><p class="note-category">Editable worksheet · Markdown</p><h2 id="' + slug + '-title">' + title + '</h2><p>' + description + '</p><div class="link-row"><a class="button" href="/downloads/' + slug + '.md" download>Download ' + title.lower() + ' <span aria-hidden="true">↓</span></a><a class="text-link" href="/notes/' + note + '/">Read the related note <span aria-hidden="true">→</span></a></div><details><summary>Preview ' + title.lower() + '</summary><pre>' + escape(content) + '</pre></details></section>')
    return {'note_count': f'{len(notes):02d}', 'resource_count': f'{len(RESOURCES):02d}', 'notes_table': table, 'resources_list': '<div class="resource-list">' + ''.join(summaries) + '</div>', 'worksheets': ''.join(worksheets)}
