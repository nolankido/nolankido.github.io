"""Stable Poker destinations, separate from the personal-site navigation."""
from html import escape


def section_navigation(page: dict) -> str:
    if not page['path'].startswith('/poker/'):
        return ''
    links = []
    for route, label in [('/poker/', 'Home'), ('/poker/topics/', 'Topics'), ('/poker/find/', 'Search'),
                         ('/poker/library/', 'Guides'), ('/poker/resources/', 'External links'),
                         ('/poker/study/', 'Study desk'), ('/poker/glossary/', 'Glossary')]:
        current = ' aria-current="page"' if page['path'] == route else ''
        if not current and route == '/poker/topics/' and page.get('poker_topic'):
            current = ' aria-current="location"'
        if not current and route == '/poker/library/' and (page.get('poker_guide') or page['path'] == '/poker/reviewing-a-hand/') and page['path'] != '/poker/glossary/':
            current = ' aria-current="location"'
        links.append(f'<a href="{escape(route, quote=True)}"{current}>{escape(label)}</a>')
    return ('<div class="subsite-bar"><div class="shell"><span class="subsite-name">Nolan Kido / Poker</span>'
            '<nav class="subsite-links" aria-label="Poker section">' + ''.join(links) + '</nav></div></div>')
