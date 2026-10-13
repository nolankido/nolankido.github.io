"""Make the existing fictional time comparisons editable without rewriting them."""
from html import escape
import json

PATH = 'technology/ai-time-savings/index.html'
KEYS = ('manual', 'assisted', 'review', 'count', 'setup', 'upkeep')
EXAMPLES = (
    ('Repeated task', ('30', '8', '7', '6', '60', '15')),
    ('One-off task', ('30', '8', '7', '1', '60', '0')),
    ('Review costs more', ('20', '5', '18', '10', '10', '5')),
)
BEGIN = '<!-- Editable time examples: start -->'
END = '<!-- Editable time examples: end -->'


def marked(text):
    return BEGIN + text + END


def blocks():
    buttons = ''.join('<button type="button" data-time-example="' +
                      escape(json.dumps(dict(zip(KEYS, values)), separators=(',', ':')), quote=True) +
                      '" data-time-label="' + label + '">' + label + '</button>'
                      for label, values in EXAMPLES)
    picker = ('<div id="time-example-picker" hidden><h3>Try a fictional example</h3>'
              '<p>Choose a starting point, adjust the values, then calculate. '
              '<a href="#time-examples">Read the worked arithmetic</a>.</p>'
              '<div class="time-actions">' + buttons + '</div></div>'
              '<div id="time-example-confirm" class="time-confirm" role="group" aria-labelledby="time-example-title" hidden>'
              '<h3 id="time-example-title">Replace your current entries?</h3>'
              '<p id="time-example-message"></p>'
              '<p>Save or copy the current result first if you need it.</p>'
              '<div class="time-actions"><button id="time-example-yes" type="button">Replace entries</button>'
              '<button id="time-example-no" type="button">Keep my comparison</button></div></div>')
    origin = '<p id="time-example-origin" class="evidence-note" hidden></p>'
    return marked(picker), marked(origin)


def decorate(page, body):
    if page['id'] != 'ai-time-savings':
        return body
    if BEGIN in body:
        raise ValueError('Editable time examples must be added exactly once')
    anchors = ('<div id="time-editor" hidden>', '<p id="time-basis-note"></p>')
    if any(body.count(anchor) != 1 for anchor in anchors):
        raise ValueError('The original calculator structure needs review')
    for anchor, block in zip(anchors, blocks()):
        body = body.replace(anchor, anchor + block, 1)
    return body
