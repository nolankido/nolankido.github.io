"""Native beginner practice connections and an exact private-workbook preview."""
from html import escape
import poker_beginner_path
import poker_final_hands

ROUTE = '/poker/beginner-checkpoint/'
SHEET = 'downloads/poker-beginner-checkpoint.txt'
LESSONS = {'/poker/' + slug + '/' for slug, _ in poker_beginner_path.LESSONS} | {
    '/poker/ranges-for-beginners/', '/poker/betting-with-a-purpose/'}
MARKER = '<!-- Beginner checkpoint workbook -->'


def decorate(page, body, root):
    if page['path'] == ROUTE:
        if body.count(MARKER) != 1:
            raise ValueError('Checkpoint requires one workbook preview marker')
        preview = ('<details class="poker-details" id="checkpoint-workbook-preview">'
                   '<summary>Preview the complete blank checkpoint workbook</summary>'
                   '<div><pre class="worksheet-preview">' + escape((root / SHEET).read_text(encoding='utf-8')) +
                   '</pre></div></details>')
        final_marker = '<!-- Connected final hands -->'
        if body.count(final_marker) != 1:
            raise ValueError('Checkpoint needs one connected final exercise')
        return body.replace(final_marker, poker_final_hands.render(root, poker_beginner_path.poker_course.cards), 1).replace(MARKER, preview, 1)
    if page['path'] == poker_beginner_path.PATH.split('#')[0]:
        anchor = '<section class="course-later" aria-labelledby="how-to-use">'
        finish = '<section class="viewer-example" aria-labelledby="course-finish">'
        if finish in body:
            anchor = finish
        if body.count(anchor) != 1 or 'id="beginner-next-step"' in body:
            raise ValueError('Checkpoint route requires one original study-plan anchor')
        return body.replace(anchor, (root / '_source/poker/beginner-checkpoint-route.html').read_text(encoding='utf-8') + anchor, 1)
    if page['path'] in LESSONS:
        anchor = '<nav class="article-navigation"'
        if body.count(anchor) != 1 or 'id="beginner-checkpoint-invite"' in body:
            raise ValueError('Checkpoint invitation requires one lesson continuation')
        return body.replace(anchor, (root / '_source/poker/beginner-checkpoint-invitation.html').read_text(encoding='utf-8') + anchor, 1)
    return body
