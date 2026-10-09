"""Stable Poker destinations, separate from the personal-site navigation."""
from html import escape
import re


def section_navigation(page: dict) -> str:
    if not page['path'].startswith('/poker/'):
        return ''
    # Every utility and guide has a single meaningful current section.
    path = page['path']
    study_routes = {'/poker/study/', '/poker/study-calculators/', '/poker/decision-labs/',
                    '/poker/tournament-checklists/'}
    if path == '/poker/': current_route = path
    elif path == '/poker/glossary/': current_route = path
    elif path == '/poker/find/': current_route = path
    elif path in {'/poker/resources/', '/poker/resource-quality/'}: current_route = '/poker/resources/'
    elif path in study_routes: current_route = '/poker/study/'
    elif path.startswith('/poker/topics/') or path == '/poker/resource-collections/': current_route = '/poker/topics/'
    elif page.get('poker_guide') or path in {'/poker/library/', '/poker/reviewing-a-hand/', '/poker/start-here/', '/poker/live-tournament-guide/'}: current_route = '/poker/library/'
    else: current_route = '/poker/'
    links = []
    for route, label in [('/poker/', 'Home'), ('/poker/topics/', 'Topics'), ('/poker/find/', 'Search'),
                         ('/poker/library/', 'Guides'), ('/poker/resources/', 'External links'),
                         ('/poker/study/', 'Study desk'), ('/poker/glossary/', 'Glossary')]:
        current = (' aria-current="page"' if path == route else ' aria-current="location"') if route == current_route else ''
        links.append(f'<a href="{escape(route, quote=True)}"{current}>{escape(label)}</a>')
    return ('<div class="subsite-bar"><div class="shell"><span class="subsite-name">Nolan Kido / Poker</span>'
            '<nav class="subsite-links" aria-label="Poker section">' + ''.join(links) + '</nav></div></div>')


def clean_body(source: str) -> str:
    """Remove legacy breadcrumb duplicates, but never remove fragment targets."""
    def replace(match):
        markup = match.group()
        if re.search(r'\bid\s*=', markup):
            raise ValueError('Legacy breadcrumb contains a fragment target; migrate it explicitly')
        return ''
    return re.sub(r'<nav\b[^>]*\bclass="viewer-breadcrumb"[^>]*>.*?</nav>', replace, source, flags=re.S)
