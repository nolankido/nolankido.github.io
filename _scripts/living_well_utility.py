"""Reader-first, static helpers for the Technology for Real Life guide series."""
from html import escape

SERIES = 'technology-for-real-life'
EVIDENCE = 'worked-guide-not-firsthand-result'
FIELDS = ('start', 'simplest_route', 'finish', 'starter')


def validate(entry: dict) -> None:
    """Require explicit, bounded examples rather than silently claiming field results."""
    if not entry.get('series'):
        if 'utility' in entry or 'evidence_status' in entry or 'outcome' in entry:
            raise ValueError('Utility metadata needs an explicit Living Well series')
        return
    if entry['series'] != SERIES or entry['kind'] != 'guide':
        raise ValueError('Unknown Living Well utility series or kind')
    if entry.get('evidence_status') != EVIDENCE:
        raise ValueError('Utility guides must not imply firsthand results')
    if not isinstance(entry.get('outcome'), str) or not entry['outcome'].strip():
        raise ValueError('Utility guides need a concrete outcome')
    if entry['slug'] == SERIES:
        if entry.get('format') != 'practice-path' or 'utility' in entry:
            raise ValueError('The utility starting path is distinct from a worked guide')
        return
    data = entry.get('utility')
    if not isinstance(data, dict) or set(data) != set(FIELDS):
        raise ValueError('A worked guide needs its input, simple route, finish and starter')
    for field in FIELDS:
        if not isinstance(data[field], str) or not data[field].strip():
            raise ValueError('Empty utility field: ' + field)
        if len(data[field]) > (2500 if field == 'starter' else 500):
            raise ValueError('Utility field is too long: ' + field)


def brief(entry: dict) -> str:
    data = entry.get('utility')
    if not data:
        return ''
    return ('<aside class="lw-callout lw-utility-brief" aria-labelledby="useful-result">'
            '<p class="lw-eyebrow">Technology for real life · Worked guide</p>'
            '<h2 id="useful-result">What you will make</h2><p>' + escape(entry['outcome']) + '</p>'
            '<p><strong>Start with:</strong> ' + escape(data['start']) + '</p>'
            '<p><strong>Simplest route:</strong> ' + escape(data['simplest_route']) + '</p>'
            '<p><strong>Finish when:</strong> ' + escape(data['finish']) + '</p>'
            '<p class="small-copy">No generative AI required. Worked examples illustrate the method; '
            'they are not reports of personal tests.</p></aside>')


def starter(entry: dict) -> str:
    data = entry.get('utility')
    if not data:
        return ''
    return ('<section class="lw-utility-starter" aria-labelledby="plain-text-starter">'
            '<h2 id="plain-text-starter">A small template to use</h2>'
            '<p>Use these headings on paper or copy them into your own note. '
            'Keep the answers with you; there is nothing to submit to this website.</p>'
            '<details class="lw-preview" open><summary>Read or select the plain-text template</summary>'
            '<pre>' + escape(data['starter']) + '</pre></details></section>')


def outline(entry: dict, html: str) -> str:
    if not entry.get('utility'):
        return html
    html = html.replace('<ol>', '<ol><li><a href="#useful-result">What you will make</a></li>', 1)
    return html.replace('<li><a href="#one-question">',
                        '<li><a href="#plain-text-starter">A small template to use</a></li>'
                        '<li><a href="#one-question">', 1)


def reading_text(entry: dict) -> str:
    data = entry.get('utility', {})
    return ' '.join([entry.get('outcome', '')] + [data.get(field, '') for field in FIELDS])
