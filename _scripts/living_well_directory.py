"""Task-led resource discovery. All content is static; optional filtering is local only."""
from __future__ import annotations
from datetime import date
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re

PREFIX = '/living-well/'
FINDER = PREFIX + 'find/'
CATALOG = Path('_source/living-well/directory.json')
VERSION = 1


def text(value, label):
    if not isinstance(value, str) or not value.strip() or len(value) > 3000:
        raise ValueError('Invalid directory text: ' + label)
    return value


def ident(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value):
        raise ValueError('Invalid directory identifier')
    return value


def read(root: Path) -> dict:
    data = json.loads((root / CATALOG).read_text(encoding='utf-8'))
    if type(data.get('version')) is not int or data['version'] != VERSION:
        raise ValueError('Unknown directory version')
    if set(data) != {'version', 'reviewed_on', 'shelves', 'resources', 'tasks'}:
        raise ValueError('Unexpected directory fields')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', data['reviewed_on']) or date.fromisoformat(data['reviewed_on']) > date.today():
        raise ValueError('Invalid directory review date')
    for field in ('resources', 'shelves', 'tasks'):
        if not isinstance(data[field], list) or not data[field]:
            raise ValueError('Directory collections must be nonempty lists')
    task_ids = set()
    for task in data['tasks']:
        if set(task) != {'id', 'title', 'description', 'purpose', 'simplest', 'finish', 'choices', 'steps', 'guides'}:
            raise ValueError('Unexpected task fields')
        key = ident(task['id'])
        if key in task_ids:
            raise ValueError('Duplicate task')
        task_ids.add(key)
        for field in ('title', 'description', 'purpose', 'simplest', 'finish'):
            text(task[field], field)
        if not isinstance(task['choices'], list) or not 3 <= len(task['choices']) <= 8:
            raise ValueError('Task needs three to eight distinct choices')
        selected = set()
        for choice in task['choices']:
            if set(choice) != {'resource', 'when', 'check'}:
                raise ValueError('Unexpected choice fields')
            key = ident(choice['resource'])
            if key in selected:
                raise ValueError('Duplicate choice in task')
            selected.add(key)
            text(choice['when'], 'when'); text(choice['check'], 'check')
        if not isinstance(task['steps'], list) or not 2 <= len(task['steps']) <= 5:
            raise ValueError('Task needs useful selection guidance')
        for step in task['steps']:
            if set(step) != {'title', 'text'}:
                raise ValueError('Unexpected guidance fields')
            text(step['title'], 'step title'); text(step['text'], 'step text')
        if not isinstance(task['guides'], list) or len(task['guides']) != 2 or len(set(task['guides'])) != 2:
            raise ValueError('Task needs two distinct companion guides')
        for key in task['guides']:
            ident(key)
    return data


def extend(root: Path, base: dict) -> dict:
    """Keep historical resource records and their review dates unchanged."""
    if not (root / CATALOG).exists():
        return base
    extra = read(root)
    return {**base, 'reviewed_on': max(base['reviewed_on'], extra['reviewed_on']),
            'shelves': [*base['shelves'], *extra['shelves']],
            'resources': [*base['resources'], *extra['resources']]}


def context(root: Path):
    import living_well_resources as resources
    data = read(root)
    library = resources.load(root)
    entries = {e['id']: e for e in library['resources']}
    guides = {}
    for name in ('launch.json', 'further.json', 'discovery.json', 'expansion.json'):
        guides.update({e['slug']: e for e in json.loads((root / '_source/living-well' / name).read_text())['entries']})
    for task in data['tasks']:
        if any(c['resource'] not in entries for c in task['choices']):
            raise ValueError('Task refers to missing resource')
        if any(key not in guides or guides[key]['kind'] == 'experiment' for key in task['guides']):
            raise ValueError('Task companion must be a published reading')
    return data, library, entries, guides


def route(key: str) -> str:
    return PREFIX + 'tasks/' + ident(key) + '/'


def manifest(root: Path) -> list[dict]:
    data, library, entries, guides = context(root)
    pages = [{'id': 'living-well-find', 'path': FINDER, 'title': 'Find a useful resource',
              'description': 'Search Living Well resources by interest, everyday task, collection, and entry access. All links remain available without JavaScript.',
              'directory_kind': 'finder'}]
    pages += [{'id': 'living-well-task-' + t['id'], 'path': route(t['id']), 'title': t['title'],
               'description': t['description'], 'directory_kind': 'task', 'directory_task': t['id']}
              for t in data['tasks']]
    for page in pages:
        page.update(seo_title=page['title'] + ' | Living Well', kicker='Living Well / Resource directory',
                    source='living-well/page.html', section='living-well', living_well_hub='free-resources',
                    updated=data['reviewed_on'])
    return pages


def tiles(root: Path) -> str:
    return '<div class="lw-cards">' + ''.join(
        '<article class="lw-card"><h3><a href="' + route(t['id']) + '">' + escape(t['title'])
        + '</a></h3><p>' + escape(t['description']) + '</p></article>' for t in read(root)['tasks']) + '</div>'


def header(root: Path, page: dict) -> str:
    css = '/assets/living-well-directory.css?v=' + sha256((root / 'assets/living-well-directory.css').read_bytes()).hexdigest()[:12]
    out = '\n  <link rel="stylesheet" href="' + css + '">'
    if page['directory_kind'] == 'finder':
        js = '/assets/living-well-directory.js?v=' + sha256((root / 'assets/living-well-directory.js').read_bytes()).hexdigest()[:12]
        out += '\n  <script defer src="' + js + '"></script>'
    return out


def nav() -> str:
    return '<p class="lw-directory-nav"><a href="/living-well/free-resources/#by-task">Choose another task</a> · <a href="/living-well/find/">Find a resource</a> · <a href="/living-well/free-resources/">Browse all collections</a></p>'


def render(root: Path, page: dict, section) -> str:
    import living_well_resources as resources
    data, library, entries, guides = context(root)
    if page['directory_kind'] == 'finder':
        return finder(library, section)
    task = next(t for t in data['tasks'] if t['id'] == page['directory_task'])
    body = section('a-useful-result', 'Start with life', 'What would be useful?',
        '<p class="section-deck">' + escape(task['purpose']) + '</p><div class="prose">'
        + '<p><strong>The simpler starting point:</strong> ' + escape(task['simplest']) + '</p>'
        + '<p><strong>Finish when:</strong> ' + escape(task['finish']) + '</p></div>' + nav())
    choices = []
    for choice in task['choices']:
        e = entries[choice['resource']]
        choices.append('<article class="lw-choice" id="choice-' + escape(e['id']) + '"><h3>' + escape(e['title'])
            + '</h3><p><strong>Consider it when:</strong> ' + escape(choice['when'])
            + '</p><p><strong>Check first:</strong> ' + escape(choice['check'])
            + '</p><p class="small-copy"><strong>Access:</strong> ' + escape(e['requirements'])
            + '</p><p>' + resources.external(e['entry_url'], e['entry_title']) + ' · <a href="'
            + resources.collection_route(e['shelf']) + '#' + escape(e['id']) + '">Full context and source</a></p></article>')
    body += section('compare-options', 'Choose by fit', 'Different tools, different jobs.',
        '<p class="section-deck">These are editorial comparisons based on public descriptions, not a ranking from hands-on tests. Choose one suitable route; using every option is not the goal.</p>'
        + '<div class="lw-choices">' + ''.join(choices) + '</div>')
    body += section('use-it-thoughtfully', 'From choice to use', 'Keep the human purpose visible.',
        '<div class="prose">' + ''.join('<h3>' + escape(s['title']) + '</h3><p>' + escape(s['text']) + '</p>' for s in task['steps'])
        + '<p>Published as a selection path, not a personal field note. Source dates and access limits belong to each resource. No paid placement or affiliation is implied.</p></div>')
    body += section('continue-with-a-guide', 'Go a little further', 'Make the next step concrete.',
        '<div class="lw-situations">' + ''.join('<p><span>Related Living Well reading</span><a href="/living-well/' + key + '/">' + escape(guides[key]['title']) + '</a></p>' for key in task['guides']) + '</div>' + nav())
    return body


def finder(library: dict, section) -> str:
    import living_well_resources as resources
    shelves = {s['id']: s for s in library['shelves']}
    entries = sorted(library['resources'], key=lambda e: (e['title'].casefold(), e['id']))
    controls = ('<div id="lw-filters" class="lw-filters" hidden><div><label for="lw-query">A topic, task, or resource name</label>'
        '<input type="search" id="lw-query" maxlength="120" autocomplete="off" spellcheck="false" aria-describedby="lw-filter-help" placeholder="Try notes, poetry, captions, or backup"></div>'
        '<div><label for="lw-collection">Collection</label><select id="lw-collection"><option value="">All collections</option>'
        + ''.join('<option value="' + escape(s['id']) + '">' + escape(s['title']) + '</option>' for s in library['shelves'])
        + '</select></div><div><label for="lw-access">Entry access</label><select id="lw-access"><option value="">All access types</option>'
        + ''.join('<option value="' + escape(key) + '">' + escape(value) + '</option>' for key, value in resources.ACCESS.items())
        + '</select></div><button type="button" id="lw-clear">Clear filters</button>'
        '<p id="lw-filter-help">Filtering happens in this page. This feature does not send or save search text, change the address, or contact an AI service. Entry access describes the selected resource, not free hardware or every feature. Ordinary page visits follow the <a href="/privacy/">site privacy notice</a>.</p></div>')
    body = section('find-your-start', 'The complete directory', 'Choose something useful.',
        '<p class="section-deck">' + str(len(entries)) + ' resources in ' + str(len(shelves))
        + ' collections. Narrow the list, or <a href="/living-well/free-resources/#by-task">start with an everyday task</a>.</p>'
        + controls + '<noscript><p>Every resource is available below. Use your browser’s Find command to search this page without JavaScript.</p></noscript>'
        + '<p id="lw-result-count" role="status" aria-live="polite" aria-atomic="true">Showing ' + str(len(entries)) + ' of ' + str(len(entries)) + ' resources.</p>'
        + '<p id="lw-empty" hidden>No matching resources. Try fewer words, another collection, or clear the filters. The <a href="/living-well/free-resources/#by-task">task paths</a> offer another way in.</p>')
    results = []
    for e in entries:
        # Hidden metadata comes only from public editorial text, never from visitor input.
        terms = ' '.join([e['start'], e['limit'], e['format'], e['creator'], shelves[e['shelf']]['title']])
        results.append('<article class="lw-finder-item" data-lw-entry data-collection="' + escape(e['shelf'])
            + '" data-access="' + escape(e['access']) + '" data-terms="' + escape(terms, quote=True)
            + '" id="resource-' + escape(e['id']) + '"><h3>' + escape(e['title']) + '</h3><p>' + escape(e['why'])
            + '</p><p class="small-copy">' + escape(e['creator']) + ' · ' + escape(e['format']) + '</p>'
            + '<p><strong>Access:</strong> ' + escape(e['requirements']) + '</p><p>'
            + resources.external(e['entry_url'], 'Open resource') + ' · <a href="' + resources.collection_route(e['shelf']) + '#' + escape(e['id'])
            + '">Context and review notes</a></p></article>')
    body += section('directory-results', 'Browse or filter', 'Resources A to Z.', '<div id="lw-results">' + ''.join(results) + '</div>')
    body += section('selection-context', 'Keep the context', 'Choose for the life you have.',
        '<p class="section-deck">A useful selection is not a claim of personal use, affiliation, clinical benefit, or independent security testing. Original review dates remain visible in the full notes.</p>' + nav())
    return body
