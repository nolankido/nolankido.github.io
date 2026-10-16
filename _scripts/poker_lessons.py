"""Native short lessons: teach, model, explain a changed case, continue."""
from html import escape
import json
import re

DATA = '_source/poker/course-lessons.json'


def load(root, slugs):
    data = json.loads((root / DATA).read_text(encoding='utf-8'))
    if data.get('version') != 1 or [r['slug'] for r in data['lessons']] != list(slugs):
        raise ValueError('Short lessons must match the six canonical course lessons')
    for lesson in data['lessons']:
        for key in ['idea', 'recall']:
            if not isinstance(lesson.get(key), str) or not lesson[key].strip():
                raise ValueError('Short lessons need an idea and a recall task')
        for paragraphs in [lesson['teach'], lesson['worked']['setup'], lesson['worked']['answer'], lesson['attempt']['setup'], lesson['attempt']['answer']]:
            if not paragraphs or any(not isinstance(p, str) or not p.strip() for p in paragraphs):
                raise ValueError('Short lessons need teaching, examples and explained attempts')
        if not lesson['attempt']['prompt'].strip():
            raise ValueError('Each attempt needs a learner explanation prompt')
        for case in [lesson['worked'], lesson['attempt']]:
            known = []
            for kind in ['cards', 'candidates']:
                for group in case.get(kind, []):
                    values = group['values']
                    if not group['label'].strip() or not 1 <= len(values) <= 5 or len(set(values)) != len(values) or any(not re.fullmatch(r'[2-9TJQKA][shdc]', c) for c in values):
                        raise ValueError('Lesson cards need distinct standard cards and a label')
                    if kind == 'cards':
                        known.extend(values)
            if len(set(known)) != len(known):
                raise ValueError('Private and shared cards must not overlap')
        route, anchor = lesson['attempt']['repair'].split('#')
        if route != '/poker/' + lesson['slug'] + '/' or 'id="' + anchor + '"' not in (root / '_source/poker' / (lesson['slug'] + '.html')).read_text():
            raise ValueError('Each explanation must repair to its own published lesson')
    return data['lessons']


def paragraphs(values):
    return ''.join('<p>' + escape(value) + '</p>' for value in values)


def case_display(case, card_renderer):
    groups = case.get('cards', []) + case.get('candidates', [])
    cards = '<div class="course-lesson-cards">' + ''.join('<div><p class="course-state-label">' + escape(g['label']) + '</p>' + card_renderer(g['values']) + '</div>' for g in groups) + '</div>' if groups else ''
    return paragraphs(case['setup']) + cards


def render(lesson, card_renderer, next_route, next_label, optional, revision):
    attempt = lesson['attempt']
    return ('<p class="course-lesson-intro">Work through this short lesson, then pause or continue. The full explanation and other practice are available below.</p>'
            '<h3 id="course-lesson-idea">1. Learn one idea</h3><p><strong>' + escape(lesson['idea']) + '</strong></p>' + paragraphs(lesson['teach']) +
            '<section class="course-lesson-model" aria-labelledby="course-lesson-model"><h3 id="course-lesson-model">2. Follow a worked example</h3>' + case_display(lesson['worked'], card_renderer) + paragraphs(lesson['worked']['answer']) + '</section>'
            '<section class="course-lesson-attempt" aria-labelledby="course-lesson-try"><h3 id="course-lesson-try">3. Explain a changed situation</h3>' + case_display(attempt, card_renderer) +
            '<p><strong>Your task:</strong> ' + escape(attempt['prompt']) + '</p><p>Say your explanation or write it on paper before opening the answer.</p>'
            '<details class="poker-details" id="course-lesson-answer"><summary>Check your explanation</summary><div>' + paragraphs(attempt['answer']) +
            '<p><a href="' + escape(attempt['repair'], quote=True) + '">Revisit the exact explanation</a> if your reason differed, then close this answer and explain what changed.</p></div></details></section>'
            '<p class="course-lesson-recall"><strong>Before you move on:</strong> ' + escape(lesson['recall']) + ' If that is still difficult, use the repair link or pause and return. Your explanation stays with you.</p>'
            '<nav class="course-lesson-next" aria-label="Continue from the short lesson"><a class="button" href="' + escape(next_route, quote=True) + '">' + escape(next_label) + '</a><a href="#lesson-reference">Read the full explanation</a></nav>'
            '<details class="poker-details course-lesson-options"><summary>Full explanation and other practice</summary><div>' + optional + '</div></details>'
            '<p class="editorial-note">Updated October 15, 2026: ' + escape(revision) + ' Prepared with AI assistance. All scenes are fictional teaching examples. This is a self-check, not a skill score or betting recommendation.</p>')
