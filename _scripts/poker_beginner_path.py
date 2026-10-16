"""One native route through the existing beginner lessons. No saved reader state."""
from html import escape
from hashlib import sha256
import poker_course
import poker_hand_lab
import poker_round_practice

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
    lessons = poker_course.overview(root, (root / '_source/poker/beginner-learning-path.html').read_text(encoding='utf-8'))
    tools = ('<section class="course-tool-menu" aria-labelledby="practice-tools"><h2 id="practice-tools">Optional practice when you need it.</h2>'
             '<p>The six lessons above are the course. Choose one tool below when it helps with a particular difficulty, then return to the lesson you were studying. You can use paper, a deck or counters. There is no requirement to finish all of these exercises.</p>'
             '<ul class="course-tool-choices"><li><a href="#card-basics">Card basics and best-five practice</a><p>Use this when card names, rankings or choosing five cards are unfamiliar. Read the basics and one worked selection, then begin lesson 1; the ten extra hands are available for later practice.</p></li>'
             '<li><a href="#first-hand-practice">A guided hand from deal to result</a><p>Use this when the sequence of a hand is hard to follow. Explain one scripted scene, compare the feedback, then pause or continue.</p></li>'
             '<li><a href="#betting-rehearsal">A betting round with counters</a><p>Use this when you lose track of whose turn it is or how many extra chips to add. Take the seats’ turns in one round, then return to the relevant lesson.</p></li></ul>'
             '<p><a href="#beginner-practice">Return to the six-lesson map</a> or <a href="/poker/beginner-checkpoint/#course-hand">attempt the complete-hand finish after the lessons</a>.</p></section>')
    addition = lessons + tools + poker_hand_lab.render(root) + poker_course.guided_hand(root) + poker_round_practice.render(root)
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
