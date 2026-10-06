"""Small local navigation for the poker section; no client-side routing."""
from html import escape


def section_navigation(page: dict) -> str:
    if not page['path'].startswith('/poker/'):
        return ''
    links = []
    for route, label in [('/poker/', 'Overview'), ('/poker/#watch', 'Stories & episodes'), ('/poker/start-here/', 'Start here'), ('/poker/reviewing-a-hand/', 'Hand review'), ('/poker/study/', 'Study desk'), ('/poker/glossary/', 'Glossary')]:
        current = ' aria-current="page"' if page['path'] == route else ''
        links.append(f'<a href="{escape(route, quote=True)}"{current}>{escape(label)}</a>')
    return ('<div class="subsite-bar"><div class="shell"><span class="subsite-name">Nolan Kido / Poker</span>'
            '<nav class="subsite-links" aria-label="Poker section">' + ''.join(links) + '</nav></div></div>')
