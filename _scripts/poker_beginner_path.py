"""One native route through the existing beginner lessons. No saved reader state."""
from html import escape
from hashlib import sha256
import poker_course

PATH = '/poker/free-poker-learning-path/#beginner-practice'
DOWNLOAD = '/downloads/poker-beginner-study-card.txt'
CSS = 'assets/poker-beginner-path.css'
LESSONS = poker_course.LESSONS


def stylesheet(page, root):
    if page['path'] not in {'/poker/' + slug + '/' for slug, _ in LESSONS}:
        return ''
    version = sha256((root / CSS).read_bytes()).hexdigest()[:12]
    return '\n  <link rel="stylesheet" href="/' + CSS + '?v=' + version + '">'


def decorate(page, body, root):
    if page['path'] in {'/poker/' + slug + '/' for slug, _ in LESSONS}:
        return poker_course.lesson_support(page, body, root)
    if page['path'] != PATH.split('#')[0]:
        return body
    anchor = '<section class="course-later" aria-labelledby="how-to-use">'
    if body.count(anchor) != 1 or 'id="beginner-practice"' in body:
        raise ValueError('Beginner route requires one original study-plan anchor')
    addition = poker_course.guided_hand(root) + poker_course.overview(root, (root / '_source/poker/beginner-learning-path.html').read_text(encoding='utf-8'))
    return body.replace(anchor, addition + anchor, 1)


def navigation(page, pages):
    routes = ['/poker/' + slug + '/' for slug, _ in LESSONS]
    if page['path'] not in routes:
        return ''
    public = {p['path'] for p in pages if not p.get('noindex')}
    if not set(routes + [PATH.split('#')[0]]) <= public:
        raise ValueError('Beginner path requires every public lesson and the study path')
    current = routes.index(page['path'])
    items = []
    for index, ((_, title), route) in enumerate(zip(LESSONS, routes)):
        label = escape(title)
        item = (f'<span aria-current="page">{label} <strong>(this lesson)</strong></span>'
                if index == current else f'<a href="{route}">{label}</a>')
        items.append('<li>' + item + '</li>')
    return ('<details class="reader-outline beginner-path-nav" id="beginner-path-navigation">'
            f'<summary>Beginner practice path <span class="reader-outline-count">Lesson {current + 1} of 6</span></summary>'
            '<nav aria-label="Beginner practice path"><ol>' + ''.join(items) + '</ol>'
            f'<p><a href="{PATH}">See the goals and readiness checks</a></p>'
            f'<p><a href="{DOWNLOAD}" download>Download your blank study card (TXT)</a></p>'
            '</nav><p>Keep your place in your own notes. This path does not save progress or send answers.</p></details>')
