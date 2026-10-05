"""Public reading and resource components. Selection is editorial, not a status metric."""
from datetime import datetime
from html import escape
import json

RESOURCES = [
    ('decision-record', 'Decision record', 'Separate what you knew before a decision from what you learned afterward.', 'decision-quality'),
    ('tool-trust-check', 'Tool trust check', 'Define a claim, record independent checks, and make untested cases visible.', 'trustworthy-tools'),
    ('learning-loop', 'Learning loop', 'Turn an ambitious goal into a small capability you can practice and check.', 'learning-from-the-beginning'),
]
GUIDANCE = {
    'decision-record': ('For a choice worth revisiting, especially one with uncertainty or consequences for other people.', 'Write the before section first, make the relevant conversation explicit, and add the review without replacing the earlier reasoning.', 'Do not score someone else’s preferences without their agreement. For a small reversible choice, a conversation may be enough.'),
    'tool-trust-check': ('For someone deciding whether a tool supports one clearly defined use.', 'Specify the claim, work out a small answer independently, and record discrepancies and untested cases before deciding how much to rely on the tool.', 'A few tests do not prove general correctness. High-consequence uses require proportionate scrutiny and relevant expertise.'),
    'learning-loop': ('For a learner who needs a clear next practice step rather than another long resource list.', 'Choose one capability, attempt it without the guide, check the result, and leave a small next action. Use the smaller-week option when needed.', 'The worksheet is not a curriculum or a mastery test. Adapt to circumstances; support or rest may help more than additional workload.'),
}

def reading_table(notes, caption):
    rows = []
    for note in notes:
        date = datetime.strptime(note['date'], '%Y-%m-%d')
        rows.append('<tr><td><time datetime="' + escape(note['date']) + '">' + date.strftime('%b %Y') + '</time></td><td><a href="' + escape(note['path'], quote=True) + '">' + escape(note['title']) + '</a></td><td>' + escape(note['kicker']) + '</td></tr>')
    return '<table class="reading-table"><caption class="visually-hidden">' + escape(caption) + '</caption><thead><tr><th scope="col">Date</th><th scope="col">Note</th><th scope="col">Subject</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table>'

def supplement(root, notes):
    selection = json.loads((root / '_source/selection.json').read_text(encoding='utf-8'))
    by_id = {note['id']: note for note in notes}
    chosen = selection['selected_notes']
    if len(chosen) != len(set(chosen)) or any(slug not in by_id for slug in chosen):
        raise ValueError('Selected notes must be unique published note IDs')
    if selection['featured_note'] not in by_id:
        raise ValueError('Featured note must identify a published note')
    summaries, worksheets = [], []
    for slug, title, description, note in RESOURCES:
        summaries.append('<article class="resource-row"><span class="resource-date">Thinking aid</span><div><h3><a href="/resources/#' + slug + '">' + escape(title) + '</a></h3><p>' + escape(description) + '</p></div><span class="resource-kind">Template</span></article>')
        content = (root / 'downloads' / (slug + '.md')).read_text(encoding='utf-8')
        example = (root / '_source/examples' / (slug + '.html')).read_text(encoding='utf-8')
        audience, use, limit = GUIDANCE[slug]
        worksheets.append('<section class="worksheet" id="' + slug + '" aria-labelledby="' + slug + '-title"><p class="note-category">A guide, an example, and a blank copy</p><h2 id="' + slug + '-title">' + escape(title) + '</h2><p>' + escape(description) + '</p><p><strong>Who it is for:</strong> ' + escape(audience) + '</p><p><strong>How to use it:</strong> ' + escape(use) + '</p><p><strong>When not to use it:</strong> ' + escape(limit) + '</p><details class="worked-example"><summary>Read a completed fictional example</summary><div class="prose">' + example + '</div></details><div class="link-row"><a class="button" href="/downloads/' + slug + '.md" download>Download ' + title.lower() + ' <span aria-hidden="true">↓</span></a><a class="text-link" href="/notes/' + note + '/">Read the related note <span aria-hidden="true">→</span></a></div><details><summary>Preview the blank ' + title.lower() + '</summary><pre>' + escape(content) + '</pre></details></section>')
    return {'note_count': f'{len(notes):02d}', 'resource_count': f'{len(RESOURCES):02d}', 'notes_table': reading_table(notes, 'All notes by publication date, title, and subject'), 'selected_notes_table': reading_table([by_id[slug] for slug in chosen], 'Selected reflections on communication and finishing work'), 'resources_list': '<div class="resource-list">' + ''.join(summaries) + '</div>', 'worksheets': ''.join(worksheets)}
